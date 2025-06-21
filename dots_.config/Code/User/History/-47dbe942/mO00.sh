#!/bin/bash

# Date format helper function
format_duration() {
    local duration=$1
    if [[ "$duration" == "00:00" ]]; then
        echo "a few sec"
    elif [[ "$duration" == *+* ]]; then
        # Format: 1+01:02
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

# Get the last -x output
last_output=$(last -x)

# Prepare the table header
echo -e "\033[36m╭─────────────────────────────────── Boot History ───────────────────────────────────╮\033[0m"
echo -e "  \033[37m│                    ╷                  ╷            ╷          ╷                    │\033[0m"
echo -e "  \033[37m│   Boot Time        │ Shutdown         │   Uptime   │   Exit   │           Kernel   │\033[0m"
echo -e "  \033[37m│ ╺━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━╸ │\033[0m"

# Iterate over the last output and parse reboot entries
while IFS= read -r line; do
    if [[ "$line" =~ reboot\ system\ boot\ (.*)\ (.*)\ (\w+\s+\w+\s+\d+\s+\d+:\d+) ]]; then
        boot_time="${BASH_REMATCH[3]}"
        shutdown="${BASH_REMATCH[4]}"
        kernel="${BASH_REMATCH[1]}"
        duration="${BASH_REMATCH[2]}"

        # Get uptime formatted
        formatted_uptime=$(format_duration "$duration")
        exit_type="shutdown"

        # Check if the exit type is crash or still running
        if [[ "$shutdown" == "crash" ]]; then
            exit_type="crash"
        elif [[ "$shutdown" == "still running" ]]; then
            exit_type="running"
        fi

        # Format shutdown time
        shutdown_time=$(date -d "$boot_time $duration" "+%Y-%m-%d %H:%M")

        # Set the color for exit type
        if [[ "$exit_type" == "crash" ]]; then
            exit_color="\033[1;31m"
        elif [[ "$exit_type" == "shutdown" ]]; then
            exit_color="\033[1;32m"
        elif [[ "$exit_type" == "running" ]]; then
            exit_color="\033[1;33m"
        fi

        # Print the row
        echo -e "  \033[37m│   $boot_time │ $shutdown_time │ $formatted_uptime │ \033[0m$exit_color$exit_type\033[0m │ $kernel │"
    fi
done <<< "$last_output"

# End the table
echo -e "  \033[37m│                    ╵                  ╵            ╵          ╵                    │\033[0m"
echo -e "  \033[36m╰────────────────────────────────────────────────────────────────────────────────────╯\033[0m"
