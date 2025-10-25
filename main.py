from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import Base, engine, get_db
from models import Quote
import random

from contextlib import asynccontextmanager


templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def serve_html(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quote))
    quotes = result.scalars().all()
    return templates.TemplateResponse(request, "index.html", {"quotes": quotes})


@app.get("/random-quote", response_class=HTMLResponse)
async def random_quote(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quote))
    quotes = result.scalars().all()
    quote = random.choice(quotes) if quotes else None
    return templates.TemplateResponse(request, "random_quote.html", {"quote": quote})


@app.get("/add-quote", response_class=HTMLResponse)
async def add_quote_form(request: Request):
    return templates.TemplateResponse(request, "add_quote.html", {})


@app.post("/add-quote", response_class=RedirectResponse)
async def add_quote(
    text: str = Form(...), author: str = Form(...), db: AsyncSession = Depends(get_db)
):
    db_quote = Quote(text=text, author=author)
    db.add(db_quote)
    await db.commit()
    await db.refresh(db_quote)
    return RedirectResponse(url="/", status_code=303)


@app.get("/quote/{quote_id}", response_class=HTMLResponse)
async def view_quote(request: Request, quote_id: int):
    """View a specific quote by id."""
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return templates.TemplateResponse(request, "random_quote.html", {"quote": quote})


@app.get("/search", response_class=HTMLResponse)
async def search_quotes(
    request: Request, q: str | None = None, db: AsyncSession = Depends(get_db)
):
    """Search quotes in the database and render results."""
    results = []
    error = None
    if q:
        try:
            # Case-insensitive search on text and author
            search_query = select(Quote).where(
                (Quote.text.ilike(f"%{q}%")) | (Quote.author.ilike(f"%{q}%"))
            )
            result = await db.execute(search_query)
            quotes = result.scalars().all()
            for quote in quotes:
                results.append(
                    {
                        "text": quote.text,
                        "author": quote.author,
                    }
                )
        except Exception as e:
            error = f"Database error: {e}"

    return templates.TemplateResponse(
        request, "search_results.html",
        {"query": q or "", "results": results, "error": error},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
