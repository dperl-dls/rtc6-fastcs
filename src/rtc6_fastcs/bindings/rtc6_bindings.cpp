#include <pybind11/pybind11.h>
#include "/usr/include/scanlab/rtc6.h"

int add(int i, int j) {
    return i + j;
}

int ip_str_to_int(const char* str) {
    return eth_convert_string_to_ip(str);
}

PYBIND11_MODULE(rtc6_bindings, m) {
    m.doc() = "bindings for the scanlab rtc6 ethernet laser controller"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");

    m.def("ip_str_to_int", &ip_str_to_int, "convert IP address from string to int");
}
