#!/usr/bin/env python3
"""
generate_mdx.py — 将结构化面经数据转换为腾讯文档专用的 MDX 格式。

用法：
    python generate_mdx.py --input data.json --output output.mdx

输入 JSON 格式：
{
    "title": "Agent与大模型应用面经汇总",
    "date": "2026-04-05",
    "summary": {
        "total_posts": 15,
        "valid_posts": 10,
        "company_count": 5,
        "top_positions": ["AI Agent 开发", "大模型应用工程师"],
        "top_topics": ["Agent 架构", "RAG", "Prompt Engineering"],
        "top_posts": [{"title": "...", "url": "...", "reason": "..."}]
    },
    "companies": {
        "字节跳动": {
            "color": "red",
            "posts": [
                {
                    "position": "AI Agent 开发",
                    "type": "社招",
                    "round": "一面",
                    "date": "2026-04-01",
                    "author": "xxx",
                    "url": "https://www.xiaohongshu.com/explore/abc?xsec_token=XYZ",
                    "summary": "...",
                    "questions": ["问题1", "问题2"],
                    "key_points": ["要点1", "要点2"],
                    "insights": "..."
                }
            ]
        }
    },
    "frequent_questions": {
        "Agent 架构设计": [
            {
                "question": "...",
                "focus": "...",
                "answer_hint": "..."
            }
        ]
    },
    "advice": {
        "skills_required": ["..."],
        "gaps": ["..."],
        "project_tips": ["..."],
        "daily_questions": ["..."]
    },
    "links": [
        {"company": "字节跳动", "title": "...", "url": "...", "date": "2026-04-01"}
    ]
}
"""

import json
import argparse
import sys
from typing import Any

# 公司颜色映射
COMPANY_COLORS = {
    "字节跳动": "red",
    "腾讯": "blue",
    "阿里": "orange",
    "阿里云": "orange",
    "百度": "purple",
    "美团": "yellow",
    "快手": "purple",
    "小米": "green",
    "京东": "grey",
    "OpenAI": "sky_blue",
    "Anthropic": "sky_blue",
}

DEFAULT_COLOR = "default"


def get_color(company: str) -> str:
    """根据公司名返回对应颜色。"""
    for key, color in COMPANY_COLORS.items():
        if key in company:
            return color
    return DEFAULT_COLOR


def generate_frontmatter(title: str) -> str:
    return f"""---
title: {title}
icon: 📋
---"""


def generate_summary(summary: dict) -> str:
    lines = [
        "## 一、今日摘要\n",
        f"- 今日新增帖子数：{summary.get('total_posts', 0)}",
        f"- 去重后有效帖子数：{summary.get('valid_posts', 0)}",
        f"- 涉及公司数：{summary.get('company_count', 0)}",
    ]
    if summary.get("top_positions"):
        lines.append(f"- 高频岗位方向：{'、'.join(summary['top_positions'])}")
    if summary.get("top_topics"):
        lines.append("\n今日最常见的面试主题：")
        for i, topic in enumerate(summary["top_topics"][:10], 1):
            lines.append(f"{i}. {topic}")
    if summary.get("top_posts"):
        lines.append("\n今日最值得关注的面经：")
        for post in summary["top_posts"][:3]:
            lines.append(
                f'- <Link href="{post["url"]}">{post["title"]}</Link>'
                + (f" — {post['reason']}" if post.get("reason") else "")
            )
    return "\n".join(lines)


def generate_company_table(company: str, color: str, posts: list) -> str:
    lines = [
        f'\n<Heading level="3" blockColor="{color}">{company}</Heading>\n',
        "<Table>",
        "    <TableRow>",
    ]
    headers = ["公司", "岗位", "类型", "轮次", "发布时间", "作者", "链接", "摘要", "高频问题", "回答要点", "启发"]
    for h in headers:
        lines.append(f"        <TableCell><Mark bold>{h}</Mark></TableCell>")
    lines.append("    </TableRow>")

    for post in posts:
        lines.append("    <TableRow>")
        lines.append(f'        <TableCell><Mark color="{color}">{company}</Mark></TableCell>')
        lines.append(f"        <TableCell>{post.get('position', '未明确')}</TableCell>")
        lines.append(f"        <TableCell>{post.get('type', '未明确')}</TableCell>")
        lines.append(f"        <TableCell>{post.get('round', '未明确')}</TableCell>")
        lines.append(f"        <TableCell>{post.get('date', '未明确')}</TableCell>")
        lines.append(f"        <TableCell>{post.get('author', '未明确')}</TableCell>")
        url = post.get("url", "#")
        lines.append(f'        <TableCell><Link href="{url}">原文</Link></TableCell>')
        lines.append(f"        <TableCell>{post.get('summary', '未明确')}</TableCell>")
        questions = post.get("questions", [])
        lines.append(f"        <TableCell>{'；'.join(questions) if questions else '未明确'}</TableCell>")
        key_points = post.get("key_points", [])
        lines.append(f"        <TableCell>{'；'.join(key_points) if key_points else '未明确'}</TableCell>")
        lines.append(f"        <TableCell>{post.get('insights', '未明确')}</TableCell>")
        lines.append("    </TableRow>")

    lines.append("</Table>")
    return "\n".join(lines)


def generate_companies_section(companies: dict) -> str:
    lines = ["\n## 二、按公司分类整理\n"]
    for company, data in companies.items():
        color = data.get("color", get_color(company))
        posts = data.get("posts", [])
        if posts:
            lines.append(generate_company_table(company, color, posts))
    return "\n".join(lines)


def generate_questions_section(frequent_questions: dict) -> str:
    lines = ["\n## 三、高频问题归纳\n"]
    for category, questions in frequent_questions.items():
        lines.append(f"\n### {category}\n")
        for q in questions:
            lines.append(f"<Mark bold>{q.get('question', '')}</Mark>\n")
            if q.get("focus"):
                lines.append(f"- 常见考察点：{q['focus']}")
            if q.get("answer_hint"):
                lines.append(f"- 推荐回答思路：{q['answer_hint']}")
            lines.append("")
    return "\n".join(lines)


def generate_advice_section(advice: dict) -> str:
    lines = ["\n## 四、给 Bruno 的针对性建议\n"]
    if advice.get("skills_required"):
        lines.append("### 今天面经反映出的能力要求\n")
        for s in advice["skills_required"]:
            lines.append(f"- {s}")
    if advice.get("gaps"):
        lines.append("\n### 最该补的知识点\n")
        for g in advice["gaps"]:
            lines.append(f"- {g}")
    if advice.get("project_tips"):
        lines.append("\n### 面试中最值得准备的项目讲法\n")
        for t in advice["project_tips"]:
            lines.append(f"- {t}")
    if advice.get("daily_questions"):
        lines.append("\n### 明天可以重点刷的问题\n")
        for i, q in enumerate(advice["daily_questions"][:10], 1):
            lines.append(f"{i}. {q}")
    return "\n".join(lines)


def generate_links_section(links: list) -> str:
    lines = [
        "\n## 五、原始链接列表\n",
        "<Table>",
        "    <TableRow>",
        "        <TableCell><Mark bold>公司</Mark></TableCell>",
        "        <TableCell><Mark bold>标题</Mark></TableCell>",
        "        <TableCell><Mark bold>链接</Mark></TableCell>",
        "        <TableCell><Mark bold>发布时间</Mark></TableCell>",
        "    </TableRow>",
    ]
    for link in links:
        company = link.get("company", "未明确")
        color = get_color(company)
        lines.append("    <TableRow>")
        lines.append(f'        <TableCell><Mark color="{color}">{company}</Mark></TableCell>')
        lines.append(f"        <TableCell>{link.get('title', '未明确')}</TableCell>")
        url = link.get("url", "#")
        lines.append(f'        <TableCell><Link href="{url}">原文</Link></TableCell>')
        lines.append(f"        <TableCell>{link.get('date', '未明确')}</TableCell>")
        lines.append("    </TableRow>")
    lines.append("</Table>")
    return "\n".join(lines)


def generate_mdx(data: dict) -> str:
    """主入口：从结构化数据生成完整 MDX 文档。"""
    title = data.get("title", "Agent与大模型应用面经汇总")
    date = data.get("date", "")

    parts = [
        generate_frontmatter(title),
        "",
    ]

    if date:
        parts.append(f"## {date} 面经更新\n")

    if data.get("summary"):
        parts.append(generate_summary(data["summary"]))

    if data.get("companies"):
        parts.append(generate_companies_section(data["companies"]))

    if data.get("frequent_questions"):
        parts.append(generate_questions_section(data["frequent_questions"]))

    if data.get("advice"):
        parts.append(generate_advice_section(data["advice"]))

    if data.get("links"):
        parts.append(generate_links_section(data["links"]))

    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description="将结构化面经数据转换为腾讯文档 MDX 格式")
    parser.add_argument("--input", "-i", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", default="-", help="输出 MDX 文件路径（默认 stdout）")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    mdx_content = generate_mdx(data)

    if args.output == "-":
        sys.stdout.write(mdx_content)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(mdx_content)
        print(f"已生成：{args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
