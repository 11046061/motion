from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify, send_from_directory
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wordcloud import WordCloud
from dotenv import load_dotenv  # 確保正確導入 load_dotenv

import os
import logging
import datetime
import openai
import openapi
import urllib.parse
import json

# 初始化 Flask 應用
app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

# 設置日誌
logging.basicConfig(level=logging.DEBUG)

# 加載環境變數
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 資料庫連接
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='figs0630',
        database='healthy'
    )

# 查詢與 AI 聊天
def get_open_ai_api_chat_response(member_id, prompt):
    if len(prompt) > 20:
        return "問題太長，請限制在20個字以內。"

    messages = [
        {"role": "system", "content": "You are an expert fitness and nutrition assistant. You only answer questions related to sports, exercise, fitness, and dietary advice. If the question is not related, please ask the user to ask a question about sports, exercise, or dietary advice."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        ai_answer = response.choices[0].message['content'].replace("\n", "<br>")

        # 儲存提問與回答到資料庫
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "INSERT INTO questions (member_id, question, answer, asked_at) VALUES (%s, %s, %s, NOW())"
                cursor.execute(query, (member_id, prompt, ai_answer))
                conn.commit()

        return ai_answer
    except Exception as e:
        logging.error(f"調用 OpenAI API 時出錯：{e}")
        return f"An error occurred: {str(e)}"

# 生成並保存個人文字雲到資料庫
def generate_wordcloud_and_save_to_db(member_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT question FROM questions WHERE member_id = %s"
                cursor.execute(query, (member_id,))
                questions = cursor.fetchall()

        if not questions:
            logging.info(f"用戶 {member_id} 尚未提問，無法生成文字雲")
            return None

        # 使用 OpenCC 進行繁體中文轉換
        cc = OpenCC('s2t')
        filtered_text = " ".join([cc.convert(item[0]) for item in questions])

        # 生成文字雲
        wordcloud = WordCloud(
            font_path='C:/Windows/Fonts/MSJH.TTC',
            width=800,
            height=400,
            background_color='white'
        ).generate(filtered_text)

        # 將圖片保存到內存中（不保存到文件系統）
        img_byte_arr = io.BytesIO()
        wordcloud.to_image().save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()  # 這是二進制圖片數據

        # 將圖片數據存儲到資料庫
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                insert_query = """
                    INSERT INTO user_wordclouds (user_id, wordcloud_image_data, updated_at)
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE
                    wordcloud_image_data = VALUES(wordcloud_image_data),
                    updated_at = NOW()
                """
                cursor.execute(insert_query, (member_id, img_byte_arr))
                conn.commit()

        logging.info(f"用戶 {member_id} 的文字雲已成功存儲到資料庫。")
        return True
    except Exception as e:
        logging.error(f"生成文字雲時出錯：{e}")
        return None

# 搜尋與提問路由
@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        member_id = data.get('member_id')
        prompt = data.get('prompt')

        if not member_id or not prompt:
            return jsonify({"error": "缺少必要的參數"}), 400

        response = get_open_ai_api_chat_response(member_id, prompt)
        return jsonify({"ai_answer": response})

    except Exception as e:
        logging.error(f"處理 '/ask' 路由請求時出現錯誤：{str(e)}")
        return jsonify({"error": "伺服器錯誤"}), 500


@app.route('/wordcloud/<int:user_id>')
def get_wordcloud(user_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT wordcloud_image_data FROM user_wordclouds WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        if result and result[0]:
            img_byte_arr = io.BytesIO(result[0])
            return send_file(img_byte_arr, mimetype='image/png')

        return "文字雲未找到", 404
    except mysql.connector.Error as err:
        logging.error(f"資料庫錯誤: {err}")
        return "伺服器錯誤", 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


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
                        flash('該電子郵件已經註冊過了，請使用不同的電子郵件', 'error')
                        return render_template('register.html')
                    
                    # 插入新會員紀錄
                    query = "INSERT INTO members (username, password, email, birthday) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (username, hashed_password, email, birthday))
                    conn.commit()
            flash('您的帳戶已經成功創建！請登入', 'success')
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
            flash('電子郵件或密碼錯誤')  # 更改錯誤消息，明確指出是電子郵件或密碼錯誤
            return render_template('login.html', error='電子郵件或密碼錯誤')
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



MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

#post
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_size_allowed(file):
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)  # 重置指標以便後續讀取
    return file_length <= MAX_FILE_SIZE

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
                if image and allowed_file(image.filename) and file_size_allowed(image):
                    image_filename = secure_filename(image.filename)
                    image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    image.save(image_path)
                    cursor.execute("""
                        INSERT INTO post_images (post_id, image_path)
                        VALUES (%s, %s)
                    """, (post_id, image_filename))
                else:
                    return jsonify({"status": "error", "message": "Image file not allowed or exceeds size limit"}), 400

        # 處理影片
        if 'videos' in request.files:
            videos = request.files.getlist('videos')
            for video in videos:
                if video and allowed_file(video.filename) and file_size_allowed(video):
                    video_filename = secure_filename(video.filename)
                    video_path = os.path.join(UPLOAD_FOLDER, video_filename)
                    video.save(video_path)
                    cursor.execute("""
                        INSERT INTO post_videos (post_id, video_path)
                        VALUES (%s, %s)
                    """, (post_id, video_filename))
                else:
                    return jsonify({"status": "error", "message": "Video file not allowed or exceeds size limit"}), 400

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"status": "success"})
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_posts', methods=['GET'])
def get_posts():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 獲取所有貼文及其創建者的用戶名
        cursor.execute("""
            SELECT posts.*, members.username FROM posts
            JOIN members ON posts.members_id = members.id
            ORDER BY posts.created_at DESC
        """)
        posts = cursor.fetchall()

        user_id = session.get('id')  # 獲取當前用戶的ID

        for post in posts:
            # 獲取貼文的圖片
            cursor.execute("SELECT * FROM post_images WHERE post_id = %s", (post['id'],))
            post['images'] = [url_for('static', filename=f'uploads/{img["image_path"]}') for img in cursor.fetchall()]

            # 獲取貼文的影片
            cursor.execute("SELECT * FROM post_videos WHERE post_id = %s", (post['id'],))
            post['videos'] = [url_for('static', filename=f'uploads/{vid["video_path"]}') for vid in cursor.fetchall()]

            # 確認當前用戶是否為貼文創建者，將此信息傳送到前端
            post['is_owner'] = post['members_id'] == user_id

            # 檢查當前用戶是否珍藏
            if user_id:
                cursor.execute("SELECT COUNT(*) FROM favorites WHERE post_id = %s AND members_id = %s", (post['id'], user_id))
                post['is_favorited'] = cursor.fetchone()['COUNT(*)'] > 0
            else:
                post['is_favorited'] = False

            # 獲取貼文的評論
            cursor.execute("""
                SELECT comments.*, members.username 
                FROM comments
                JOIN members ON comments.members_id = members.id
                WHERE post_id = %s
                ORDER BY comments.created_at ASC
            """, (post['id'],))
            comments = cursor.fetchall()

            # 處理每條評論
            for comment in comments:
                # 確認當前用戶是否能刪除該評論
                comment['deletable'] = comment['members_id'] == user_id

                # 獲取評論的按讚數
                cursor.execute("SELECT COUNT(*) AS likes_count FROM comment_likes WHERE comment_id = %s", (comment['id'],))
                like_result = cursor.fetchone()
                comment['likes'] = like_result['likes_count'] if like_result and 'likes_count' in like_result else 0

                # 確認當前用戶是否按讚過該評論
                if user_id:
                    cursor.execute("SELECT COUNT(*) AS liked FROM comment_likes WHERE comment_id = %s AND members_id = %s", (comment['id'], user_id))
                    user_liked_result = cursor.fetchone()
                    comment['user_liked'] = user_liked_result['liked'] > 0 if user_liked_result else False
                else:
                    comment['user_liked'] = False

            post['comments'] = comments

            # 確認當前用戶是否按讚過該貼文
            if user_id:
                cursor.execute("SELECT COUNT(*) AS liked FROM likes WHERE post_id = %s AND members_id = %s", (post['id'], user_id))
                post_liked_result = cursor.fetchone()
                post['user_liked'] = post_liked_result['liked'] > 0 if post_liked_result else False
            else:
                post['user_liked'] = False

        cursor.close()
        connection.close()

        return jsonify({'posts': posts})

    except Exception as e:
        return jsonify({'error': str(e)}), 500




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
    user_id = session.get('id')  # 獲取當前用戶的 ID

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # 檢查貼文是否屬於當前用戶
        cursor.execute("SELECT * FROM posts WHERE id = %s AND members_id = %s", (post_id, user_id))
        post = cursor.fetchone()

        if post:
            # 先刪除 favorites 中與該 post_id 相關的記錄
            cursor.execute("DELETE FROM favorites WHERE post_id = %s", (post_id,))
            
            # 先刪除與貼文相關的按讚記錄
            cursor.execute("DELETE FROM likes WHERE post_id = %s", (post_id,))
            
            # 再刪除與貼文相關的留言
            cursor.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))
            
            # 最後刪除貼文本身
            cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
            
            connection.commit()
            message = {'status': 'success', 'message': '貼文已成功刪除'}
        else:
            message = {'status': 'error', 'message': '無法刪除他人的貼文'}

    except Exception as e:
        connection.rollback()  # 發生錯誤時回滾操作
        message = {'status': 'error', 'message': f'刪除貼文時發生錯誤: {str(e)}'}

    finally:
        cursor.close()
        connection.close()

    return jsonify(message)

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    user_id = session.get('id')
    post_id = request.json.get('post_id')

    if not user_id or not post_id:
        return jsonify({"status": "error", "message": "缺少用戶或貼文資訊"}), 400

    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='figs0630',
        database='healthy'
    )
    cursor = conn.cursor()

    # 檢查是否已珍藏該貼文
    cursor.execute("SELECT id FROM favorites WHERE members_id = %s AND post_id = %s", (user_id, post_id))
    result = cursor.fetchone()

    if result:
        # 刪除珍藏
        cursor.execute("DELETE FROM favorites WHERE id = %s", (result[0],))
        conn.commit()
        response = {"status": "success", "action": "unfavorited"}
    else:
        # 新增珍藏
        cursor.execute("INSERT INTO favorites (members_id, post_id) VALUES (%s, %s)", (user_id, post_id))
        conn.commit()
        response = {"status": "success", "action": "favorited"}

    cursor.close()
    conn.close()
    return jsonify(response)


@app.route('/get_favorites', methods=['GET'])
def get_favorites():
    user_id = session.get('id')
    if not user_id:
        return jsonify({"status": "error", "message": "用戶未登入"}), 401

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 按珍藏時間排序的查詢語句
    cursor.execute("""
        SELECT posts.*, members.username, favorites.created_at AS favorited_time,
               (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count,
               (SELECT JSON_ARRAYAGG(image_path) FROM post_images WHERE post_images.post_id = posts.id) AS images,
               (SELECT JSON_ARRAYAGG(video_path) FROM post_videos WHERE post_videos.post_id = posts.id) AS videos,
               (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count
        FROM favorites
        JOIN posts ON favorites.post_id = posts.id
        JOIN members ON posts.members_id = members.id
        WHERE favorites.members_id = %s
        ORDER BY favorites.created_at DESC
    """, (user_id,))

    favorites = cursor.fetchall()

    for post in favorites:
        # 確保按讚數存在
        post['like_count'] = post.get('like_count', 0)
        post['comment_count'] = post.get('comment_count', 0)


        # 獲取貼文的圖片
        cursor.execute("SELECT * FROM post_images WHERE post_id = %s", (post['id'],))
        post['images'] = [
            url_for('static', filename=f'uploads/{img["image_path"]}') for img in cursor.fetchall()
        ]

        # 獲取貼文的影片
        cursor.execute("SELECT * FROM post_videos WHERE post_id = %s", (post['id'],))
        post['videos'] = [
            url_for('static', filename=f'uploads/{vid["video_path"]}') for vid in cursor.fetchall()
        ]


        # 查詢留言
        cursor.execute("""
            SELECT comments.*, members.username 
            FROM comments
            JOIN members ON comments.members_id = members.id
            WHERE comments.post_id = %s
            ORDER BY comments.created_at ASC
        """, (post['id'],))
        comments = cursor.fetchall()

        # 計算留言數
        post['comment_count'] = len(comments)

        # 格式化留言數據，若需要可傳遞給前端
        post['comments'] = [{
            "id": comment['id'],
            "username": comment['username'],
            "content": comment['content'],
            "created_at": comment['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
        } for comment in comments]

        # 確認是否已珍藏和按讚
        post['is_favorited'] = True
        cursor.execute("SELECT COUNT(*) AS liked FROM likes WHERE post_id = %s AND members_id = %s", (post['id'], user_id))
        post_liked_result = cursor.fetchone()
        post['user_liked'] = post_liked_result['liked'] > 0 if post_liked_result else False

    cursor.close()
    conn.close()

    return jsonify({"status": "success", "favorites": favorites})


def save_image(file):
    upload_folder = os.path.join('static', 'uploads', 'images')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return f'uploads/images/{filename}'


def generate_image_url(image):
    if not image.startswith('/static/images/'):
        return url_for('static', filename=f'images/{urllib.parse.quote(image)}')
    return image

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

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



@app.route('/delete_member', methods=['POST'])
def delete_member():
    user_id = session.get('id')
    if user_id:
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # 先刪除 likes 表中的相關記錄，包括該用戶的點贊
            cursor.execute('DELETE FROM likes WHERE post_id IN (SELECT id FROM posts WHERE members_id = %s) OR members_id = %s', (user_id, user_id))

            # 刪除 comments 表中的相關記錄
            cursor.execute('DELETE FROM comments WHERE members_id = %s', (user_id,))

            # 刪除 posts 表中的相關記錄
            cursor.execute('DELETE FROM posts WHERE members_id = %s', (user_id,))

            # 刪除 plans 表中的相關記錄
            cursor.execute('DELETE FROM plans WHERE user_id = %s', (user_id,))

            # 刪除 user_fitness_data 表中的相關記錄
            cursor.execute('DELETE FROM user_fitness_data WHERE user_id = %s', (user_id,))

            # 刪除 questions 表中的相關記錄
            cursor.execute('DELETE FROM questions WHERE member_id = %s', (user_id,))

            # 刪除 favorites 表中的相關記錄
            cursor.execute('DELETE FROM favorites WHERE members_id = %s', (user_id,))

            # 最後刪除會員本身
            cursor.execute('DELETE FROM members WHERE id = %s', (user_id,))
            connection.commit()

            # 清除 session，登出使用者
            session.clear()

            return redirect(url_for('login'))  # 刪除成功後重定向到登入頁面

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            connection.rollback()  # 如果有錯誤，回滾變更
            flash('刪除帳戶時出現錯誤，請稍後再試', 'error')  # 顯示錯誤提示
            return redirect(url_for('profile'))

        finally:
            cursor.close()
            connection.close()

    return redirect(url_for('profile'))






    
@app.route('/get-plan-status', methods=['GET'])
def get_plan_status():
    user_id = session.get('id')  # 從 session 中獲取使用者 ID
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    today_date = datetime.date.today()

    # 查詢 plans 表，檢查計畫是否已完成
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT completed FROM plans WHERE user_id = %s AND date = %s', (user_id, today_date))
    plan_status = cursor.fetchone()
    cursor.close()
    
    if plan_status and plan_status['completed']:
        return jsonify({'completed': True})
    else:
        return jsonify({'completed': False})




@app.route('/complete-plan', methods=['POST'])
def complete_plan():
    user_id = session.get('id')  # 從 session 中獲取使用者 ID
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    today_date = datetime.date.today()

    # 更新 plans 表，將計畫標記為已完成
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO plans (user_id, date, completed) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE completed = %s',
                   (user_id, today_date, True, True))
    connection.commit()
    cursor.close()

    return jsonify({'status': 'success'})


@app.route('/get-profile-data', methods=['GET'])
def get_profile_data():
    try:
        user_id = session.get('id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # 獲取身高（持久）和當天體重
        cursor.execute('SELECT height, weight_today FROM user_fitness_data WHERE user_id = %s ORDER BY date DESC LIMIT 1', (user_id,))
        profile_data = cursor.fetchone()
        cursor.close()

        if profile_data:
            return jsonify(profile_data)
        else:
            return jsonify({'error': 'No data found'}), 404
    except Exception as e:
        print(f"Error getting user profile data: {str(e)}")
        return jsonify({'error': 'Failed to get profile data'}), 500

@app.route('/update-profile', methods=['POST'])
def update_profile():
    try:
        user_id = session.get('id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401

        data = request.get_json()
        height = data.get('height')
        weight_today = data.get('weight_today')
        hip = data.get('hip')

        if not height or not weight_today or not waist or not hip:
            return jsonify({'error': 'Invalid data provided'}), 400

        # 計算腰臀比
        waist_hip_ratio = round(waist / hip, 2) if waist and hip else None

        connection = get_db_connection()
        cursor = connection.cursor()

        # 插入或更新用戶的資料
        cursor.execute('SELECT id FROM user_fitness_data WHERE user_id = %s AND date = CURDATE()', (user_id,))
        result = cursor.fetchone()

        if result:
            cursor.execute('''
                UPDATE user_fitness_data 
                SET weight_today = %s, height = %s, waist = %s, hip = %s, waist_hip_ratio = %s
                WHERE user_id = %s AND date = CURDATE()
            ''', (weight_today, height, waist, hip, waist_hip_ratio, user_id))
        else:
            cursor.execute('''
                INSERT INTO user_fitness_data (user_id, height, weight_today, waist, hip, waist_hip_ratio, date)
                VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
            ''', (user_id, height, weight_today, waist, hip, waist_hip_ratio))

        connection.commit()
        cursor.close()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update profile data'}), 500



@app.route('/get-weight-history', methods=['GET'])
def get_weight_history():
    try:
        user_id = session.get('id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT date, weight_today, waist_hip_ratio
            FROM user_fitness_data
            WHERE user_id = %s
            ORDER BY date ASC
        ''', (user_id,))
        data = cursor.fetchall()
        cursor.close()

        if not data:
            return jsonify({'error': 'No data found'}), 404

        dates = [row['date'].strftime('%Y-%m-%d') for row in data]
        weights = [row['weight_today'] for row in data]
        waist_hip_ratios = [row['waist_hip_ratio'] for row in data]

        return jsonify({'dates': dates, 'weights': weights, 'waist_hip_ratios': waist_hip_ratios})
    except Exception as e:
        logging.error(f'Error fetching weight history: {e}')
        return jsonify({'error': str(e)}), 500




@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # 清除 session
    return redirect(url_for('login'))  # 返回首頁


if __name__ == '__main__':
    app.run(debug=True)