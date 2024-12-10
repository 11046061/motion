import mysql.connector
from wordcloud import WordCloud
from openapi import get_open_ai_api_chat_response
import logging
import jieba
from opencc import OpenCC
from PIL import Image
import numpy as np
import os

# 設定 OpenCC 簡體轉繁體
cc = OpenCC('s2t')

# 設定日誌
logging.basicConfig(level=logging.INFO)

# 資料庫連接配置
db_config = {
    'user': 'root',
    'password': 'figs0630',
    'host': 'localhost',
    'database': 'healthy'
}

def get_db_connection():
    """建立資料庫連接"""
    return mysql.connector.connect(**db_config)

relevant_keywords = [
    "運動", "健身", "飲食", "營養", "健康", "深蹲", "跑步", "俯臥撐",
    "蛋白質", "卡路里", "減肥", "增肌", "瑜伽", "有氧", "無氧", "維生素"
]


def generate_wordcloud(member_id):
    """
    從資料庫提取回答並生成文字雲
    """
    try:
        # 提取回答資料
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT answer FROM questions WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        responses = cursor.fetchall()
        cursor.close()
        conn.close()

        if not responses:
            logging.warning(f"用戶 {member_id} 無可用數據生成文字雲。")
            return None, "無數據可生成文字雲。"

        # 合併回答文本並轉為繁體中文
        text = " ".join([resp[0] for resp in responses])
        text = cc.convert(text)

        # 分詞並篩選關鍵詞
        words = jieba.lcut(text)
        keywords = [word for word in words if word in relevant_keywords]

        if not keywords:
            return None, "無運動或飲食相關的關鍵詞生成文字雲。"

        # 生成文字雲
        wordcloud_dir = 'static/wordclouds'
        os.makedirs(wordcloud_dir, exist_ok=True)
        wordcloud_text = " ".join(keywords)
        wordcloud = WordCloud(
            font_path='C:/Windows/Fonts/MSJH.TTC',
            background_color='white',
            width=800,
            height=400
        ).generate(wordcloud_text)
        image_path = f'{wordcloud_dir}/user_{member_id}_wordcloud.png'
        wordcloud.to_file(image_path)

        # 提取文字雲關鍵詞
        keywords = list(wordcloud.words_.keys())
        logging.info(f"文字雲已成功生成並保存至 {image_path}")
        return image_path, keywords
    except Exception as e:
        logging.error(f"生成文字雲時發生錯誤: {e}")
        return None, "生成文字雲失敗"



def generate_wordcloud_and_ai_suggestions(member_id):
    """
    生成文字雲並傳送關鍵詞至 OpenAI 獲取建議
    """
    try:
        # 生成文字雲與關鍵詞
        image_path, keywords = generate_wordcloud(member_id)
        if not image_path:
            return None, "無法生成文字雲，請稍後再試。"

        # 將關鍵詞發送至 OpenAI 獲取建議
        ai_prompt = f"以下是用戶的文字雲關鍵詞：{'、'.join(keywords)}，請根據這些提供相關建議。"
        ai_suggestion = get_open_ai_api_chat_response(member_id, ai_prompt)

        return image_path, ai_suggestion
    except Exception as e:
        logging.error(f"生成文字雲或獲取 AI 建議失敗: {e}")
        return None, "伺服器發生錯誤，請稍後再試。"
