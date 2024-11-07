#include <pybind11/pybind11.h>

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(rtc6_bindings, m) {
    m.doc() = "bindings for the scanlab rtc6 ethernet laser controller"; // optional module docstring

    m.def("add", &add, "A function that adds two numbers");
}
