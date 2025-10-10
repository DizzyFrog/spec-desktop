#!/usr/bin/env python3
"""
简化版管理员创建脚本
非交互式，直接创建默认管理员账号
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, get_db
from app.models.user import User
from app.services.auth_service import AuthService


def init_admin():
    """创建默认管理员账号"""
    print("=" * 50)
    print("初始化管理员账号")
    print("=" * 50)

    # 初始化数据库
    init_db()

    # 默认管理员信息
    username = "admin"
    password = "admin123"
    real_name = "管理员"

    # 创建管理员
    db = next(get_db())
    auth_service = AuthService(db)

    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == username).first()

        if existing_user:
            print(f"\n⚠️  管理员账号已存在，跳过创建")
            print(f"\n用户名: {existing_user.username}")
            print(f"姓名: {existing_user.real_name}")
            print(f"如需重置密码，请手动删除数据库文件后重新运行")
        else:
            # 创建新管理员
            user = auth_service.create_user(
                username=username,
                password=password,
                real_name=real_name,
                is_admin=True
            )
            print(f"\n✅ 管理员账号创建成功！")
            print("\n" + "=" * 50)
            print("默认登录信息：")
            print(f"  用户名: {username}")
            print(f"  密码: {password}")
            print(f"  姓名: {real_name}")
            print("=" * 50)
            print("\n💡 提示：首次登录后请修改密码")

    except Exception as e:
        print(f"\n❌ 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    try:
        init_admin()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
