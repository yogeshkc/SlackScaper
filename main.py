import os
from datetime import date
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable
from alive_progress import alive_bar
import time

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

PAGINATION_LIMIT = 50
TIME_PERIOD_MONTHS = int(os.getenv("TIME_PERIOD_MONTHS"))


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


def update_participation(messageList):
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

    print("Calculating User Participation for past %d months" % TIME_PERIOD_MONTHS )
    try:
        oldestTs = date.today() + relativedelta(months=-TIME_PERIOD_MONTHS)
        cursor = ""
        while True:
            response = client.conversations_history(channel=channel, oldest=str(time.mktime(oldestTs.timetuple())),
                                                    limit=PAGINATION_LIMIT, cursor=cursor)
            messages = parse_messages(response["messages"])
            update_participation(messages)
            if "response_metadata" in response and "next_cursor" in response["response_metadata"]:
                cursor = response["response_metadata"]["next_cursor"]
            else:
                # at end of list
                break

        total_users = len(participationMap)
        print("Calculated User Participation!")
        print("Mapping UserId to User Names. Total users in channel = %d" % total_users)
        t = PrettyTable(['User', 'Score'])
        with alive_bar(total_users) as bar:
            for w in sorted(participationMap, key=participationMap.get, reverse=True):
                score = participationMap[w]
                if score > 0:
                    try:
                        user_name = client.users_info(user=w)["user"]["name"]
                        t.add_row([user_name, score])
                    except SlackApiError as e:
                        print("Could not get user %s: %s" % (w,  e.response["error"]))
                bar()
        print(t)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")
