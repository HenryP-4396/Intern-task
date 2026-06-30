CREATE DATABASE IF NOT EXISTS python_mysql_homework
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE python_mysql_homework;

DROP TABLE IF EXISTS students;

CREATE TABLE students (
  id INT PRIMARY KEY AUTO_INCREMENT COMMENT '学生编号',
  student_no VARCHAR(20) NOT NULL UNIQUE COMMENT '学号',
  name VARCHAR(50) NOT NULL COMMENT '姓名',
  height DECIMAL(4, 1) NOT NULL COMMENT '身高，单位cm',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生表';

INSERT INTO students (student_no, name, height) VALUES
('S001', '张三', 170.5),
('S002', '李四', 165.0),
('S003', '王五', 178.2);

SELECT * FROM students;

UPDATE students
SET height = 172.0
WHERE student_no = 'S001';

DELETE FROM students
WHERE student_no = 'S003';

SELECT id, student_no, name, height
FROM students
ORDER BY height DESC;
