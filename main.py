from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import Base, engine, get_db
from models import Quote
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/", response_class=HTMLResponse)
async def serve_html(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quote))
    quotes = result.scalars().all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "quotes": quotes}
    )


@app.get("/random-quote", response_class=HTMLResponse)
async def random_quote(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Quote))
    quotes = result.scalars().all()
    quote = random.choice(quotes) if quotes else None
    return templates.TemplateResponse(
        "random_quote.html", {"request": request, "quote": quote}
    )


@app.get("/add-quote", response_class=HTMLResponse)
async def add_quote_form(request: Request):
    return templates.TemplateResponse("add_quote.html", {"request": request})


@app.post("/add-quote", response_class=RedirectResponse)
async def add_quote(text: str = Form(...), author: str = Form(...), db: AsyncSession = Depends(get_db)):
    db_quote = Quote(text=text, author=author)
    db.add(db_quote)
    await db.commit()
    await db.refresh(db_quote)
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
