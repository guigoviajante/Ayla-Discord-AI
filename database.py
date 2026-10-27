import sqlite3
from datetime import datetime, timedelta


DATABASE = "ayla.db"


def connect():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            discord_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            nickname TEXT,
            relationship TEXT DEFAULT 'new',
            affection INTEGER DEFAULT 0,
            first_interaction TEXT,
            last_interaction TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id INTEGER NOT NULL,
            memory TEXT NOT NULL,
            importance INTEGER DEFAULT 1,
            created_at TEXT,
            FOREIGN KEY (discord_id)
                REFERENCES users(discord_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id INTEGER NOT NULL,
            channel_id INTEGER,
            username TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ayla_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            emotion TEXT DEFAULT 'normal',
            last_activity TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id INTEGER NOT NULL,
            alias TEXT NOT NULL COLLATE NOCASE,
            created_at TEXT,
            UNIQUE(discord_id, alias),
            FOREIGN KEY (discord_id)
                REFERENCES users(discord_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS initiative_state (
            discord_id INTEGER PRIMARY KEY,
            last_called TEXT,
            ignored_count INTEGER DEFAULT 0,
            FOREIGN KEY (discord_id)
                REFERENCES users(discord_id)
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO ayla_state (
            id,
            emotion,
            last_activity
        )
        VALUES (1, 'normal', ?)
    """, (
        datetime.now().isoformat(),
    ))

    connection.commit()
    connection.close()


def remember_user(
    discord_id,
    username,
    nickname=None,
    creator=False
):
    connection = connect()
    cursor = connection.cursor()
    now = datetime.now().isoformat()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE discord_id = ?
    """, (discord_id,))

    user = cursor.fetchone()

    if user is None:
        relationship = "creator" if creator else "new"
        affection = 100 if creator else 0

        cursor.execute("""
            INSERT INTO users (
                discord_id,
                username,
                nickname,
                relationship,
                affection,
                first_interaction,
                last_interaction
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            discord_id,
            username,
            nickname,
            relationship,
            affection,
            now,
            now
        ))
    elif creator:
        cursor.execute("""
            UPDATE users
            SET username = ?,
                nickname = ?,
                relationship = 'creator',
                affection = 100,
                last_interaction = ?
            WHERE discord_id = ?
        """, (
            username,
            nickname,
            now,
            discord_id
        ))
    else:
        cursor.execute("""
            UPDATE users
            SET username = ?,
                nickname = ?,
                last_interaction = ?
            WHERE discord_id = ?
        """, (
            username,
            nickname,
            now,
            discord_id
        ))

    connection.commit()
    connection.close()


def save_message(
    discord_id,
    role,
    content,
    channel_id=None,
    username=None
):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (
            discord_id,
            channel_id,
            username,
            role,
            content,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        discord_id,
        channel_id,
        username,
        role,
        content,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_channel_context(channel_id, limit=20):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT username, role, content
        FROM messages
        WHERE channel_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (
        channel_id,
        limit
    ))

    rows = cursor.fetchall()
    connection.close()
    return list(reversed(rows))


def get_recent_messages(discord_id, limit=10):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE discord_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (
        discord_id,
        limit
    ))

    rows = cursor.fetchall()
    connection.close()
    return list(reversed(rows))


def save_memory(discord_id, memory, importance=1):
    if not memory:
        return

    memory = memory.strip()

    if not memory:
        return

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM memories
        WHERE discord_id = ?
        AND LOWER(memory) = LOWER(?)
    """, (
        discord_id,
        memory
    ))

    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO memories (
                discord_id,
                memory,
                importance,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            discord_id,
            memory,
            importance,
            datetime.now().isoformat()
        ))

    connection.commit()
    connection.close()


def get_memories(discord_id, limit=15):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT memory
        FROM memories
        WHERE discord_id = ?
        ORDER BY importance DESC, id DESC
        LIMIT ?
    """, (
        discord_id,
        limit
    ))

    rows = cursor.fetchall()
    connection.close()
    return [row["memory"] for row in rows]


def change_affection(discord_id, amount):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT affection, relationship
        FROM users
        WHERE discord_id = ?
    """, (discord_id,))

    user = cursor.fetchone()

    if user is None:
        connection.close()
        return

    if user["relationship"] == "creator":
        connection.close()
        return

    new_value = max(
        -100,
        min(100, user["affection"] + amount)
    )

    if new_value >= 60:
        relationship = "close_friend"
    elif new_value >= 25:
        relationship = "friend"
    elif new_value <= -30:
        relationship = "disliked"
    else:
        relationship = "acquaintance"

    cursor.execute("""
        UPDATE users
        SET affection = ?,
            relationship = ?
        WHERE discord_id = ?
    """, (
        new_value,
        relationship,
        discord_id
    ))

    connection.commit()
    connection.close()


def get_user(discord_id):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE discord_id = ?
    """, (discord_id,))

    user = cursor.fetchone()
    connection.close()
    return user


def find_user_by_name(name):
    connection = connect()
    cursor = connection.cursor()

    pattern = f"%{name}%"

    cursor.execute("""
        SELECT *
        FROM users
        WHERE LOWER(username) LIKE LOWER(?)
        OR LOWER(nickname) LIKE LOWER(?)
        ORDER BY affection DESC
        LIMIT 1
    """, (
        pattern,
        pattern
    ))

    user = cursor.fetchone()
    connection.close()
    return user


def get_friends(min_affection=25):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE affection >= ?
        OR relationship = 'creator'
        ORDER BY affection DESC
    """, (min_affection,))

    users = cursor.fetchall()
    connection.close()
    return users


def set_emotion(emotion):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE ayla_state
        SET emotion = ?,
            last_activity = ?
        WHERE id = 1
    """, (
        emotion,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_emotion():
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT emotion
        FROM ayla_state
        WHERE id = 1
    """)

    row = cursor.fetchone()
    connection.close()

    if row:
        return row["emotion"]

    return "normal"


def update_activity():
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE ayla_state
        SET last_activity = ?
        WHERE id = 1
    """, (
        datetime.now().isoformat(),
    ))

    connection.commit()
    connection.close()


def save_alias(discord_id, alias):
    alias = alias.strip().lower()

    if len(alias) < 2 or len(alias) > 20:
        return

    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO aliases (
            discord_id,
            alias,
            created_at
        )
        VALUES (?, ?, ?)
    """, (
        discord_id,
        alias,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_aliases(discord_id):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT alias
        FROM aliases
        WHERE discord_id = ?
        ORDER BY id ASC
    """, (discord_id,))

    rows = cursor.fetchall()
    connection.close()
    return [row["alias"] for row in rows]


def mark_called(discord_id):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO initiative_state (
            discord_id,
            last_called,
            ignored_count
        )
        VALUES (?, ?, 0)
        ON CONFLICT(discord_id)
        DO UPDATE SET
            last_called = excluded.last_called
    """, (
        discord_id,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def mark_ignored(discord_id):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO initiative_state (
            discord_id,
            last_called,
            ignored_count
        )
        VALUES (?, ?, 1)
        ON CONFLICT(discord_id)
        DO UPDATE SET
            last_called = excluded.last_called,
            ignored_count = initiative_state.ignored_count + 1
    """, (
        discord_id,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def reset_ignored(discord_id):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE initiative_state
        SET ignored_count = 0
        WHERE discord_id = ?
    """, (discord_id,))

    connection.commit()
    connection.close()


def can_call_user(discord_id):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT last_called, ignored_count
        FROM initiative_state
        WHERE discord_id = ?
    """, (discord_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return True

    ignored = row["ignored_count"] or 0

    if ignored >= 2:
        return False

    if not row["last_called"]:
        return True

    try:
        last_called = datetime.fromisoformat(
            row["last_called"]
        )

        if datetime.now() - last_called < timedelta(hours=2):
            return False

    except (TypeError, ValueError):
        pass

    return True