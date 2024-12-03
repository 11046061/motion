import os
import openai
import opencc
from dotenv import load_dotenv
import mysql.connector
from wordcloud import WordCloud
import jieba
from flask import Flask, request, jsonify

app = Flask(__name__)

# 加載環境變數
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 繁體中文轉換器
converter = opencc.OpenCC('s2t')

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
        # 發送 API 請求
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        ai_answer = response.choices[0].message['content'].replace("\n", "<br>")
        ai_answer = converter.convert(ai_answer)

        # 儲存提問與回答到資料庫
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "INSERT INTO questions (member_id, question, answer) VALUES (%s, %s, %s)"
                cursor.execute(query, (member_id, prompt, ai_answer))
                conn.commit()

        return ai_answer
    except Exception as e:
        return f"An error occurred: {str(e)}"

# 生成個人文字雲
def generate_wordcloud(member_id):
    try:
        # 提取用戶的提問
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT question FROM questions WHERE member_id = %s"
                cursor.execute(query, (member_id,))
                questions = cursor.fetchall()

        # 合併問題文本
        text = " ".join([item[0] for item in questions])
        words = jieba.lcut(converter.convert(text))

        # 生成文字雲
        wordcloud = WordCloud(
            font_path='C:/Windows/Fonts/MSJH.TTC',
            background_color='white',
            width=800,
            height=400
        ).generate(" ".join(words))

        # 儲存圖片
        image_path = f"static/wordclouds/user_{member_id}_wordcloud.png"
        wordcloud.to_file(image_path)

        # 更新或插入到資料庫
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO user_wordclouds (user_id, wordcloud_image_path)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE wordcloud_image_path = %s
                """
                cursor.execute(query, (member_id, image_path, image_path))
                conn.commit()

        return image_path
    except Exception as e:
        return str(e)

@app.route('/get-wordcloud', methods=['POST'])
def get_wordcloud():
    try:
        data = request.json
        member_id = data.get('member_id')

        if not member_id:
            return jsonify({'error': '用戶 ID 缺失'}), 400

        # 生成文字雲
        image_path = generate_wordcloud(member_id)

        return jsonify({'wordcloud_path': image_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
