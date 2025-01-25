from flask import Flask, g
import sqlite3

app = Flask(__name__)

with sqlite3.connect("textbook-review.db") as conn:
    conn.executescript(open("tables.sql").read())


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("textbook-review.db")
    return db


@app.route("/book/<int:book_id>")
def get_book(book_id):
    print(type(book_id))
    cursor = (
        get_db()
        .cursor()
        .execute(
            "SELECT title, author, year, edition, isbn FROM books WHERE rowid = ?",
            (book_id,),
        )
        .fetchone()
    )
    return {
        "title": cursor[0],
        "author": cursor[1],
        "year": cursor[2],
        "edition": cursor[3],
        "isbn": cursor[4],
    }
