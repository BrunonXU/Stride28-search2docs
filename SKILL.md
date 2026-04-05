---
name: xhs-interview-collector
description: 当用户想要采集小红书上的公开面经并写入腾讯文档时使用此技能。完整流程：MCP 搜索 → 去重整理 → MDX 格式化 → 通过 mcporter 写入腾讯文档。触发词包括"采集面经"、"写进腾讯文档"、"整理面经到腾讯文档"、"小红书面经汇总"。
---

# XHS 面经采集器

## 概述

此技能用于自动采集小红书上的公开面经帖子，并按照固定格式写入腾讯文档。

**核心流程：**
1. 通过 `stride28-search` MCP 服务搜索小红书
2. 获取帖子详情，提取结构化信息
3. 过滤、去重、数据结构化
4. 按照腾讯文档 MDX 规范生成内容
5. 通过 `mcporter` CLI（`tencent-docs` MCP 服务）写入腾讯文档

**必需 MCP 服务：**
- `stride28-search`（小红书/知乎搜索）
- `tencent-docs`（腾讯文档写入，通过 mcporter 调用）

---

## 第一步 — 登录小红书

搜索前必须先登录。调用后会弹出浏览器窗口，需要用户使用小红书 App 扫码完成登录。

**MCP 调用：**
```
工具：login_xiaohongshu
参数：无
```

登录成功后，后续搜索调用将复用登录态。

如果登录态失效，可以重置后重新登录：
```
工具：reset_xiaohongshu_login
参数：无
```

---

## 第二步 — 搜索小红书

使用以下搜索词逐一搜索（可根据需要调整）：

- "Agent开发面经"
- "AI Agent面试"
- "大模型应用面经"
- "LLM应用面经"
- "智能体开发面经"
- "RAG面经"
- "多Agent面经"
- "Agent面试题"

**MCP 调用：**
```
工具：search_xiaohongshu
参数：
  query: "Agent开发面经"    # 搜索关键词
  limit: 20                 # 返回条数，建议 10-20
  note_type: "all"          # 笔记类型，默认 all
```

**返回字段：** 标题、URL、作者、点赞数、note_id、xsec_token 等。

每次搜索后：
1. 筛选包含真实面经内容的帖子
2. 过滤广告、付费群、无实质内容的情绪帖、spam
3. 记录 `note_id` 和 `xsec_token`，后续获取详情需要

---

## 第三步 — 获取帖子详情

对筛选后的帖子，逐一获取完整内容：

**MCP 调用：**
```
工具：get_note_detail
参数：
  note_id: "abc123def"      # 从搜索结果中获取
  xsec_token: "XYZ..."      # 从搜索结果中获取
  max_comments: 10           # 评论数，默认 10，一般不需要更多
```

**返回字段：** 正文、评论、图片、互动数据等。

从详情中提取：
- 公司名（无法识别则标记"其他/未明确"）
- 岗位名
- 招聘类型（实习/校招/社招）
- 面试轮次
- 发布时间
- 作者
- 面经摘要（提炼总结，不要只贴原文）
- 高频问题
- 回答要点
- 对 Agent/大模型应用岗位准备的启发

---

## 第四步 — 过滤与去重

### 保留条件
- 真实面试经验、面试复盘、面试题总结、岗位经历分享
- 优先保留包含：公司名、岗位名、面试轮次、高频问题、回答思路、结果或反馈

### 过滤条件
- 广告、培训引流、付费社群推广
- 纯情绪帖、无实质内容的帖子

### 去重规则
- 标题相近、链接相同、内容高度重复的帖子只保留一条
- 优先保留信息更完整的版本

### 时间范围
- 搜索最近 30 天内的公开帖子
- 优先近 7 天

---

## 第五步 — 应用格式规范

完整格式规范见 `references/specification.md`，MDX 格式规则见 `references/tencent-docs-mdx.md`。

### 文档结构

```
# Agent与大模型应用面经汇总

## 一、今日摘要
## 二、按公司分类整理
## 三、高频问题归纳
## 四、给 Bruno 的针对性建议
## 五、原始链接列表
```

### 公司颜色映射（用 `<Mark color="...">` 包裹）

| 公司 | 颜色 |
|------|------|
| 字节跳动 | red |
| 腾讯 | blue |
| 阿里/阿里云 | orange |
| 百度 | purple |
| 美团 | yellow |
| 快手 | purple |
| 小米 | green |
| 京东 | grey |
| OpenAI/Anthropic/海外AI | sky_blue |
| 其他公司 | default |

### 链接中的 xsec_token

每条原文链接必须包含 `xsec_token`（从搜索结果中获取），格式：
```
https://www.xiaohongshu.com/explore/{note_id}?xsec_token={token}
```

---

## 第六步 — 生成 MDX 内容

可使用 `scripts/generate_mdx.py` 辅助生成，也可由 agent 直接按规范生成。

### MDX 关键规则

1. **表格**：必须使用 `<Table>` / `<TableRow>` / `<TableCell>` 组件，禁止 Markdown 管道语法
2. **链接**：必须使用 `<Link href="...">文字</Link>`，禁止 Markdown 语法
3. **粗体**：必须使用 `<Mark bold>`，禁止 `**粗体**`
4. **公司名**：用 `<Mark color="{颜色}">公司名</Mark>` 包裹
5. **Frontmatter**：文档开头必须有 YAML frontmatter
6. **标题颜色**：使用 `<Heading level="2" blockColor="red">` 添加颜色

---

## 第七步 — 写入腾讯文档

> 腾讯文档 MCP 服务名：`tencent-docs`，端点：`https://docs.qq.com/openapi/mcp`。
> 首次使用需完成授权，详见 `references/auth.example.md`。

### 查找文档
```bash
mcporter call tencent-docs manage.search_file --args '{"search_key": "Agent与大模型应用面经汇总"}' 2>&1
```

### 创建新文档（文档不存在时）
```bash
mcporter call tencent-docs create_smartcanvas_by_mdx --args '{"title": "Agent与大模型应用面经汇总", "mdx": "<完整 MDX 内容>"}' 2>&1
```

从返回结果中获取 `file_id` 和 `url`。

### 追加章节（文档已存在时）

章节标题为当天日期，如 `## 2026-04-05 面经更新`。使用 `INSERT_AFTER`（id 为空则追加到文档末尾）：
```bash
mcporter call tencent-docs smartcanvas.edit --args '{"file_id": "{file_id}", "action": "INSERT_AFTER", "content": "<新章节 MDX>"}' 2>&1
```

---

## 输出

写入完成后，只返回：
1. 文档名
2. 新增条目数
3. 涉及公司数
4. 文档链接

---

## 资源文件

- `references/specification.md` — 完整格式规范
- `references/tencent-docs-mdx.md` — MDX 格式规则（颜色、表格、链接、Mark 组件）
- `references/auth.example.md` — 认证配置示例
- `prompts/interview-briefing.md` — 面经整理 workflow 模板
- `scripts/generate_mdx.py` — 结构化数据 → MDX 转换脚本
- `scripts/postprocess_results.py` — 搜索结果去重脚本
