import mysql.connector
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from opencc import OpenCC

# 設定資料庫連接
db_config = {
    'user': 'root',
    'password': '11046067',
    'host': 'localhost',
    'database': 'healthy'
}

# 建立資料庫連接
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# 定義與運動及飲食相關的關鍵詞
keywords = ['運動', '健身', '瑜伽', '跑步', '飲食', '營養', '蛋白質', '碳水化合物', '減肥','握推','深蹲']

# 從資料庫中提取數據
query = "SELECT question FROM questions"
cursor.execute(query)
data = cursor.fetchall()

# 過濾只含有關鍵詞的問題
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

# 生成文字雲，使用支持繁體中文的字體
wordcloud = WordCloud(font_path='C:/Windows/Fonts/MSJH.TTC', width=800, height=400, background_color='white').generate(filtered_text)

# 顯示文字雲
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()

# 關閉資料庫連接
cursor.close()
conn.close()
