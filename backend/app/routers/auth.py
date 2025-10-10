"""
认证相关路由
提供真实的用户登录认证
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

from app.database import get_db
from app.services.auth_service import AuthService, get_current_user
from app.models.user import User

router = APIRouter()


# Request/Response Models
class LoginParams(BaseModel):
    username: str
    password: str


class LoginResult(BaseModel):
    accessToken: str


@router.post("/login")
async def login(params: LoginParams, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    用户登录接口
    验证用户名密码，返回 JWT Token
    """
    auth_service = AuthService(db)

    # 验证用户
    user = auth_service.authenticate_user(params.username, params.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 生成 Token
    access_token = auth_service.create_access_token(user)

    print(f"✅ 用户登录成功: {user.username} (ID: {user.id})")

    return {
        "code": 0,
        "data": {
            "accessToken": access_token
        }
    }


@router.get("/getUserInfo")
async def get_user_info(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    获取当前登录用户信息
    需要在 Header 中携带 Authorization: Bearer <token>
    """
    return {
        "code": 0,
        "data": {
            "userId": str(current_user.id),
            "username": current_user.username,
            "realName": current_user.real_name,
            "avatar": "https://unpkg.com/@vbenjs/static-source@0.1.7/source/avatar-v1.webp",
            "desc": "管理员" if current_user.is_admin else "普通用户",
            "homePath": "/spec/generator",
            "roles": ["admin"] if current_user.is_admin else ["user"]
        }
    }


@router.get("/codes")
async def get_access_codes(current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    获取用户权限码
    管理员返回 ["admin", "user"]，普通用户返回 ["user"]
    """
    codes = ["admin", "user"] if current_user.is_admin else ["user"]

    return {
        "code": 0,
        "data": codes
    }


@router.post("/logout")
async def logout() -> Dict[str, Any]:
    """
    退出登录
    前端应该删除本地存储的 Token
    """
    return {
        "code": 0,
        "data": "ok"
    }


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    刷新 Token
    使用现有 Token 获取新的 Token
    """
    auth_service = AuthService(db)
    new_token = auth_service.create_access_token(current_user)

    return {
        "code": 0,
        "data": new_token
    }
