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
import bleak
import requests

ble1 = None
ble2 = None
ble3 = None

#This is called when the device receives data
def motion_callback(value: bytes):
    print("Motion Message", value)
    global motionData
    motionData = motionData + value
    print(motionData)

def door_callback(value: bytes):
    print("Door Message", value)
    global doorData
    doorData = doorData + value
    print(doorData)

async def disarmMotion(ble: BLE_interface): #These are just for Motion right now
    global motionData
    global MotionArmedState
    global ble1
    for i in range(10):
        await asyncio.sleep(0.5)
        print("Sending disarm")
        ble.queue_send(b'DSM')
        if(ble1 == None or (b'A' in motionData)):
            MotionArmedState = False
            ble1.stop_loop()
            break
    ble.stop_loop()
    await ble.disconnect()

async def disarmDoor(ble: BLE_interface):
    print("We are in disarm")
    global doorData
    global DoorArmedState
    global ble3
    for i in range(10):
        await asyncio.sleep(0.5)
        print("Sending disarm")
        ble.queue_send(b'DSD')
        if(ble3 == None or (b'A' in doorData)):
            DoorArmedState = False
            ble3.stop_loop()
            break
    ble.stop_loop()
    await ble.disconnect()

async def armMotion(ble: BLE_interface):
    global motionData
    global MotionArmedState
    global ble1
    for i in range(10):
        await asyncio.sleep(0.5)
        print("Sending arm")
        ble.queue_send(b'RSM')
        if(ble1 == None or (b'A' in motionData)):
            MotionArmedState = True
            ble1.stop_loop()
            break
    ble.stop_loop()
    await ble.disconnect()

async def armDoor(ble: BLE_interface):
    global doorData
    global DoorArmedState
    global ble3
    for i in range(10):
        await asyncio.sleep(0.5)
        print("Sending Arm")
        ble.queue_send(b'RSD')
        if(ble3 == None or (b'A' in doorData)):
            DoorArmedState = True
            ble3.stop_loop()
            break
    ble.stop_loop()
    await ble.disconnect()

async def connection(device, rwuuid, adapter, suuid):
    ble = BLE_interface(adapter, suuid)
    if(device == "44:B7:D0:2C:D3:0A"):
        ble.set_receiver(motion_callback)
    elif(device == "44:B7:D0:2C:D3:27"):
        ble.set_receiver(door_callback)
    try:
        await ble.connect(device, "public", 10.0)
        await ble.setup_chars(rwuuid, rwuuid, "rw")
    except Exception as e:
        print("An error occurred:", e)
    
    return ble

async def main():
    global motionData
    motionData = b''
    global doorData
    doorData = b''
    
    activityLog = open("activityLog.txt", "a")
    
    PiArmedState = True

    global MotionArmedState
    MotionArmedState = True
    global DoorArmedState
    DoorArmedState = True
    
    global doorTriggered
    doorTriggered = False
    global motionTriggered
    motionTriggered = False

    notifyMessage = {'value1':"PLACEHOLDER"}
    notifyURL = 'https://maker.ifttt.com/trigger/Timeout/with/key/drkDV7BLk5F_sqrYTDTwbW'
    dbURL = 'https://home-security-90ecb2cf8b83.herokuapp.com/securitystatus'

    doorCheckInTime = time.time()
    motionCheckInTime = time.time()

    ADAPTER = "hci0"
    SCAN_TIME = 1 
    SERVICE_UUID = None
    uuid = "49535343-1e4d-4bd9-ba61-23c647249616"
    Checking = True
    device1 = "44:B7:D0:2C:D3:0A" #Motion
    device3 = "44:B7:D0:2C:D3:27" #Door

    while True:
        while Checking:
            devices = await scanner.scan(ADAPTER, SCAN_TIME, SERVICE_UUID)
    
            try:
                print(devices[device1])
                #Checking = False #Might not need this if it awaits for the connection
                global ble1
                motionCheckInTime = time.time()
                try:
                    ble1 = await connection(device1, uuid, ADAPTER, SERVICE_UUID)
                except Exception as e:
                    print("An error occurred", e)
                    await ble1.disconnect()
                print(ble1)
            except KeyError:
                print("Motion not found")
                try:
                    print(devices[device3])
                    global ble3
                    doorCheckInTime = time.time()
                    try:
                        ble3 = await connection(device3, uuid, ADAPTER, SERVICE_UUID)
                    except Exception as e:
                        print("An error occurred", e)
                        await ble3.disconnect()
                    print(ble3)
                except KeyError:
                    print("Door not found")

            response = requests.get(dbURL)
            data = response.json()
            ArmedStatus = data[0].get('status')
            if(ArmedStatus == 'Arm'):
                PiArmedState = True
            elif(ArmedStatus == 'Disarm'):
                PiArmedState = False

            #Armed and awaiting messages
            if(PiArmedState and (MotionArmedState or DoorArmedState)):        
                if b'MD' in motionData:
                    print("Motion activity")
                    theTime = time.localtime()
                    notifyMessage = {"value1":"Motion Sensor Activity"}
                    requests.post(notifyURL, notifyMessage)
                    motionTriggered = True
                    activityLog.write("Motion activity: " + str(theTime[1]) + "/" + str(theTime[2]) + "/" + str(theTime[0]) + "/" + str(theTime[1]) + " " + str(theTime[3]) + ":" + str(theTime[4]) + "\n")
                    try:
                        await asyncio.gather(ble1.send_loop(), disarmMotion(ble1))
                    except Exception as e:
                        print("An error has occurred", e)
                        await ble1.disconnect()
                    finally:
                        await ble1.disconnect()
                    motionData = b''
                    ble1 = None

                if b'DO' in doorData:
                    print("Door activity")
                    theTime = time.localtime()
                    notifyMessage = {"value1":"Door Sensor Activity"}
                    requests.post(notifyURL, notifyMessage)
                    doorTriggered = True
                    activityLog.write("Door activity: " + str(theTime[1]) + "/" + str(theTime[2]) + "/" + str(theTime[0]) + "/" + str(theTime[1]) + " " + str(theTime[3]) + ":" + str(theTime[4]) + "\n")
                    try:
                        await asyncio.gather(ble3.send_loop(), disarmDoor(ble3))
                    except Exception as e:
                        print("An error has occurred", e)
                        await ble3.disconnect()
                    finally:
                        await ble3.disconnect()
                    doorData = b''
                    ble3 = None

            #Disarmed
            if(not(PiArmedState)):
                doorTriggered = False
                motionTriggered = False
                if not(ble1 == None):
                    try:
                        await asyncio.gather(ble1.send_loop(), disarmMotion(ble1))
                        MotionArmedState = False
                    except Exception as e:
                        print("An error occurred", e)
                        ble1.stop_loop()
                        await ble1.disconnect()
                    finally:
                        ble1.stop_loop()
                        await ble1.disconnect()
                        motionData = b''
                        ble1 = None
                    motionData = b''
                    ble1 = None
   
                if not(ble3 == None):
                    try:
                        await asyncio.gather(ble3.send_loop(), disarmDoor(ble3))
                        DoorArmedState = False
                    except Exception as e:
                        print("An error occurred", e)
                        ble3.stop_loop()
                        await ble3.disconnect()
                    finally:
                        ble3.stop_loop()
                        await ble3.disconnect()
                        doorData = b''
                        ble3 = None 
                    doorData = b''
                    ble3 = None

            #Rearming
            if(PiArmedState and (not(MotionArmedState) or not(DoorArmedState))):
                if not(ble1 == None):
                    if(not(motionTriggered)):
                        try:
                            await asyncio.gather(ble1.send_loop(), armMotion(ble1))
                            MotionArmedState = True
                        except Exception as e:
                            print("An error occurred", e)
                            ble1.stop_loop()
                            await ble1.disconnect()
                        finally:
                            ble1.stop_loop()
                            await ble1.disconnect()
                            motionData = b''
                            ble1 = None
                        motionData = b''
                        ble1 = None

                if not(ble3 == None):
                    if(not(doorTriggered)):
                        try:
                            await asyncio.gather(ble3.send_loop(), armDoor(ble3))
                            DoorArmedState = True
                        except Exception as e:
                            print("An error occurred", e)
                            ble3.stop_loop()
                            await ble3.disconnect()
                        finally:
                            ble3.stop_loop()
                            await ble3.disconnect()
                            doorData = b''
                            ble3 = None
                        doorData = b''
                        ble3 = None

            #Health Check every 5 minutes
            if((time.time() - motionCheckInTime) > 300):
                notifyMessage = {"value1":"Motion Sensor Connection Loss"}
                requests.post(notifyURL, notifyMessage)
                #WANT TO LOG IN FILE THAT HEALTH CHECK FAILED

            if((time.time() - doorCheckInTime) > 300):
                notifyMessage = {"value1":"Door Sensor Connection Loss"}
                requests.post(notifyURL)

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    asyncio.run(main())
