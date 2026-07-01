from datetime import date

import requests
from bs4 import BeautifulSoup

from config import DB_CONFIG
from mysql_helper import MySqlHelper


class BaiduHotSearchSpider:
    def __init__(self, db: MySqlHelper) -> None:
        self.db = db
        self.url = "https://top.baidu.com/board?tab=realtime"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            )
        }

    def create_table(self) -> None:
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS baidu_hot_search (
              id INT PRIMARY KEY AUTO_INCREMENT,
              rank_no INT NOT NULL,
              keyword VARCHAR(255) NOT NULL,
              hot_score INT DEFAULT NULL,
              url VARCHAR(500) DEFAULT NULL,
              source VARCHAR(30) NOT NULL DEFAULT 'baidu',
              crawl_date DATE NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              UNIQUE KEY uk_source_date_rank (source, crawl_date, rank_no)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )

    def fetch_html(self) -> str:
        response = requests.get(self.url, headers=self.headers, timeout=10)
        response.raise_for_status()
        return response.text

    def parse_items(self, html: str) -> list[tuple[int, str, int | None, str]]:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        cards = soup.select(".category-wrap_iQLoo, .category-wrap")

        for index, card in enumerate(cards[:10], start=1):
            title_node = card.select_one(".c-single-text-ellipsis, .content_1YWBm a")
            score_node = card.select_one(".hot-index_1Bl1a, .hot-index")
            link_node = card.select_one("a")
            keyword = title_node.get_text(strip=True) if title_node else ""
            score_text = score_node.get_text(strip=True).replace(",", "") if score_node else ""
            hot_score = int(score_text) if score_text.isdigit() else None
            detail_url = link_node.get("href", "") if link_node else ""
            if keyword:
                items.append((index, keyword, hot_score, detail_url))

        if not items:
            raise RuntimeError("没有解析到百度热搜数据，可能是页面结构变化或触发了反爬。")
        return items

    def save_items(self, items: list[tuple[int, str, int | None, str]]) -> None:
        sql = """
            INSERT INTO baidu_hot_search (rank_no, keyword, hot_score, url, crawl_date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              keyword = VALUES(keyword),
              hot_score = VALUES(hot_score),
              url = VALUES(url)
        """
        today = date.today()
        params = [(rank, keyword, score, url, today) for rank, keyword, score, url in items]
        self.db.execute_many(sql, params)

    def run(self) -> int:
        self.create_table()
        items = self.parse_items(self.fetch_html())
        self.save_items(items)
        return len(items)


if __name__ == "__main__":
    spider = BaiduHotSearchSpider(MySqlHelper(**DB_CONFIG))
    count = spider.run()
    print(f"已保存百度热搜 {count} 条")
