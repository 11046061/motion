from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # 保護密碼

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='11046067',
        database='healthy'
    )
    return connection

@app.route('/')
def home():
    return render_template('home.html')

#新增會員
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        birthday = request.form.get('birthday')

        if None in [username, password, email, birthday]:
            flash('Please fill in all fields', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            query = """INSERT INTO members (username, password, email, birthday) 
                       VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, (username, hashed_password, email, birthday))
            connection.commit()
            flash('Registration successful! Please log in.', 'success')  # 显示成功消息
        except Exception as e:
            flash(str(e), 'error')
            return render_template('register.html')
        finally:
            if connection:
                cursor.close()
                connection.close()

        return redirect(url_for('login')+"?registered=True")  # 注册成功后重定向到登录页面
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']  # 注意前端用的是'email'作帳號
        password = request.form['password']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT password FROM members WHERE username = %s', (username,))
        account = cursor.fetchone()
        cursor.close()
        connection.close()

        if account and check_password_hash(account[0], password):
            return redirect(url_for('home'))  # 登录成功后连到首页
        else:
            error = 'Invalid username or password'  # 登入失敗的錯誤訊息
            return render_template('login.html', error=error)  # 直接返回頁面和錯誤訊息
    # 如果是 GET 请求，显示登录表单
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
