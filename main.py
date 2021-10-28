import random
from time import sleep
from common.driver import Driver
from common.ggl_spreadsheet import Gspread
from common.tweet import Tweet
from common.util import del_kanma, now_time
import numpy as np
import threading


THREAD_COUNT = 3

class BuyableTweet:
    def __init__(self) -> None:
        self.gs = Gspread()
        self.gs.fetch_sheet(0)
        self.sheet = self.gs.worksheet
        self.tw = Tweet()
        self.errors = []
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
        
    def buy_tweet_detail(self, url_datas, driver) -> None:
        for (hash_tag, url, afili_url, price, is_buyable, row_count) in url_datas:
            self.tweet_decision(hash_tag, url, afili_url, del_kanma(price), is_buyable, int(row_count), driver)
            
    def convert_class(self, class_str: str) -> str:
        class_str = class_str.replace(" ", ".")
        class_str = "." + class_str
        return class_str
        
    def fetch_amazon_now_price(self, driver) -> list:
        cls = self.convert_class("a-size-base a-color-price a-color-price")
        now_price_int: int = 0
        now_price_str: str = ""

        if driver.find_elements_by_css_selector(
            "span.a-price.a-text-price.a-size-medium"
        ):
            now_price_str = driver.find_element_by_css_selector(
                "span.a-price.a-text-price.a-size-medium"
            ).text
            now_price_int = del_kanma(now_price_str)
        elif driver.find_elements_by_css_selector("#priceblock_ourprice"):
            now_price_str = driver.find_element_by_css_selector(
                "#priceblock_ourprice"
            ).text
            now_price_int = del_kanma(now_price_str)
        elif driver.find_elements_by_css_selector(f".a-color-base > {cls}"):
            now_price_str = driver.find_element_by_css_selector(
                f".a-color-base > {cls}"
            ).text
            now_price_int = del_kanma(now_price_str)
        return now_price_str, now_price_int
        
    def fetch_rakuten_book_now_price(self, driver) -> list:
        now_price_int: int = 0
        now_price_str: str = ""
        now_price_str = "￥" + driver.find_element_by_css_selector("span.price").text.replace("円", "")
        now_price_int = del_kanma(now_price_str)
        return now_price_str, now_price_int
        
    def fetch_now_price_kanma(self, price) -> list:
        now_price_str = "￥" + "{:,}".format(price)
        return now_price_str, price

    def tweet_decision(
        self,
        hash_tag: str,
        url: str,
        afili_url: str,
        price: int,
        is_buyable: str,
        row_count: int,
        driver,
    ) -> None:
        try:
            is_buy: bool = False
            if "amazon" in url:
                driver.get(url)
                sleep(random.randint(3, 5))
                # アクセス制限食らったらreturn
                print(driver.driver.title)
                if (
                    "アクセス" in driver.driver.title
                    or "ご迷惑" in driver.driver.title
                    or driver.driver.title == "Amazon.co.jp"
                ):
                    print(f"{row_count}番目アクセス制限")
                    return
                target_site = "Amazon"
                # タイトル取得
                title = driver.find_element_by_css_selector(
                    "#productTitle"
                    ).text.replace("\n", "")
                # 金額取得
                now_price_str, now_price_int = self.fetch_amazon_now_price(driver)
                """
                #add-to-cart-buttonと#buy-now-buttonは普通の商品
                #one-click-buttonは本
                #buy-now-buttonのみは予約ボタン
                """
                if (
                    driver.find_elements_by_css_selector("#add-to-cart-button")
                    or driver.find_elements_by_css_selector("#one-click-button")
                    or driver.find_elements_by_css_selector("#buy-now-button")
                ):
                    is_buy = True
            elif "books.rakuten" in url:
                driver.get(url)
                sleep(random.randint(3, 5))
                print(driver.driver.title)
                target_site = "楽天ブックス"
                # タイトル取得
                title = driver.find_element_by_css_selector(
                    "#productTitle"
                ).text.replace("\n", "")
                # 金額取得
                now_price_str, now_price_int = self.fetch_rakuten_book_now_price(driver)
                
                if driver.find_elements_by_css_selector(".new_addToCart"):
                    is_buy = True
            else:
                target_site = "楽天市場"
                api_url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
                params = {
                    "applicationId": "1019079537947262807",
                    "format": "json",
                    # F12押して一番下のitemidをとる~~~~~~:~~~~~~~という形
                    "itemCode": url,
                }
                res = requests.get(api_url, params)
                sleep(3)
                if not (300 > res.status_code >= 200):
                    return None
                result = res.json()
                title = result["Items"][0]["Item"]["itemName"]
                print(title)
                now_price_str, now_price_int = self.fetch_now_price_kanma(result["Items"][0]["Item"]["itemPrice"])
                if result["Items"][0]["Item"]["availability"] == 1:
                    is_buy = True

            if is_buyable == "":
                if is_buy:
                    self.gs.update_cell(row_count, 5, 1)
                else:
                    self.gs.update_cell(row_count, 5, 0)
            else:
                is_buyable = int(is_buyable)
                if is_buy:
                    formated_hash_tag = self.formating_hash_tag(hash_tag)
                    if formated_hash_tag:
                        formated_hash_tag = "\n" + formated_hash_tag
                    """
                    指定した金額より低いとき値引きTweet
                    値引き時はずっと通知するように
                    値引き通知
                    """
                    if now_price_int < price:
                        self.tw.tweet(
                            f"({now_time()})\n＼{target_site}で値引きされました！／\n{title}"
                            + f"\n{now_price_str}\n{afili_url}{formated_hash_tag}"
                        )
                        print(
                            f"({now_time()})\n＼{target_site}で値引きされました！／\n{title}"
                            + f"\n{now_price_str}\n{afili_url}{formated_hash_tag}"
                        )
                        # 値引き後の金額に上書き
                        self.gs.update_cell(row_count, 4, now_price_int)
                    # is_buyableが0ならTweet(再入荷通知)
                    if is_buyable == 0:
                        self.tw.tweet(
                            f"({now_time()})\n＼{target_site}で再入荷中！／\n{title}"
                            + f"\n{afili_url}{formated_hash_tag}"
                        )
                        print(
                            f"({now_time()})\n＼{target_site}で再入荷中！／\n{title}"
                            + f"\n{afili_url}{formated_hash_tag}"
                        )
                        # 前回購入可を1にする
                        self.gs.update_cell(row_count, 5, 1)
                else:
                    self.gs.update_cell(row_count, 5, 0)
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
                bt.output_errors()
                print("==========")
            except Exception:
                pass
        bt.driver_quit()

if __name__ == "__main__":
    main()