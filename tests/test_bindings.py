from rtc6_fastcs.rtc6_bindings.build import rtc6_bindings


def test_add():
    assert rtc6_bindings.add(2, 3) == 5
