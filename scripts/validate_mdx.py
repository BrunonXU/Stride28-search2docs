#!/usr/bin/env python3
"""
validate_mdx.py — 校验 MDX 内容是否符合腾讯文档规范。

用法：
    python validate_mdx.py --input output.mdx
    python validate_mdx.py --input output.mdx --strict

检查项：
1. frontmatter 存在且有 title
2. 禁止 **bold** / *italic*（应使用 <Mark>）
3. 禁止 Markdown 表格语法（应使用 <Table>）
4. 禁止 Markdown 链接语法（应使用 <Link>）
5. 颜色值是否在白名单内
6. 正文不重复 frontmatter title
"""

import re
import sys
import argparse

TEXT_COLORS = {"default", "grey", "blue", "sky_blue", "green", "yellow", "orange", "red", "rose_red", "purple"}
BLOCK_COLORS = {
    "default", "grey", "light_grey", "dark",
    "light_blue", "blue", "light_sky_blue", "sky_blue",
    "light_green", "green", "light_yellow", "yellow",
    "light_orange", "orange", "light_red", "red",
    "light_rose_red", "rose_red", "light_purple", "purple",
}
BORDER_COLORS = {"default", "grey", "blue", "sky_blue", "green", "yellow", "orange", "red", "rose_red", "purple"}


def validate(content: str, strict: bool = False) -> list[dict]:
    """校验 MDX 内容，返回问题列表。"""
    issues = []
    lines = content.split("\n")

    # 1. frontmatter 检查
    if not content.startswith("---"):
        issues.append({"severity": "error", "line": 1, "message": "缺少 frontmatter（文档必须以 --- 开头）"})
    else:
        fm_end = content.find("---", 3)
        if fm_end == -1:
            issues.append({"severity": "error", "line": 1, "message": "frontmatter 未闭合"})
        else:
            fm = content[3:fm_end]
            if "title:" not in fm:
                issues.append({"severity": "error", "line": 1, "message": "frontmatter 缺少 title 字段"})

            # 检查正文是否重复 title
            fm_title_match = re.search(r"title:\s*(.+)", fm)
            if fm_title_match:
                fm_title = fm_title_match.group(1).strip().strip('"').strip("'")
                body = content[fm_end + 3:]
                if re.match(rf"\s*#\s+{re.escape(fm_title)}\s*$", body, re.MULTILINE):
                    issues.append({
                        "severity": "warning", "line": 0,
                        "message": f"正文第一个标题与 frontmatter title 重复：「{fm_title}」"
                    })

    # 逐行检查
    for i, line in enumerate(lines, 1):
        # 2. 禁止 Markdown bold/italic
        if re.search(r"(?<!\*)\*\*(?!\*).+?\*\*(?!\*)", line):
            issues.append({"severity": "error", "line": i, "message": f"禁止使用 **bold**，应使用 <Mark bold>"})
        if re.search(r"(?<!\*)\*(?!\*)(?!\s).+?(?<!\s)\*(?!\*)", line) and "<Mark" not in line:
            if not line.strip().startswith("- ") and not line.strip().startswith("* "):
                if strict:
                    issues.append({"severity": "warning", "line": i, "message": f"可能使用了 *italic*，应使用 <Mark italic>"})

        # 3. 禁止 Markdown 表格
        if re.match(r"\s*\|.+\|.+\|", line) and "<Table" not in line:
            issues.append({"severity": "error", "line": i, "message": "禁止使用 Markdown 表格语法，应使用 <Table> 组件"})

        # 4. 禁止 Markdown 链接
        if re.search(r"\[.+?\]\(https?://.+?\)", line) and "<Link" not in line:
            issues.append({"severity": "error", "line": i, "message": "禁止使用 [text](url) 语法，应使用 <Link href=\"...\">text</Link>"})

        # 5. 颜色值检查
        color_matches = re.findall(r'color="([^"]+)"', line)
        for color in color_matches:
            if "Mark" in line and color not in TEXT_COLORS and color not in BLOCK_COLORS:
                issues.append({"severity": "error", "line": i, "message": f"无效颜色值: {color}"})

        blockcolor_matches = re.findall(r'blockColor="([^"]+)"', line)
        for color in blockcolor_matches:
            if color not in BLOCK_COLORS:
                issues.append({"severity": "error", "line": i, "message": f"无效 blockColor: {color}"})

        bordercolor_matches = re.findall(r'borderColor="([^"]+)"', line)
        for color in bordercolor_matches:
            if color not in BORDER_COLORS:
                issues.append({"severity": "error", "line": i, "message": f"无效 borderColor: {color}"})

        # 6. 表达式属性检查
        if re.search(r'level=\{', line) or re.search(r'width=\{', line):
            issues.append({"severity": "error", "line": i, "message": "禁止使用 {...} 表达式属性，应使用双引号字符串"})

    return issues


def main():
    parser = argparse.ArgumentParser(description="校验 MDX 是否符合腾讯文档规范")
    parser.add_argument("--input", "-i", required=True, help="MDX 文件路径")
    parser.add_argument("--strict", action="store_true", help="严格模式（更多警告）")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    issues = validate(content, strict=args.strict)

    if not issues:
        print("✅ MDX 校验通过，未发现问题。")
        sys.exit(0)

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    for issue in issues:
        icon = "❌" if issue["severity"] == "error" else "⚠️"
        loc = f"L{issue['line']}" if issue["line"] else ""
        print(f"  {icon} {loc} {issue['message']}")

    print(f"\n共 {len(errors)} 个错误, {len(warnings)} 个警告")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
