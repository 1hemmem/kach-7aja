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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
