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
        ("Google Workspace Updates", "https://workspaceupdates.googleblog.com/feeds/posts/default", "edtech"),
        ("The Neuron Daily", "https://rss.beehiiv.com/feeds/N4eCstxvgX.xml", "ai"),
        # UK Research & Policy
        ("BERA", "https://www.bera.ac.uk/feed", "research"),
        ("UCL Institute of Education", "https://blogs.ucl.ac.uk/ioe/feed/", "research"),
        ("Cambridge Education Blog", "https://blog.cambridgeinternational.org/feed/", "research"),
        ("UK Dept for Education", "https://www.gov.uk/government/organisations/department-for-education.atom", "policy"),
        ("Ofsted", "https://www.gov.uk/government/organisations/ofsted.atom", "policy"),
        ("DfE Teaching Blog", "https://teaching.blog.gov.uk/feed/", "policy"),
        ("DfE Education Hub", "https://educationhub.blog.gov.uk/feed/", "policy"),
        ("Wonkhe", "https://wonkhe.com/feed/", "policy"),
        ("HEPI", "https://www.hepi.ac.uk/feed/", "policy"),
        # EU & International
        ("OECD Education & Skills Today", "https://oecdeducationtoday.blogspot.com/feeds/posts/default?alt=rss", "policy"),
        ("CEDEFOP News", "https://www.cedefop.europa.eu/news-and-press/news.rss", "policy"),
        # AI & Academic Research
        ("arXiv Computers & Society", "https://rss.arxiv.org/rss/cs.CY", "research"),
        ("arXiv AI", "https://rss.arxiv.org/rss/cs.AI", "ai"),
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


async def seed_default_articles():
    """Insert curated AI-in-education articles if none exist."""
    articles = [
        (
            "How AI Is Changing — Not 'Killing' — College",
            "https://www.insidehighered.com/news/students/academics/2025/08/29/survey-college-students-views-ai",
            "Inside Higher Ed",
            "Survey of 1,047 college students reveals AI use hasn't diminished their perception of college value — students primarily use AI for supportive learning activities like studying and brainstorming.",
            "ai, education, research, students",
        ),
        (
            "Looking for Light in the New Brookings Report on AI and Education",
            "https://davidpblross.substack.com/p/looking-for-light-in-the-new-brookings",
            "David Ross (Substack)",
            "Identifies six concrete opportunities in the Brookings report — improving equity, optimising teacher time, enhancing learning, personalising instruction, supporting neurodivergent learners, and advancing assessment.",
            "ai, education, research, equity",
        ),
        (
            "The Fifteen AI World-Altering Challenges Most Schools Refuse to See",
            "https://stefanbauschard.substack.com/p/the-fifteen-ai-world-altering-challenges",
            "Stefan Bauschard (Substack)",
            "Argues schools are preparing students for an economy that no longer exists, identifying sixteen critical areas — from AI relationships and economic disruption to deepfakes — where students need preparation.",
            "ai, education, future, curriculum",
        ),
        (
            "Google for Education Generative AI Resources",
            "https://services.google.com/fh/files/misc/gfe_generative_ai_resources.pdf",
            "Google for Education",
            "Comprehensive guide to Google's generative AI tools and resources for K-12 and higher education — covers training programmes, certifications, and implementation guides for Gemini and NotebookLM.",
            "ai, edtech, resources, google",
        ),
        (
            "Cartography of Generative AI",
            "https://cartography-of-generative-ai.net/",
            "Cartography of Generative AI",
            "Maps the complex infrastructure and global supply chains underlying generative AI systems — tracing data extraction, computational processing, raw material mining, energy consumption, and environmental impacts.",
            "ai, infrastructure, ethics, environment",
        ),
        (
            "Everything Educators Need to Know About GenAI in 2026",
            "https://leonfurze.com/2026/01/15/everything-educators-need-to-know-about-genai-in-2026/",
            "Leon Furze",
            "Comprehensive overview of GenAI for educators covering how it works, available applications, concerns for educators and students, and how schools should respond through policy and practice.",
            "ai, education, pedagogy, policy",
        ),
        (
            "Get Started with Google AI in K12 Education",
            "https://skillshop.exceedlms.com/student/path/1178011-get-started-with-gemini-for-google-workspace",
            "Google Skillshop",
            "Free course teaching K-12 educators how to use Gemini across Google Workspace apps — Docs, Gmail, Slides, and Classroom — to enhance productivity and creativity.",
            "ai, edtech, google, training, cpd",
        ),
        (
            "Teaching Responsible Use of AI — Lesson Plan",
            "https://services.google.com/fh/files/misc/google_teaching_responsible_ai.pdf",
            "Google for Education",
            "Structured lesson plan for teaching students about the ethical and responsible use of artificial intelligence, with guidance on introducing AI concepts and responsible practices.",
            "ai, education, ethics, pedagogy, lesson-plan",
        ),
        (
            "AI 2027 — Scenario Forecast",
            "https://ai-2027.com/",
            "AI 2027",
            "Detailed scenario forecasting how AI could evolve and transform society between 2025 and 2027, exploring potential capabilities, alignment challenges, and global competition around superintelligent AI.",
            "ai, future, scenarios, alignment",
        ),
        (
            "Process Feedback — A Learning-First Alternative to AI Detection",
            "https://processfeedback.org/",
            "Process Feedback",
            "Free tool that captures students' writing process — edits, revision patterns, and AI usage — shifting the conversation from 'Did you cheat?' to 'How did you learn?'",
            "ai, assessment, writing, tools, integrity",
        ),
        (
            "Thinking — Fast, Slow, and Artificial: How AI is Reshaping Human Reasoning",
            "https://ssrn.com/abstract=6097646",
            "SSRN (Shaw & Nave, UPenn)",
            "Examines how AI is affecting human cognitive processes, introducing the concept of 'cognitive surrender' — the idea that humans may increasingly defer their reasoning to AI systems.",
            "ai, research, cognition, psychology",
        ),
        (
            "Agentic Engineering Patterns",
            "https://simonwillison.net/2026/Feb/23/agentic-engineering-patterns/",
            "Simon Willison",
            "Documents coding practices for working with AI coding agents that can generate and execute code independently — covers test-driven development approaches and how 'writing code is cheap now'.",
            "ai, coding, engineering, agentic",
        ),
        (
            "The AI Fluency Index",
            "https://www.anthropic.com/research/AI-fluency-index",
            "Anthropic",
            "Research tracking 11 observable behaviours across 9,830 conversations to measure how people develop skills in AI collaboration — finds iterative conversations and critical evaluation are key indicators of fluency.",
            "ai, research, fluency, skills",
        ),
        (
            "OECD Digital Education Outlook 2026: Exploring Effective Uses of Generative AI in Education",
            "https://www.oecd.org/en/publications/oecd-digital-education-outlook-2026_062a7394-en.html",
            "OECD",
            "Flagship OECD report examining how generative AI is reshaping education — finds GenAI can scale personalised learning and cut lesson planning time by 31%, but warns over-reliance risks reducing metacognitive engagement.",
            "ai, education, research, policy, oecd",
        ),
        (
            "Quantifying Human-AI Synergy",
            "https://osf.io/preprints/psyarxiv/vbkmt_v1",
            "Riedl & Weidmann (PsyArXiv)",
            "Introduces a Bayesian framework to measure human-AI collaboration ability, finding it is a distinct competence separate from individual problem-solving skill — users who adapt to others' perspectives achieve superior AI collaboration.",
            "ai, research, collaboration, skills",
        ),
        (
            "From Superficial Outputs to Superficial Learning: Risks of Large Language Models in Education",
            "https://arxiv.org/abs/2509.21972",
            "Delikoura, Fung & Hui (arXiv)",
            "Systematic review of 70 empirical studies examining how LLMs are applied in education — identifies risks including reduced student independence, weaker memory formation, and over-reliance alongside technical concerns like bias and hallucinations.",
            "ai, education, research, cognition, assessment",
        ),
        (
            "Teaching the AI-Native Generation: Empowering Schools in the Age of AI",
            "https://fdslive.oup.com/www.oup.com/oxed/secondary/Teaching_the_AI_Native_Generation.pdf",
            "Oxford University Press",
            "Survey of 2,000 UK students finds 80% use AI for schoolwork yet fewer than half feel confident identifying AI-generated misinformation — students want teacher guidance on trustworthy sources, not prohibition.",
            "ai, education, research, students, literacy",
        ),
        (
            "Underreporting of AI Use: The Role of Social Desirability Bias",
            "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5464215",
            "Ling, Kale & Imas (SSRN)",
            "Surveys 338 university students and finds a significant gap: ~60% report using AI themselves while estimating 90% of peers do — embarrassment and fear of judgement drive underreporting, meaning institutional surveys likely underestimate AI adoption.",
            "ai, research, students, integrity, assessment",
        ),
        (
            "Cyborgs, Centaurs and Self-Automators: Human-GenAI Knowledge Work and Implications for Skilling",
            "https://www.hbs.edu/ris/Publication%20Files/26-036_e7d0e59a-904c-49f1-b610-56eb2bdfe6f9.pdf",
            "Randazzo et al. (Harvard Business School)",
            "Field study of 244 management consultants identifies three modes of human-GenAI work — Centaurs upskill domain expertise, Cyborgs develop AI expertise, and Self-Automators risk eroding both — highlighting the tension between automation and augmentation.",
            "ai, research, future, skills, employment",
        ),
        (
            "Randomized Trial of a Generative AI Chatbot for Mental Health Treatment",
            "https://gwern.net/doc/psychiatry/depression/2025-heinz.pdf",
            "Heinz et al. (NEJM AI)",
            "First clinical trial of a generative AI therapy chatbot (Therabot) with 210 adults — produced clinically significant reductions in depression, anxiety, and eating disorder symptoms, with participants rating it comparably to a human therapist.",
            "ai, research, wellbeing, mental-health",
        ),
        (
            "Uneven Adoption of AI Tools Among U.S. Teachers and Principals",
            "https://www.rand.org/pubs/research_reports/RRA134-25.html",
            "Kaufman et al. (RAND Corporation)",
            "Finds teachers in higher-poverty schools are significantly less likely to use AI tools and receive less guidance — only 25% of teachers used AI for instruction, while principals in high-poverty schools were half as likely to provide AI guidance.",
            "ai, education, research, equity, policy",
        ),
    ]

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM articles")
        count = (await cursor.fetchone())[0]
        if count == 0:
            await db.executemany(
                "INSERT INTO articles (title, url, source, summary, tags, saved) VALUES (?, ?, ?, ?, ?, 1)",
                articles,
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
