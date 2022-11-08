import json
import mysql.connector
import serial

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

SHOPNAME = "Jalan Song Shop"
AWS_EDGE_TOPIC = "smartlocker/edge"
AWS_CLOUD_TOPIC = "smartlocker/cloud"
AWS_INFO_TOPIC = "smartlocker/info"

# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient(SHOPNAME)
# myMQTTClient.configureEndpoint("YOUR.ENDPOINT", 8883)
myMQTTClient.configureEndpoint("a6gvbxmq08z2y-ats.iot.ap-southeast-1.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/ssmartlocker/server/cert/Amazon_Root_CA_1.pem", "/home/ssmartlocker/server/cert/bd76d6f21c0792f46f890d595e999d2443a00687a90fc056949f1ed6b2b2bef9-private.pem.key", "/home/ssmartlocker/server/cert/bd76d6f21c0792f46f890d595e999d2443a00687a90fc056949f1ed6b2b2bef9-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

#connect and publish
myMQTTClient.connect()
myMQTTClient.publish(AWS_INFO_TOPIC, "connected", 0)

# Compile information from DB and send to cloud as MQTT message
def send_cloud():
    conn = mysql.connector.connect(
        host="localhost",
        user="USER",
        password="PASSWORD",
        database="localServerDB"
    )

    # Gather information from all lockers
    query = """
    SELECT Locker, Lot, Occupied, Closed FROM Lockers
    """

    myCursor = conn.cursor()
    results = myCursor.fetchall()

    print(results)


# Message handler when receiving MQTT message from cloud
# Identify the shop ID that matches the local server is registered as.
# Break down commands into smaller components that matches the respective locker and lot.
def msg_callback(client, userdata, message):
    msg = json.loads(message.payload)

    if msg["Shop"] == SHOPNAME:
        # Unpack list of commands and send to Arduino via serial (XBee)
        commands = msg["CommandList"]

        for command in commands:
            # Send each command in JSON to XBee connected locker
            data = json.dumps(command)
            print(data)
            ser.write(data.encode("ascii"))

# Message handler when receiving serial message via XBee
# Update information in local database
# Combine all the information from all lockers in shop and send it as MQTT message to cloud
def serial_msg(dict_json):
    locker = dict_json["Locker"]
    lot = dict_json["Lot"]
    occupied = dict_json["Occupied"]
    closed = dict_json["Closed"]

    conn = mysql.connector.connect(
        host="localhost",
        user="USER",
        password="PASSWORD",
        database="localServerDB"
    )

    query = """UPDATE Lockers SET Occupied=%s, Closed=%s
    WHERE Locker=%s AND Lot=%s"""

    data = (occupied, closed, locker, lot)

    with conn:
        myCursor = conn.cursor()
        myCursor.execute(query, data)
        conn.commit()
        myCursor.close()
    
    send_cloud()

myMQTTClient.subscribe(AWS_CLOUD_TOPIC, 0, msg_callback)

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    ser.flush()
    send_cloud()

    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode("utf-8")
            try: 
                dict_json = json.loads(data)
                print(dict_json)
                serial_msg(dict_json)
            except json.JSONDecodeError as e:
                print("JSON:", e)


