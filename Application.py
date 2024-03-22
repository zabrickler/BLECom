import subprocess
import threading
import serial
import os
import time
import asyncio
from ble_serial.scan import main as scanner
import subprocess
import logging
from ble_serial.bluetooth.ble_interface import BLE_interface
##########################################################
#HOW DOES THE RECEIVE CALLBACK WORK WITH MULTIPLE DEVICES#
##########################################################
#CAN I SETUP MULTIPLE BLE_INTERFACES

#This is called when the device receives data
def receive_callback(value: bytes):
    print("Received", value)
    #Logs it in file

async def sender(ble:BLE_interface):
    ble.queue_send(b"Hello world\n")
    ble.disconnect()

#Sends back an acknowledgement when it receives activity
#Not sure if I need to async this
def acknowledge(ble: BLE_interface):
    pass

async def connection(device, rwuuid, adapter, suuid):
    ble = BLE_interface(adapter, suuid)
    ble.set_receiver(receive_callback)
    try:
        await ble.connect(device, "public", 10.0)
        await ble.setup_chars(rwuuid, rwuuid, "rw")
        #await asyncio.gather(ble.send_loop(), hello_sender(ble))
    except Exception as e:
        print("An error occurred:", e)
    
    return ble

async def main():
    ADAPTER = "hci0"
    SCAN_TIME = 5 
    SERVICE_UUID = None
    uuid = "49535343-1e4d-4bd9-ba61-23c647249616"
    Checking = True
    device1 = "44:B7:D0:2C:D3:0A" #Motion
    device2 = "44:B7:D0:2D:6A:B3" #Window
    device3 = "44:B7:D0:2C:D3:27" #Door

    while True:
        while Checking:
            devices = await scanner.scan(ADAPTER, SCAN_TIME, SERVICE_UUID)
    
            try:
                print(devices[device1])
                #Checking = False #Might not need this if it awaits for the connection
                #Make this into a thread
                #Lines 25 - 31 of serialExample.py
                ble1 = await connection(device1, uuid, ADAPTER, SERVICE_UUID)
                print(ble1)
            except KeyError:
                try:
                    print(devices[device2])
                    #Checking = False
                    #Make this into a thread
                    ble2 = await connection(device2, uuid, ADAPTER, SERVICE_UUID)
                    print(ble2)
                except KeyError:
                    try:
                        print(devices[device3])
                        #Checking = False
                        #Make this into a thread
                        ble3 = await connection(device3, uuid, ADAPTER, SERVICE_UUID)
                        print(ble3)
                    except KeyError:
                        print("No device found")






if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    asyncio.run(main())
