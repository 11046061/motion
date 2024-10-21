#完整版

import mysql.connector
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from opencc import OpenCC
from PIL import Image
import numpy as np
import imageio

# 設定資料庫連接
db_config = {
    'user': 'root',
    'password': 'figs0630',
    'host': 'localhost',
    'database': 'healthy'
}

# 建立資料庫連接
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

mask = np.array(Image.open("test2.jpg"))

# 定義與運動及飲食相關的關鍵詞
keywords = ['運動', '健身', '瑜伽', '跑步', '飲食', '營養', '蛋白質', '碳水化合物', '減肥', '握推', '深蹲']

# 從資料庫中提取數據
query = "SELECT answer FROM questions"
cursor.execute(query)
data = cursor.fetchall()

# 過濾只含有關鍵詞的回答
filtered_questions = [item[0] for item in data if any(kw in item[0] for kw in keywords)]

# 繁體中文轉換器
cc = OpenCC('s2t')

# 使用 jieba 進行中文分詞，並轉換為繁體中文
def chinese_tokenizer(text):
    text = cc.convert(text)
    return jieba.lcut(text)

# 使用 TF-IDF 提取特徵
tfidf_vectorizer = TfidfVectorizer(tokenizer=chinese_tokenizer, stop_words=['的', '是', '在', '有', '和', '了'])
tfidf_matrix = tfidf_vectorizer.fit_transform(filtered_questions)
feature_names = tfidf_vectorizer.get_feature_names_out()

# 從 TF-IDF 矩陣中選取最重要的詞彙
max_words = 100
sorted_words = sorted(zip(tfidf_vectorizer.idf_, feature_names), reverse=True)[:max_words]
filtered_text = " ".join([word for score, word in sorted_words])

# 生成文字雲，使用支持繁體中文的字體並應用舉重遮罩
wordcloud = WordCloud(
    font_path='C:/Windows/Fonts/MSJH.TTC',  # 確保字體支持繁體中文
    width=400,   # 調小寬度
    height=200,  # 調小高度
    margin=1,    # 減少邊框，默認為2，設置為1
    background_color='white',
    mask=imageio.imread('wilthe.jpg'),
    contour_color='black',  # 這樣可以讓邊界更清晰
    contour_width=1  # 調整邊界的寬度
).generate(filtered_text)

# 顯示文字雲並調整圖像顯示大小
plt.figure(figsize=(5, 2.5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # 隱藏軸線

# 調整圖像布局，減少白邊
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

# 保存圖片到文件，設置 dpi 控制圖片解析度
plt.savefig('wordcloud_image_small.png', format='png', dpi=150, bbox_inches='tight', pad_inches=0)
plt.show()

# 關閉資料庫連接
cursor.close()
conn.close()
