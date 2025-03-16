import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, request
from jinja2 import Environment, FileSystemLoader

from dashboard.constants import APP_DIR
from dashboard.container import container
from dashboard.lib.order.order import get_address, get_name, get_ship

SUPABASE_CLI = container.get("SUPABASE_CLI")

notifier_bp = Blueprint("notifier", __name__)


class Notifier:
    protocol = "http"
    sender_email = "spa.detente.france@gmail.com"
    email_sender_password = os.getenv("EMAIL_SENDER_PASSWORD")
    template_dir = str(APP_DIR / "templates" / "notification")

    def __init__(self, flask_address=""):
        self.flask_address = flask_address or request.host_url.rstrip("/")
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))

    @classmethod
    def notify(cls, order, line_items, test=False, flask_address=""):
        notifier = cls(flask_address)
        providers = notifier.get_delivery_mens(order, test=test)
        tokens = notifier.create_tokens(order["id"], providers)
        notifier.notify_providers(providers, tokens, order, line_items)

    @staticmethod
    def get_delivery_mens(order, test=False) -> list[dict]:
        lat, lon = order["shipping_lat"], order["shipping_lon"]

        delivery_mens = (
            SUPABASE_CLI.rpc(
                "check_delivery_men_around_point",
                {
                    "in_shipping_lon": lon,
                    "in_shipping_lat": lat,
                },
            )
            .execute()
            .data
        )
        if test:
            delivery_mens = list(
                filter(lambda x: "python" in x["username"], delivery_mens)
            )
        return delivery_mens

    @staticmethod
    def create_tokens(order_id, providers: list[dict]) -> list[str]:
        tokens = []
        for provider in providers:
            tokens.append(f"{str(order_id)}|{provider['username']}")
        return tokens

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

    def accept_command(self, token_id):
        order_id, provider_username = token_id.split("|")
        order = (
            SUPABASE_CLI.table("orders")
            .select("*")
            .eq("id", order_id)
            .limit(1)
            .single()
            .execute()
            .data
        )

        if order is None:
            return "La commande n'existe plus. Il ne s'agissait peut-être que d'une commande test pour le développement."

        if "provider" in order:
            return "La commande a déjà été accepté par un autre livreur."

        else:
            provider = (
                SUPABASE_CLI.table("users")
                .select("*")
                .eq("username", provider_username)
                .limit(1)
                .single()
                .execute()
                .data
            )
            line_items = (
                SUPABASE_CLI.table("line_items")
                .select("*")
                .eq("order_id", order_id)
                .execute()
                .data
            )
            provider_email = provider["email"]

            order["provider"] = {"username": provider_username, "email": provider_email}
            SUPABASE_CLI.table("orders").update({"delivery_men_id": provider["id"]}).eq(
                "id", order_id
            ).execute()

            plain_customer_name = get_name(order)

            template_vars = {
                "phone": order.get("phone", ""),
                "email": order.get("email", ""),
                "customer_name": plain_customer_name,
            }

            text_template = self.jinja_env.get_template("accept_command.txt")
            html_template = self.jinja_env.get_template("accept_command.html")

            text = text_template.render(**template_vars)
            html = html_template.render(**template_vars)

            subject = "Détails sur votre commande ThalassHome"
            self.send_mail(provider_email, subject, html, text)

            self.notify_customer(provider)
            self.notify_admins(order, provider, line_items)
            self.update_employee(order, provider)

            return """La prise en charge de la commande a bien été accepté. Vous recevrez très prochainement un mail
            contenant des informations supplémentaires pour votre commande. A bientôt ! """

    def update_employee(self, order, provider):
        pass

    def notify_customer(self, provider: dict):
        subject = "ThalassHome - Contact prestataire pour votre commande"

        template_vars = {
            "provider_email": provider["email"],
            "provider_number": provider["phone_number"],
        }

        html_template = self.jinja_env.get_template("notify_customer.html")
        html = html_template.render(**template_vars)

        self.send_mail(provider["email"], subject, html)

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


@notifier_bp.route("/commands/accept/<token_id>", methods=["GET"])
def _accept_command(token_id):
    return Notifier().accept_command(token_id)
