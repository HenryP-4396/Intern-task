from config import DB_CONFIG
from baidu_hot_search_crawler import BaiduHotSearchCrawler
from douban_top100_crawler import DoubanTop100Crawler
from mysql_helper import MySqlHelper


class CrawlerApplication:
    def __init__(self) -> None:
        self.db = MySqlHelper(**DB_CONFIG)
        self.crawlers = [
            ("百度热搜", BaiduHotSearchCrawler(self.db)),
            ("豆瓣电影Top100", DoubanTop100Crawler(self.db)),
        ]

    def run(self) -> None:
        for name, crawler in self.crawlers:
            count = crawler.run()
            print(f"{name} 已保存 {count} 条")


if __name__ == "__main__":
    CrawlerApplication().run()
