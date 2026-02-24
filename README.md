# TechTips — Education Innovation Hub

A curated resource website for innovation in **pedagogy**, **digital technology**, and **enterprise** for 11-18 education. No API keys required.

## Features

### Curated Newsfeed
Live RSS feeds from top education sources including TES, BBC Education, The Guardian, EdSurge, Schools Week, TeachThought, and more. Articles are automatically tagged with school values and filtered by category.

### School Values Tagging
Every article is auto-tagged against six core character values — **Courage**, **Curiosity**, **Integrity**, **Kindness**, **Respect**, and **Service** — so you can filter content that aligns with your school ethos.

### Haileybury 2030 Alignment
Articles are matched against key academic ambitions: curriculum innovation, pedagogical excellence, technology & digital, leadership & enterprise, learning habits, assessment, and university & futures.

### Resource Toolkit
Hand-picked tools, organisations, and platforms across seven innovation themes:
- AI in Education
- Project-Based Learning
- Assessment Innovation
- Digital & Computing
- Enterprise & Careers
- Research & Evidence
- Inclusive Education

### Reading List & Notes
Save articles for later, create personal notes with tags, and search across your knowledge base.

### Surprise Me
Discover random articles from the feed for serendipitous reading.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python run.py
   ```

3. Open http://localhost:8000 in your browser.

No API keys or environment variables needed.

## Tech Stack

- **Backend:** Python, FastAPI, SQLite (via aiosqlite)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Feeds:** RSS via feedparser

## Project Structure

```
TechTips/
├── app/
│   ├── main.py          # FastAPI routes
│   ├── database.py      # Database setup, migrations, seed data
│   ├── newsfeed.py      # RSS feed aggregator
│   └── library.py       # Library and resources CRUD
├── static/
│   ├── css/style.css    # Styles
│   └── js/app.js        # Frontend logic, values tagging engine
├── templates/
│   └── index.html       # Main HTML template
├── requirements.txt
├── run.py               # Server entry point
└── README.md
```
