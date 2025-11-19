# DNS 配置指南 - zhonghuafreedom.org

## 概述
为了将 `zhonghuafreedom.org` 绑定到 GitHub Pages，需要在您的域名服务商处配置 DNS 记录。

## 配置步骤

### 方法一：使用 A 记录（推荐用于根域名）

在您的域名服务商控制面板中添加以下 **4 条 A 记录**：

| 记录类型 | 主机名/名称 | 值（IPv4 地址） | TTL |
|---------|------------|----------------|-----|
| A | @ | 185.199.108.153 | 3600 |
| A | @ | 185.199.109.153 | 3600 |
| A | @ | 185.199.110.153 | 3600 |
| A | @ | 185.199.111.153 | 3600 |

**说明：**
- `@` 表示根域名（zhonghuafreedom.org）
- 需要添加所有 4 条 A 记录（GitHub 要求）
- TTL 可以设置为 3600 秒（1小时）或使用默认值

### 方法二：使用 CNAME 记录（如果支持）

如果您的域名服务商支持根域名的 CNAME 记录（ALIAS/ANAME），可以添加：

| 记录类型 | 主机名/名称 | 值 | TTL |
|---------|------------|-----|-----|
| CNAME | @ | zhonghuafreedom.github.io | 3600 |

**注意：** 不是所有域名服务商都支持根域名的 CNAME 记录。

### 可选：配置 www 子域名

如果您也想让 `www.zhonghuafreedom.org` 可以访问，添加：

| 记录类型 | 主机名/名称 | 值 | TTL |
|---------|------------|-----|-----|
| CNAME | www | zhonghuafreedom.github.io | 3600 |

## 常见域名服务商配置位置

### Cloudflare
1. 登录 Cloudflare 控制台
2. 选择域名 `zhonghuafreedom.org`
3. 进入 "DNS" → "Records"
4. 添加上述 A 记录或 CNAME 记录

### GoDaddy
1. 登录 GoDaddy
2. 进入 "我的产品" → "DNS"
3. 在 DNS 管理页面添加记录

### Namecheap
1. 登录 Namecheap
2. 进入 "Domain List" → 选择域名 → "Advanced DNS"
3. 添加记录

### 阿里云/万网
1. 登录阿里云控制台
2. 进入 "域名" → "解析设置"
3. 添加记录

### 其他服务商
查找 "DNS 管理"、"域名解析"、"DNS 设置" 等选项

## 验证 DNS 配置

配置完成后，可以使用以下命令验证：

```bash
# 检查 A 记录
dig zhonghuafreedom.org A

# 或使用 nslookup
nslookup zhonghuafreedom.org

# 检查是否指向 GitHub
dig zhonghuafreedom.org A +short
```

应该看到返回的 IP 地址包含：`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` 中的至少一个。

## 时间线

- **DNS 传播时间：** 通常 5 分钟到 48 小时
- **GitHub SSL 证书申请：** DNS 生效后，GitHub 会自动申请 SSL 证书，通常需要几分钟到几小时
- **完全生效：** 通常 1-24 小时内可以完全访问

## 检查清单

- [ ] 已在域名服务商添加 DNS 记录
- [ ] CNAME 文件已存在于 GitHub 仓库
- [ ] 在 GitHub 仓库设置中已配置自定义域名
- [ ] 等待 DNS 传播完成
- [ ] 等待 GitHub SSL 证书申请完成
- [ ] 测试访问 https://zhonghuafreedom.org

## 故障排除

如果配置后无法访问：

1. **检查 DNS 是否生效**
   ```bash
   dig zhonghuafreedom.org A
   ```

2. **检查 GitHub Pages 设置**
   - 访问：https://github.com/zhonghuafreedom/zhonghuafreedom.github.io/settings/pages
   - 确认自定义域名已配置
   - 确认 "Enforce HTTPS" 已启用

3. **清除浏览器缓存**
   - 尝试使用无痕模式访问
   - 或清除 DNS 缓存

4. **等待更长时间**
   - DNS 传播可能需要更长时间
   - 某些地区可能需要 24-48 小时

## 需要帮助？

如果遇到问题，可以：
1. 检查 GitHub Pages 文档：https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site
2. 查看域名服务商的帮助文档
3. 联系域名服务商的技术支持

