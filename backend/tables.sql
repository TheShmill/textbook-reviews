CREATE TABLE IF NOT EXISTS books(
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    year INT NOT NULL,
    edition TEXT NOT NULL,
    isbn TEXT NOT NULL UNIQUE,
    authorid INT
);

CREATE TABLE IF NOT EXISTS users(
    username TEXT NOT NULL UNIQUE,
    displayname TEXT,
    profilepicture TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews(
    stars REAL NOT NULL,
    bookid INT NOT NULL,
    userid INT NOT NULL,
    comment TEXT,
    UNIQUE(bookid, userid)
);

CREATE TABLE IF NOT EXISTS likes(
    userid INT NOT NULL,
    reviewid INT NOT NULL,
    UNIQUE(userid, reviewid)
);
