from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class CallRecording(Base):
    __tablename__ = "call_recordings"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    agent_name: Mapped[str] = mapped_column(String(80), default="agent")
    transcript: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class RubricScore(Base):
    __tablename__ = "rubric_scores"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    recording_id: Mapped[str] = mapped_column(String(32), index=True)
    dimension: Mapped[str] = mapped_column(String(64))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    max_score: Mapped[float] = mapped_column(Float, default=5.0)
    notes: Mapped[str] = mapped_column(Text, default="")

class CoachingTip(Base):
    __tablename__ = "coaching_tips"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    recording_id: Mapped[str] = mapped_column(String(32), index=True)
    tip: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(16), default="medium")
