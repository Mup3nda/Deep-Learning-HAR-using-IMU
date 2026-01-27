import asyncio
import logging
from bleak import BleakScanner, BleakClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BLEClient:
    def __init__(self, device_name="ESP32-NimBLE-Test", service_uuid="12345678-1234-1234-1234-1234567890ab", char_uuid="abcdefab-1234-5678-1234-abcdefabcdef"):
        self.device_name = device_name
        self.service_uuid = service_uuid
        self.char_uuid = char_uuid
        self.client = None

    async def scan_and_connect(self):
        logger.info("Scanning for devices...")
        devices = await BleakScanner.discover()

        esp = None
        for d in devices:
            if d.name == self.device_name:
                esp = d
                break

        if not esp:
            logger.error("Device not found")
            return False

        logger.info(f"Connecting to {esp.address}")
        self.client = BleakClient(esp.address)
        await self.client.connect()
        logger.info("Connected")
        return True

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            logger.info("Disconnected")

    async def read_characteristic(self):
        if not self.client or not self.client.is_connected:
            raise ConnectionError("Not connected")
        value = await self.client.read_gatt_char(self.char_uuid)
        return value.decode()

    async def write_characteristic(self, data):
        if not self.client or not self.client.is_connected:
            raise ConnectionError("Not connected")
        await self.client.write_gatt_char(self.char_uuid, data.encode() if isinstance(data, str) else data)

    async def start_notifications(self, handler):
        if not self.client or not self.client.is_connected:
            raise ConnectionError("Not connected")
        await self.client.start_notify(self.char_uuid, handler)

    async def stop_notifications(self):
        if not self.client or not self.client.is_connected:
            raise ConnectionError("Not connected")
        await self.client.stop_notify(self.char_uuid)

async def main():
    client = BLEClient()

    try:
        if not await client.scan_and_connect():
            return

        def notification_handler(sender, data):
            logger.info(f"Notification: {data.decode()}")

        await client.start_notifications(notification_handler)

        # value = await client.read_characteristic()  # read once
        # logger.info(f"Read: {value}")

        # await client.write_characteristic("Hello from laptop") # test

        # logger.info("Listening for notifications (10s)...")
        # await asyncio.sleep(10)

        logger.info("Listening for notifications... (Press Ctrl+C to stop)")
        try:
            while True:
                await asyncio.sleep(1)  # Keep connection alive
        except KeyboardInterrupt:
            logger.info("Stopping...")


        await client.stop_notifications()

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())