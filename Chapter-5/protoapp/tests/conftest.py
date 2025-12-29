import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from protoapp.database import Base
from protoapp.main import app, get_db_session


@pytest.fixture(scope="function")
def db_session_test():
    # Setup code for database session (e.g., create tables, connect to test DB)
    yield
    # Teardown code for database session (e.g., drop tables, disconnect from test DB)
@pytest.fixture(scope="function")
def test_client(db_session_test):
    client = TestClient(app)
    
    app.dependency_overrides[get_db_session] = (lambda: db_session_test)
    
    return client 
    
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine)  # Bind the engine


TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

@pytest.fixture
def test_db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()