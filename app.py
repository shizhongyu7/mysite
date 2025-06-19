from flask import Flask, render_template, request, redirect, url_for, make_response, flash, session, abort
import sqlite3, os
from datetime import datetime
import time



app = Flask(__name__)
app.secret_key = 'a-very-secret-key-1234567890'
DB_PATH = os.path.join(os.path.dirname(__file__), 'data/messages.db')
ADMIN_PASSWORD = "12345"

# 多语言词典
translations = {
    'zh': {
        'title': 'szy的网站',
        'home': '首页',
        'hi': '你好',
        'username': '你的名字',
        'placeholder': '写下你的留言...',
        'submit': '发送',
        'switch': 'English',
        'guestbook': '留言板',
        'nothing': '制作中',
    },
    'en': {
        'title': "My Site",
        'home': 'home',
        'hi': 'hi',
        'username': 'Your name',
        'placeholder': 'Leave your message...',
        'submit': 'Send',
        'switch': '中文',
        'guestbook': 'guestbook',
        'nothing': "nothing",
    }
}

# 初始化数据库
def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            with open('init.sql', 'r') as f:
                conn.executescript(f.read())

init_db()

def get_lang():
    lang = request.cookies.get('lang', 'zh')
    return 'en' if lang == 'en' else 'zh'

@app.route('/')
def index():
    t, lang = get_translations()
    saved_username = request.cookies.get('username', '')

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT username, text, timestamp FROM messages ORDER BY id DESC")
        rows = c.fetchall()

    messages = []
    for username, text, ts in rows:
        try:
            ts_fmt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
        except:
            ts_fmt = ts
        messages.append((username, text, ts_fmt))

    return render_template('index.html', messages=messages, t=t, lang=lang, saved_username=saved_username)

@app.route('/submit', methods=['POST'])
def submit():
    scrollY = request.form.get('scrollY', '0')

    now_ts = time.time()
    last_submit = session.get('last_submit', 0)

    # 限制频率
    if now_ts - last_submit < 10:
        lang = get_lang()
        flash("提交太频繁，请稍候再试" if lang == 'zh' else "Please wait before submitting again.")
        return redirect(url_for('index'))

    session['last_submit'] = now_ts

    username = request.form.get('username', '').strip()
    text = request.form.get('text', '').strip()
    lang = get_lang()

    resp = redirect(url_for('index'))

    if username and text:
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 本地时间字符串
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO messages (username, text, timestamp) VALUES (?, ?, ?)",
                      (username, text, now_str))
            conn.commit()
        resp.set_cookie('username', username, max_age=60 * 60 * 24 * 30)

    resp.set_cookie('last_submit_time', str(now_ts), max_age=3600)
    return resp

@app.route('/admin')
def admin():
    pw = request.args.get('pw')
    if pw != ADMIN_PASSWORD:
        abort(403)
    
    lang = get_lang()
    t = translations[lang]

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, text, timestamp FROM messages ORDER BY id DESC")
        rows = c.fetchall()

    return render_template('admin.html', messages=rows, t=t, lang=lang)

@app.route('/delete/<int:message_id>', methods=['POST'])
def delete(message_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM messages WHERE id=?", (message_id,))
        conn.commit()
    return redirect(url_for('admin'))

@app.route('/lang/<code>')
def switch_lang(code):
    resp = redirect(url_for('index'))
    if code in ['zh', 'en']:
        resp.set_cookie('lang', code, max_age=60 * 60 * 24 * 365)
    return resp

@app.route('/nothing')
def nothing():
    t, lang = get_translations()
    return render_template('nothing.html', t=t, lang=lang)

@app.route('/O_o')
def O_o():
    t, lang = get_translations()
    return render_template('O_o.html', t=t, lang=lang)

def get_translations():
    lang = get_lang()
    return translations[lang], lang

@app.errorhandler(404)
def page_not_found(e):
    t, lang = get_translations()
    return render_template('404.html', t=t, lang=lang), 404

@app.errorhandler(403)
def forbidden(e):
    t, lang = get_translations()
    return render_template('403.html', t=t, lang=lang), 403


if __name__ == '__main__':
    app.run(debug=True)