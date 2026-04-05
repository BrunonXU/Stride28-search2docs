# 腾讯文档 MDX 格式规范

> 本文件是面经场景的 MDX 速查手册。完整的腾讯文档 MDX 规范见腾讯文档 skill 中的 `smartcanvas/mdx_references.md`。

---

## Frontmatter

文档开头必须包含 YAML frontmatter：

```yaml
---
title: Agent与大模型应用面经汇总
icon: 📋
---
```

---

## 标题

使用标准 Markdown 标题语法：

```mdx
# 一级标题
## 二级标题
### 三级标题
```

带颜色的标题使用 `<Heading>` 组件：

```mdx
<Heading level="2" blockColor="red">字节跳动</Heading>
<Heading level="2" blockColor="blue">腾讯</Heading>
```

---

## 文本格式

### 粗体

禁止使用 `**粗体**`，必须使用：

```mdx
<Mark bold>粗体文字</Mark>
```

### 斜体

禁止使用 `*斜体*`，必须使用：

```mdx
<Mark italic>斜体文字</Mark>
```

### 颜色标记

```mdx
<Mark color="red">红色文字</Mark>
<Mark color="blue">蓝色文字</Mark>
<Mark color="orange">橙色文字</Mark>
<Mark color="purple">紫色文字</Mark>
<Mark color="yellow">黄色文字</Mark>
<Mark color="green">绿色文字</Mark>
<Mark color="grey">灰色文字</Mark>
<Mark color="sky_blue">天蓝色文字</Mark>
<Mark color="default">默认颜色</Mark>
```

### 组合使用

```mdx
<Mark bold color="red">字节跳动</Mark>
```

---

## 表格

禁止使用 Markdown 管道语法（`| col1 | col2 |`），必须使用 MDX 组件：

```mdx
<Table>
    <TableRow>
        <TableCell><Mark bold>公司</Mark></TableCell>
        <TableCell><Mark bold>岗位</Mark></TableCell>
        <TableCell><Mark bold>面试轮次</Mark></TableCell>
    </TableRow>
    <TableRow>
        <TableCell><Mark color="red">字节跳动</Mark></TableCell>
        <TableCell>AI Agent 开发工程师</TableCell>
        <TableCell>一面</TableCell>
    </TableRow>
</Table>
```

---

## 链接

禁止使用 Markdown 链接语法（`[文字](url)`），必须使用 MDX 组件：

```mdx
<Link href="https://www.xiaohongshu.com/explore/abc123?xsec_token=XYZ">原文链接</Link>
```

---

## 列表

标准 Markdown 列表语法可用：

```mdx
- 项目一
- 项目二
  - 子项目

1. 有序项目一
2. 有序项目二
```

---

## 分割线

```mdx
---
```

---

## 完整示例

```mdx
---
title: Agent与大模型应用面经汇总
icon: 📋
---

# Agent与大模型应用面经汇总

## 一、今日摘要

- 今日新增帖子数：15
- 去重后有效帖子数：10
- 涉及公司数：5

## 二、按公司分类整理

<Heading level="3" blockColor="red">字节跳动</Heading>

<Table>
    <TableRow>
        <TableCell><Mark bold>公司</Mark></TableCell>
        <TableCell><Mark bold>岗位</Mark></TableCell>
        <TableCell><Mark bold>轮次</Mark></TableCell>
        <TableCell><Mark bold>链接</Mark></TableCell>
    </TableRow>
    <TableRow>
        <TableCell><Mark color="red">字节跳动</Mark></TableCell>
        <TableCell>AI Agent 开发</TableCell>
        <TableCell>一面</TableCell>
        <TableCell><Link href="https://www.xiaohongshu.com/explore/abc123?xsec_token=XYZ">原文</Link></TableCell>
    </TableRow>
</Table>
```

---

## 可用颜色值（TEXT_COLORS）

| 颜色名 | 用途 |
|--------|------|
| red | 字节跳动 |
| blue | 腾讯 |
| orange | 阿里/阿里云 |
| purple | 百度、快手 |
| yellow | 美团 |
| green | 小米 |
| grey | 京东 |
| sky_blue | OpenAI/Anthropic/海外AI |
| default | 其他公司 |
