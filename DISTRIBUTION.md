# 应用分发说明

## 问题原因

macOS 在其他电脑上显示"已损坏"是因为：
1. 应用使用了开发者证书签名（Apple Development）
2. macOS Gatekeeper 会检查从互联网下载的应用签名

## 解决方案

### 方案 1：接收方手动解除隔离（推荐，最简单）

发送 ZIP 文件给对方后，让对方在终端执行：

```bash
# 解压后，进入应用所在目录
cd ~/Downloads  # 或应用所在的目录

# 解除隔离属性
xattr -cr "需求说明书生成工具.app"

# 然后双击打开应用即可
```

### 方案 2：使用 Apple Distribution 证书（正式分发）

如果需要正式分发，需要申请 Apple Distribution 证书并公证：

1. **申请证书**（需要 Apple Developer 账号，99 美元/年）
   - 登录 https://developer.apple.com
   - 创建 Distribution 证书

2. **配置 electron-builder.yml**

```yaml
mac:
  identity: "Developer ID Application: Your Name (TEAM_ID)"
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist
  notarize: true  # 改为 true

# 在环境变量中设置（不要提交到代码库）
# export APPLE_ID="your-apple-id@email.com"
# export APPLE_ID_PASSWORD="app-specific-password"
# export APPLE_TEAM_ID="YOUR_TEAM_ID"
```

3. **重新打包**

```bash
npm run build:mac
```

公证后的应用可以直接分发，不会显示"已损坏"。

### 方案 3：DMG 分发（当前推荐）

当前构建已经生成了 DMG 文件，位于：
```
release/1.0.0/mac-arm64/需求说明书生成工具-1.0.0.dmg
```

直接分发 DMG 文件，接收方需要执行：

```bash
xattr -cr "/Volumes/需求说明书生成工具/需求说明书生成工具.app"
```

或者拖到 Applications 后：

```bash
xattr -cr "/Applications/需求说明书生成工具.app"
```

## 当前构建状态

- ✅ 应用已使用开发者证书签名
- ✅ 后端已正确打包（包含 numpy）
- ✅ 本机可以正常运行
- ⚠️  其他 Mac 需要手动解除隔离

## 测试方法

在接收方 Mac 上：

```bash
# 方法 1：解除隔离后打开
xattr -cr "需求说明书生成工具.app"
open "需求说明书生成工具.app"

# 方法 2：查看签名信息
codesign -dv --verbose=4 "需求说明书生成工具.app"

# 方法 3：检查 Gatekeeper 状态
spctl -a -vv "需求说明书生成工具.app"
```

## 注意事项

1. **不要使用 AirDrop**：可能会损坏签名，建议使用云盘分享
2. **保持 ZIP 完整性**：解压前不要修改 ZIP 文件
3. **macOS 版本**：需要 macOS 10.15+ 才能运行
