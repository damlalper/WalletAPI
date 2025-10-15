import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base
from app.deps import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


import time

@pytest.fixture
def client():
    print("Creating client and database")
    Base.metadata.create_all(bind=engine)
    time.sleep(1)
    db = TestingSessionLocal()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(bind=engine)
    print("Client and database destroyed")


def test_create_expense(client):
    response = client.post(
        "/expenses",
        json={
            "title": "Test Expense",
            "amount": "10.50",
            "currency": "USD",
            "category": "Test",
            "spent_at": "2025-10-15T10:00:00Z",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Expense"
    assert data["amount"] == "10.50"
    assert "id" in data


def test_read_expense(client):
    response = client.post(
        "/expenses",
        json={
            "title": "Test Expense",
            "amount": "10.50",
            "currency": "USD",
            "category": "Test",
            "spent_at": "2025-10-15T10:00:00Z",
        },
    )
    expense_id = response.json()["id"]

    response = client.get(f"/expenses/{expense_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Expense"


def test_read_expenses(client):
    client.post(
        "/expenses",
        json={
            "title": "Test Expense 1",
            "amount": "10.50",
            "currency": "USD",
            "category": "Test",
            "spent_at": "2025-10-15T10:00:00Z",
        },
    )
    client.post(
        "/expenses",
        json={
            "title": "Test Expense 2",
            "amount": "20.00",
            "currency": "USD",
            "category": "Test",
            "spent_at": "2025-10-15T11:00:00Z",
        },
    )

    response = client.get("/expenses?limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/expenses?offset=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_expense(client):
    response = client.post(
        "/expenses",
        json={
            "title": "Test Expense",
            "amount": "10.50",
            "currency": "USD",
            "category": "Test",
            "spent_at": "2025-10-15T10:00:00Z",
        },
    )
    expense_id = response.json()["id"]

    response = client.patch(f"/expenses/{expense_id}", json={"title": "Updated Title"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


def test_delete_expense(client):
    response = client.post(
        "/expenses",
        json={
            "title": "Test Expense",
            "amount": "10.50",
            "currency": "USD",
            "category": "Test",
            "spent_at": "2025-10-15T10:00:00Z",
        },
    )
    expense_id = response.json()["id"]

    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 204

    response = client.get(f"/expenses/{expense_id}")
    assert response.status_code == 404


def test_summary_report(client):
    client.post(
        "/expenses",
        json={
            "title": "Expense 1",
            "amount": "10.00",
            "currency": "USD",
            "category": "Food",
            "spent_at": "2025-10-15T10:00:00Z",
        },
    )
    client.post(
        "/expenses",
        json={
            "title": "Expense 2",
            "amount": "20.00",
            "currency": "USD",
            "category": "Transport",
            "spent_at": "2025-10-16T11:00:00Z",
        },
    )

    response = client.get("/reports/summary?from_date=2025-10-15&to_date=2025-10-17&group_by=category")
    assert response.status_code == 200
    data = response.json()
    assert data["grand_total"] == "30.00"
    assert len(data["buckets"]) == 2


def test_export_csv(client):
    client.post(
        "/expenses",
        json={
            "title": "Test Expense",
            "amount": "10.50",
            "currency": "USD",
            "category": "Test",
            "spent_at": "2025-10-15T10:00:00Z",
        },
    )
    response = client.get("/export?from_date=2025-10-15&to_date=2025-10-16&format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Test Expense" in response.text


def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Wallet"