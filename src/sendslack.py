from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
with open('slack_api_key.txt', 'r') as f:
    KEY = f.readline().strip()
client = WebClient(token=KEY)

def send(channel, text):
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        assert response["message"]["text"] == text
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
