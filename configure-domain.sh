#!/bin/bash

# GitHub Pages 自定义域名配置脚本
# 用于配置 zhonghuafreedom.org 域名

REPO_OWNER="zhonghuafreedom"
REPO_NAME="zhonghuafreedom.github.io"
DOMAIN="zhonghuafreedom.org"

echo "=========================================="
echo "GitHub Pages 自定义域名配置"
echo "=========================================="
echo ""

# 检查是否已登录 GitHub CLI
if ! gh auth status &>/dev/null; then
    echo "需要登录 GitHub..."
    echo "请按照提示完成登录："
    gh auth login
fi

echo ""
echo "正在配置 GitHub Pages 自定义域名: $DOMAIN"
echo ""

# 首先确保 Pages 已启用（使用 main 分支的 / 路径）
echo "正在启用 GitHub Pages..."
gh api repos/$REPO_OWNER/$REPO_NAME/pages \
  -X PUT \
  -f source[type]=branch \
  -f source[branch]=main \
  -f source[path]=/ \
  -f https_enforced:true

# 等待一下让 Pages 启用
sleep 2

# 配置自定义域名
echo "正在配置自定义域名..."
gh api repos/$REPO_OWNER/$REPO_NAME/pages \
  -X PUT \
  -f source[type]=branch \
  -f source[branch]=main \
  -f source[path]=/ \
  -f cname=$DOMAIN \
  -f https_enforced:true

if [ $? -eq 0 ]; then
    echo "✅ GitHub Pages 自定义域名配置成功！"
    echo ""
    echo "域名: $DOMAIN"
    echo "仓库: https://github.com/$REPO_OWNER/$REPO_NAME"
    echo ""
    echo "⚠️  重要提示："
    echo "1. 确保 CNAME 文件已存在于仓库根目录"
    echo "2. 需要在域名服务商配置 DNS 记录（见 DNS 配置指南）"
    echo "3. DNS 生效可能需要几分钟到几小时"
else
    echo "❌ 配置失败，请检查："
    echo "1. 是否已登录 GitHub CLI"
    echo "2. 是否有仓库访问权限"
    echo "3. GitHub Pages 是否已启用"
fi

