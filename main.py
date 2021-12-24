import json
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Message:
    def __init__(self, msgStr):
        self.msg = msgStr

    def user(self):
        return self.msg["user"]

    def thread_ts(self):
        return self.msg["thread_ts"]

    def ts(self):
        return self.msg["ts"]

    def reply_users(self):
        if "reply_users" in self.msg:
            return self.msg["reply_users"]
        return []


def parse_messages(msgs):
    messages = []
    for item in msgs:
        messages.append(Message(item))
    return messages


participationMap = {}


def find_participation(messageList):
    for msg in messageList:
        user = msg.user()
        replyUsers = msg.reply_users()
        if len(user) > 0 and len(replyUsers) > 0:
            for u in replyUsers:
                if u in participationMap:
                    participationMap[u] = participationMap[u] + 1
                else:
                    participationMap[u] = 1
            if user in replyUsers:
                participationMap[user] = participationMap[user] - 1


if __name__ == '__main__':
    channel = os.getenv("CHANNEL_ID")

    client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    try:
        response = client.conversations_history(channel=channel, limit=10)
        messages = parse_messages(response["messages"])
        find_participation(messages)
        for w in sorted(participationMap, key=participationMap.get, reverse=True):
            print(w, participationMap[w])
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
