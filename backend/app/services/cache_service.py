"""
缓存清理服务
提供用户级别的缓存和临时文件清理功能
"""
import os
import shutil
import tempfile
from typing import Dict, List, Optional
from pathlib import Path


class CacheService:
    """缓存清理服务"""

    def __init__(self):
        # 缓存目录（Mermaid 图片）
        self.cache_base_dir = Path(tempfile.gettempdir()) / 'spec-desktop-backend' / 'cache'
        # 上传目录（Excel 文件）
        self.upload_base_dir = Path(tempfile.gettempdir()) / 'spec-desktop-uploads'
        # 输出目录（Word 文档）
        self.output_base_dir = Path(tempfile.gettempdir()) / 'spec-desktop-backend' / 'outputs'

    def get_user_cache_size(self, user_id: int) -> Dict[str, int]:
        """
        获取用户缓存大小统计

        Args:
            user_id: 用户 ID

        Returns:
            {
                "cache_size": 缓存目录大小（字节）,
                "upload_size": 上传目录大小（字节）,
                "output_size": 输出目录大小（字节）,
                "total_size": 总大小（字节）,
                "cache_files": 缓存文件数量,
                "upload_files": 上传文件数量,
                "output_files": 输出文件数量
            }
        """
        def get_dir_size(directory: Path) -> tuple[int, int]:
            """返回 (size, file_count)"""
            if not directory.exists():
                return 0, 0

            total_size = 0
            file_count = 0
            for item in directory.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
                    file_count += 1
            return total_size, file_count

        user_cache_dir = self.cache_base_dir / f'user_{user_id}'
        user_upload_dir = self.upload_base_dir / f'user_{user_id}'
        user_output_dir = self.output_base_dir / f'user_{user_id}'

        cache_size, cache_files = get_dir_size(user_cache_dir)
        upload_size, upload_files = get_dir_size(user_upload_dir)
        output_size, output_files = get_dir_size(user_output_dir)

        return {
            "cache_size": cache_size,
            "upload_size": upload_size,
            "output_size": output_size,
            "total_size": cache_size + upload_size + output_size,
            "cache_files": cache_files,
            "upload_files": upload_files,
            "output_files": output_files
        }

    def clear_user_cache(
        self,
        user_id: int,
        clear_cache: bool = True,
        clear_uploads: bool = True,
        clear_outputs: bool = True
    ) -> Dict[str, any]:
        """
        清理用户缓存

        Args:
            user_id: 用户 ID
            clear_cache: 是否清理缓存目录（Mermaid 图片）
            clear_uploads: 是否清理上传目录（Excel 文件）
            clear_outputs: 是否清理输出目录（Word 文档）

        Returns:
            {
                "success": True,
                "cleared": {
                    "cache": bool,
                    "uploads": bool,
                    "outputs": bool
                },
                "message": "清理结果描述"
            }
        """
        cleared = {"cache": False, "uploads": False, "outputs": False}
        messages = []

        # 清理缓存目录
        if clear_cache:
            user_cache_dir = self.cache_base_dir / f'user_{user_id}'
            if user_cache_dir.exists():
                try:
                    shutil.rmtree(user_cache_dir)
                    user_cache_dir.mkdir(parents=True, exist_ok=True)
                    cleared["cache"] = True
                    messages.append("缓存目录已清理")
                except Exception as e:
                    messages.append(f"清理缓存目录失败: {str(e)}")

        # 清理上传目录
        if clear_uploads:
            user_upload_dir = self.upload_base_dir / f'user_{user_id}'
            if user_upload_dir.exists():
                try:
                    shutil.rmtree(user_upload_dir)
                    user_upload_dir.mkdir(parents=True, exist_ok=True)
                    cleared["uploads"] = True
                    messages.append("上传目录已清理")
                except Exception as e:
                    messages.append(f"清理上传目录失败: {str(e)}")

        # 清理输出目录
        if clear_outputs:
            user_output_dir = self.output_base_dir / f'user_{user_id}'
            if user_output_dir.exists():
                try:
                    shutil.rmtree(user_output_dir)
                    user_output_dir.mkdir(parents=True, exist_ok=True)
                    cleared["outputs"] = True
                    messages.append("输出目录已清理")
                except Exception as e:
                    messages.append(f"清理输出目录失败: {str(e)}")

        return {
            "success": True,
            "cleared": cleared,
            "message": "、".join(messages) if messages else "没有可清理的内容"
        }

    def clear_all_users_cache(
        self,
        clear_cache: bool = True,
        clear_uploads: bool = True,
        clear_outputs: bool = True
    ) -> Dict[str, any]:
        """
        清理所有用户的缓存（管理员功能）

        Args:
            clear_cache: 是否清理缓存目录
            clear_uploads: 是否清理上传目录
            clear_outputs: 是否清理输出目录

        Returns:
            {
                "success": True,
                "users_cleared": int,
                "message": "清理结果描述"
            }
        """
        users_cleared = set()
        messages = []

        # 清理缓存目录
        if clear_cache and self.cache_base_dir.exists():
            try:
                for user_dir in self.cache_base_dir.glob('user_*'):
                    if user_dir.is_dir():
                        shutil.rmtree(user_dir)
                        users_cleared.add(user_dir.name)
                messages.append(f"清理了缓存目录")
            except Exception as e:
                messages.append(f"清理缓存目录失败: {str(e)}")

        # 清理上传目录
        if clear_uploads and self.upload_base_dir.exists():
            try:
                for user_dir in self.upload_base_dir.glob('user_*'):
                    if user_dir.is_dir():
                        shutil.rmtree(user_dir)
                        users_cleared.add(user_dir.name)
                messages.append(f"清理了上传目录")
            except Exception as e:
                messages.append(f"清理上传目录失败: {str(e)}")

        # 清理输出目录
        if clear_outputs and self.output_base_dir.exists():
            try:
                for user_dir in self.output_base_dir.glob('user_*'):
                    if user_dir.is_dir():
                        shutil.rmtree(user_dir)
                        users_cleared.add(user_dir.name)
                messages.append(f"清理了输出目录")
            except Exception as e:
                messages.append(f"清理输出目录失败: {str(e)}")

        return {
            "success": True,
            "users_cleared": len(users_cleared),
            "message": "、".join(messages) if messages else "没有可清理的内容"
        }

    def get_all_users_cache_stats(self) -> List[Dict[str, any]]:
        """
        获取所有用户的缓存统计（管理员功能）

        Returns:
            [
                {
                    "user_id": int,
                    "cache_size": int,
                    "upload_size": int,
                    "output_size": int,
                    "total_size": int,
                    "total_files": int
                },
                ...
            ]
        """
        stats = []
        user_ids = set()

        # 收集所有用户 ID
        for base_dir in [self.cache_base_dir, self.upload_base_dir, self.output_base_dir]:
            if base_dir.exists():
                for user_dir in base_dir.glob('user_*'):
                    if user_dir.is_dir():
                        user_id_str = user_dir.name.replace('user_', '')
                        if user_id_str.isdigit():
                            user_ids.add(int(user_id_str))

        # 获取每个用户的统计
        for user_id in sorted(user_ids):
            user_stats = self.get_user_cache_size(user_id)
            stats.append({
                "user_id": user_id,
                "cache_size": user_stats["cache_size"],
                "upload_size": user_stats["upload_size"],
                "output_size": user_stats["output_size"],
                "total_size": user_stats["total_size"],
                "total_files": (
                    user_stats["cache_files"] +
                    user_stats["upload_files"] +
                    user_stats["output_files"]
                )
            })

        return stats


# 全局实例
cache_service = CacheService()
