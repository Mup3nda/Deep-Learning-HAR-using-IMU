#!/usr/bin/env python3
"""
Helper script to find available serial ports
"""

import serial.tools.list_ports

print("\n" + "="*60)
print("AVAILABLE SERIAL PORTS")
print("="*60)

ports = serial.tools.list_ports.comports()

if not ports:
    print("No serial ports found!")
else:
    for i, port in enumerate(ports, 1):
        print(f"\n{i}. {port.device}")
        print(f"   Description: {port.description}")
        print(f"   Manufacturer: {port.manufacturer}")
        
        # Highlight likely ESP32/Arduino ports
        if 'usb' in port.device.lower() or 'serial' in port.device.lower():
            print("   👉 This looks like an ESP32/Arduino port!")

print("\n" + "="*60)
print("\nUpdate SERIAL_PORT in read_imu.py with one of these devices.")
print("="*60 + "\n")
