import pytest

from capstone.middleware.message_translator import translate_messages


def test_translates_json():
    msg = translate_messages('{"type": "STATUS", "amr": "AMR_7", "state": "ARRIVED"}')
    assert msg["type"] == "STATUS" and msg["state"] == "ARRIVED"


def test_rejects_message_without_type():
    with pytest.raises(ValueError):
        translate_messages('{"amr": "AMR_7"}')
