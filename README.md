# stride28-search2docs

> 把中文社区里碎片化的真实经验内容，变成结构化、可持续更新的文档资产。

## 这是什么

`stride28-search2docs` 是一个建立在 `stride28-search-mcp` 之上的 workflow skill，遵循 [AgentSkills 开放标准](https://agentskills.io)。

它把"中文社区经验内容 → 过滤去重 → 结构化整理 → 写入文档系统"这条链路，打包成一个可复用的 workflow。

## 旗舰案例

自动采集小红书上的 AI Agent / 大模型应用面经，整理后写入腾讯文档。

同一套链路也适合：产品反馈汇总、AI 工具评价追踪、课程口碑整理、岗位信息沉淀、竞品体验收集。如果你有其他场景，可以参照 `prompts/interview-briefing.md` 的结构自建一个 workflow 模板。

## 目录结构

```
stride28-search2docs/
├── README.md                       # 本文件
├── SKILL.md                        # Skill 入口（AgentSkills 标准）
├── references/                     # 参考规范
│   ├── specification.md            #   面经格式规范（文档结构、字段定义、筛选规则）
│   ├── tencent-docs-mdx.md         #   腾讯文档 MDX 格式说明（表格、链接、Mark 组件）
│   └── auth.example.md             #   认证配置示例（模板，不含真实 token）
├── prompts/                        # Workflow 模板
│   └── interview-briefing.md       #   面经整理 workflow（旗舰案例，可参照此模板自建其他 workflow）
├── scripts/                        # 辅助脚本
│   ├── generate_mdx.py             #   结构化 JSON → 腾讯文档 MDX
│   └── postprocess_results.py      #   搜索结果过滤与去重
├── templates/                      # 输出模板
│   ├── interview_briefing_template.mdx
│   └── generic_briefing_template.mdx
└── examples/                       # 示例
    └── agent-interview-briefing/
        ├── input.json              #   结构化面经数据示例
        ├── output.mdx              #   生成的 MDX 示例
        └── README.md
```

---

## 前置依赖

### 1. stride28-search-mcp

底层搜索能力层，提供小红书和知乎的搜索与详情获取。

**提供的 MCP 工具：**

| 工具 | 说明 | 关键参数 |
|------|------|----------|
| `login_xiaohongshu` | 登录小红书（弹出浏览器扫码） | 无 |
| `search_xiaohongshu` | 搜索小红书笔记 | `query`, `limit`(10-20), `note_type`(默认 all) |
| `get_note_detail` | 获取笔记完整详情 | `note_id`, `xsec_token`, `max_comments`(默认 10) |
| `reset_xiaohongshu_login` | 重置小红书登录态 | 无 |
| `login_zhihu` | 登录知乎 | 无 |
| `search_zhihu` | 搜索知乎内容 | `query`, `limit` |
| `get_zhihu_question` | 获取知乎问题详情 | `question_id`, `limit`, `max_content_length` |
| `reset_zhihu_login` | 重置知乎登录态 | 无 |

安装方式取决于你的 agent 客户端，通常配置为 MCP 服务即可。

### 2. mcporter（用于写入腾讯文档）

MCP 客户端 CLI，用于调用腾讯文档 MCP 服务。

```bash
npm install -g mcporter
mcporter list    # 确认安装成功
```

### 3. 腾讯文档 MCP 服务（tencent-docs）

```bash
# 检查是否已配置
mcporter list
# 应该能看到 tencent-docs
```

如果没有，需要手动配置（见下方"腾讯文档 Token 获取与配置"）。

---

## 腾讯文档 MCP 接入

WorkBuddy 用户无需配置，微信登录直接用。

其他客户端跑一次授权脚本：

```bash
bash setup.sh tdoc_check_and_start_auth
# 输出 READY → 已就绪
# 输出 AUTH_REQUIRED:<url> → 浏览器打开链接，QQ/微信扫码

bash setup.sh tdoc_wait_auth
# 输出 TOKEN_READY → 搞定，三个服务自动配好
```

手动兜底：访问 [docs.qq.com/scenario/open-claw.html](https://docs.qq.com/scenario/open-claw.html) 复制 Token，然后 `mcporter config add tencent-docs "https://docs.qq.com/openapi/mcp" --header "Authorization=$TOKEN" --transport http --scope home`。

详细说明见 `references/auth.example.md`。

---

## OpenClaw 兼容性

本项目遵循 [AgentSkills 开放标准](https://agentskills.io)，OpenClaw、Claude Code、CodeBuddy 等 20+ 客户端原生支持。安装到 skills 目录即可，OpenClaw 用户也可以通过 ClawHub 安装。

---

## 小红书 xsec_token

小红书的帖子链接需要 `xsec_token` 参数才能让读者直接访问内容。

这个 token 不需要手动获取 — `stride28-search-mcp` 的 `search_xiaohongshu` 搜索结果中会自动返回每条笔记对应的 `xsec_token`。

生成文档时，每条原文链接都必须拼接上对应的 token：
```
https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}
```

---

## 完整工作流程

```
1. 登录小红书
   └─ MCP: login_xiaohongshu（扫码登录）

2. 搜索面经
   └─ MCP: search_xiaohongshu × 8 个关键词
   └─ 每次 limit=20，收集所有结果

3. 获取详情
   └─ MCP: get_note_detail（对筛选后的帖子逐一获取）
   └─ 提取公司、岗位、轮次、问题、要点等字段

4. 过滤去重
   └─ 过滤广告/引流/情绪帖
   └─ 标题相似度去重
   └─ 优先保留信息完整的版本

5. 生成 MDX
   └─ 按 specification.md 结构组织内容
   └─ 按 tencent-docs-mdx.md 格式规范输出
   └─ 公司名用颜色标记，表格用 MDX 组件

6. 写入腾讯文档
   └─ mcporter: manage.search_file（查找已有文档）
   └─ mcporter: create_smartcanvas_by_mdx（新建）
   └─ 或 mcporter: smartcanvas.edit（追加章节，action=INSERT_AFTER）

7. 返回结果
   └─ 文档名、新增条目数、涉及公司数、文档链接
```

---

## 使用方式

### WorkBuddy（最简单）

把 repo 链接丢给 WorkBuddy 说"帮我安装这个 skill"，它自动完成。腾讯文档内置不用管。首次采集面经时会弹浏览器让你扫码登录小红书，扫一次后续复用。

### Claude Code

需要有浏览器的电脑上操作（两个扫码都需要弹浏览器）：

```bash
git clone <repo_url> ~/.claude/skills/stride28-search2docs
cd ~/.claude/skills/stride28-search2docs
bash setup.sh tdoc_check_and_start_auth   # 扫码授权腾讯文档
bash setup.sh tdoc_wait_auth              # 等待授权完成
```

配好后在 Claude Code 里说"采集面经"即可。

### OpenClaw（飞书/Telegram 等远程接入）

首次配置必须在服务器端完成（SSH 上去操作）：

```bash
git clone <repo_url> ~/.openclaw/skills/stride28-search2docs
cd ~/.openclaw/skills/stride28-search2docs
bash setup.sh tdoc_check_and_start_auth   # 扫码授权腾讯文档
bash setup.sh tdoc_wait_auth
```

小红书登录也需要服务器端有浏览器环境。配好之后，日常使用可以在手机上通过飞书/Telegram 发消息触发。

### Kiro / Cursor 等 IDE

确保 `stride28-search-mcp` 和 `tencent-docs` 已配置为 MCP 服务，参考 `prompts/interview-briefing.md` 操作。

---

## 面经文档结构

生成的文档包含五个部分：

1. **今日摘要** — 新增帖子数、有效帖子数、涉及公司数、高频岗位、热门主题、最值得关注的 3 条面经
2. **按公司分类整理** — 每个公司一个分组，颜色标记，表格展示（公司/岗位/类型/轮次/时间/作者/链接/摘要/问题/要点/启发）
3. **高频问题归纳** — 按 8 个主题分类（Agent 架构、Prompt/Tool Calling、RAG、多 Agent、大模型基础、项目难点、工程化、八股行为面）
4. **给 Bruno 的针对性建议** — 能力要求、知识缺口、项目准备、每日 10 题
5. **原始链接列表** — 所有保留帖子的公司/标题/链接/时间索引

详细格式规范见 `references/specification.md`，MDX 语法规则见 `references/tencent-docs-mdx.md`。

---

## 架构

```
stride28-search-mcp (底层能力)       stride28-search2docs (上层 workflow)
┌──────────────────────────┐        ┌──────────────────────────────┐
│  login_xiaohongshu       │        │  搜索 → 筛选 → 去重          │
│  search_xiaohongshu      │  ──→   │  提取字段 → 结构化           │
│  get_note_detail         │        │  生成 MDX → 写入腾讯文档      │
│  search_zhihu            │        │                              │
│  get_zhihu_question      │        │  prompts/ → 定义 workflow    │
└──────────────────────────┘        │  scripts/ → 辅助处理         │
                                    │  references/ → 格式规范       │
                                    └──────────────────────────────┘
```

两个 repo 独立维护。MCP 层保持泛化不绑定场景，skill 层负责具体 workflow 落地。

---

## License

MIT
