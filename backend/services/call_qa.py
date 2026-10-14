from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import CallRecording, CoachingTip, RubricScore
from backend.repositories import audit
from backend.utils.ids import short_id
from backend.utils.text import normalize

RUBRIC = [
    ("empathy", ["sorry", "understand", "appreciate"]),
    ("resolution", ["fixed", "resolved", "next step", "follow up"]),
    ("compliance", ["recorded", "privacy", "consent"]),
]

def _score_dimension(transcript: str, keywords: list[str]) -> float:
    blob = normalize(transcript).lower()
    hits = sum(1 for k in keywords if k in blob)
    return min(5.0, 1.0 + hits * 1.5)

async def ingest_call(session: AsyncSession, title: str, agent_name: str, transcript: str) -> CallRecording:
    rec = CallRecording(
        id=short_id(),
        title=title[:160],
        agent_name=agent_name[:80],
        transcript=transcript.strip(),
        status="pending",
    )
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    audit.record("call_ingested", rec.id)
    return rec

async def score_call(session: AsyncSession, recording_id: str) -> CallRecording:
    rec = await session.get(CallRecording, recording_id)
    if not rec:
        raise ValueError("recording not found")
    rec.status = "scoring"
    await session.commit()
    for dim, keys in RUBRIC:
        val = _score_dimension(rec.transcript, keys)
        session.add(
            RubricScore(
                id=short_id(),
                recording_id=recording_id,
                dimension=dim,
                score=val,
                max_score=5.0,
                notes=f"Keyword coverage for {dim}",
            )
        )
    llm = get_llm()
    tips_raw = await llm.complete(
        rec.transcript[:1500],
        system="Give 2 short coaching tips for a call center agent as bullet lines.",
    )
    for line in [ln.strip("-• ").strip() for ln in tips_raw.split("\n") if ln.strip()][:4]:
        session.add(
            CoachingTip(id=short_id(), recording_id=recording_id, tip=line[:500], priority="medium")
        )
    rec.status = "scored"
    await session.commit()
    await session.refresh(rec)
    return rec

async def list_calls(session: AsyncSession) -> list[CallRecording]:
    return list((await session.execute(select(CallRecording).order_by(CallRecording.created_at.desc()))).scalars())

async def get_scores(session: AsyncSession, recording_id: str) -> list[RubricScore]:
    stmt = select(RubricScore).where(RubricScore.recording_id == recording_id)
    return list((await session.execute(stmt)).scalars())

async def get_tips(session: AsyncSession, recording_id: str) -> list[CoachingTip]:
    stmt = select(CoachingTip).where(CoachingTip.recording_id == recording_id)
    return list((await session.execute(stmt)).scalars())
