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
    edit_id = request.args.get('edit', '')  # 編集ボタンが押されたデータのIDを取得
    
    edit_log = None
    if edit_id:
        # 編集対象のデータを1件だけ取得してフォームに仕込む用
        edit_log = conn.execute('SELECT *, rowid FROM logs WHERE rowid = ?', (edit_id,)).fetchone()

    # 記録の「追加」または「更新」処理
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        title = request.form['title']
        theater = request.form['theater']
        seat = request.form['seat']
        handler = request.form['handler']
        memo = request.form['memo']
        current_edit_id = request.form.get('edit_id', '')

        if date and title:
            if current_edit_id:
                # 【新処理】edit_idがあれば「新しく追加」ではなく「既存の上書き修正」
                conn.execute(
                    """UPDATE logs SET 
                       date=?, time=?, title=?, theater=?, seat=?, handler=?, memo=? 
                       WHERE rowid=?""",
                    (date, time, title, theater, seat, handler, memo, current_edit_id)
                )
            else:
                # 通常の新規追加
                conn.execute(
                    'INSERT INTO logs (date, time, title, theater, seat, handler, memo) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    (date, time, title, theater, seat, handler, memo)
                )
            conn.commit()
            return redirect('/')

    # 検索・一覧表示処理
    if search_query:
        logs = conn.execute(
            """SELECT *, rowid FROM logs WHERE 
               title LIKE ? OR theater LIKE ? OR memo LIKE ? OR handler LIKE ? 
               ORDER BY date DESC""",
            (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        logs = conn.execute('SELECT *, rowid FROM logs ORDER BY date DESC').fetchall()
        
    conn.close()
    return render_template('index.html', logs=logs, search_query=search_query, edit_log=edit_log)

# データを削除するページ
@app.route('/delete/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM logs WHERE rowid = ?', (log_id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
