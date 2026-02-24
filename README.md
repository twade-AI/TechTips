# TechTips — Education Knowledge Base

A knowledge base application focused on innovation in **pedagogy**, **digital technology**, and **enterprise** for 11-18 education.

## Features

### Perspectives Engine (Dialogical Partner)
Ask any question about education innovation and receive three expert perspectives:
- **The Guardian** — cautious, evidence-first, values proven methods
- **The Radical** — transformative, advocates for fundamental redesign
- **The Pragmatist** — balanced, implementation-focused, realistic

Each perspective includes supporting and contradicting evidence, a debate section where they engage with each other, and a verdict on which has the strongest support. You can ask follow-up questions to continue the debate.

### Curated Newsfeed
RSS-based feed pulling from configurable education and EdTech sources including TES, BBC Education, The Guardian Education, EdSurge, and more. Articles can be filtered by category and summarised using AI.

### Knowledge Library
- **Saved Articles** — save and organise articles from the newsfeed
- **Notes** — create your own notes with tags
- **Collections** — group articles and notes into themed collections
- **Search** — full-text search across your saved knowledge

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Anthropic API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

3. Run the application:
   ```bash
   python run.py
   ```

4. Open http://localhost:8000 in your browser.

## Tech Stack

- **Backend:** Python, FastAPI, SQLite (via aiosqlite)
- **AI:** Anthropic Claude API (Sonnet for perspectives, Haiku for summaries)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Feeds:** RSS via feedparser

## Project Structure

```
TechTips/
├── app/
│   ├── main.py          # FastAPI application and API routes
│   ├── database.py      # Database setup and migrations
│   ├── perspectives.py  # Perspectives Engine (dialogical partner)
│   ├── newsfeed.py      # RSS feed aggregator with AI summaries
│   └── library.py       # Knowledge library CRUD operations
├── static/
│   ├── css/style.css    # Application styles
│   └── js/app.js        # Frontend JavaScript
├── templates/
│   └── index.html       # Main HTML template
├── requirements.txt
├── run.py               # Server entry point
└── .env.example         # Environment variable template
```
