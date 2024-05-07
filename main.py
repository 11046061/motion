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
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        birthday = request.form.get('birthday')

        if None in [username, password, email, birthday]:  # 確保所有欄位都已填寫
            flash('Please fill in all fields', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)  # 使用 Werkzeug 提供的方法來哈希密碼

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    query = "INSERT INTO members (username, password, email, birthday) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (username, hashed_password, email, birthday))
                    conn.commit()
            flash('Registration successful! Please log in.', 'success')
            # 註冊成功後，重定向到登錄頁面並附加 registered 參數
            return redirect(url_for('login', registered='True'))
        except mysql.connector.Error as e:
            flash(str(e), 'error')
            return render_template('register.html')
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']  # 使用電子郵件作為登錄憑證
        password = request.form['password']
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT password FROM members WHERE email = %s', (email,))  # 透過電子郵件來查找密碼
                account = cursor.fetchone()
        if account and check_password_hash(account[0], password):
            session['logged_in'] = True
            return redirect(url_for('homepage'))  # 登錄成功，重定向到主頁
        else:
            flash('Invalid email or password')  # 更改錯誤消息，明確指出是電子郵件或密碼錯誤
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@app.route('/homepage')
def homepage():
    if not session.get('logged_in'):
        flash('Please log in to view this page.', 'error')
        return redirect(url_for('login'))
    return render_template('homepage.html')

@app.route('/plans')
def plans():
    return render_template('plans.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')



@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
