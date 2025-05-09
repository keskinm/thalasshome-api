import email
from pathlib import Path

import pytest
from flask import request

from dashboard.lib.delivery_men import accept_order, get_delivery_mens
from dashboard.lib.notifier import Notifier
from dashboard.lib.services import notify_receive_command


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("EMAIL_SENDER_PASSWORD", "test_password")


@pytest.fixture(autouse=True)
def setup_inspect_dir():
    inspect_dir = Path("inspect")
    inspect_dir.mkdir(exist_ok=True)
    yield


@pytest.fixture
def flask_test_context(app, monkeypatch):
    """Creates a proper Flask test request context and configures it for testing.

    This fixture:
    1. Creates a test request context using Flask's built-in test_request_context
    2. Ensures request.is_secure is properly set for protocol determination

    Use this fixture in any test that needs to access Flask request context
    (e.g., when using flask.request or other request-dependent functionality)
    """

    class MockRequest:
        is_secure = False

    monkeypatch.setattr("flask.request", MockRequest())

    with app.test_request_context():
        yield


def save_email_content(email_str: str, filename: str):
    msg = email.message_from_string(email_str)
    for part in msg.walk():
        content_type = part.get_content_type()
        payload = part.get_payload(decode=True)

        if not payload:
            continue

        if content_type == "text/html":
            with open(f"inspect/{filename}.html", "w", encoding="utf-8") as f:
                f.write(payload.decode())
        elif content_type == "text/plain":
            with open(f"inspect/{filename}.txt", "w", encoding="utf-8") as f:
                f.write(payload.decode())


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


def test_notify_providers(
    mock_smtp, flask_test_context, sample_order, sample_provider, sample_line_items
):
    notifier = Notifier(flask_address="test.com")
    providers = [sample_provider]
    tokens = [f"{sample_order['id']}|{sample_provider['username']}"]

    notifier.notify_providers(providers, tokens, sample_order, sample_line_items)

    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()
    args = mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0]
    assert args[0] == notifier.sender_email
    assert args[1] == sample_provider["email"]
    assert "Une nouvelle commande ThalassHome !" in args[2]


def test_notify_customer(mock_smtp, flask_test_context, sample_provider):
    notifier = Notifier(flask_address="test.com")
    notifier.notify_customer(sample_provider, "customer@yopmail.com")

    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()
    args = mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0]
    assert args[0] == notifier.sender_email
    assert args[1] == "customer@yopmail.com"
    assert "ThalassHome - Contact prestataire" in args[2]


def test_notify_admins(
    mock_smtp, flask_test_context, sample_order, sample_provider, sample_line_items
):
    notifier = Notifier(flask_address="test.com")
    notifier.notify_admins(sample_order, sample_provider, sample_line_items)

    mock_smtp.return_value.__enter__.return_value.sendmail.assert_called_once()
    args = mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0]
    assert args[0] == notifier.sender_email
    assert args[1] == notifier.sender_email
    assert "Commande prise en charge par un prestataire" in args[2]


def test_accept_command(
    test_db_client,
    mock_smtp,
    flask_test_context,
    sample_provider,
    sample_order_line_item,
):
    sample_order, sample_line_items = sample_order_line_item
    result = accept_order(
        f"{sample_order['id']}|{sample_provider['username']}", flask_address="test.com"
    )

    assert "La prise en charge de la commande a bien été accepté" in result
    assert (
        mock_smtp.return_value.__enter__.return_value.sendmail.call_count == 3
    )  # Provider + Customer + Admin notifications


def test_get_delivery_mens(sample_order_line_item):
    sample_order, _ = sample_order_line_item

    delivery_mens = get_delivery_mens(sample_order)

    assert len(delivery_mens) == 1
    assert "python" in delivery_mens[0]["username"]


def test_notification_flow_integration(
    client,
    test_db_client,
    mock_smtp,
    flask_test_context,
    sample_order_line_item,
    sample_provider,
):
    """Test the complete notification flow:
    1. Notify providers about new order
    2. Provider accepts the order by clicking the email link
    """
    sample_order, sample_line_items = sample_order_line_item

    # Step 1: Notify providers through the new service function
    notify_receive_command(sample_order, sample_line_items, flask_address="test.com")

    # Verify provider notification was sent
    assert mock_smtp.return_value.__enter__.return_value.sendmail.call_count == 1
    notification_args = (
        mock_smtp.return_value.__enter__.return_value.sendmail.call_args[0]
    )
    assert "Une nouvelle commande ThalassHome !" in notification_args[2]

    # Reset mock to track new emails
    mock_smtp.return_value.__enter__.return_value.sendmail.reset_mock()

    # Step 2: Simulate provider clicking accept link - should show confirmation page
    token = f"{sample_order['id']}|{sample_provider['username']}"
    response = client.get(f"/delivery_men/orders/{token}/accept")

    assert response.status_code == 200
    assert "Confirmation de prise en charge" in response.data.decode()
    assert (
        "Voulez-vous vraiment prendre en charge cette commande"
        in response.data.decode()
    )

    # Step 3: Simulate confirming the acceptance via POST
    response = client.post(f"/delivery_men/orders/{token}/accept")
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
    assert updated_order["status"] == "assigned"


def test_accept_order_confirmation_page(
    client, test_db_client, sample_order_line_item, sample_provider
):
    """Test that the confirmation page displays correctly"""
    sample_order, _ = sample_order_line_item
    token = f"{sample_order['id']}|{sample_provider['username']}"

    # Test normal case - should show confirmation form
    response = client.get(f"/delivery_men/orders/{token}/accept")
    assert response.status_code == 200
    assert "Confirmation de prise en charge" in response.data.decode()
    assert (
        "Voulez-vous vraiment prendre en charge cette commande"
        in response.data.decode()
    )

    # When order doesn't exist
    non_existent_token = f"999999|{sample_provider['username']}"
    response = client.get(f"/delivery_men/orders/{non_existent_token}/accept")
    assert response.status_code == 200
    assert "La commande n&#39;existe plus." in response.data.decode()

    # When order is already accepted by another delivery person
    test_db_client.update_table(
        "orders",
        {"delivery_men_id": sample_provider["id"] + 1},  # Different delivery person
        conditions={"id": sample_order["id"]},
    )

    response = client.get(f"/delivery_men/orders/{token}/accept")
    assert response.status_code == 200
    assert (
        "La commande a déjà été acceptée par un autre livreur."
        in response.data.decode()
    )


def test_accept_order_same_delivery_person(
    client, test_db_client, sample_order_line_item, sample_provider
):
    """Test when the same delivery person tries to accept again"""
    sample_order, _ = sample_order_line_item
    token = f"{sample_order['id']}|{sample_provider['username']}"

    # First, accept the order
    test_db_client.update_table(
        "orders",
        {"delivery_men_id": sample_provider["id"]},
        conditions={"id": sample_order["id"]},
    )

    # Try to access the confirmation page again
    response = client.get(f"/delivery_men/orders/{token}/accept")
    assert response.status_code == 200
    assert "Vous avez déjà accepté cette commande." in response.data.decode()


def test_accept_order_post(
    client, test_db_client, mock_smtp, sample_order_line_item, sample_provider
):
    """Test the POST endpoint that actually accepts the order"""
    sample_order, sample_line_items = sample_order_line_item
    token = f"{sample_order['id']}|{sample_provider['username']}"

    # Test successful acceptance
    response = client.post(f"/delivery_men/orders/{token}/accept")
    assert response.status_code == 200
    assert (
        "La prise en charge de la commande a bien été accepté" in response.data.decode()
    )

    # Verify that emails were sent
    assert mock_smtp.return_value.__enter__.return_value.sendmail.call_count == 3

    # Verify database was updated
    updated_order = test_db_client.select_from_table(
        "orders",
        select_columns="*",
        conditions={"id": sample_order["id"]},
        single=True,
    )
    assert updated_order["delivery_men_id"] == sample_provider["id"]
    assert updated_order["status"] == "assigned"

    # Try to accept again - should fail
    response = client.post(f"/delivery_men/orders/{token}/accept")
    assert (
        "La commande a déjà été accepté par un autre livreur" in response.data.decode()
    )
