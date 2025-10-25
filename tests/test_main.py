import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import Quote

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def clean_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client(clean_db: None):
    with TestClient(app) as client:
        yield client


@pytest.mark.asyncio
async def test_read_main(async_client: TestClient):
    response = async_client.get("/")
    assert response.status_code == 200
    assert (
        "No quotes available. Add one!" in response.text
    )


@pytest.mark.asyncio
async def test_add_quote_form(async_client: TestClient):
    response = async_client.get("/add-quote")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_quote(async_client: TestClient):
    response = async_client.post(
        "/add-quote",
        data={"text": "Test quote", "author": "Test author"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/"

    # Verify the quote was added
    response = async_client.get("/")
    assert response.status_code == 200
    assert "Test quote" in response.text
    assert "Test author" in response.text


@pytest.mark.asyncio
async def test_random_quote_no_quotes(async_client: TestClient):
    response = async_client.get("/random-quote")
    assert response.status_code == 200
    assert (
        "No quotes available. Add one first!" in response.text
    )


@pytest.mark.asyncio
async def test_random_quote_with_quotes(async_client: TestClient):
    async_client.post(
        "/add-quote",
        data={"text": "Quote 1", "author": "Author 1"},
        follow_redirects=False,
    )
    async_client.post(
        "/add-quote",
        data={"text": "Quote 2", "author": "Author 2"},
        follow_redirects=False,
    )
    response = async_client.get("/random-quote")
    assert response.status_code == 200
    assert "Quote 1" in response.text or "Quote 2" in response.text

@pytest.mark.asyncio
async def test_search_quotes_found(async_client: TestClient):
    # Add a quote to the database
    async_client.post(
        "/add-quote",
        data={"text": "This is a test quote", "author": "Test Author"},
        follow_redirects=False,
    )

    # Search for the quote
    response = async_client.get("/search?q=test")
    assert response.status_code == 200
    assert "Search Results" in response.text
    assert "This is a test quote" in response.text
    assert "Test Author" in response.text

@pytest.mark.asyncio
async def test_search_quotes_not_found(async_client: TestClient):
    response = async_client.get("/search?q=nonexistent")
    assert response.status_code == 200
    assert "Search Results" in response.text
    assert "No results found." in response.text