import os
import time
from collections import defaultdict, deque

import anthropic
from flask import Flask, jsonify, render_template, request

app = Flask(__name__, template_folder=".")

# ---- Settings (environment variables thi badli shakay) ----
BRAND_NAME = os.environ.get("BRAND_NAME", "ADUQT")
MODEL = os.environ.get("MODEL", "claude-sonnet-5-5")
MAX_REQUESTS_PER_MINUTE = int(os.environ.get("RATE_LIMIT", "10"))
MAX_QUESTION_LENGTH = 500

SYSTEM_PROMPT = (
    f"Tu {BRAND_NAME} chhe, ek AI search assistant. "
    "User je bhasha ma sawal puchhe (Gujarati, Hindi, English) te j bhasha ma jawab aap. "
    "Jawab saral, spasht ane tunko rakh. Taaza mahiti mate web search vapar. "
    "Tu potane {brand} tarike oLkhavje.".replace("{brand}", BRAND_NAME)
)

# API key environment variable ANTHROPIC_API_KEY parthi aapo-aap vanchay chhe
client = anthropic.Anthropic()

# ---- Saral rate limit (darek IP mate) ----
_hits = defaultdict(deque)


def too_many_requests(ip: str) -> bool:
    now = time.time()
    q = _hits[ip]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= MAX_REQUESTS_PER_MINUTE:
        return True
    q.append(now)
    return False


@app.route("/")
def home():
    return render_template("index.html", brand=BRAND_NAME)


@app.route("/api/ask", methods=["POST"])
def ask():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
    if too_many_requests(ip):
        return jsonify(error="Ghani request thai gai. Ek minute pachi fari prayatna karo."), 429

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return jsonify(error="Sawal khali chhe."), 400
    if len(question) > MAX_QUESTION_LENGTH:
        return jsonify(error="Sawal khub lambo chhe."), 400

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
            messages=[{"role": "user", "content": question}],
        )
    except Exception:
        return jsonify(error="Kaik gadbad thai. Thodi vaar pachi prayatna karo."), 500

    answer_parts = []
    sources = []
    seen = set()
    for block in response.content:
        if block.type == "text":
            answer_parts.append(block.text)
        elif block.type == "web_search_tool_result":
            results = block.content if isinstance(block.content, list) else []
            for r in results:
                url = getattr(r, "url", None)
                if url and url not in seen:
                    seen.add(url)
                    sources.append({"title": getattr(r, "title", url), "url": url})

    return jsonify(answer="".join(answer_parts).strip(), sources=sources[:6])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
