REQUIRED_VARIABLES = {"email_sender_password",
                      "SUPABASE_URL",
                      "SUPABASE_KEY",
                      }

JACUZZI2P='jacuzzi2p'
JACUZZI4P='jacuzzi4p'

def normalize_jac_string(string):
    if 'jac' not in string:
        raise ValueError("String does not contain jac")
    if '4' in string:
        res = JACUZZI4P
    elif '2' in string:
        res = JACUZZI2P
    else:
        raise ValueError(f"Was unable to jac-normalize string: {string}")
    return res
