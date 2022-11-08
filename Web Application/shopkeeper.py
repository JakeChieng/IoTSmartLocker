import mysql.connector
from flask import Flask, request, render_template, redirect, url_for
import time  #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

#aws ec2 stuff

conn = mysql.connector.connect(user="root", password="221013", host="localhost", database="Membership")

if conn:
    print("Connection successful")
    cursor = conn.cursor()
else:
    print("Connection failed")
    
app = Flask(__name__)

@app.route("/")
def nothing():
    return redirect(url_for('index'))

@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/order")
def get_orders():
    orders = "SELECT * FROM Orders"
    cursor.execute(orders)
    result = cursor.fetchall()
    return render_template("order.html", data = result)

@app.route("/customer")
def get_customers():
    customers = "SELECT * FROM Customers"
    cursor.execute(customers)
    result = cursor.fetchall()
    return render_template("customer.html", data = result)

@app.route("/locker")
def get_lockers():
    lockers = "SELECT * FROM Locker"
    cursor.execute(lockers)
    result = cursor.fetchall()
    return render_template("locker.html", data = result)

@app.route("/payment", methods = ["POST"])
def order_paid():
    ost = request.form["ost"]
    order = "UPDATE Orders SET status = 1 WHERE order_id = %s"
    cursor.execute(order, (ost, ))
    order = "UPDATE Orderdetails SET status = 1 WHERE order_id = %s"
    cursor.execute(order, (ost, ))
    conn.commit()
    return redirect(url_for('get_orders'))
    
@app.route("/details", methods = ["POST"])
def order_details():
    oid = request.form["oid"]
    details = "SELECT * FROM Orderdetails WHERE order_id = %s"
    cursor.execute(details, (oid, ))
    result = cursor.fetchone()
    temp = cursor.fetchall()
    lockers = "SELECT * FROM Locker"
    cursor.execute(lockers)
    alloc = cursor.fetchall()
    return render_template("details.html", data = result, locker = alloc)
    
@app.route("/locker", methods = ["POST"])
def set_locker():
    slo = request.form["locker_alloc"]
    oid = request.form["oid"]
    check = "SELECT * FROM Orderdetails WHERE locker_id = %s AND status != 2"
    cursor.execute(check, (slo, ))
    result = cursor.fetchone()
    temp = cursor.fetchall()
    print(result)
    if(result is None):
        alloc = "UPDATE Orderdetails SET locker_id = %s WHERE order_id = %s"
        cursor.execute(alloc, (slo, oid, ))
        alloc = "UPDATE Locker SET occupied = 1 WHERE locker_id = %s"
        cursor.execute(alloc, (slo, ))
        alloc = "UPDATE Locker SET closed = 1 WHERE locker_id = %s"
        cursor.execute(alloc, (slo, ))
        conn.commit()
    return redirect(url_for('get_orders'))
    
@app.route("/pickup", methods = ["POST"])
def picked_up():
    pup = request.form["pup"]
    order = "UPDATE Orders SET status = 2 WHERE order_id = %s"
    cursor.execute(order, (pup, ))
    order = "UPDATE Orderdetails SET status = 2 WHERE order_id = %s"
    cursor.execute(order, (pup, ))
    locker = "SELECT locker_id FROM Orderdetails WHERE order_id = %s"
    cursor.execute(locker, (pup, ))
    result = cursor.fetchone()
    temp = cursor.fetchall()
    locker_id = "UPDATE Locker SET occupied = 0 WHERE locker_id = %s"
    cursor.execute(locker_id, result)
    conn.commit()
    return redirect(url_for('get_orders'))

if __name__ == "__main__":
    app.run()