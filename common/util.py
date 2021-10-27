import os
import random
from datetime import datetime


def hyphen_now():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def now_time():
    return datetime.now().strftime("%H:%M:%S")


def fetch_user_agent() -> str:
    user_agent = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        + "(KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    ]
    return user_agent[random.randrange(0, len(user_agent), 1)]


def fetch_sp_user_agent() -> str:
    user_agent = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) "
        + "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) "
        + "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 "
        + "Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; U; Android 2.2) AppleWebKit/533.1 "
        + "(KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) "
        + "AppleWebKit/535.19 (KHTML, like Gecko; googleweblight) "
        + "Chrome/38.0.1025.166 Mobile Safari/535.19",
    ]
    return user_agent[random.randrange(0, len(user_agent), 1)]


def filename_creation(filename: str) -> str:
    os.path.join(os.getcwd(), "csv")
    return "{filename}_{datetime}".format(filename=filename, datetime=hyphen_now())


def del_kanma(price: str) -> int:
    price = price.replace(",", "").replace("￥", "")
    return int(price)