#include <iostream>
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
        if (!line.starts_with("reboot")) continue;
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

    for (const auto& e : entries) {
        tm shutdown_dt = add_duration(e.start_dt, e.duration);
        string boot_str = format_tm(e.start_dt, long_date);
        string shut_str = (e.end == "still running") ? "still running" : format_tm(shutdown_dt, long_date);

        string exit_type = (e.end == "crash") ? "crash" : ((e.end == "still running") ? "running" : "shutdown");

        cout << setw(22) << boot_str
             << setw(22) << shut_str
             << setw(12) << format_duration(e.duration)
             << setw(10) << exit_type
             << e.kernel << endl;
    }

    return 0;
}
