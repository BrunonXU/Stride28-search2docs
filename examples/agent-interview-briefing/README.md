# 示例：Agent 面经整理

本目录包含一个完整的面经整理示例。

## 文件说明

- `input.json` — 结构化面经数据（模拟搜索结果经过筛选去重后的数据）
- `output.mdx` — 由 `generate_mdx.py` 生成的 MDX 输出

## 生成 output.mdx

```bash
python scripts/generate_mdx.py --input examples/agent-interview-briefing/input.json --output examples/agent-interview-briefing/output.mdx
```
