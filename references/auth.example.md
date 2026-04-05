# 腾讯文档授权

## 快速开始

WorkBuddy 用户无需配置，微信登录即可使用。

其他客户端（OpenClaw / Claude Code / Kiro 等）运行一次授权脚本即可：

```bash
# 检查状态，如果未授权会输出一个链接
bash setup.sh tdoc_check_and_start_auth

# 浏览器打开链接，QQ/微信扫码，然后执行
bash setup.sh tdoc_wait_auth
```

搞定。Token 自动写入 mcporter，三个服务（tencent-docs / tencent-docengine / tencent-sheetengine）同时配好。

## 手动兜底

如果脚本不好使，访问 [docs.qq.com/scenario/open-claw.html](https://docs.qq.com/scenario/open-claw.html) 复制 Token，然后：

```bash
mcporter config add tencent-docs "https://docs.qq.com/openapi/mcp" \
    --header "Authorization=$TOKEN" --transport http --scope home
```
