#include <iostream>
#include <string>
#include <iomanip>
#include <vector>
#include <regex>
#include <sstream>
#include <ctime>
#include <cstdlib>
#include <algorithm>
#include <chrono>
#include <array>

using namespace std;

// ANSI renk kodları
string cyan    = "\033[96m";
string magenta = "\033[95m";
string green   = "\033[92m";
string yellow  = "\033[93m";
string red     = "\033[91m";
string bold    = "\033[1m";
string reset   = "\033[0m";

void print_table_header() {
    cout << cyan << "╝── Boot History ──╞\n";
    cout << cyan << "║   " << bold << "Boot Time" << reset << cyan
         << "     ║ " << bold << "Shutdown" << reset << cyan
         << "      ║ " << bold << "Uptime" << reset << cyan
         << "  ║ " << bold << "Exit" << reset << cyan
         << "  ║ " << bold << "Kernel" << reset << cyan << " ║\n";
    cout << "╟──────────────────────┼──────────────────┼─────────┼─────┼──────────╜" << reset << endl;
}

void print_table_row(const string& boot_time, const string& shutdown,
                     const string& uptime, const string& exit_type,
                     const string& kernel)
{
    string exit_colored;

    if (exit_type == "shutdown")      exit_colored = green + exit_type + reset;
    else if (exit_type == "crash")    exit_colored = bold + red + exit_type + reset;
    else if (exit_type == "running")  exit_colored = yellow + exit_type + reset;
    else                              exit_colored = exit_type;

    cout << "║ " << setw(16) << left << boot_time
         << " ║ " << setw(14) << left << shutdown
         << " ║ " << setw(8) << right << uptime
         << " ║ " << setw(6) << exit_colored
         << " ║ " << setw(10) << right << kernel << " ║" << endl;
}

struct Entry {
    string boot_time;
    string shutdown;
    string uptime;
    string exit_type;
    string kernel;
};

string exec(const char* cmd) {
    array<char, 128> buffer;
    string result;
    FILE* pipe = popen(cmd, "r");
    if (!pipe) return "ERROR";
    while (fgets(buffer.data(), buffer.size(), pipe) != nullptr) {
        result += buffer.data();
    }
    pclose(pipe);
    return result;
}

string format_tm(const tm& t, bool long_date) {
    char buf[64];
    if (long_date)
        strftime(buf, sizeof(buf), "%b %d, %Y %H:%M", &t);
    else
        strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M", &t);
    return string(buf);
}

string format_duration(const string& dur) {
    if (dur == "00:00") return "a few sec";
    if (dur.find('+') != string::npos) {
        int d, h, m;
        sscanf(dur.c_str(), "%d+%d:%d", &d, &h, &m);
        ostringstream out;
        out << d << "d " << h << "h " << m << "m";
        return out.str();
    } else {
        int h, m;
        sscanf(dur.c_str(), "%d:%d", &h, &m);
        ostringstream out;
        out << h << "h " << m << "m";
        return out.str();
    }
}

tm parse_datetime(const string& timestr, int year) {
    tm t = {};
    istringstream ss(to_string(year) + " " + timestr);
    ss >> get_time(&t, "%Y %a %b %d %H:%M");
    return t;
}

tm add_duration(const tm& start, const string& duration) {
    tm result = start;
    time_t base = mktime(&result);

    int d = 0, h = 0, m = 0;
    if (duration.find('+') != string::npos)
        sscanf(duration.c_str(), "%d+%d:%d", &d, &h, &m);
    else
        sscanf(duration.c_str(), "%d:%d", &h, &m);

    base += d * 86400 + h * 3600 + m * 60;
    result = *localtime(&base);
    return result;
}

int main(int argc, char* argv[]) {
    bool long_date = false;
    for (int i = 1; i < argc; ++i)
        if (string(argv[i]) == "--long-date")
            long_date = true;

    string output = exec("last -x");
    istringstream ss(output);
    string line;

    time_t current_time = chrono::system_clock::to_time_t(chrono::system_clock::now());
    tm* now = localtime(&current_time);
    int year = now->tm_year + 1900;

    regex pattern(R"(reboot\s+system boot\s+([\w\.\-\*]+)?\s+(\w{3}\s+\w{3}\s+\d+\s+\d+:\d+)(?:\s+-\s+(\w{3}\s+\d+:\d+|\d+:\d+|crash|down|still running))?\s+\(([^)]+)\))");

    vector<Entry> entries;
    while (getline(ss, line)) {
        if (line.rfind("reboot", 0) != 0) continue;
        smatch match;
        if (regex_search(line, match, pattern)) {
            tm start_tm = parse_datetime(match[2], year);
            string dur = match[4];
            tm end_tm = (match[3].matched && dur != "") ? add_duration(start_tm, dur) : start_tm;

            entries.push_back({
                format_tm(start_tm, long_date),
                match[3].matched ? format_tm(end_tm, long_date) : "running",
                format_duration(dur),
                match[3].matched ? (match[3].str() == "crash" ? "crash" : "shutdown") : "running",
                match[1].matched ? match[1].str() : "-"
            });
        }
    }

    sort(entries.begin(), entries.end(), [](const Entry& a, const Entry& b) {
        tm at = {}, bt = {};
        istringstream sa(a.boot_time), sb(b.boot_time);
        sa >> get_time(&at, "%Y-%m-%d %H:%M");
        sb >> get_time(&bt, "%Y-%m-%d %H:%M");
        return mktime(&at) > mktime(&bt);
    });

    print_table_header();
    for (const auto& e : entries) {
        print_table_row(e.boot_time, e.shutdown, e.uptime, e.exit_type, e.kernel);
    }

    return 0;
}