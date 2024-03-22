import asyncio, logging, time
from ble_serial.bluetooth.ble_interface import BLE_interface

def receive_callback(value: bytes):
    print("Reieved:", value)

async def hello_sender(ble: BLE_interface):
    x = 0
    for x in range(10):
        await asyncio.sleep(1.0)
        print("Sending...")
        ble.queue_send(b"i")       
    await ble.disconnect()

async def main():
    ADAPTER = "hci0"
    SERVICE_UUID = None
    WRITE_UUID = "49535343-1e4d-4bd9-ba61-23c647249616"
    READ_UUID = "49535343-1e4d-4bd9-ba61-23c647249616"
    DEVICE = "44:B7:D0:2C:D3:0A"

    ble = BLE_interface(ADAPTER, SERVICE_UUID)
    ble.set_receiver(receive_callback)

    try:
        await ble.connect(DEVICE, "public", 10.0)
        await ble.setup_chars(WRITE_UUID, READ_UUID, "rw")
        await asyncio.gather(ble.send_loop(), hello_sender(ble))
    finally:
       # await ble.disconnect()
       pass

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    asyncio.run(main())
