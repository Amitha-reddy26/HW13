from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, Session

from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserResponse, Token

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(Base):
    __tablename__ = "users"

    # ---------------------------------------------------------------
    # Columns
    # ---------------------------------------------------------------
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    email = Column(String(120), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)

    password_hash = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    last_login = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ---------------------------------------------------------------
    # repr (your tests expect this style)
    # ---------------------------------------------------------------
    def __repr__(self):
        return f"<User(name={self.first_name} {self.last_name}, email={self.email})>"

    # ---------------------------------------------------------------
    # Custom __init__ so tests can pass password="..."
    # ---------------------------------------------------------------
    def __init__(self, **kwargs):
        raw_password = kwargs.pop("password", None)
        super().__init__(**kwargs)
        if raw_password is not None:
            self.password = raw_password   # triggers setter → hashes

    # ---------------------------------------------------------------
    # Password property (write-only)
    # ---------------------------------------------------------------
    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, raw_password: str):
        if raw_password is None:
            raise ValueError("Password cannot be None")
        self.password_hash = User.hash_password(raw_password)

    # ---------------------------------------------------------------
    # Password utilities
    # ---------------------------------------------------------------
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt (truncate at 72 bytes)."""
        return pwd_context.hash(password[:72])

    def verify_password(self, plain_password: str) -> bool:
        """Verify plaintext password against stored hash."""
        return pwd_context.verify(plain_password[:72], self.password_hash)

    # ---------------------------------------------------------------
    # JWT utilities
    # ---------------------------------------------------------------
    @staticmethod
    def create_access_token(data: dict,
                            expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[uuid.UUID]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            return uuid.UUID(user_id) if user_id else None
        except (JWTError, ValueError):
            return None

    # ---------------------------------------------------------------
    # Registration method (used by router)
    # ---------------------------------------------------------------
    @classmethod
    def register(cls, db: Session, user_data: Dict[str, Any]) -> "User":

        # basic validation before Pydantic
        raw_pw = user_data.get("password")
        if not raw_pw or len(raw_pw) < 6:
            raise ValueError("Password must be at least 6 characters long")

        # uniqueness check
        existing = db.query(cls).filter(
            (cls.email == user_data.get("email")) |
            (cls.username == user_data.get("username"))
        ).first()

        if existing:
            raise ValueError("Username or email already exists")

        # Validate with Pydantic
        try:
            validated = UserCreate.model_validate(user_data)
        except ValidationError as e:
            raise ValueError(str(e))

        # Create user instance
        new_user = cls(
            first_name=validated.first_name,
            last_name=validated.last_name,
            email=validated.email,
            username=validated.username,
        )

        # Hash password through setter
        new_user.password = validated.password

        db.add(new_user)
        db.flush()       # Assigns UUID immediately for token creation

        return new_user

    # ---------------------------------------------------------------
    # Authentication method (used by router)
    # ---------------------------------------------------------------
    @classmethod
    def authenticate(cls, db: Session,
                     username: str, password: str) -> Optional[Dict[str, Any]]:

        user = db.query(cls).filter(
            (cls.username == username) |
            (cls.email == username)
        ).first()

        if not user or not user.verify_password(password):
            return None

        user.last_login = datetime.utcnow()
        db.commit()

        user_res = UserResponse.model_validate(user)

        token = cls.create_access_token({"sub": str(user.id)})

        token_obj = Token(
            access_token=token,
            token_type="bearer",
            user=user_res
        )

        return token_obj.model_dump()