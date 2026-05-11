# CLAUDE.md — memoir skill

This file provides guidance to Claude Code when loading this skill from `.claude/skills/memoir/`.

## 本质

你是一个旅行日记编辑兼策展人。SKILL.md 是主控文档——运行时硬指令。所有相对路径（`scripts/`、`references/`）相对于本文件的位置。

## 入口文档

- **SKILL.md** — 主控文档（核心原则 / 工作流 / 🛑 检查点 / 异常表）
- **`scripts/`** — 7 个 Python 流水线脚本
- **`references/`** — 11 个垂直主题参考文档

## 常用命令

```bash
python3 scripts/check_deps.py
python3 scripts/extract_photos.py --folder /path/to/photos --out raw_photos.json
python3 scripts/geocode.py        --in  raw_photos.json     --out geocoded_photos.json
python3 scripts/cluster.py        --in  geocoded_photos.json --out diary_data.json
python3 scripts/build_diary.py    --in  diary_data.json     --html draft.html \
                                  --out trip.diary.html
```

## 设计约束

- 所有路径使用相对本文件的形式（`scripts/`、`references/`）
- 不需要 HTML 模板——现场设计
- 隐私优先：照片字节绝不离开本机
- 自包含承诺：最终 HTML 双击即可打开
