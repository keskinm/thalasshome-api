from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from google.cloud import datastore

from dashboard.db.tabledef import User
from dashboard.lib.utils.utils import find_zone
from dashboard.lib.parser.creation_order.creation_order import CreationOrderParser

engine = create_engine('sqlite:///providers.db', echo=True)


class Notifier:
    def __init__(self):
        self.protocol = 'http'
        self.orders_collection_name = "orders"
        self.sender_email = "spa.detente.france@gmail.com"
        self.flask_address = os.getenv('flask_address')
        self.email_sender_password = os.getenv('email_sender_password')

    def __call__(self, order):
        providers = self.get_providers(order)
        tokens = self.create_tokens(order['id'], providers)
        self.notify_providers(providers, tokens, order)

    @staticmethod
    def get_providers(order):
        providers = []

        db_session = sessionmaker(bind=engine)()
        table = db_session.query(User).filter()
        for user in table:
            command_country = order['shipping_address']['country']
            command_zip = order['shipping_address']['zip']
            command_zone = find_zone(command_zip, command_country)

            if user.zone == command_zone:
                providers.append(user)

        return providers

    @staticmethod
    def create_tokens(order_id, providers):
        tokens = []
        for provider in providers:
            tokens.append(str(order_id)+'|'+provider.username)
        return tokens

    def notify_providers(self, providers, tokens, order):
        item = order

        adr = CreationOrderParser().get_address(item)
        ship, amount = CreationOrderParser().get_ship(item)

        for i in range(len(providers)):
            provider = providers[i]
            token = tokens[i]

            text = """\
            Bonjour, une nouvelle commande à livrer est disponible ! 
            Commande:  {ship}
            Adresse de la commande : {adr}
            Total restant pour vous : {amount}€
            Pour accepter la commande : {protocol}://{flask_address}/commands/accept/{token_id}""".format(protocol=self.protocol,
                                                                                                          flask_address=self.flask_address,
                                                                                                          token_id=token,
                                                                                                          ship=ship,
                                                                                                          adr=adr,
                                                                                                          amount=amount)

            html = """\
            <html>
              <body>
                <p>Bonjour, une nouvelle commande à livrer est disponible !<br>
                ship: {ship} <br>
                addr: {adr} <br>
                <strong> Total restant pour vous: {amount}€ </strong> <br>
                <a href="{protocol}://{flask_address}/commands/accept/{token_id}">Je me charge de cette commande !</a><br>
                </p>
              </body>
            </html>
            """.format(ship=ship, adr=adr, protocol=self.protocol, flask_address=self.flask_address, token_id=token,
                       amount=amount)

            subject = "Une nouvelle commande ThalassHome !"
            receiver_email = provider.email

            self.send_mail(receiver_email, text, html, subject)

    def accept_command(self, token_id):
        datastore_client = datastore.Client()
        order_id, provider_username = token_id.split('|')

        key = datastore_client.key(self.orders_collection_name, order_id)
        order = datastore_client.get(key)
        if order is None:
            order_id = int(order_id)
            key = datastore_client.key(self.orders_collection_name, order_id)
            order = datastore_client.get(key)
            if order is None:
                return "La commande n'existe plus. Il ne s'agissait peut-être que d'une commande test pour le développement."

        if 'provider' in order:
            return 'La commande a déjà été accepté par un autre livreur.'

        else:
            db_session = sessionmaker(bind=engine)()
            user = db_session.query(User).filter_by(username=provider_username).first()
            order['provider'] = {'username': provider_username, 'email': user.email}
            datastore_client.put(order)

            receiver_email = user.email

            html_customer_phone_number = 'Numéro du client : {phone} <br>'.format(phone=order["phone"]) if 'phone' in order else ''
            html_customer_mail = 'E-mail : {mail} <br>'.format(mail=order["email"]) if 'email' in order else ''

            text_customer_phone_number = 'Numéro du client : {phone} \n'.format(phone=order["phone"]) if 'phone' in order else ''
            text_customer_mail = 'E-mail : {mail} \n'.format(mail=order["email"]) if 'email' in order else ''

            text = """\
                Merci d'avoir accepté la commande ! Voici les détails conçernant le client :
                {customer_phone_number} 
                {customer_mail}""".format(customer_phone_number=text_customer_phone_number, customer_mail=text_customer_mail)
            html = """\
                <html>
                  <body>
                    <p>Merci d'avoir accepté la commande ! Voici les détails conçernant le client : <br>
                    {customer_phone_number} 
                    {customer_mail}
                    </p>
                  </body>
                </html>
                """.format(customer_phone_number=html_customer_phone_number, customer_mail=html_customer_mail)
            subject = "Détails sur votre commande ThalassHome"
            self.send_mail(receiver_email, text, html, subject)

            return """La prise en charge de la commande a bien été accepté. Vous recevrez très prochainement un mail 
            contenant des informations supplémentaires pour votre commande. A bientôt ! """

    def send_mail(self, receiver_email, text, html, subject):
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        message["To"] = receiver_email

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.sender_email, self.email_sender_password)
            server.sendmail(
                self.sender_email, receiver_email, message.as_string()
            )




