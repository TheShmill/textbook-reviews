from flask import Flask, g, request
import sqlite3

app = Flask(__name__)

with sqlite3.connect("textbook-review.db") as conn:
    conn.executescript(open("tables.sql").read())


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("textbook-review.db")
    return db


@app.route("/search")
def search():
    query = request.args.get("query")
    hits = {}
    for word in query.split():
        matches = (
            get_db()
            .cursor()
            .execute(
                """
        select rowid
        from books
        where title like :word
        or edition like :word
        or author like :word
        or isbn like :word
        """,
                {"word": "%" + word + "%"},
            )
            .fetchall()
        )
        for match in matches:
            hits[match[0]] = 1 + hits.get(match[0], 0)

    results = []
    for hit in hits.items():
        results.append(hit)
    results.sort(key=lambda x: x[1], reverse=True)
    for i in range(len(results)):
        results[i] = results[i][0]
    return results


@app.route("/book/<int:book_id>/reviews")
def get_book_reviews(book_id):
    reviews = (
        get_db()
        .cursor()
        .execute(
            """select stars, IFNULL(displayname, username), count(likes.rowid), comment
            from reviews
            left join likes on likes.reviewid = reviews.rowid
            inner join users on users.rowid = reviews.userid
            where reviews.bookid = ?
            group by reviews.rowid""",
            (book_id,),
        )
        .fetchall()
    )
    if reviews == []:
        return {"error": "Book not found"}
    return [
        {
            "stars": review[0],
            "name": review[1],
            "likes": review[2],
            "comment": review[3],
        }
        for review in reviews
    ]


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
        "reviews": get_book_reviews(book_id),
    }


@app.route("/user/<int:user_id>")
def get_user(user_id):
    print(type(user_id))
    user_cursor = (
        get_db()
        .cursor()
        .execute(
            "SELECT username, displayname FROM users WHERE rowid = ?",
            (user_id,),
        )
        .fetchone()
    )
    reviews_cursor = (
        get_db()
        .cursor()
        .execute(
            "SELECT stars, bookid, userid, comment FROM reviews WHERE userid = ?",
            (user_id,),
        )
        .fetchall()
    )
    if user_cursor is None:
        return {"error": "Book not found"}

    res = []
    res.append({"username": user_cursor[0], "displayname": user_cursor[1]})
    x = 0
    while x < len(reviews_cursor):
        res.append(
            {
                "star": reviews_cursor[x][0],
                "bookid": reviews_cursor[x][1],
                "userid": reviews_cursor[x][2],
                "comment": reviews_cursor[x][3],
            }
        )
        x += 1
    return res
