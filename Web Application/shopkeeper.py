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
#return all orders in database
def get_orders():
    orders = "SELECT * FROM Orders"
    cursor.execute(orders)
    result = cursor.fetchall()
    return render_template("order.html", data = result)

@app.route("/customer")
#return all customers in database
def get_customers():
    customers = "SELECT * FROM Customers"
    cursor.execute(customers)
    result = cursor.fetchall()
    return render_template("customer.html", data = result)

@app.route("/locker")
#return all lockers in database
def get_lockers():
    lockers = "SELECT * FROM Locker"
    cursor.execute(lockers)
    result = cursor.fetchall()
    return render_template("locker.html", data = result)

@app.route("/payment", methods = ["POST"])
#set order as paid by customer
def order_paid():
    #get order id
    ost = request.form["ost"]
    #update order status to paid in Orders
    order = "UPDATE Orders SET status = 2 WHERE order_id = %s"
    cursor.execute(order, (ost, ))
    #update order status to paid in Orderdetails
    order = "UPDATE Orderdetails SET status = 2 WHERE order_id = %s"
    cursor.execute(order, (ost, ))
    conn.commit()
    return redirect(url_for('get_orders'))
    
@app.route("/details", methods = ["POST"])
#get details of order
def order_details():
    #get order id
    oid = request.form["oid"]
    #get details of order id
    details = "SELECT * FROM Orderdetails WHERE order_id = %s"
    cursor.execute(details, (oid, ))
    result = cursor.fetchone()
    temp = cursor.fetchall()
    #get all lockers to be assigned
    lockers = "SELECT * FROM Locker"
    cursor.execute(lockers)
    alloc = cursor.fetchall()
    #get amount to pay for order id
    order = "SELECT amount FROM Orders WHERE order_id = %s"
    cursor.execute(order, (oid, ))
    amount = cursor.fetchone()
    temp = cursor.fetchall()
    return render_template("details.html", data = result, locker = alloc, order = amount)
    
@app.route("/locker", methods = ["POST"])
#assign locker to order
def set_locker():
    #get locker id
    slo = request.form["locker_alloc"]
    #get order id
    oid = request.form["oid"]
    #get details of order that's not picked up
    check = "SELECT * FROM Orderdetails WHERE locker_id = %s AND status != 3"
    cursor.execute(check, (slo, ))
    result = cursor.fetchone()
    temp = cursor.fetchall()
    #check if the order is not picked up
    if(result is None):
        #set order's assigned locker 
        alloc = "UPDATE Orderdetails SET locker_id = %s WHERE order_id = %s"
        cursor.execute(alloc, (slo, oid, ))
        #!!!!!!!!!! might be deleted in favor of sensor !!!!!!!!!!
        #set locker's occupied and closed status
        alloc = "UPDATE Locker SET occupied = 1, closed = 1 WHERE locker_id = %s"
        cursor.execute(alloc, (slo, ))
        conn.commit()
    return redirect(url_for('get_orders'))
    
@app.route("/amount", methods = ["POST"])
#set amount to be paid
def set_amount():
    #get locker id
    oid = request.form["oid"]
    #get amount to be paid
    amt = request.form["amt"]
    #set the amount to be paid for an order
    order = "UPDATE Orders SET amount = %s WHERE order_id = %s"
    cursor.execute(order, (amt, oid, ))
    order = "UPDATE Orderdetails SET status = 1 WHERE order_id = %s"
    cursor.execute(order, (oid, ))
    conn.commit()
    return redirect(url_for('get_orders'))
    
#!!!!!!!!!! might be deleted for the verson in customer.py !!!!!!!!!!
@app.route("/pickup", methods = ["POST"])
#set order status to picked up by customer
def picked_up():
    #get order id
    pup = request.form["pup"]
    #set order's status to picked up
    order = "UPDATE Orders SET status = 3 WHERE order_id = %s"
    cursor.execute(order, (pup, ))
    #set order's status to picked up
    order = "UPDATE Orderdetails SET status = 3 WHERE order_id = %s"
    cursor.execute(order, (pup, ))
    #get locker id of picked up order
    locker = "SELECT locker_id FROM Orderdetails WHERE order_id = %s"
    cursor.execute(locker, (pup, ))
    result = cursor.fetchone()
    temp = cursor.fetchall()
    #!!!!!!!!!! might be changed in favor of sensor !!!!!!!!!!
    #set locker assigned to picked up order to unoccupied
    locker_id = "UPDATE Locker SET occupied = 0, closed = 0 WHERE locker_id = %s"
    cursor.execute(locker_id, result)
    conn.commit()
    return redirect(url_for('get_orders'))
    
    
@app.route("/login")
def login():
    return render_template("login.html")

if __name__ == "__main__":
    app.run()