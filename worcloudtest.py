import mysql.connector
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from opencc import OpenCC
import io
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)

# 資料庫連接配置
db_config = {
    'user': 'root',
    'password': 'figs0630',
    'host': 'localhost',
    'database': 'healthy'
}

def generate_wordcloud_and_save_to_db(member_id):
    try:
        # 建立資料庫連接
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 從資料庫中提取相關的問答數據
        query = "SELECT answer FROM questions WHERE member_id = %s"
        cursor.execute(query, (member_id,))
        data = cursor.fetchall()

        if not data:
            logging.info(f"用戶 {member_id} 尚未有問題記錄，無法生成文字雲。")
            return None

        # 使用 OpenCC 進行繁體中文轉換
        cc = OpenCC('s2t')

        # 生成文字雲的文本
        filtered_text = " ".join([cc.convert(item[0]) for item in data])

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

    except mysql.connector.Error as err:
        logging.error(f"資料庫錯誤：{err}")
    except Exception as e:
        logging.error(f"生成文字雲時出錯：{e}")
    finally:
        # 確保資料庫連接被正確關閉
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 生成並保存文字雲
member_id = 1  # 這裡根據需要更改用戶 ID
generate_wordcloud_and_save_to_db(member_id)
