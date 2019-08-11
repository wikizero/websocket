import sqlite3


class DBHelper():
    def __init__(self):
        self.conn = sqlite3.connect('data.db')
        self.cursor = self.conn.cursor()

        # 如果不存在表则创建表
        self.create_table()

    def create_table(self):
        sql = '''
            CREATE TABLE IF NOT EXISTS data(
            `id` integer,
            `alias` varchar(20),  
            `from` varchar(20) NOT NULL,  
            `datetime` TIMESTAMP default (datetime('now', 'localtime')),
            `type` varchar(10) NOT NULL,
            `content` text NOT NULL,
            PRIMARY KEY (id));
        '''
        self.cursor.execute(sql)

    def insert(self, val):
        # sql = f"INSERT INTO DATA (`alias`, `from`, `type`, `content`) VALUES ({str(val)[1:-1]});"
        sql = f"INSERT INTO DATA (`alias`, `from`, `type`, `content`) VALUES (?, ?, ?, ?);"
        res = self.cursor.execute(sql, val)
        self.conn.commit()
        print(f"Insert into data, {res.rowcount} rows effected!")
        return res.lastrowid

    def select(self, limit=10):
        columns = ['id', 'alias', 'from', 'datetime', 'type', 'content']
        sql = f"SELECT * FROM DATA ORDER BY ID DESC LIMIT {limit};"
        res = self.cursor.execute(sql)
        return [dict(zip(columns, row)) for row in res.fetchall()]

    def select_by_id(self, _id):
        columns = ['id', 'alias', 'from', 'datetime', 'type', 'content']
        sql = f"SELECT * FROM DATA WHERE id={_id};"
        res = self.cursor.execute(sql)
        return dict(zip(columns, res.fetchall()[0]))

    def close(self):
        self.cursor.close()


if __name__ == '__main__':
    db = DBHelper()
    lst = [None, '127.0.0.1', 'type', 'paste']
    # db.insert(lst)
    print(db.select())
