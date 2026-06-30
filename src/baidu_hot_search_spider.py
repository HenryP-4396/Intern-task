from datetime import date

import requests
from bs4 import BeautifulSoup

from config import DB_CONFIG
from mysql_helper import MySqlHelper


def create_table(db: MySqlHelper) -> None:
    db.execute(
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


def fetch_baidu_top10() -> list[tuple[int, str, int | None, str]]:
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
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
            results.append((index, keyword, hot_score, detail_url))

    if not results:
        raise RuntimeError("没有解析到百度热搜数据，可能是页面结构变化或触发了反爬。")
    return results


def save_items(db: MySqlHelper, items: list[tuple[int, str, int | None, str]]) -> None:
    sql = """
        INSERT INTO baidu_hot_search (rank_no, keyword, hot_score, url, crawl_date)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          keyword = VALUES(keyword),
          hot_score = VALUES(hot_score),
          url = VALUES(url)
    """
    today = date.today()
    db.execute_many(sql, [(rank, keyword, score, url, today) for rank, keyword, score, url in items])


def main() -> None:
    db = MySqlHelper(**DB_CONFIG)
    create_table(db)
    items = fetch_baidu_top10()
    save_items(db, items)
    print(f"已保存百度热搜 {len(items)} 条")


if __name__ == "__main__":
    main()
