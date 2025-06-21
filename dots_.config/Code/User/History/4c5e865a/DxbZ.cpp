#include <iostream>
#include <string>
#include <iomanip>
#include <vector>
#include <regex>
#include <sstream>
#include <iomanip>
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
    cout << cyan << "╭─────────────────────────────────── Boot History ───────────────────────────────────╮\n";
    cout << "│                    ╷                  ╷            ╷          ╷                    │\n";
    cout << "│   " << bold << "Boot Time" << reset << cyan
         << "        │ " << bold << "Shutdown" << reset << cyan
         << "         │ " << bold << "  Uptime   " << reset << cyan
         << "│  " << bold << "Exit" << reset << cyan
         << "   │           " << bold << "Kernel" << reset << cyan << "   │\n";
    cout << "│ ╺━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━╸ │\n" << reset;
}

void print_table_row(const string& boot_time,
                     const string& shutdown,
                     const string& uptime,
                     const string& exit_type,
                     const string& kernel)
{
    string exit_colored;

    if (exit_type == "shutdown")      exit_colored = green + exit_type + reset;
    else if (exit_type == "crash")    exit_colored = bold + red + exit_type + reset;
    else if (exit_type == "running")  exit_colored = yellow + exit_type + reset;
    else                              exit_colored = exit_type;

    cout << "│   " << setw(16) << left << boot_time
         << "│ " << setw(16) << left << shutdown
         << "│ " << setw(10) << right << uptime << " "
         << "│ " << setw(8) << exit_colored
         << "│ " << setw(18) << right << kernel << "   │\n";
}

struct Entry {
    string type;
    string kernel;
    tm start_dt;
    string duration;
    string end;
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
            Entry e;
            e.type = "reboot";
            e.kernel = match[1].matched ? match[1].str() : "-";
            e.start_dt = parse_datetime(match[2], year);
            e.end = match[3].matched ? match[3].str() : "still running";
            e.duration = match[4];
            entries.push_back(e);
        }
    }

    sort(entries.begin(), entries.end(), [](const Entry& a, const Entry& b) {
        return mktime((tm*)&a.start_dt) > mktime((tm*)&b.start_dt);
    });

    cout << left << setw(22) << "Boot Time"
         << setw(22) << "Shutdown"
         << setw(12) << "Uptime"
         << setw(10) << "Exit"
         << "Kernel" << endl;
    cout << string(80, '-') << endl;

    print_table_header();
    for (const auto& e : entries) {
        print_table_row(
        format_datetime(e.boot_time),
        format_datetime(e.shutdown),
        e.uptime,
        e.exit_type,
        e.kernel
    );
    }

    return 0;
}
