import mysql.connector
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, static_folder='static', template_folder='templates')

def get_db_connection():
    connection = mysql.connector.connect(host='localhost',
                                         port='3306',
                                         user='root',
                                         password='113409',  # Use your actual MySQL root password
                                         database='sql_sports')  # Use your actual database name
    return connection

@app.route('/')
def home():
    return render_template('login.html')

#新增會員資料
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
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
        return redirect(url_for('login'))
    else:
        # 如果是 GET 請求，顯示註冊表單
        return render_template('register.html')
    
#登入畫面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM members WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        cursor.close()
        connection.close()

        if account:
            return redirect(url_for('home'))  # 登入成功後連到首頁
        else:
            return "Invalid username or password"  # 登入失敗
    # 如果是 GET 請求，顯示登入表單
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)

