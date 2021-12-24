import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

if __name__ == '__main__':
    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    try:
        response = client.conversations_history(channel="#help-engineering", limit=10)
        print(response)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
