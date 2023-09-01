#!/usr/bin/env -S /usr/bin/sudo -- python3
import subprocess
import time
import re

def monitor_logs():
    log_keyword = "timed out to flush pci tx ring"
    driver_name = "rtw_8821ce"
    driver_unload_command = ["modprobe", "-r", driver_name]
    driver_load_command = ["modprobe", driver_name]
    alternative_unload_command = ["rfkill", "block", "wlan"]
    alternative_load_command = ["rfkill", "unblock", "wlan"]
    alternative_check_command = ["ping", "-c1", "1.1.1.1"]
    use_alternative_reload_commands = True
    use_alternative_check_command = True
    unload_command = alternative_unload_command if use_alternative_reload_commands else driver_unload_command
    load_command = alternative_load_command if use_alternative_reload_commands else driver_load_command
    last_n_messages = 5

    # Check if dmesg supports --since flag
    dmesg_help = subprocess.check_output(['dmesg', '--help']).decode('utf-8')
    use_dmesg_since_flag = '--since' in dmesg_help

    while True:
        should_reload = False
        if use_alternative_check_command:
            try:
                subprocess.check_call(alternative_check_command)
            except subprocess.CalledProcessError as e:
                print(f"Failed to ping: {e}")
                should_reload = True
        else:
            if use_dmesg_since_flag:
                logs = subprocess.check_output(['dmesg', '--since', '1 minute ago']).decode('utf-8')
            else:
                logs = subprocess.check_output(['dmesg']).decode('utf-8')

            # Filter logs related to the driver_name
            driver_logs = [line for line in logs.split('\n') if driver_name in line]

            # Check last_n_messages for the log_keyword
            if all(log_keyword in log for log in driver_logs[-last_n_messages:]):
                print("Detected driver issue, reloading driver...")
                should_reload = True

        if should_reload:
            try:
                subprocess.check_call(unload_command)
                print("Driver unloaded successfully")
            except subprocess.CalledProcessError as e:
                print(f"Failed to unload driver: {e}")

            time.sleep(2)

            try:
                subprocess.check_call(load_command)
                print("Driver loaded successfully")
            except subprocess.CalledProcessError as e:
                print(f"Failed to load driver: {e}")

        time.sleep(60)

if __name__ == "__main__":
    monitor_logs()

