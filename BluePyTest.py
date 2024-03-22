import asyncio
from ble_serial.scan import main as scanner
import subprocess

async def main():
    ADAPTER = "hci0"
    SCAN_TIME = 5 
    SERVICE_UUID = None
    uuid = "49535343-1e4d-4bd9-ba61-23c647249616"
    Checking = True

    while Checking:
        devices = await scanner.scan(ADAPTER, SCAN_TIME, SERVICE_UUID)
    
        try:
            print(devices["44:B7:D0:2D:6A:B3"])
            Checking = False
            subprocess.run(["ble-serial", "-d", "44:B7:D0:2D:6A:B3", "-r", uuid, "-w", uuid])
        except KeyError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
