import sqlite3
from io import StringIO

class SQLReader(object):
    """Wrapper around an in-memory SQLite database"""
    def __init__(self, db_path):
        # open in read-only mode just to be sure
        conn = sqlite3.connect('file:{}?mode=ro'.format(db_path),
                                    check_same_thread=False, uri=True)
        tempfile = StringIO()

        for line in conn.iterdump():
            tempfile.write('{}\n'.format(line))

        conn.close()
        tempfile.seek(0)

        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        self.cursor = self.conn.cursor()

        # copy the old database
        self.cursor.executescript(tempfile.read())
        self.conn.commit()

    def fetch_one(self, query, *args):
        self.cursor.execute(query, *args)
        return self.cursor.fetchone()

    def fetch_all(self, query, *args):
        self.cursor.execute(query, *args)
        return self.cursor.fetchall()

    def fetch_iterator(self, query, *args):
        return self.cursor.execute(query, *args)
