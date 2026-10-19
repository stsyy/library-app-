import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.test_client() as client:
        yield client


@pytest.fixture
def author(client):
    return client.post("/api/authors", json={"full_name": "Лев Толстой", "country": "Россия", "birth_year": 1828}).get_json()


@pytest.fixture
def genre(client):
    return client.post("/api/genres", json={"name": "Роман"}).get_json()


@pytest.fixture
def book(client, author, genre):
    return client.post(
        "/api/books", json={"title": "Война и мир", "year": 1869, "author_id": author["id"], "genre_id": genre["id"]}
    ).get_json()


@pytest.fixture
def reader(client):
    return client.post("/api/readers", json={"full_name": "Иван Иванов", "email": "ivan@example.com"}).get_json()
