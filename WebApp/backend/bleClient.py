import asyncio
import struct
from bleak import BleakClient, BleakScanner

SERVICE_UUID = "180C"
CHARACTERISTIC_UUID = "2A56"

def handle_notification(sender, data):
    try:
        values = struct.unpack('fffff', data)  # Adjust if needed
        # print(f"AccelX: {values[0]:.3f}, AccelY: {values[1]:.3f}, AccelZ: {values[2]:.3f}, GyroZ: {values[3]:.3f}, Millis: {values[4]:.0f}")
        print(f"{values[0]:.3f}, {values[1]:.3f}, {values[2]:.3f}, {values[3]:.3f}, {values[4]:.0f}")

    except struct.error as e:
        print("Failed to unpack:", e)

async def run():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover(timeout=5)
    for d in devices:
        print(f"Found: {d.name}, Address: {d.address}")
        if d.name == "SensorNode":
            async with BleakClient(d.address) as client:
                print("Connected to SensorNode")
                await client.start_notify(CHARACTERISTIC_UUID, handle_notification)
                print("Listening for notifications (Ctrl+C to stop)...")

                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    print("Stopping...")
                    await client.stop_notify(CHARACTERISTIC_UUID)

asyncio.run(run())
