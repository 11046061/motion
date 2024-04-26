import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder='static', template_folder='templates')

def get_db_connection():
    connection = mysql.connector.connect(host='localhost',
                                         port='3306',
                                         user='root',
                                         password='11046061',  # Use your actual MySQL root password
                                         database='sql_sports')  # Use your actual database name
    return connection

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    full_name = request.form['full_name']
    age = request.form['age']
    gender = request.form['gender']
    address = request.form['address']
    
    connection = get_db_connection()
    cursor = connection.cursor()
    query = """INSERT INTO members (username, password, email, full_name, age, gender, address) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(query, (username, password, email, full_name, age, gender, address))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

