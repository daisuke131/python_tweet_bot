import requests
from bs4 import BeautifulSoup

from common.util import fetch_user_agent


def fetch_soup(url: str):
    headers = {"User-Agent": fetch_user_agent()}
    resp = requests.get(url, headers=headers)
    return BeautifulSoup(resp.text, "html.parser")
