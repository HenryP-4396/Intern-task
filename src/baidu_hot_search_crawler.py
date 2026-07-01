from datetime import date

from bs4 import BeautifulSoup

from base_crawler import BaseCrawler
from config import DB_CONFIG
from mysql_helper import MySqlHelper


class BaiduHotSearchCrawler(BaseCrawler):
    def __init__(self, db: MySqlHelper) -> None:
        super().__init__(db)
        self.url = "https://top.baidu.com/board?tab=realtime"

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

    def crawl(self) -> list[tuple[int, str, int | None, str]]:
        html = self.fetch_html(self.url)
        return self.parse_items(html)

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

    def save(self, items: list[tuple[int, str, int | None, str]]) -> None:
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


if __name__ == "__main__":
    crawler = BaiduHotSearchCrawler(MySqlHelper(**DB_CONFIG))
    count = crawler.run()
    print(f"已保存百度热搜 {count} 条")
