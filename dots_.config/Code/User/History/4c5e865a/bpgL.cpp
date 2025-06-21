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

// Görünen karakter sayısını (renk kodları hariç) hesapla
int visible_length(const string& s) {
    int length = 0;
    bool in_escape = false;
    for (char c : s) {
        if (c == '\033') {
            in_escape = true;
            continue;
        }
        if (in_escape) {
            if (c == 'm')
                in_escape = false;
            continue;
        }
        length++;
    }
    return length;
}

// Boşluklu hizalama için yardımcı fonksiyon (renk kodlarını göz ardı ederek padding yapar)
string color_wrap(const string& text, const string& color_code, int width, bool left_align = true) {
    int visible_len = visible_length(text);
    if (visible_len > width) visible_len = width; // sınırla

    int pad_len = width - visible_len;
    if (pad_len < 0) pad_len = 0;

    string visible_text = text;
    if (visible_len < width) {
        if (left_align)
            visible_text += string(pad_len, ' ');
        else
            visible_text = string(pad_len, ' ') + visible_text;
    }
    return color_code + visible_text + reset;
}

// Zamanı formatlama (yyyy-mm-dd HH:MM)
string format_tm(const tm& t, bool valid = true) {
    if (!valid) return string(col_boot_time, ' '); // boşluk

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

// Tarih stringini parse et (örn: "Mon Jun 16 22:27") -> tm
tm parse_datetime(const string& timestr, int year) {
    tm t = {};
    istringstream ss(to_string(year) + " " + timestr);
    ss >> get_time(&t, "%Y %a %b %d %H:%M");
    return t;
}

struct Entry {
    string type;
    string kernel;
    tm start_dt;
    tm shutdown_dt;
    bool has_shutdown; // shutdown zamanı varsa true
    string duration;
    string exit_type; // shutdown, crash, running vb.
};

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
    string shutdown_str = e.has_shutdown ? format_tm(e.shutdown_dt) : string(col_shutdown, ' ');

    string uptime_str = format_duration(e.duration);

    // Exit sütunu renkleri
    string exit_text_colored;
    if (e.exit_type == "shutdown")
        exit_text_colored = green + e.exit_type + reset;
    else if (e.exit_type == "crash")
        exit_text_colored = bold + red + e.exit_type + reset;
    else if (e.exit_type == "running")
        exit_text_colored = yellow + e.exit_type + reset;
    else
        exit_text_colored = e.exit_type;

    // Kernel sarı renk
    string kernel_colored = yellow + e.kernel + reset;

    cout << "│ "
         << color_wrap(boot_str, bright_cyan, col_boot_time)
         << "│ "
         << color_wrap(shutdown_str, bright_magenta, col_shutdown)
         << "│ "
         << color_wrap(uptime_str, green, col_uptime, false)
         << " │ "
         << color_wrap(exit_text_colored, "", col_exit, false)
         << " │ "
         << color_wrap(kernel_colored, "", col_kernel, false)
         << " │\n";
}

int main() {
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
            string end_str = match[3].matched ? match[3].str() : "still running";
            e.duration = match[4].matched ? match[4].str() : "";

            // Exit tipi ve shutdown zamanı ayrımı
            if (end_str == "crash") {
                e.exit_type = "crash";
                e.has_shutdown = false;
            } else if (end_str == "down" || end_str == "still running") {
                e.exit_type = (end_str == "down") ? "shutdown" : "running";
                e.has_shutdown = false;
            } else {
                e.exit_type = "shutdown";
                e.shutdown_dt = parse_datetime(end_str, year);
                e.has_shutdown = true;
            }
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

    cout << "│                    ╵                  ╵            ╵          ╵                    │\n";
    cout << "╰────────────────────────────────────────────────────────────────────────────────────╯\n";

    return 0;
}
