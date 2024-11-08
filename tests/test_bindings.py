import pytest


@pytest.mark.needs_librtc6
def test_add():
    from rtc6_fastcs import bindings

    sum = bindings.add(4, 5)
    assert sum == 9
    sum = bindings.add(7, 13)
    assert sum == 20


@pytest.mark.needs_librtc6
def test_ip_conversion():
    from rtc6_fastcs import bindings

    result = bindings.ip_str_to_int("123.0.0.1")
    assert result == 16777339
    back = bindings.ip_int_to_str(result)
    assert back == "123.0.0.1"

    result = bindings.ip_str_to_int("123.123.123.123")
    assert result == 2071690107
    back = bindings.ip_int_to_str(result)
    assert back == "123.123.123.123"
