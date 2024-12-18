from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify, send_from_directory
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from wordcloud import WordCloud
from dotenv import load_dotenv  # 確保正確導入 load_dotenv
from opencc import OpenCC
from flask import send_file
from datetime import datetime
import opencc
from worcloudtest import generate_wordcloud_and_ai_suggestions
import logging
converter = opencc.OpenCC('s2t')
import io
import logging
import os
import openai
import urllib.parse
import jieba
import random
from PIL import Image

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
cc = OpenCC('s2t')  # 簡轉繁
from flask import send_file

# 生成文字雲
def generate_wordcloud(member_id):
    try:
        # 從資料庫提取回答
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT answer FROM questions WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        responses = cursor.fetchall()
        cursor.close()
        conn.close()

        if not responses:
            logging.warning(f"用戶 {member_id} 無可用數據生成文字雲。")
            return None

        # 合併回答文本並轉為繁體中文
        text = " ".join([resp[0] for resp in responses])
        text = cc.convert(text)

        # 生成文字雲
        wordcloud_dir = 'static/wordclouds'
        os.makedirs(wordcloud_dir, exist_ok=True)
        wordcloud = WordCloud(
            font_path='C:/Windows/Fonts/MSJH.TTC',
            background_color='white',
            width=800,
            height=400
        ).generate(text)
        image_path = f'{wordcloud_dir}/user_{member_id}_wordcloud.png'
        wordcloud.to_file(image_path)

        return image_path
    except Exception as e:
        logging.error(f"生成文字雲失敗: {e}")
        return None

# 呼叫 OpenAI API 並儲存回答
def get_open_ai_api_chat_response(member_id, prompt):
    messages = [
        {"role": "system", "content": "You are an expert fitness and nutrition assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        # 呼叫 OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        ai_answer = response['choices'][0]['message']['content']
        ai_answer_traditional = cc.convert(ai_answer)

        # 保存提問與回答到資料庫
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO questions (member_id, question, answer, asked_at) VALUES (%s, %s, %s, NOW())"
        cursor.execute(query, (member_id, prompt, ai_answer_traditional))
        conn.commit()
        cursor.close()
        conn.close()

        # 更新文字雲
        generate_wordcloud(member_id)

        return ai_answer_traditional
    except Exception as e:
        logging.error(f"OpenAI API 呼叫失敗: {e}")
        return "系統發生錯誤，請稍後再試。"

@app.route('/search', methods=['GET'])
def search():
    member_id = session.get('id')
    if not member_id:
        return redirect(url_for('login'))

    # 頁面加載時生成文字雲
    generate_wordcloud(member_id)

    # 獲取歷史記錄
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT question, answer, asked_at FROM questions WHERE member_id = %s ORDER BY asked_at DESC"
    cursor.execute(query, (member_id,))
    history = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('search.html', history=history, user_id=member_id)

@app.route('/generate-wordcloud/<int:member_id>', methods=['GET'])
def generate_wordcloud_api(member_id):
    """
    調用文字雲與 AI 建議的生成功能
    """
    try:
        wordcloud_path, ai_suggestion = generate_wordcloud_and_ai_suggestions(member_id)
        if not wordcloud_path:
            return jsonify({'error': ai_suggestion}), 500
        return jsonify({'wordcloud_path': wordcloud_path, 'ai_suggestion': ai_suggestion})
    except Exception as e:
        logging.error(f"生成文字雲或 AI 建議時發生錯誤: {e}")
        return jsonify({'error': '伺服器發生錯誤，請稍後再試。'}), 500


@app.route('/get-wordcloud', methods=['GET'])
def get_wordcloud():
    member_id = request.args.get('member_id', type=int)
    if not member_id:
        return jsonify({"error": "Member ID is missing"}), 400
    try:
        wordcloud_path = f'static/wordclouds/user_{member_id}_wordcloud.png'
        if not os.path.exists(wordcloud_path):
            return jsonify({"error": "文字雲未找到"}), 404
        return send_file(wordcloud_path, mimetype='image/png')
    except Exception as e:
        logging.error(f"無法生成文字雲: {e}")
        return jsonify({"error": "無法獲取文字雲"}), 500

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
    member_id = session.get('id')  # 檢查用戶是否登入
    if not member_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing prompt"}), 400

    prompt = data['prompt']
    try:
        ai_answer = get_open_ai_api_chat_response(member_id, prompt)
        return jsonify({"ai_answer": ai_answer}), 200
    except Exception as e:
        logging.error(f"Error in ask route: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/example')
def example():
    current_time = datetime.now()
    return render_template('example.html', time=current_time)


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
    
    # 左側廣告清單
    left_ads = [
        {"title": "啞鈴廣告", "image": "images/健身啞鈴廣告.jpg", "link": "https://24h.pchome.com.tw/prod/DEBYLG-A900GPLSF"},
        {"title": "健身環", "image": "images/健身環廣告.jpg", "link": "https://24h.pchome.com.tw/prod/DEBY2C-A900BFHXT"},
        {"title": "滑輪繩", "image": "images/滑輪繩.png", "link": "https://www.inhandsports.com/products/diy--pulley-tricep-rope?gad_source=1&gclid=EAIaIQobChMIkImZx9ueigMV79EWBR23jSL6EAYYCCABEgL9C_D_BwE&variation=60ec17e8bf4fbc5484f490e7"}

    ]

    # 右側廣告清單
    right_ads = [
        {"title": "瑜珈墊廣告", "image": "images/健身瑜珈墊廣告.png", "link": "https://m.momoshop.com.tw/goods.momo?i_code=12221717"},
        {"title": "蛋白粉廣告", "image": "images/蛋白粉廣告.png", "link": "https://shopee.tw/%F0%9F%94%A5%E6%B0%B8%E4%B9%85%E5%85%8D%E9%81%8B-ON-%E9%87%91%E7%89%8C-5%E7%A3%85-%E4%B9%B3%E6%B8%85-%E8%9B%8B%E7%99%BD-%E9%80%81%E6%90%96%E6%90%96%E6%9D%AF-%E4%BD%8E%E7%86%B1%E9%87%8F-%E5%81%A5%E8%BA%AB-%E9%81%8B%E5%8B%95-%E7%87%9F%E9%A4%8A%E5%93%81-%E7%87%9F%E9%A4%8A%E8%A3%9C%E7%B5%A6-%E9%87%8D%E9%87%8F%E8%A8%93%E7%B7%B4-%E8%9B%8B%E7%99%BD%E7%B2%89-%E9%AB%98%E8%9B%8B%E7%99%BD-i.2381542.852279997?sp_atk=f4bb633d-2542-474e-8fc5-ccabfcf8ba5a&xptdk=f4bb633d-2542-474e-8fc5-ccabfcf8ba5a"},
        {"title": "雞胸肉廣告", "image": "images/健身雞胸肉.png", "link": "https://www.itsonion.com.tw/products/%E6%96%B0%E6%89%8B%E5%93%81%E5%9A%90%E7%B5%84"}

    ]

    # 隨機選擇廣告
    selected_left_ad = random.choice(left_ads)
    selected_right_ad = random.choice(right_ads)
    
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
    return render_template('homepage.html', left_ads=[selected_left_ad], right_ads=[selected_right_ad])



MAX_IMAGE_SIZE = 25 * 1024 * 1024  # 25MB for images
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB for videos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    """檢查檔案副檔名是否允許"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file_size_allowed(file, file_type):
    """根據檔案類型檢查檔案大小"""
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)  # 重置檔案指標
    if file_type == 'image':
        return file_length <= MAX_IMAGE_SIZE
    elif file_type == 'video':
        return file_length <= MAX_VIDEO_SIZE
    return False

def process_file(file, file_type, post_id, cursor):
    """統一處理圖片或影片的儲存與檢查"""
    if not allowed_file(file.filename):
        logging.warning(f"{file_type.capitalize()} '{file.filename}' 被拒絕，原因：檔案類型不允許")
        return {"status": "error", "message": f"{file_type.capitalize()} file type not allowed"}
    if not file_size_allowed(file, file_type):
        size_limit = MAX_IMAGE_SIZE if file_type == 'image' else MAX_VIDEO_SIZE
        logging.warning(f"{file_type.capitalize()} '{file.filename}' 被拒絕，原因：檔案大小超過 {size_limit / (1024 * 1024)}MB")
        return {"status": "error", "message": f"{file_type.capitalize()} file size exceeds {size_limit / (1024 * 1024)}MB"}

    try:
        file_filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, file_filename)
        file.save(file_path)
        
        # 插入資料庫
        if file_type == 'image':
            cursor.execute("""
                INSERT INTO post_images (post_id, image_path)
                VALUES (%s, %s)
            """, (post_id, file_filename))
        elif file_type == 'video':
            cursor.execute("""
                INSERT INTO post_videos (post_id, video_path)
                VALUES (%s, %s)
            """, (post_id, file_filename))
    except Exception as e:
        logging.error(f"儲存 {file_type} '{file.filename}' 發生錯誤: {e}")
        return {"status": "error", "message": f"Failed to save {file_type.capitalize()}"}

    return {"status": "success"}

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
                result = process_file(image, 'image', post_id, cursor)
                if result["status"] == "error":
                    connection.rollback()  # 若失敗則回滾
                    return jsonify(result), 400

        # 處理影片
        if 'videos' in request.files:
            videos = request.files.getlist('videos')
            for video in videos:
                result = process_file(video, 'video', post_id, cursor)
                if result["status"] == "error":
                    connection.rollback()  # 若失敗則回滾
                    return jsonify(result), 400

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




from datetime import datetime, date  # 確保導入正確的日期模組


@app.route('/get-plan-status', methods=['GET'])
def get_plan_status():
    try:
        user_id = session.get('id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401

        today_date = datetime.now().date()

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查詢今日的計畫完成狀態
        cursor.execute("""
            SELECT completed
            FROM plans
            WHERE user_id = %s AND date = %s
        """, (user_id, today_date))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        # 返回完成狀態，預設為 False
        return jsonify({'completed': bool(result['completed']) if result else False})
    except Exception as e:
        app.logger.error(f"Error in /get-plan-status: {e}")
        return jsonify({'error': 'Unable to fetch plan status.'}), 500











@app.route('/complete-plan', methods=['POST'])
def complete_plan():
    try:
        user_id = session.get('id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401

        today_date = datetime.now().date()

        connection = get_db_connection()
        cursor = connection.cursor()

        # 確保資料庫更新完成狀態
        cursor.execute("""
            INSERT INTO plans (user_id, date, completed)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE completed = VALUES(completed)
        """, (user_id, today_date, True))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'status': 'success'})
    except Exception as e:
        app.logger.error(f"Error in /complete-plan: {e}")
        return jsonify({'error': 'Unable to mark plan as complete.'}), 500




import openai

openai.api_key="sk-1qb4-OeziAth5JwGh-uDp_rnnUArW0f30wQcAVDSAHT3BlbkFJ8RXkphamEGGrXhVNHGKU9KGD8Dmd0KldyM3Qrfw4gA"
print("使用的 API Key:", openai.api_key)  # 測試是否正確設置

@app.route('/get-profile-data', methods=['GET'])
def get_profile_data():
    try:
        user_id = session.get('id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 獲取最近一筆數據，不限於當天
        cursor.execute('''
            SELECT height, weight_today, waist, hip, waist_hip_ratio, DATE(date) as record_date
            FROM user_fitness_data
            WHERE user_id = %s
            ORDER BY date DESC
            LIMIT 1
        ''', (user_id,))
        profile_data = cursor.fetchone()

        cursor.close()
        connection.close()

        # 若無數據，返回空值
        if not profile_data:
            profile_data = {
                "height": None,
                "weight_today": None,
                "waist": None,
                "hip": None,
                "waist_hip_ratio": None,
                "record_date": None,
            }

        return jsonify(profile_data)
    except Exception as e:
        app.logger.error(f"Error in get-profile-data: {e}")
        return jsonify({'error': 'Server error occurred'}), 500














@app.route('/update-profile', methods=['POST'])
def update_profile():
    user_id = session.get('id')
    if not user_id:
        return jsonify({'success': False, 'error': '用戶未登入'}), 401

    data = request.get_json()
    height = data.get('height')
    weight_today = data.get('weight_today')
    waist = data.get('waist')
    hip = data.get('hip')

    try:
        # 計算腰臀比
        waist_hip_ratio = round(waist / hip, 2) if waist and hip and hip != 0 else None

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 刪除當日所有舊記錄
        cursor.execute("""
            DELETE FROM user_fitness_data
            WHERE user_id = %s AND date = CURDATE()
        """, (user_id,))

        # 插入新記錄
        cursor.execute("""
            INSERT INTO user_fitness_data (user_id, height, weight_today, waist, hip, waist_hip_ratio, date)
            VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
        """, (user_id, height, weight_today, waist, hip, waist_hip_ratio))

        connection.commit()
        cursor.close()

        return jsonify({
            'success': True,
            'data': {
                'height': height,
                'weight_today': weight_today,
                'waist': waist,
                'hip': hip,
                'waist_hip_ratio': waist_hip_ratio
            }
        })
    except Exception as e:
        app.logger.error(f"Error in update-profile: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500














    
@app.route('/get-exercise-data', methods=['GET'])
def get_exercise_data():
    user_id = session.get('id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
        SELECT exercise, SUM(reps) as total_reps
        FROM user_exercises
        WHERE user_id = %s
        GROUP BY exercise
    ''', (user_id,))
    data = cursor.fetchall()
    cursor.close()

    exercises = [row['exercise'] for row in data]
    reps = [row['total_reps'] for row in data]

    return jsonify({'exercises': exercises, 'reps': reps})

@app.route('/get-exercise-stats', methods=['GET'])
def get_exercise_stats():
    user_id = session.get('id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT DATE_FORMAT(date, "%Y-%m-%d") AS date, exercise_name, SUM(sets * reps) AS total_reps
            FROM user_exercises
            WHERE user_id = %s
            GROUP BY date, exercise_name
        ''', (user_id,))
        stats = cursor.fetchall()
        cursor.close()
        # 若無數據，返回預設格式
        if not stats:
            return jsonify({
                'stats': [],
                'labels': ['無記錄'],
                'datasets': [{
                    'label': '卡路里消耗',
                    'data': [0],
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'tension': 0.4
                }]
            })
        return jsonify({'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500






        
@app.route('/add-exercise', methods=['POST'])
def add_exercise():
    try:
        # 驗證用戶是否已登入
        user_id = session.get('id')
        if not user_id:
            return jsonify({'error': 'User not logged in'}), 401

        # 接收前端數據
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request, no data provided'}), 400

        exercise_name = data.get('exercise_name')
        sets = data.get('sets')
        reps = data.get('reps')
        calories = data.get('calories')  # 從前端接收卡路里數據

        if not all([exercise_name, sets, reps, calories]):
            return jsonify({'error': 'Missing required fields'}), 400

        # 插入到數據庫
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO user_exercises (user_id, exercise_name, sets, reps, calories, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        today_date = datetime.now().date()  # 獲取當天日期
        cursor.execute(query, (user_id, exercise_name, sets, reps, calories, today_date))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"status": "success", "message": "Exercise added successfully"}), 200
    except Exception as e:
        logging.error(f"新增動作時發生錯誤: {e}")
        return jsonify({"status": "error", "message": "伺服器內部錯誤"}), 500




@app.route('/get-daily-calorie-summary', methods=['GET'])
def get_daily_calorie_summary():
    try:
        user_id = session.get('id')
        if not user_id:
            return jsonify({"dates": [], "calories": []}), 200

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT DATE(date) AS date, SUM(calories) AS total_calories
            FROM user_exercises
            WHERE user_id = %s
            GROUP BY DATE(date)
            ORDER BY DATE(date) ASC
        """
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()

        dates = [row['date'].strftime('%Y-%m-%d') for row in results] if results else []
        calories = [row['total_calories'] for row in results] if results else []

        cursor.close()
        connection.close()

        # 返回空數據時的預設值
        if not results:
            return jsonify({"dates": [], "calories": []}), 200

        return jsonify({"dates": dates, "calories": calories}), 200
    except Exception as e:
        logging.error(f"獲取每日卡路里數據失敗: {e}")
        return jsonify({"error": "伺服器內部錯誤"}), 500












    
@app.route('/get-today-exercises', methods=['GET'])
def get_today_exercises():
    user_id = session.get('id')  # 確保用戶已登入
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 獲取用戶數據
        cursor.execute("""
            SELECT height, weight_today, waist, hip, waist_hip_ratio
            FROM user_fitness_data
            WHERE user_id = %s AND DATE(date) = CURDATE()
            ORDER BY date DESC
            LIMIT 1
        """, (user_id,))
        user_data = cursor.fetchone()


        if not user_data or not all([user_data['height'], user_data['weight_today'], user_data['waist'], user_data['hip']]):
            return jsonify({'error': '今日數據未完整輸入'}), 400

        # 計算 BMI 和腰臀比
        height = user_data['height']
        weight = user_data['weight_today']
        waist = user_data['waist']
        hip = user_data['hip']

        bmi = weight / ((height / 100) ** 2)
        whr = waist / hip

        # 確定體型
        if bmi < 18.5 and whr < 0.9:
            body_type = 'thin'
        elif 18.5 <= bmi <= 25 and whr < 0.9:
            body_type = 'average'
        else:
            body_type = 'overweight'

        # 日期轉換成中文格式
        day_of_week_map = {
            'Monday': '星期一',
            'Tuesday': '星期二',
            'Wednesday': '星期三',
            'Thursday': '星期四',
            'Friday': '星期五',
            'Saturday': '星期六',
            'Sunday': '星期日'
        }
        day_of_week = day_of_week_map[datetime.now().strftime('%A')]

        # 構造健身計劃
        fitness_plans = {
    'thin': {
        '星期一': [
            {'exercise': '俯臥撐', 'image': '俯臥撐.png', 'video': '登山跑.mp4'},
            {'exercise': '仰臥起坐', 'image': '仰臥起坐.png', 'video': '臀橋.mp4'},
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '深蹲.mp4'}
        ],
        '星期二': [
            {'exercise': '深蹲', 'image': '深蹲.png', 'video': '深蹲.mp4'},
            {'exercise': '跳躍深蹲', 'image': '跳躍深蹲.png', 'video': '跳躍深蹲.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'}
        ],
        '星期三': [
            {'exercise': '平板支撐', 'image': '平板支撐.png', 'video': '平板支撐.mp4'},
            {'exercise': '高抬腿', 'image': '高抬腿.png', 'video': '登山跑.mp4'},
            {'exercise': '仰臥自行車', 'image': '仰臥自行車.png', 'video': '深蹲.mp4'}
        ],
        '星期四': [
            {'exercise': '弓步蹲', 'image': '弓箭步.png', 'video': '登山跑.mp4'},
            {'exercise': '單腳硬拉', 'image': '單腳硬拉.png', 'video': '波比跳.mp4'},
            {'exercise': '跳躍深蹲', 'image': '跳躍深蹲.png', 'video': '跳躍深蹲.mp4'}
        ],
        '星期五': [
            {'exercise': '波比跳', 'image': '波比跳.png', 'video': '波比跳.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'},
            {'exercise': '跳躍深蹲', 'image': '跳躍深蹲.png', 'video': '跳躍深蹲.mp4'}
        ],
        '星期六': [
            {'exercise': '開合跳', 'image': '開合跳.png', 'video': '登山跑.mp4'},
            {'exercise': '仰臥腿舉', 'image': '仰臥腿舉.png', 'video': '深蹲.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'}
        ],
        '星期日': [
            {'exercise': '休息日：放鬆並進行輕度伸展', 'image': None, 'video': None}
        ]
    },
    'average': {
        '星期一': [
            {'exercise': '凳上臂屈伸', 'image': '凳上臂屈伸.png', 'video': '登山跑.mp4'},
            {'exercise': '俯臥撐', 'image': '俯臥撐.png', 'video': '登山跑.mp4'},
            {'exercise': '跳繩', 'image': '跳繩.png', 'video': '登山跑.mp4'}
        ],
        '星期二': [
            {'exercise': '波比跳', 'image': '波比跳.png', 'video': '波比跳.mp4'},
            {'exercise': '俯臥撐', 'image': '俯臥撐.png', 'video': '俯臥撐.mp4'},
            {'exercise': '凳上臂屈伸', 'image': '凳上臂屈伸.png', 'video': '凳上臂屈伸.mp4'}
        ],
        '星期三': [
            {'exercise': '高抬腿', 'image': '高抬腿.png', 'video': '登山跑.mp4'},
            {'exercise': '深蹲', 'image': '深蹲.png', 'video': '登山跑.mp4'},
            {'exercise': '俯臥撐', 'image': '俯臥撐.png', 'video': '登山跑.mp4'}
        ],
        '星期四': [
            {'exercise': '俯臥撐', 'image': '俯臥撐.png', 'video': '登山跑.mp4'},
            {'exercise': '凳上臂屈伸', 'image': '凳上臂屈伸.png', 'video': '登山跑.mp4'},
            {'exercise': '仰臥自行車', 'image': '仰臥自行車.png', 'video': '登山跑.mp4'}
        ],
        '星期五': [
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '俯臥撐', 'image': '俯臥撐.png', 'video': '俯臥撐.mp4'},
            {'exercise': '平板支撐', 'image': '平板支撐.png', 'video': '平板支撐.mp4'}
        ],
        '星期六': [
            {'exercise': '高抬腿', 'image': '高抬腿.png', 'video': '登山跑.mp4'},
            {'exercise': '開合跳', 'image': '開合跳.png', 'video': '登山跑.mp4'},
            {'exercise': '肩膀挺舉', 'image': '肩膀挺舉.png', 'video': '登山跑.mp4'}
        ],
        '星期日': [
            {'exercise': '休息日：放鬆並進行輕度伸展', 'image': None, 'video': None}
        ]
    },
    'overweight': {
        '星期一': [
            {'exercise': '步行', 'image': '步行.png', 'video': '深蹲.mp4'},
            {'exercise': '牽拉運動', 'image': '牽拉運動.png', 'video': '俯臥撐.mp4'},
            {'exercise': '高抬腿', 'image': '高抬腿.png', 'video': '平板支撐.mp4'}
        ],
        '星期二': [
            {'exercise': '靠牆深蹲', 'image': '深蹲.png', 'video': '深蹲.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'},
            {'exercise': '波比跳', 'image': '波比跳.png', 'video': '波比跳.mp4'}
        ],
        '星期三': [
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '深蹲', 'image': '深蹲.png', 'video': '登山跑.mp4'},
            {'exercise': '側步蹲', 'image': '側步蹲.png', 'video': '登山跑.mp4'}
        ],
        '星期四': [
            {'exercise': '跪姿俯臥撐', 'image': '俯臥撐.png', 'video': '俯臥撐.mp4'},
            {'exercise': '平板支撐', 'image': '平板支撐.png', 'video': '平板支撐.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'}
        ],
        '星期五': [
            {'exercise': '深蹲', 'image': '深蹲.png', 'video': '深蹲.mp4'},
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '開合跳', 'image': '開合跳.png', 'video': '開合跳.mp4'}
        ],
        '星期六': [
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '跳繩', 'image': '跳繩.png', 'video': '登山跑.mp4'},
            {'exercise': '側棒式支撐', 'image': '側棒式支撐.png', 'video': '登山跑.mp4'}
        ],
        '星期日': [
            {'exercise': '休息日：放鬆並進行輕度伸展', 'image': None, 'video': None}
        ]
    },
    'thin_high_whr': {
        '星期一': [
            {'exercise': '步行', 'image': '步行.png', 'video': '深蹲.mp4'},
            {'exercise': '牽拉運動', 'image': '牽拉運動.png', 'video': '俯臥撐.mp4'},
            {'exercise': '高抬腿', 'image': '高抬腿.png', 'video': '平板支撐.mp4'}
        ],
        '星期二': [
            {'exercise': '靠牆深蹲', 'image': '深蹲.png', 'video': '深蹲.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'},
            {'exercise': '波比跳', 'image': '波比跳.png', 'video': '波比跳.mp4'}
        ],
        '星期三': [
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '波比跳.mp4'},
            {'exercise': '深蹲', 'image': '深蹲.png', 'video': '波比跳.mp4'},
            {'exercise': '側步蹲', 'image': '側步蹲.png', 'video': '波比跳.mp4'}
        ],
        '星期四': [
            {'exercise': '跪姿俯臥撐', 'image': '俯臥撐.png', 'video': '俯臥撐.mp4'},
            {'exercise': '平板支撐', 'image': '平板支撐.png', 'video': '平板支撐.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'}
        ],
        '星期五': [
            {'exercise': '深蹲', 'image': '深蹲.png', 'video': '深蹲.mp4'},
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '開合跳', 'image': '開合跳.png', 'video': '開合跳.mp4'}
        ],
        '星期六': [
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '跳繩', 'image': '跳繩.png', 'video': '登山跑.mp4'},
            {'exercise': '側棒式支撐', 'image': '側棒式支撐.png', 'video': '登山跑.mp4'}
        ],
        '星期日': [
            {'exercise': '休息日：放鬆並進行輕度伸展', 'image': None, 'video': None}
        ]
    },
    'average_high_whr': {
        '星期一': [
            {'exercise': '步行', 'image': '步行.png', 'video': '深蹲.mp4'},
            {'exercise': '牽拉運動', 'image': '牽拉運動.png', 'video': '俯臥撐.mp4'},
            {'exercise': '高抬腿', 'image': '高抬腿.png', 'video': '平板支撐.mp4'}
        ],
        '星期二': [
            {'exercise': '靠牆深蹲', 'image': '深蹲.png', 'video': '深蹲.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'},
            {'exercise': '波比跳', 'image': '波比跳.png', 'video': '波比跳.mp4'}
        ],
        '星期三': [
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '深蹲', 'image': '深蹲.png', 'video': '登山跑.mp4'},
            {'exercise': '側步蹲', 'image': '側步蹲.png', 'video': '登山跑.mp4'}
        ],
        '星期四': [
            {'exercise': '跪姿俯臥撐', 'image': '俯臥撐.png', 'video': '俯臥撐.mp4'},
            {'exercise': '平板支撐', 'image': '平板支撐.png', 'video': '平板支撐.mp4'},
            {'exercise': '臀橋', 'image': '臀橋.png', 'video': '臀橋.mp4'}
        ],
        '星期五': [
            {'exercise': '深蹲', 'image': '深蹲.png', 'video': '深蹲.mp4'},
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '開合跳', 'image': '開合跳.png', 'video': '開合跳.mp4'}
        ],
        '星期六': [
            {'exercise': '登山跑', 'image': '登山跑.png', 'video': '登山跑.mp4'},
            {'exercise': '跳繩', 'image': '跳繩.png', 'video': '登山跑.mp4'},
            {'exercise': '側棒式支撐', 'image': '側棒式支撐.png', 'video': '登山跑.mp4'}
        ],
        '星期日': [
            {'exercise': '休息日：放鬆並進行輕度伸展', 'image': None, 'video': None}
        ]
    }
}


        today_plan = fitness_plans.get(body_type, {}).get(day_of_week)
        if not today_plan:
            return jsonify({'error': '未找到相應的健身計畫'}), 404

        return jsonify({'bodyType': body_type, 'dayOfWeek': day_of_week, 'exercises': today_plan})
    except Exception as e:
        logging.error(f"Error fetching today's exercises: {e}")
        return jsonify({'error': str(e)}), 500






@app.route('/get-exercises', methods=['GET'])
def get_exercises():
    user_id = session.get('id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    today_date = datetime.now().date()  # 獲取當天日期
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查詢當日動作
        cursor.execute('''
            SELECT id, exercise_name, sets, reps
            FROM user_exercises
            WHERE user_id = %s AND date = %s
        ''', (user_id, today_date))
        exercises = cursor.fetchall()

        # 動作名稱對應表
        exercise_translation = {
            "pushup": "伏地挺身",
            "squat": "深蹲",
            "plank": "平板支撐",
            "jump_squat": "跳躍深蹲",
            "burpee": "波比跳",
            # 添加更多動作翻譯
        }

        # 將英文名稱轉換為中文
        for exercise in exercises:
            exercise['exercise_name'] = exercise_translation.get(exercise['exercise_name'], exercise['exercise_name'])

        cursor.close()
        connection.close()

        return jsonify({'exercises': exercises})
    except Exception as e:
        app.logger.error(f"Error in /get-exercises: {e}")
        return jsonify({'error': 'Internal server error'}), 500



@app.route('/complete-exercises', methods=['POST'])
def complete_exercises():
    user_id = session.get('id')
    if not user_id:
        return jsonify({'success': False, 'error': 'User not logged in'}), 401

    today_date = datetime.date.today()
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 標記當天的動作為已完成
        cursor.execute('''
            UPDATE user_exercises
            SET completed = TRUE
            WHERE user_id = %s AND date = %s
        ''', (user_id, today_date))

        # 查詢圖表所需的總數據
        cursor.execute('''
            SELECT exercise_name AS name, SUM(sets * reps) AS total_reps
            FROM user_exercises
            WHERE user_id = %s AND completed = TRUE
            GROUP BY exercise_name
        ''', (user_id,))
        chart_data = cursor.fetchall()

        connection.commit()

        return jsonify({'success': True, 'chartData': chart_data})
    except Exception as e:
        logging.error(f"Error in /complete-exercises: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def get_random_color():
    return f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.6)"


@app.route('/query-exercises', methods=['POST'])
def query_exercises():
    user_id = session.get('id')
    date = request.json.get('date')

    if not user_id or not date:
        return jsonify({'error': 'Missing user_id or date'}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # 查詢指定日期的動作數據
        cursor.execute('''
            SELECT date, exercise_name, SUM(sets) AS total_sets, SUM(reps) AS total_reps
            FROM user_exercises
            WHERE user_id = %s AND date = %s
            GROUP BY exercise_name
        ''', (user_id, date))
        exercises = cursor.fetchall()

        # 確保即使 `completed = 0` 的記錄也會顯示
        if not exercises:  # 如果沒有找到任何數據，檢查是否有當日數據
            cursor.execute('''
                SELECT exercise_name, sets, reps
                FROM user_exercises
                WHERE user_id = %s AND date = %s
            ''', (user_id, date))
            exercises = cursor.fetchall()

        # 整理圖表數據
        cursor.execute('''
            SELECT date, exercise_name, SUM(sets * reps) AS total_reps
            FROM user_exercises
            WHERE user_id = %s
            GROUP BY date, exercise_name
            ORDER BY date ASC
        ''', (user_id,))
        chart_data = cursor.fetchall()

        grouped_data = {}
        for row in chart_data:
            date_str = row['date'].strftime('%Y-%m-%d')
            if date_str not in grouped_data:
                grouped_data[date_str] = {}
            grouped_data[date_str][row['exercise_name']] = row['total_reps']

        labels = sorted(grouped_data.keys())
        datasets = [
            {
                'label': exercise,
                'data': [grouped_data[date].get(exercise, 0) for date in labels],
                'borderColor': get_random_color(),
                'fill': False,
            }
            for exercise in {row['exercise_name'] for row in chart_data}
        ]

        return jsonify({
            'labels': labels,
            'datasets': datasets,
            'exercises': exercises
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

















@app.route('/delete-exercise/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    user_id = session.get('id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM user_exercises WHERE id = %s AND user_id = %s', (exercise_id, user_id))
        exercise = cursor.fetchone()

        if exercise:
            cursor.execute('DELETE FROM user_exercises WHERE id = %s', (exercise_id,))
            connection.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Exercise not found or not authorized'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/get-weight-history', methods=['GET'])
def get_weight_history():
    user_id = session.get('id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 查詢每日最新數據
        cursor.execute('''
            SELECT DATE(date) as date, weight_today as weight, waist_hip_ratio
            FROM user_fitness_data
            WHERE user_id = %s
            ORDER BY DATE(date) ASC, date DESC
        ''', (user_id,))
        records = {}
        for row in cursor.fetchall():
            records[row['date']] = row  # 只保留每日最新記錄

        cursor.close()

        dates = list(records.keys())
        weights = [records[date]['weight'] for date in dates]
        waist_hip_ratios = [records[date]['waist_hip_ratio'] for date in dates]

        return jsonify({'dates': dates, 'weights': weights, 'waist_hip_ratios': waist_hip_ratios})
    except Exception as e:
        return jsonify({'error': str(e)}), 500






@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # 清除 session
    return redirect(url_for('login'))  # 返回首頁


if __name__ == '__main__':
    app.run(debug=True)