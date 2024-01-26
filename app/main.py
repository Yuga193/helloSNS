from flask import Flask, render_template, request, redirect, url_for, g, session, flash
import sqlite3
import re
app = Flask(__name__)
app.secret_key = 'your_secret_key' 

DATABASE = 'database.db'

def get_db(): #DBからデータを取得
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
        db.row_factory = sqlite3.Row
    return db

def jinja2_enumerate(iterable, start=0):
    return enumerate(iterable, start)
app.jinja_env.filters['enumerate'] = jinja2_enumerate

@app.route('/')#メイン画面。入ると同時にDBが存在しない場合はDBの作成
def main():
    db = get_db()
    db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                userID TEXT NOT NULL,
                password NOT NULL
            )
            ''')
    db.commit()

    db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                send_name TEXT,
                receiver_name TEXT,
                chat_session_id TEXT,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id),
                FOREIGN KEY (receiver_id) REFERENCES users(id)
            )
            ''')
    
    return render_template('test.html')

@app.route('/user')
def reg():
    return render_template('user.html')

@app.route('/com')
def com():
    db = get_db()
    cursor = db.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return render_template('completion.html', users=users)

@app.route('/completion', methods=['POST'])#会員登録画面
def register():
    name = request.form['name']
    userID = request.form['userID']
    password = request.form['password']

    # 入力チェック
    if not userID or not password or not name:
        flash("入力されていない箇所があります", "error")
        return redirect(url_for('reg'))

    # ユーザーIDが英数字のみかチェック
    if not re.match("^[a-zA-Z0-9]+$", userID):
        flash("ユーザーIDは半角英数字のみ使用可能です", "error")
        return redirect(url_for('reg'))

    # ユーザーIDの重複チェック
    db = get_db()
    cursor = db.execute('SELECT * FROM users WHERE userID = ?', (userID,))
    if cursor.fetchone():
        flash("そのユーザーIDは既に使用されています", "error")
        return redirect(url_for('reg'))

    # データベースへの挿入
    db.execute('INSERT INTO users (id, name, userID, password) VALUES(NULL, ?, ?, ?)',
                [name, userID, password])
    db.commit()

    return redirect(url_for('com'))


@app.route('/login', methods=['GET', 'POST'])#ログイン機能
def login():
    if request.method == 'POST':
        userID = request.form['userID']
        password = request.form['password']
        db = get_db()
        cursor = db.execute('SELECT * FROM users WHERE userID = ? AND password = ?', (userID, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['userID']
            return redirect(url_for('mypage'))
        else:
            flash('ユーザーIDもしくはパスワードが違います', 'error')

    return render_template('login.html')

@app.route('/mypage')#ユーザーIDからユーザー名を所得
def mypage():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    userID = session.get('user_id')
    db = get_db()
    cursor = db.execute('SELECT name FROM users WHERE userID = ?', (userID,))
    user = cursor.fetchone()

    if user:
        return render_template('mypage.html', name=user['name'])
    else:
        return "ユーザーが見つかりません"
    

@app.route('/search', methods=['POST'])#ユーザー検索機能
def search():
    search_term = request.form['search_term']
    db = get_db()
    cursor = db.execute('SELECT * FROM users WHERE userID = ?', (search_term,))
    user = cursor.fetchone()

    if user:
        return render_template('search.html', user=user)
    else:
        flash('ユーザーが見つかりませんでした', 'error')
        return redirect(url_for('mypage'))
    
@app.route('/logout')#ログアウト機能
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/send_message/<chat_session_id>', methods=['POST'])
def send_message(chat_session_id):

    # セッションから現在のchat_session_idを取得（URLパラメーターは無視）
    chat_session_id = session.get('chat_session_id')

    if not chat_session_id:
        flash('チャットセッションが見つかりません。')
        return redirect(url_for('mypage'))

    user_id_text = session.get('user_id')

    # データベースから現在のユーザー（送信者）の整数IDを取得
    db = get_db()
    sender = db.execute('SELECT id, name FROM users WHERE userID = ?', (user_id_text,)).fetchone()
    sender_id = sender['id']

    # chat_session_id から receiver_id を取得
    ids = [int(i) for i in chat_session_id.split('_')]
    receiver_id = min(ids) if sender_id == max(ids) else max(ids)

    # データベースから受信者の名前を取得
    receiver = db.execute('SELECT name FROM users WHERE id = ?', (receiver_id,)).fetchone()
    receiver_name = receiver['name']

    content = request.form['content']

    # データベースにメッセージを保存
    db.execute('''
        INSERT INTO messages (sender_id, receiver_id, send_name, receiver_name, content, chat_session_id) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (sender_id, receiver_id, sender['name'], receiver_name, content, chat_session_id))
    db.commit()

    return redirect(url_for('chat_page', chat_session_id=chat_session_id))



@app.route('/chat/<chat_session_id>')
def chat_page(chat_session_id):
    print("Chat Session ID:", chat_session_id)
    db = get_db()
    user_id_text = session.get('user_id')
    current_user = db.execute('SELECT id FROM users WHERE userID = ?', (user_id_text,)).fetchone()
    current_user_id = current_user['id']

    messages = db.execute('SELECT * FROM messages WHERE chat_session_id = ?', (chat_session_id,)).fetchall()

    # 他のユーザーの名前を取得（チャットセッションにメッセージが存在する場合のみ）
    other_user_name = None
    if messages:
        other_user_id = messages[0]['receiver_id'] if messages[0]['sender_id'] == current_user_id else messages[0]['sender_id']
        other_user_name = db.execute('SELECT name FROM users WHERE id = ?', (other_user_id,)).fetchone()['name']

    print(chat_session_id)

    return render_template('DM.html', messages=messages, other_user_name=other_user_name, current_user_id=current_user_id)

@app.route('/generate_chat_session/<searched_user_id>')
def generate_chat_session(searched_user_id):
    db = get_db()
    current_user_id_text = session.get('user_id')

    # 現在のユーザーと検索されたユーザーの整数IDを取得
    current_user = db.execute('SELECT id FROM users WHERE userID = ?', (current_user_id_text,)).fetchone()
    searched_user = db.execute('SELECT id FROM users WHERE userID = ?', (searched_user_id,)).fetchone()

    if not current_user or not searched_user:
        flash('ユーザーが見つかりません。')
        return redirect(url_for('mypage'))

    # チャットセッションIDを生成してセッションに保存
    chat_session_id = '{}_{}'.format(min(current_user['id'], searched_user['id']), max(current_user['id'], searched_user['id']))
    session['chat_session_id'] = chat_session_id

    return redirect(url_for('chat_page', chat_session_id=chat_session_id))


@app.route('/messages')
def messages():
    user_id_text = session.get('user_id')
    if not user_id_text:
        return redirect(url_for('login'))

    db = get_db()
    user = db.execute('SELECT id FROM users WHERE userID = ?', (user_id_text,)).fetchone()
    if not user:
        flash('ユーザーが見つかりません。')
        return redirect(url_for('login'))

    user_id = user['id']

    # 各チャットセッションの最終メッセージと相手の名前を取得
    message_list = db.execute('''
        SELECT M.chat_session_id, M.content, U.name as other_user_name
        FROM messages M
        JOIN users U ON U.id = CASE WHEN M.sender_id = ? THEN M.receiver_id ELSE M.sender_id END
        WHERE M.id IN (
            SELECT MAX(id) FROM messages WHERE sender_id = ? OR receiver_id = ? GROUP BY chat_session_id
        )
        ORDER BY M.timestamp DESC
    ''', (user_id, user_id, user_id)).fetchall()

    return render_template('message.html', messages=message_list)



if __name__ == '__main__':
    app.run()
