import possum_every_hour
import json

client_id = ""
client_secret = "" 
token_url = "https://api.twitter.com/2/oauth2/token"

twitter_client = possum_every_hour.make_token()
redis_client = possum_every_hour.r

token_data = redis_client.get("token")
decoded_token_data = token_data.decode("utf-8").replace("'", '"')
parsed_token_data = json.loads(decoded_token_data)

refreshed_token_data = twitter_client.refresh_token(
    token_url=token_url,
    refresh_token=parsed_token_data["refresh_token"],
    auth=(client_id, client_secret),
)

json_refreshed_token_data = json.dumps(refreshed_token_data)

redis_client.set("token", json_refreshed_token_data)

media_id = possum_every_hour.upload_media("possum.jpeg", refreshed_token_data)

possum_every_hour.post_tweet({"media_ids": media_id})

