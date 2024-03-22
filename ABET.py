import subprocess
import threading
import serial
import os
import time

def runBLESerial(deviceID, readUUID, writeUUID, thePort):
    command = ["ble-serial", "-d", deviceID, "-r", readUUID, "-w", writeUUID, "-p", thePort]

    subprocess.run(command)

ID1 = "44:B7:D0:2C:D3:0A"
ID2 = "44:B7:D0:2D:6A:B3"
UUID = "49535343-1e4d-4bd9-ba61-23c647249616"
port1 = "/tmp/ttyBLE"
port2 = "/tmp/ttyBLE1"

bleThread = threading.Thread(target = runBLESerial, args = (ID1, UUID, UUID, port1))
bleThread.daemon = True
bleThread.start()

bleThread1 = threading.Thread(target = runBLESerial, args = (ID2, UUID, UUID, port2))
bleThread1.daemon = True
bleThread1.start()
