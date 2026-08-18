import sqlite3
import settings

conn = None
cursor = None


def open_db():
    global conn, cursor
    conn = sqlite3.connect(settings.PATH_DB)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")


def close_db():
    if cursor:
        cursor.close()
    if conn:
        conn.close()


def execute(query, params=None):
    if params is None:
        cursor.execute(query)
    else:
        cursor.execute(query, params)
    conn.commit()


def create_tables():
    open_db()

    execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            image TEXT,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            desciption_short TEXT,
            description TEXT
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS posts (
            post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT,
            text TEXT NOT NULL,
            image TEXT,
            datetime TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON UPDATE CASCADE ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
        )
    """)

    columns = cursor.execute("PRAGMA table_info(posts)").fetchall()
    column_names = {column[1] for column in columns}
    if "user_id" not in column_names:
        cursor.execute("ALTER TABLE posts RENAME TO posts_old")
        execute("""
            CREATE TABLE posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                title TEXT,
                text TEXT NOT NULL,
                image TEXT,
                datetime TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories(category_id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
            )
        """)
        cursor.execute(
            "INSERT INTO posts (post_id, category_id, user_id, title, text, image, datetime) "
            "SELECT post_id, category_id, 1, title, text, image, datetime FROM posts_old"
        )
        conn.commit()
        cursor.execute("DROP TABLE posts_old")
        conn.commit()

    close_db()


def get_user():
    open_db()
    execute("SELECT * FROM users LIMIT 1")
    user = cursor.fetchone()
    close_db()
    return user


def get_user_by_id(user_id):
    open_db()
    execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    close_db()
    return user


def get_categories():
    open_db()
    execute("SELECT * FROM categories ORDER BY category_id")
    categories = cursor.fetchall()
    close_db()
    return categories


def add_category(category_name):
    open_db()
    execute("INSERT INTO categories (category_name) VALUES (?)", (category_name,))
    close_db()


def add_user(name, login, password):
    open_db()
    execute(
        "INSERT INTO users (name, image, login, password, desciption_short, description) VALUES (?, ?, ?, ?, ?, ?)",
        (name, "", login, password, "", ""),
    )
    close_db()


def add_post(user_id, category_id, title, text, image):
    open_db()
    execute(
        "INSERT INTO posts (user_id, category_id, title, text, image) VALUES (?, ?, ?, ?, ?)",
        (user_id, category_id, title, text, image),
    )
    close_db()


def get_posts():
    open_db()
    execute(
        """
        SELECT p.post_id, p.category_id, p.title, p.text, p.image, p.datetime, p.user_id,
               c.category_name, u.name AS author_name
        FROM posts p
        INNER JOIN categories c ON c.category_id = p.category_id
        INNER JOIN users u ON u.user_id = p.user_id
        ORDER BY p.post_id DESC
        """
    )
    rows = cursor.fetchall()
    close_db()
    return [
        {
            "post_id": row[0],
            "category_id": row[1],
            "title": row[2],
            "text": row[3],
            "image": row[4],
            "datetime": row[5],
            "user_id": row[6],
            "category_name": row[7],
            "author_name": row[8],
        }
        for row in rows
    ]


def get_post_by_id(post_id):
    open_db()
    execute(
        """
        SELECT p.post_id, p.category_id, p.title, p.text, p.image, p.datetime, p.user_id,
               c.category_name, u.name AS author_name
        FROM posts p
        INNER JOIN categories c ON c.category_id = p.category_id
        INNER JOIN users u ON u.user_id = p.user_id
        WHERE p.post_id = ?
        """,
        (post_id,),
    )
    row = cursor.fetchone()
    close_db()
    if row is None:
        return None
    return {
        "post_id": row[0],
        "category_id": row[1],
        "title": row[2],
        "text": row[3],
        "image": row[4],
        "datetime": row[5],
        "user_id": row[6],
        "category_name": row[7],
        "author_name": row[8],
    }


def delete_post(post_id):
    open_db()
    execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
    close_db()


def get_user_by_login(login):
    open_db()
    execute("SELECT * FROM users WHERE login = ?", (login,))
    user = cursor.fetchone()
    close_db()
    return user
