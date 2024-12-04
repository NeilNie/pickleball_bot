import requests
import argparse
import json
from termcolor import colored
import datetime as DT
from scheduler import Scheduler
from scheduler.trigger.core import Tuesday, Wednesday
import time
import pytz


LOGIN_URL = "https://api.ussquash.com/clublocker_login"
RESERVATION_URL = "https://api.ussquash.com/resources/res/clubs/13911/reservations"


def get_date_week_from_today_string():
    today = DT.date.today()
    week_future = today + DT.timedelta(days=7)
    # format date into yyyy-mm-dd
    today = today.strftime("%Y-%m-%d")
    week_future = week_future.strftime("%Y-%m-%d")
    return week_future


def get_court_reservation_on_schedule(username: str, password: str, time_slot, now: bool = False):
    """_summary_

    Args:
            username (str): _description_
            password (str): _description_
    """

    
    print("verifying your login information")
    verify_login(username, password)

    if now:
        get_court_reservation(username, password, time_slot)
    else:
        tz_sf = pytz.timezone("America/Los_Angeles")
        schedule = Scheduler(tzinfo=tz_sf)
        schedule.weekly([Wednesday(DT.time(hour=19, minute=0, second=1, tzinfo=tz_sf))], get_court_reservation, args=(username, password, time_slot))
        print(schedule)

        print(f"Request court reservation every day...")
        while True:
            schedule.exec_jobs()
            time.sleep(1)


def verify_login(username: str, password: str):
    payload = f"backTo=stanfordtennis.clublocker.com&customLogin=stanfordtennis&username={username}%40stanford.edu&password={password}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.request(
        "POST", LOGIN_URL, headers=headers, data=payload, allow_redirects=False
    )

    try:
        _ = response.text.split("access_token=")[1].split("&")[0]
    except Exception as e:
        print(
            colored("Failed to login. Please check your username and password.", "red")
        )
        exit()

    print(colored("Successfully logged in!", "green"))



def get_court_reservation(username: str, password: str, slot: int):
    """_summary_

    Args:
            username (str): _description_
            password (str): _description_
    """

    payload = f"backTo=stanfordtennis.clublocker.com&customLogin=stanfordtennis&username={username}%40stanford.edu&password={password}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "USSQ-API-SESSION=s%3A_R5-cmtx4Rpftj_TeZVpgfxCw-oEz7WY.kJH3RlHC0u2j%2BAbnTRuQABwew70JetPwfRi9NSbyajw",
    }

    response = requests.request(
        "POST", LOGIN_URL, headers=headers, data=payload, allow_redirects=False
    )

    try:
        access_token = response.text.split("access_token=")[1].split("&")[0]
    except Exception as e:
        print(
            colored("Failed to login. Please check your username and password.", "red")
        )
        exit()

    print(colored("Successfully logged in!", "green"))

    if slot == 0:
        slot = "20:00-21:00"
    elif slot == 1:
        slot = "21:00-22:00"

    with open("users.json", "r") as f:
        users = json.load(f)

    # =========
    payload = json.dumps(
        {
            "type": "match",
            "applyUserRestrictionsForAdmin": True,
            "clubId": 13911,
            "courtId": 3988,
            "date": get_date_week_from_today_string(),
            "slot": slot,
            "isPrivate": True,
            "notes": [],
            "players": [
                users[username],
                {
                    "type": "fill",
                    "text": "Let other players join this reservation",
                    "id": 0,
                },
                {
                    "type": "fill",
                    "text": "Let other players join this reservation",
                    "id": 0,
                },
                {
                    "type": "fill",
                    "text": "Let other players join this reservation",
                    "id": 0,
                },
            ],
            "payingForAll": False,
            "MatchProperties": {
                "restrictJoinByRating": False,
                "matchType": 2,
                "customMatchType": 587,
            },
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
        "Cookie": "USSQ-API-SESSION=s%3A_R5-cmtx4Rpftj_TeZVpgfxCw-oEz7WY.kJH3RlHC0u2j%2BAbnTRuQABwew70JetPwfRi9NSbyajw",
    }

    response = requests.request("POST", RESERVATION_URL, headers=headers, data=payload)

    response_json = json.loads(response.text)
    if response_json.get("error"):
        print(colored(response_json.get("error"), "red"))
    else:
        print(colored("Successfully created reservation!", "green"))


parser = argparse.ArgumentParser(description="Pickleball Bot")
parser.add_argument("--username", type=str, help="Username for clublocker")
parser.add_argument("--password", type=str, help="Password for clublocker")
parser.add_argument("--slot", type=int, help="0 for the 8-9 slot 1 for the 9-10 slot")

args = parser.parse_args()

get_court_reservation_on_schedule(args.username, args.password, args.slot)
