from rtc6_fastcs import bindings


def test_add():
    sum = bindings.add(4, 5)
    assert sum == 9
    sum = bindings.add(7, 13)
    assert sum == 20


def test_ip_conversion():
    result = bindings.ip_str_to_int("123.0.0.1")
    assert result == 16777339
