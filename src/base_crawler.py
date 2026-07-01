from abc import ABC, abstractmethod
from time import sleep
from typing import Any

import requests

from mysql_helper import MySqlHelper


class BaseCrawler(ABC):
    def __init__(self, db: MySqlHelper, sleep_seconds: float = 0) -> None:
        self.db = db
        self.sleep_seconds = sleep_seconds
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            )
        }

    def fetch_html(self, url: str, params: dict | None = None) -> str:
        response = requests.get(url, params=params, headers=self.headers, timeout=10)
        response.raise_for_status()
        if self.sleep_seconds > 0:
            sleep(self.sleep_seconds)
        return response.text

    def run(self) -> int:
        self.create_table()
        items = self.crawl()
        self.save(items)
        return len(items)

    @abstractmethod
    def create_table(self) -> None:
        pass

    @abstractmethod
    def crawl(self) -> list[Any]:
        pass

    @abstractmethod
    def save(self, items: list[Any]) -> None:
        pass
