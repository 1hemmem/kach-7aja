from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
import random
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In-memory quote storage
quotes = [
    {
        "id": 1,
        "text": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    {
        "id": 2,
        "text": "Life is what happens when you're busy making other plans.",
        "author": "John Lennon",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
]


@app.get("/", response_class=HTMLResponse)
async def serve_html(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "quotes": quotes}
    )


@app.get("/random-quote", response_class=HTMLResponse)
async def random_quote(request: Request):
    quote = random.choice(quotes) if quotes else None
    return templates.TemplateResponse(
        "random_quote.html", {"request": request, "quote": quote}
    )


@app.get("/add-quote", response_class=HTMLResponse)
async def add_quote_form(request: Request):
    return templates.TemplateResponse("add_quote.html", {"request": request})


@app.post("/add-quote", response_class=RedirectResponse)
async def add_quote(text: str = Form(...), author: str = Form(...)):
    new_quote = {
        "id": len(quotes) + 1,
        "text": text,
        "author": author,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    quotes.append(new_quote)
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.get("/quote/{quote_id}", response_class=HTMLResponse)
async def view_quote(request: Request, quote_id: int):
    """View a specific quote by id."""
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    return templates.TemplateResponse("random_quote.html", {"request": request, "quote": quote})
