from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def serve_html(request: Request):
    data = {
        "greeting": "Hello from kach-7aja!",
        "message": "Welcome to the modular FastAPI server!",
    }
    return templates.TemplateResponse("index.html", {"request": request, **data})


@app.get("/page1", response_class=HTMLResponse)
async def serve_page1(request: Request):
    data = {
        "title": "Explore Kach-7aja",
        "content": "Discover the wonders of our platform with this page!",
    }
    return templates.TemplateResponse("page1.html", {"request": request, **data})


@app.get("/page2", response_class=HTMLResponse)
async def serve_page2(request: Request):
    data = {
        "title": "Kach-7aja Adventures",
        "content": "Join us on an exciting journey through our services!",
    }
    return templates.TemplateResponse("page2.html", {"request": request, **data})


@app.get("/health")
async def check_health():
    return {"health": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
