import sqlite3

from app.main import db_location

from fastapi.testclient import TestClient

# TODO Rename test files and group them properly (db tests, endpoints tests, ...)


def test_database_creation():
    # sqlite_db_file = "test.db"
    # os.remove(sqlite_db_file) if os.path.exists(sqlite_db_file) else None
    # SqlModelDataStore(f"sqlite:///{sqlite_db_file}")

    with sqlite3.connect(db_location) as connection:
        c = connection.cursor()
        c.execute("PRAGMA table_info(fastapi_sqlmodel_api_keys);")
        columns = c.fetchall()
        assert len(columns) == 7, columns


def test_api_key_name(client: TestClient, admin_key: str):
    response = client.get(url="/auth/new", headers={"x-secret-key": admin_key}, params={"name": "Test"})
    assert response.status_code == 200
    key = str(response.json())

    response = client.get("/auth/logs", headers={"x-secret-key": admin_key})
    assert response.status_code == 200
    data = [x for x in response.json()["logs"] if x.get("api_key") == key]
    assert len(data) == 1
    assert data[0].get("name") == "Test", data[0]


def test_api_key_never_expire(client: TestClient, admin_key: str):
    # Create with never_expires param
    response = client.get(
        url="/auth/new",
        headers={"x-secret-key": admin_key},
        params={"never_expires": True, "name": "Forever"},
    )
    assert response.status_code == 200

    response = client.get("/auth/logs", headers={"x-secret-key": admin_key})
    assert response.status_code == 200
    data = [x for x in response.json()["logs"] if x.get("name") == "Forever"]
    assert len(data) == 1
    assert data[0].get("never_expire") is True, data[0]
