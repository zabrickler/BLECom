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

ble1 = None
ble2 = None
ble3 = None

######################################################################
#WHAT IS THE PLAN FOR PUSHING THE BUTTON TO ENABLE OR DISABLE DEVICES#
######################################################################
###################################################################
#Might need to separate the logic from the scanning and connecting#
###################################################################

#This is called when the device receives data
def motion_callback(value: bytes):
    print("Motion Message", value)
    global motionData
    motionData = motionData + value
    print(motionData)

def window_callback(value: bytes):
    print("Window Message", value)
    global windowData
    windowData = windowData + value
    print(windowData)

def door_callback(value: bytes):
    print("Door Message", value)
    global doorData
    doorData = doorData + value
    print(doorData)

#Sends back an acknowledgement when it receives activity
async def acknowledge(ble: BLE_interface):
    while True:
        await asyncio.sleep(3.0)
        print("Sending ack")
        ble.queue_send(b'A')

async def disarmDev(ble: BLE_interface): #These are just for Motion right now
    global motionData
    while not(b'A' in motionData):
        await asyncio.sleep(3.0)
        print("Sending disarm")
        ble.queue_send(b'DSM')
    ble.disconnect()

async def armDev(ble: BLE_interface):
    while True:
        await asyncio.sleep(3.0)
        print("Sending arm")
        ble.queue_send(b'RSM')

async def connection(device, rwuuid, adapter, suuid):
    ble = BLE_interface(adapter, suuid)
    if(device == "44:B7:D0:2C:D3:0A"):
        ble.set_receiver(motion_callback)
    elif(device == "44:B7:D0:2D:6A:B3"):
        ble.set_receiver(window_callback)
    else:
        ble.set_receiver(door_callback)
    try:
        await ble.connect(device, "public", 10.0)
        await ble.setup_chars(rwuuid, rwuuid, "rw")
        #await asyncio.gather(ble.send_loop(), hello_sender(ble))
    except Exception as e:
        print("An error occurred:", e)
    
    return ble

async def main():
    global motionData
    motionData = b''
    global windowData
    windowData = b''
    global doorData
    doorData = b''
    activityLog = open("activityLog.txt", "a")
    PiArmedState = True
    DevicesArmedState = True

    ADAPTER = "hci0"
    SCAN_TIME = 1 
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
                global ble1
                ble1 = await connection(device1, uuid, ADAPTER, SERVICE_UUID)
                print(ble1)
            except KeyError:
                try:
                    print(devices[device2])
                    global ble2
                    ble2 = await connection(device2, uuid, ADAPTER, SERVICE_UUID)
                    print(ble2)
                except KeyError:
                    try:
                        print(devices[device3])
                        global ble3
                        ble3 = await connection(device3, uuid, ADAPTER, SERVICE_UUID)
                        print(ble3)
                    except KeyError:
                        print("No device found")

            if(PiArmedState and DevicesArmedState):        
                if b'MD' in motionData:
                    print("Motion activity")
                    theTime = time.localtime()
                    activityLog.write("Motion activity: " + str(theTime[1]) + "/" + str(theTime[2]) + "/" + str(theTime[0]) + "/" + str(theTime[1]) + " " + str(theTime[3]) + ":" + str(theTime[4]) + "\n")
                    await asyncio.gather(ble1.send_loop(), acknowledge(ble1))
                    motionData = b''

                if b'PLACEHOLDER' in windowData:
                    print("Window activity")
                    activityLog.write("Window activity: " + str(theTime[1]) + "/" + str(theTime[2]) + "/" + str(theTime[0]) + "/" + str(theTime[1]) + " " + str(theTime[3]) + ":" + str(theTime[4]) + "\n")
                    await asyncio.gather(ble2.send_loop(), acknowledge(ble2))
                    windowData = b''

                if b'DO' in doorData:
                    print("Door activity")
                    activityLog.write("Door activity: " + str(theTime[1]) + "/" + str(theTime[2]) + "/" + str(theTime[0]) + "/" + str(theTime[1]) + " " + str(theTime[3]) + ":" + str(theTime[4]) + "\n")
                    await asyncio.gather(ble3.send_loop(), acknowledge(ble3))
                    doorData = b''
            
            if(not(PiArmedState) and DevicesArmedState):
                if not(motionData == b''):
                    await asyncio.gather(ble1.send_loop(), disarmDev(ble1))

                if not(windowData == b''):
                    await asyncio.gather(ble2.send_loop(), disarmDev(ble2))

                if not(doorData == b''):
                    await asyncio.gather(ble3.send_loop(), disarmDev(ble3))
                
                DevicesArmedState = False

            if(PiArmedState and not(DevicesArmedState)):
                pass
                #How do I know when it is connected
                     

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    asyncio.run(main())
