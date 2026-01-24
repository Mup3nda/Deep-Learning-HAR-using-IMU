#!/usr/bin/env python3
"""
Simple IMU Data Reader
Reads sensor data from ESP32 via serial port and displays it.
"""

import serial as pyserial  # Rename to avoid conflicts
import time
import serial.tools.list_ports
import traceback
import csv
import os
from datetime import datetime

# ============================================
# Configuration
# ============================================
#SERIAL_PORT = '/dev/cu.usbserial-110'  # Update this to your ESP32 port
SERIAL_PORT = '/dev/cu.SLAB_USBtoUART'  # Update this to your ESP32 porta
BAUD_RATE = 115200
LSB_ACC =  16384.0
LSB_GYRO = 131.0

# CSV logging settings
ENABLE_LOGGING = True  # Set to False to disable logging
LOG_DIR = './sensor_data/Recorded'  # Directory to save CSV files
#ACTIVITY_NAME = 'standing'  # Change this to the activity you're recording
#ACTIVITY_NAME = 'walking'  # Change this to the activity you're recording
#ACTIVITY_NAME = 'laying'  # Change this to the activity you're recording
ACTIVITY_NAME = 'test'  # Change this to the activity you're recording

# ============================================
# CSV Logger
# ============================================
def create_csv_logger(activity_name):
    """
    Create a CSV file with timestamp in filename.
    
    Returns:
        csv_writer: CSV writer object
        csv_file: File handle (to close later)
        filename: Path to created file
    """
    # Create directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{LOG_DIR}/{activity_name}_{timestamp}.csv"
    
    # Open file and create CSV writer
    csv_file = open(filename, 'w', newline='')
    csv_writer = csv.writer(csv_file, delimiter=';')  # Use semicolon like your other files
    
    # Write header
    csv_writer.writerow(['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'])
    
    print(f"📝 Logging to: {filename}")
    
    return csv_writer, csv_file, filename

# ============================================
# Main Loop
# ============================================
def main():
    print("="*60)
    print("IMU DATA READER & LOGGER")
    print("="*60)
    print(f"Serial Port: {SERIAL_PORT} @ {BAUD_RATE} baud")
    if ENABLE_LOGGING:
        print(f"Activity: {ACTIVITY_NAME}")
        print(f"Log Directory: {LOG_DIR}")
    else:
        print("Logging: DISABLED")
    print("="*60)
    print("\nConnecting to ESP32...")
    
    # Initialize CSV logger
    csv_writer = None
    csv_file = None
    log_filename = None
    
    try:
        ser = pyserial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for connection
        print("✓ Connected!\n")

        # Create CSV logger
        if ENABLE_LOGGING:
            csv_writer, csv_file, log_filename = create_csv_logger(ACTIVITY_NAME)

        # Flush initial garbage data
        ser.reset_input_buffer()
        for _ in range(5):
            ser.readline()
        
        print("Reading IMU data... (Press Ctrl+C to stop)\n")
        print(f"{'Time':^8} | {'acc_x':^8} | {'acc_y':^8} | {'acc_z':^8} | {'gyro_x':^8} | {'gyro_y':^8} | {'gyro_z':^8}")
        print("-" * 80)
        
        sample_count = 0
        logged_count = 0
        
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                
                if not line:
                    continue
                
                # Skip non-CSV lines (like "Initializing MPU6050...")
                if not (line[0].isdigit() or line[0] == '-'):
                    print(f"ℹ️  Info: {line}")  # Show non-CSV messages
                    continue
                
                # Parse CSV: acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z
                parts = line.split(',')
                if len(parts) != 6:
                    print(f"⚠️  Invalid data: {line}")
                    continue
                
                # Convert to float
                try:
                    acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = [float(x) for x in parts]
                except ValueError:
                    print(f"⚠️  Parse error: {line}")
                    continue

                # Convert raw values to physical units
                ax_g = acc_x / LSB_ACC
                ay_g = acc_y / LSB_ACC
                az_g = acc_z / LSB_ACC

                gx_dps = gyro_x / LSB_GYRO
                gy_dps = gyro_y / LSB_GYRO
                gz_dps = gyro_z / LSB_GYRO

                sample_count += 1
                
                # Log to CSV
                if ENABLE_LOGGING and csv_writer:
                    csv_writer.writerow([ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps])
                    logged_count += 1
                    
                    # Flush to disk every 100 samples (1 second at 100Hz)
                    if logged_count % 100 == 0:
                        csv_file.flush()
                
                # Display data (every 10 samples to not flood terminal)
                if sample_count % 10 == 0:
                    timestamp = time.strftime("%H:%M:%S")
                    log_indicator = "Writing" if ENABLE_LOGGING else "  "
                    print(f"{timestamp} {log_indicator} | {ax_g:+8.3f} | {ay_g:+8.3f} | {az_g:+8.3f} | {gx_dps:+8.3f} | {gy_dps:+8.3f} | {gz_dps:+8.3f}")
                
            except KeyboardInterrupt:
                print("\n\n Stopping...")
                break
            except Exception as e:
                print(f"❌ Error reading data: {e}")
                continue
        
        # Close serial connection
        ser.close()
        
        # Close CSV file
        if csv_file:
            csv_file.close()
            print(f"\n✓ Saved {logged_count} samples to: {log_filename}")
        
        print(f"✓ Disconnected (read {sample_count} samples)")
        
    except pyserial.SerialException as e:
        print(f"\n❌ Error: Could not open serial port {SERIAL_PORT}")
        print(f"   {e}")
        print("\n💡 Available ports:")
        for port in serial.tools.list_ports.comports():
            print(f"   - {port.device}: {port.description}")
        print("\nUpdate SERIAL_PORT in the script to match your ESP32 port.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
    finally:
        # Ensure CSV file is closed even if error occurs
        if csv_file:
            csv_file.close()
            print(f"\n✓ CSV file saved: {log_filename}")

if __name__ == "__main__":
    main()
