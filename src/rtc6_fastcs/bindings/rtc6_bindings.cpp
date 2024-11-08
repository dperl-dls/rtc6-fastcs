#include <pybind11/pybind11.h>
#include "/usr/include/scanlab/rtc6.h"
#include <cstdint>
#include <string>

namespace py = pybind11;

int add(int i, int j)
{
    return i + j;
}

int ip_str_to_int(const char *ipStr)
{
    return eth_convert_string_to_ip(ipStr);
}

std::string ip_int_to_str(int ip)
{
    char out[] = "123.123.123.123";
    auto out_ptr = reinterpret_cast<std::uintptr_t>(&out);
    eth_convert_ip_to_string(ip, out_ptr);
    return out;
}

void connect(const char *ipStr)
{
}

void close_connection()
{
}

PYBIND11_MODULE(rtc6_bindings, m)
{
    m.doc() = "bindings for the scanlab rtc6 ethernet laser controller"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers", py::arg("i"), py::arg("j"));

    m.def("ip_str_to_int", &ip_str_to_int, "convert IP address from string to int", py::arg("ip_string"));

    m.def("ip_int_to_str", &ip_int_to_str, "convert IP address from int to string", py::arg("ip_int"));

    m.def("connect", &connect, "connect to the eth-box at the given IP", py::arg("ip_string"));

    m.def("close", &close_connection, "close the open connection, if any");
}
