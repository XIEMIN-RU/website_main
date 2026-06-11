# Sets up the routes for all the pages

from flask import Flask, render_template, request, make_response
from flask_caching import Cache
from config import TEMPLATES_PATH, TEXT_PATH
from application.helpers import *
import os
from flask import request, jsonify
from openai import OpenAI
# 初始化 OpenAI 客戶端 (會自動讀取環境變數 OPENAI_API_KEY)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))



app = Flask(__name__, template_folder=TEMPLATES_PATH)
app.jinja_env.filters["is_active"] = is_active
app.jinja_env.filters["get_language_image"] = get_language_image

app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = 3600
cache = Cache(app)


@app.route("/")
def loading():
    """Renders the 'Loading' page of the website."""

    #response = make_response(render_template("loading.html"))
    #response.headers["Cache-Control"] = "public, max-age=3"

    #return response
    return render_template("home.html")


@app.route("/home")
@cache.cached()
def home():
    """Renders the 'Home' page of the website."""

    return render_template("home.html")


@app.route("/about")
@cache.cached()
def about():
    """Renders the 'About Me' page of the website."""

    content = read_description(f"{TEXT_PATH}/about.txt")

    return render_template("about.html", content=content)


# @app.route("/skills")
# @cache.cached()
# def skills():
#     """Renders the 'Skills' page of the website."""

#     skills = get_skills(f"{TEXT_PATH}/skills.json")

#     return render_template("skills.html", skills=skills)

@app.route("/skills")
# @cache.cached()  # 依你原本的設定保留
def skills():
    skills = get_skills(f"{TEXT_PATH}/skills.json")
    return render_template("skills.html", skills=skills)

# --- 新增這個對話專用的 API 路由 ---
@app.route("/api/chat", methods=["POST"])
def chat():
    # 接收來自前端的資料
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "請輸入訊息"}), 400

    try:
        # 呼叫 OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # 也可以換成 gpt-4o-mini，比較便宜且快速
            messages=[
                {"role": "system", "content": "你是一個放在我個人履歷網站上的 AI 助手，請用友善、簡潔的語氣回答問題。"},
                {"role": "user", "content": user_message}
            ]
        )
        
        # 取得 AI 的回覆並傳回給前端
        bot_reply = response.choices[0].message.content
        return jsonify({"reply": bot_reply})
        
    except Exception as e:
        # 捕捉錯誤避免伺服器崩潰
        return jsonify({"error": str(e)}), 500

--------------------------------------------------------

@app.route("/portfolio")
@cache.cached()
def portfolio():
    """Renders the 'Portfolio' page of the website."""

    repos = get_repositories()

    return render_template("portfolio.html", repos=repos)


@app.route("/contact", methods=["GET", "POST"])
@cache.cached()
def contact():
    """Renders the 'Contact' page of the website."""

    # User reached route via POST
    if request.method == "POST":
        return render_template("result.html")

    # User reached route via GET
    return render_template("contact.html")


@app.route("/result")
@cache.cached()
def result():
    """Renders the 'Result' page of the website."""

    return render_template("result.html")
