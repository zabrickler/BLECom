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
import RPi.GPIO as GPIO

global ble1
ble1 = None
global ble3
ble3 = None
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)

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

async def disarmMotion(ble: BLE_interface):
    global motionData
    global MotionArmedState
    global ble1
    global notifyURL
    notifyURL = 'https://maker.ifttt.com/trigger/Timeout/with/key/drkDV7BLk5F_sqrYTDTwbW'
    for i in range(10):
        if((b'A' in motionData)):
            MotionArmedState = False
            notifyMessage = {"value1":"Motion Disarmed"}
            requests.post(notifyURL, notifyMessage)
            ble1.stop_loop()
            break
        await asyncio.sleep(0.5)
        print("Sending disarm")
        ble.queue_send(b'DSM')
        
    ble.stop_loop()
    await ble.disconnect()

async def disarmDoor(ble: BLE_interface):
    print("We are in disarm")
    global doorData
    global DoorArmedState
    global ble3
    global notifyURL
    notifyURL = 'https://maker.ifttt.com/trigger/Timeout/with/key/drkDV7BLk5F_sqrYTDTwbW'
    for i in range(10):
        if((b'A' in doorData)):
            DoorArmedState = False
            notifyMessage = {"value1":"Door Disarmed"}
            requests.post(notifyURL, notifyMessage)
            ble3.stop_loop()
            break
        await asyncio.sleep(0.5)
        print("Sending disarm")
        ble.queue_send(b'DSD')
        
    ble.stop_loop()
    await ble.disconnect()

async def armMotion(ble: BLE_interface):
    global motionData
    global MotionArmedState
    global ble1
    global notifyURL
    notifyURL = 'https://maker.ifttt.com/trigger/Timeout/with/key/drkDV7BLk5F_sqrYTDTwbW'
    for i in range(10):
        if((b'A' in motionData)):
            MotionArmedState = True
            notifyMessage = {"value1":"Motion Armed"}
            requests.post(notifyURL, notifyMessage)
            ble1.stop_loop()
            break
        await asyncio.sleep(0.5)
        print("Sending arm")
        ble.queue_send(b'RSD')
        
    ble.stop_loop()
    await ble.disconnect()

async def armDoor(ble: BLE_interface):
    global doorData
    global DoorArmedState
    global ble3
    global notifyURL
    notifyURL = 'https://maker.ifttt.com/trigger/Timeout/with/key/drkDV7BLk5F_sqrYTDTwbW'
    for i in range(10):
        if((b'A' in doorData)):
            DoorArmedState = True
            notifyMessage = {"value1":"Door Armed"}
            requests.post(notifyURL, notifyMessage)
            ble3.stop_loop()
            break
        await asyncio.sleep(0.5)
        print("Sending Arm")
        ble.queue_send(b'RSD')
        
    ble.stop_loop()
    await ble.disconnect()

async def connection(device, rwuuid, adapter, suuid):
    ble = BLE_interface(adapter, suuid)
    if(device == "44:B7:D0:2C:D3:0A"): #Motion MAC Address
        ble.set_receiver(motion_callback) 
    elif(device == "44:B7:D0:2C:D3:27"): #Door MAC Address
        ble.set_receiver(door_callback)
    try:
        await ble.connect(device, "public", 10.0)
        await ble.setup_chars(rwuuid, rwuuid, "rw")
    except Exception as e:
        print("An error occurred:", e)
    
    return ble

def get_status_armed():
    global response
    global dbURL
    dbURL = 'https://home-security-90ecb2cf8b83.herokuapp.com/securitystatus'
    global data

    global PiArmedState
    PiArmedState = True
    global doorTriggered
    doorTriggered = False
    global motionTriggered
    motionTriggered = False
    while True:
        try:
            response = requests.get(dbURL)
            data = response.json()
            ArmedStatus = data[0].get('status')
            if(ArmedStatus == 'Arm'):
                PiArmedState = True
            elif(ArmedStatus == 'Disarm'):
                PiArmedState = False
                motionTriggered = False
                doorTriggered = False
                GPIO.output(17,GPIO.LOW)
            time.sleep(1)
        except Exception as e:
            print("Error om status ", e)

armState = threading.Thread(target=get_status_armed).start()

async def main():
    global ble1
    global ble3

    global motionData
    motionData = b''
    global doorData
    doorData = b''
    MotionPriority = True
    
    activityLog = open("activityLog.txt", "a")
    
    global PiArmedState
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
    global notifyURL
    notifyURL = 'https://maker.ifttt.com/trigger/Timeout/with/key/drkDV7BLk5F_sqrYTDTwbW'
    global dbURL
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

            if(MotionPriority):
                try:
                    print(devices[device1])
                    try:
                        ble1 = await connection(device1, uuid, ADAPTER, SERVICE_UUID)
                        motionCheckInTime = time.time()
                        MotionPriority = False
                    except Exception as e:
                        print("An error occurred", e)
                        await ble1.disconnect()
                    print(ble1)
                except KeyError:
                    print("Motion not found")
                    try:
                        print(devices[device3])
                        try:
                            ble3 = await connection(device3, uuid, ADAPTER, SERVICE_UUID)
                            doorCheckInTime = time.time()
                        except Exception as e:
                            print("An error occurred", e)
                            await ble3.disconnect()
                        print(ble3)
                    except KeyError:
                        print("Door not found")
            else:
                try:
                    print(devices[device3])
                    try:
                        ble3 = await connection(device3, uuid, ADAPTER, SERVICE_UUID)
                        doorCheckInTime = time.time()
                        MotionPriority = True
                    except Exception as e:
                        print("An error occurred", e)
                        await ble3.disconnect()
                    print(ble3)
                except KeyError:
                    print("Door not found")
                    try:
                        print(devices[device1])
                        try:
                            ble1 = await connection(device1, uuid, ADAPTER, SERVICE_UUID)
                            motionCheckInTime = time.time()
                        except Exception as e:
                            print("An error occurred", e)
                            await ble1.disconnect()
                        print(ble1)
                    except KeyError:
                        print("Motion not found")

            #Armed and awaiting messages
            if(PiArmedState and (MotionArmedState or DoorArmedState)):        
                if b'MD' in motionData:
                    GPIO.output(17,GPIO.HIGH)
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
                    GPIO.output(17,GPIO.HIGH)
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
                        #MotionArmedState = False
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
                        #DoorArmedState = False
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
                    if(not(motionTriggered) and not(MotionArmedState)):
                        try:
                            await asyncio.gather(ble1.send_loop(), armMotion(ble1))
                            #MotionArmedState = True
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
                    if(not(doorTriggered) and not(DoorArmedState)):
                        try:
                            await asyncio.gather(ble3.send_loop(), armDoor(ble3))
                            #DoorArmedState = True
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
                motionCheckInTime = time.time()
                #WANT TO LOG IN FILE THAT HEALTH CHECK FAILED

            if((time.time() - doorCheckInTime) > 300):
                notifyMessage = {"value1":"Door Sensor Connection Loss"}
                requests.post(notifyURL, notifyMessage)
                doorCheckInTime = time.time()

if __name__ == "__main__":
    logging.basicConfig(level = logging.INFO)
    asyncio.run(main())
