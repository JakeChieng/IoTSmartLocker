testServer2.py

from flask import Flask,  request,render_template 

app = Flask(__name__)

msg = { 
0: {'title' : 'led on', 'message' : 'led off'}
}

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
             
@app.route('/')
def testServer():
	templateData = { 'TheSet' : msg }
    return render_template('testServer.html', **templateData)
    
@app.route("/<action>") 
def action(action):
    led='3'
    if action == 'action1':
		led='1' #led on
	if action == 'action2':
		led='0' #led off
        
    payload = '{"cloud message: ":'+ led +'}'
    print(payload)
    myMQTTClient.publish("cloud/data", payload, 0)
    
	templateData = { 'TheSet' : msg }

    return render_template('act.html', **templateData)

if __name__ == "__main__" :
	app.run(host='0.0.0.0',port=8080,debug=False)

