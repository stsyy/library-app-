import pytest


def test_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}


# ---------- Genres ----------
def test_genre_crud(client):
    r = client.post("/api/genres", json={"name": "Фантастика", "description": "Sci-fi"})
    assert r.status_code == 201
    gid = r.get_json()["id"]

    assert client.get(f"/api/genres/{gid}").get_json()["name"] == "Фантастика"
    assert len(client.get("/api/genres").get_json()) == 1

    r = client.put(f"/api/genres/{gid}", json={"description": "Научная фантастика"})
    assert r.get_json()["description"] == "Научная фантастика"

    assert client.delete(f"/api/genres/{gid}").status_code == 204
    assert client.get(f"/api/genres/{gid}").status_code == 404


def test_genre_duplicate_name(client, genre):
    assert client.post("/api/genres", json={"name": "Роман"}).status_code == 400


# ---------- Authors ----------
def test_author_crud(client, author):
    aid = author["id"]
    assert client.get(f"/api/authors/{aid}").get_json()["birth_year"] == 1828
    r = client.put(f"/api/authors/{aid}", json={"country": "Российская империя"})
    assert r.get_json()["country"] == "Российская империя"
    assert client.delete(f"/api/authors/{aid}").status_code == 204
    assert client.get("/api/authors").get_json() == []


def test_author_requires_name(client):
    r = client.post("/api/authors", json={"country": "Франция"})
    assert r.status_code == 400
    assert "full_name" in r.get_json()["error"]


def test_author_invalid_year(client):
    assert client.post("/api/authors", json={"full_name": "X", "birth_year": "abc"}).status_code == 400


# ---------- Books ----------
def test_book_crud(client, book):
    bid = book["id"]
    assert client.get(f"/api/books/{bid}").get_json()["title"] == "Война и мир"
    r = client.put(f"/api/books/{bid}", json={"copies": 5})
    assert r.get_json()["copies"] == 5
    assert len(client.get("/api/books").get_json()) == 1
    assert client.delete(f"/api/books/{bid}").status_code == 204
    assert client.get(f"/api/books/{bid}").status_code == 404


def test_book_unknown_author(client):
    r = client.post("/api/books", json={"title": "Нет автора", "author_id": 999})
    assert r.status_code == 400
    assert "author 999 not found" in r.get_json()["error"]


def test_delete_author_cascades_books(client, author, book):
    client.delete(f"/api/authors/{author['id']}")
    assert client.get("/api/books").get_json() == []


# ---------- Readers ----------
def test_reader_crud(client, reader):
    rid = reader["id"]
    r = client.put(f"/api/readers/{rid}", json={"phone": "+7 900 000-00-00"})
    assert r.get_json()["phone"] == "+7 900 000-00-00"
    assert client.get(f"/api/readers/{rid}").get_json()["email"] == "ivan@example.com"
    assert client.delete(f"/api/readers/{rid}").status_code == 204


def test_reader_unique_email(client, reader):
    r = client.post("/api/readers", json={"full_name": "Другой", "email": "ivan@example.com"})
    assert r.status_code == 400


# ---------- Loans ----------
def test_loan_crud(client, book, reader):
    r = client.post(
        "/api/loans", json={"book_id": book["id"], "reader_id": reader["id"], "due_at": "2026-12-01"}
    )
    assert r.status_code == 201
    loan = r.get_json()
    assert loan["returned"] is False
    assert loan["due_at"] == "2026-12-01"

    r = client.put(f"/api/loans/{loan['id']}", json={"returned": True})
    assert r.get_json()["returned"] is True
    assert len(client.get("/api/loans").get_json()) == 1
    assert client.delete(f"/api/loans/{loan['id']}").status_code == 204


def test_loan_invalid_date(client, book, reader):
    r = client.post("/api/loans", json={"book_id": book["id"], "reader_id": reader["id"], "due_at": "31-12-2026"})
    assert r.status_code == 400


# ---------- Общие проверки ----------
@pytest.mark.parametrize("resource", ["genres", "authors", "books", "readers", "loans"])
def test_not_found(client, resource):
    assert client.get(f"/api/{resource}/12345").status_code == 404
    assert client.put(f"/api/{resource}/12345", json={}).status_code == 404
    assert client.delete(f"/api/{resource}/12345").status_code == 404


def test_book_search_by_title(client, author):
    for title in ["Война и мир", "Анна Каренина", "Воскресение"]:
        client.post("/api/books", json={"title": title, "author_id": author["id"]})
    found = client.get("/api/books?title=Анна").get_json()
    assert [b["title"] for b in found] == ["Анна Каренина"]
    assert len(client.get("/api/books?title=Вос").get_json()) == 1
