import os
import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# データベースの絶対パスを取得
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
            return redirect('/')

    # 検索処理
    if search_query:
        logs = conn.execute(
            """SELECT * FROM logs WHERE 
               title LIKE ? OR theater LIKE ? OR memo LIKE ? OR handler LIKE ? 
               ORDER BY date DESC""",
            (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        logs = conn.execute('SELECT *, rowid FROM logs ORDER BY date DESC').fetchall() # rowid(データの背番号)を取得
        
    conn.close()
    return render_template('index.html', logs=logs, search_query=search_query)

# 【新機能】データを削除する専用のページ（ルート）
@app.route('/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    conn = get_db_connection()
    # 指定された背番号（rowid）のデータを削除
    conn.execute('DELETE FROM logs WHERE rowid = ?', (log_id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
