import os

import gspread
import pandas as pd
from dotenv import load_dotenv
from gspread.models import Worksheet
from oauth2client.service_account import ServiceAccountCredentials

JASON_FILE_NAME = "python-buyable-twitter-bot-0bb63e591ec9.json"
JSON_PATH = os.path.join(os.getcwd(), JASON_FILE_NAME)
load_dotenv()
SPREAD_SHEET_KEY = os.getenv("SPREAD_SHEET_KEY")


class Gspread:
    def __init__(self) -> None:
        self.workbook = self.connect_gspread()
        self.worksheet: Worksheet
        self.df = []

    def connect_gspread(self):
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                JSON_PATH, scope
            )
            gc = gspread.authorize(credentials)
            workbook = gc.open_by_key(SPREAD_SHEET_KEY)
            return workbook
        except Exception:
            print("Googleスプレッドシートを読み込めませんでした。")
            # return None

    def read_sheet(self, sheet_num: int):
        # 0が一枚目のシート
        self.worksheet = self.workbook.get_worksheet(sheet_num)
        return self.worksheet

    # def read_sheet(self, workbook, sheet_name: str):
    #     self.worksheet = self.workbook.worksheet(sheet_name)

    def set_df(self):
        self.df = pd.DataFrame(self.worksheet.get_all_values())
        self.df.columns = list(self.df.loc[0, :])
        self.df.drop(0, inplace=True)
        self.df.reset_index(inplace=True)
        self.df.drop("index", axis=1, inplace=True)
