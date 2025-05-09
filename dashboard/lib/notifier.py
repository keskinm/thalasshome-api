import os
import smtplib
import ssl
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import request
from jinja2 import Environment, FileSystemLoader

from dashboard.constants import APP_DIR
from dashboard.lib.order.order import get_address, get_name, get_ship


class Notifier:
    sender_email = "spa.detente.france@gmail.com"
    email_sender_password = os.getenv("EMAIL_SENDER_PASSWORD")
    template_dir = str(APP_DIR / "templates" / "notification")

    def __init__(self, flask_address=""):
        self.flask_address = (
            flask_address or urllib.parse.urlparse(request.host_url).netloc
        )
        self.protocol = "https" if request.is_secure else "http"
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))

    def notify_providers(
        self,
        providers: list[dict],
        tokens: list[str],
        order: dict,
        line_items: list[dict],
    ):
        adr = get_address(order)
        ship, amount = get_ship(line_items)

        template_vars = {
            "protocol": self.protocol,
            "flask_address": self.flask_address,
            "ship": ship,
            "adr": adr,
            "amount": amount,
        }

        text_template = self.jinja_env.get_template("provider_notification.txt")
        html_template = self.jinja_env.get_template("provider_notification.html")

        for i in range(len(providers)):
            provider = providers[i]
            template_vars["token_id"] = tokens[i]

            text = text_template.render(**template_vars)
            html = html_template.render(**template_vars)
            subject = "Une nouvelle commande ThalassHome !"

            self.send_mail(provider["email"], subject, html, text)

    def notify_customer(self, provider: dict, order_email: str):
        subject = "ThalassHome - Contact prestataire pour votre commande"

        template_vars = {
            "provider_email": provider["email"],
            "provider_number": provider["phone_number"],
        }

        html_template = self.jinja_env.get_template("notify_customer.html")
        html = html_template.render(**template_vars)

        self.send_mail(order_email, subject, html)

    def notify_admins(self, order: dict, provider: dict, line_items: list[dict]):
        adr = get_address(order)
        ship, amount = get_ship(line_items)
        customer_name = get_name(order)

        subject = "Commande prise en charge par un prestataire"

        template_vars = {
            "ship": ship,
            "customer_name": customer_name,
            "adr": adr,
            "provider": provider["username"],
            "amount": amount,
            "provider_mail": provider["email"],
            "provider_number": provider["phone_number"],
            "customer_mail": order.get("email", ""),
            "customer_number": order.get("phone", ""),
        }

        html_template = self.jinja_env.get_template("notify_admin.html")
        html = html_template.render(**template_vars)

        self.send_mail(self.sender_email, subject, html)

    def send_mail(self, receiver_email: str, subject: str, html: str, text: str = ""):
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
            server.sendmail(self.sender_email, receiver_email, message.as_string())
