import uuid
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from google.cloud import datastore

from dashboard.db.tabledef import User
from dashboard.lib.utils.utils import find_zone

engine = create_engine('sqlite:///providers.db', echo=True)

flask_address = os.getenv('flask_address')


class Notifier:
    def __init__(self):
        self.protocol = 'http'
        self.orders_collection_name = "orders"
        self.email_sender_password = os.getenv('email_sender_password')
        self.sender_email = "spa.detente.france@gmail.com"

    def get_providers(self, order):
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

    def __call__(self, order):
        providers = self.get_providers(order)
        tokens = self.create_tokens(order['id'], providers)
        self.notify_providers(providers, tokens, order)

    def create_tokens(self, order_id, providers):
        tokens = []
        for provider in providers:
            tokens.append(order_id+'|'+provider.username)
        return tokens

    def notify_providers(self, providers, tokens, order):
        for i in range(len(providers)):
            provider = providers[i]
            token = tokens[i]

            receiver_email = provider.email

            message = MIMEMultipart("alternative")
            message["Subject"] = "Une nouvelle commande ThalassHome !"
            message["From"] = self.sender_email
            message["To"] = receiver_email

            text = """\
            Bonjour, une nouvelle commande à livrer est disponible ! 
            Pour accepter la commande : {protocol}://{flask_address}/commands/accept/{token_id}""".format(protocol=self.protocol,
                                                                                                          flask_address=flask_address,
                                                                                                          token_id=token)

            html = """\
            <html>
              <body>
                <p>Bonjour, une nouvelle commande à livrer est disponible !<br>
                   <a href="{protocol}://{flask_address}/commands/accept/{token_id}">Je me charge de cette commande !</a><br>
                </p>
              </body>
            </html>
            """.format(protocol=self.protocol, flask_address=flask_address, token_id=token)

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

    def accept_command(self, token_id):
        print("IN ACCEPT COMMAND!")

        datastore_client = datastore.Client()
        order_id, provider_username = token_id.split('|')
        key = datastore_client.key(self.orders_collection_name, order_id)
        order = datastore_client.get(key)

        print("token_id", token_id)
        print("order id", order_id)
        print("provider_username", provider_username)
        print("key", key)
        print("order", order)

        if 'provider' in order:
            return 'La commande a déjà été accepté par un autre livreur.'

        else:
            db_session = sessionmaker(bind=engine)()
            user = db_session.query(User).filter_by(username=provider_username).first()

            order['provider'] = {'username': provider_username, 'email': user.email}

            datastore_client.put(order)

            receiver_email = user.email

            message = MIMEMultipart("alternative")
            message["Subject"] = "Une nouvelle commande ThalassHome !"
            message["From"] = self.sender_email
            message["To"] = receiver_email

            text = """\
            Merci d'avoir accepté la commande ! Voici les détails : 
            .... """
            html = """\
            <html>
              <body>
                <p>Merci d'avoir accepté la commande ! Voici les détails : ...</p>
              </body>
            </html>
            """
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

            return """La prise en charge de la commande a bien été accepté. Vous recevrez très prochainement un mail 
            contenant des informations supplémentaires pour votre commande. A bientôt ! """

    @staticmethod
    def test_notification():
        from dashboard.utils.samples.orders.orders import mixed_order

        datastore_client = datastore.Client()

        name = mixed_order['id']
        key = datastore_client.key("orders", name)
        c_order = datastore.Entity(key=key)
        for k, v in mixed_order.items():
            c_order[k] = v
        datastore_client.put(c_order)

        Notifier()(mixed_order)
        return 'SENT TEST NOTIFICATION :) !'




