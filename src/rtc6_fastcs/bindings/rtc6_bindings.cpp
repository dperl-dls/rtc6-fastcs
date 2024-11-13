#include <pybind11/pybind11.h>
#include <cstdint>
#include <string>

#include "scanlab/rtc6.h"
#include "boost/format.hpp"
#include <bitset>

namespace py = pybind11;
using boost::format;

// Bindings from the rtc6 DLL to python
// This should simplify some functions where possible,
// but not hold state, since that is more the job of the IOC

// Custom exceptions allow us to catch RtcError and derivatives in python-land
// Examples for use of the RTC6 library often involve returning int error codes,
// here we interrogate replace those with exceptions to be more pythonic
class RtcError : public std::runtime_error
{
    using std::runtime_error::runtime_error;
};
class RtcConnectionError : public RtcError
{
    using RtcError::RtcError;
};
class RtcListError : public RtcError
{
    using RtcError::RtcError;
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
    throw RtcError(errorText);
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
            throw RtcError(str(format("Initialisation of the RTC6 library failed with error code: %1%") % initLib));
        }
    }
}

std::string failed_text(std::string task, int card, int errorCode)
{
    return str(format("%1% for card %2%  failed with error code: %3%") % task % card % errorCode);
}
std::string failed_text(std::string task, int card, int errorCode, int pageNo)
{
    return str(format("%1% for card %2%  failed with error code: %3%. Details about this error can be found on page %4% of the manual.") % task % card % errorCode % pageNo);
}

std::string parse_error(int errorCode)
{
    std::string out = "";
    std::bitset<32> errorBits(errorCode);
    std::string errorStrings[32] = {
        "No board found",                                           // 0
        "Access denied. Could indicate wrong program files. ",      // 1
        "Command not forwarded. ",                                  // 2
        "No response from board. ",                                 // 3
        "Invalid parameter. ",                                      // 4
        "Busy: list processing in wrong state for command. ",       // 5
        "List command rejected: invalid input pointer. ",           // 6
        "Ignored: list command converted to nop. ",                 // 7
        "Version mismatch error. ",                                 // 8
        "Download verification error. ",                            // 9
        "PCIe command sent to Eth board or vice-versa. ",           // 10
        "Windows memory request failed. ",                          // 11
        "Download error. The values have possibly not been saved.", // 12
        "General ethernet error",                                   // 13
        "",                                                         // 14: Reserved
        "Unsupported Windows version. ",                            // 15
    };
    for (int i = 0; i != 32; i++)
    {
        if (errorBits[i])
        {
            out += errorStrings[i];
        }
    };
    return out;
}

int load_program_and_correction_files(uint card, char *programFilePath, char *correctionFilePath)
{ // DAT, ETH/OUT and RBF need to be in the current working directory
    const auto loadProgram = n_load_program_file(card, programFilePath);
    // TODO: improve error messages for specific errors.
    if (loadProgram != ERROR_NO_ERROR)
    {
        throw RtcError(failed_text("n_load_program_file", card, loadProgram, 489));
    }
    // Acquire board for further access
    const auto acquire = acquire_rtc(card);
    if (acquire != card)
    {
        throw RtcError(failed_text("acquire_rtc", card, loadProgram));
    }
    // Load 2D correction file as table 1
    const auto loadCorrection = n_load_correction_file(card, correctionFilePath, 1, 2);
    if (loadCorrection != ERROR_NO_ERROR)
    {
        throw RtcError(failed_text("n_load_correction_file", card, loadCorrection, 474));
    }
    // select_cor_table( 1, 0 ); is done internally. Call select_cor_table, if you want a different setting.
    return n_get_serial_number(card);
}

// Real functions which we expect to use and expose
void clear_all_errors() { reset_error(-1); }

void check_conection()
{
    const int connection = eth_check_connection();
    if (!connection) // 1 if connection OK
    {
        const int error = get_error();
        const std::string errorString = parse_error(get_error());
        throw RtcConnectionError(str(format("Checking connection to the eth box failed! Result of check: %1%. Error %2%: %3%") % connection % error % errorString));
    }
}

std::string get_error_string()
{
    return parse_error(get_error());
}

int connect(const char *ipStr, char *programFilePath, char *correctionFilePath)
{
    init_dll();
    // The library allows for connecting to multiple cards, but we just use one
    // See manual page 855 for info about the conversion of IP address to an int
    int cardNo = eth_assign_card_ip(eth_convert_string_to_ip(ipStr), 0);
    int result = select_rtc(cardNo);
    if (result != cardNo)
    {
        const int error = get_error();
        throw RtcError(str(format("select_rtc for card %1% failed with result: %2%. Most likely, a card was not found at the given IP address: %3%. Alternatively, it may already be acquired by another process. Error code: %4%. Description: %5%") % cardNo % result % ipStr % error % parse_error(error)));
    }
    return load_program_and_correction_files(cardNo, programFilePath, correctionFilePath);
    const int error = get_error();
    if (error)
    {
        throw RtcError(str(format("Error loading program files: %1%") % parse_error(error)));
    }
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
    check_conection();
    int32_t out[16];
    auto out_ptr = reinterpret_cast<std::uintptr_t>(&out);
    eth_get_card_info(1, out_ptr);
    return CardInfo(out);
}

void init_list_loading(int listNo)
{
    set_start_list(listNo);
}
enum ListStatus
{
    LOAD1,
    LOAD2,
    READY1,
    READY2,
    BUSY1,
    BUSY2,
    USED1,
    USED2,
};
py::list get_list_statuses()
{
    py::list result;
    std::bitset<32> statuses(read_status());
    for (int status = 0; status != 8; status++)
    {
        if (statuses[status])
        {
            result.append(static_cast<ListStatus>(status));
        }
    }
    return result;
}

void close_connection()
{
    // TODO: check if there is anything to release
    int releasedCard = release_rtc(1);
    if (!releasedCard)
    {
        throw RtcConnectionError("Could not release card - maybe it was not acquired?");
    }
}

// Definition of our exposed python module - things must be registered here to be accessible
PYBIND11_MODULE(rtc6_bindings, m)
{
    m.doc() = "bindings for the scanlab rtc6 ethernet laser controller"; // optional module docstring
    py::register_exception<RtcError>(m, "RtcError");
    py::register_exception<RtcConnectionError>(m, "RtcConnectionError");
    py::register_exception<RtcListError>(m, "RtcListError");

    // Structs
    py::class_<CardInfo>(m, "CardInfo")
        .def_property("firmware_version", &CardInfo::getFirmwareVersion, nullptr)
        .def_property("serial_number", &CardInfo::getSerialNumber, nullptr)
        .def_property("ip_address", &CardInfo::getIpStr, nullptr)
        .def_property("is_acquired", &CardInfo::getIsAcquired, nullptr);

    py::enum_<ListStatus>(m, "ListStatus")
        .value("LOAD1", ListStatus::LOAD1)
        .value("LOAD2", ListStatus::LOAD2)
        .value("READY1", ListStatus::READY1)
        .value("READY2", ListStatus::READY2)
        .value("BUSY1", ListStatus::BUSY1)
        .value("BUSY2", ListStatus::BUSY2)
        .value("USED1", ListStatus::USED1)
        .value("USED2", ListStatus::USED2);

    // Real functions which are intended to be used
    m.def("check_connection", &check_conection, "check the active connection to the eth box: throws RtcConnectionError on failure, otherwise does nothing. If it fails, errors must be cleared afterwards.");
    m.def("connect", &connect, "connect to the eth-box at the given IP", py::arg("ip_string"), py::arg("program_file_path"), py::arg("correction_file_path"));
    m.def("close", &close_connection, "close the open connection, if any");
    m.def("get_card_info", &get_card_info, "get info for the connected card; throws RtcConnectionError on failure");
    m.def("init_list_loading", &init_list_loading, "initialise the given list (1 or 2)");
    m.def("get_list_statuses", &get_list_statuses, "get the statuses of the command lists");
    m.def("get_error", &get_error, "get the current error code. 0 is no error. table of errors is on p387, get_error_string() can be called for a human-readable version.");
    m.def("get_error_string", &get_error_string, "get human-readable error info");
    m.def("clear_errors", &clear_all_errors, "clear errors in the RTC6 library");

    // Taken directly from the library, might need to be updated with better typing, enums etc.
    m.def("get_last_error", &get_last_error, "get the last error for an ethernet command");
    m.def("set_laser_mode", &set_laser_mode, "set the mode of the laser, see p645", py::arg("mode"));
    m.def("set_laser_control", &set_laser_control, "set the control settings of the laser, see p641", py::arg("settings"));
    m.def("get_input_pointer", &get_input_pointer, "get the pointer of list input");
    m.def("config_list_memory", &config_list, "set the memory for each position list, see p330", py::arg("list_1_mem"), py::arg("list_2_mem"));
    m.def("load_list", &load_list, "set the pointer to load at position of list_no, see p330", py::arg("list_no"), py::arg("position"));

    m.def("get_io_status", &get_io_status, "---");
    m.def("get_list_space", &get_list_space, "---");
    m.def("get_config_list", &get_config_list, "---");
    m.def("get_rtc_mode", &get_rtc_mode, "---");
    m.def("get_temperature", &get_temperature, "---");

    // Just for testing - TODO remove these when things are going
    m.def("add", &add, "A function that adds two numbers", py::arg("i"), py::arg("j"));
    m.def("throw_rtc_error", &throw_rtc_error, "throw an exception with the given text", py::arg("error_text"));
    m.def("ip_str_to_int", &ip_str_to_int, "convert IP address from string to int", py::arg("ip_string"));
    m.def("ip_int_to_str", &ip_int_to_str, "convert IP address from int to string", py::arg("ip_int"));
}
