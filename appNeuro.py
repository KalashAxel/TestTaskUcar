# appNeuro.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
from transformers import pipeline  # Добавляем импорт для нейросети

app = Flask(__name__)
DATABASE = 'reviews.db'

# Загружаем модель при старте сервиса
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="blanchefort/rubert-tiny-sentiment"
)

def get_db():
    return sqlite3.connect(DATABASE)

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()

def analyze_sentiment(text):
    # Используем нейросеть вместо словарного подхода
    result = sentiment_analyzer(text)[0]
    
    # Конвертируем результат модели в наши категории
    label_map = {
        'POSITIVE': 'positive',
        'NEGATIVE': 'negative',
        'NEUTRAL': 'neutral'
    }
    return label_map.get(result['label'], 'neutral')

@app.route('/reviews', methods=['POST'])
def create_review():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Invalid data'}), 400
    
    text = data['text']
    sentiment = analyze_sentiment(text)
    created_at = datetime.utcnow().isoformat()
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)',
        (text, sentiment, created_at)
    )
    review_id = cursor.lastrowid
    conn.commit()
    
    review = {
        'id': review_id,
        'text': text,
        'sentiment': sentiment,
        'created_at': created_at
    }
    
    conn.close()
    return jsonify(review), 201

@app.route('/reviews', methods=['GET'])
def get_reviews():
    sentiment_filter = request.args.get('sentiment')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if sentiment_filter:
        cursor.execute('SELECT * FROM reviews WHERE sentiment = ?', (sentiment_filter,))
    else:
        cursor.execute('SELECT * FROM reviews')
    
    reviews = []
    for row in cursor.fetchall():
        reviews.append({
            'id': row[0],
            'text': row[1],
            'sentiment': row[2],
            'created_at': row[3]
        })
    
    conn.close()
    return jsonify(reviews)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)