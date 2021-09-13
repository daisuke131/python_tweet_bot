import os

import gspread
import pandas as pd
from dotenv import load_dotenv
from gspread.models import Worksheet
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()
JASON_FILE_NAME = os.getenv("JASON_FILE_NAME")
JSON_PATH = os.path.join(os.getcwd(), JASON_FILE_NAME)
SPREAD_SHEET_KEY = os.getenv("SPREAD_SHEET_KEY")


class Gspread:
    def __init__(self) -> None:
        self.workbook = self.fetch_workbook()
        self.worksheet: Worksheet
        self.df = []

    def fetch_workbook(self):
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

    def fetch_sheet(self, sheet_num: int):
        # 0が一枚目のシート
        self.worksheet = self.workbook.get_worksheet(sheet_num)

    # def fetch_sheet(self, workbook, sheet_name: str):
    #     self.worksheet = self.workbook.worksheet(sheet_name)

    def append_row(self, val: list) -> None:
        # value_input_option="USER_ENTERED"全て文字列として書き込みのを防止
        self.worksheet.append_row(val, value_input_option="USER_ENTERED")

    def update_cell(self, row_count: int, column_count: int, val):
        self.worksheet.update_cell(row_count, column_count, val)

    def set_df(self):
        self.df = pd.DataFrame(self.worksheet.get_all_values())
        self.df.columns = list(self.df.loc[0, :])
        self.df.drop(0, inplace=True)
        self.df.reset_index(inplace=True)
        self.df.drop("index", axis=1, inplace=True)
