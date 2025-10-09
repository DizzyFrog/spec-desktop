#!/bin/bash

# 修复 macOS "已损坏无法打开" 问题的脚本
# 使用方法：将此脚本和应用放在同一目录，然后在终端执行：
# chmod +x fix-macos-quarantine.sh && ./fix-macos-quarantine.sh

APP_NAME="需求说明书生成工具.app"

echo "================================"
echo "修复 macOS 应用隔离问题"
echo "================================"
echo ""

# 检查应用是否存在
if [ ! -d "$APP_NAME" ]; then
    echo "❌ 错误：未找到应用 '$APP_NAME'"
    echo "   请确保此脚本和应用在同一目录"
    exit 1
fi

echo "📦 找到应用: $APP_NAME"
echo ""

# 解除隔离属性
echo "🔧 正在解除隔离属性..."
xattr -cr "$APP_NAME"

if [ $? -eq 0 ]; then
    echo "✅ 隔离属性已解除"
    echo ""
    echo "🎉 应用已修复，现在可以正常打开了！"
    echo ""
    echo "💡 提示：双击应用图标即可启动"
else
    echo "❌ 解除隔离失败"
    echo ""
    echo "请尝试手动执行："
    echo "   xattr -cr \"$APP_NAME\""
    exit 1
fi

# 可选：直接打开应用
read -p "是否现在打开应用？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 正在启动应用..."
    open "$APP_NAME"
fi

echo ""
echo "================================"
echo "完成！"
echo "================================"
