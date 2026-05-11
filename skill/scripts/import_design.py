#!/usr/bin/env python3
"""Import, validate, and register a new design direction.

Usage:
  # From local file
  python3 import_design.py path/to/my-design.md

  # From GitHub raw URL
  python3 import_design.py https://raw.githubusercontent.com/user/repo/main/designs/my-design.md

  # List registered designs
  python3 import_design.py --list

The design.md must follow the TEMPLATE.md format and include YAML frontmatter
at the end with metadata fields (name, name_en, vibe, layout_type, etc.).

On import, the script:
  1. Downloads/reads the file
  2. Validates required sections exist
  3. Checks for structural uniqueness (layout_type not duplicated)
  4. Copies to designs/<name_en>.md
  5. Updates designs/README.md index table
"""
from __future__ import annotations

import os
import re
import sys
import urllib.request
from pathlib import Path

DESIGNS_DIR = Path(__file__).resolve().parent.parent / "designs"
README_PATH = DESIGNS_DIR / "README.md"

# Design files must mention these concepts somewhere.
# They can be dedicated `## 地图` sections OR inline statements like "没有地图。没有灯箱。"
KEY_CONCEPTS = [
    "气质", "适用场景", "布局", "色彩", "字体",
    "照片", "地图", "灯箱", "严禁",
]

EXISTING_LAYOUT_TYPES = {"spread", "scroll", "grid", "slide", "collage", "single"}


def parse_metadata(content: str) -> dict:
    """Parse YAML-like metadata block at end of file after <!--META--> marker."""
    meta = {}
    m = re.search(r'<!--META-->\s*\n(.+?)(?:\n\n|\n$|\Z)', content, re.DOTALL)
    if not m:
        # fallback: try to find name: / vibe: / layout_type: anywhere
        for key in ("name", "name_en", "vibe", "layout_type", "has_map", "has_lightbox", "has_narrative"):
            vm = re.search(rf'^{key}:\s*(.+)$', content, re.MULTILINE)
            if vm:
                meta[key] = vm.group(1).strip().strip('"\'')
        return meta
    block = m.group(1).strip()
    for line in block.strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip('"\'')
    return meta


def infer_layout_type(content: str) -> str | None:
    """Guess layout_type from content if not in metadata."""
    text = content.lower()
    if "跨页" in text or "对开" in text:
        return "spread"
    if "拼贴" in text or "重叠" in text:
        return "collage"
    if "网格" in text or "接触印相" in text:
        return "grid"
    if "幻灯片" in text or "黑场" in text:
        return "slide"
    if "单张" in text or "独占" in text:
        return "single"
    if "滚" in text or "长卷" in text:
        return "scroll"
    return None


def validate(content: str, source: str) -> list[str]:
    """Return list of validation errors (empty = valid)."""
    errors = []

    # Check required concepts (as section headers OR inline mentions)
    for concept in KEY_CONCEPTS:
        # Look for ## headers, **bold emphasis**, or plain-text mentions
        found = (
            f"## {concept}" in content
            or f"##{concept}" in content
            or f"**{concept}" in content
            or (f" {concept} " in content and concept not in ("照片", "布局"))
        )
        # "照片" is too common as a word; check it's a proper section
        if concept == "照片":
            found = f"## 照片" in content or f"照片处理" in content or f"##照片" in content
        if concept == "布局":
            found = f"## 布局" in content or f"布局 Archetype" in content
        if not found:
            errors.append(f"缺少必要概念: {concept}（应有 ## 章节或文中明确提及）")

    # Check metadata
    meta = parse_metadata(content)
    if "name" not in meta and "name_en" not in meta:
        errors.append("缺少方向名称（name 或 name_en）—— 加在文件末尾 <!--META--> 块中")

    lt = meta.get("layout_type") or infer_layout_type(content)
    if not lt:
        errors.append("无法推断 layout_type——请在元数据中指定，或使用明确的布局关键词")
    else:
        meta["layout_type"] = lt

    # Check structural uniqueness
    lt = meta.get("layout_type", "")
    existing_layouts = get_registered_layouts()
    if lt in existing_layouts:
        names = existing_layouts[lt]
        errors.append(
            f"布局类型 '{lt}' 已被 {names} 使用。"
            f"设计方向必须结构不同——请换一种布局 archetype"
        )

    return errors


def get_registered_layouts() -> dict[str, list[str]]:
    """Scrape designs/README.md for existing layout_type → name mapping."""
    layout_map: dict[str, list[str]] = {}
    if not README_PATH.exists():
        return layout_map
    for line in README_PATH.read_text(encoding="utf-8").split("\n"):
        # Match table rows: | # | [name](file) | vibe | `layout_type` text | best_for
        m = re.match(r'\|\s*\d+\s*\|\s*\[(.+?)\]\(.+?\)\s*\|\s*.+?\s*\|\s*`(.+?)`', line)
        if m:
            name = m.group(1).strip()
            lt = m.group(2).strip().lower()
            layout_map.setdefault(lt, []).append(name)
    return layout_map


def update_index(name: str, name_en: str, vibe: str, layout_type: str,
                 has_map: bool, has_lightbox: bool, has_narrative: bool,
                 meta: dict | None = None) -> None:
    """Insert the new design into README.md index table."""
    if not README_PATH.exists():
        print(f"⚠ {README_PATH} not found — skipping index update")
        return

    content = README_PATH.read_text(encoding="utf-8")

    # Find the table rows and determine next number
    existing = re.findall(r'^\|\s*(\d+)\s*\|', content, re.MULTILINE)
    next_num = max((int(n) for n in existing), default=0) + 1

    # Build new row (5-column: # / name / vibe / `layout` / best_for)
    best_for = (meta or {}).get("best_for", "")
    new_row = (f"| {next_num:02d} | [{name}]({name_en}.md) | "
               f"{vibe} | `{layout_type}` | {best_for} |\n")

    # Insert before the last "---" or the "## 原则" section
    insert_before = "\n## 原则"
    if insert_before in content:
        content = content.replace(insert_before, f"{new_row}{insert_before}", 1)
        README_PATH.write_text(content, encoding="utf-8")
        print(f"  ✓ 已注册到 {README_PATH.name}")
    else:
        print(f"  ⚠ 找不到插入位置，请手动添加：{new_row.strip()}")


def main():
    args = sys.argv[1:]

    if "--list" in args:
        print("已注册的设计方向：")
        lt_map = get_registered_layouts()
        for lt, names in sorted(lt_map.items()):
            print(f"  [{lt}] {', '.join(names)}")
        return

    if not args:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    source = args[0]

    # Read content
    if source.startswith(("http://", "https://")):
        print(f"⬇ 下载 {source} ...")
        req = urllib.request.Request(source, headers={"User-Agent": "memoir-import-design/0.1"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
    else:
        src_path = Path(source)
        if not src_path.exists():
            sys.exit(f"文件不存在: {source}")
        content = src_path.read_text(encoding="utf-8")

    # Validate
    errors = validate(content, source)
    if errors:
        print("❌ 校验失败：")
        for e in errors:
            print(f"  · {e}")
        sys.exit(1)

    # Parse metadata for registration
    meta = parse_metadata(content)
    name = meta.get("name", meta.get("name_en", "unnamed"))
    name_en = meta.get("name_en", name.lower().replace(" ", "-"))
    vibe = meta.get("vibe", "未指定")
    layout_type = meta.get("layout_type") or infer_layout_type(content) or "other"
    has_map = meta.get("has_map", "false").lower() in ("true", "yes", "1")
    has_lightbox = meta.get("has_lightbox", "false").lower() in ("true", "yes", "1")
    has_narrative = meta.get("has_narrative", "true").lower() in ("true", "yes", "1")

    # Write to designs/
    out_path = DESIGNS_DIR / f"{name_en}.md"
    if out_path.exists():
        print(f"  ⚠ {out_path.name} 已存在，将覆盖")
    out_path.write_text(content, encoding="utf-8")
    print(f"  ✓ 已写入: {out_path.name}")

    # Update index
    update_index(name, name_en, vibe, layout_type, has_map, has_lightbox, has_narrative, meta)

    print(f"\n✅ 导入完成。方向 '{name}' 现在可以在设计推荐步骤中被选中。")


if __name__ == "__main__":
    main()
