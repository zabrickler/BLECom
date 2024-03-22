import subprocess
import threading
import serial
import os
import time
import asyncio
from ble_serial.scan import main as scanner
import subprocess
import logging

async def main():
    ADAPTER = "hci0"
    SCAN_TIME = 5 
    SERVICE_UUID = None
    uuid = "49535343-1e4d-4bd9-ba61-23c647249616"
    Checking = True
    device1 = "44:B7:D0:2D:6A:B3" #Window
    device2 = "44:B7:D0:2C:D3:0A" #Motion
    device3 = "44:B7:D0:2C:D3:27" #Door

    while True:
        while Checking:
            devices = await scanner.scan(ADAPTER, SCAN_TIME, SERVICE_UUID)
    
            try:
                print(devices[device1])
                Checking = False
                #Make this into a thread
                #Lines 25 - 31 of serialExample.py
            except KeyError:
                try:
                    print(devices[device2])
                    Checking = False
                    #Make this into a thread
                except KeyError:
                    try:
                        print(devices[device3])
                        Checking = False
                    except KeyError:
                        print("No device found")






if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    asyncio.run(main())