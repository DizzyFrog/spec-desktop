"""
测试缓存管理功能
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 测试用户登录
print("=" * 60)
print("1. 测试用户登录")
print("=" * 60)

login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "admin", "password": "123456"}
)

if login_response.status_code == 200:
    data = login_response.json()
    token = data["data"]["accessToken"]
    print(f"✅ 登录成功，获取 Token: {token[:20]}...")
else:
    print(f"❌ 登录失败: {login_response.text}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# 测试获取缓存统计
print("\n" + "=" * 60)
print("2. 获取当前用户缓存统计")
print("=" * 60)

stats_response = requests.get(f"{BASE_URL}/api/cache/stats", headers=headers)
if stats_response.status_code == 200:
    stats = stats_response.json()["data"]
    print(f"✅ 缓存统计:")
    print(f"   - 用户: {stats['username']} (ID: {stats['user_id']})")
    print(f"   - 缓存大小: {stats['cache_size']} bytes")
    print(f"   - 上传大小: {stats['upload_size']} bytes")
    print(f"   - 输出大小: {stats['output_size']} bytes")
    print(f"   - 总大小: {stats['total_size']} bytes ({stats['total_size_mb']} MB)")
    print(f"   - 缓存文件: {stats['cache_files']} 个")
    print(f"   - 上传文件: {stats['upload_files']} 个")
    print(f"   - 输出文件: {stats['output_files']} 个")
    print(f"   - 总文件: {stats['total_files']} 个")
else:
    print(f"❌ 获取统计失败: {stats_response.text}")

# 测试清理缓存
print("\n" + "=" * 60)
print("3. 清理当前用户缓存")
print("=" * 60)

clear_response = requests.post(
    f"{BASE_URL}/api/cache/clear",
    json={
        "clear_cache": True,
        "clear_uploads": False,  # 保留上传文件
        "clear_outputs": True
    },
    headers=headers
)

if clear_response.status_code == 200:
    result = clear_response.json()["data"]
    print(f"✅ 清理结果:")
    print(f"   - 成功: {result['success']}")
    print(f"   - 已清理: {result['cleared']}")
    print(f"   - 消息: {result['message']}")
else:
    print(f"❌ 清理失败: {clear_response.text}")

# 再次获取统计
print("\n" + "=" * 60)
print("4. 清理后的缓存统计")
print("=" * 60)

stats_response2 = requests.get(f"{BASE_URL}/api/cache/stats", headers=headers)
if stats_response2.status_code == 200:
    stats2 = stats_response2.json()["data"]
    print(f"✅ 缓存统计:")
    print(f"   - 缓存大小: {stats2['cache_size']} bytes (清理了 {stats['cache_size'] - stats2['cache_size']} bytes)")
    print(f"   - 上传大小: {stats2['upload_size']} bytes (保留)")
    print(f"   - 输出大小: {stats2['output_size']} bytes (清理了 {stats['output_size'] - stats2['output_size']} bytes)")
    print(f"   - 总大小: {stats2['total_size']} bytes ({stats2['total_size_mb']} MB)")
else:
    print(f"❌ 获取统计失败: {stats_response2.text}")

print("\n" + "=" * 60)
print("✅ 测试完成！")
print("=" * 60)
