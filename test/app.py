# app.py
from flask import Flask, request, jsonify
import requests
from openai import OpenAI
import dotenv
import os
import time

# ——— Load config from .env ——————————————————
dotenv.load_dotenv()
PAGE_ID      = os.getenv("PAGE_ID", "106816445689970")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GRAPH_URL    = os.getenv("GRAPH_URL", "https://graph.facebook.com/v23.0")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
MODEL_NAME          = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
TEMPERATURE         = float(os.getenv("OPENAI_API_TEMPERATURE", 0.7))

if not all([ACCESS_TOKEN, OPENAI_API_KEY]):
    raise RuntimeError("Please set ACCESS_TOKEN and OPENAI_API_KEY in your .env")

# ——— Init Flask & OpenAI —————————————————————
app    = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_llm_reply(post_description, user_comment, user_name):
    prompt = f"""
Post Description: "{post_description}"
User Comment: "{user_comment}"
Task: Write a friendly, meaningful reply to the user's comment based on the post description.
- If the comment feels casual or enthusiastic, reply in a slightly longer, conversational tone (but still concise).
- If the comment feels formal or professional, keep the reply short and polite.
- If the comment is very brief (like "Nice" or "Good"), give a short, crisp reply.
In all cases, mention the user's name ("{user_name}") naturally in the reply.
"""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful, friendly assistant for social media."},
            {"role": "user",   "content": prompt}
        ],
        temperature=TEMPERATURE
    )
    return resp.choices[0].message.content.strip()

@app.route('/create_post', methods=['POST'])
def create_post():
    data    = request.get_json()
    message = data.get('message', 'Hello!')
    url     = f"{GRAPH_URL}/{PAGE_ID}/feed"
    payload = {'message': message, 'access_token': ACCESS_TOKEN}
    fb_resp = requests.post(url, data=payload)
    return jsonify(fb_resp.json()), fb_resp.status_code

@app.route('/post_details/<post_id>', methods=['GET'])
def post_details(post_id):
    url     = f"{GRAPH_URL}/{post_id}"
    params  = {'access_token': ACCESS_TOKEN}
    fb_resp = requests.get(url, params=params)
    return jsonify(fb_resp.json()), fb_resp.status_code

@app.route('/view_comments/<post_id>', methods=['GET'])
def view_comments(post_id):
    url    = f"{GRAPH_URL}/{post_id}/comments"
    params = {
        'access_token': ACCESS_TOKEN,
        'fields': 'id,message,from'   # ← explicitly request these fields
    }
    fb_resp = requests.get(url, params=params)
    # optional: log fb_resp.json() here to see Graph API errors
    return jsonify(fb_resp.json()), fb_resp.status_code

@app.route('/reply_comment/<comment_id>', methods=['POST'])
def reply_comment(comment_id):
    data  = request.get_json()
    reply = data.get('message', 'Thanks!')
    url      = f"{GRAPH_URL}/{comment_id}/comments"
    payload  = {'message': reply, 'access_token': ACCESS_TOKEN}
    fb_resp  = requests.post(url, data=payload)
    return jsonify(fb_resp.json()), fb_resp.status_code

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get("hub.verify_token")
        if token == ACCESS_TOKEN:
            return request.args.get("hub.challenge")
        return "Invalid verification token", 403

    # Facebook will POST here on new comments
    payload = request.json or {}
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") == "feed" and change["value"].get("item") == "comment":
                c_id    = change["value"]["comment_id"]
                msg     = change["value"].get("message", "")
                user_nm = change["value"].get("from", {}).get("name", "there")
                post_id = change["value"].get("post_id")

                # fetch post text
                post_txt = requests.get(
                    f"{GRAPH_URL}/{post_id}",
                    params={'access_token': ACCESS_TOKEN}
                ).json().get("message", "")

                # generate & send reply
                reply = generate_llm_reply(post_txt, msg, user_nm)
                requests.post(
                    f"{GRAPH_URL}/{c_id}/comments",
                    data={'message': reply, 'access_token': ACCESS_TOKEN}
                )
    return "Event Received", 200

if __name__ == '__main__':
    # give Flask a moment
    time.sleep(2)
    app.run(port=8080)