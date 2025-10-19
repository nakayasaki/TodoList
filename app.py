from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ユーザー管理
class User(UserMixin):
    # コンストラクタ
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

def get_user_by_name(username):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    return User(*row) if row else None

def get_user_by_id(user_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT id, username, password FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return User(*row) if row else None

#ユーザー情報を保持
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# ログイン画面
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # 初めはGETでForm送信後はPOST
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            error = "ユーザー名とパスワードを入力してください。"
        else:
            user = get_user_by_name(username)
            if user and user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                error = "ユーザー名またはパスワードが間違っています。"
    return render_template('login.html', error=error)

# 新規登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            error = "ユーザー名とパスワードを入力してください。"
        else:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "そのユーザー名はすでに使われています。"
            finally:
                conn.close()
    return render_template('register.html', error=error)

# メインページ
@app.route('/')
@login_required
def index():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM tasks WHERE user_id=?", (current_user.id,))
    tasks = cur.fetchall()
    conn.close()

    task_html = ""
    for task in tasks:
        task_html += f"""
        <li class="list-group-item d-flex justify-content-between align-items-center">
            {task[1]}
            <a href="/delete/{task[0]}" class="btn btn-danger btn-sm">削除</a>
        </li>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>{current_user.username} さんのToDoリスト</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h1 class="mb-4">{current_user.username} さんのToDoリスト</h1>

            <ul class="list-group mb-4">
                {task_html}
            </ul>

            <form method="POST" action="/add" class="d-flex gap-2">
                <input type="text" name="content" placeholder="新しいタスク" class="form-control">
                <input type="submit" value="追加" class="btn btn-primary">
            </form>

            <div class="mt-3">
                <a href="/logout" class="btn btn-secondary">ログアウト</a>
            </div>
        </div>
    </body>
    </html>
    """


# タスク追加
@app.route('/add', methods=['POST'])
@login_required
def add_task():
    content = request.form['content']
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (user_id, content) VALUES (?, ?)", (current_user.id, content))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# タスク削除
@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, current_user.id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
