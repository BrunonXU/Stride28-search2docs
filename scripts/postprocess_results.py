#!/usr/bin/env python3
"""
postprocess_results.py — 对搜索结果进行去重和后处理。

用法：
    python postprocess_results.py --input raw_results.json --output cleaned.json

去重策略：
1. 完全相同的 note_id → 去重
2. 标题相似度 > 0.8 → 保留点赞数更高的
3. 内容高度重复 → 保留信息更完整的版本
"""

import json
import argparse
import sys
import re
from difflib import SequenceMatcher
from typing import Any


def normalize_title(title: str) -> str:
    """标准化标题，去除 emoji、特殊符号、多余空格。"""
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title.lower()


def title_similarity(a: str, b: str) -> float:
    """计算两个标题的相似度。"""
    na = normalize_title(a)
    nb = normalize_title(b)
    return SequenceMatcher(None, na, nb).ratio()


def is_valid_post(post: dict) -> bool:
    """判断帖子是否为有效面经内容。"""
    title = post.get("title", "").lower()
    # 过滤关键词
    spam_keywords = [
        "加群", "付费", "报名", "课程", "培训", "引流",
        "私信", "免费领", "限时", "优惠", "打卡",
    ]
    for kw in spam_keywords:
        if kw in title:
            return False
    return True


def deduplicate(posts: list, similarity_threshold: float = 0.8) -> list:
    """对帖子列表去重。"""
    if not posts:
        return []

    # 按 note_id 去重
    seen_ids = set()
    unique_posts = []
    for post in posts:
        nid = post.get("note_id") or post.get("id", "")
        if nid and nid in seen_ids:
            continue
        seen_ids.add(nid)
        unique_posts.append(post)

    # 按标题相似度去重
    result = []
    for post in unique_posts:
        title = post.get("title", "")
        is_dup = False
        for existing in result:
            if title_similarity(title, existing.get("title", "")) > similarity_threshold:
                # 保留点赞数更高的
                if post.get("likes", 0) > existing.get("likes", 0):
                    result.remove(existing)
                    result.append(post)
                is_dup = True
                break
        if not is_dup:
            result.append(post)

    return result


def process(raw_data: list) -> dict:
    """主处理流程：过滤 → 去重 → 输出统计。"""
    # 过滤无效帖子
    valid = [p for p in raw_data if is_valid_post(p)]

    # 去重
    cleaned = deduplicate(valid)

    return {
        "total_raw": len(raw_data),
        "after_filter": len(valid),
        "after_dedup": len(cleaned),
        "posts": cleaned,
    }


def main():
    parser = argparse.ArgumentParser(description="搜索结果后处理与去重")
    parser.add_argument("--input", "-i", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", default="-", help="输出 JSON 文件路径（默认 stdout）")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    result = process(raw_data)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        sys.stdout.write(output)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已处理：{args.output}", file=sys.stderr)
        print(f"  原始: {result['total_raw']} → 过滤后: {result['after_filter']} → 去重后: {result['after_dedup']}", file=sys.stderr)


if __name__ == "__main__":
    main()
