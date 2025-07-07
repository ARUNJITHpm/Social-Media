# post.py (poller)
import time
import schedule
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# ——— Load environment ——————————————————————
load_dotenv()
ACCESS_TOKEN    = os.getenv("ACCESS_TOKEN")
raw             = os.getenv("NGROK_URL", "")
# take only the first “word” before any space or #
NGROK_URL       = raw.split()[0].strip().strip('"')
POST_ID         = os.getenv("POST_ID")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
MODEL_NAME      = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
TEMPERATURE     = float(os.getenv("OPENAI_API_TEMPERATURE", 0.7))

if not all([ACCESS_TOKEN, NGROK_URL, POST_ID, OPENAI_API_KEY]):
    raise RuntimeError("Please set ACCESS_TOKEN, NGROK_URL, POST_ID, and OPENAI_API_KEY in your .env")

# ——— Init OpenAI client —————————————————————
client = OpenAI(api_key=OPENAI_API_KEY)

# ——— Track which comments we've replied to —————————————
replied_ids = set()

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

def poll_and_reply():
    global replied_ids

    # 1) Fetch all comments from our local webhook proxy
    r = requests.get(f"{NGROK_URL}/view_comments/{POST_ID}")
    try:
        r.raise_for_status()
    except requests.HTTPError:
        print("Failed to fetch comments:", r.text)
        return

    comments = r.json().get("data", [])
    if not comments:
        return

    # 2) Filter to only brand-new, un-replied comments
    new_comments = [c for c in comments if c["id"] not in replied_ids]
    if not new_comments:
        return

    # 3) Grab the post text once
    pd = requests.get(f"{NGROK_URL}/post_details/{POST_ID}")
    try:
        pd.raise_for_status()
    except requests.HTTPError:
        print("Failed to fetch post details:", pd.text)
        return

    post_desc = pd.json().get("message", "")

    # 4) Generate & send a reply for each new comment
    for c in new_comments:
        cid     = c["id"]
        author  = c.get("from", {}).get("name", "there")
        message = c.get("message", "")

        reply = generate_llm_reply(post_desc, message, author)
        resp  = requests.post(
            f"{NGROK_URL}/reply_comment/{cid}",
            json={"message": reply}
        )
        if resp.ok:
            print(f"Replied to {cid} by {author}: {reply}")
            # mark it so we don't reply again
            replied_ids.add(cid)
        else:
            print(f"Failed to send reply to {cid}:", resp.text)

# 5) Schedule the poll every 3 seconds
schedule.every(3).seconds.do(poll_and_reply)

if __name__ == "__main__":
    # do one immediate run, then enter loop
    poll_and_reply()
    while True:
        schedule.run_pending()
        time.sleep(1)
