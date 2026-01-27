#!/usr/bin/env python3
"""
BLE IMU Data Logger
Receives sensor data from ESP32 via Bluetooth and saves to CSV
"""

import asyncio
import logging
import csv
import os
import time
from datetime import datetime
from bleak import BleakScanner, BleakClient

# ============================================
# Configuration (Edit these)
# ============================================
DEVICE_NAME = "ESP32-NimBLE-Test"
SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
CHAR_UUID = "abcdefab-1234-5678-1234-abcdefabcdef"

LOG_DIR = '../data/sensor_data/BLE_Recorded'
ACTIVITY_NAME = 'walking'  # Change this before recording

# ============================================
# Logging setup
# ============================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# CSV Logger Class
# ============================================
class CSVLogger:
    """Handles CSV file creation and writing"""
    
    def __init__(self, activity_name, log_dir):
        """Initialize CSV logger"""
        # Create directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"{log_dir}/{activity_name}_{timestamp}.csv"
        
        # Open file and create CSV writer
        self.csv_file = open(self.filename, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, delimiter=';')
        
        # Write header
        self.csv_writer.writerow(['timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'])
        
        # Sample counter
        self.sample_count = 0
        
        logger.info(f"📝 Logging to: {self.filename}")
    
    def write_row(self, data_dict):
        """Write a single row to CSV"""
        timestamp = time.strftime("%H%M%S")
        
        self.csv_writer.writerow([
            timestamp,
            data_dict['acc_x'],
            data_dict['acc_y'],
            data_dict['acc_z'],
            data_dict['gyro_x'],
            data_dict['gyro_y'],
            data_dict['gyro_z']
        ])
        
        self.sample_count += 1
        
        # Flush to disk every 100 samples
        if self.sample_count % 100 == 0:
            self.csv_file.flush()
    
    def close(self):
        """Close CSV file"""
        self.csv_file.flush()
        self.csv_file.close()
        logger.info(f"✓ Saved {self.sample_count} samples to: {self.filename}")

# ============================================
# BLE Data Logger Class
# ============================================
class BLEDataLogger:
    """Manages BLE connection and data logging"""
    
    def __init__(self, device_name, service_uuid, char_uuid, csv_logger):
        """Initialize BLE logger"""
        self.device_name = device_name
        self.service_uuid = service_uuid
        self.char_uuid = char_uuid
        self.csv_logger = csv_logger
        self.client = None
        self.sample_count = 0
    
    async def scan_and_connect(self):
        """Scan for BLE device and connect"""
        logger.info("🔍 Scanning for devices...")
        devices = await BleakScanner.discover()
        
        esp_device = None
        for d in devices:
            if d.name == self.device_name:
                esp_device = d
                break
        
        if not esp_device:
            logger.error(f"❌ Device '{self.device_name}' not found")
            logger.info("Available devices:")
            for d in devices:
                if d.name:
                    logger.info(f"  - {d.name} ({d.address})")
            return False
        
        logger.info(f"📱 Found device at {esp_device.address}")
        logger.info(f"🔗 Connecting...")
        
        self.client = BleakClient(esp_device.address)
        await self.client.connect()
        
        logger.info("✅ Connected!")
        return True
    
    def notification_handler(self, sender, data):
        """Handle incoming BLE notifications"""
        try:
            # Decode bytes to string
            decoded = data.decode('utf-8').strip()
            
            # Parse CSV format: "acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z"
            parts = decoded.split(',')
            
            # Check if we have 6 values
            if len(parts) != 6:
                logger.warning(f"⚠️  Invalid data (expected 6 values, got {len(parts)}): {decoded}")
                return
            
            # Convert to float
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = [float(x) for x in parts]
            
            # Create dictionary
            data_dict = {
                'acc_x': acc_x,
                'acc_y': acc_y,
                'acc_z': acc_z,
                'gyro_x': gyro_x,
                'gyro_y': gyro_y,
                'gyro_z': gyro_z
            }
            
            # Write to CSV
            self.csv_logger.write_row(data_dict)
            
            # Increment counter
            self.sample_count += 1
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            # Print to terminal (every 10 samples to avoid spam)
            if self.sample_count % 10 == 0:
                logger.info(f"Timestamp: {timestamp} | acc: [{acc_x:+6.2f}, {acc_y:+6.2f}, {acc_z:+6.2f}] | gyro: [{gyro_x:+8.3f}, {gyro_y:+8.3f}, {gyro_z:+8.3f}]")
        
        except ValueError as e:
            logger.warning(f"⚠️  Parse error: {decoded}")
        except Exception as e:
            logger.error(f"❌ Error in notification handler: {e}")
    
    async def start_logging(self):
        """Start receiving and logging data"""
        if not self.client or not self.client.is_connected:
            raise ConnectionError("Not connected to BLE device")
        
        logger.info("📊 Starting data logging... (Press Ctrl+C to stop)")
        
        # Enable notifications
        await self.client.start_notify(self.char_uuid, self.notification_handler)
        
        # Keep connection alive
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Ctrl+C was pressed...")
        
        # Stop notifications
        await self.client.stop_notify(self.char_uuid)
    
    async def disconnect(self):
        """Disconnect from BLE device"""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            logger.info("🔌 Disconnected from BLE device")

# ============================================
# Main Function
# ============================================
async def main():
    """Main entry point"""
    print("=" * 60)
    print("BLE IMU DATA LOGGER")
    print("=" * 60)
    print(f"Device: {DEVICE_NAME}")
    print(f"Activity: {ACTIVITY_NAME}")
    print(f"Log Directory: {LOG_DIR}")
    print("=" * 60)
    print()
    
    # Create CSV logger
    csv_logger = CSVLogger(ACTIVITY_NAME, LOG_DIR)
    
    # Create BLE logger
    ble_logger = BLEDataLogger(DEVICE_NAME, SERVICE_UUID, CHAR_UUID, csv_logger)
    
    try:
        # Connect to device
        if not await ble_logger.scan_and_connect():
            logger.error("❌ Failed to connect. Exiting.")
            return
        
        # Start logging
        await ble_logger.start_logging()
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        await ble_logger.disconnect()
        csv_logger.close()
        print("\n" + "=" * 60)
        print("✅ Logging session complete!")
        print("=" * 60)

# ============================================
# Run Script
# ============================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Quiting the program...")
