from concurrent.futures import ThreadPoolExecutor
from time import sleep

from common.driver import Driver
from common.ggl_spreadsheet import Gspread
from common.tweet import Tweet

THREAD_COUNT = None


class BuyableTweet:
    def __init__(self) -> None:
        self.gs = Gspread()
        self.tw = Tweet()
        self.errors = []

    def buy_tweet(self) -> None:
        row_count = 0
        self.gs.fetch_sheet(0)
        with ThreadPoolExecutor(THREAD_COUNT) as executor:
            for (
                hash_tag,
                url,
                afili_url,
                is_buyable,
            ) in self.gs.worksheet.get_all_values():
                row_count += 1
                if row_count == 1:  # 一行目はカラム名なのでスルー
                    continue
                executor.submit(
                    self.tweet_decision,
                    hash_tag,
                    url,
                    afili_url,
                    int(is_buyable),
                    row_count,
                )
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
        #         int(is_buyable),
        #         row_count,
        #     )
        print(row_count)

    def fetch_platform(self, url: str) -> str:
        platform: str = ""
        if "item.rakuten" in url:
            platform = "SP"
        else:
            platform = "PC"
        return platform

    def convert_class(self, class_str: str) -> str:
        class_str = class_str.replace(" ", ".")
        class_str = "." + class_str
        return class_str

    def tweet_decision(
        self, hash_tag: str, url: str, afili_url: str, is_buyable: int, row_count: int
    ) -> None:
        try:
            platform = self.fetch_platform(url=url)
            driver = Driver(platform=platform)
            driver.get(url)
            print(driver.driver.title)
            sleep(3)
            is_buy: bool = False
            if "amazon" in url:
                target_site = "Amazon"
                title = driver.find_element_by_css_selector(
                    "#productTitle"
                ).text.replace("\n", "")
                if driver.find_elements_by_css_selector("#add-to-cart-button"):
                    is_buy = True
            elif "item.rakuten" in url:
                # selector = ".cart-button.add-cart.new-cart-button"
                target_site = "楽天市場"
                # title = driver.find_element_by_css_selector(
                #     ".item_name > b"
                # ).text.replace("\n", "")
                title = driver.find_element_by_css_selector(
                    ".section--1LTGf"
                ).text.replace("\n", "")
                cls = self.convert_class(
                    "button--3SNaj size-m--2eTK1 size-m-padding--1SMUk "
                    + "border-radius--1ip29 block--3qHE8 type-primary--3cgWx"
                )
                el = driver.find_element_by_css_selector(cls)
                if el.is_enabled():
                    is_buy = True

            elif "books.rakuten" in url:
                target_site = "楽天ブックス"
                title = driver.find_element_by_css_selector(
                    "#productTitle"
                ).text.replace("\n", "")
                if driver.find_elements_by_css_selector(".new_addToCart"):
                    is_buy = True
            else:
                return

            if is_buy:
                if is_buyable == 0:
                    formated_hash_tag = self.formating_hash_tag(hash_tag)
                    if formated_hash_tag:
                        formated_hash_tag = "\n" + formated_hash_tag
                    self.tw.tweet(
                        f"＼{target_site}で購入できます！／\n{title}"
                        + "\n{afili_url}{formated_hash_tag}"
                    )
                    print(
                        f"＼{target_site}で購入できます！／\n{title}"
                        + "\n{afili_url}{formated_hash_tag}"
                    )
                    self.gs.update_cell(row_count, 4, 1)
            else:
                self.gs.update_cell(row_count, 4, 0)
            print(f"{row_count}番目成功")
        except Exception:
            self.errors.append([f"{row_count}番目", url])
            print(f"{row_count}番目失敗")
            pass

        driver.quit()

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


def main():
    bt = BuyableTweet()
    bt.buy_tweet()
    bt.output_errors()


if __name__ == "__main__":
    main()
