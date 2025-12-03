from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.calculation import CalculationCreate, CalculationRead
from app.models.calculation import Calculation
from app.operations import add, subtract, multiply, divide

router = APIRouter(prefix="/calculations", tags=["Calculations"])

OPERATION_MAP = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
}

@router.get("/", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).all()


@router.get("/{calc_id}", response_model=CalculationRead)
def read_calculation(calc_id: str, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calc


@router.post("/", response_model=CalculationRead)
def create_calculation(payload: CalculationCreate, db: Session = Depends(get_db)):

    if payload.operation not in OPERATION_MAP:
        raise HTTPException(status_code=400, detail="Invalid operation")

    operation_fn = OPERATION_MAP[payload.operation]
    result = operation_fn(payload.a, payload.b)

    calc = Calculation(
        operation=payload.operation,
        a=payload.a,
        b=payload.b,
        result=result,
    )

    db.add(calc)
    db.commit()
    db.refresh(calc)

    return calc


@router.put("/{calc_id}", response_model=CalculationRead)
def update_calculation(calc_id: str, payload: CalculationCreate, db: Session = Depends(get_db)):

    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    if payload.operation not in OPERATION_MAP:
        raise HTTPException(status_code=400, detail="Invalid operation")

    operation_fn = OPERATION_MAP[payload.operation]
    calc.result = operation_fn(payload.a, payload.b)

    calc.operation = payload.operation
    calc.a = payload.a
    calc.b = payload.b

    db.commit()
    db.refresh(calc)

    return calc


@router.delete("/{calc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calc_id: str, db: Session = Depends(get_db)):
    calc = db.query(Calculation).filter(Calculation.id == calc_id).first()
    if not calc:
        raise HTTPException(status_code=404, detail="Calculation not found")

    db.delete(calc)
    db.commit()