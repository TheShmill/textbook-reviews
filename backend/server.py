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


@app.route("/book/<int:book_id>/reviews")
def get_book_reviews(book_id):
    reviews = (
        get_db()
        .cursor()
        .execute(
            "SELECT stars, comment, userid FROM reviews WHERE bookid=?", (book_id,)
        )
        .fetchall()
    )
    data = []
    for review in reviews:
        stars = review[0]
        comment = review[1]
        userid = review[2]
        user = (
            get_db()
            .cursor()
            .execute("SELECT username, displayname FROM users WHERE rowid=?", (userid,))
            .fetchone()
        )
        if user[1]:
            name = user[1]
        else:
            name = user[0]
        print(name)
        data.append({"stars": stars, "comment": comment, "name": name})
    return data


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
    if cursor is None:
        return {"error": "Book not found"}
    return {
        "title": cursor[0],
        "author": cursor[1],
        "year": cursor[2],
        "edition": cursor[3],
        "isbn": cursor[4],
    }
