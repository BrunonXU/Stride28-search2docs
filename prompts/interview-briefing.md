# 面经整理 Workflow

## 触发词

- 采集面经
- 整理面经到腾讯文档
- 小红书面经汇总
- 写进腾讯文档

## 输入

搜索关键词列表（默认）：

- Agent 开发面经
- Agent 应用面经
- AI Agent 面试
- 大模型应用面经
- LLM 应用面经
- 智能体开发面经
- RAG 面经
- 多 Agent 面经

## 执行流程

### 1. 登录

```
MCP 工具：login_xiaohongshu
参数：无
说明：弹出浏览器，用小红书 App 扫码登录。登录成功后复用登录态。
```

### 2. 搜索

对每个关键词调用搜索：

```
MCP 工具：search_xiaohongshu
参数：
  query: "{关键词}"
  limit: 20
  note_type: "all"
```

返回：标题、URL、作者、点赞数、note_id、xsec_token 等。

### 3. 初步筛选

从搜索结果中筛选：

保留：
- 真实面试经验、面试复盘、面试题总结、岗位经历分享
- 优先包含：公司名、岗位名、面试轮次、高频问题、回答思路

过滤：
- 广告、培训引流、付费社群推广
- 纯情绪帖、无实质内容
- spam

### 4. 获取详情

对筛选后的帖子逐一获取完整内容：

```
MCP 工具：get_note_detail
参数：
  note_id: "{从搜索结果获取}"
  xsec_token: "{从搜索结果获取}"
  max_comments: 10
```

返回：正文、评论、图片、互动数据。

### 5. 结构化提取

从每条帖子详情中提取：
- 公司名（无法识别则标记"其他/未明确"）
- 岗位名
- 招聘类型（实习/校招/社招）
- 面试轮次
- 发布时间
- 作者
- 原帖链接（含 xsec_token）
- 面经摘要（提炼总结，不要只贴原文）
- 高频问题
- 回答要点
- 对 Agent/大模型应用岗位准备的启发

### 6. 去重

- 标题相近 → 只保留一条
- 链接相同 → 只保留一条
- 内容高度重复 → 保留信息更完整的版本

### 7. 生成文档

按 `references/specification.md` 的结构生成内容：
- 一、今日摘要
- 二、按公司分类整理（颜色标记）
- 三、高频问题归纳（8 个主题分类）
- 四、给 Bruno 的针对性建议
- 五、原始链接列表

按 `references/tencent-docs-mdx.md` 的格式规范输出 MDX。

### 8. 写入腾讯文档

查找文档：
```bash
mcporter call tencent-docs manage.search_file --args '{"search_key": "Agent与大模型应用面经汇总"}' 2>&1
```

文档不存在 → 创建：
```bash
mcporter call tencent-docs create_smartcanvas_by_mdx --args '{"title": "Agent与大模型应用面经汇总", "mdx": "{MDX 内容}"}' 2>&1
```

文档已存在 → 追加章节到末尾（id 为空 = 追加到文档末尾）：
```bash
mcporter call tencent-docs smartcanvas.edit --args '{"file_id": "{file_id}", "action": "INSERT_AFTER", "content": "{新章节 MDX}"}' 2>&1
```

## 输出

仅返回：
1. 文档名
2. 新增条目数
3. 涉及公司数
4. 文档链接

## 时间范围

- 搜索最近 30 天内的公开帖子
- 优先近 7 天
