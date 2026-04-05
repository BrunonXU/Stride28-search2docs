# stride28-search-mcp 安装配置

小红书/知乎搜索能力，PyPI 包，Python 3.10+。

## 安装

```bash
# uv（推荐）
uv tool install stride28-search-mcp

# 或 pipx
pipx install stride28-search-mcp

# 安装浏览器（首次）
stride28-search-mcp install-browser

# 验证
stride28-search-mcp doctor
```

## MCP 客户端配置

在你的 MCP 客户端配置文件中添加以下内容。不同客户端建议用不同的 `STRIDE28_SEARCH_MCP_PROFILE`，避免共用浏览器状态。

### Claude Code

项目根目录 `.mcp.json`：

```json
{
  "mcpServers": {
    "stride28-search": {
      "command": "stride28-search-mcp",
      "env": {
        "STRIDE28_SEARCH_MCP_PROFILE": "claude",
        "STRIDE28_XHS_HEADLESS": "false"
      }
    }
  }
}
```

### Kiro

`.kiro/settings/mcp.json`：

```json
{
  "mcpServers": {
    "stride28-search": {
      "command": "stride28-search-mcp",
      "env": {
        "STRIDE28_SEARCH_MCP_PROFILE": "kiro",
        "STRIDE28_XHS_HEADLESS": "false"
      }
    }
  }
}
```

### WorkBuddy

```json
{
  "mcpServers": {
    "stride28-search": {
      "command": "uvx",
      "args": ["stride28-search-mcp"],
      "env": {
        "STRIDE28_SEARCH_MCP_PROFILE": "workbuddy",
        "STRIDE28_XHS_HEADLESS": "false"
      }
    }
  }
}
```

### Cursor

`.cursor/mcp.json`，格式同 Claude Code。

## 可用工具

| 工具 | 平台 | 说明 | 关键参数 |
|------|------|------|----------|
| `login_xiaohongshu` | 小红书 | 扫码登录 | 无 |
| `search_xiaohongshu` | 小红书 | 搜索笔记 | `query`, `limit`(10-20), `note_type` |
| `get_note_detail` | 小红书 | 笔记详情+评论 | `note_id`, `xsec_token`, `max_comments` |
| `reset_xiaohongshu_login` | 小红书 | 重置登录态 | 无 |
| `login_zhihu` | 知乎 | 手动登录 | 无 |
| `search_zhihu` | 知乎 | 搜索内容 | `query`, `limit`(5-10) |
| `get_zhihu_question` | 知乎 | 问题详情 | `question_id`, `limit`, `max_content_length` |
| `reset_zhihu_login` | 知乎 | 重置登录态 | 无 |

## 首次使用

1. 配置好 MCP 后，在 agent 中说"登录小红书"
2. 弹出浏览器，用小红书 App 扫码
3. 登录成功后后续复用

## 使用原则

本 MCP 是低频定向检索工具，不是批量采集器：
- 不要连续发起很多轮相似搜索
- 遇到 `captcha_detected`、`search_blocked`、`risk_cooldown_active` 立即停止，不要重试
- `risk_cooldown_active` 默认冷却 15 分钟

详细文档：https://github.com/BrunonXU/Stride28-search-mcp
