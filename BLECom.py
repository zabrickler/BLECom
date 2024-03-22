import subprocess
import threading
import serial
import os
import time

def run_ble_serial(deviceID, readUUID, writeUUID, thePort):
    command = ["ble-serial", "-d", deviceID, "-r", readUUID, "-w", writeUUID, "-p", thePort]

    try:
        subprocess.run(command, check = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

deviceID1 = "44:B7:D0:2C:D3:0A"
deviceID2 = "44:B7:D0:2D:6A:B3"
UUID = "49535343-1e4d-4bd9-ba61-23c647249616"
port1 = "/tmp/ttyBLE"
port2 = "/tmp/ttyBLE1"

bleThread1 = threading.Thread(target = run_ble_serial, args = (deviceID1, UUID, UUID, port1))
bleThread1.daemon = True
bleThread1.start()

while True:
    try:
        fileStat1 = os.stat('/dev/pts/1')
        print("File exists")
        break
    except FileNotFoundError:
        print("Waiting on File")
        time.sleep(1)

time.sleep(10)

ser1 = serial.Serial(port = '/dev/pts/1', timeout = 1)

bleThread2 = threading.Thread(target = run_ble_serial, args = (deviceID2, UUID, UUID, port2))
bleThread2.daemon = True
bleThread2.start()

while True:
    try:
        fileStat2 = os.stat('/dev/pts/2')
        print("File exists")
        break
    except FileNotFoundError:
        print("Waiting on File")
        time.sleep(1)

time.sleep(10)

ser2 = serial.Serial(port = '/dev/pts/2', timeout = 1)

time.sleep(5)

response1 = 'N'
response2 = 'N'
ack1 = True
ack2 = True

while ack1 or ack2: if not(response1 == b'A'):
        print("SENDING DATA TO MOTION\n")
        ser1.write(b'A')
        ser1.write(b'B')
        ser1.write(b'C')

        response1 = ser1.read()
        print(response1)

    if not(response2 == b'A'):
        print("SENDING DATA TO WINDOW\n")
        ser2.write(b'A')
        ser2.write(b'B')
        ser2.write(b'C')

        response2 = ser2.read()
        print(response2)

    if(response1 == b'A'):
        subprocess.run(["bluetoothctl", "disconnect", deviceID1])
        ack1 = False

    if(response2 == b'A'):
        subprocess.run(["bluetoothctl", "disconnect", deviceID2])
        ack2 = False

print("End of Process")

