"""
认证服务
处理用户认证、JWT Token 生成和验证
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"  # 生产环境请修改为随机密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24  # Token 有效期 24 小时

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer 认证方案
security = HTTPBearer()


class AuthService:
    """认证服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_password_hash(self, password: str) -> str:
        """
        对密码进行 bcrypt 加密
        """
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码是否正确
        """
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(
        self,
        username: str,
        password: str,
        real_name: str,
        is_admin: bool = False
    ) -> User:
        """
        创建新用户
        """
        # 检查用户名是否已存在
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            raise ValueError(f"用户名 {username} 已存在")

        # 创建用户
        hashed_password = self.get_password_hash(password)
        user = User(
            username=username,
            hashed_password=hashed_password,
            real_name=real_name,
            is_admin=is_admin,
            is_active=True
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户登录
        返回用户对象，如果验证失败返回 None
        """
        user = self.db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    def create_access_token(self, user: User) -> str:
        """
        为用户创建 JWT Token
        """
        expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        expire = datetime.utcnow() + expires_delta

        to_encode = {
            "sub": str(user.id),  # subject: 用户 ID
            "username": user.username,
            "is_admin": user.is_admin,
            "exp": expire  # expiration time
        }

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        """
        解码并验证 JWT Token
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据 ID 获取用户
        """
        return self.db.query(User).filter(User.id == user_id).first()


# 依赖注入函数：获取当前登录用户
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    从 JWT Token 中获取当前登录用户
    用于保护需要登录的接口
    """
    token = credentials.credentials
    auth_service = AuthService(db)

    try:
        payload = auth_service.decode_token(token)
        user_id = int(payload.get("sub"))

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据"
            )

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据"
        )

    user = auth_service.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


# 可选的依赖注入：获取当前用户（如果已登录）
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    可选的用户认证，如果未登录返回 None
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
