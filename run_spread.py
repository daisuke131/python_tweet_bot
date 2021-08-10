from concurrent.futures import ThreadPoolExecutor

from gspread.models import Worksheet

from common.beutifulsoup import fetch_soup
from common.ggl_spreadsheet import Gspread
from common.tweet import Tweet

THREAD_COUNT = None


class BuyableTweet:
    def __init__(self, ws: Worksheet) -> None:
        self.ws: Worksheet = ws
        self.tw = Tweet()

    def buy_tweet(self):
        row_count = 0
        with ThreadPoolExecutor(THREAD_COUNT) as executor:
            for hash_tag, url, afili_url, is_buyable in self.ws.get_all_values():
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
        print(row_count)

    def tweet_decision(
        self, hash_tag: str, url: str, afili_url: str, is_buyable: int, row_count: int
    ) -> None:
        try:
            soup = fetch_soup(url)
            if "amazon" in url:
                selector = "#add-to-cart-button"
                platform = "Amazon"
                title = soup.select_one("#productTitle").get_text().replace("\n", "")
            elif "item.rakuten" in url:
                selector = ".cart-button.add-cart.new-cart-button"
                platform = "楽天市場"
                title = soup.select_one(".item_name > b").get_text().replace("\n", "")
            elif "books.rakuten" in url:
                selector = ".new_addToCart"
                platform = "楽天ブックス"
                title = soup.select_one("#productTitle").get_text().replace("\n", "")
            else:
                return

            if soup.select(selector):
                if is_buyable == 0:
                    formated_hash_tag = self.formating_hash_tag(hash_tag)
                    if formated_hash_tag:
                        formated_hash_tag = "\n" + formated_hash_tag
                    self.tw.tweet(
                        f"＼{platform}で購入できます！／\n{title}\n{afili_url}{formated_hash_tag}"
                    )
                    print(
                        f"＼{platform}で購入できます！／\n{title}\n{afili_url}{formated_hash_tag}"
                    )
                    self.ws.update_cell(row_count, 4, 1)
            else:
                if is_buyable == 1:
                    self.ws.update_cell(row_count, 4, 0)
        except Exception:
            print(f"{row_count}番目失敗")
            pass

    def formating_hash_tag(self, hash_tag: str) -> str:
        hash_tag_list = hash_tag.split()
        if not hash_tag_list:
            return ""
        new_hash_tag_list = []
        for s in hash_tag_list:
            new_hash_tag_list.append("#" + s)
        return " ".join(new_hash_tag_list)


def main():
    gs = Gspread()
    ws: Worksheet = gs.read_sheet(0)
    bt = BuyableTweet(ws)
    bt.buy_tweet()


if __name__ == "__main__":
    main()
