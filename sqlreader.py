import sqlite3


class SQLReader(object):
    def __init__(self, db_path):
        # open in read-only mode just to be sure
        self.conn = sqlite3.connect('file:{}?mode=ro'.format(db_path),
                                    check_same_thread=False, uri=True)
        self.cursor = self.conn.cursor()

    def fetch_one(self, query, *args):
        self.cursor.execute(query, *args)
        return self.cursor.fetchone()

    def fetch_all(self, query, *args):
        self.cursor.execute(query, *args)
        return self.cursor.fetchall()

    def fetch_iterator(self, query, *args):
        return self.cursor.execute(query, *args)
