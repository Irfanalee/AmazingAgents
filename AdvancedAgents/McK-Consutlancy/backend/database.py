import os
from sqlalchemy import create_engine, Column, String, Text, Float, Integer, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "mck.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    shared_context = Column(Text)  # JSON
    theme = Column(String, default="mckinsey-dark")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=True)
    prompt_id = Column(String, nullable=False)
    prompt_title = Column(String)
    inputs = Column(Text)  # JSON
    output = Column(Text)
    model = Column(String)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    from_cache = Column(Boolean, default=False)
    excel_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Cache(Base):
    __tablename__ = "cache"
    cache_key = Column(String, primary_key=True)
    prompt_id = Column(String)
    model = Column(String)
    response = Column(Text)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    hit_count = Column(Integer, default=0)


class FeedbackMessage(Base):
    __tablename__ = "feedback_messages"
    id = Column(String, primary_key=True)
    analysis_id = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE analyses ADD COLUMN excel_path TEXT"))
            conn.commit()
        except Exception:
            pass  # column already exists


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
