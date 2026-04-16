#!/bin/bash
# Jiao Factory - WeChat-XHS-Automation 一键发布脚本
# 使用方法: ./publish.sh YOUR_GITHUB_USERNAME

set -e

GITHUB_USERNAME=$1

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ 错误: 需要提供GitHub用户名"
    echo "使用方法: ./publish.sh your_github_username"
    exit 1
fi

echo "🏭 Jiao Factory - WeChat-XHS-Automation 发布脚本"
echo "================================================"
echo ""

# 检查git
if ! command -v git &> /dev/null; then
    echo "❌ 错误: 未安装git"
    exit 1
fi

# 进入项目目录
cd ~/.openclaw/workspace/skills/wechat-xhs-automation

echo "✅ 步骤1: 检查Git状态"
git status

echo ""
echo "✅ 步骤2: 添加远程仓库"
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$GITHUB_USERNAME/wechat-xhs-automation.git"

echo ""
echo "✅ 步骤3: 重命名分支为main"
git branch -M main

echo ""
echo "🚀 步骤4: 推送到GitHub"
echo "   仓库地址: https://github.com/$GITHUB_USERNAME/wechat-xhs-automation"
echo ""

# 提示用户创建仓库
echo "⚠️  请先确保已在GitHub创建空仓库:"
echo "   https://github.com/new"
echo "   仓库名: wechat-xhs-automation"
echo ""
read -p "确认已创建仓库并继续? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push -u origin main
    echo ""
    echo "🎉 推送成功!"
    echo "   查看: https://github.com/$GITHUB_USERNAME/wechat-xhs-automation"
    echo ""
    echo "下一步: 发布到ClawHub"
    echo "   npx clawhub publish ~/.openclaw/workspace/skills/wechat-xhs-automation"
else
    echo "❌ 已取消"
    exit 1
fi
