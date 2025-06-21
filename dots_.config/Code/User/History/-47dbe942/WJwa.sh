#!/bin/bash

# Helper function to format duration
format_duration() {
    local duration=$1
    if [[ "$duration" == "00:00" ]]; then
        echo "a few sec"
    elif [[ "$duration" == *+* ]]; then
        local days_part=$(echo $duration | cut -d'+' -f1)
        local time_part=$(echo $duration | cut -d'+' -f2)
        local days=$((days_part))
        local hours=$(echo $time_part | cut -d':' -f1)
        local minutes=$(echo $time_part | cut -d':' -f2)
        echo "${days}d ${hours}h ${minutes}m"
    else
        local hours=$(echo $duration | cut -d':' -f1)
        local minutes=$(echo $duration | cut -d':' -f2)
        echo "${hours}h ${minutes}m"
    fi
}

# Function to handle date formatting
format_date() {
    local date_str=$1
    local long_date=$2
    if [[ "$long_date" == "true" ]]; then
        # Format like "May 05, 2025"
        echo "$(date -d "$date_str" '+%b %d, %Y %H:%M')"
    else
        # Format like "2025-05-05"
        echo "$(date -d "$date_str" '+%Y-%m-%d %H:%M')"
    fi
}

# Parse command line arguments
long_date=false
if [[ "$1" == "--long-date" ]]; then
    long_date=true
fi

# Get the last -x output and filter out only the reboot lines
last_output=$(last -x | grep "reboot")

# Print header
echo -e "\033[36m╭─────────────────────────────────── Boot History ───────────────────────────────────╮\033[0m"
echo -e "  \033[37m│                    ╷                  ╷            ╷          ╷                    │\033[0m"
echo -e "  \033[37m│   Boot Time        │ Shutdown         │   Uptime   │   Exit   │           Kernel   │\033[0m"
echo -e "  \033[37m│ ╺━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━╸ │\033[0m"

# Iterate through each line of the last command output
while IFS= read -r line; do
    if [[ "$line" =~ reboot\ system\ boot\ ([^ ]*)\ ([^ ]*)\ ([^ ]+\s[^ ]+\s[^ ]+\s[^ ]+:\d{2}) ]]; then
        boot_time="${BASH_REMATCH[3]}"
        kernel="${BASH_REMATCH[1]}"
        duration="${BASH_REMATCH[2]}"

        # Handle end status (crash, down, running)
        if [[ "$line" =~ \((.*)\) ]]; then
            end_status="${BASH_REMATCH[1]}"
        else
            end_status="still running"
        fi

        # Calculate shutdown time by adding uptime to boot time
        shutdown_time=$(date -d "$boot_time $duration" "+%Y-%m-%d %H:%M")

        # Format duration
        formatted_uptime=$(format_duration "$duration")

        # Determine exit status color and text
        if [[ "$end_status" == "crash" ]]; then
            exit_type="crash"
            exit_color="\033[1;31m"
        elif [[ "$end_status" == "still running" ]]; then
            exit_type="running"
            exit_color="\033[1;33m"
        else
            exit_type="shutdown"
            exit_color="\033[1;32m"
        fi

        # Format boot time and shutdown time
        formatted_boot_time=$(format_date "$boot_time" "$long_date")
        formatted_shutdown_time=$(format_date "$shutdown_time" "$long_date")

        # Print the row with formatted values
        echo -e "  \033[37m│   $formatted_boot_time │ $formatted_shutdown_time │ $formatted_uptime │ \033[0m$exit_color$exit_type\033[0m │ $kernel │"
    fi
done <<< "$last_output"

# End the table
echo -e "  \033[37m│                    ╵                  ╵            ╵          ╵                    │\033[0m"
echo -e "  \033[36m╰────────────────────────────────────────────────────────────────────────────────────╯\033[0m"
