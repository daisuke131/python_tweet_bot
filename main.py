import random
from time import sleep
import requests
from common.driver import Driver
from common.ggl_spreadsheet import Gspread
from common.tweet import Tweet
from common.util import del_kanma, now_time
import numpy as np
import threading


THREAD_COUNT = 2

class BuyableTweet:
    def __init__(self) -> None:
        self.gs = Gspread()
        self.gs.fetch_sheet(0)
        self.sheet = self.gs.worksheet
        self.tw = Tweet()
        self.errors = []
        # self.driver = Driver("PC")
        self.drivers = self.create_driver()
        
    def create_driver(self):
        drivers = []
        for i in range(THREAD_COUNT):
            drivers.append(Driver("PC"))
        return drivers

    def buy_tweet(self) -> None:
        url_datas = self.sheet.get_all_values()
        del url_datas[:1]
        for index, url_data in enumerate(url_datas):
            url_data.append(index + 2)
        url_datas_list = np.array_split(url_datas, THREAD_COUNT)
        threads = []
        for i in range(THREAD_COUNT):
            thread = threading.Thread(target=self.buy_tweet_detail, args=(url_datas_list[i], self.drivers[i]))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        
        # row_count = 0
        # for (
        #     hash_tag,
        #     url,
        #     afili_url,
        #     is_buyable,
        # ) in self.gs.worksheet.get_all_values():
        #     row_count += 1
        #     if row_count == 1:  # 一行目はカラム名なのでスルー
        #         continue
        #     self.tweet_decision(
        #         hash_tag,
        #         url,
        #         afili_url,
        #         is_buyable,
        #         row_count,
        #     )
        
    def buy_tweet_detail(self, url_datas, driver) -> None:
        for (hash_tag, url, afili_url, is_buyable, row_count) in url_datas:
            self.tweet_decision(hash_tag, url, afili_url, is_buyable, row_count, driver)
            
    def convert_class(self, class_str: str) -> str:
        class_str = class_str.replace(" ", ".")
        class_str = "." + class_str
        return class_str
        
    # def driver_get(self, url: str) -> None:
    #     if "amazon" in url:
    #         self.driver.get(url)
    #         sleep(random.randint(3, 15))
    #     elif "books.rakuten" in url:
    #         self.driver.get(url)
    #         sleep(random.randint(3, 15))

    def tweet_decision(
        self,
        hash_tag: str,
        url: str,
        afili_url: str,
        is_buyable: str,
        row_count: int,
        driver,
    ) -> None:
        try:
            is_buy: bool = False
            # self.driver_get(url)
            if "amazon" in url:
                driver.get(url)
                sleep(random.randint(3, 8))
                # sleep(3)
            elif "books.rakuten" in url:
                driver.get(url)
                sleep(random.randint(3, 15))
            if "amazon" in url:
                # アクセス制限食らったらreturn
                # print(self.driver.driver.title)
                print(driver.driver.title)
                if (
                    # "アクセス" in self.driver.driver.title
                    # or "ご迷惑" in self.driver.driver.title
                    # or self.driver.driver.title == "Amazon.co.jp"
                    "アクセス" in driver.driver.title
                    or "ご迷惑" in driver.driver.title
                    or driver.driver.title == "Amazon.co.jp"
                ):
                    print(f"{row_count}番目アクセス制限")
                    return
                target_site = "Amazon"
                # title = self.driver.find_element_by_css_selector(
                
                title = driver.find_element_by_css_selector(
                    "#productTitle"
                    ).text.replace("\n", "")
                """
                #add-to-cart-buttonと#buy-now-buttonは普通の商品
                #one-click-buttonは本
                #buy-now-buttonのみは予約ボタン
                """
                if (
                    # self.driver.find_elements_by_css_selector("#add-to-cart-button")
                    # or self.driver.find_elements_by_css_selector("#one-click-button")
                    # or self.driver.find_elements_by_css_selector("#buy-now-button")
                    driver.find_elements_by_css_selector("#add-to-cart-button")
                    or driver.find_elements_by_css_selector("#one-click-button")
                    or driver.find_elements_by_css_selector("#buy-now-button")
                ):
                    is_buy = True
            elif "books.rakuten" in url:
                # print(self.driver.driver.title)
                print(driver.driver.title)
                target_site = "楽天ブックス"
                # title = self.driver.find_element_by_css_selector(
                title = driver.find_element_by_css_selector(
                    "#productTitle"
                ).text.replace("\n", "")
                # if self.driver.find_elements_by_css_selector(".new_addToCart"):
                if driver.find_elements_by_css_selector(".new_addToCart"):
                    is_buy = True
            else:
                target_site = "楽天市場"
                # taget_url = url
                # taget_urls = taget_url.split("/")
                # item_code = f"{taget_urls[3]}:{taget_urls[4]}"
                api_url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
                params = {
                    "applicationId": "1019079537947262807",
                    "format": "json",
                    "itemCode": url,
                }
                res = requests.get(api_url, params)
                if not (300 > res.status_code >= 200):
                    return None
                result = res.json()
                title = result["Items"][0]["Item"]["itemName"]
                print(title)
                if result["Items"][0]["Item"]["availability"] == 1:
                    is_buy = True

            if is_buyable == "":
                if is_buy:
                    self.gs.update_cell(row_count, 4, 1)
                else:
                    self.gs.update_cell(row_count, 4, 0)
            else:
                is_buyable = int(is_buyable)
                if is_buy:
                    # is_buyableが0ならTweet
                    if is_buyable == 0:
                        formated_hash_tag = self.formating_hash_tag(hash_tag)
                        if formated_hash_tag:
                            formated_hash_tag = "\n" + formated_hash_tag
                        self.tw.tweet(
                            f"{now_time()}\n＼{target_site}で購入できます！／\n{title}"
                            + f"\n{afili_url}{formated_hash_tag}"
                        )
                        print(
                            f"{now_time()}\n＼{target_site}で購入できます！／\n{title}"
                            + f"\n{afili_url}{formated_hash_tag}"
                        )
                        # 前回購入可を1にする
                    self.gs.update_cell(row_count, 4, 1)
                else:
                    self.gs.update_cell(row_count, 4, 0)
            print(f"({now_time()}){row_count}番目成功")
        except Exception:
            self.errors.append([f"{row_count}番目", url])
            print(f"({now_time()}){row_count}番目失敗")

    def formating_hash_tag(self, hash_tag: str) -> str:
        hash_tag_list = hash_tag.split()
        if not hash_tag_list:
            return ""
        new_hash_tag_list = []
        for s in hash_tag_list:
            new_hash_tag_list.append("#" + s)
        return " ".join(new_hash_tag_list)

    def output_errors(self) -> None:
        self.gs.fetch_sheet(1)
        for error in self.errors:
            self.gs.append_row(error)
        self.gs.fetch_sheet(0)
    
    def driver_quit(self) -> None:
        for driver in self.drivers:
            driver.quit()


def main():
    while True:
        bt = BuyableTweet()
        for i in range(100):
            try:
                bt.buy_tweet()
                # bt.driver.quit()
                bt.output_errors()
                print("==========")
            except Exception:
                pass
        bt.driver_quit()

if __name__ == "__main__":
    main()