rpitestServer2.py

import serial
import time  #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

device = '/dev/ttyUSB0'

def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    
# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("SrRPI")
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 8883)
myMQTTClient.configureEndpoint("a6gvbxmq08z2y-ats.iot.ap-southeast-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/ssmartlocker/server/cert/Amazon_Root_CA_1.pem", "/home/ssmartlocker/server/cert/bd76d6f21c0792f46f890d595e999d2443a00687a90fc056949f1ed6b2b2bef9-private.pem.key", "/home/ssmartlocker/server/cert/bd76d6f21c0792f46f890d595e999d2443a00687a90fc056949f1ed6b2b2bef9-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

#connect and publish
myMQTTClient.connect()
myMQTTClient.publish("rpi/info", "connected", 0)

ser = serial.Serial(device, 9600, timeout=1)
while 1:
    time.sleep(2)  #Delay of 2 seconds
   
    myMQTTClient.subscribe("cloud/data", 0,customCallback)
    ser.write((message.payload).encode('utf-8'))
