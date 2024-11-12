#include <pybind11/pybind11.h>
#include <cstdint>
#include <string>

#include "scanlab/rtc6.h"
#include "boost/format.hpp"

namespace py = pybind11;
using boost::format;

// Bindings from the rtc6 DLL to python
// This should simplify some functions where possible,
// but not hold state, since that is more the job of the IOC

// Custom exceptions allow us to catch RtcError and derivatives in python-land
// Examples for use of the RTC6 library often involve returning int error codes,
// here we interrogate replace those with exceptions to be more pythonic
class rtc_error : public std::runtime_error
{
    using std::runtime_error::runtime_error;
};
class rtc_connection_error : public rtc_error
{
    using rtc_error::rtc_error;
};

// RTC error codes
const uint ERROR_NO_ERROR = 0U;
const uint ERROR_NO_CARD = 1U;
const uint ERROR_VERSION_MISMATCH = 256U;

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

// Utilities for internal use - TODO probably move these to a separate file
std::string ip_int_to_str(int ip) // remove this one from exposed functions
{
    char out[] = "123.123.123.123";
    auto out_ptr = reinterpret_cast<std::uintptr_t>(&out);
    eth_convert_ip_to_string(ip, out_ptr);
    return out;
}

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
            throw rtc_error(str(format("Initialisation of the RTC6 library failed with error code: %1%") % initLib));
        }
    }
}

std::string failed_text(std::string task, int card, int errorcode)
{
    return str(format("%1% for card %2%  failed with error code: %3%") % task % card % errorcode);
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
void check_conection()
{
    const int connection = eth_check_connection();
    if (!connection) // 1 if connection OK
    {
        throw rtc_connection_error("Checking connection to the eth box failed!");
    }
}

int connect(const char *ipStr, char *programFilePath, char *correctionFilePath)
{
    init_dll();

    // The library allows for connecting to multiple cards, but we just use one
    // See manual page 855 for info about the conversion of IP address to an int
    int cardNo = eth_assign_card_ip(eth_convert_string_to_ip(ipStr), 0);
    int result = acquire_rtc(cardNo);
    if (result != cardNo)
    {
        throw rtc_error(str(format("acquire_rtc for card %1% failed with error: %2%. Most likely, a card was not found at the given IP address: %3%. Alternatively, it may already be acquired by another process.") % cardNo % result % ipStr));
    }
    return load_program_and_correction_files(cardNo, programFilePath, correctionFilePath);
}

struct CardInfo
{
    // Holder for card info from the manual page 354
public:
    CardInfo(const int32_t infoArray[])
    {
        firmwareVersion = infoArray[0];
        serialNumber = infoArray[1];
        ipStr = ip_int_to_str(infoArray[8]);
        isAcquired = (infoArray[5] == 1);
    };
    int getFirmwareVersion() { return firmwareVersion; };
    int getSerialNumber() { return serialNumber; };
    std::string getIpStr() { return ipStr; };
    bool getIsAcquired() { return isAcquired; };

private:
    int firmwareVersion;
    int serialNumber;
    std::string ipStr;
    bool isAcquired;
};

CardInfo get_card_info()
{
    // check_conection(); // not working ?
    int32_t out[16];
    auto out_ptr = reinterpret_cast<std::uintptr_t>(&out);
    eth_get_card_info(1, out_ptr);
    return CardInfo(out);
}

int get_last_eth_error()
{
    return eth_get_last_error();
}

void close_connection()
{
    // TODO: check if there is anything to release
    int releasedCard = release_rtc(1);
    if (!releasedCard)
    {
        throw rtc_connection_error("Could not release card - maybe it was not acquired?");
    }
}

// Definition of our exposed python module - things must be registered here to be accessible
PYBIND11_MODULE(rtc6_bindings, m)
{
    m.doc() = "bindings for the scanlab rtc6 ethernet laser controller"; // optional module docstring
    py::register_exception<rtc_error>(m, "RtcError");
    py::register_exception<rtc_connection_error>(m, "RtcConnectionError");

    // Structs
    py::class_<CardInfo>(m, "CardInfo")
        .def_property("firmware_version", &CardInfo::getFirmwareVersion, nullptr)
        .def_property("serial_number", &CardInfo::getSerialNumber, nullptr)
        .def_property("ip_address", &CardInfo::getIpStr, nullptr)
        .def_property("is_acquired", &CardInfo::getIsAcquired, nullptr);

    // Real functions which are intended to be used
    m.def("check_connection", &check_conection, "check the active connection to the eth box: throws RtcConnectionError on failure, otherwise does nothing.");
    m.def("connect", &connect, "connect to the eth-box at the given IP", py::arg("ip_string"), py::arg("program_file_path"), py::arg("correction_file_path"));
    m.def("close", &close_connection, "close the open connection, if any");
    m.def("close_again", &close_connection, "close the open connection, if any");
    m.def("get_card_info", &get_card_info, "get info for the connected card; throws RtcConnectionError on failure");
    m.def("get_last_error", &get_last_eth_error, "get the last error for an ethernet command");

    // Just for testing - TODO remove these when things are going
    m.def("add", &add, "A function that adds two numbers", py::arg("i"), py::arg("j"));
    m.def("throw_rtc_error", &throw_rtc_error, "throw an exception with the given text", py::arg("error_text"));
    m.def("ip_str_to_int", &ip_str_to_int, "convert IP address from string to int", py::arg("ip_string"));
    m.def("ip_int_to_str", &ip_int_to_str, "convert IP address from int to string", py::arg("ip_int"));
}
