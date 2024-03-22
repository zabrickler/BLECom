import subprocess

def kill_ble_serial():
    subprocess.run(["bluetoothctl", "disconnect", "44:B7:D0:2C:D3:0A"])

kill_ble_serial()
