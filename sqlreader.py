import sqlite3
from flask import g

db_path = 'static/kanji.db'

def get_cursor(g):
    db = getattr(g, '_database', None)
    if not db:
        db = g._database = sqlite3.connect(db_path)

    return db.cursor()


def fetch_one(query, *args):
    cursor = get_cursor(g)
    cursor.execute(query, *args)
    return cursor.fetchone()


def fetch_all(query, *args):
    cursor = get_cursor(g)
    cursor.execute(query, *args)
    return cursor.fetchall()


def fetch_iterator(query, *args):
    cursor = get_cursor(g)
    return cursor.execute(query, *args)

def db_commit(query, *args):
    db = getattr(g, '_database', None)
    if not db:
        db = g._database = sqlite3.connect(db_path)

    cursor = db.cursor()
    cursor.execute(query, *args)
    db.commit()