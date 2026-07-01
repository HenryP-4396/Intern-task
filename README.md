# MySQL + Python 爬虫实习任务

本目录包含实习任务要求对应的 SQL 和 Python 示例：

- 使用命令行创建学生表，并演示增删改查。
- 编写 `MySqlHelper` 类，封装 MySQL 查询、执行和批量执行。
- 使用面向对象方式爬取百度热搜 Top10，并存入 MySQL。
- 使用面向对象方式爬取豆瓣电影 Top100，并按可视化展示需要设计字段后存入 MySQL。

## 1. 安装 MySQL 并创建数据库

先启动 MySQL，然后在命令行执行：

```bash
mysql -uroot -p
```

进入 MySQL 后执行：

```sql
SOURCE sql/01_student.sql;
SOURCE sql/02_hot_search.sql;
SOURCE sql/03_douban_movies.sql;
```

如果 `SOURCE` 找不到文件，可以复制 SQL 文件内容到 MySQL 命令行执行。

## 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

默认数据库配置在 `src/config.py`：

```python
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root123
MYSQL_DATABASE=python_mysql_homework
```

如果你的 MySQL 密码不是 `root123`，可以修改 `src/config.py`，也可以在命令行设置环境变量。
首次运行时，如果 `python_mysql_homework` 数据库不存在，程序会自动创建。

## 3. 运行学生表增删改查示例

```bash
python src/student_demo.py
```

运行后会通过 `StudentCrudDemo` 类创建 `students` 表，插入 3 条学生记录，修改张三身高，删除王五，再查询剩余学生。

## 4. 运行百度热搜爬虫

```bash
python src/baidu_hot_search_spider.py
```

爬虫类：`BaiduHotSearchSpider`

入库表：`baidu_hot_search`

适合可视化的字段：

- `rank_no`：排名，可做柱状图排序。
- `keyword`：热搜词，可做标签或词云。
- `hot_score`：热度，可做热度柱状图。
- `crawl_date`：爬取日期，可做趋势分析。

## 5. 运行豆瓣电影 Top100 爬虫

```bash
python src/douban_top100_spider.py
```

爬虫类：`DoubanTop100Spider`

入库表：`douban_movies`

适合可视化的字段：

- `rank_no`：排名。
- `title`：电影名。
- `rating`：评分，可做评分分布图。
- `rating_count`：评价人数，可做热度对比。
- `release_year`：上映年份，可做年代分布。
- `country`：国家/地区，可做地区统计。
- `genre`：电影类型，可做类型占比。
- `poster_url`：海报图，可用于前端卡片展示。

## 6. MySqlHelper 设计思路

从使用者角度看，常见需求只有三类：

1. 查询一条数据：`query_one(sql, params)`
2. 查询多条数据：`query_all(sql, params)`
3. 执行增删改：`execute(sql, params)`
4. 批量执行：`execute_many(sql, params_list)`

所有方法都支持参数化 SQL，例如：

```python
db.execute(
    "UPDATE students SET height = %s WHERE student_no = %s",
    (172.0, "S001"),
)
```

这样既方便调用，也能避免直接拼接字符串带来的 SQL 注入问题。

百度热搜、豆瓣电影和学生表演示都采用类封装，入口文件只负责创建对象并调用 `run()` 方法。
