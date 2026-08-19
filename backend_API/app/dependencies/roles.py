from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user

def require_instructor_or_admin(current_user = Depends(get_current_user)):
    user_role = current_user.role.name.lower()

    if user_role not in ["admin", "instructor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors or admins can manage lessons"
        )

    return current_user