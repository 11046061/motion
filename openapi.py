import os
import openai
import opencc
from dotenv import load_dotenv
import mysql.connector



#api key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#轉換為繁體中文
converter = opencc.OpenCC('s2t')



#匯入ai的功能
def get_open_ai_api_chat_response(member_id, prompt):
    if len(prompt) > 20:
        return "問題太長，請限制在20個字以內。"

    messages = [
        {"role": "system", "content": "You are an expert fitness and nutrition assistant. You only answer questions related to sports, exercise, fitness, and dietary advice. If the question is not related, please ask the user to ask a question about sports, exercise, or dietary advice."},
        {"role": "assistant", "content": "你是一位健身助理"},
        {"role": "user", "content": prompt}
    ]

    try:
        # 发送 API 请求
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        # 处理返回的回答
        ai_answer = response.choices[0].message['content'].replace("\n", "<br>")
        
        # 儲存問題及回應至資料庫
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "INSERT INTO questions (member_id, question, answer) VALUES (%s, %s, %s)"
                cursor.execute(query, (member_id, prompt, ai_answer))
                conn.commit()
        
        return ai_answer
    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        port='3306',
        user='root',
        password='11046067',
        database='healthy'
    )
