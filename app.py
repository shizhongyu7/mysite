from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, abort, jsonify, make_response
)
import sqlite3, os, time
from datetime import datetime
from config import DB_PATH, SECRET_KEY, ADMIN_PASSWORD, RATE_LIMIT_SEC, COOKIE_MAX_AGE
from translations import translations

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ---------- 多语言 ----------
def get_t():
    lang = request.cookies.get('lang', 'zh')
    return translations.get(lang, translations['zh']), lang

# ---------- 数据库 ----------
def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn, open('init.sql') as f:
            conn.executescript(f.read())
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
init_db()

# ---------- 工具 ----------
def require_admin():
    if not session.get('is_admin'):
        abort(403)

# ---------- 主页 ----------
@app.route('/')
def index():
    t, lang = get_t()
    saved_username = request.cookies.get('username', '')

    with get_db() as db:
        rows = db.execute(
            "SELECT id, username, text, timestamp, reply FROM messages ORDER BY id DESC"
        ).fetchall()

    # 格式化时间
    messages = [
        (
            r['username'], r['text'],
            datetime.strptime(r['timestamp'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M"),
            r['reply']
        ) for r in rows
    ]

    return render_template('index.html', messages=messages,
                           t=t, lang=lang, saved_username=saved_username)

# ---------- 提交留言（同步 & AJAX 二合一） ----------
@app.route('/submit', methods=['POST'])
def submit():
    now, last = time.time(), session.get('last_submit', 0)
    if now - last < RATE_LIMIT_SEC:
        msg = "提交太频繁，请稍候再试" if request.cookies.get('lang') != 'en' else "Please wait before submitting again."
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': msg}), 429
        flash(msg)
        return redirect(url_for('index'))
    session['last_submit'] = now

    username = request.form.get('username', '').strip()
    text     = request.form.get('text', '').strip()
    if not (username and text):
        return redirect(url_for('index'))

    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with get_db() as db:
        db.execute("INSERT INTO messages (username, text, timestamp) VALUES (?,?,?)",
                   (username, text, ts))
        db.commit()

    # AJAX 请求 → 返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        response = jsonify({'username': username, 'text': text, 'timestamp': ts})
        response.set_cookie('username', username, max_age=COOKIE_MAX_AGE)
        return response

    # 普通请求 → 重定向
    resp = redirect(url_for('index'))
    resp.set_cookie('username', username, max_age=COOKIE_MAX_AGE)
    return resp

# ---------- 语言切换 ----------
@app.route('/lang/<code>')
def switch_lang(code):
    resp = redirect(request.referrer or url_for('index'))
    if code in translations:
        resp.set_cookie('lang', code, max_age=COOKIE_MAX_AGE)
    return resp

# ---------- 管理后台 ----------
@app.route('/admin')
def admin():
    if request.args.get('pw') == ADMIN_PASSWORD:
        session['is_admin'] = True
    require_admin()

    t, lang = get_t()
    with get_db() as db:
        rows = db.execute(
            "SELECT id, username, text, timestamp, reply FROM messages ORDER BY id DESC"
        ).fetchall()
    return render_template('admin.html', messages=rows, t=t, lang=lang)

@app.route('/delete/<int:mid>', methods=['POST'])
def delete(mid):
    require_admin()
    with get_db() as db:
        db.execute("DELETE FROM messages WHERE id=?", (mid,))
        db.commit()
    return redirect(url_for('admin'))

@app.route('/reply/<int:mid>', methods=['POST'])
def reply(mid):
    require_admin()
    reply_text = request.form.get('reply', '').strip()
    with get_db() as db:
        db.execute("UPDATE messages SET reply=? WHERE id=?", (reply_text, mid))
        db.commit()
    return redirect(url_for('admin'))

# ---------- 其它页面 ----------
@app.route('/nothing')
def nothing():
    t, lang = get_t()
    return render_template('nothing.html', t=t, lang=lang)

@app.route('/O_o')
def o_o():
    t, lang = get_t()
    return render_template('O_o.html', t=t, lang=lang)

# ---------- 错误处理 ----------
@app.errorhandler(404)
def not_found(e):
    t, lang = get_t()
    return render_template('404.html', t=t, lang=lang), 404

@app.errorhandler(403)
def forbidden(e):
    t, lang = get_t()
    return render_template('403.html', t=t, lang=lang), 403

# ---------- 网站配置 ----------
@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')

# ---------- 本地开发 ----------
if __name__ == '__main__':
    app.run(debug=True)