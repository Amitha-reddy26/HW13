from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------
@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    - Receives username/email/password
    - Validates (checks duplicates, hashes PW)
    - Stores in DB
    - Returns JWT + user object
    """
    try:
        new_user = User.register(db, user_data.model_dump())
        db.commit()
        db.refresh(new_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = User.create_access_token({"sub": str(new_user.id)})

    return Token(
        access_token=token,
        user=new_user
    )


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------
@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    - Valid username/email + password => return JWT
    - Invalid => 401 Unauthorized
    """
    result = User.authenticate(
        db=db,
        username=credentials.username,
        password=credentials.password
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return result