import serial
Bee = serial.Serial('/dev/ttyUSB0', 9600)
lockStat = 'unlock'
lockStat = lockStat.encode("utf-8")
Bee.write(lockStat)