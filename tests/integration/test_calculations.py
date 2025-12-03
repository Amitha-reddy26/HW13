import pytest
import requests
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture
def create_payload():
    return {
        "operation": "add",
        "a": 10,
        "b": 20
    }


# ---------------------------------------------------------
# CREATE Calculation
# ---------------------------------------------------------
def test_create_calculation(fastapi_server, db_session, create_payload):
    url = f"{BASE_URL}/calculations/"
    response = requests.post(url, json=create_payload)

    assert response.status_code == 200
    data = response.json()

    assert data["operation"] == "add"
    assert data["a"] == 10
    assert data["b"] == 20
    assert data["result"] == 30.0

    # Verify in DB
    calc_id = data["id"]
    calc = db_session.query(Calculation).filter_by(id=calc_id).first()
    assert calc is not None
    assert calc.result == 30.0


# ---------------------------------------------------------
# READ Calculation
# ---------------------------------------------------------
def test_read_calculation(fastapi_server, db_session):
    # create one directly in DB
    calc = Calculation(operation="multiply", a=3, b=4, result=12)
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    url = f"{BASE_URL}/calculations/{calc.id}"
    response = requests.get(url)

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(calc.id)
    assert data["operation"] == "multiply"
    assert data["result"] == 12


# ---------------------------------------------------------
# BROWSE Calculations
# ---------------------------------------------------------
def test_browse_calculations(fastapi_server, db_session):
    # seed some data
    c1 = Calculation(operation="add", a=1, b=2, result=3)
    c2 = Calculation(operation="subtract", a=10, b=5, result=5)
    db_session.add_all([c1, c2])
    db_session.commit()

    url = f"{BASE_URL}/calculations/"
    response = requests.get(url)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2  # at least the two items we added


# ---------------------------------------------------------
# UPDATE Calculation
# ---------------------------------------------------------
def test_update_calculation(fastapi_server, db_session):
    calc = Calculation(operation="add", a=5, b=5, result=10)
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    url = f"{BASE_URL}/calculations/{calc.id}"
    payload = {
        "operation": "multiply",
        "a": 5,
        "b": 3
    }

    response = requests.put(url, json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["operation"] == "multiply"
    assert data["result"] == 15


# ---------------------------------------------------------
# DELETE Calculation
# ---------------------------------------------------------
def test_delete_calculation(fastapi_server, db_session):
    calc = Calculation(operation="subtract", a=20, b=5, result=15)
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    url = f"{BASE_URL}/calculations/{calc.id}"
    
    response = requests.delete(url)
    assert response.status_code == 204  # No content

    # Ensure row deleted
    lookup = db_session.query(Calculation).filter_by(id=calc.id).first()
    assert lookup is None


# ---------------------------------------------------------
# INVALID operation
# ---------------------------------------------------------
def test_invalid_operation(fastapi_server):
    url = f"{BASE_URL}/calculations/"
    payload = {
        "operation": "square_root",  # invalid
        "a": 10,
        "b": 2
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 400
    assert "Invalid operation" in response.text


# ---------------------------------------------------------
# INVALID input type
# ---------------------------------------------------------
def test_invalid_input_type(fastapi_server):
    url = f"{BASE_URL}/calculations/"
    payload = {
        "operation": "add",
        "a": "not_a_number",
        "b": 10
    }

    response = requests.post(url, json=payload)
    assert response.status_code == 400  # FastAPI validation error