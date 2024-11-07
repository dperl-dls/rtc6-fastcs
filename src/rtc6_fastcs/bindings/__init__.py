from rtc6_fastcs.bindings import rtc6_bindings


def add(a: int, b: int) -> int:
    return rtc6_bindings.add(a, b)


def ip_str_to_int(ip_string: str) -> int:
    return rtc6_bindings.ip_str_to_int(ip_string)
