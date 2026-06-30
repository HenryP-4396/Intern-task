USE python_mysql_homework;

CREATE TABLE IF NOT EXISTS douban_movies (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  rank_no INT NOT NULL COMMENT '豆瓣排名',
  title VARCHAR(255) NOT NULL COMMENT '电影名称',
  original_title VARCHAR(255) DEFAULT NULL COMMENT '原始片名',
  rating DECIMAL(3, 1) DEFAULT NULL COMMENT '豆瓣评分',
  rating_count INT DEFAULT NULL COMMENT '评价人数',
  quote VARCHAR(500) DEFAULT NULL COMMENT '短评/引言',
  directors VARCHAR(255) DEFAULT NULL COMMENT '导演',
  actors VARCHAR(500) DEFAULT NULL COMMENT '主演',
  release_year INT DEFAULT NULL COMMENT '上映年份',
  country VARCHAR(255) DEFAULT NULL COMMENT '国家/地区',
  genre VARCHAR(255) DEFAULT NULL COMMENT '类型',
  detail_url VARCHAR(500) DEFAULT NULL COMMENT '豆瓣详情链接',
  poster_url VARCHAR(500) DEFAULT NULL COMMENT '海报链接',
  crawl_date DATE NOT NULL COMMENT '爬取日期',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  UNIQUE KEY uk_rank_date (rank_no, crawl_date),
  KEY idx_rating (rating),
  KEY idx_release_year (release_year),
  KEY idx_genre (genre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='豆瓣电影Top100';
