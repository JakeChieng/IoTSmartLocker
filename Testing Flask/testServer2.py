testServer2.py

import serial
from flask import Flask,  request,render_template 
import threading

app = Flask(__name__)

device = '/dev/ttyUSB0' 
             
@app.route('/')
def testServer():
    global p
    p = threading.Thread(target=sqlUp, args=(10000000,))
    p.daemon = True
    p.start()

    return render_template('testServer.html', **templateData)
    
@app.route("/<action>") 
def action(action):
    msg1=''
    waterpump ='3'
    if action == 'action1' : 
        waterpump='1'
        msg1='servo TURNed 90 degree' 
    if action == 'action2' : 
        waterpump='0'
        msg1='servo TURNed back to 0 degree'  

    # This data will be sent to arduino
    ser.write((servo).encode('utf-8'))
    
    templateData = {
        'msg'  : msg1
        }
    # Pass the template data into the template act.html and return it 
    return render_template('act.html', **templateData)

if __name__ == "__main__" :
    ser = serial.Serial(device, 9600, timeout=1)
    ser.flush() 
    app.run(host='0.0.0.0', port = 8080, debug = False)



