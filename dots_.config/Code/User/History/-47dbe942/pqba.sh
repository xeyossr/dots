#!/usr/bin/env bash

# Renk tanımları (ANSI)
CYAN='\033[96m'
MAGENTA='\033[95m'
GREEN='\033[32m'
YELLOW='\033[33m'
BOLDRED='\033[1;31m'
BRIGHT_GREEN='\033[92m'
RESET='\033[0m'

# ASCII çizim karakterleri
UL='╭'; UR='╮'; LL='╰'; LR='╯'
VL='│'; HL='─'; CROSS='┿'; SEP='┼'
LHL='╺'; RHL='╸'; TSEP='╷'; BSEP='╵'
LINE="━━━━━━━━━━━━━━━━━━"

# Başlık
printf "${CYAN}${UL}─────────────────────────────────── Boot History ───────────────────────────────────${UR}${RESET}\n"
printf "${CYAN}${VL}                    ${TSEP}                  ${TSEP}            ${TSEP}          ${TSEP}                    ${VL}${RESET}\n"
printf "${CYAN}${VL}   Boot Time        ${VL} Shutdown         ${VL}   Uptime   ${VL}   Exit   ${VL}           Kernel   ${VL}${RESET}\n"
printf "${CYAN}${VL} ${LHL}${LINE}${CROSS}${LINE}${CROSS}${LINE}${CROSS}${LINE}${CROSS}${LINE} ${RHL} ${VL}${RESET}\n"

last -x | grep "^reboot" | while read -r line; do
    start_date=$(echo "$line" | awk '{print $5, $6, $7, $8}')
    end_raw=$(echo "$line" | grep -oP '(?<=- ).+?(?=\s+\()' || true)
    duration=$(echo "$line" | grep -oP '\(\K[^)]+' || echo "00:00")
    kernel=$(echo "$line" | awk '{print $3}')
    year=$(date '+%Y')

    # Tarih hesaplama
    start_epoch=$(date -d "$start_date $year" +%s 2>/dev/null)
    if [[ -z "$start_epoch" ]]; then continue; fi

    # Süre parse
    if [[ "$duration" == "00:00" ]]; then
        uptime="a few sec"
        end_disp=$(date -d "@$start_epoch" '+%Y-%m-%d %H:%M')
    elif [[ "$duration" == *"+"* ]]; then
        d=$(echo "$duration" | cut -d+ -f1)
        t=$(echo "$duration" | cut -d+ -f2)
        h=$(echo "$t" | cut -d: -f1)
        m=$(echo "$t" | cut -d: -f2)
        uptime="${d}d ${h}h ${m}m"
        end_epoch=$((start_epoch + (d*86400) + (h*3600) + (m*60)))
        end_disp=$(date -d "@$end_epoch" '+%Y-%m-%d %H:%M')
    else
        h=$(echo "$duration" | cut -d: -f1)
        m=$(echo "$duration" | cut -d: -f2)
        uptime="${h}h ${m}m"
        end_epoch=$((start_epoch + (h*3600) + (m*60)))
        end_disp=$(date -d "@$end_epoch" '+%Y-%m-%d %H:%M')
    fi

    start_disp=$(date -d "@$start_epoch" '+%Y-%m-%d %H:%M')

    # Çıkış türü belirle
    if [[ "$end_raw" == "crash" ]]; then
        exit="${BOLDRED}crash${RESET}"
    elif [[ "$end_raw" == "down" || "$end_raw" == "" ]]; then
        exit="${BRIGHT_GREEN}shutdown${RESET}"
    elif [[ "$end_raw" == "still running" ]]; then
        exit="${YELLOW}running${RESET}"
        end_disp="still running"
    else
        exit="${BRIGHT_GREEN}shutdown${RESET}"
    fi

    # Yazdır
    printf "${CYAN}${VL}${RESET} %-17s ${CYAN}${VL}${RESET} %-17s ${CYAN}${VL}${RESET} %10s ${CYAN}${VL}${RESET} %8b ${CYAN}${VL}${RESET} %18s ${CYAN}${VL}${RESET}\n" \
        "$start_disp" "$end_disp" "$uptime" "$exit" "$kernel"
done

# Alt kısım
printf "${CYAN}${VL}                    ${BSEP}                  ${BSEP}            ${BSEP}          ${BSEP}                    ${VL}${RESET}\n"
printf "${CYAN}${LL}────────────────────────────────────────────────────────────────────────────────────${LR}${RESET}\n"
