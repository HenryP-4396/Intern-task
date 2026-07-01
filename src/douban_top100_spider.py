from config import DB_CONFIG
from douban_top100_crawler import DoubanTop100Crawler
from mysql_helper import MySqlHelper


DoubanTop100Spider = DoubanTop100Crawler


if __name__ == "__main__":
    crawler = DoubanTop100Crawler(MySqlHelper(**DB_CONFIG))
    count = crawler.run()
    print(f"已保存豆瓣电影 Top{count}")
