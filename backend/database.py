import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeBase

# Load environment variables from .env file
load_dotenv()

# Default SQLite path for fallback
SQLITE_DB_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "component_1.db"
    )
)

DEFAULT_SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# Retrieve DATABASE_URL from environment or fallback
DATABASE_URL = DEFAULT_SQLITE_URL
SQLITE_FALLBACK_URL = os.getenv("SQLITE_FALLBACK_URL", DEFAULT_SQLITE_URL)


def create_db_engine(db_url: str):
    """
    Creates SQLAlchemy engine with driver-specific arguments.
    """
    is_sqlite = db_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    
    return create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )


# Attempt to initialize database engine with graceful fallback if local PostgreSQL server is offline
active_db_url = DATABASE_URL
try:
    engine = create_db_engine(active_db_url)
    # Test connection
    with engine.connect() as conn:
        pass
    print(f"[Database] Successfully connected to database: {active_db_url.split('@')[-1]}")
except Exception as err:
    if not active_db_url.startswith("sqlite"):
        print(f"[Database Notice] PostgreSQL connection to '{DATABASE_URL}' was not established: {err}")
        print(f"[Database] Falling back to SQLite database: {SQLITE_FALLBACK_URL}")
        active_db_url = SQLITE_FALLBACK_URL
        engine = create_db_engine(active_db_url)
    else:
        raise err

# Auto-patch SQLite table columns if fallback database is missing new traceability columns
if active_db_url.startswith("sqlite"):
    for col_def in [
        "ALTER TABLE analysis_records ADD COLUMN business_profile_id VARCHAR",
        "ALTER TABLE analysis_records ADD COLUMN business_name VARCHAR",
        "ALTER TABLE analysis_records ADD COLUMN original_business_description TEXT",
        "ALTER TABLE analysis_records ADD COLUMN extraction_metadata TEXT",
        "ALTER TABLE users ADD COLUMN password_hash VARCHAR",
        "ALTER TABLE analysis_records ADD COLUMN user_id VARCHAR",
        "ALTER TABLE analysis_records ADD COLUMN is_deleted BOOLEAN DEFAULT 0",
        "ALTER TABLE analysis_audit_logs ADD COLUMN business_name VARCHAR"
    ]:
        try:
            with engine.connect() as conn:
                conn.execute(text(col_def))
                conn.commit()
        except Exception:
            pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    FastAPI dependency yielding database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
