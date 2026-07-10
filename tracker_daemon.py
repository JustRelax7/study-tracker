import cv2
import time
import os
import subprocess
from datetime import datetime


# SETTINGS BLOCK
CHECK_INTERVAL_SECONDS = 10       
MIN_FACE_WIDTH = 100              # minimum pixel width of face 
GRACE_PERIOD_SECONDS = 5 * 60     # 5 minute tolerance

# File paths
LOG_FILE = os.path.expanduser("~/study-tracker/study_log.txt")
PAUSE_FILE = os.path.expanduser("~/study-tracker/PAUSED")
RECOVERY_FILE = os.path.expanduser("~/study-tracker/.tracker_recovery.tmp") #recovery file

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def is_paused():
    """If PAUSED file exists, then pause the tracker"""
    return os.path.exists(PAUSE_FILE)

def is_screen_locked():
    """checks ubuntu GNOME to see if the laptop lid is closed or screen is locked"""
    try:
        result = subprocess.run(
            ['gdbus', 'call', '-e', '-d', 'org.gnome.ScreenSaver', 
             '-o', '/org/gnome/ScreenSaver', '-i', 'org.gnome.ScreenSaver', 
             '-m', 'GetActive'], 
            capture_output=True, text=True
        )
        return "true" in result.stdout.lower()
    except Exception:
        return False

def check_face():
    """takes a quick snapshot of face."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False
    
    time.sleep(0.2)  # sensor adjust to light
    ret, frame = cap.read()
    cap.release()    # turn off camera light
    
    if not ret: return False
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    for (x, y, w, h) in faces:
        if w >= MIN_FACE_WIDTH:
            return True
    return False

def log_block(state, start_time, end_time):
    """logging of the state done into the text file."""
    if state == "STARTING_UP": return
    
    duration = end_time - start_time
    minutes = duration.total_seconds() / 60
    
    # ignore micro-fluctuations under 1 minute
    if minutes < 1.0: return
        
    start_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    
    with open(LOG_FILE, "a") as f:
        f.write(f"[{start_str} to {end_str}] - {state} - ({minutes:.1f} mins)\n")
    print(f"Logged: {state} for {minutes:.1f} mins")



def save_checkpoint(state, start_time, last_face_time): #part of crash recovery system
    """saves the active session states to a temporary file in case of a crash."""
    try:
        with open(RECOVERY_FILE, "w") as f:
            f.write(f"{state}\n{start_time.isoformat()}\n{last_face_time.isoformat()}")
    except Exception as e:
        print(f"Error saving checkpoint: {e}")

def clear_checkpoint():     #part of crash recovery system
    """removes the recovery file when the daemon exits cleanly"""
    if os.path.exists(RECOVERY_FILE):
        try:
            os.remove(RECOVERY_FILE)
        except Exception:
            pass

def check_and_recover_crash():  #part of crash recovery system
    """scans for an un-cleared recovery file from a previous crash and saves the data."""
    if os.path.exists(RECOVERY_FILE):
        print("Detected an un-cleared checkpoint file. Recovering crashed session...")
        try:
            with open(RECOVERY_FILE, "r") as f:
                lines = f.read().splitlines()
            
            if len(lines) == 3:
                saved_state = lines[0]
                start_time = datetime.fromisoformat(lines[1])
                last_seen = datetime.fromisoformat(lines[2])
                
                # only log it if it was an active studying session
                if saved_state == "STUDYING":
                    log_block("STUDYING (CRASH_RECOVERED)", start_time, last_seen)
        except Exception as e:
            print(f"Failed to read recovery file: {e}")
        finally:
            # always ensure the stale file is cleared so we don't duplicate logs
            clear_checkpoint()


if __name__ == "__main__":
    print("Tracker started. Press Ctrl+C to quit.")

    check_and_recover_crash()

    current_state = "STARTING_UP"
    state_start_time = datetime.now()
    last_face_time = datetime.now()
    
    try:
        while True:
            now = datetime.now()
            
            # 1. Determine literal current status
            if is_paused():
                literal_status = "PAUSED"
            elif is_screen_locked():
                literal_status = "SYSTEM_LOCKED"
            elif check_face():
                literal_status = "STUDYING"
                last_face_time = now  # Update the last seen timer
            else:
                literal_status = "AWAY_FROM_SCREEN"
            
            # 2. Apply Grace Period Logic
            if literal_status == "AWAY_FROM_SCREEN":
                time_since_last_face = (now - last_face_time).total_seconds()
                if time_since_last_face <= GRACE_PERIOD_SECONDS:
                    effective_state = "STUDYING" # Overwrite to studying because of grace period
                else:
                    effective_state = "AWAY_FROM_SCREEN"
            else:
                effective_state = literal_status
                
            # 3. Detect State Change & Log
            if effective_state != current_state:
                actual_end_time = now
                if(current_state == "STUDYING"):
                    actual_end_time = last_face_time
                log_block(current_state, state_start_time, actual_end_time)
                current_state = effective_state
                state_start_time = now
                print(f"[{now.strftime('%H:%M:%S')}] State changed to: {current_state}")
            
            if current_state == "STUDYING":
                save_checkpoint(current_state, state_start_time, last_face_time)
            time.sleep(CHECK_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        # Save final block if you quit manually in the terminal
        now = datetime.now()
        log_block(current_state, state_start_time, now)
        clear_checkpoint()
        print("\nExiting and saving final log.")