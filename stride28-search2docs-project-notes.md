# stride28-search2docs 项目说明

> 把中文社区里碎片化的真实经验内容，变成结构化、可持续更新的文档资产。

---

## 1. 项目是怎么来的

最开始做的是底层 MCP：`stride28-search-mcp`，负责从小红书、知乎抓取真实经验内容。

但抓到内容不是终点。真正麻烦的是：

- 内容太碎，散落在各个帖子里
- 更新快，收藏了也不会回头看
- 去重、整理、归类、复盘全靠手动

所以 `stride28-search2docs` 就是为了解决这个问题：

> 把"中文社区经验内容 → 过滤去重 → 结构化整理 → 写入文档系统"这条链路，打包成一个可复用的 workflow skill。

---

## 2. 架构：两层分离

### 底层：`stride28-search-mcp`

能力层，保持泛化，不绑定具体场景。

- 搜索中文社区经验内容
- 获取详情
- 返回结构化结果

### 上层：`stride28-search2docs`

Workflow skill 层，负责具体场景的落地。

- 调用 `stride28-search-mcp` 获取原始内容
- 过滤、去重、抽字段、摘要整理
- 生成文档格式内容
- 写入腾讯文档 / 飞书文档

两个 repo 独立维护，边界清晰。MCP 不被单一场景锁死，skill repo 可以沉淀多个 workflow。

---

## 3. 这个项目不是什么

- 不是"全网情报平台"——定位太大，不是当前真正的优势
- 不是"腾讯文档工具箱"——重点不是造文档工具，是把社区经验沉淀进去
- 不是"只做面经"——面经是第一个旗舰案例，不是唯一定位

---

## 4. 目录结构

```text
stride28-search2docs/
├── README.md                      # 项目说明
├── SKILL.md                       # Skill 入口（AgentSkills 标准）
├── references/                    # 参考规范与格式说明
│   ├── specification.md           #   workflow 规范定义
│   ├── tencent-docs-mdx.md        #   腾讯文档 MDX 格式说明
│   └── auth.example.md            #   认证配置示例
├── prompts/                       # Workflow 模板
│   └── interview-briefing.md      #   面经整理（旗舰案例，可参照自建其他 workflow）
├── scripts/                       # 辅助脚本（由 agent 调用）
│   ├── generate_mdx.py            #   生成 MDX 格式输出
│   └── postprocess_results.py     #   结果后处理与去重
├── templates/                     # 输出模板
│   ├── interview_briefing_template.mdx
│   └── generic_briefing_template.mdx
└── examples/                      # 经典案例
    └── agent-interview-briefing/
        ├── input.json
        ├── output.mdx
        ├── screenshot.png
        └── README.md
```

---

## 5. Skill 是什么

Skill 遵循 [AgentSkills 开放标准](https://agentskills.io)，入口是一个 SKILL.md 文件，但一个真正可用的 skill 不止一个 md。

一个完整 skill 包括：

- 入口说明（SKILL.md）
- Workflow prompt 模板（prompts/）
- 参考文档（references/）
- 辅助脚本（scripts/）
- 输出模板（templates/）
- 示例（examples/）

AgentSkills 是一个跨平台的开放标准，兼容 20+ 个 agent 平台，包括 Claude Code、OpenAI Codex、OpenClaw、CodeBuddy/WorkBuddy、GitHub Copilot、Gemini CLI、Cursor、Windsurf 等。写一次，到处跑。

---

## 6. 安装与使用

### 前提

已安装并配置 `stride28-search-mcp`。

### 安装

把本 repo clone 到你的 agent 的 skills 目录即可。不同客户端的 skills 目录位置不同，常见的：

```bash
# Claude Code
~/.claude/skills/stride28-search2docs

# OpenClaw
~/.openclaw/skills/stride28-search2docs

# Codex
~/.codex/skills/stride28-search2docs

# CodeBuddy
.codebuddy/skills/stride28-search2docs
```

大部分支持 AgentSkills 标准的客户端也支持直接在对话中说：

> "帮我安装 GitHub 上的 stride28-search2docs skill"

或者直接贴 repo 链接，agent 会自动识别并安装。

### IDE 用户

如果你在 IDE 环境（Kiro / Cursor 等）中使用，不需要安装 skill。直接安装 `stride28-search-mcp`，参考 `prompts/` 里的 workflow 模板自行接入即可。

---

## 7. 旗舰案例

> 自动抓取小红书 / 知乎上的 AI Agent 面经，并写入腾讯文档。

选这个案例是因为它足够痛、足够直观、足够容易展示价值。

同一套链路也适合：

- 产品反馈汇总
- AI 工具评价追踪
- 课程口碑整理
- 岗位信息沉淀
- 竞品体验收集

---

## 8. 一句话定义

> `stride28-search2docs` 是一个建立在 `stride28-search-mcp` 之上的 workflow skill repo，遵循 AgentSkills 开放标准，用来把中文社区中碎片化的真实经验内容，转成结构化、可沉淀、可持续更新的文档结果。
