"""
缓存管理路由
提供用户级别的缓存查看和清理功能
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any
from pydantic import BaseModel

from app.models.user import User
from app.services.auth_service import get_current_user
from app.services.cache_service import cache_service

router = APIRouter()


# Request Models
class ClearCacheRequest(BaseModel):
    clear_cache: bool = True  # 清理 Mermaid 图片缓存
    clear_uploads: bool = True  # 清理上传的 Excel 文件
    clear_outputs: bool = True  # 清理生成的 Word 文档


@router.get("/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    获取当前用户的缓存统计信息
    包括缓存大小、文件数量等
    """
    stats = cache_service.get_user_cache_size(current_user.id)

    return {
        "code": 0,
        "data": {
            "user_id": current_user.id,
            "username": current_user.username,
            "cache_size": stats["cache_size"],
            "upload_size": stats["upload_size"],
            "output_size": stats["output_size"],
            "total_size": stats["total_size"],
            "cache_files": stats["cache_files"],
            "upload_files": stats["upload_files"],
            "output_files": stats["output_files"],
            "total_files": (
                stats["cache_files"] +
                stats["upload_files"] +
                stats["output_files"]
            ),
            # 友好的大小显示
            "total_size_mb": round(stats["total_size"] / 1024 / 1024, 2)
        }
    }


@router.post("/clear")
async def clear_cache(
    request: ClearCacheRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    清理当前用户的缓存
    可选择性清理缓存、上传文件、输出文件
    """
    result = cache_service.clear_user_cache(
        current_user.id,
        clear_cache=request.clear_cache,
        clear_uploads=request.clear_uploads,
        clear_outputs=request.clear_outputs
    )

    print(f"🗑️  用户 {current_user.username} (ID: {current_user.id}) 清理缓存: {result['message']}")

    return {
        "code": 0,
        "data": {
            "success": result["success"],
            "cleared": result["cleared"],
            "message": result["message"]
        }
    }
