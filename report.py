import os
import re
from datetime import datetime
import sys

LOG_FILE = os.path.expanduser("~/study-tracker/study_log.txt")

def format_time(minutes):
    """Converts minutes into Hours and Minutes."""
    hrs = int(minutes // 60)
    mins = int(minutes % 60)
    if hrs > 0:
        return f"{hrs}h {mins}m"
    return f"{mins}m"

def generate_report(target_date=None):
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
        
    if not os.path.exists(LOG_FILE):
        print(f"No log file found at {LOG_FILE}.")
        return

    total_study, total_away, total_locked = 0.0, 0.0, 0.0
    longest_streak = 0.0
    
    pattern = r"\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2} to \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] - ([A-Z_]+) - \(([\d\.]+) mins\)"
    
    with open(LOG_FILE, 'r') as f:
        for line in f:
            match = re.match(pattern, line.strip())
            if match:
                log_date, state, mins_str = match.groups()
                
                if log_date == target_date:
                    mins = float(mins_str)
                    if state == "STUDYING":
                        total_study += mins
                        if mins > longest_streak:
                            longest_streak = mins
                    elif state in ["AWAY_FROM_SCREEN", "PAUSED"]:
                        total_away += mins
                    elif state == "SYSTEM_LOCKED":
                        total_locked += mins

    print(f"\n=== Study Report for {target_date} ===")
    print(f" Total Study Time:     {format_time(total_study)}")
    print(f" Longest Streak:       {format_time(longest_streak)}")
    print(f" Total Away/Paused:    {format_time(total_away)}")
    print(f" System Locked:        {format_time(total_locked)}")
    print("===================================\n")

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    generate_report(date_arg)