---
name: interview-collector
description: 采集小红书/知乎上的公开面经并写入腾讯文档。触发词："采集面经"、"写进腾讯文档"、"整理面经到腾讯文档"、"小红书面经汇总"。
---

# 面经采集器

> ⚠️ **Beta** — 社区平台账号建议用小号登录，频繁搜索可能触发平台风控提醒，请合理使用。

## ⛔ 强制交互检查清单（每一步都必须对照执行）

以下 5 个检查点，每一个都必须停下来等用户回复后才能继续。
跳过任何一个 = 流程失败。不存在"用户没说所以我自己决定"的情况。

| # | 检查点 | 什么时候 | 必须问什么 | 禁止做什么 |
|---|--------|----------|-----------|-----------|
| ① | 启动确认 | 开始搜索前 | 搜哪个平台？用哪些关键词？每个关键词搜多少条？ | 禁止不问就开始搜索 |
| ② | 搜索汇报 | 所有关键词搜完后 | 汇报总数/公司分布/高赞数量，问用户要获取多少条详情 | 禁止自己决定获取几条 |
| ③ | 过滤确认 | 获取详情并过滤去重后 | 汇报保留了多少条/按公司分布/质量分级，问用户保留哪些 | 禁止不问就生成文档 |
| ④ | 文档名确认 | 生成 MDX 后、写入前 | 文档叫什么名字？检查有没有同名文档 | 禁止不问就写入 |
| ⑤ | 写入确认 | 找到同名文档时 | 追加到已有文档还是创建新的？ | 禁止自己决定新建或追加 |

**如果你发现自己正在做某件事但还没问过用户 → 立刻停下来问。**

---

## 前置条件

本 skill 依赖两个 MCP 服务和一个 skill，必须先装好：

1. **stride28-search MCP** — 小红书/知乎搜索能力，详见 `references/mcp-setup.md`
2. **tencent-docs MCP + 腾讯文档 skill** — 写入腾讯文档的能力
   - 安装腾讯文档 skill：从 https://cdn.addon.tencentsuite.com/static/tencent-docs.zip 下载解压到 skills 目录
   - 或者通过 mcporter 配置 tencent-docs 服务，详见 `references/tencent-docs-setup.md`
   - WorkBuddy 用户无需配置，内置已有

> ⚠️ 腾讯文档 skill 里包含了完整的 MDX 格式规范和工具调用规范（`smartcanvas/entry.md`、`smartcanvas/mdx_references.md`）。写入文档时必须按照腾讯文档 skill 的规范调用工具，不要自己猜参数。

### 腾讯文档快速授权

如果 agent 调用腾讯文档时报错"未配置"或"Token invalid"，让用户做一件事：

1. 打开 https://docs.qq.com/scenario/open-claw.html
2. QQ/微信扫码登录
3. 页面上会显示 Token，复制贴回来

agent 拿到 token 后执行：
```bash
mcporter config add tencent-docs "https://docs.qq.com/openapi/mcp" \
    --header "Authorization=$TOKEN" --transport http --scope home
```

> Token 会过期。如果调用时报 `Mcp Token user invalid`，让用户重新去上面的链接获取新 Token。不要反复重试同一个失效的 Token。

或者如果已安装腾讯文档 skill（带 setup.sh），设置环境变量 `TENCENT_DOCS_TOKEN` 后运行 `bash setup.sh tdoc_check_and_start_auth`。

---

## 核心流程

1. ⛔① 确认搜索参数（平台、关键词、每个搜多少条）
2. 登录并搜索
3. ⛔② 搜索汇报，问用户获取多少条详情
4. 获取详情
5. ⛔③ 过滤去重后汇报，问用户保留哪些
6. 生成 MDX 格式内容
7. ⛔④ 确认文档名，检查同名文档
8. ⛔⑤ 如有同名文档，问新建还是追加
9. 写入腾讯文档

---

## ⛔ 检查点① — 启动确认（禁止不问就开始搜索）

在开始任何搜索之前，必须先向用户确认：

1. **搜索平台**：小红书 / 知乎 / 都搜？（默认：小红书）
2. **搜索关键词**：使用默认关键词还是自定义？
   - 默认：Agent开发面经、AI Agent面试、大模型应用面经、LLM应用面经、智能体开发面经、RAG面经、多Agent面经、Agent面试题
   - 用户可指定公司或岗位
3. **每个关键词搜多少条**：默认 15 条，可调整（10-20，不建议超过 20）
4. **确认开始**：列出配置，等用户确认

```
Agent: 开始采集面经前，确认一下：
  - 搜索平台：小红书
  - 关键词：Agent开发面经、AI Agent面试、大模型应用面经...（共 8 个）
  - 每个关键词搜：15 条
  要调整还是直接开始？
```

---

## 第一步 — 登录

### 小红书
```
工具：login_xiaohongshu
参数：无
```

### 知乎（如果用户选择了知乎）
```
工具：login_zhihu
参数：无
```

---

## 第二步 — 搜索

### 小红书
```
工具：search_xiaohongshu
参数：
  query: "{关键词}"
  limit: {用户在检查点①确认的条数，默认 15，范围 10-20}
  note_type: "all"
```

### 知乎（可选）
```
工具：search_zhihu
参数：
  query: "{关键词}"
  limit: {默认 10，范围 5-10}
```

### ⚠️ 风控与错误处理

搜索过程中如果遇到以下错误，必须立即停止，不要重试：
- `captcha_detected` — 验证码拦截，等待后重试
- `search_blocked` — 搜索被拦截，检查登录态或等待
- `risk_cooldown_active` — 风控冷却中，默认 15 分钟后再试

**使用原则：** 本 MCP 是低频定向检索工具，不是批量采集器。不要连续发起很多轮相似搜索。每个关键词搜一次就够了。

### ⛔ 检查点②：搜索汇报（必须停下来等用户回复）

搜完所有关键词后，必须停下来汇报。**禁止自己决定获取几条详情。**

```
Agent: 已搜索完全部 8 个关键词，结果汇总：
  - 原始结果：共 160 条
  - 按公司分布：字节 23 条、阿里 18 条、美团 15 条、快手 12 条、其他 92 条
  - 高赞帖子（>100赞）：约 35 条
  - 看起来是真实面经的：约 50 条

  我的建议：获取 Top 25-30 条的详情（高赞 + 含公司名的优先）
  你觉得呢？
```

---

## 第三步 — 获取帖子详情

用户在检查点②确认后，按用户指定的数量获取详情：

### 小红书
```
工具：get_note_detail
参数：
  note_id: "{从搜索结果获取}"
  xsec_token: "{从搜索结果获取}"
  max_comments: 10          # 推荐 10-20，硬上限 50，面经场景 10 够用
```

### 知乎
```
工具：get_zhihu_question
参数：
  question_id: "{从搜索结果的 xsec_token 字段获取}"
  limit: 5                  # 推荐 3-5，获取 Top N 回答
  max_content_length: 10000 # 0=不截断，面经场景 10000 够用
```

从详情中提取：公司名、岗位名、招聘类型、面试轮次、发布时间、作者、面经摘要、高频问题、回答要点、启发。

---

## 第四步 — 过滤与去重

可使用 `scripts/filter_and_dedupe.py` 辅助，也可由 agent 直接判断。

过滤规则：广告/引流/付费社群/纯情绪帖
去重规则：相同 ID / 标题相似度 > 75% / 跨关键词重复

### ⛔ 检查点③：过滤确认（必须停下来等用户回复）

**禁止不问就生成文档。**

```
Agent: 过滤去重完成：
  - 获取详情：25 条 → 去重 3 条 → 有效 22 条
  - 按公司：字节 5 条、阿里 4 条、美团 3 条...
  - 按质量：高质量 15 条、中等 5 条、一般 2 条

  我的建议：保留全部 22 条（高质量详细展开，一般的简要列出）
  你觉得呢？
```

---

## 第五步 — 生成 MDX

格式规范见 `specification.md`，MDX 规则见 `references/tencent-docs-mdx.md`。

### 文档结构
```
## {日期} 面经更新
## 一、今日摘要
## 二、按公司分类整理
## 三、高频问题归纳
## 四、给 Bruno 的针对性建议
## 五、原始链接列表
```

### 公司颜色映射

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
| 其他 | default |

### MDX 关键规则

1. 表格：`<Table>` / `<TableRow>` / `<TableCell>`，禁止 Markdown 管道语法
2. 链接：`<Link href="...">文字</Link>`，禁止 Markdown 语法
3. 粗体：`<Mark bold>`，禁止 `**粗体**`
4. 公司名：`<Mark color="{颜色}">公司名</Mark>`
5. Frontmatter：`---\ntitle: ...\nicon: 📋\n---`，不加 cover
6. 正文不重复 frontmatter title

校验：`python scripts/validate_mdx.py --input output.mdx`

---

## 第六步 — 写入腾讯文档

### ⛔ 检查点④：文档名确认（必须停下来等用户回复）

**禁止不问就写入。**

```
Agent: 内容已生成（22 条面经），准备写入腾讯文档。
  - 文档名：《Agent与大模型应用面经汇总 2026-04-05》（默认带日期）
  - 要用这个名字还是换一个？
```

用户确认后，搜索是否已存在同名文档：
```bash
node scripts/write_doc.mjs search --keyword "{文档名}"
```

- 没找到 → 创建新文档
- 找到了 → ⛔ 检查点⑤：问用户追加还是新建

```
Agent: 找到同名文档《Agent与大模型应用面经汇总》
  - 追加到这个文档？（末尾加「2026-04-05 面经更新」章节）
  - 还是创建新文档？
```

### 写入

**方案一（推荐）：agent 直接调用 tencent-docs MCP 工具**

如果你的客户端已配置 tencent-docs MCP 服务，直接调用工具，不走命令行：
```
工具：create_smartcanvas_by_mdx
参数：{ "title": "标题", "mdx": "{读取 MDX 文件的完整内容}" }

工具：smartcanvas.edit
参数：{ "file_id": "{id}", "action": "INSERT_AFTER", "content": "{MDX 内容}" }
```
这是最可靠的方式，不受命令行长度限制，不受操作系统差异影响。

**方案二：脚本写入**

先把 MDX 内容写到文件，再用脚本：
```bash
node scripts/write_doc.mjs create --title "标题" --mdx-file output.mdx
node scripts/write_doc.mjs append --file-id {id} --mdx-file output.mdx
```

**方案三：mcporter CLI（仅适合短内容）**
```bash
mcporter call tencent-docs create_smartcanvas_by_mdx title:"标题" mdx:"短内容"
```

### ⚠️ 写入常见问题排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `Mcp Token user invalid` | Token 过期或不正确 | 重新去 https://docs.qq.com/scenario/open-claw.html 获取新 Token |
| `missing required parameters: [mdx]` | MDX 内容没传进去 | 不要用 `@file` 或 `$(cat file)`，必须把文件内容读出来作为字符串传入 |
| `tencent-docs 未配置`（脚本报错但 `mcporter list` 正常） | mcporter SDK 读不到配置 | 不用脚本，用方案一直接调 MCP 工具，或用 mcporter CLI |
| `Unknown flag '--args-file'` | mcporter 0.8.x 不支持 `--args-file` | 用 `--args` 传 JSON 字符串，或用 Python 生成 JSON 再传 |
| 命令行太长 / 参数被截断 | MDX 内容 >8KB，超出命令行限制 | 用方案一（MCP 工具直接调用）或方案二（脚本从文件读取） |
| 文档内容是文件路径而不是内容 | 用了 `mdx:@filepath` 语法，mcporter 不支持 | mdx 参数必须传内容字符串，不是文件路径 |
| `$(cat file)` 不工作 | Windows PowerShell/CMD 不支持 bash 语法 | 用 PowerShell 的 `Get-Content file -Raw` 或 Python 读文件 |

**核心原则：遇到写入失败不要原地重试同一种方式超过 2 次，按方案一→二→三的顺序切换。如果连续失败 3 次，停下来告诉用户具体错误，让用户决定怎么办。**

### ⚠️ Windows 环境特别注意

- `$(cat file)` 是 bash 语法，Windows 上不工作
- PowerShell 传大段 JSON 容易出转义问题
- 推荐方式：用 Python 读文件生成 JSON，再传给 mcporter：
  ```bash
  python -c "import json; mdx=open('output.mdx','r',encoding='utf-8').read(); print(json.dumps({'title':'标题','mdx':mdx}))" > _tmp.json
  mcporter call tencent-docs create_smartcanvas_by_mdx --args "$(cat _tmp.json)"
  ```
- 或者最稳的方式：让 agent 直接调用 tencent-docs MCP 工具（方案一），完全不走命令行

---

## 输出

写入完成后，只返回：
1. 文档名
2. 新增条目数
3. 涉及公司数
4. 文档链接

---

## 资源文件

- `specification.md` — 面经格式规范（本 skill 专属）
- `references/tencent-docs-mdx.md` — MDX 格式规则（共享）
- `references/mcp-setup.md` — stride28-search-mcp 安装配置
- `references/tencent-docs-setup.md` — 腾讯文档 MCP 安装配置
- `scripts/write_doc.mjs` — 写入腾讯文档
- `scripts/filter_and_dedupe.py` — 过滤去重
- `scripts/validate_mdx.py` — MDX 校验
- `scripts/generate_mdx.py` — JSON → MDX 转换
