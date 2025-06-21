#!/bin/bash

# Renk kodları
RESET="\033[0m"
BRIGHT_CYAN="\033[96m"
BRIGHT_MAGENTA="\033[95m"
GREEN="\033[32m"
BRIGHT_GREEN="\033[92m"
RED="\033[31m"
YELLOW="\033[33m"
BOLD_RED="\033[1;31m"
YELLOW_BRIGHT="\033[93m"
CYAN="\033[36m"

# Tarih formatı seçeneği (uzun veya kısa)
LONG_DATE=false
if [[ "$1" == "--long-date" ]]; then
    LONG_DATE=true
fi

# Fonksiyon: duration formatlama (Python'dakine benzer)
format_duration() {
    local dur=$1
    if [[ "$dur" == "00:00" ]]; then
        echo "a few sec"
        return
    fi
    if [[ "$dur" == *"+"* ]]; then
        local days="${dur%%+*}"
        local time="${dur#*+}"
        local h="${time%%:*}"
        local m="${time#*:}"
        echo "${days}d ${h}h ${m}m"
    else
        local h="${dur%%:*}"
        local m="${dur#*:}"
        echo "${h}h ${m}m"
    fi
}

# Şu anki yıl
YEAR=$(date +%Y)

# Header ve çizgiler
print_header() {
    echo -e "${CYAN}╭─────────────────────────────────── Boot History ───────────────────────────────────╮${RESET}"
    echo -e "  │                    ╷                  ╷            ╷          ╷                    │"
    echo -e "  │ ${BRIGHT_CYAN}Boot Time        ${RESET}│ ${BRIGHT_MAGENTA}Shutdown         ${RESET}│ ${GREEN}  Uptime   ${RESET}│   Exit   │           Kernel   │"
    echo -e "  │ ╺━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━╸ │"
}

print_footer() {
    echo -e "  │                    ╵                  ╵            ╵          ╵                    │"
    echo -e "  ╰────────────────────────────────────────────────────────────────────────────────────╯"
}

# last -x çıktısını işleme
mapfile -t lines < <(last -x | grep '^reboot')

# Dizi oluşturmak için geçici alanlar
declare -a BOOT_TIMES
declare -a SHUTDOWNS
declare -a UPTIMES
declare -a EXITS
declare -a KERNELS

# Satırları işle
for line in "${lines[@]}"; do
    # Örnek satır:
    # reboot   system boot  6.15.2-arch1-1  Mon Jun 16 22:27 - Mon Jun 16 22:34  (00:07)
    # regex ile ayrıştırma

    if [[ "$line" =~ reboot[[:space:]]+system\ boot[[:space:]]+([^\ ]+)?[[:space:]]+([A-Z][a-z]{2}\ [A-Z][a-z]{2}\ [0-9]{1,2}\ [0-9]{2}:[0-9]{2})([[:space:]]+-[[:space:]]+([A-Z][a-z]{2}\ [0-9]{1,2}:[0-9]{2}|[0-9]{1,2}:[0-9]{2}|crash|down|still\ running))?[[:space:]]+\(([0-9+:\ ]+)\) ]]; then
        
        KERNEL=${BASH_REMATCH[1]}
        [[ -z "$KERNEL" ]] && KERNEL="-"

        START_STR="${BASH_REMATCH[2]}"
        END_STR="${BASH_REMATCH[4]}"
        DURATION_STR="${BASH_REMATCH[5]}"

        # Tarihi yıla tamamla
        START_DATE_STR="$YEAR $START_STR"
        # GNU date kullanarak saniye cinsinden epoch'a çevir
        START_EPOCH=$(date -d "$START_DATE_STR" +%s 2>/dev/null)
        if [[ $? -ne 0 ]]; then
            continue
        fi

        # DURATION içeriğine göre kapanış zamanını hesapla
        DAYS=0
        HOURS=0
        MINUTES=0

        if [[ "$DURATION_STR" == *"+"* ]]; then
            DAYS=${DURATION_STR%%+*}
            TIME_PART=${DURATION_STR#*+}
            HOURS=${TIME_PART%%:*}
            MINUTES=${TIME_PART#*:}
        else
            HOURS=${DURATION_STR%%:*}
            MINUTES=${DURATION_STR#*:}
        fi

        # Kapanış zamanı epoch
        SHUTDOWN_EPOCH=$(( START_EPOCH + DAYS*86400 + HOURS*3600 + MINUTES*60 ))

        # Eğer end 'crash' veya 'down' veya 'still running' ise ayarla
        if [[ "$END_STR" == "crash" ]]; then
            EXIT_TYPE="crash"
            SHUTDOWN_DISPLAY="crash"
        elif [[ "$END_STR" == "down" ]]; then
            EXIT_TYPE="crash"
            SHUTDOWN_DISPLAY="down"
        elif [[ "$END_STR" == "still running" ]]; then
            EXIT_TYPE="running"
            SHUTDOWN_DISPLAY="still running"
        else
            EXIT_TYPE="shutdown"
            SHUTDOWN_DISPLAY=$(date -d "@$SHUTDOWN_EPOCH" +"%Y-%m-%d %H:%M")
        fi

        # Tarih formatı seçeneğine göre boot ve shutdown formatı
        if $LONG_DATE ; then
            BOOT_TIME_DISPLAY=$(date -d "$START_DATE_STR" +"%b %d, %Y %H:%M")
            if [[ "$SHUTDOWN_DISPLAY" != "still running" && "$SHUTDOWN_DISPLAY" != "crash" && "$SHUTDOWN_DISPLAY" != "down" ]]; then
                SHUTDOWN_DISPLAY=$(date -d "@$SHUTDOWN_EPOCH" +"%b %d, %Y %H:%M")
            fi
        else
            BOOT_TIME_DISPLAY=$(date -d "$START_DATE_STR" +"%Y-%m-%d %H:%M")
        fi

        # Format duration (uptime)
        FORMATTED_DURATION=$(format_duration "$DURATION_STR")

        # Dizilere ekle
        BOOT_TIMES+=("$BOOT_TIME_DISPLAY")
        SHUTDOWNS+=("$SHUTDOWN_DISPLAY")
        UPTIMES+=("$FORMATTED_DURATION")
        EXITS+=("$EXIT_TYPE")
        KERNELS+=("$KERNEL")
    fi
done

# Tarihe göre sıralama (ters)
# Bash dizileriyle karmaşık, basitçe tarih bazlı sıralamayı yapabilmek için
# tüm satırları tek string olarak hazırlayıp sıralayacağız

# Satır formatı: epoch|boot_time|shutdown|uptime|exit|kernel
declare -a SORTABLE_LINES

for i in "${!BOOT_TIMES[@]}"; do
    # Boot time epoch hesapla (bu sefer yeniden hesap)
    EPOCH=$(date -d "${BOOT_TIMES[i]}" +%s 2>/dev/null)
    SORTABLE_LINES+=("$EPOCH|${BOOT_TIMES[i]}|${SHUTDOWNS[i]}|${UPTIMES[i]}|${EXITS[i]}|${KERNELS[i]}")
done

# Ters sırada sırala (en yeni üstte)
IFS=$'\n' SORTED=($(sort -r -n <<<"${SORTABLE_LINES[*]}"))
unset IFS

# Tablo başlığı yazdır
print_header

# Satırları yazdır (hizalama ve renk kodlarıyla)
for line in "${SORTED[@]}"; do
    # parçala
    IFS='|' read -r epoch boot shutdown uptime exit kernel <<< "$line"

    # Renkleri uygula
    BOOT_COLOR=$BRIGHT_CYAN
    SHUT_COLOR=$BRIGHT_MAGENTA
    UPTIME_COLOR=$GREEN
    KERNEL_COLOR=$YELLOW

    case "$exit" in
        crash)
            EXIT_COLOR=$BOLD_RED
            EXIT_TEXT="crash"
            ;;
        shutdown)
            EXIT_COLOR=$BRIGHT_GREEN
            EXIT_TEXT="shutdown"
            ;;
        running)
            EXIT_COLOR=$YELLOW_BRIGHT
            EXIT_TEXT="running"
            ;;
        *)
            EXIT_COLOR=$RESET
            EXIT_TEXT="$exit"
            ;;
    esac

    # Hizalama için uzunlukları belirle (renk kodlarını sayma!)
    # Boot Time 16 karakter (ör: 2025-06-16 22:27) / uzun tarih 18+ karakter
    # Shutdown 16 karakter / uzun tarih 18+
    # Uptime max 8-9 karakter (ör: 1d 5h 6m)
    # Exit max 8 karakter
    # Kernel 18 karakter sağa yaslı

    # Boşluklu hizalamayı bash string modifikasyonla yapacağız (padding)
    pad_right() {
        local str="$1"
        local len=$2
        local pad=$((len - ${#str}))
        printf "%s%*s" "$str" "$pad" ""
    }
    pad_left() {
        local str="$1"
        local len=$2
        local pad=$((len - ${#str}))
        printf "%*s%s" "$pad" "" "$str"
    }

    # Format tarih
    if $LONG_DATE; then
        # Long date örn: "Jun 16, 2025 22:27"
        BOOT_FMT=$(pad_right "$boot" 18)
        if [[ "$shutdown" == "still running" || "$shutdown" == "crash" || "$shutdown" == "down" ]]; then
            SHUT_FMT=$(pad_right "$shutdown" 18)
        else
            SHUT_FMT=$(pad_right "$shutdown" 18)
        fi
    else
        BOOT_FMT=$(pad_right "$boot" 16)
        if [[ "$shutdown" == "still running" || "$shutdown" == "crash" || "$shutdown" == "down" ]]; then
            SHUT_FMT=$(pad_right "$shutdown" 16)
        else
            SHUT_FMT=$(pad_right "$shutdown" 16)
        fi
    fi

    UPTIME_FMT=$(pad_left "$uptime" 10)
    EXIT_FMT=$(pad_left "$EXIT_TEXT" 8)
    KERNEL_FMT=$(pad_left "$kernel" 18)

    # Renkleri ekle ve yazdır
    # Soldaki 2 sütun solda, uptime & exit ortalanmış gibi hizalanmış sayılabilir,
    # kernel sağa yaslı.

    echo -e "  │ ${BOOT_COLOR}${BOOT_FMT}${RESET} │ ${SHUT_COLOR}${SHUT_FMT}${RESET} │ ${UPTIME_COLOR}${UPTIME_FMT}${RESET} │ ${EXIT_COLOR}${EXIT_FMT}${RESET} │ ${KERNEL_COLOR}${KERNEL_FMT}${RESET} │"
done

print_footer
