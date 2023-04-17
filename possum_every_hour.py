import base64
import hashlib
import os
import re
import json
import redis
from requests_oauthlib import OAuth1Session, OAuth2Session
from flask import Flask, redirect, request, session


r = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.secret_key = os.urandom(50)

# v2 API stuff
client_id = ""
client_secret = ""
auth_url = ""
token_url = ""
redirect_uri = ""

# v1 API stuff
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

# Set the scopes
scopes = ["tweet.read", "users.read", "tweet.write", "offline.access"]


# Create a code verifier
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

# Create a code challenge
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")


def get_pic_path():
    return "possum.jpg"

oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret
)
    
def upload_media(file_path, token):
    url = "https://upload.twitter.com/1.1/media/upload.json"

    with open(file_path, "rb") as media_file:
        media_data = media_file.read()

    response = oauth.post(url, files={"media": media_data})
    response.raise_for_status()
    return response.json()["media_id_string"]



def post_tweet(payload):    
    response = oauth.post("https://api.twitter.com/1.1/statuses/update.json", data=payload)
    response.raise_for_status()
    return response.json()

@app.route("/")
def demo():
    global twitter
    twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)
    authorization_url, state = twitter.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)


@app.route("/oauth/callback", methods=["GET"])
def callback():
    code = request.args.get("code")
    token = twitter.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code,
    )
    st_token = '"{}"'.format(token)
    j_token = json.loads(st_token)
    r.set("token", j_token)
    payload = {"text": "hi from save_the_possum_bot"}
    response = post_tweet(payload, token).json()
    return response


if __name__ == "__main__":
    app.run()