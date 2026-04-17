from fastapi import Depends,HTTPException 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt,JWTError
from app.core.config import get_settings

settings = get_settings()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM],options={"verify_aud": False})
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
