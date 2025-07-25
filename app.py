# app.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = 'reviews.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def analyze_sentiment(text):
    positive_words = ['хорош', 'отличн', 'прекрасн', 'любл', 'нравит', 'супер', 'класс']
    negative_words = ['плох', 'ужасн', 'ненавид', 'отвратительн', 'мерзк', 'кошмар']
    
    text_lower = text.lower()
    
    for word in positive_words:
        if word in text_lower:
            return 'positive'
    
    for word in negative_words:
        if word in text_lower:
            return 'negative'
    
    return 'neutral'

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