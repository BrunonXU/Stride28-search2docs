#!/usr/bin/env python3
"""
filter_and_dedupe.py — 对小红书搜索结果进行过滤、去重、评分排序。

用法：
    python filter_and_dedupe.py --input raw_results.json --output cleaned.json
    python filter_and_dedupe.py --input raw_results.json --output cleaned.json --min-likes 50

输入 JSON 格式（搜索结果数组）：
[
    {"id": "...", "title": "...", "author": "...", "likes": 100, "snippet": "...", "xsec_token": "...", ...},
    ...
]

输出 JSON 格式：
{
    "stats": {"total_raw": 96, "filtered_spam": 12, "filtered_dedup": 8, "final": 76},
    "filtered_reasons": [{"id": "...", "title": "...", "reason": "广告引流"}],
    "posts": [...]
}
"""

import json
import argparse
import re
import sys
from difflib import SequenceMatcher


# ── 广告/引流/无效内容关键词 ──
SPAM_KEYWORDS = [
    "加群", "付费", "报名", "课程", "培训", "引流", "私信",
    "免费领", "限时", "优惠", "打卡", "社群", "星球",
    "知识付费", "训练营", "体验课", "试听", "咨询",
    "代面", "包过", "保offer", "内推费",
]

# 纯情绪帖/无实质内容的模式
LOW_VALUE_PATTERNS = [
    r"^(哭了|崩溃|emo|无语|裂开|寄了|凉了|g了)$",
    r"^.{0,10}$",  # 标题太短
]


def is_spam(post: dict) -> str | None:
    """检查是否为广告/引流帖。返回原因或 None。"""
    title = post.get("title", "").lower()
    snippet = post.get("snippet", "").lower()
    text = title + " " + snippet

    for kw in SPAM_KEYWORDS:
        if kw in text:
            return f"广告引流关键词: {kw}"

    for pattern in LOW_VALUE_PATTERNS:
        if re.match(pattern, title, re.IGNORECASE):
            return f"低价值内容: {title[:20]}"

    return None


def normalize_title(title: str) -> str:
    """标准化标题用于去重比较。"""
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title.lower()


def title_similarity(a: str, b: str) -> float:
    """计算两个标题的相似度。"""
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def deduplicate(posts: list, threshold: float = 0.75) -> tuple[list, list]:
    """去重。返回 (保留的, 被去重的)。"""
    # 先按 id 去重
    seen_ids = set()
    unique = []
    id_dupes = []
    for p in posts:
        pid = p.get("id", "")
        if pid in seen_ids:
            id_dupes.append({"id": pid, "title": p.get("title", ""), "reason": "ID 重复"})
            continue
        seen_ids.add(pid)
        unique.append(p)

    # 再按标题相似度去重
    result = []
    title_dupes = []
    for post in unique:
        title = post.get("title", "")
        is_dup = False
        for existing in result:
            sim = title_similarity(title, existing.get("title", ""))
            if sim > threshold:
                # 保留点赞数更高的
                if post.get("likes", 0) > existing.get("likes", 0):
                    title_dupes.append({
                        "id": existing.get("id"), "title": existing.get("title"),
                        "reason": f"标题相似({sim:.0%})，保留点赞更高的版本"
                    })
                    result.remove(existing)
                    result.append(post)
                else:
                    title_dupes.append({
                        "id": post.get("id"), "title": title,
                        "reason": f"标题相似({sim:.0%})，已有点赞更高的版本"
                    })
                is_dup = True
                break
        if not is_dup:
            result.append(post)

    return result, id_dupes + title_dupes


def has_interview_signals(post: dict) -> bool:
    """检查帖子是否包含面经信号。"""
    signals = ["面经", "面试", "一面", "二面", "三面", "笔试", "面试题", "面试官",
               "offer", "挂了", "过了", "hr面", "技术面", "面试复盘"]
    text = (post.get("title", "") + " " + post.get("snippet", "")).lower()
    return any(s in text for s in signals)


def score_post(post: dict) -> float:
    """给帖子打分，用于排序。"""
    score = 0.0
    score += min(post.get("likes", 0) / 100, 10)  # 点赞，最多 10 分
    if has_interview_signals(post):
        score += 5
    # 包含公司名加分
    companies = ["字节", "腾讯", "阿里", "百度", "美团", "快手", "小米", "京东",
                 "华为", "蚂蚁", "淘天", "拼多多", "网易", "滴滴", "openai", "anthropic"]
    text = post.get("title", "").lower()
    if any(c in text for c in companies):
        score += 3
    return score


def process(raw_posts: list, min_likes: int = 0) -> dict:
    """主处理流程：过滤 → 去重 → 评分排序。"""
    filtered_reasons = []

    # 1. 过滤广告/引流
    clean = []
    for p in raw_posts:
        reason = is_spam(p)
        if reason:
            filtered_reasons.append({"id": p.get("id"), "title": p.get("title"), "reason": reason})
        else:
            clean.append(p)
    spam_count = len(raw_posts) - len(clean)

    # 2. 过滤低点赞
    if min_likes > 0:
        before = len(clean)
        low_likes = [p for p in clean if p.get("likes", 0) < min_likes]
        clean = [p for p in clean if p.get("likes", 0) >= min_likes]
        for p in low_likes:
            filtered_reasons.append({
                "id": p.get("id"), "title": p.get("title"),
                "reason": f"点赞数 {p.get('likes', 0)} < {min_likes}"
            })

    # 3. 去重
    deduped, dedup_reasons = deduplicate(clean)
    filtered_reasons.extend(dedup_reasons)

    # 4. 评分排序
    deduped.sort(key=lambda p: score_post(p), reverse=True)

    return {
        "stats": {
            "total_raw": len(raw_posts),
            "filtered_spam": spam_count,
            "filtered_dedup": len(dedup_reasons),
            "filtered_low_likes": len(raw_posts) - spam_count - len(clean) if min_likes > 0 else 0,
            "final": len(deduped),
        },
        "filtered_reasons": filtered_reasons,
        "posts": deduped,
    }


def main():
    parser = argparse.ArgumentParser(description="搜索结果过滤与去重")
    parser.add_argument("--input", "-i", required=True, help="输入 JSON 文件（搜索结果数组）")
    parser.add_argument("--output", "-o", default="-", help="输出 JSON 文件（默认 stdout）")
    parser.add_argument("--min-likes", type=int, default=0, help="最低点赞数过滤（默认 0 不过滤）")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        raw = json.load(f)

    # 支持直接传数组或 {"results": [...]} 格式
    if isinstance(raw, dict) and "results" in raw:
        raw = raw["results"]

    result = process(raw, min_likes=args.min_likes)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output == "-":
        print(output)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)

    # 打印统计到 stderr
    s = result["stats"]
    print(f"\n📊 过滤统计：", file=sys.stderr)
    print(f"   原始: {s['total_raw']} 条", file=sys.stderr)
    print(f"   广告/引流: -{s['filtered_spam']} 条", file=sys.stderr)
    print(f"   去重: -{s['filtered_dedup']} 条", file=sys.stderr)
    if s.get("filtered_low_likes"):
        print(f"   低点赞: -{s['filtered_low_likes']} 条", file=sys.stderr)
    print(f"   最终保留: {s['final']} 条", file=sys.stderr)


if __name__ == "__main__":
    main()
