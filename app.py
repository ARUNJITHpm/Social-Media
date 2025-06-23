from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

PAGE_ID = "106816445689970"
ACCESS_TOKEN = "EAAKTwjTcKBoBO1bQO9ZCDxJVRZCZAfu0W15kZBGkDhGr36ZBI9aubFXkgYp92IHoTjGgDI8Iyotz9LnfADW0G9q7lK63eJabTb1cyA7Vq2gNvY7y9R5Rq4vSGs7R9nKlEOxJJ6pg7PZAK7HQ4ZBgGbtcKsUGSWP17oileuYYgX1yNGQzAFQDBm65rhUjGnOq8bYt0n048LZCx61XFxsuZAB3S110ZBzMV7sbYEHkx865t4OZB0QzJLZBueyOgjGvNwZDZD"
GRAPH_URL = "https://graph.facebook.com/v23.0"


@app.route('/create_post', methods=['POST'])
def create_post():
    data = request.get_json()
    message = data.get('message', 'Hello!')

    url = f"{GRAPH_URL}/{PAGE_ID}/feed"
    payload = {'message': message, 'access_token': ACCESS_TOKEN}

    fb_response = requests.post(url, data=payload)
    return jsonify(fb_response.json()), fb_response.status_code


@app.route('/post_details/<post_id>', methods=['GET'])
def post_details(post_id):
    url = f"{GRAPH_URL}/{post_id}"
    params = {'access_token': ACCESS_TOKEN}
    fb_response = requests.get(url, params=params)
    return jsonify(fb_response.json()), fb_response.status_code


@app.route('/comments/<post_id>', methods=['POST'])
def comment_post(post_id):
    data = request.get_json()
    comment_message = data.get('message', 'Nice post!')

    url = f"{GRAPH_URL}/{post_id}/comments"
    payload = {'message': comment_message, 'access_token': ACCESS_TOKEN}
    fb_response = requests.post(url, data=payload)
    return jsonify(fb_response.json()), fb_response.status_code


@app.route('/view_comments/<post_id>', methods=['GET'])
def view_comments(post_id):
    url = f"{GRAPH_URL}/{post_id}/comments"
    params = {'access_token': ACCESS_TOKEN}
    fb_response = requests.get(url, params=params)
    return jsonify(fb_response.json()), fb_response.status_code


@app.route('/reply_comment/<comment_id>', methods=['POST'])
def reply_comment(comment_id):
    data = request.get_json()
    reply_message = data.get('message', 'Thanks!')

    url = f"{GRAPH_URL}/{comment_id}/comments"
    payload = {'message': reply_message, 'access_token': ACCESS_TOKEN}
    fb_response = requests.post(url, data=payload)
    return jsonify(fb_response.json()), fb_response.status_code


if __name__ == '__main__':
    app.run(port=8080)
