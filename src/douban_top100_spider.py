import re
from datetime import date
from time import sleep

import requests
from bs4 import BeautifulSoup

from config import DB_CONFIG
from mysql_helper import MySqlHelper


def create_table(db: MySqlHelper) -> None:
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS douban_movies (
          id INT PRIMARY KEY AUTO_INCREMENT,
          rank_no INT NOT NULL,
          title VARCHAR(255) NOT NULL,
          original_title VARCHAR(255) DEFAULT NULL,
          rating DECIMAL(3, 1) DEFAULT NULL,
          rating_count INT DEFAULT NULL,
          quote VARCHAR(500) DEFAULT NULL,
          directors VARCHAR(255) DEFAULT NULL,
          actors VARCHAR(500) DEFAULT NULL,
          release_year INT DEFAULT NULL,
          country VARCHAR(255) DEFAULT NULL,
          genre VARCHAR(255) DEFAULT NULL,
          detail_url VARCHAR(500) DEFAULT NULL,
          poster_url VARCHAR(500) DEFAULT NULL,
          crawl_date DATE NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          UNIQUE KEY uk_rank_date (rank_no, crawl_date),
          KEY idx_rating (rating),
          KEY idx_release_year (release_year),
          KEY idx_genre (genre)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )


def parse_movie(item) -> dict:
    rank_no = int(item.select_one(".pic em").get_text(strip=True))
    title_nodes = item.select(".hd .title")
    title = title_nodes[0].get_text(strip=True)
    original_title = title_nodes[1].get_text(strip=True).replace("/", "").strip() if len(title_nodes) > 1 else None
    detail_url = item.select_one(".hd a").get("href", "")
    poster_url = item.select_one(".pic img").get("src", "")
    rating = float(item.select_one(".rating_num").get_text(strip=True))

    rating_text = item.select_one(".star span:last-child").get_text(strip=True)
    rating_count_match = re.search(r"(\d+)", rating_text.replace(",", ""))
    rating_count = int(rating_count_match.group(1)) if rating_count_match else None

    quote_node = item.select_one(".quote .inq")
    quote = quote_node.get_text(strip=True) if quote_node else None

    info_lines = [line.strip() for line in item.select_one(".bd p").get_text("\n", strip=True).split("\n")]
    people_line = info_lines[0] if info_lines else ""
    meta_line = info_lines[1] if len(info_lines) > 1 else ""

    director_match = re.search(r"导演:\s*([^主演]+)", people_line)
    actor_match = re.search(r"主演:\s*(.*)", people_line)
    directors = director_match.group(1).strip() if director_match else None
    actors = actor_match.group(1).strip() if actor_match else None

    meta_parts = [part.strip() for part in meta_line.split("/") if part.strip()]
    release_year = int(meta_parts[0]) if meta_parts and meta_parts[0].isdigit() else None
    country = meta_parts[1] if len(meta_parts) > 1 else None
    genre = meta_parts[2] if len(meta_parts) > 2 else None

    return {
        "rank_no": rank_no,
        "title": title,
        "original_title": original_title,
        "rating": rating,
        "rating_count": rating_count,
        "quote": quote,
        "directors": directors,
        "actors": actors,
        "release_year": release_year,
        "country": country,
        "genre": genre,
        "detail_url": detail_url,
        "poster_url": poster_url,
    }


def fetch_douban_top100() -> list[dict]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        )
    }
    movies = []
    for start in range(0, 100, 25):
        url = f"https://movie.douban.com/top250?start={start}&filter="
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        for item in soup.select(".grid_view .item"):
            movies.append(parse_movie(item))
        sleep(1)
    return movies[:100]


def save_movies(db: MySqlHelper, movies: list[dict]) -> None:
    sql = """
        INSERT INTO douban_movies (
          rank_no, title, original_title, rating, rating_count, quote,
          directors, actors, release_year, country, genre,
          detail_url, poster_url, crawl_date
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          title = VALUES(title),
          original_title = VALUES(original_title),
          rating = VALUES(rating),
          rating_count = VALUES(rating_count),
          quote = VALUES(quote),
          directors = VALUES(directors),
          actors = VALUES(actors),
          release_year = VALUES(release_year),
          country = VALUES(country),
          genre = VALUES(genre),
          detail_url = VALUES(detail_url),
          poster_url = VALUES(poster_url)
    """
    today = date.today()
    params = [
        (
            movie["rank_no"],
            movie["title"],
            movie["original_title"],
            movie["rating"],
            movie["rating_count"],
            movie["quote"],
            movie["directors"],
            movie["actors"],
            movie["release_year"],
            movie["country"],
            movie["genre"],
            movie["detail_url"],
            movie["poster_url"],
            today,
        )
        for movie in movies
    ]
    db.execute_many(sql, params)


def main() -> None:
    db = MySqlHelper(**DB_CONFIG)
    create_table(db)
    movies = fetch_douban_top100()
    save_movies(db, movies)
    print(f"已保存豆瓣电影 Top{len(movies)}")


if __name__ == "__main__":
    main()
