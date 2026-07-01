from config import DB_CONFIG
from mysql_helper import MySqlHelper


class StudentCrudDemo:
    def __init__(self, db: MySqlHelper) -> None:
        self.db = db

    def create_table(self) -> None:
        self.db.execute(
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

    def reset_data(self) -> None:
        self.db.execute("DELETE FROM students")

    def insert_students(self) -> None:
        self.db.execute_many(
            "INSERT INTO students (student_no, name, height) VALUES (%s, %s, %s)",
            [
                ("S001", "张三", 170.5),
                ("S002", "李四", 165.0),
                ("S003", "王五", 178.2),
            ],
        )

    def update_student(self) -> None:
        self.db.execute(
            "UPDATE students SET height = %s WHERE student_no = %s",
            (172.0, "S001"),
        )

    def delete_student(self) -> None:
        self.db.execute("DELETE FROM students WHERE student_no = %s", ("S003",))

    def query_students(self) -> list[dict]:
        return self.db.query_all(
            "SELECT student_no, name, height FROM students ORDER BY height DESC"
        )

    def run(self) -> list[dict]:
        self.create_table()
        self.reset_data()
        self.insert_students()
        self.update_student()
        self.delete_student()
        return self.query_students()


if __name__ == "__main__":
    demo = StudentCrudDemo(MySqlHelper(**DB_CONFIG))
    for row in demo.run():
        print(row)
