import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "techtips.db")


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT,
                source TEXT,
                summary TEXT,
                content TEXT,
                tags TEXT DEFAULT '',
                saved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS perspectives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                cautious_view TEXT,
                radical_view TEXT,
                pragmatic_view TEXT,
                verdict TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS collection_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS feed_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                category TEXT DEFAULT 'general',
                active INTEGER DEFAULT 1
            );
        """)
        await db.commit()


async def seed_default_feeds():
    """Insert default education/edtech RSS feeds if none exist."""
    default_feeds = [
        ("TES Magazine", "https://www.tes.com/rss/news.xml", "education"),
        ("EdSurge", "https://www.edsurge.com/articles_rss", "edtech"),
        ("Gov.uk Education", "https://www.gov.uk/search/news-and-communications.atom?topical_events%5B%5D=education", "policy"),
        ("BBC Education", "https://feeds.bbci.co.uk/news/education/rss.xml", "education"),
        ("The Guardian Education", "https://www.theguardian.com/education/rss", "education"),
        ("OECD Education", "https://www.oecd.org/education/rss.xml", "policy"),
        ("EdTech Magazine", "https://edtechmagazine.com/k12/rss.xml", "edtech"),
        ("TeachThought", "https://www.teachthought.com/feed/", "pedagogy"),
    ]
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM feed_sources")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.executemany(
                "INSERT OR IGNORE INTO feed_sources (name, url, category) VALUES (?, ?, ?)",
                default_feeds,
            )
            await db.commit()
