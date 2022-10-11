import time  #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("MyCloudComputer")
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 8883)
myMQTTClient.configureEndpoint("a6gvbxmq08z2y-ats.iot.ap-southeast-1.amazonaws.com", 8883)#v
myMQTTClient.configureCredentials("/home/ubuntu/certEc2/AmazonRootCA1.pem", "/home/ubuntu/certEc2/0f2deb2a9e43840ae73fb949f9ed54e437cac1f3d45323efe2fcfcee4692afe4-private.pem.key", "/home/ubuntu/certEc2/0f2deb2a9e43840ae73fb949f9ed54e437cac1f3d45323efe2fcfcee4692afe4-certificate.pem.crt")#v
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

#connect and publish
myMQTTClient.connect()
myMQTTClient.publish("cloud/info", "connected", 0)
#myMQTTClient.publish("cloud/info", "connected", 0)

while 1:
    time.sleep(2)  #Delay of 2 seconds
    
    value = 200
    payload = '{"cloud message: ":'+ str(value) +'}'
    print (payload)
    myMQTTClient.publish("cloud/data", payload, 0)
