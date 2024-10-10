from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import logging
import datetime
import openai
import openapi

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # 保護密碼

logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='figs0630',
        database='healthy'
    )
    return connection

# 確保uploads目錄存在
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
                cursor.execute('SELECT id,username, password, email, birthday FROM members WHERE email = %s', (email,))  # 透過電子郵件來查找密碼
                account = cursor.fetchone()
        if account and check_password_hash(account[2], password):
            session['logged_in'] = True
            session['id'] = account[0]  # 确保在登录时会话中存储了用户ID
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
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT posts.*, members.username FROM posts
        JOIN members ON posts.members_id = members.id
        ORDER BY posts.created_at DESC  # 按時間倒序排序
    """)
    posts = cursor.fetchall()
    # ...其餘代碼保持不變...

    for post in posts:
        cursor.execute("""
            SELECT comments.*, members.username FROM comments
            JOIN members ON comments.members_id = members.id
            WHERE post_id = %s
        """, (post['id'],))
        post['comments'] = cursor.fetchall()
        cursor.execute("""
            SELECT COUNT(*) FROM likes WHERE post_id = %s
        """, (post['id'],))
        post['likes'] = cursor.fetchone()['COUNT(*)']
        cursor.execute("""
            SELECT COUNT(*) FROM likes WHERE post_id = %s AND members_id = %s
        """, (post['id'], session.get('id')))
        post['isLiked'] = cursor.fetchone()['COUNT(*)'] > 0

    cursor.close()
    connection.close()
    return render_template('homepage.html', posts=posts)

#post
@app.route('/add_post', methods=['POST'])
def add_post():
    try:
        content = request.form.get('content')
        members_id = session.get('id')  # 確保用戶已登入

        if not members_id:
            return jsonify({"status": "error", "message": "User not logged in"}), 401

        connection = get_db_connection()
        cursor = connection.cursor()

        # 插入貼文內容
        cursor.execute("""
            INSERT INTO posts (members_id, content)
            VALUES (%s, %s)
        """, (members_id, content))
        post_id = cursor.lastrowid

        # 處理圖片
        if 'images' in request.files:
            images = request.files.getlist('images')
            for image in images:
                if image and allowed_file(image.filename):
                    image_filename = secure_filename(image.filename)
                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    image.save(image_path)
                    cursor.execute("""
                        INSERT INTO post_images (post_id, image_path)
                        VALUES (%s, %s)
                    """, (post_id, image_filename))

        # 處理影片
        if 'videos' in request.files:
            videos = request.files.getlist('videos')
            for video in videos:
                if video and allowed_file(video.filename):
                    video_filename = secure_filename(video.filename)
                    video_path = os.path.join(UPLOAD_FOLDER, video_filename)
                    video.save(video_path)
                    cursor.execute("""
                        INSERT INTO post_videos (post_id, video_path)
                        VALUES (%s, %s)
                    """, (post_id, video_filename))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"status": "success"})
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return jsonify({"status": "error", "message": str(e)}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get_posts', methods=['GET'])
def get_posts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT posts.*, members.username FROM posts
        JOIN members ON posts.members_id = members.id
        ORDER BY posts.created_at DESC
    """)
    posts = cursor.fetchall()

    for post in posts:
        cursor.execute("SELECT * FROM post_images WHERE post_id = %s", (post['id'],))
        post['images'] = [url_for('static', filename=f'uploads/{img["image_path"]}') for img in cursor.fetchall()]

        cursor.execute("SELECT * FROM post_videos WHERE post_id = %s", (post['id'],))
        post['videos'] = [url_for('static', filename=f'uploads/{vid["video_path"]}') for vid in cursor.fetchall()]

        cursor.execute("""
            SELECT comments.*, members.username 
            FROM comments
            JOIN members ON comments.members_id = members.id
            WHERE post_id = %s
            ORDER BY comments.created_at ASC
        """, (post['id'],))
        comments = cursor.fetchall()

        for comment in comments:
            comment['deletable'] = comment['members_id'] == session.get('id')

            # 加強防錯邏輯以避免 None 和 KeyError 問題
            try:
                cursor.execute("SELECT COUNT(*) AS likes_count FROM comment_likes WHERE comment_id = %s", (comment['id'],))
                like_result = cursor.fetchone()

                # 使用安全檢查來避免 KeyError
                if like_result is not None and 'likes_count' in like_result:
                    comment['likes'] = like_result['likes_count']
                else:
                    comment['likes'] = 0

            except Exception as e:
                print(f"Error fetching likes for comment {comment['id']}: {e}")
                comment['likes'] = 0

            if session.get('id'):
                cursor.execute("SELECT COUNT(*) AS liked FROM comment_likes WHERE comment_id = %s AND members_id = %s", (comment['id'], session.get('id')))
                user_liked_result = cursor.fetchone()
                comment['user_liked'] = user_liked_result['liked'] > 0 if user_liked_result else False
            else:
                comment['user_liked'] = False

        post['comments'] = comments

    cursor.close()
    connection.close()
    return jsonify({'posts': posts})

@app.route('/get_post_images/<int:post_id>')
def get_post_images(post_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT image_path FROM post_images WHERE post_id = %s", (post_id,))
    images = cursor.fetchall()
    image_urls = [url_for('static', filename=f'uploads/{img["image_path"]}') for img in images]
    cursor.close()
    connection.close()
    return jsonify({'images': image_urls})

@app.route('/get_post_videos/<int:post_id>')
def get_post_videos(post_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT video_path FROM post_videos WHERE post_id = %s", (post_id,))
    videos = cursor.fetchall()
    video_urls = [url_for('static', filename=f'uploads/{vid["video_path"]}') for vid in videos]
    cursor.close()
    connection.close()
    return jsonify({'videos': video_urls})

@app.route('/add_comment', methods=['POST'])
def add_comment():
    data = request.json
    post_id = data.get('post_id')
    content = data.get('content').strip()
    member_id = session.get('id')
    parent_comment_id = data.get('parent_comment_id')  # 新增這個欄位來接收父留言的ID
    
    # 檢查留言內容是否為空
    if not content:
        return jsonify({"status": "error", "message": "留言內容不能為空"})

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # 檢查該用戶在該貼文下是否有重複的留言
    cursor.execute("""
        SELECT * FROM comments 
        WHERE post_id = %s AND members_id = %s AND content = %s AND parent_comment_id = %s
    """, (post_id, member_id, content, parent_comment_id))
    existing_comment = cursor.fetchone()

    # 如果找到相同的留言，返回錯誤
    if existing_comment:
        return jsonify({"status": "error", "message": "重複的留言"})

    # 插入新留言
    cursor.execute("""
        INSERT INTO comments (post_id, members_id, content, parent_comment_id) 
        VALUES (%s, %s, %s, %s)
    """, (post_id, member_id, content, parent_comment_id))
    connection.commit()
    comment_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({"status": "success", "comment_id": comment_id, "username": session.get('username')})

@app.route('/delete_comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    members_id = session.get('id')

    connection = get_db_connection()
    cursor = connection.cursor()

    # 確認是否是該用戶自己的留言
    cursor.execute("SELECT members_id FROM comments WHERE id = %s", (comment_id,))
    comment = cursor.fetchone()

    if comment and comment[0] == members_id:
        # 刪除回覆（如果有回覆）
        cursor.execute("DELETE FROM comments WHERE parent_comment_id = %s", (comment_id,))

        # 刪除主留言
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"status": "success"})
    else:
        cursor.close()
        connection.close()
        return jsonify({"status": "error", "message": "You cannot delete this comment"}), 403

    
@app.route('/get_comment_count/<int:post_id>', methods=['GET'])
def get_comment_count(post_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # 計算該貼文的留言數，包括回覆
    cursor.execute("""
        SELECT COUNT(*) FROM comments WHERE post_id = %s
    """, (post_id,))
    count = cursor.fetchone()[0]
    
    cursor.close()
    connection.close()

    return jsonify({'count': count})


@app.route('/like_post', methods=['POST'])
def like_post():
    post_id = request.json.get('post_id')
    members_id = session.get('id')

    connection = get_db_connection()
    cursor = connection.cursor()

    # 先檢查這個用戶是否已經對這個帖子按讚
    cursor.execute("SELECT * FROM likes WHERE post_id = %s AND members_id = %s", (post_id, members_id))
    if cursor.fetchone():
        cursor.execute("DELETE FROM likes WHERE post_id = %s AND members_id = %s", (post_id, members_id))
    else:
        cursor.execute("INSERT INTO likes (post_id, members_id) VALUES (%s, %s)", (post_id, members_id))

    connection.commit()

    # 確保按讚數為正確數值
    cursor.execute("SELECT COUNT(*) FROM likes WHERE post_id = %s", (post_id,))
    likes_count = cursor.fetchone()[0] or 0  # 如果為 None 設置為 0

    cursor.execute("UPDATE posts SET likes = %s WHERE id = %s", (likes_count, post_id))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"status": "success", "likes": likes_count})

@app.route('/unlike_post', methods=['POST'])
def unlike_post():
    post_id = request.json.get('post_id')
    members_id = session.get('id')

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM likes WHERE post_id = %s AND members_id = %s", (post_id, members_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"status": "success"})

@app.route('/like_comment', methods=['POST'])
def like_comment():
    comment_id = request.json.get('comment_id')
    members_id = session.get('id')

    if not members_id:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # 檢查該用戶是否已經對這個留言按讚
        cursor.execute("SELECT * FROM comment_likes WHERE comment_id = %s AND members_id = %s", (comment_id, members_id))
        result = cursor.fetchone()

        if result:
            # 如果已經按讚，則刪除該按讚
            cursor.execute("DELETE FROM comment_likes WHERE comment_id = %s AND members_id = %s", (comment_id, members_id))
            user_liked = False  # 用戶取消了按讚
        else:
            # 如果尚未按讚，則插入按讚數據
            cursor.execute("INSERT INTO comment_likes (comment_id, members_id) VALUES (%s, %s)", (comment_id, members_id))
            user_liked = True  # 用戶點擊了按讚

        connection.commit()

        # 查詢更新後的按讚總數
        cursor.execute("SELECT COUNT(*) FROM comment_likes WHERE comment_id = %s", (comment_id,))
        likes_count = cursor.fetchone()[0]

        return jsonify({
            "status": "success", 
            "likes": likes_count,
            "user_liked": user_liked  # 返回用戶是否已按讚的狀態
        })

    except mysql.connector.Error as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    finally:
        cursor.close()
        connection.close()

@app.route('/delete_post/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM likes WHERE post_id = %s", (post_id,))
        cursor.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))
        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"status": "success"})
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)}), 500

def format_time(time):
    now = datetime.datetime.now()
    time_diff = now - time
    if time_diff.days > 0:
        return f"{time_diff.days}天前"
    elif time_diff.seconds >= 3600:
        return f"{time_diff.seconds // 3600}小時前"
    elif time_diff.seconds >= 60:
        return f"{time_diff.seconds // 60}分鐘前"
    else:
        return "剛剛"


@app.route('/plans')
def plans():
    return render_template('plans.html')

#搜尋
@app.route('/search', methods=['POST', 'GET'])
def search():
    member_id = session.get('id')
    
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "No prompt provided"}), 400

        prompt = data['prompt']
        try:
            ai_answer = openapi.get_open_ai_api_chat_response(member_id, prompt)
            # 移除答案中的所有 <br> 標籤
            cleaned_answer = ai_answer.replace('<br>', ' ')
            return jsonify({'ai_answer': cleaned_answer})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # 如果是 GET 請求，載入歷史記錄
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT question, answer, asked_at FROM questions WHERE member_id = %s ORDER BY asked_at DESC"
                cursor.execute(query, (member_id,))
                history_data = cursor.fetchall()
                 # 移除歷史記錄中答案的 <br> 標籤
                cleaned_history = [(q, a.replace('<br>', ' '), at) for q, a, at in history_data]
                
        return render_template('search.html', history=cleaned_history)
    except mysql.connector.Error as e:
        flash(str(e), 'error')
        return redirect(url_for('homepage'))

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