#!/usr/bin/env python3
"""
创建管理员账号的命令行脚本
用于首次部署或重置管理员密码

使用方法：
    uv run python scripts/create_admin.py
"""

import sys
import os
import getpass

# 添加父目录到路径以便导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db, get_db
from app.models.user import User
from app.services.auth_service import AuthService


def create_admin():
    """交互式创建管理员账号"""
    print("=" * 50)
    print("创建管理员账号")
    print("=" * 50)

    # 初始化数据库
    init_db()

    # 获取用户输入
    username = input("请输入管理员用户名（默认: admin）: ").strip() or "admin"
    real_name = input("请输入管理员姓名（默认: 管理员）: ").strip() or "管理员"

    # 安全输入密码
    while True:
        password = getpass.getpass("请输入密码: ")
        if len(password) < 6:
            print("❌ 密码长度不能少于 6 位，请重新输入")
            continue

        password_confirm = getpass.getpass("请再次输入密码: ")
        if password != password_confirm:
            print("❌ 两次密码不一致，请重新输入")
            continue

        break

    # 创建管理员
    db = next(get_db())
    auth_service = AuthService(db)

    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == username).first()

        if existing_user:
            # 更新现有管理员
            response = input(f"\n⚠️  用户 '{username}' 已存在，是否重置密码？(y/n): ")
            if response.lower() == 'y':
                existing_user.hashed_password = auth_service.get_password_hash(password)
                existing_user.real_name = real_name
                existing_user.is_admin = True
                existing_user.is_active = True
                db.commit()
                print(f"\n✅ 管理员账号已更新！")
            else:
                print("\n❌ 操作已取消")
                return
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
        print("登录信息：")
        print(f"  用户名: {username}")
        print(f"  姓名: {real_name}")
        print(f"  角色: 管理员")
        print("=" * 50)
        print("\n💡 提示：请妥善保管登录信息")

    except Exception as e:
        print(f"\n❌ 创建失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
