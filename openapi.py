import os
import openai
from opencc import OpenCC
from dotenv import load_dotenv
import mysql.connector
from wordcloud import WordCloud
import logging
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# 加載環境變數
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始化繁體中文轉換器
cc = OpenCC('s2t')

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
    """
    向 OpenAI 請求建議
    """
    if len(prompt) > 1000000000:  # 假設 OpenAI 請求的限制在 1000 字
        return "關鍵字數量過多，無法生成建議，請縮短文字雲內容。"

    messages = [
        {"role": "system", "content": "You are an expert fitness and nutrition assistant."},
        {"role": "user", "content": prompt}
    ]

    try:
        # 發送請求至 OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        ai_answer = response['choices'][0]['message']['content']
        # 將回答轉為繁體中文
        ai_answer_traditional = cc.convert(ai_answer)
        return ai_answer_traditional
    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API 請求失敗: {e}")
        return "AI 無法回應，請稍後再試。"
    except Exception as e:
        logging.error(f"未知錯誤: {e}")
        return "系統發生錯誤，請稍後再試。"


# 生成個人文字雲
def generate_wordcloud(member_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT answer FROM questions WHERE member_id = %s"
                cursor.execute(query, (member_id,))
                questions = cursor.fetchall()

        if not questions:
            logging.error(f"無法找到用戶 {member_id} 的數據生成文字雲。")
            return None

        # 合併數據並轉換
        text = " ".join([item[0] for item in questions])
        text = cc.convert(text)

        # 確保目錄存在
        wordcloud_dir = 'static/wordclouds'
        os.makedirs(wordcloud_dir, exist_ok=True)

        # 生成文字雲
        wordcloud = WordCloud(font_path='C:/Windows/Fonts/MSJH.TTC', background_color='white').generate(text)
        image_path = f'{wordcloud_dir}/user_{member_id}_wordcloud.png'
        wordcloud.to_file(image_path)

        return image_path
    except Exception as e:
        logging.error(f"生成文字雲失敗: {e}")
        return None


@app.route('/get-wordcloud', methods=['GET'])
def get_wordcloud():
    member_id = request.args.get('member_id')
    try:
        member_id = int(member_id)
    except (ValueError, TypeError):
        return jsonify({'error': '無效的 member_id'}), 400

    # 構造圖片路徑
    image_path = f'static/wordclouds/user_{member_id}_wordcloud.png'

    # 檢查文件是否存在
    if not os.path.exists(image_path):
        logging.error(f"文字雲文件未找到: {image_path}")
        return jsonify({'error': '文字雲未找到'}), 404

    # 返回圖片文件
    return send_file(image_path, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
