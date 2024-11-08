import pytest


@pytest.mark.needs_librtc6
class TestBindings:
    from rtc6_fastcs import bindings

    def test_add(self):
        sum = self.bindings.add(4, 5)
        assert sum == 9
        sum = self.bindings.add(7, 13)
        assert sum == 20

    def test_ip_conversion(self):
        result = self.bindings.ip_str_to_int("123.0.0.1")
        assert result == 16777339
        back = self.bindings.ip_int_to_str(result)
        assert back == "123.0.0.1"

        result = self.bindings.ip_str_to_int("123.123.123.123")
        assert result == 2071690107
        back = self.bindings.ip_int_to_str(result)
        assert back == "123.123.123.123"
