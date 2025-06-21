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
const string bright_cyan    = "\033[96m";
const string bright_magenta = "\033[95m";
const string green          = "\033[92m";
const string yellow         = "\033[93m";
const string red            = "\033[91m";
const string bold           = "\033[1m";
const string reset          = "\033[0m";

// Tablo sütun genişlikleri
constexpr int col_boot_time = 18;
constexpr int col_shutdown  = 18;
constexpr int col_uptime    = 12;
constexpr int col_exit      = 10;
constexpr int col_kernel    = 18;

// Boşluklu hizalama için yardımcı fonksiyon
string color_wrap(const string& text, const string& color_code, int width, bool left_align = true) {
    int visible_len = (int)text.length();
    if (visible_len > width) visible_len = width; // sınırla

    int pad_len = width - visible_len;
    if (pad_len < 0) pad_len = 0;

    string padded;
    if (left_align) {
        padded = text + string(pad_len, ' ');
    } else {
        padded = string(pad_len, ' ') + text;
    }
    return color_code + padded + reset;
}


// Zamanı formatlama (yyyy-mm-dd HH:MM)
string format_tm(const tm& t) {
    char buf[64];
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M", &t);
    return string(buf);
}

// Duration formatlama (ör: 5h 33m)
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

struct Entry {
    string type;
    string kernel;
    tm start_dt;
    string duration;
    string end_str;
    string exit_type; // shutdown, crash, running vb.
};

// Komut çalıştırma ve çıktı alma
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

// Tablo başlığı çizimi
void print_table_header() {
    cout << bright_cyan
         << "╭─────────────────────────────────── Boot History ───────────────────────────────────╮\n"
         << "│                    ╷                  ╷            ╷          ╷                    │\n"
         << "│ "
         << color_wrap("Boot Time", bright_cyan, col_boot_time)
         << "│ "
         << color_wrap("Shutdown", bright_magenta, col_shutdown)
         << "│ "
         << color_wrap("Uptime", green, col_uptime, false)
         << " │ "
         << color_wrap("Exit", green, col_exit, false)
         << " │ "
         << color_wrap("Kernel", yellow, col_kernel, false)
         << " │\n"
         << "│ ╺━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━╸ │"
         << reset << "\n";
}

// Tablo satırı yazdırma
void print_table_row(const Entry& e) {
    // Formatlar
    string boot_str = format_tm(e.start_dt);
    string shutdown_str = e.end_str;

    string uptime_str = format_duration(e.duration);

    // Exit sütunu renkleri
    string exit_colored;
    if (e.exit_type == "shutdown") exit_colored = green + e.exit_type + reset;
    else if (e.exit_type == "crash") exit_colored = bold + red + e.exit_type + reset;
    else exit_colored = e.exit_type;

    // Kernel sarı renk
    string kernel_colored = yellow + e.kernel + reset;

    // Hücreleri hizala ve renk kodları ile sar
    cout << "│ "
         << color_wrap(boot_str, bright_cyan, col_boot_time)
         << "│ "
         << color_wrap(shutdown_str, bright_magenta, col_shutdown)
         << "│ "
         << color_wrap(uptime_str, green, col_uptime, false)
         << " │ "
         << setw(col_exit) << right << exit_colored
         << " │ "
         << color_wrap(kernel_colored, "", col_kernel, false) // Kernel zaten sarıldı, tekrar renk kodu eklenmez
         << " │\n";
}

// main
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
            e.end_str = match[3].matched ? match[3].str() : "still running";
            e.duration = match[4];
            // Exit type çıkarımı:
            if (e.end_str == "still running") e.exit_type = "running";
            else if (e.end_str == "crash" || e.end_str == "down") e.exit_type = "crash";
            else e.exit_type = "shutdown";

            entries.push_back(e);
        }
    }

    sort(entries.begin(), entries.end(), [](const Entry& a, const Entry& b) {
        return mktime((tm*)&a.start_dt) > mktime((tm*)&b.start_dt);
    });

    print_table_header();

    for (const auto& e : entries) {
        print_table_row(e);
    }

    // Alt çizgi ve son satır
    cout << "│                    ╵                  ╵            ╵          ╵                    │\n";
    cout << "╰────────────────────────────────────────────────────────────────────────────────────╯\n";

    return 0;
}
