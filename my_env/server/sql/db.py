import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "my_env.sqlite3"

CHAT_TABLE = """
CREATE TABLE IF NOT EXISTS chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    chat_key TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CONVERSION_TABLE = """
CREATE TABLE IF NOT EXISTS conversion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_key TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    customer_message TEXT NOT NULL,
    agent_message TEXT NOT NULL,
    reward REAL DEFAULT 0.0,
    step_count INTEGER DEFAULT 0,
    resolution_status TEXT,
    customer_sentiment TEXT,
    satisfaction_score REAL,
    done BOOLEAN DEFAULT 0,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_key) REFERENCES chat (chat_key)
);
"""

MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_key TEXT NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    reward REAL DEFAULT 0.0,
    resolution_status TEXT DEFAULT 'in_progress',
    customer_sentiment TEXT DEFAULT 'negative',
    satisfaction_score REAL DEFAULT 0.0,
    awaiting_customer_response BOOLEAN DEFAULT 1,
    done BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_key) REFERENCES chat (chat_key)
);
"""


def init_db() -> None:
    db_path = DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(CHAT_TABLE)
        conn.execute(CONVERSION_TABLE)
        conn.execute(MESSAGES_TABLE)
        _migrate_messages_table(conn)
        conn.commit()


def _migrate_messages_table(conn: sqlite3.Connection) -> None:
    existing_columns = {
        row[1] for row in conn.execute("PRAGMA table_info(messages)").fetchall()
    }
    required_columns = {
        "reward": "ALTER TABLE messages ADD COLUMN reward REAL DEFAULT 0.0",
        "resolution_status": (
            "ALTER TABLE messages ADD COLUMN resolution_status TEXT DEFAULT 'in_progress'"
        ),
        "customer_sentiment": (
            "ALTER TABLE messages ADD COLUMN customer_sentiment TEXT DEFAULT 'negative'"
        ),
        "satisfaction_score": (
            "ALTER TABLE messages ADD COLUMN satisfaction_score REAL DEFAULT 0.0"
        ),
        "awaiting_customer_response": (
            "ALTER TABLE messages ADD COLUMN awaiting_customer_response BOOLEAN DEFAULT 1"
        ),
        "done": "ALTER TABLE messages ADD COLUMN done BOOLEAN DEFAULT 0",
    }

    for column_name, statement in required_columns.items():
        if column_name not in existing_columns:
            conn.execute(statement)


def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def get_chat_by_key(chat_key: str) -> dict[str, str | int | None] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, customer_name, chat_key, created_at FROM chat WHERE chat_key = ?",
            (chat_key,),
        ).fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "customer_name": row[1],
            "chat_key": row[2],
            "created_at": row[3],
        }


def get_messages_by_chat_key(chat_key: str) -> list[dict[str, str | int | float | bool]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                chat_key,
                sender,
                message,
                created_at,
                reward,
                resolution_status,
                customer_sentiment,
                satisfaction_score,
                awaiting_customer_response,
                done
            FROM messages
            WHERE chat_key = ?
            ORDER BY created_at ASC, id ASC
            """,
            (chat_key,),
        ).fetchall()

        return [
            {
                "id": row[0],
                "chat_key": row[1],
                "sender": row[2],
                "message": row[3],
                "created_at": row[4],
                "reward": float(row[5] if row[5] is not None else 0.0),
                "resolution_status": str(row[6] or "in_progress"),
                "customer_sentiment": str(row[7] or "negative"),
                "satisfaction_score": float(row[8] if row[8] is not None else 0.0),
                "awaiting_customer_response": (
                    bool(row[9]) if row[9] is not None else True
                ),
                "done": bool(row[10]) if row[10] is not None else False,
            }
            for row in rows
        ]


def create_chat(customer_name: str, chat_key: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO chat (customer_name, chat_key) VALUES (?, ?)",
            (customer_name, chat_key),
        )
        conn.commit()
        if cur.lastrowid:
            return cur.lastrowid
        row = conn.execute(
            "SELECT id FROM chat WHERE chat_key = ?", (chat_key,)
        ).fetchone()
        return row[0]  # type: ignore[index]


def add_message(
    chat_key: str,
    sender: str,
    message: str,
    reward: float = 0.0,
    resolution_status: str = "in_progress",
    customer_sentiment: str = "negative",
    satisfaction_score: float = 0.0,
    awaiting_customer_response: bool = True,
    done: bool = False,
) -> dict[str, str | int | float | bool]:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO messages (
                chat_key,
                sender,
                message,
                reward,
                resolution_status,
                customer_sentiment,
                satisfaction_score,
                awaiting_customer_response,
                done
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_key,
                sender,
                message,
                reward,
                resolution_status,
                customer_sentiment,
                satisfaction_score,
                int(awaiting_customer_response),
                int(done),
            ),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT
                id,
                chat_key,
                sender,
                message,
                created_at,
                reward,
                resolution_status,
                customer_sentiment,
                satisfaction_score,
                awaiting_customer_response,
                done
            FROM messages
            WHERE id = ?
            """,
            (cur.lastrowid,),
        ).fetchone()
        assert row is not None
        return {
            "id": row[0],
            "chat_key": row[1],
            "sender": row[2],
            "message": row[3],
            "created_at": row[4],
            "reward": float(row[5] if row[5] is not None else 0.0),
            "resolution_status": str(row[6] or "in_progress"),
            "customer_sentiment": str(row[7] or "negative"),
            "satisfaction_score": float(row[8] if row[8] is not None else 0.0),
            "awaiting_customer_response": bool(row[9]) if row[9] is not None else True,
            "done": bool(row[10]) if row[10] is not None else False,
        }


def add_conversion_entry(
    chat_key: str,
    customer_id: str,
    customer_message: str,
    agent_message: str,
    reward: float = 0.0,
    step_count: int = 0,
    resolution_status: str | None = None,
    customer_sentiment: str | None = None,
    satisfaction_score: float | None = None,
    done: bool = False,
    metadata: str | None = None,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO conversion (
                chat_key,
                customer_id,
                customer_message,
                agent_message,
                reward,
                step_count,
                resolution_status,
                customer_sentiment,
                satisfaction_score,
                done,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_key,
                customer_id,
                customer_message,
                agent_message,
                reward,
                step_count,
                resolution_status,
                customer_sentiment,
                satisfaction_score,
                int(done),
                metadata,
            ),
        )
        conn.commit()
        return cur.lastrowid
