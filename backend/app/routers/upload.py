"""
文件上传路由
"""
import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter()

# 使用一个固定的、可预见的临时目录
UPLOAD_BASE_DIR = os.path.join(tempfile.gettempdir(), "spec-desktop-uploads")
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)


def _get_user_upload_dir(user_id: int) -> str:
    """
    获取用户专属的上传目录
    每个用户有独立的文件存储空间
    """
    user_upload_dir = os.path.join(UPLOAD_BASE_DIR, f'user_{user_id}')
    os.makedirs(user_upload_dir, exist_ok=True)
    return user_upload_dir

@router.post("/excel")
async def upload_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    接收 Excel 文件上传，保存到用户专属的临时目录，并返回文件路径。需要登录。
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="没有提供文件名")

    # 获取用户专属的上传目录
    user_upload_dir = _get_user_upload_dir(current_user.id)

    # 为了避免文件名冲突，可以使用更唯一的文件名
    _, ext = os.path.splitext(file.filename)
    temp_file_path = os.path.join(user_upload_dir, f"{os.urandom(8).hex()}{ext}")

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"📤 用户 {current_user.username} (ID: {current_user.id}) 上传文件: {temp_file_path}")

        return {
            "code": 0,
            "data": {
                "file_path": temp_file_path
            }
        }
    except Exception as e:
        print(f"文件上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    finally:
        file.file.close()