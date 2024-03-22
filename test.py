from bluepy import btle

mac = "44:B7:D0:2C:D3:0A"

peripheral = btle.Peripheral(mac)

uuid = "49535343-1e4d-4bd9-ba61-23c647249616"

service = peripheral.getServiceByUUID(uuid)

readChar = service.getCharacteristics(uuid)[0]
writeChar = service.getCharacteristics(uuid)[0]

data = readChar.read()
print("Received data:", data)

datatowrite = b"Hello"
writeChar.write(datatowrite)

peripheral.disconnect()
