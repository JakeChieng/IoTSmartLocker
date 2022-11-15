import mysql.connector
from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
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
    #change to login
    return redirect(url_for('order_form'))
    
#incomplete
@app.route("/login")
def login():
    #redirect changes
    return render_template("login.html")
    
@app.route("/order_form")
#show list of products
def order_form():
    order = "SELECT * FROM Products"
    cursor.execute(order)
    product = cursor.fetchall()
    return render_template("order_form.html", data = product)
    
@app.route("/place_order", methods = ["POST"])
#place order
def place_order():
    today = datetime.today().strftime('%Y-%m-%d')
    #get payment method
    pay = request.form["payment_method"]
    #get remark
    rmk = request.form["remark"]
    #!!!!!!!!!!IMPORTANT!!!!!!!!!!
    #implement customer id after membership system is complete
    #!!!!!!!!!!IMPORTANT!!!!!!!!!!
    order = "INSERT INTO Orders (customer_id, order_date, status, payment_method, amount, remark) VALUES order_id = (1, %s, 0, %s, NULL, %s)"
    cursor.execute(order, (today, pay, rmk, ))
    last_id = "SELECT LAST_INSERT_ID()"
    cursor.execute(last_id)
    oid = cursor.fetchone()
    temp = cursor.fetchall()
    itm = request.form["item"]
    qty = request.form["qty"]
    #might need something to correlate order_ids across Orders and Orderdetails
    #order = "SELECT order_id FROM Orders WHERE "
    #cursor.execute(order, (itm, ))
    #oid = cursor.fetchone()
    #temp = cursor.fetchall()
    order = "SELECT product_id FROM Products WHERE product_name = %s"
    cursor.execute(order, (itm, ))
    pid = cursor.fetchone()
    temp = cursor.fetchall()
    order = "INSERT INTO Orderdetails (order_id, product_id, locker_id, quantityOrdered, status, remark) VALUES order_id = (%s, %s, -1, %s, 0, %s)"
    cursor.execute(order, (oid, pid, qty, rmk, ))
    conn.commit()
    return render_template("order_form.html")
    
@app.route("/customer_orders")
#check orders
def customer_orders():
    #!!!!!!!!!!IMPORTANT!!!!!!!!!!
    #implement customer id after membership system is complete
    #!!!!!!!!!!IMPORTANT!!!!!!!!!!
    #get orders based on customer id
    orders = "SELECT * FROM Orders WHERE customer_id = %s"
    cursor.execute(orders, ('1', ))
    result = cursor.fetchall()
    #get order details based on customer id
    orders = "SELECT * FROM Orderdetails WHERE customer_id = %s"
    cursor.execute(orders, ('1', ))
    details = cursor.fetchall()
    #get order id based on customer id
    orders = "SELECT product_id FROM Orderdetails WHERE customer_id = %s"
    cursor.execute(orders, ('1', ))
    pid = cursor.fetchone()
    temp = cursor.fetchall()
    #get product name based on product id
    orders = "SELECT product_name FROM Products WHERE product_id = %s"
    cursor.execute(orders, (pid, ))
    product = cursor.fetchone()
    temp = cursor.fetchall()
    return render_template("customer_orders.html", data = result, order = details, name = product)
    
@app.route("/open_locker", methods = ["POST"])
#open locker
def open_locker():
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
    return redirect(url_for('customer_orders'))
    
@app.route("/order_details", methods = ["POST"])
#get details of order
def order_details():
    #get order id
    oid = request.form["oid"]
    #get details of order id
    details = "SELECT * FROM Orderdetails WHERE order_id = %s"
    cursor.execute(details, (oid, ))
    result = cursor.fetchone()
    temp = cursor.fetchall()
    #get amount to pay for order id
    order = "SELECT amount FROM Orders WHERE order_id = %s"
    cursor.execute(order, (oid, ))
    amount = cursor.fetchone()
    temp = cursor.fetchall()
    return render_template("order_details.html", data = result, order = amount)

if __name__ == "__main__":
    app.run()