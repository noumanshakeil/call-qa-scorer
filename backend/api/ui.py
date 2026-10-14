from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import call_qa as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    calls = await svc.list_calls(db)
    return templates.TemplateResponse("index.html", {"request": request, "title": "Call QA Scorer", "calls": calls})

@router.post("/ui/calls")
async def ui_call(title: str = Form(...), transcript: str = Form(...), db: AsyncSession = Depends(get_db)):
    rec = await svc.ingest_call(db, title, "agent", transcript)
    await svc.score_call(db, rec.id)
    return RedirectResponse("/", status_code=303)
