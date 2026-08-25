from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config import settings
from database.connection import get_db
from database.crud import create_user, get_user_by_email, verify_password
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer()

# --- Request/Response schemas ---

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OnboardingRequest(BaseModel):
    current_year: str      # "1st Year" / "2nd Year" / "3rd Year" / "Final Year"
    interest_field: str    # "AI/ML" / "Web Development" / "DSA/CP" / "Core CS" / etc.
    target_role: str | None = None


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    onboarding_complete: bool
    current_year: str | None
    interest_field: str | None
    target_role: str | None

    class Config:
        from_attributes = True


# --- JWT helpers ---

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


# --- Routes ---

@router.post("/signup", response_model=TokenResponse)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = create_user(db, name=request.name, email=request.email, password=request.password)
    token = create_access_token({"sub": user.email})
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token({"sub": user.email})
    return {"access_token": token}


@router.post("/onboarding", response_model=UserProfileResponse)
def complete_onboarding(
    request: OnboardingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.current_year = request.current_year
    current_user.interest_field = request.interest_field
    current_user.target_role = request.target_role
    current_user.onboarding_complete = True
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user