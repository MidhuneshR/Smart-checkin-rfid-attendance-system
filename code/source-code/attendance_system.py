#!/usr/bin/env python3
"""
Smart Check-In: RFID College Bus Attendance System
Main Controller Script
--------------------------------------------------
This script initializes and controls the hardware modules (RFID, LCD, RTC, LED, Buzzer)
on a Raspberry Pi. It handles real-time RFID scans, LCD printouts, local CSV logging,
and simulates/performs Cloud Database updates asynchronously.

If run on a non-Raspberry Pi system, it automatically falls back to 'Simulation Mode',
allowing the system logic and cloud sync to be tested using command-line inputs.
"""

import os
import sys
import time
import csv
import queue
import threading
from datetime import datetime

# ==========================================
# HARDWARE CONFIGURATION & PIN DEFINITIONS (BCM)
# ==========================================
LED_PIN = 18       # Green LED indicator
BUZZER_PIN = 23    # Audible alert buzzer
LCD_I2C_ADDR = 0x27 # Standard I2C address for 16x2 LCD
RTC_I2C_ADDR = 0x68 # Standard I2C address for DS3231 RTC

# Database / CSV settings
LOCAL_LOG_FILE = "attendance_log.csv"
CLOUD_API_URL = "https://api.mockcloud.com/attendance/sync" # Placeholder cloud API endpoint

# Registered Student Profiles Database (Mock DB)
STUDENT_REGISTRY = {
    "1234567890": {"name": "Alice", "roll_no": "710723106040", "dept": "ECE"},
    "0987654321": {"name": "Bob", "roll_no": "710723106046", "dept": "ECE"},
    "5555555555": {"name": "Charlie", "roll_no": "710723106058", "dept": "ECE"},
    "710723106060": {"name": "Midhunesh R", "roll_no": "710723106060", "dept": "ECE"}
}

# ==========================================
# HARDWARE INITIALIZATION & FALLBACK CHECK
# ==========================================
SIMULATION_MODE = False

# Try importing RPi.GPIO and hardware libraries
try:
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
    import board
    import busio
    import adafruit_character_lcd.character_lcd_i2c as character_lcd
    import adafruit_ds3231
except (ImportError, ModuleNotFoundError) as e:
    print(f"\n[!] Hardware libraries missing: {e}")
    print("[!] Falling back to SIMULATION MODE (No physical hardware required)\n")
    SIMULATION_MODE = True

# ==========================================
# CLOUD SYNC ENGINE (Asynchronous Queue)
# ==========================================
class CloudSyncEngine(threading.Thread):
    def __init__(self, upload_queue):
        super().__init__()
        self.upload_queue = upload_queue
        self.daemon = True
        self.running = True

    def run(self):
        # Verify requests library is available for HTTP communication
        try:
            import requests
        except ImportError:
            requests = None
            print("[Cloud Sync] Info: 'requests' module not found. Cloud uploads will be simulated.")

        while self.running:
            try:
                # Blocks until an item is available in the queue
                record = self.upload_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            print(f"\n[Cloud Sync] Processing record: {record['name']} ({record['tag_id']})")
            
            # Simulate/Perform network upload
            success = False
            if requests:
                try:
                    # Simulated mock upload request
                    # response = requests.post(CLOUD_API_URL, json=record, timeout=3.0)
                    # if response.status_code == 200: success = True
                    time.sleep(1.0) # Simulating network delay
                    success = True
                except Exception as ex:
                    print(f"[Cloud Sync] Connection failed: {ex}")
            else:
                time.sleep(1.0) # Simulating network delay
                success = True

            if success:
                print(f"[Cloud Sync] Successfully updated Cloud Database for {record['name']}")
            else:
                print(f"[Cloud Sync] Failed to upload. Re-queueing record for retry...")
                self.upload_queue.put(record)
                time.sleep(5) # Delay before next retry

    def stop(self):
        self.running = False


# ==========================================
# HARDWARE DRIVERS (Real vs Simulated)
# ==========================================
class SystemController:
    def __init__(self):
        self.upload_queue = queue.Queue()
        self.sync_thread = CloudSyncEngine(self.upload_queue)
        self.sync_thread.start()

        if not SIMULATION_MODE:
            self._init_hardware()
        else:
            print("--- SIMULATION HARDWARE RUNNING ---")
            print("Enter student RFID card number in terminal to simulate a swipe.")
            print("Registered tag examples: 1234567890, 0987654321, 5555555555, 710723106060")
            print("Press Ctrl+C to terminate system.")
            print("-" * 35)

    def _init_hardware(self):
        # GPIO Configuration
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)

        # RFID initialization
        self.rfid_reader = SimpleMFRC522()

        # I2C Protocol setup (SDA/SCL pins)
        self.i2c = busio.I2C(board.SCL, board.SDA)

        # LCD initialization (16 Columns, 2 Rows)
        self.lcd = character_lcd.Character_LCD_I2C(self.i2c, 16, 2, address=LCD_I2C_ADDR)
        self.lcd.backlight = True
        self.lcd.clear()
        self.lcd.message = "System Ready\nScan RFID Tag..."

        # RTC initialization
        self.rtc = adafruit_ds3231.DS3231(self.i2c)

    def get_timestamp(self):
        if SIMULATION_MODE:
            return datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        else:
            try:
                t = self.rtc.datetime
                return f"{t.tm_hour:02d}:{t.tm_min:02d}:{t.tm_sec:02d} {t.tm_mday:02d}/{t.tm_mon:02d}/{t.tm_year}"
            except Exception:
                # Fallback to system time if RTC communication fails
                return datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    def show_message(self, line1, line2=""):
        if SIMULATION_MODE:
            print("\n┌────────────────┐")
            print(f"│ {line1:<14} │")
            print(f"│ {line2:<14} │")
            print("└────────────────┘")
        else:
            self.lcd.clear()
            self.lcd.message = f"{line1}\n{line2}"

    def trigger_success_feedback(self):
        if SIMULATION_MODE:
            print("[FEEDBACK] -> GREEN LED ON, Buzzer: 1 Quick Beep")
        else:
            GPIO.output(LED_PIN, GPIO.HIGH)
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(0.8)
            GPIO.output(LED_PIN, GPIO.LOW)

    def trigger_failure_feedback(self):
        if SIMULATION_MODE:
            print("[FEEDBACK] -> RED LED OFF (No LED), Buzzer: 3 Alarm Beeps")
        else:
            # ACCESS DENIED alarm feedback: 3 rapid sound pulses
            for _ in range(3):
                GPIO.output(BUZZER_PIN, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(BUZZER_PIN, GPIO.LOW)
                time.sleep(0.1)

    def log_locally(self, tag_id, name, roll_no, timestamp):
        # Create CSV file with header if it doesn't exist
        file_exists = os.path.isfile(LOCAL_LOG_FILE)
        with open(LOCAL_LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Tag ID", "Student Name", "Roll Number"])
            writer.writerow([timestamp, tag_id, name, roll_no])
        print(f"[Local Log] Written to {LOCAL_LOG_FILE}")

    def process_scan(self, tag_id):
        tag_id = str(tag_id).strip()
        timestamp = self.get_timestamp()
        
        if tag_id in STUDENT_REGISTRY:
            student = STUDENT_REGISTRY[tag_id]
            name = student["name"]
            roll_no = student["roll_no"]
            
            print(f"\n[Swipe Detected] ID: {tag_id} | Name: {name} | Time: {timestamp}")
            self.show_message(f"Welcome {name}", f"ID: {roll_no}")
            
            # Local Logging
            self.log_locally(tag_id, name, roll_no, timestamp)
            
            # Push payload to cloud sync queue
            record = {
                "tag_id": tag_id,
                "name": name,
                "roll_no": roll_no,
                "timestamp": timestamp,
                "status": "Boarded"
            }
            self.upload_queue.put(record)
            
            # Hardware feedback indicator
            self.trigger_success_feedback()
        else:
            # Student not registered
            print(f"\n[Swipe Warning] Unregistered RFID ID: {tag_id} | Time: {timestamp}")
            self.show_message("Access Denied", "Card Invalid")
            self.trigger_failure_feedback()

        # Reset Display after a short timeout
        time.sleep(1.5)
        self.show_message("Smart Check-In", "Scan RFID Tag...")

    def read_loop(self):
        if SIMULATION_MODE:
            while True:
                try:
                    user_tag = input("\nRFID Scanner Input: ")
                    if not user_tag.strip():
                        continue
                    self.process_scan(user_tag)
                except (KeyboardInterrupt, EOFError):
                    break
        else:
            while True:
                try:
                    # Non-blocking scan attempt
                    id, text = self.rfid_reader.read_no_block()
                    if id:
                        self.process_scan(id)
                    time.sleep(0.2)
                except KeyboardInterrupt:
                    break

    def cleanup(self):
        print("\nStopping Smart Check-In system...")
        self.sync_thread.stop()
        if not SIMULATION_MODE:
            self.lcd.clear()
            self.lcd.backlight = False
            GPIO.cleanup()
        print("System shutdown complete. Goodbye.")

# ==========================================
# MAIN EXECUTION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    controller = SystemController()
    try:
        controller.read_loop()
    finally:
        controller.cleanup()
