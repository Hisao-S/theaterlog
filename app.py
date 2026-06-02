import os
import sqlite3
from flask import Flask, render_template, request, redirect, send_file, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'theater_log.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    search_query = request.args.get('search', '')
    
    # 記録の追加処理
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        title = request.form['title']
        theater = request.form['theater']
        seat = request.form['seat']
        handler = request.form['handler']
        memo = request.form['memo']
        
        if date and title:
            conn.execute(
                'INSERT INTO logs (date, time, title, theater, seat, handler, memo) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (date, time, title, theater, seat, handler, memo)
            )
            conn.commit()
        conn.close()
        return redirect('/')

    # データ一覧の取得
    if search_query:
        logs = conn.execute(
            """SELECT date, time, title, theater, seat, handler, memo FROM logs WHERE 
               title LIKE ? OR theater LIKE ? OR memo LIKE ? OR handler LIKE ? 
               ORDER BY date DESC""",
            (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        logs = conn.execute('SELECT date, time, title, theater, seat, handler, memo FROM logs ORDER BY date DESC').fetchall()
        
    # 📊 【新処理】グラフ用の集計データを取得
    # 1. 年ごとの観劇本数（日付の先頭4文字を「年」としてグループ化）
    yearly_data = conn.execute(
        "SELECT SUBSTR(date, 1, 4) as year, COUNT(*) as count FROM logs WHERE date IS NOT NULL AND date != '' GROUP BY year ORDER BY year ASC"
    ).fetchall()
    
    # 2. 出演者回数ランキング トップ5（空欄やカンマ区切りの簡易集計。部分一致ではなく全体一致ベース）
    actor_data = conn.execute(
        "SELECT handler, COUNT(*) as count FROM logs WHERE handler IS NOT NULL AND handler != '' GROUP BY handler ORDER BY count DESC LIMIT 5"
    ).fetchall()

    conn.close()
    
    # HTML側に集計したデータを辞書の形で引き渡す
    stats = {
        'years': [row['year'] for row in yearly_data],
        'year_counts': [row['count'] for row in yearly_data],
        'actors': [row['handler'] for row in actor_data],
        'actor_counts': [row['count'] for row in actor_data]
    }
    
    return render_template('index.html', logs=logs, search_query=search_query, stats=stats)

@app.route('/download-db')
def download_db():
    if os.path.exists(DB_PATH):
        return send_file(DB_PATH, as_attachment=True, download_name='theater_log.db')
    return "データベースファイルが見つかりません。", 404

if __name__ == '__main__':
    app.run(debug=True)
