#!/usr/bin/env python3
"""Pre-filter cloud-only Photos.app photos using Apple scores + GPS diversity.

Before downloading thousands of iCloud photos, use metadata already available
in Photos.sqlite (Apple aesthetic scores, GPS, screenshot flag, favorites)
to select only the best candidates. Outputs a UUID list for targeted download.

Usage:
    python3 scripts/prefilter.py --in raw_photos.json --out download_list.json
    python3 scripts/prefilter.py --in raw_photos.json --out download_list.json --top 8
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

# Default: how many photos to keep per GPS-diverse location per day
TOP_PER_GROUP = 5
# Minimum Apple aesthetic score to consider (skip obvious junk)
MIN_APPLE_SCORE = 0.15
# GPS bucket precision (~1km at mid-latitudes)
GPS_BUCKET_DECIMALS = 2


def prefilter(photos: list[dict], top_per_group: int = TOP_PER_GROUP,
              persons_filter: list[str] | None = None,
              persons_boost: float = 0.3) -> dict:
    """Group by date + rough GPS, rank by Apple score, select top N per group.

    Args:
        photos: raw_photos.json records (must have apple_score + persons fields)
        top_per_group: max photos to keep per GPS-diverse location per day
        persons_filter: if set, only keep photos containing these person names
        persons_boost: extra score boost for photos matching persons_filter

    Returns: {"selected_uuids": [...], "stats": {...}}
    """
    by_day_gps: dict[tuple[str, str], list[dict]] = defaultdict(list)
    all_persons: dict[str, int] = defaultdict(int)  # person name → total count

    for p in photos:
        date = (p.get("datetime") or "")[:10]
        if not date:
            continue

        apple = p.get("apple_score") or {}
        gps = p.get("gps") or {}
        lat = gps.get("lat")
        lon = gps.get("lon")
        gps_key = f"{round(lat, GPS_BUCKET_DECIMALS)},{round(lon, GPS_BUCKET_DECIMALS)}" if lat else "no_gps"

        apple_overall = apple.get("overall", 0)
        is_screenshot = p.get("is_screenshot", False)
        is_favorite = p.get("is_favorite", False)
        is_hidden = p.get("is_hidden", False)
        p_persons = p.get("persons", [])
        persons_count = len(p_persons)

        for name in p_persons:
            if name and name != "_UNKNOWN_":
                all_persons[name] += 1

        # Check persons filter
        if persons_filter:
            has_target = any(t in p_persons for t in persons_filter)
            if not has_target:
                continue  # skip photos without target persons

        by_day_gps[(date, gps_key)].append({
            "uuid": p["path"].replace("<icloud:", "").replace(">", ""),
            "apple_score": apple_overall,
            "is_screenshot": is_screenshot,
            "is_favorite": is_favorite,
            "is_hidden": is_hidden,
            "persons_count": persons_count,
            "persons": p_persons,
        })

    selected = []
    stats = {"total": len(photos), "groups": len(by_day_gps),
             "screenshots_skipped": 0, "low_score_skipped": 0,
             "hidden_skipped": 0, "persons_filtered_out": 0,
             "selected": 0, "top_persons": dict(
                 sorted(all_persons.items(), key=lambda x: x[1], reverse=True)[:20])}

    if persons_filter:
        stats["persons_filter"] = persons_filter

    for (day, gps_key), pics in sorted(by_day_gps.items()):
        # Compute final score: Apple overall + user signals + persons boost
        for pic in pics:
            boost = 0.0
            if pic["is_favorite"]:
                boost += 0.3
            if pic["is_screenshot"]:
                boost -= 1.0
            if pic["is_hidden"]:
                boost -= 0.5
            if persons_filter:
                matched = sum(1 for t in persons_filter if t in pic["persons"])
                boost += matched * persons_boost
            boost += pic["persons_count"] * 0.03
            pic["_final_score"] = pic["apple_score"] + boost

        pics.sort(key=lambda x: x["_final_score"], reverse=True)

        taken = 0
        for pic in pics:
            if pic["is_screenshot"]:
                stats["screenshots_skipped"] += 1
                continue
            if pic["is_hidden"] and not pic["is_favorite"]:
                stats["hidden_skipped"] += 1
                continue
            if pic["apple_score"] < MIN_APPLE_SCORE and not pic["is_favorite"]:
                stats["low_score_skipped"] += 1
                continue

            selected.append(pic["uuid"])
            taken += 1
            if taken >= top_per_group:
                break

    if persons_filter:
        # Count how many of the selected photos match each filter person
        person_match_counts = {name: 0 for name in persons_filter}
        for uid in selected:
            for pic_list in by_day_gps.values():
                for pic in pic_list:
                    if pic["uuid"] == uid:
                        for name in persons_filter:
                            if name in pic["persons"]:
                                person_match_counts[name] += 1
        stats["person_match_counts"] = person_match_counts

    stats["selected"] = len(selected)
    return {"selected_uuids": selected, "stats": stats}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp", type=Path, default=Path("raw_photos.json"),
                    help="extract_photos.py 输出（必须含 apple_score 字段，即 Photos.app 模式）")
    ap.add_argument("--out", type=Path, default=Path("download_list.json"))
    ap.add_argument("--top", type=int, default=TOP_PER_GROUP,
                    help=f"每日期+GPS组内保留的最大照片数（默认 {TOP_PER_GROUP}）")
    ap.add_argument("--min-score", type=float, default=MIN_APPLE_SCORE,
                    help=f"最低 Apple 美学评分阈值（默认 {MIN_APPLE_SCORE}）")
    ap.add_argument("--persons", type=str, default=None,
                    help="只保留包含这些人的照片（逗号分隔），如 '张三,李四'")
    ap.add_argument("--persons-boost", type=float, default=0.3,
                    help="匹配人物时的额外加分（默认 0.3）")
    ap.add_argument("--list-persons", action="store_true",
                    help="只列出照片中出现的人物及频次，不做筛选")
    args = ap.parse_args()

    if not args.inp.exists():
        sys.exit(f"找不到输入：{args.inp}（先跑 extract_photos.py --date-range ...）")

    photos = json.loads(args.inp.read_text(encoding="utf-8"))

    has_apple = sum(1 for p in photos if p.get("apple_score"))
    if has_apple == 0:
        sys.exit(
            "raw_photos.json 里没有 apple_score 字段。\n"
            "prefilter.py 需要 Photos.app 模式（非 --folder 模式）的元数据，\n"
            "因为只有 Photos.sqlite 里才有 Apple 美学评分。\n"
            "请重新运行：python3 scripts/extract_photos.py --date-range ..."
        )

    # --list-persons mode: just show person stats, no filtering
    if args.list_persons:
        all_persons: dict[str, int] = defaultdict(int)
        for p in photos:
            for name in p.get("persons", []):
                if name and name != "_UNKNOWN_":
                    all_persons[name] += 1
        top = sorted(all_persons.items(), key=lambda x: x[1], reverse=True)[:30]
        print("👥 照片中出现的人物（按频次）：")
        for name, count in top:
            print(f"   {name}: {count} 次")
        if not top:
            print("   （未检测到已命名的人物）")
        return

    persons_filter = None
    if args.persons:
        persons_filter = [n.strip() for n in args.persons.split(",") if n.strip()]

    result = prefilter(photos, top_per_group=args.top,
                       persons_filter=persons_filter,
                       persons_boost=args.persons_boost)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    s = result["stats"]
    print(
        f"🎯 预筛选完成：{s['total']} → {s['selected']} 张（{100*s['selected']//max(s['total'],1)}%）\n"
        f"   GPS 分组：{s['groups']} 组\n"
        f"   跳过截图：{s['screenshots_skipped']} 张\n"
        f"   跳过低分：{s['low_score_skipped']} 张\n"
        f"   跳过隐藏：{s['hidden_skipped']} 张"
    )
    if persons_filter:
        print(f"   人物筛选：{', '.join(persons_filter)}")
        mc = s.get("person_match_counts", {})
        for name, count in mc.items():
            print(f"     {name}: {count} 张入选")
    if s.get("top_persons"):
        top = list(s["top_persons"].items())[:5]
        print(f"   最常出现：{', '.join(f'{n}({c})' for n, c in top)}")
    print(f"\n→ {args.out}")


if __name__ == "__main__":
    main()
