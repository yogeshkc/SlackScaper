This script uses the Slack python SDK to find out participation of members in a given slack channel.

### Scoring
1 point is given to every user involved in a thread except the one who started the thread. 
API Reference: https://api.slack.com/methods/conversations.history https://api.slack.com/methods/users.info


### Env Variables

- SLACK_BOT_TOKEN: Oath token
- CHANNEL_ID: id of the channel to scrap
- TIME_PERIOD_MONTHS: Look behind period
