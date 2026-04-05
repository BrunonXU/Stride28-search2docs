# 腾讯文档 MCP 安装配置

腾讯文档通过 mcporter 调用，端点 `https://docs.qq.com/openapi/mcp`。

## 安装 mcporter

```bash
npm install -g mcporter
```

## 授权

### 方式一：setup.sh 自动授权（需要 bash 环境）

```bash
bash setup.sh tdoc_check_and_start_auth
# 输出 READY → 已就绪
# 输出 AUTH_REQUIRED:<url> → 浏览器打开链接，QQ/微信扫码

bash setup.sh tdoc_wait_auth
# 输出 TOKEN_READY → 搞定
```

授权成功后 `tencent-docs`、`tencent-docengine`、`tencent-sheetengine` 三个服务同时配好。

### 方式二：手动获取 Token

1. 访问 [docs.qq.com/scenario/open-claw.html](https://docs.qq.com/scenario/open-claw.html)
2. QQ 或微信登录后，页面上显示 Token，复制
3. 配置到 mcporter：

```bash
mcporter config add tencent-docs "https://docs.qq.com/openapi/mcp" \
    --header "Authorization=$TOKEN" --transport http --scope home
```

### WorkBuddy 用户

无需配置，腾讯文档内置，微信登录即可。

## 验证

```bash
mcporter list tencent-docs
```

## 常见错误

| 错误码 | 含义 | 解决 |
|--------|------|------|
| 400006 | Token 鉴权失败 | 重新授权 |
| 400007 | VIP 权限不足 | [升级 VIP](https://docs.qq.com/vip?immediate_buy=1?part_aid=persnlspace_mcp) |
