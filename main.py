from fastapi import FastAPI, Request, Form, HTTPException
import urllib.request
import urllib.parse
import urllib.error
import ssl
import json
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


@app.get("/search", response_class=HTMLResponse)
async def search_quotes(request: Request, q: str | None = None):
    """Search external quotes API and render results."""
    results = []
    error = None
    if q:
        safe_q = urllib.parse.quote(q)
        url = f"https://api.quotable.io/search/quotes?query={safe_q}&fields=content,author"

        def _fetch_with_context(context=None):
            with urllib.request.urlopen(url, timeout=10, context=context) as resp:
                return json.load(resp)

        try:
            # First try default system verification
            data = _fetch_with_context()
        except urllib.error.URLError as e:
            # Detect certificate verification failures and try safer fallbacks
            reason = getattr(e, 'reason', None)
            msg = str(e)
            # ssl.SSLError can be nested inside URLError.reason
            if isinstance(reason, ssl.SSLError) or 'certificate verify failed' in msg.lower():
                # Try to use certifi's CA bundle if available
                try:
                    import certifi

                    ctx = ssl.create_default_context(cafile=certifi.where())
                    data = _fetch_with_context(context=ctx)
                except Exception:
                    # Last resort: disable verification (INSECURE)
                    try:
                        ctx = ssl.create_default_context()
                        ctx.check_hostname = False
                        ctx.verify_mode = ssl.CERT_NONE
                        data = _fetch_with_context(context=ctx)
                        # warn user that verification was disabled
                        error = 'Warning: SSL verification was disabled to fetch external API. Install the "certifi" package to fix this securely.'
                    except Exception as e2:
                        error = f'Failed to fetch external API (ssl): {e2}'
                        data = {}
            else:
                error = f'Network error: {e}'
                data = {}
        except Exception as e:
            error = str(e)

        # parse results when data available
        for item in data.get("results", []) if isinstance(data, dict) else []:
            results.append({
                "text": item.get("content"),
                "author": item.get("author", "Unknown"),
            })

    return templates.TemplateResponse(
        "search_results.html",
        {"request": request, "query": q or "", "results": results, "error": error},
    )
