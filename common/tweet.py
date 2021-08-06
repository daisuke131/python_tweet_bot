import os

import tweepy
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


class Tweet:
    def __init__(self) -> None:
        auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

    def tweet(self, tweet_text: str) -> None:
        self.api.update_status(tweet_text)

    def fetch_tweet(self, user_id: str, count: int) -> None:
        # ツイートを投稿
        Account = user_id  # 取得したいユーザーのユーザーIDを代入
        tweets = self.api.user_timeline(Account, count=count, page=1)
        num = 1  # ツイート数を計算するための変数
        for tweet in tweets:
            print("twid : ", tweet.id)  # tweetのID
            print("user : ", tweet.user.screen_name)  # ユーザー名
            print("date : ", tweet.created_at)  # 呟いた日時
            print(tweet.text)  # ツイート内容
            print("favo : ", tweet.favorite_count)  # ツイートのいいね数
            print("retw : ", tweet.retweet_count)  # ツイートのリツイート数
            print("ツイート数 : ", num)  # ツイート数
            print("=" * 80)  # =を80個表示
            num += 1  # ツイート数を計算
