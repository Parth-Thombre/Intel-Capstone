import json


def translate_messages(raw_message: str) -> dict:
    """Turn a raw vendor/MCS message into a typed dict.

    Placeholder format (JSON). Replace once the sponsor's sample messages arrive.
    """
    msg = json.loads(raw_message)
    if "type" not in msg and "message_type" not in msg:  # 'message_type' is the INTERFACES.md name
        raise ValueError("message has no 'type' or 'message_type'")
    return msg
