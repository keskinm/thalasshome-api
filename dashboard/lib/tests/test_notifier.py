from unittest.mock import MagicMock, patch

import pytest

from dashboard.lib.notifier import Notifier


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("EMAIL_SENDER_PASSWORD", "test_password")


@pytest.fixture
def mock_smtp(mocker):
    return mocker.patch("smtplib.SMTP_SSL")


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


def test_accept_command(db_engine, mock_smtp, sample_provider, sample_order_line_item):
    sample_order, sample_line_items = sample_order_line_item
    notifier = Notifier(flask_address="test.com")
    result = notifier.accept_command(
        f"{sample_order['id']}|{sample_provider['username']}"
    )

    assert "La prise en charge de la commande a bien été accepté" in result
    assert (
        mock_smtp.return_value.__enter__.return_value.sendmail.call_count == 3
    )  # Provider + Customer + Admin notifications


def test_get_delivery_mens(mocker, sample_order):
    mock_supabase = MagicMock()
    mock_supabase.rpc.return_value.execute.return_value.data = [
        {"username": "provider1"}
    ]

    with patch("dashboard.lib.notifier.SUPABASE_CLI", mock_supabase):
        delivery_mens = Notifier.get_delivery_mens(sample_order)

    assert len(delivery_mens) == 1
    assert delivery_mens[0]["username"] == "provider1"
    mock_supabase.rpc.assert_called_once_with(
        "check_delivery_men_around_point",
        {
            "in_shipping_lon": sample_order["shipping_lon"],
            "in_shipping_lat": sample_order["shipping_lat"],
        },
    )
