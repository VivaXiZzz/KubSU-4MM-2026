import logging
import sqlite3
from contextlib import closing
from typing import Any

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = "page_views.db"


class PageView(BaseModel):
    url: str
    title: str
    lang: str
    text: str
    content: dict[str, Any]
    timestamp: str


class LlmRequest(BaseModel):
    prompt: str


def init_db() -> None:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS page_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                lang TEXT NOT NULL,
                text TEXT NOT NULL,
                headers TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            )
            """
        )
        conn.commit()


def save_page_view(page_view: PageView) -> None:
    headings_dict = page_view.content.get("headings", {})

    all_headings = []
    for level in ["h1", "h2", "h3", "h4"]:
        for text in headings_dict.get(level, []):
            all_headings.append(f"{level}: {text}")

    headers_text = "\n".join(all_headings)

    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute(
            """
            INSERT INTO page_views (url, title, lang, text, headers, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                page_view.url,
                page_view.title,
                page_view.lang,
                page_view.text,
                headers_text,
                page_view.timestamp,
            ),
        )
        conn.commit()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info("Database initialized: %s", DB_PATH)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


@app.post("/page-view")
def page_view(page_view: PageView) -> dict[str, str]:
    logger.info("=" * 60)
    logger.info("URL:       %s", page_view.url)
    logger.info("Title:     %s", page_view.title)
    logger.info("Lang:      %s", page_view.lang)
    logger.info("=" * 60)

    save_page_view(page_view)
    logger.info("Page view saved to database")

    return {"status": "ok"}


# docker compose -f ./docker-compose.ollama.yml up -d
# docker exec -it ollama ollama run gemma3:4b-it-qat


@app.post("/request")
def llm_proxy(req: LlmRequest) -> Any:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:4b-it-qat",
            "prompt": req.prompt,
            "system": "абубе",
            "temperature": 0.1,
            "stream": False,
        },
    )
    return response.json().get("response")
