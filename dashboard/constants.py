REQUIRED_VARIABLES = {"email_sender_password",
                      "SUPABASE_URL",
                      "SUPABASE_KEY",
                      }

JACUZZI6P= 'jacuzzi6p'
JACUZZI4P='jacuzzi4p'

def normalize_jac_string(string):
    if 'jac' not in string.lower():
        raise ValueError("String does not contain jac")
    if '4' in string:
        res = JACUZZI4P
    elif '6' in string:
        res = JACUZZI6P
    else:
        raise ValueError(f"Was unable to jac-normalize string: {string}")
    return res
