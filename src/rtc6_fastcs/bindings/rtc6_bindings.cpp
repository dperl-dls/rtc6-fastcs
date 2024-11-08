#include <pybind11/pybind11.h>
#include "/usr/include/scanlab/rtc6.h"
#include <cstdint>
#include <string>

namespace py = pybind11;

class rtc_error : public std::runtime_error
{
    using std::runtime_error::runtime_error;
};

// Utilities for testing - TODO remove when things are working

int add(int i, int j)
{
    return i + j;
}

int throw_rtc_error(const char *errorText)
{
    throw rtc_error(errorText);
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

// RTC error codes
const uint ERROR_NO_ERROR = 0U;
const uint ERROR_NO_CARD = 1U;
const uint ERROR_VERSION_MISMATCH = 256U;

// Utilities for internal use

void init_dll()
{
    const auto initLib = init_rtc6_dll();
    if (initLib != ERROR_NO_ERROR)
    {
        if (initLib & ERROR_VERSION_MISMATCH || initLib & ERROR_NO_CARD)
        {
            // These errors only pertain to PCIe boards
        }
        else
        {
            throw rtc_error("Initialisation of the RTC6 library failed with error code: " + std::to_string(initLib));
        }
    }
}

std::string failed_text(std::string task, int card, int errorcode)
{
    return task + " for card " + std::to_string(card) + " failed with error code: " + std::to_string(errorcode);
}

int load_program_and_correction_files(uint card, char *programFilePath, char *correctionFilePath)
{ // DAT, ETH/OUT and RBF need to be in the current working directory
    const auto loadProgram = n_load_program_file(card, programFilePath);
    if (loadProgram != ERROR_NO_ERROR)
    {
        throw rtc_error(failed_text("n_load_program_file", card, loadProgram));
    }
    // Acquire board for further access
    const auto acquire = acquire_rtc(card);
    if (acquire != card)
    {
        throw rtc_error(failed_text("acquire_rtc", card, loadProgram));
    }
    // Load 2D correction file as table 1
    const auto loadCorrection = n_load_correction_file(card, correctionFilePath, 1, 2);
    if (loadCorrection != ERROR_NO_ERROR)
    {
        throw rtc_error(failed_text("n_load_correction_file", card, loadCorrection));
    }
    // select_cor_table( 1, 0 ); is done internally. Call select_cor_table, if you want a different setting.
    return n_get_serial_number(card);
}

// Real functions which we expect to use and expose

void connect(const char *ipStr, char *programFilePath, char *correctionFilePath)
{
    init_dll();

    // The library allows for connecting to multiple cards, but we just use one
    int cardNo = eth_assign_card_ip(eth_convert_string_to_ip(ipStr), 0);
    int result = select_rtc(cardNo);
    if (result != cardNo)
    {
        throw rtc_error("select_rtc failed with error: " + std::to_string(result) + ". Most likely, a card was not found at the given IP.");
    }
    auto serialNum = load_program_and_correction_files(cardNo, programFilePath, correctionFilePath);
}

void close_connection()
{
}

PYBIND11_MODULE(rtc6_bindings, m)
{
    m.doc() = "bindings for the scanlab rtc6 ethernet laser controller"; // optional module docstring
    py::register_exception<rtc_error>(m, "RtcError");

    // Real functions which are intended to be used
    m.def("connect", &connect, "connect to the eth-box at the given IP", py::arg("ip_string"), py::arg("program_file_path"), py::arg("correction_file_path"));
    m.def("close", &close_connection, "close the open connection, if any");

    // Just for testing - TODO remove these when things are going
    m.def("add", &add, "A function that adds two numbers", py::arg("i"), py::arg("j"));
    m.def("throw_rtc_error", &throw_rtc_error, "throw an exception with the given text", py::arg("error_text"));
    m.def("ip_str_to_int", &ip_str_to_int, "convert IP address from string to int", py::arg("ip_string"));
    m.def("ip_int_to_str", &ip_int_to_str, "convert IP address from int to string", py::arg("ip_int"));
}
