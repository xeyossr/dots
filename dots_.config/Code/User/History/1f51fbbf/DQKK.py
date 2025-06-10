#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path

def load_env_from_shell_script(script_path):
    command = ['bash', '-c', f'source "{script_path}" && env']
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
    env_vars = {}
    for line in proc.stdout:
        line = line.strip()
        if '=' in line:
            k, v = line.split('=', 1)
            env_vars[k] = v
    proc.wait()
    return env_vars

def parse_config_ctl(path):
    data = {}
    current_section = None
    current_subsection = None
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line and current_section is None:
                key, val = map(str.strip, line.split("=", 1))
                data[key] = val
                continue
            if re.match(r"^\d+:\s*$", line):
                current_section = line[:-1]
                data[current_section] = {"style": {}, "config": {}}
                current_subsection = None
                continue
            if line in ("style:", "config:"):
                current_subsection = line[:-1]
                continue
            if current_section and current_subsection and "=" in line:
                key, val = map(str.strip, line.split("=", 1))
                data[current_section][current_subsection][key] = val
                continue
    return data

def replace_variables_in_text(text, variables):
    pattern = re.compile(r"\{([a-zA-Z0-9_]+)\}")
    def replacer(match):
        var_name = match.group(1)
        return variables.get(var_name, match.group(0))  # Değişken yoksa olduğu gibi bırak
    return pattern.sub(replacer, text)

def read_and_order_jsonc_files(modules_dir):
    files_ordered = []
    header = modules_dir / "header.jsonc"
    footer = modules_dir / "footer.jsonc"

    if header.exists():
        files_ordered.append(header)
    
    others = sorted(f for f in modules_dir.glob("*.jsonc") if f not in (header, footer))
    files_ordered.extend(others)

    if footer.exists():
        files_ordered.append(footer)

    combined_text = ""
    for f in files_ordered:
        combined_text += f.read_text() + "\n"
    return combined_text

def main():
    scrDir = Path(__file__).parent.resolve()
    globalcontrol_path = scrDir / "globalcontrol.sh"
    env_vars = load_env_from_shell_script(globalcontrol_path)

    confDir = Path(env_vars.get('confDir', Path.home() / ".config"))
    waybar_dir = confDir / "waybar"
    modules_dir = waybar_dir / "modules"
    conf_ctl_path = waybar_dir / "config.ctl"
    style_in_path = modules_dir / "style.css"
    style_out_path = waybar_dir / "style.css"
    config_out_path = waybar_dir / "config.jsonc"

    ctl_data = parse_config_ctl(conf_ctl_path)
    section_key = ctl_data.get("enabled", "1")

    if section_key not in ctl_data:
        print(f"ERROR: Section '{section_key}' not found in config.ctl")
        sys.exit(1)

    style_vars = ctl_data[section_key].get("style", {})
    config_vars = ctl_data[section_key].get("config", {})

    # style.css
    style_text = style_in_path.read_text()
    replaced_style = replace_variables_in_text(style_text, style_vars)
    style_out_path.write_text(replaced_style)
    print(f"✔ style.css written to: {style_out_path}")

    # config.jsonc
    config_text = read_and_order_jsonc_files(modules_dir)
    replaced_config = replace_variables_in_text(config_text, config_vars)
    config_out_path.write_text(replaced_config)
    print(f"✔ config.jsonc written to: {config_out_path}")

if __name__ == "__main__":
    main()
