import os
import sqlite3
from flask import Flask, render_template, request, redirect, send_file

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
        
    conn.close()
    return render_template('index.html', logs=logs, search_query=search_query)

# 【新機能】データベースファイルを丸ごとダウンロードするページ
@app.route('/download-db')
def download_db():
    if os.path.exists(DB_PATH):
        return send_file(
            DB_PATH,
            as_attachment=True,
            download_name='theater_log.db' # パソコンに保存される時のファイル名
        )
    return "データベースファイルが見つかりません。", 404

if __name__ == '__main__':
    app.run(debug=True)
