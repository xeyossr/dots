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
        for line_no, line in enumerate(f, 1):
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

def replace_variables_in_text(text, variables, section_name):
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

def read_and_order_jsonc_files(modules_dir):
    # Önce header.jsonc
    files_ordered = []
    header = modules_dir / "header.jsonc"
    footer = modules_dir / "footer.jsonc"

    if header.exists():
        files_ordered.append(header)

    # Diğer .jsonc dosyaları header ve footer hariç
    others = sorted([f for f in modules_dir.glob("*.jsonc") if f not in (header, footer)])
    files_ordered.extend(others)

    # Son olarak footer
    if footer.exists():
        files_ordered.append(footer)

    # Hepsini birleştir
    combined_text = ""
    for f in files_ordered:
        combined_text += f.read_text() + "\n"
    return combined_text

def main():
    # globalcontrol.sh dosyasının yolu
    scrDir = Path(__file__).parent.resolve()
    globalcontrol_path = scrDir / "globalcontrol.sh"
    env_vars = load_env_from_shell_script(globalcontrol_path)

    confDir = env_vars.get('confDir', str(Path.home() / ".config"))
    waybar_dir = Path(confDir) / "waybar"
    modules_dir = waybar_dir / "modules"
    conf_ctl_path = waybar_dir / "config.ctl"
    style_in_path = modules_dir / "style.css"
    style_out_path = waybar_dir / "style.css"
    config_out_path = waybar_dir / "config.jsonc"

    # config.ctl parse
    ctl_data = parse_config_ctl(conf_ctl_path)
    section_key = "1"  # İstersen burayı değiştirebilirsin

    if section_key not in ctl_data:
        print(f"ERROR: Section '{section_key}' not found in {conf_ctl_path}")
        sys.exit(1)

    style_vars = ctl_data[section_key].get("style", {})
    config_vars = ctl_data[section_key].get("config", {})

    # style.css input
    style_text = style_in_path.read_text()
    style_result, style_warnings = replace_variables_in_text(style_text, style_vars, "style")
    style_out_path.write_text(style_result)
    print(f"Written replaced style to {style_out_path}")

    # config.jsonc input (modules altındaki tüm .jsonc dosyaları sıralı birleşim)
    config_text = read_and_order_jsonc_files(modules_dir)
    config_result, config_warnings = replace_variables_in_text(config_text, config_vars, "config")
    config_out_path.write_text(config_result)
    print(f"Written replaced config to {config_out_path}")

    all_warnings = style_warnings + config_warnings
    if all_warnings:
        print("\n".join(all_warnings))
    else:
        print("All variables replaced successfully.")

if __name__ == "__main__":
    main()
