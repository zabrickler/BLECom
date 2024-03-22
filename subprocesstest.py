import subprocess
import threading
import serial
import os
import time

def run_ble_serial(device_id, read_uuid, write_uuid):
    command = ["ble-serial", "-d", device_id, "-r", read_uuid, "-w", write_uuid]

    try:
        subprocess.run(command, check = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")

device_id = "44:B7:D0:2C:D3:0A"
read_uuid = "49535343-1e4d-4bd9-ba61-23c647249616"
write_uuid = "49535343-1e4d-4bd9-ba61-23c647249616"

ble_thread = threading.Thread(target=run_ble_serial, args = (device_id, read_uuid, write_uuid))
ble_thread.daemon = True
ble_thread.start()

isIt = False

while True:
    try:
        file_stat = os.stat = os.stat('/dev/pts/1')
        print("File exists")
        break
    except FileNotFoundError:
        print("Waiting on file")
        time.sleep(1)


ser = serial.Serial(port = '/dev/pts/1', timeout = 1)

response = 'N'

while not(response == b'A'):
    print("SENDING DATA!\n")
    ser.write(b'A')
    ser.write(b'B')
    ser.write(b'C')

    response = ser.read()
    print(response)

subprocess.run(["bluetoothctl", "disconnect", device_id])

print("End of process")
