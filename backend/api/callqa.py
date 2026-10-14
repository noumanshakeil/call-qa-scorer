from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import call_qa as svc

class CallIn(BaseModel):
    title: str = Field(min_length=2)
    agent_name: str = "agent"
    transcript: str = Field(min_length=10)

router = APIRouter()

@router.post("/calls")
async def ingest(payload: CallIn, db: AsyncSession = Depends(get_db)):
    rec = await svc.ingest_call(db, payload.title, payload.agent_name, payload.transcript)
    return {"id": rec.id, "status": rec.status}

@router.get("/calls")
async def list_calls(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_calls(db)
    return {"calls": [{"id": c.id, "title": c.title, "status": c.status} for c in rows]}

@router.post("/calls/{recording_id}/score")
async def score(recording_id: str, db: AsyncSession = Depends(get_db)):
    try:
        rec = await svc.score_call(db, recording_id)
        return {"id": rec.id, "status": rec.status}
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@router.get("/calls/{recording_id}/scores")
async def scores(recording_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.get_scores(db, recording_id)
    return {"scores": [{"dimension": s.dimension, "score": s.score, "max_score": s.max_score} for s in rows]}

@router.get("/calls/{recording_id}/tips")
async def tips(recording_id: str, db: AsyncSession = Depends(get_db)):
    rows = await svc.get_tips(db, recording_id)
    return {"tips": [{"tip": t.tip, "priority": t.priority} for t in rows]}
