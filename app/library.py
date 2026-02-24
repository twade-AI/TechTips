"""
Knowledge Library — Save, organise, search, and manage
articles, notes, and curated resources.
"""

import aiosqlite


async def save_article(db: aiosqlite.Connection, title: str, url: str = "",
                       source: str = "", summary: str = "", content: str = "",
                       tags: str = "") -> int:
    cursor = await db.execute(
        "INSERT INTO articles (title, url, source, summary, content, tags, saved) VALUES (?, ?, ?, ?, ?, ?, 1)",
        (title, url, source, summary, content, tags),
    )
    await db.commit()
    return cursor.lastrowid


async def get_saved_articles(db: aiosqlite.Connection, limit: int = 50, offset: int = 0) -> list[dict]:
    cursor = await db.execute(
        "SELECT * FROM articles WHERE saved = 1 ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def search_articles(db: aiosqlite.Connection, query: str) -> list[dict]:
    pattern = f"%{query}%"
    cursor = await db.execute(
        "SELECT * FROM articles WHERE title LIKE ? OR summary LIKE ? OR tags LIKE ? ORDER BY created_at DESC",
        (pattern, pattern, pattern),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def create_note(db: aiosqlite.Connection, title: str, content: str, tags: str = "") -> int:
    cursor = await db.execute(
        "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
        (title, content, tags),
    )
    await db.commit()
    return cursor.lastrowid


async def get_notes(db: aiosqlite.Connection, limit: int = 50) -> list[dict]:
    cursor = await db.execute(
        "SELECT * FROM notes ORDER BY created_at DESC LIMIT ?", (limit,)
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def search_notes(db: aiosqlite.Connection, query: str) -> list[dict]:
    pattern = f"%{query}%"
    cursor = await db.execute(
        "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY created_at DESC",
        (pattern, pattern, pattern),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def create_collection(db: aiosqlite.Connection, name: str, description: str = "") -> int:
    cursor = await db.execute(
        "INSERT INTO collections (name, description) VALUES (?, ?)",
        (name, description),
    )
    await db.commit()
    return cursor.lastrowid


async def get_collections(db: aiosqlite.Connection) -> list[dict]:
    cursor = await db.execute("SELECT * FROM collections ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def add_to_collection(db: aiosqlite.Connection, collection_id: int,
                            item_type: str, item_id: int) -> int:
    cursor = await db.execute(
        "INSERT INTO collection_items (collection_id, item_type, item_id) VALUES (?, ?, ?)",
        (collection_id, item_type, item_id),
    )
    await db.commit()
    return cursor.lastrowid


async def get_collection_items(db: aiosqlite.Connection, collection_id: int) -> list[dict]:
    cursor = await db.execute(
        "SELECT * FROM collection_items WHERE collection_id = ? ORDER BY added_at DESC",
        (collection_id,),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def delete_article(db: aiosqlite.Connection, article_id: int):
    await db.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    await db.commit()


async def delete_note(db: aiosqlite.Connection, note_id: int):
    await db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    await db.commit()


async def delete_collection(db: aiosqlite.Connection, collection_id: int):
    await db.execute("DELETE FROM collection_items WHERE collection_id = ?", (collection_id,))
    await db.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
    await db.commit()


async def get_feed_sources(db: aiosqlite.Connection) -> list[dict]:
    cursor = await db.execute("SELECT * FROM feed_sources WHERE active = 1 ORDER BY name")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def add_feed_source(db: aiosqlite.Connection, name: str, url: str, category: str = "general") -> int:
    cursor = await db.execute(
        "INSERT OR IGNORE INTO feed_sources (name, url, category) VALUES (?, ?, ?)",
        (name, url, category),
    )
    await db.commit()
    return cursor.lastrowid


async def remove_feed_source(db: aiosqlite.Connection, feed_id: int):
    await db.execute("DELETE FROM feed_sources WHERE id = ?", (feed_id,))
    await db.commit()


# ── Resources ────────────────────────────────────────────────────

async def get_resources(db: aiosqlite.Connection, category: str = None) -> list[dict]:
    if category:
        cursor = await db.execute(
            "SELECT * FROM resources WHERE category = ? ORDER BY sort_order",
            (category,),
        )
    else:
        cursor = await db.execute("SELECT * FROM resources ORDER BY category, sort_order")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def get_featured_resources(db: aiosqlite.Connection, limit: int = 8) -> list[dict]:
    cursor = await db.execute(
        "SELECT * FROM resources WHERE featured = 1 ORDER BY RANDOM() LIMIT ?",
        (limit,),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]
