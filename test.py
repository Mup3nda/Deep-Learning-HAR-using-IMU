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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVLogger:
    def __init__(self, activity, filedir):

        os.makedirs(filedir, exist_ok=True)

        timestamp = datetime.strftime("%d%m%Y_%H%M%S")

        self.file_name = f'{filedir}/{activity}_{timestamp}.csv'
        self.csv_file = open(self.csv_file, 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file, delimiter=';')
        self.csv_write.writerow(['timestamp', 'acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'])

        self.sample_count = 0

        logger.info("Csv file created")

    def write_row(self, data_dir):
        self.timestamp = datetime.strftime('%H%M%S')
        self.csv_writer([
            self.timestamp,
            data_dir['acc_x'],
            data_dir['acc_y'],
            data_dir['acc_z'],
            data_dir['gyro_x'],
            data_dir['gyro_y'],
            data_dir['gyro_z']
        ])

        self.sample_count += 1
        if self.sample_count % 100 == 0:
            self.csv_file.flush()

    def close(self):
        self.csv_file.flush()
        self.csv_file.close()
        logger.info('Closing csv file')

class BLEDataLogger:
    def __init__(self, device_name, service_uuid, char_uuid, csv_logger):
        self.device_name = device_name
        self.service_uuid = service_uuid
        self.char_uuid = char_uuid
        self.csv_logger = csv_logger
        self.client = None
        self.sample_count = 0
    
    async def scan_and_connect(self):
        logger.info("Scanning")
        devices = await BleakScanner.discover()

        esp_device = None
        for d in devices:
            if d.name == self.device_name:
                esp_device = d

        if not esp_device:
            logger("Could not find the device")
            for d in devices:
                logger.info(f"Found device name here {d.name}")
            return False
        
        logger.info(f"Found device at : {esp_device.address}")

        self.client = BleakClient(esp_device.address)
        await self.client.connect()
        logger.info("Connected")

        return True
    
    def notification_handler(self, sender, data):

        try:
            encoded = data.decoded('utf-8')

            parts = encoded.split(',')

            if not (parts == 6):
                logger.warning("Invalid formating")
                return None
            
            acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z = [float(x) for x in parts]

            data_dir = {
                'acc_x': acc_x,
                'acc_y': acc_y,
                'acc_z': acc_z,
                'gyro_x': gyro_x,
                'gyro_y': gyro_y,
                'gyro_z': gyro_z
            }

            self.csv_logger.writer_row(data_dir)
            self.sample_count += 1

            if self.sample_count % 10 == 0:
                logger.info(f"Samples: {self.sample_count:4d} | acc: [{acc_x:+6.2f}, {acc_y:+6.2f}, {acc_z:+6.2f}] | gyro: [{gyro_x:+6.3f}, {gyro_y:+6.3f}, {gyro_z:+6.3f}]")
        

        except ValueError as e:
            logger.warning(f"Parsog failed: {e}")
        except Exception as e:
            logger.error(f"Something went wrong: {e}")

    async def start_logging(self):
        if not self.client or self.client.is_connected():
            raise ConnectionError(f"Device not connected")
        
        logger.info("Sstarting logging")

        await self.client.start_notify(self.char_uuid, self.notification_handler)

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Quiting")
        
        await self.client.stop_notify(self.char_uuid)

    async def disconnect(self):
        if self.client.is_connected() and self.client:
            await self.client.disconnect()
            logger.info("Disconnected now!")


async def main():

    csv_logger = CSVLogger(ACTIVITY_NAME, LOG_DIR)

    ble_logger = BLEDataLogger(DEVICE_NAME, SERVICE_UUID, CHAR_UUID, csv_logger)

    try:
        if not await ble_logger.scan_and_connect():
            logger.error("Could not connect")
        ble_logger.start_logging()

    except Exception as e:
        logger.error(f"Got an error while trying to connect: {e}")
        return None
    finally:
        ble_logger.disconnect()
        csv_logger.close()


if __name__ == '__main__':
    asyncio.run(main())

    

    





