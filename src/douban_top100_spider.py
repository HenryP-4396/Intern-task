import re
from datetime import date
from time import sleep

import requests
from bs4 import BeautifulSoup

from config import DB_CONFIG
from mysql_helper import MySqlHelper


class DoubanTop100Spider:
    def __init__(self, db: MySqlHelper) -> None:
        self.db = db
        self.base_url = "https://movie.douban.com/top250"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            )
        }

    def create_table(self) -> None:
        self.db.execute(
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

    def fetch_page(self, start: int) -> str:
        response = requests.get(
            self.base_url,
            params={"start": start, "filter": ""},
            headers=self.headers,
            timeout=10,
        )
        response.raise_for_status()
        return response.text

    def parse_movie(self, item) -> dict:
        rank_no = int(item.select_one(".pic em").get_text(strip=True))
        title_nodes = item.select(".hd .title")
        title = title_nodes[0].get_text(strip=True)
        original_title = self._parse_original_title(title_nodes)
        detail_url = item.select_one(".hd a").get("href", "")
        poster_url = item.select_one(".pic img").get("src", "")
        rating = float(item.select_one(".rating_num").get_text(strip=True))
        rating_count = self._parse_rating_count(item)
        quote = self._parse_quote(item)
        directors, actors, release_year, country, genre = self._parse_movie_info(item)

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

    def parse_page(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        return [self.parse_movie(item) for item in soup.select(".grid_view .item")]

    def fetch_movies(self) -> list[dict]:
        movies = []
        for start in range(0, 100, 25):
            movies.extend(self.parse_page(self.fetch_page(start)))
            sleep(1)
        return movies[:100]

    def save_movies(self, movies: list[dict]) -> None:
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
        self.db.execute_many(sql, params)

    def run(self) -> int:
        self.create_table()
        movies = self.fetch_movies()
        self.save_movies(movies)
        return len(movies)

    def _parse_original_title(self, title_nodes) -> str | None:
        if len(title_nodes) <= 1:
            return None
        return title_nodes[1].get_text(strip=True).replace("/", "").strip()

    def _parse_rating_count(self, item) -> int | None:
        star_texts = [span.get_text(strip=True) for span in item.select(".bd div span")]
        rating_text = next((text for text in star_texts if "评价" in text), "")
        rating_count_match = re.search(r"(\d+)", rating_text.replace(",", ""))
        return int(rating_count_match.group(1)) if rating_count_match else None

    def _parse_quote(self, item) -> str | None:
        quote_node = item.select_one(".quote .inq, .quote span")
        return quote_node.get_text(strip=True) if quote_node else None

    def _parse_movie_info(self, item) -> tuple[str | None, str | None, int | None, str | None, str | None]:
        info_lines = [
            line.strip()
            for line in item.select_one(".bd p").get_text("\n", strip=True).split("\n")
        ]
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
        return directors, actors, release_year, country, genre


if __name__ == "__main__":
    spider = DoubanTop100Spider(MySqlHelper(**DB_CONFIG))
    count = spider.run()
    print(f"已保存豆瓣电影 Top{count}")
