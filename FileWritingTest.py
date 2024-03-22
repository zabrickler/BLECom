import serial

while True:
    theInput = input("Do you want to arm/disarm the system?\nY or N")
    ser = serial.Serial('/dev/pts/1')

    if theInput == "Y":
        print("SENDING DATA!\n")
        ser.write(b'i')
        print(ser.read())
        print(ser.read())


    if theInput == "e":
        exit()
