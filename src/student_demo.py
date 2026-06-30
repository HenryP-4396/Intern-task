from config import DB_CONFIG
from mysql_helper import MySqlHelper


def main() -> None:
    db = MySqlHelper(**DB_CONFIG)

    db.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
          id INT PRIMARY KEY AUTO_INCREMENT,
          student_no VARCHAR(20) NOT NULL UNIQUE,
          name VARCHAR(50) NOT NULL,
          height DECIMAL(4, 1) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )

    db.execute("DELETE FROM students")

    db.execute_many(
        "INSERT INTO students (student_no, name, height) VALUES (%s, %s, %s)",
        [
            ("S001", "张三", 170.5),
            ("S002", "李四", 165.0),
            ("S003", "王五", 178.2),
        ],
    )

    db.execute(
        "UPDATE students SET height = %s WHERE student_no = %s",
        (172.0, "S001"),
    )
    db.execute("DELETE FROM students WHERE student_no = %s", ("S003",))

    rows = db.query_all("SELECT student_no, name, height FROM students ORDER BY height DESC")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
