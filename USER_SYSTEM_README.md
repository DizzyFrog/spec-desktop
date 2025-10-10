# 用户管理系统 - 完整指南

## 📦 系统概述

本系统实现了完整的用户认证和管理功能，适用于内部团队协作使用。

### 核心功能
- ✅ 用户登录/登出（JWT Token）
- ✅ 密码加密存储（bcrypt）
- ✅ 管理员用户管理界面
- ✅ 用户权限隔离（每个用户只能看到自己的文档）
- ✅ Web 管理后台（创建/编辑/删除用户）

---

## 🚀 快速开始

### 1. 首次部署

```bash
# 1. 安装后端依赖
cd backend
uv sync

# 2. 创建管理员账号
uv run python scripts/init_admin.py

# 输出：
# 用户名: admin
# 密码: admin123
# 姓名: 管理员

# 3. 启动后端服务
uv run uvicorn app.main:app --reload --port 8000

# 4. 启动前端（在另一个终端）
cd ../frontend
pnpm dev:antd
```

### 2. 管理员登录

```
访问: http://localhost:5888/
用户名: admin
密码: admin123
```

登录成功后，您将看到：
- **需求说明书** - 生成文档的主功能
- **系统管理** - 用户管理（仅管理员可见）

---

## 👥 用户管理操作指南

### 创建新用户

1. 管理员登录后，点击左侧菜单 **系统管理 → 用户管理**
2. 点击右上角 **[+ 创建用户]** 按钮
3. 填写表单：
   - **用户名**：登录使用，不可重复
   - **姓名**：显示名称
   - **密码**：至少 6 位
   - **设置为管理员**：勾选则该用户拥有管理员权限
4. 点击 **[创建]**
5. 将用户名和密码告知新用户

### 重置用户密码

1. 在用户列表中找到目标用户
2. 点击 **[重置密码]**
3. 输入新密码（至少 6 位）
4. 点击 **[确认重置]**
5. 将新密码告知用户

###启用/禁用用户

1. 在用户列表中找到目标用户
2. 点击 **[禁用]** 或 **[启用]**
3. 禁用后用户无法登录

### 删除用户

1. 在用户列表中找到目标用户
2. 点击 **[删除]**
3. 确认删除（不可恢复）

⚠️ **限制**：
- 不能删除自己的账号
- 不能删除最后一个管理员
- 不能取消最后一个管理员的管理员权限

---

## 🔐 用户隔离机制

### 数据隔离

每个用户的数据完全隔离：

```
用户A登录 → 上传 Excel → 生成文档 → 只能看到自己的文档
用户B登录 → 上传 Excel → 生成文档 → 只能看到自己的文档
管理员登录 → 可以看到所有用户的文档
```

### 文件存储

文件按用户 ID 隔离存储：

```
backend/data/
├── users.db                    # 用户数据库
└── uploads/
    ├── user_1/
    │   ├── input/             # 用户1上传的Excel
    │   └── output/            # 用户1生成的Word
    ├── user_2/
    │   ├── input/
    │   └── output/
    └── ...
```

---

## 🛠️ 数据库管理

### 数据库位置

```
backend/data/users.db
```

### 查看数据库（可选）

```bash
# 使用 sqlite3 命令行工具
sqlite3 backend/data/users.db

# 查看所有用户
SELECT id, username, real_name, is_admin, is_active FROM users;

# 退出
.quit
```

### 重置系统

如果需要完全重置系统（删除所有用户数据）：

```bash
# 1. 停止后端服务（Ctrl+C）

# 2. 删除数据库文件
rm backend/data/users.db

# 3. 重新创建管理员
cd backend
uv run python scripts/init_admin.py

# 4. 重新启动后端
uv run uvicorn app.main:app --reload --port 8000
```

---

## 🔑 密码安全

### 密码加密

- 使用 **bcrypt** 算法加密
- 自动加盐（每次加密结果都不同）
- 不可逆（数据库泄露也无法获取明文密码）

### 示例

```
用户输入: "admin123"
数据库存储: "$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

即使两个用户使用相同密码，数据库中的 hash 值也完全不同。

---

## 📊 API 接口文档

### 认证相关

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/auth/login` | POST | 用户登录 | 公开 |
| `/api/auth/getUserInfo` | GET | 获取当前用户信息 | 需登录 |
| `/api/auth/codes` | GET | 获取权限码 | 需登录 |
| `/api/auth/logout` | POST | 退出登录 | 需登录 |
| `/api/auth/refresh` | POST | 刷新 Token | 需登录 |

### 管理员相关

| 接口 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/admin/users` | GET | 获取用户列表 | 管理员 |
| `/api/admin/users` | POST | 创建新用户 | 管理员 |
| `/api/admin/users/{id}` | PUT | 更新用户信息 | 管理员 |
| `/api/admin/users/{id}/reset-password` | POST | 重置密码 | 管理员 |
| `/api/admin/users/{id}` | DELETE | 删除用户 | 管理员 |
| `/api/admin/stats` | GET | 获取统计信息 | 管理员 |

---

## 🔧 技术架构

### 后端技术栈

```
FastAPI          - Web 框架
SQLAlchemy       - ORM (数据库)
SQLite           - 数据库（文件存储）
passlib + bcrypt - 密码加密
python-jose      - JWT Token 生成和验证
```

### 前端技术栈

```
Vue 3            - 前端框架
Vue Vben Admin   - 管理后台模板
TypeScript       - 类型安全
Ant Design Vue   - UI 组件库（可选）
```

### 数据库表结构

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);
```

---

## 🐛 常见问题

### Q1: 忘记管理员密码怎么办？

**方法1：重置数据库**
```bash
rm backend/data/users.db
uv run python scripts/init_admin.py
```

**方法2：直接修改数据库**
```bash
cd backend
uv run python scripts/init_admin.py
# 会提示管理员已存在，选择 y 重置密码
```

### Q2: 如何修改默认管理员密码？

编辑 `backend/scripts/init_admin.py`：

```python
# 修改这两行
username = "admin"       # 修改默认用户名
password = "admin123"    # 修改默认密码
```

### Q3: Token 过期时间是多久？

默认 24 小时，在 `backend/app/services/auth_service.py` 中配置：

```python
ACCESS_TOKEN_EXPIRE_HOURS = 24  # 修改为其他小时数
```

### Q4: 如何修改数据库存储位置？

编辑 `backend/app/database.py`：

```python
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'users.db')}"
# 修改 'users.db' 为其他路径
```

### Q5: 如何备份用户数据？

```bash
# 备份数据库文件
cp backend/data/users.db backend/data/users_backup_$(date +%Y%m%d).db

# 恢复备份
cp backend/data/users_backup_20241010.db backend/data/users.db
```

---

## 📝 开发者文档

### 添加新的权限角色

当前系统只有两种角色：
- `user` - 普通用户
- `admin` - 管理员

如需添加更多角色（如 `editor`, `viewer`），需要：

1. 修改数据库模型添加 `role` 字段
2. 修改认证服务的权限验证逻辑
3. 更新前端路由权限配置

### 添加用户资料编辑功能

如需允许用户修改自己的资料：

1. 创建新接口 `/api/user/profile`
2. 前端添加"个人资料"页面
3. 允许修改：姓名、头像、邮箱等

### 添加操作日志

如需记录管理员操作：

1. 创建 `audit_logs` 表
2. 在管理员操作接口中记录日志
3. 添加日志查询界面

---

## 📞 技术支持

如有问题或建议，请：
1. 查看本文档的常见问题部分
2. 检查后端日志 (终端输出)
3. 检查浏览器控制台错误

---

## ✅ 完成清单

系统实现的功能：

- [x] 用户数据库（SQLite）
- [x] 密码加密（bcrypt）
- [x] JWT Token 认证
- [x] 登录/登出
- [x] 用户信息查询
- [x] 管理员用户管理界面
- [x] 创建/编辑/删除用户
- [x] 重置密码
- [x] 启用/禁用用户
- [x] 用户统计信息
- [x] 权限隔离
- [x] 命令行初始化脚本

---

## 🎉 完成！

您的用户管理系统已经完全配置完成。现在可以：

1. 启动后端和前端服务
2. 使用 `admin` / `admin123` 登录
3. 创建团队成员账号
4. 开始使用需求说明书生成功能

祝使用愉快！🚀
