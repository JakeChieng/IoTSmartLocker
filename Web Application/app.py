import mysql.connector
from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
import time  #Import time library
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from werkzeug.security import generate_password_hash, check_password_hash
#aws ec2 stuff

conn = mysql.connector.connect(user="root", password="221013", host="localhost", database="Membership1")

if conn:
    print("Connection successful")
    cursor = conn.cursor()
else:
    print("Connection failed")
    
app = Flask(__name__)

@app.route("/")
def nothing():
    #change to login
    return redirect(url_for('test'))

@app.route("/test")
def test():
    #change to login
    return render_template("login.html")

@app.route("/testp")
def othing():
    #change to login
    return render_template("payment.html")

#incomplete
@app.route("/login", methods = ["POST"])
def login():

    email = request.form["uname"]
    pw = request.form["pword"]

    query = "SELECT password FROM Customers WHERE email = %s"
    cursor.execute(query, (email,))
    encryptPass = cursor.fetchone()
    temp = cursor.fetchall()
    print(encryptPass)
    
    if check_password_hash(encryptPass[0], pw) :
        print("password is correct")
        order = "SELECT * FROM Products"
        cursor.execute(order)
        product = cursor.fetchall()
        return render_template("order_form.html", data = product)
    else:
        print("password is not correct")
        return render_template("login.html",msg="no" )
    return redirect(url_for('test'))

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
def details():
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

if __name__ == "__main__":
    app.run()