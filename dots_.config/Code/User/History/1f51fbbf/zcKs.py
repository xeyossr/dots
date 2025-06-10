#!/usr/bin/env python3
import re
import sys
from pathlib import Path

def parse_config_ctl(path):
    """
    Parses the config.ctl file with format:
    enabled=1

    1:
        style:
            var1=value1
            var2=value2
        config:
            var3=value3
    2:
        style:
            ...
        config:
            ...
    Returns a dict of dicts:
    {
        "enabled": "1",
        "1": {
            "style": {var1: value1, ...},
            "config": {var3: value3, ...},
        },
        ...
    }
    """
    data = {}
    current_section = None
    current_subsection = None
    with open(path, "r") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # global key=value
            if "=" in line and current_section is None:
                key, val = map(str.strip, line.split("=", 1))
                data[key] = val
                continue
            # section start e.g. 1:
            if re.match(r"^\d+:\s*$", line):
                current_section = line[:-1]
                data[current_section] = {"style": {}, "config": {}}
                current_subsection = None
                continue
            # subsection e.g. style:
            if line in ("style:", "config:"):
                current_subsection = line[:-1]
                continue
            # key=value inside subsection
            if current_section and current_subsection and "=" in line:
                key, val = map(str.strip, line.split("=", 1))
                data[current_section][current_subsection][key] = val
                continue
            # If line not recognized, ignore or warn
            # print(f"Warning: Line {line_no} not recognized: {line}")
    return data

def replace_variables_in_text(text, variables, section_name):
    """
    Replaces ${var} in text with corresponding values from variables dict.
    If var not found, print WARNING and leave as is.
    """
    pattern = re.compile(r"\$\{([^\}]+)\}")
    warnings = []
    def replacer(match):
        var_name = match.group(1)
        if var_name in variables:
            return variables[var_name]
        else:
            warnings.append(f"WARNING: Variable '{var_name}' not found in {section_name}")
            return match.group(0)
    new_text = pattern.sub(replacer, text)
    return new_text, warnings

def main():
    if len(sys.argv) != 6:
        print("Usage: python3 script.py config_ctl_path style_in_path style_out_path config_in_path config_out_path")
        sys.exit(1)

    config_ctl_path = Path(sys.argv[1])
    style_in_path = Path(sys.argv[2])
    style_out_path = Path(sys.argv[3])
    config_in_path = Path(sys.argv[4])
    config_out_path = Path(sys.argv[5])

    # Parse config.ctl
    ctl_data = parse_config_ctl(config_ctl_path)

    # For simplicity, choose section "1" (or prompt user)
    # You can extend this script to accept section number as argument if needed
    section_key = "1"
    if section_key not in ctl_data:
        print(f"ERROR: Section '{section_key}' not found in {config_ctl_path}")
        sys.exit(1)

    style_vars = ctl_data[section_key].get("style", {})
    config_vars = ctl_data[section_key].get("config", {})

    # Read style input file
    style_text = style_in_path.read_text()

    # Replace variables in style
    style_result, style_warnings = replace_variables_in_text(style_text, style_vars, "style")

    # Write replaced style to output
    style_out_path.write_text(style_result)
    print(f"Written replaced style to {style_out_path}")

    # Read config input file
    config_text = config_in_path.read_text()

    # Replace variables in config
    config_result, config_warnings = replace_variables_in_text(config_text, config_vars, "config")

    # Write replaced config to output
    config_out_path.write_text(config_result)
    print(f"Written replaced config to {config_out_path}")

    # Print warnings
    all_warnings = style_warnings + config_warnings
    if all_warnings:
        print("\n".join(all_warnings))
    else:
        print("All variables replaced successfully.")

if __name__ == "__main__":
    main()
