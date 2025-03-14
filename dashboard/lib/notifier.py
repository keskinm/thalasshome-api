import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, request

from dashboard.db.client import supabase_cli
from dashboard.lib.order.order import get_address, get_name, get_ship

notifier_bp = Blueprint("notifier", __name__)


class Notifier:
    def __init__(self):
        self.protocol = "http"
        self.sender_email = "spa.detente.france@gmail.com"
        self.flask_address = request.host_url.rstrip("/")
        self.email_sender_password = os.getenv("EMAIL_SENDER_PASSWORD")

    def __call__(self, order, line_items, test=False):
        providers = self.get_providers(order, test=test)
        tokens = self.create_tokens(order["id"], providers)
        self.notify_providers(providers, tokens, order, line_items)

    @staticmethod
    def get_providers(order, test=False) -> list[dict]:
        command_country = order["shipping_address"]["country"]
        command_zip = order["shipping_address"]["zip"]
        raise NotImplementedError(
            "find_zone does not exists anymore, code will be update soon"
        )
        # command_zone = find_zone(command_zip, command_country)

        providers = (
            supabase_cli.rpc("get_user_by_zone", {"command_zone": command_zone})
            .execute()
            .data
        )

        if test:
            providers = list(filter(lambda x: "python" in x["username"], providers))
        return providers

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

        for i in range(len(providers)):
            provider = providers[i]
            token = tokens[i]

            text = """\
            Bonjour, une nouvelle commande à livrer est disponible !
            Commande:  {ship}
            Adresse de la commande : {adr}
            Total restant pour vous : {amount}€
            Pour accepter la commande : {protocol}://{flask_address}/commands/accept/{token_id}""".format(
                protocol=self.protocol,
                flask_address=self.flask_address,
                token_id=token,
                ship=ship,
                adr=adr,
                amount=amount,
            )

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
            """.format(
                ship=ship,
                adr=adr,
                protocol=self.protocol,
                flask_address=self.flask_address,
                token_id=token,
                amount=amount,
            )

            subject = "Une nouvelle commande ThalassHome !"

            self.send_mail(provider["email"], subject, html, text)

    def accept_command(self, token_id):
        order_id, provider_username = token_id.split("|")
        order = (
            supabase_cli.table("orders")
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
                supabase_cli.table("users")
                .select("*")
                .eq("username", provider_username)
                .limit(1)
                .single()
                .execute()
                .data
            )
            line_items = (
                supabase_cli.table("line_items")
                .select("*")
                .eq("order_id", order_id)
                .execute()
                .data
            )
            provider_email = provider["email"]

            order["provider"] = {"username": provider_username, "email": provider_email}
            supabase_cli.table("orders").update({"delivery_men_id": provider["id"]}).eq(
                "id", order_id
            ).execute()

            html_customer_phone_number = (
                "Numéro du client : {phone} <br>".format(phone=order["phone"])
                if "phone" in order
                else ""
            )
            html_customer_mail = (
                "E-mail : {mail} <br>".format(mail=order["email"])
                if "email" in order
                else ""
            )

            text_customer_phone_number = (
                "Numéro du client : {phone} \n".format(phone=order["phone"])
                if "phone" in order
                else ""
            )
            text_customer_mail = (
                "E-mail : {mail} \n".format(mail=order["email"])
                if "email" in order
                else ""
            )

            plain_customer_name = get_name(order)
            text_customer_name = "Nom : {name} \n".format(name=plain_customer_name)
            html_customer_name = "Nom : {name} <br>".format(name=plain_customer_name)

            text = """\
                Merci d'avoir accepté la commande ! Voici les détails conçernant le client :
                {customer_phone_number}
                {customer_mail}
                {customer_name}""".format(
                customer_phone_number=text_customer_phone_number,
                customer_mail=text_customer_mail,
                customer_name=text_customer_name,
            )
            html = """\
                <html>
                  <body>
                    <p>Merci d'avoir accepté la commande ! Voici les détails conçernant le client : <br>
                    {customer_phone_number}
                    {customer_mail}
                    {customer_name}
                    </p>
                  </body>
                </html>
                """.format(
                customer_phone_number=html_customer_phone_number,
                customer_mail=html_customer_mail,
                customer_name=html_customer_name,
            )
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
        html = """<p>
                    Voici les coordonnées de notre prestataire qui se charge de votre commande : <br>
                    {provider_email}
                    {provider_number}
                  </p>
               """.format(
            provider_email=provider["email"], provider_number=provider["phone_number"]
        )

        self.send_mail(provider["email"], subject, html)

    def notify_admins(self, order: dict, provider: dict, line_items: list[dict]):
        adr = get_address(order)
        ship, amount = get_ship(line_items)
        customer_name = get_name(order)

        subject = "Commande prise en charge par un prestataire"

        html = """
        <p>
        La commande : {ship} <br>
        du client : {customer_name}, <br>
        située à : {adr} <br>
        coordonnées du client : {customer_mail} {customer_number} <br>
        d'un solde à récuperer de : {amount}€ <br>
        a été acceptée par le prestataire : {provider} <br>
        coordonnées du prestataire : {provider_mail}, {provider_number} <br>
        </p>
        """.format(
            ship=ship,
            customer_name=customer_name,
            adr=adr,
            provider=provider["username"],
            amount=amount,
            provider_mail=provider["email"],
            provider_number=provider["phone_number"],
            customer_mail=order["email"] if "email" in order else "",
            customer_number=order["phone"] if "phone" in order else "",
        )

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
