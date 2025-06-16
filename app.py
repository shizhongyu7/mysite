from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>szy's site</title>
        <meta charset="utf-8">
        <style>
            body { font-family: sans-serif; background: #f0f0f0; text-align: center; padding: 5em; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>你好，这里是史钟毓的个人网站</h1>
        <p>欢迎访问！这个网站是用 Flask 搭建的。</p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)
