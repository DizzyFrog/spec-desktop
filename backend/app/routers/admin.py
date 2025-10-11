"""
管理员专用路由
仅管理员可以访问这些接口
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService, get_current_user
from app.services.cache_service import cache_service

router = APIRouter()


# Request/Response Models
class CreateUserRequest(BaseModel):
    username: str
    password: str
    real_name: str
    is_admin: bool = False


class UpdateUserRequest(BaseModel):
    real_name: str = None
    is_active: bool = None
    is_admin: bool = None


class ResetPasswordRequest(BaseModel):
    new_password: str


class ClearAllCacheRequest(BaseModel):
    clear_cache: bool = True
    clear_uploads: bool = True
    clear_outputs: bool = True


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str
    is_admin: bool
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True


def require_admin(current_user: User = Depends(get_current_user)):
    """验证当前用户是否为管理员"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足，需要管理员权限")
    return current_user


@router.get("/users")
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """获取所有用户列表（仅管理员）"""
    users = db.query(User).order_by(User.created_at.desc()).all()

    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })

    return {
        "code": 0,
        "data": {
            "users": user_list,
            "total": len(user_list)
        }
    }


@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """创建新用户（仅管理员）"""
    auth_service = AuthService(db)

    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 密码长度验证
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于 6 位")

    try:
        user = auth_service.create_user(
            username=request.username,
            password=request.password,
            real_name=request.real_name,
            is_admin=request.is_admin
        )

        return {
            "code": 0,
            "data": {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "is_admin": user.is_admin,
                "message": "用户创建成功"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """更新用户信息（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新字段
    if request.real_name is not None:
        user.real_name = request.real_name
    if request.is_active is not None:
        user.is_active = request.is_active
    if request.is_admin is not None:
        # 防止最后一个管理员被取消管理员权限
        if not request.is_admin and user.is_admin:
            admin_count = db.query(User).filter(User.is_admin == True).count()
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="至少需要保留一个管理员账号")
        user.is_admin = request.is_admin

    try:
        db.commit()
        db.refresh(user)

        return {
            "code": 0,
            "data": {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
                "message": "用户信息已更新"
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新用户失败: {str(e)}")


@router.post("/users/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """重置用户密码（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 密码长度验证
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于 6 位")

    try:
        auth_service = AuthService(db)
        user.hashed_password = auth_service.get_password_hash(request.new_password)
        db.commit()

        return {
            "code": 0,
            "data": {
                "message": f"用户 {user.username} 的密码已重置"
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"重置密码失败: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """删除用户（仅管理员）"""
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 防止删除最后一个管理员
    if user.is_admin:
        admin_count = db.query(User).filter(User.is_admin == True).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="不能删除最后一个管理员账号")

    try:
        db.delete(user)
        db.commit()

        return {
            "code": 0,
            "data": {
                "message": f"用户 {user.username} 已删除"
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """获取系统统计信息（仅管理员）"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()

    return {
        "code": 0,
        "data": {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "inactive_users": total_users - active_users
        }
    }


@router.get("/cache/stats")
async def get_all_cache_stats(
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """获取所有用户的缓存统计（仅管理员）"""
    stats = cache_service.get_all_users_cache_stats()

    # 计算总计
    total_cache_size = sum(s["cache_size"] for s in stats)
    total_upload_size = sum(s["upload_size"] for s in stats)
    total_output_size = sum(s["output_size"] for s in stats)
    total_size = sum(s["total_size"] for s in stats)
    total_files = sum(s["total_files"] for s in stats)

    return {
        "code": 0,
        "data": {
            "users": stats,
            "summary": {
                "total_users": len(stats),
                "total_cache_size": total_cache_size,
                "total_upload_size": total_upload_size,
                "total_output_size": total_output_size,
                "total_size": total_size,
                "total_files": total_files,
                "total_size_mb": round(total_size / 1024 / 1024, 2)
            }
        }
    }


@router.post("/cache/clear-all")
async def clear_all_cache(
    request: ClearAllCacheRequest,
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """清理所有用户的缓存（仅管理员）"""
    result = cache_service.clear_all_users_cache(
        clear_cache=request.clear_cache,
        clear_uploads=request.clear_uploads,
        clear_outputs=request.clear_outputs
    )

    print(f"🗑️  管理员 {current_user.username} 清理了所有用户缓存: {result['message']}")

    return {
        "code": 0,
        "data": {
            "success": result["success"],
            "users_cleared": result["users_cleared"],
            "message": result["message"]
        }
    }


@router.post("/cache/clear-user/{user_id}")
async def clear_user_cache(
    user_id: int,
    request: ClearAllCacheRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """清理指定用户的缓存（仅管理员）"""
    # 验证用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    result = cache_service.clear_user_cache(
        user_id,
        clear_cache=request.clear_cache,
        clear_uploads=request.clear_uploads,
        clear_outputs=request.clear_outputs
    )

    print(f"🗑️  管理员 {current_user.username} 清理了用户 {user.username} (ID: {user_id}) 的缓存")

    return {
        "code": 0,
        "data": {
            "success": result["success"],
            "user_id": user_id,
            "username": user.username,
            "cleared": result["cleared"],
            "message": result["message"]
        }
    }
