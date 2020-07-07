import pymysql

db = 'CentDB'


class SqlHelper(object):
    def __init__(self):
        self.connect()

    def connect(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='smile0217',use_unicode=True, db=db, charset='utf8')
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def get_list(self, sql, args):
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    def get_one(self, sql, args):
        self.cursor.execute(sql, args)
        return self.cursor.fetchone()

    def modify(self, sql, args):
        self.cursor.execute(sql, args)
        self.conn.commit()

    def multipleModify(self, sql, args):
        self.cursor.executemany(sql, args)
        self.conn.commit()

    def creat(self, sql, args):
        self.cursor.execute(sql, args)
        self.conn.commit()
        return self.cursor.lastrowid

    def close(self):
        self.cursor.close()
        self.conn.close()

