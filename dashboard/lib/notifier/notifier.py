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

email_sender_password = os.getenv('email_sender_password')
sender_email = "spa.detente.france@gmail.com"


class Notifier:
    def __init__(self):
        pass

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
        tokens = self.create_tokens(providers)
        self.notify_providers(providers, tokens, order)

    def create_tokens(self, providers):
        uuids = []
        for _ in range(len(providers)):
            uuids.append(uuid.uuid4())
        return uuids

    def notify_providers(self, providers, tokens, order):
        for i in range(len(providers)):
            provider = providers[i]
            token = tokens[i]

            receiver_email = provider.email

            message = MIMEMultipart("alternative")
            message["Subject"] = "Une nouvelle commande ThalassHome !"
            message["From"] = sender_email
            message["To"] = receiver_email

            text = """\
            Bonjour, une nouvelle commande à livrer est disponible ! 
            Accepter : http://www.{ws_adress}.com/accept/{token_id}
            Refuser : http://www.{ws_adress}.com/refuser/{token_id}""".format(ws_adress=None, token_id=token)

            html = """\
            <html>
              <body>
                <p>Hi,<br>
                   Bonjour, une nouvelle commande à livrer est disponible !<br>
                   <a href="http://www.{ws_adress}.com/accept/{token_id}">Real Python</a><br>
                   <a href="http://www.{ws_adress}.com/refuser/{token_id}">Real Python</a><br>
                </p>
              </body>
            </html>
            """.format(ws_adress=None, token_id=token)

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            message.attach(part1)
            message.attach(part2)

            context = ssl.create_default_context()

            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(sender_email, email_sender_password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )

    def notify_accept_provider(self, token_id):
        datastore_client = datastore.Client()

        provider_tokens_key = datastore_client.key("provider_tokens", token_id)

        provider_token = datastore_client.get(key=provider_tokens_key)
        provider_email = provider_token['provider_email']
        order_id = provider_token['order_id']

        order_key = datastore_client.key("orders", order_id)
        order = datastore_client.get(key=order_key)

        email_sender_password = os.getenv('email_sender_password')
        sender_email = "spa.detente.france@gmail.com"
        receiver_email = provider_email

        message = MIMEMultipart("alternative")
        message["Subject"] = "Une nouvelle commande ThalassHome !"
        message["From"] = sender_email
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
            server.login(sender_email, email_sender_password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

    def accept_command(self, token_id):
        self.notify_accept_provider(token_id)

    def decline_command(self, token_id):
        pass

    @staticmethod
    def test_notification():
        from dashboard.utils.samples.orders.orders import mixed_order
        Notifier()(mixed_order)
        return 'SENT TEST NOTIFICATION :) !'




