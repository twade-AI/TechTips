"""
TechTips — Education Innovation Hub

A curated resource website for education innovation (11-18 year olds)
covering pedagogy, digital technology, and enterprise.
No API keys required.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import aiosqlite

from .database import get_db, init_db, seed_default_feeds, seed_default_resources
from . import newsfeed, library


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_default_feeds()
    await seed_default_resources()
    yield


app = FastAPI(
    title="TechTips — Education Innovation Hub",
    description="Curated resources for innovation in pedagogy, digital technology and enterprise for 11-18 education",
    version="2.0.0",
    lifespan=lifespan,
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# ── Pages ────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ── Newsfeed API ─────────────────────────────────────────────────────

@app.get("/api/feed")
async def get_feed(db: aiosqlite.Connection = Depends(get_db)):
    sources = await library.get_feed_sources(db)
    feed_list = [{"url": s["url"], "name": s["name"], "category": s.get("category", "general")} for s in sources]
    articles = await newsfeed.fetch_all_feeds(feed_list, limit_per_feed=5)
    return JSONResponse(articles)


@app.get("/api/feed/sources")
async def list_feed_sources(db: aiosqlite.Connection = Depends(get_db)):
    sources = await library.get_feed_sources(db)
    return JSONResponse(sources)


@app.post("/api/feed/sources")
async def add_feed(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    body = await request.json()
    name = body.get("name", "").strip()
    url = body.get("url", "").strip()
    category = body.get("category", "general")
    if not name or not url:
        return JSONResponse({"error": "Name and URL are required"}, status_code=400)
    feed_id = await library.add_feed_source(db, name, url, category)
    return JSONResponse({"id": feed_id, "name": name, "url": url})


@app.delete("/api/feed/sources/{feed_id}")
async def delete_feed(feed_id: int, db: aiosqlite.Connection = Depends(get_db)):
    await library.remove_feed_source(db, feed_id)
    return JSONResponse({"ok": True})


# ── Resources API ────────────────────────────────────────────────────

@app.get("/api/resources")
async def list_resources(category: str = None, db: aiosqlite.Connection = Depends(get_db)):
    resources = await library.get_resources(db, category=category)
    return JSONResponse(resources)


@app.get("/api/resources/featured")
async def featured_resources(db: aiosqlite.Connection = Depends(get_db)):
    resources = await library.get_featured_resources(db)
    return JSONResponse(resources)


# ── Library API ──────────────────────────────────────────────────────

@app.post("/api/articles")
async def save_article(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    body = await request.json()
    article_id = await library.save_article(
        db,
        title=body.get("title", ""),
        url=body.get("url", ""),
        source=body.get("source", ""),
        summary=body.get("summary", ""),
        content=body.get("content", ""),
        tags=body.get("tags", ""),
    )
    return JSONResponse({"id": article_id})


@app.get("/api/articles")
async def list_articles(db: aiosqlite.Connection = Depends(get_db)):
    articles = await library.get_saved_articles(db)
    return JSONResponse(articles)


@app.get("/api/articles/search")
async def search_articles(q: str = "", db: aiosqlite.Connection = Depends(get_db)):
    if not q:
        return JSONResponse([])
    results = await library.search_articles(db, q)
    return JSONResponse(results)


@app.delete("/api/articles/{article_id}")
async def delete_article(article_id: int, db: aiosqlite.Connection = Depends(get_db)):
    await library.delete_article(db, article_id)
    return JSONResponse({"ok": True})


# ── Notes API ────────────────────────────────────────────────────────

@app.post("/api/notes")
async def create_note(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    body = await request.json()
    note_id = await library.create_note(
        db,
        title=body.get("title", ""),
        content=body.get("content", ""),
        tags=body.get("tags", ""),
    )
    return JSONResponse({"id": note_id})


@app.get("/api/notes")
async def list_notes(db: aiosqlite.Connection = Depends(get_db)):
    notes = await library.get_notes(db)
    return JSONResponse(notes)


@app.get("/api/notes/search")
async def search_notes(q: str = "", db: aiosqlite.Connection = Depends(get_db)):
    if not q:
        return JSONResponse([])
    results = await library.search_notes(db, q)
    return JSONResponse(results)


@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int, db: aiosqlite.Connection = Depends(get_db)):
    await library.delete_note(db, note_id)
    return JSONResponse({"ok": True})


# ── Collections API ──────────────────────────────────────────────────

@app.post("/api/collections")
async def create_collection(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    body = await request.json()
    coll_id = await library.create_collection(
        db,
        name=body.get("name", ""),
        description=body.get("description", ""),
    )
    return JSONResponse({"id": coll_id})


@app.get("/api/collections")
async def list_collections(db: aiosqlite.Connection = Depends(get_db)):
    collections = await library.get_collections(db)
    return JSONResponse(collections)


@app.post("/api/collections/{collection_id}/items")
async def add_collection_item(collection_id: int, request: Request,
                               db: aiosqlite.Connection = Depends(get_db)):
    body = await request.json()
    item_id_val = await library.add_to_collection(
        db,
        collection_id=collection_id,
        item_type=body.get("item_type", ""),
        item_id=body.get("item_id", 0),
    )
    return JSONResponse({"id": item_id_val})


@app.get("/api/collections/{collection_id}/items")
async def get_collection_items(collection_id: int, db: aiosqlite.Connection = Depends(get_db)):
    items = await library.get_collection_items(db, collection_id)
    return JSONResponse(items)


@app.delete("/api/collections/{collection_id}")
async def delete_collection(collection_id: int, db: aiosqlite.Connection = Depends(get_db)):
    await library.delete_collection(db, collection_id)
    return JSONResponse({"ok": True})
