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

            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT 'general',
                icon TEXT DEFAULT '',
                featured INTEGER DEFAULT 0,
                sort_order INTEGER DEFAULT 0
            );
        """)
        await db.commit()


async def seed_default_feeds():
    """Insert default education/edtech RSS feeds if none exist."""
    default_feeds = [
        ("TES Magazine", "https://www.tes.com/rss/news.xml", "education"),
        ("EdSurge", "https://www.edsurge.com/articles_rss", "edtech"),
        ("BBC Education", "https://feeds.bbci.co.uk/news/education/rss.xml", "education"),
        ("The Guardian Education", "https://www.theguardian.com/education/rss", "education"),
        ("EdTech Magazine", "https://edtechmagazine.com/k12/rss.xml", "edtech"),
        ("TeachThought", "https://www.teachthought.com/feed/", "pedagogy"),
        ("Schools Week", "https://schoolsweek.co.uk/feed/", "education"),
        ("Teacher Toolkit", "https://www.teachertoolkit.co.uk/feed/", "pedagogy"),
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


async def seed_default_resources():
    """Insert curated education innovation resources if none exist."""
    resources = [
        # AI in Education
        ("TeacherMatic", "https://teachermatic.com/", "AI-powered lesson planning and resource generation tool built for teachers", "ai", "1", 1),
        ("AI for Education", "https://www.aiforeducation.io/", "Practical guides for integrating AI into classroom teaching and learning", "ai", "1", 2),
        ("UNESCO AI in Education", "https://www.unesco.org/en/artificial-intelligence/education", "UNESCO's guidance on ethical and effective use of AI in education worldwide", "ai", "0", 3),
        ("Oak National Academy AI", "https://www.thenational.academy/", "Free curriculum resources and AI-assisted lesson planning for UK teachers", "ai", "1", 4),

        # Project-Based Learning
        ("PBLWorks", "https://www.pblworks.org/", "The leading organisation for project-based learning — frameworks, research, and planning tools", "pbl", "1", 1),
        ("High Tech High", "https://www.hightechhigh.org/", "Pioneering PBL school network with open-source project ideas and student work", "pbl", "0", 2),
        ("Expeditionary Learning", "https://eleducation.org/", "Curriculum, professional development, and school design rooted in deeper learning", "pbl", "0", 3),
        ("Big Picture Learning", "https://www.bigpicture.org.au/", "Student-centred school model where learning is driven by individual interests and internships", "pbl", "0", 4),

        # Assessment Innovation
        ("No More Marking", "https://www.nomoremarking.com/", "Comparative judgement platform that rethinks how student work is assessed", "assessment", "1", 1),
        ("Evidence Based Education", "https://evidencebased.education/", "Tools and training for evidence-informed assessment and teaching decisions", "assessment", "0", 2),
        ("Rethinking Assessment", "https://rethinkingassessment.com/", "Network of schools exploring alternatives to traditional exams and grading", "assessment", "1", 3),
        ("Education Endowment Foundation", "https://educationendowmentfoundation.org.uk/", "The UK's leading source of evidence on what works in education for disadvantaged pupils", "assessment", "1", 4),

        # Digital Literacy & EdTech
        ("Raspberry Pi Foundation", "https://www.raspberrypi.org/", "Free computing education resources, projects, and teacher CPD", "digital", "1", 1),
        ("Micro:bit Foundation", "https://microbit.org/", "Physical computing device with free lesson plans and coding resources", "digital", "1", 2),
        ("National Centre for Computing Education", "https://teachcomputing.org/", "Free CPD courses and resources for teaching computing in England", "digital", "0", 3),
        ("Google for Education", "https://edu.google.com/", "Tools, training, and resources for technology in the classroom", "digital", "0", 4),

        # Enterprise & Employability
        ("Founders4Schools", "https://www.founders4schools.org.uk/", "Connects schools with local business leaders for workplace encounters and mentoring", "enterprise", "1", 1),
        ("Young Enterprise", "https://www.young-enterprise.org.uk/", "UK's leading enterprise and financial education charity for young people", "enterprise", "1", 2),
        ("Careers & Enterprise Company", "https://www.careersandenterprise.co.uk/", "Supports schools to deliver world-class careers education through benchmarks and funding", "enterprise", "0", 3),
        ("Gatsby Benchmarks", "https://www.gatsby.org.uk/education/focus-areas/good-career-guidance", "The 8 benchmarks of excellent careers provision used across UK schools", "enterprise", "0", 4),

        # Research & Evidence
        ("ResearchED", "https://researched.org.uk/", "Grassroots movement bridging the gap between education research and classroom practice", "research", "1", 1),
        ("John Hattie — Visible Learning", "https://www.visiblelearningmetax.com/", "The world's largest evidence base on what works in education — effect sizes and rankings", "research", "1", 2),
        ("OECD Education", "https://www.oecd.org/en/topics/education.html", "International education data, policy analysis, and PISA results", "research", "0", 3),
        ("Chartered College of Teaching", "https://chartered.college/", "Professional body for teachers — research journals, CPD, and chartered status", "research", "0", 4),

        # Inclusive Education
        ("SEND Gateway", "https://www.sendgateway.org.uk/", "One-stop shop for SEND resources, research, and effective practice from nasen", "inclusion", "1", 1),
        ("Whole School SEND", "https://www.wholeschoolsend.org.uk/", "Free resources and training to support SEND provision across mainstream schools", "inclusion", "0", 2),
        ("The Key", "https://www.thekeysupport.com/", "Practical school leadership guidance including SEND, safeguarding, and governance", "inclusion", "0", 3),
        ("Pupil Premium Awards", "https://educationendowmentfoundation.org.uk/guidance-for-teachers/using-pupil-premium", "EEF guidance on effective use of pupil premium funding to close the disadvantage gap", "inclusion", "1", 4),
    ]

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM resources")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.executemany(
                "INSERT INTO resources (title, url, description, category, featured, sort_order) VALUES (?, ?, ?, ?, ?, ?)",
                resources,
            )
            await db.commit()
