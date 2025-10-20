from contextlib import contextmanager
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{settings.db_path}", echo=False, connect_args={"check_same_thread": False})
    return _engine

@contextmanager
def session_scope():
    session = Session(get_engine())
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def ensure_db():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)