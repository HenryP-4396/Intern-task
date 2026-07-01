from config import DB_CONFIG
from baidu_hot_search_crawler import BaiduHotSearchCrawler
from mysql_helper import MySqlHelper


BaiduHotSearchSpider = BaiduHotSearchCrawler


if __name__ == "__main__":
    crawler = BaiduHotSearchCrawler(MySqlHelper(**DB_CONFIG))
    count = crawler.run()
    print(f"已保存百度热搜 {count} 条")
