from pathlib import Path

APP_DIR = Path(__file__).parent
ROOT_DIR = APP_DIR.parent
ENV_DIR = ROOT_DIR / "env"
DB_DIR = APP_DIR / "db"

REQUIRED_VARIABLES = {
    "EMAIL_SENDER_PASSWORD",
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "SHOPIFY_ADMIN_API_ACCESS_TOKEN",
}

JACUZZI6P = "jacuzzi6p"
JACUZZI4P = "jacuzzi4p"


def normalize_jac_string(string):
    if "jac" not in string.lower():
        raise ValueError("String does not contain jac")
    if "4" in string:
        res = JACUZZI4P
    elif "6" in string:
        res = JACUZZI6P
    else:
        raise ValueError(f"Was unable to jac-normalize string: {string}")
    return res


def parse_rent_duration_jac(string):
    """
    :return: the number of days the jacuzzi is rent (if applicable)
    """
    if "jac" not in string.lower():
        raise ValueError("String does not contain jac")
    if "1" in string:
        res = 1
    elif "2" in string:
        res = 2
    else:
        raise ValueError(f"Was unable to parse number of rent days of jac in: {string}")
    return res
