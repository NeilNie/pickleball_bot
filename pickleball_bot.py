import requests
import argparse
import json
from termcolor import colored
import datetime as DT


def get_date_week_from_today_string():
    today = DT.date.today()
    week_future = today + DT.timedelta(days=7)
    # format date into yyyy-mm-dd
    today = today.strftime("%Y-%m-%d")
    week_future = week_future.strftime("%Y-%m-%d")
    print(week_future)


parser = argparse.ArgumentParser(description='Pickleball Bot')
parser.add_argument('--username', type=str, help='Username for clublocker')
parser.add_argument('--password', type=str, help='Password for clublocker')

args = parser.parse_args()

login_url = "https://api.ussquash.com/clublocker_login"

payload = f'backTo=stanfordtennis.clublocker.com&customLogin=stanfordtennis&username={args.username}%40stanford.edu&password={args.password}'
headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Cookie': 'USSQ-API-SESSION=s%3A_R5-cmtx4Rpftj_TeZVpgfxCw-oEz7WY.kJH3RlHC0u2j%2BAbnTRuQABwew70JetPwfRi9NSbyajw'
}

response = requests.request("POST", login_url, headers=headers, data=payload, allow_redirects=False)

try:
    access_token = response.text.split('access_token=')[1].split('&')[0]
except Exception as e:
    print(colored("Failed to login. Please check your username and password.", "red"))
    exit()

print(colored("Successfully logged in!", "green"))

# =========

url = "https://api.ussquash.com/resources/res/clubs/13911/reservations"

payload = json.dumps({
  "type": "match",
  "applyUserRestrictionsForAdmin": True,
  "clubId": 13911,
  "courtId": 3988,
  "date": get_date_week_from_today_string(),
  "slot": "20:00-21:00",
  "isPrivate": True,
  "notes": [],
  "players": [
    {
      "type": "member",
      "confirmed": False,
      "id": 470522,
      "text": "Neil Nie",
      "isMyself": True
    },
    {
      "type": "fill",
      "text": "Let other players join this reservation",
      "id": 0
    },
    {
      "type": "fill",
      "text": "Let other players join this reservation",
      "id": 0
    },
    {
      "type": "fill",
      "text": "Let other players join this reservation",
      "id": 0
    }
  ],
  "payingForAll": False,
  "MatchProperties": {
    "restrictJoinByRating": False,
    "matchType": 2,
    "customMatchType": 587
  }
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + access_token,
  'Cookie': 'USSQ-API-SESSION=s%3A_R5-cmtx4Rpftj_TeZVpgfxCw-oEz7WY.kJH3RlHC0u2j%2BAbnTRuQABwew70JetPwfRi9NSbyajw'
}

response = requests.request("POST", url, headers=headers, data=payload)

response_json = json.loads(response.text)
if response_json.get('error'):
    print(colored(response_json.get('error'), "red"))
else:
    print(colored("Successfully created reservation!", "green"))
