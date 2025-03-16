import email
from pathlib import Path

import pytest

from dashboard.lib.notifier import Notifier


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("EMAIL_SENDER_PASSWORD", "test_password")


@pytest.fixture(autouse=True)
def setup_inspect_dir():
    inspect_dir = Path("inspect")
    inspect_dir.mkdir(exist_ok=True)
    yield


def save_email_content(email_str: str, filename: str):
    msg = email.message_from_string(email_str)
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html_content = part.get_payload(decode=True).decode()
            with open(f"inspect/{filename}.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            break


@pytest.fixture
def mock_smtp(mocker):
    smtp_mock = mocker.patch("smtplib.SMTP_SSL")
    mock_sendmail = mocker.Mock()

    def sendmail_and_save(*args):
        # args[2] contains the email content
        subject = email.message_from_string(args[2])["Subject"]
        sanitized_subject = "".join(c if c.isalnum() else "_" for c in subject)
        save_email_content(args[2], f"email_{sanitized_subject}")
        return None  # Return None instead of calling the mock again

    mock_sendmail.side_effect = sendmail_and_save
    smtp_mock.return_value.__enter__.return_value.sendmail = mock_sendmail
    return smtp_mock


def test_notify_providers(mock_smtp, sample_order, sample_provider, sample_line_items):
    notifier = Notifier(flask_address="test.com")
    providers = [sample_provider]
    tokens = [f"{sample_order['id']}|{sample_provider['username']}"]

    notifier.notify_providers(providers, tokens, sample_order, sample_line_items)

    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()
    args = mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0]
    assert args[0] == notifier.sender_email
    assert args[1] == sample_provider["email"]
    assert "Une nouvelle commande ThalassHome !" in args[2]


def test_notify_customer(mock_smtp, sample_provider):
    notifier = Notifier(flask_address="test.com")
    notifier.notify_customer(sample_provider)

    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()
    args = mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0]
    assert args[0] == notifier.sender_email
    assert args[1] == sample_provider["email"]
    assert "ThalassHome - Contact prestataire" in args[2]


def test_notify_admins(mock_smtp, sample_order, sample_provider, sample_line_items):
    notifier = Notifier(flask_address="test.com")
    notifier.notify_admins(sample_order, sample_provider, sample_line_items)

    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()
    args = mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0]
    assert args[0] == notifier.sender_email
    assert args[1] == notifier.sender_email
    assert "Commande prise en charge par un prestataire" in args[2]


def test_accept_command(
    test_db_client, mock_smtp, sample_provider, sample_order_line_item
):
    sample_order, sample_line_items = sample_order_line_item
    result = Notifier.accept_command(
        f"{sample_order['id']}|{sample_provider['username']}", flask_address="test.com"
    )

    assert "La prise en charge de la commande a bien été accepté" in result
    assert (
        mock_smtp.return_value.__enter__.return_value.sendmail.call_count == 3
    )  # Provider + Customer + Admin notifications


def test_get_delivery_mens(sample_order_line_item, sample_provider):
    sample_order, sample_line_items = sample_order_line_item

    delivery_mens = Notifier.get_delivery_mens(sample_order)

    assert len(delivery_mens) == 1
    assert "python" in delivery_mens[0]["username"]


def test_notification_flow_integration(
    client, test_db_client, mock_smtp, sample_order_line_item, sample_provider
):
    """Test the complete notification flow:
    1. Notify providers about new order
    2. Provider accepts the order by clicking the email link
    """
    sample_order, sample_line_items = sample_order_line_item
    notifier = Notifier(flask_address="test.com")

    # Step 1: Notify providers
    providers = [sample_provider]
    tokens = notifier.create_tokens(sample_order["id"], providers)
    notifier.notify_providers(providers, tokens, sample_order, sample_line_items)

    # Verify provider notification was sent
    assert mock_smtp.return_value.__enter__.return_value.sendmail.call_count == 1
    notification_args = (
        mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0]
    )
    assert "Une nouvelle commande ThalassHome !" in notification_args[2]

    # Reset mock to track new emails
    mock_smtp.return_value.__enter__.return_value.sendmail.reset_mock()

    # Step 2: Simulate provider clicking accept link
    token = f"{sample_order['id']}|{sample_provider['username']}"
    response = client.get(f"notifier/commands/accept/{token}")

    assert response.status_code == 200
    assert (
        "La prise en charge de la commande a bien été accepté" in response.data.decode()
    )

    # Verify all notification emails were sent (provider confirmation + customer + admin)
    assert mock_smtp.return_value.__enter__.return_value.sendmail.call_count == 3

    # Verify order was updated in database with provider
    updated_order = test_db_client.select_from_table(
        "orders",
        select_columns="*",
        conditions={"id": sample_order["id"]},
        single=True,
        limit=1,
    )
    assert updated_order["delivery_men_id"] == sample_provider["id"]
