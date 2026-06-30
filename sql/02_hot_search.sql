USE python_mysql_homework;

CREATE TABLE IF NOT EXISTS baidu_hot_search (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
  rank_no INT NOT NULL COMMENT '热搜排名',
  keyword VARCHAR(255) NOT NULL COMMENT '热搜关键词',
  hot_score INT DEFAULT NULL COMMENT '热度值',
  url VARCHAR(500) DEFAULT NULL COMMENT '详情链接',
  source VARCHAR(30) NOT NULL DEFAULT 'baidu' COMMENT '数据来源',
  crawl_date DATE NOT NULL COMMENT '爬取日期',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
  UNIQUE KEY uk_source_date_rank (source, crawl_date, rank_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='百度热搜Top10';
