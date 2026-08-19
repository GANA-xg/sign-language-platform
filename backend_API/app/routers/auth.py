from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.refresh_token import RefreshToken

from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenPairResponse,
    RefreshTokenRequest,
)

from app.schemas.user import (
    UpdateProfileRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_user_roles,
    generate_refresh_token,
    hash_refresh_token,
)

from app.core.limiter import limiter
from app.core.account_rate_limiter import (
    is_rate_limited,
    reset_attempts,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

DEFAULT_ROLE = "learner"


# ============================================================
# PROFILE
# ============================================================

@router.get(
    "/profile",
    response_model=UserResponse,
    summary="Get current user's profile",
)
def get_profile(current_user: User = Depends(get_current_user)):
    user_roles = get_user_roles(current_user)
    return UserResponse(
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        roles=user_roles,
        created_at=current_user.created_at,
    )


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user's profile",
)
def update_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.email is not None:
        existing = (
            db.query(User)
            .filter(
                User.email == payload.email,
                User.user_id != current_user.user_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
        current_user.email = payload.email

    db.commit()
    db.refresh(current_user)

    user_roles = get_user_roles(current_user)
    return UserResponse(
        user_id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        roles=user_roles,
        created_at=current_user.created_at,
    )


@router.put(
    "/me/password",
    summary="Change current user's password",
)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(
        payload.old_password,
        current_user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.password_hash = hash_password(
        payload.new_password
    )
    db.commit()
    return {"message": "Password changed successfully"}


REFRESH_TOKEN_EXPIRE_DAYS = 30

reset_tokens: dict[str, str] = {}


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Check existing email
    # --------------------------------------------------------

    existing = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # --------------------------------------------------------
    # Determine requested role
    # --------------------------------------------------------

    role_name = (
        payload.requested_role or DEFAULT_ROLE
    ).strip().lower()

    # Only learner/instructor can self-register.
    if role_name not in {"learner", "instructor"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Registration role must be either "
                "'learner' or 'instructor'."
            ),
        )

    # --------------------------------------------------------
    # Find role
    # --------------------------------------------------------

    role = (
        db.query(Role)
        .filter(Role.role_name == role_name)
        .first()
    )

    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Setup error: role '{role_name}' "
                "is missing."
            ),
        )

    # --------------------------------------------------------
    # Create user
    # --------------------------------------------------------

    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(new_user)
    db.flush()

    # --------------------------------------------------------
    # Assign EXACTLY ONE role
    # --------------------------------------------------------

    db.add(
        UserRole(
            user_id=new_user.user_id,
            role_id=role.role_id,
        )
    )

    db.commit()
    db.refresh(new_user)

    return UserResponse(
        user_id=new_user.user_id,
        full_name=new_user.full_name,
        email=new_user.email,
        roles=[role_name],
        created_at=new_user.created_at,
    )


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenPairResponse,
)
@limiter.limit("5/minute")
def login(
    request: Request,
    payload: UserLogin,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Rate limiting
    # --------------------------------------------------------

    account_key = f"login:{payload.email.lower()}"

    if is_rate_limited(
        account_key,
        max_attempts=5,
        window_seconds=60,
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Too many login attempts for this account. "
                "Please try again in a minute."
            ),
        )

    # --------------------------------------------------------
    # Find user
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.email == payload.email)
        .first()
    )

    print("===== LOGIN DEBUG =====")
    print("Email:", payload.email)
    print("User found:", user is not None)

    # --------------------------------------------------------
    # Validate credentials
    # --------------------------------------------------------

    if not user or not verify_password(
        payload.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    print(
        "Password valid:",
        verify_password(
            payload.password,
            user.password_hash,
        ),
    )

    print("Active:", user.is_active)

    # --------------------------------------------------------
    # Validate account
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    # --------------------------------------------------------
    # Get registered roles
    # --------------------------------------------------------

    user_roles = [
        role.strip().lower()
        for role in get_user_roles(user)
    ]

    print("Registered roles:", user_roles)
    print("Requested role:", payload.role)

    # --------------------------------------------------------
    # Account MUST have exactly one role
    # --------------------------------------------------------

    if len(user_roles) == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "This account has no role assigned. "
                "Contact an administrator."
            ),
        )

    if len(user_roles) > 1:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Account configuration error. "
                "Each account must have exactly one role."
            ),
        )

    registered_role = user_roles[0]

    # --------------------------------------------------------
    # Login role is REQUIRED
    # --------------------------------------------------------

    requested_role = (
        payload.role.strip().lower()
        if payload.role
        else None
    )

    if not requested_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select a role before logging in.",
        )

    # --------------------------------------------------------
    # THE IMPORTANT CHECK
    #
    # learner account + instructor login
    #        => REJECT
    #
    # instructor account + learner login
    #        => REJECT
    #
    # instructor account + instructor login
    #        => ALLOW
    # --------------------------------------------------------

    if requested_role != registered_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"This account is registered as "
                f"'{registered_role}' and cannot log in as "
                f"'{requested_role}'."
            ),
        )

    # --------------------------------------------------------
    # Successful login
    # --------------------------------------------------------

    reset_attempts(account_key)

    # IMPORTANT:
    # Token contains ONLY the registered role.
    active_roles = [registered_role]

    print("Registered role:", registered_role)
    print("Active role:", registered_role)

    # --------------------------------------------------------
    # Access token
    # --------------------------------------------------------

    access_token = create_access_token(
        {
            "sub": str(user.user_id),
            "roles": active_roles,
        }
    )

    # --------------------------------------------------------
    # Refresh token
    # --------------------------------------------------------

    raw_refresh, refresh_hash = generate_refresh_token()

    db.add(
        RefreshToken(
            user_id=user.user_id,
            token_hash=refresh_hash,
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(
                    days=REFRESH_TOKEN_EXPIRE_DAYS
                )
            ),
        )
    )

    db.commit()

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        token_type="bearer",
        user=UserResponse(
            user_id=user.user_id,
            full_name=user.full_name,
            email=user.email,
            roles=active_roles,
            created_at=user.created_at,
        ),
    )