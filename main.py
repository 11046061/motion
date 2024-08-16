from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os
import openai
import openapi

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

 #新增會員
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        birthday = request.form.get('birthday')

        if None in [username, password, email, birthday]:  # 确保所有字段都已填寫
            flash('Please fill in all fields', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)  # 使用 Werkzeug 提供的方法加密密碼

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # 檢查電子郵件是否已存在
                    cursor.execute("SELECT COUNT(*) FROM members WHERE email = %s", (email,))
                    if cursor.fetchone()[0] > 0:
                        flash('Email already registered, please use a different email.', 'error')
                        return render_template('register.html')
                    
                    # 插入新會員紀錄
                    query = "INSERT INTO members (username, password, email, birthday) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (username, hashed_password, email, birthday))
                    conn.commit()
            flash('Registration successful! Please log in.', 'success')
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
                cursor.execute('SELECT id, username, password, email, birthday FROM members WHERE email = %s', (email,))  # 透過電子郵件來查找密碼
                account = cursor.fetchone()
        if account and check_password_hash(account[2], password):
            session['logged_in'] = True
            session['user_id'] = account[0]  # 儲存 user_id 到 session
            session['username'] = account[1]
            session['email'] = account[3]
            session['birthday'] = account[4]
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

#搜尋
@app.route('/search', methods=['POST', 'GET'])
def search():
    member_id = session.get('user_id')
    
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "No prompt provided"}), 400

        prompt = data['prompt']
        try:
            ai_answer = openapi.get_open_ai_api_chat_response(member_id, prompt)
            return jsonify({'ai_answer': ai_answer})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # 如果是 GET 請求，載入歷史記錄
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT question, answer, asked_at FROM questions WHERE member_id = %s ORDER BY asked_at DESC"
                cursor.execute(query, (member_id,))
                history_data = cursor.fetchall()
                
        return render_template('search.html', history=history_data)
    except mysql.connector.Error as e:
        flash(str(e), 'error')
        return redirect(url_for('homepage'))
#個人
@app.route('/profile')
def profile():
    if not session.get('logged_in'):
        flash('Please log in to view your profile.', 'error')
        return redirect(url_for('login'))

    # 獲取用户信息
    user_info = {
        'username': session.get('username'),
        'email': session.get('email'),
        'birthday': session.get('birthday')
    }

    return render_template('profile.html', **user_info)
#刪除會員資料
@app.route('/delete_member', methods=['POST'])
def delete_member():
    if not session.get('logged_in'):
        flash('You need to log in to delete your account.', 'error')
        return redirect(url_for('login'))

    email = session.get('email')
    if email:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    query = "DELETE FROM members WHERE email = %s"
                    cursor.execute(query, (email,))
                    conn.commit()
            # 清除 session 中所有資料
            session.clear()
            flash('Your account has been deleted.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as e:
            flash(str(e), 'error')
            return redirect(url_for('profile'))
    else:
        flash('Unable to find your account information.', 'error')
        return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('birthday', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
