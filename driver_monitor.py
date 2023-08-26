#!/usr/bin/env -S /usr/bin/sudo -- python3
import subprocess
import time
import re

def monitor_logs():
    log_keyword = "timed out to flush pci tx ring"
    driver_name = "rtw_8821ce"
    last_n_messages = 5

    # Check if dmesg supports --since flag
    dmesg_help = subprocess.check_output(['dmesg', '--help']).decode('utf-8')
    use_since_flag = '--since' in dmesg_help

    while True:
        # Read the logs from the last minute if --since flag is supported
        if use_since_flag:
            logs = subprocess.check_output(['dmesg', '--since', '1 minute ago']).decode('utf-8')
        else:
            logs = subprocess.check_output(['dmesg']).decode('utf-8')

        # Filter logs related to the driver_name
        driver_logs = [line for line in logs.split('\n') if driver_name in line]

        # Check last_n_messages for the log_keyword
        if all(log_keyword in log for log in driver_logs[-last_n_messages:]):
            print("Detected driver issue, reloading driver...")

            try:
                subprocess.check_call(['modprobe', '-r', driver_name])
                print("Driver unloaded successfully")
            except subprocess.CalledProcessError as e:
                print(f"Failed to unload driver: {e}")

            time.sleep(2)

            try:
                subprocess.check_call(['modprobe', driver_name])
                print("Driver loaded successfully")
            except subprocess.CalledProcessError as e:
                print(f"Failed to load driver: {e}")

        time.sleep(5)

if __name__ == "__main__":
    monitor_logs()

