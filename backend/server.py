from flask import Flask, g, request, make_response, redirect
from jinja2 import Environment, PackageLoader, select_autoescape
import sqlite3

app = Flask(__name__)
env = Environment(loader=PackageLoader("server"), autoescape=select_autoescape())

with sqlite3.connect("textbook-review.db") as conn:
    conn.executescript(open("tables.sql").read())


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect("textbook-review.db")
    return db


@app.route("/")
def index():
    return env.get_template("index.html").render(user=user())


@app.route("/login")
def login():
    return env.get_template("login.html").render()


@app.route("/logged-in")
def logged_in():
    username = request.args.get("username")
    displayname = request.args.get("display")
    url = request.args.get("url")
    user = (
        get_db()
        .cursor()
        .execute(
            """
    SELECT * FROM users
    WHERE username=?
    """,
            (username,),
        )
        .fetchone()
    )
    if not user:
        db = get_db()
        db.cursor().execute(
            """
            INSERT INTO users VALUES (?, ?, ?)""",
            (username, displayname, url),
        )
        db.commit()
    resp = make_response(redirect("/"))
    resp.set_cookie("username", username)
    return resp


@app.route("/signout")
def signout():
    resp = make_response(redirect("/"))
    resp.delete_cookie("username")
    return resp


class User:
    def __init__(self, id, user, display, pfp):
        self.id = id
        self.user = user
        self.display = display
        self.pfp = pfp


def user():
    name = request.cookies.get("username")
    if name is None:
        return None
    user = (
        get_db()
        .cursor()
        .execute(
            "SELECT rowid, username, displayname, profilepicture FROM users WHERE username=?",
            (name,),
        )
        .fetchone()
    )
    return User(user[0], user[1], user[2], user[3])


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
        select books.rowid, title, edition, author, IFNULL(AVG(stars), "-")
        from books
        left join reviews on reviews.bookid = books.rowid
        where title like :word
        or edition like :word
        or author like :word
        or isbn like :word
        group by books.rowid
        """,
                {"word": "%" + word + "%"},
            )
            .fetchall()
        )
        for match in matches:
            hits[match[0]] = (
                1 + hits.get(match[0], [0])[0],
                {
                    "bookid": match[0],
                    "title": match[1],
                    "edition": match[2],
                    "author": match[3],
                    "rating": match[4],
                },
            )

    results = []
    for hit in hits.items():
        results.append(hit)
    results.sort(key=lambda x: x[1][0], reverse=True)
    for i in range(len(results)):
        results[i] = results[i][1][1]
    return env.get_template("searchres.html").render(books=results, user=user())


def get_book_reviews(book_id):
    reviews = (
        get_db()
        .cursor()
        .execute(
            """select stars, IFNULL(displayname, username), COUNT(likes.rowid), comment
            from reviews
            left join likes on likes.reviewid = reviews.rowid
            inner join users on users.rowid = reviews.userid
            where reviews.bookid = ?
            group by reviews.rowid""",
            (book_id,),
        )
        .fetchall()
    )
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
    book = (
        get_db()
        .cursor()
        .execute(
            """
            SELECT title, author, year, edition, isbn, AVG(stars), books.rowid
            FROM books
            LEFT JOIN reviews
            ON books.rowid = reviews.bookid
            WHERE books.rowid = ?
            GROUP BY books.rowid
            """,
            (book_id,),
        )
        .fetchone()
    )

    if book is None:
        return {"error": "Book not found"}
    return env.get_template("bookpage.html").render(
        user=user(),
        bookid=book_id,
        title=book[0],
        author=book[1],
        year=book[2],
        edition=book[3],
        isbn=book[4],
        stars=book[5],
        reviews=get_book_reviews(book_id),
    )


@app.route("/user/<int:user_id>")
def get_user(user_id):
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


@app.route("/book/<int:book_id>/review/")
def new_review(book_id):
    stars = int(request.args.get("stars"))
    comment = request.args.get("comment")
    if comment == "":
        comment = None
    print(stars, comment.__repr__())
    cursor = get_db().execute(
        """
            INSERT INTO reviews(userid, stars, bookid, comment)
            VALUES (?, ?, ?, ?) 
            """,
        (user().id, stars, book_id, comment),
    )
    get_db().commit()
    return redirect(f"/book/{book_id}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
