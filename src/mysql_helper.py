from typing import Any, Iterable, Optional

import pymysql
from pymysql.cursors import DictCursor


class MySqlHelper:
    """Small helper class for common MySQL CRUD operations."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        charset: str = "utf8mb4",
    ) -> None:
        self.config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
            "charset": charset,
            "cursorclass": DictCursor,
            "autocommit": False,
        }

    def _connect(self):
        try:
            return pymysql.connect(**self.config)
        except pymysql.err.OperationalError as exc:
            if exc.args[0] != 1049:
                raise
            bootstrap_config = self.config.copy()
            database = bootstrap_config.pop("database")
            with pymysql.connect(**bootstrap_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        f"CREATE DATABASE IF NOT EXISTS `{database}` "
                        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                    )
                conn.commit()
            return pymysql.connect(**self.config)

    def query_one(self, sql: str, params: Optional[Iterable[Any]] = None) -> Optional[dict]:
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchone()

    def query_all(self, sql: str, params: Optional[Iterable[Any]] = None) -> list[dict]:
        with self._connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return list(cursor.fetchall())

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        with self._connect() as conn:
            try:
                with conn.cursor() as cursor:
                    row_count = cursor.execute(sql, params)
                conn.commit()
                return row_count
            except Exception:
                conn.rollback()
                raise

    def execute_many(self, sql: str, params_list: Iterable[Iterable[Any]]) -> int:
        with self._connect() as conn:
            try:
                with conn.cursor() as cursor:
                    row_count = cursor.executemany(sql, params_list)
                conn.commit()
                return row_count
            except Exception:
                conn.rollback()
                raise
