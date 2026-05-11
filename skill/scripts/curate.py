#!/usr/bin/env python3
"""Pre-curation quality analysis: blur, screenshot, exposure, duplicate/burst detection.

Generates curation_manifest.json (machine recommendations) and an optional
visual contact sheet (thumbnail grid with metadata overlays) that Claude reads
in ONE multimodal call instead of reading every photo individually.

Usage:
    python3 scripts/curate.py --in diary_data.json --out curation_manifest.json
    python3 scripts/curate.py --in diary_data.json --out curation_manifest.json \
                              --contact-sheet output/contact_sheet.jpg
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

THUMB_SIZE = 200
GRID_COLS = 6
BLUR_THRESHOLD = 100.0
EXPOSURE_CLIP_PCT = 0.05
PHASH_HAMMING_DEDUP = 10


def compute_blur_score(img_array: np.ndarray) -> float:
    """Laplacian variance — higher = sharper. < BLUR_THRESHOLD is likely blurry."""
    import cv2
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    return float(lap.var())


def compute_exposure(img_array: np.ndarray) -> dict[str, Any]:
    """Histogram analysis for clipped highlights / crushed blacks."""
    import cv2
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    total = gray.size
    clipped_high = float((gray >= 250).sum()) / total
    clipped_low = float((gray <= 5).sum()) / total
    return {
        "clipped_high_pct": round(clipped_high, 4),
        "clipped_low_pct": round(clipped_low, 4),
        "is_overexposed": clipped_high > EXPOSURE_CLIP_PCT,
        "is_underexposed": clipped_low > EXPOSURE_CLIP_PCT,
    }


def compute_phash(img_array: np.ndarray) -> str:
    """Perceptual hash for duplicate/burst detection."""
    import imagehash
    from PIL import Image
    pil_img = Image.fromarray(img_array)
    return str(imagehash.phash(pil_img))


def hamming_distance(h1: str, h2: str) -> int:
    """Hamming distance between two hex-string pHashes."""
    try:
        i1 = int(h1, 16)
        i2 = int(h2, 16)
    except ValueError:
        return 999
    return (i1 ^ i2).bit_count()


def is_screenshot(photo: dict, img_array: np.ndarray | None = None) -> bool:
    """Detect screenshots via EXIF Software tag or aspect-ratio heuristic."""
    # Check EXIF Software tag via PIL
    try:
        from PIL import Image
        img = Image.open(photo["path"])
        exif = img.getexif()
        software = exif.get(0x0131, "")
        if software and "screenshot" in str(software).lower():
            return True
    except Exception:
        pass

    if img_array is not None:
        h, w = img_array.shape[:2]
        # Phone screenshot aspect ratios: ~9:19.5, ~9:16
        ratio = max(w, h) / max(min(w, h), 1)
        if 1.7 < ratio < 2.3:
            return False
        if ratio >= 2.1:
            return True

    return False


def load_image(path: str) -> np.ndarray | None:
    """Load image as RGB numpy array. Returns None on failure."""
    import cv2
    try:
        img = cv2.imread(path)
        if img is None:
            try:
                from PIL import Image
                pil = Image.open(path).convert("RGB")
                return np.array(pil)
            except Exception:
                return None
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    except Exception:
        return None


def generate_contact_sheet(photos: list[dict], manifest: dict,
                           out_path: Path, thumb_size: int = THUMB_SIZE) -> None:
    """Generate a single JPEG grid of thumbnails with metadata overlays."""
    import cv2

    valid_ids = [p["id"] for p in photos if p.get("_img") is not None]
    if not valid_ids:
        print("⚠ 没有可用的照片生成 contact sheet", file=sys.stderr)
        return

    cols = min(GRID_COLS, len(valid_ids))
    rows = (len(valid_ids) + cols - 1) // cols

    canvas_w = cols * (thumb_size + 4) + 4
    canvas_h = rows * (thumb_size + 28) + 4
    canvas = np.full((canvas_h, canvas_w, 3), 240, dtype=np.uint8)

    # Build a quick lookup: photo id → machine recommendation
    recommendation = {}
    for p in manifest["photos"]:
        recommendation[p["id"]] = p.get("machine_recommendation", "keep")

    for idx, pid in enumerate(valid_ids):
        row, col = divmod(idx, cols)
        x = 4 + col * (thumb_size + 4)
        y = 4 + row * (thumb_size + 28)

        photo = next(p for p in photos if p["id"] == pid)
        img = photo["_img"]

        # Resize thumbnail
        h, w = img.shape[:2]
        scale = thumb_size / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        thumb = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Center in cell
        ox = x + (thumb_size - new_w) // 2
        oy = y + (thumb_size - new_h) // 2
        canvas[oy:oy + new_h, ox:ox + new_w] = thumb

        # Color-coded border: green=keep, yellow=maybe, red=reject/skip
        rec = recommendation.get(pid, "keep")
        if rec.startswith("reject") or rec == "skip_unavailable":
            border_color = (0, 0, 255)
        elif rec == "maybe":
            border_color = (0, 215, 255)
        else:
            border_color = (0, 180, 0)

        cv2.rectangle(canvas, (x, y), (x + thumb_size, y + thumb_size),
                      border_color, 2)

        # ID label below thumbnail
        label_y = y + thumb_size + 16
        cv2.putText(canvas, f"#{pid.split('_')[1]}", (x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (50, 50, 50), 1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), canvas)
    print(f"📋 Contact sheet → {out_path} ({len(valid_ids)} photos)", file=sys.stderr)


def curate(manifest: list[dict]) -> tuple[list[dict], dict[str, Any]]:
    """Run all quality checks. Return (per_photo_results, summary)."""
    results = []
    duplicate_groups: dict[str, list[str]] = {}
    burst_groups: dict[str, list[str]] = {}
    summary = {
        "blurry_count": 0,
        "screenshot_count": 0,
        "overexposed_count": 0,
        "underexposed_count": 0,
        "duplicate_groups_count": 0,
        "burst_groups_count": 0,
        "unavailable_count": 0,
    }

    # Phase 1: per-photo metrics
    for photo in manifest:
        pid = photo["id"]
        apple = photo.get("apple_score")
        is_screenshot_apple = photo.get("is_screenshot", False)
        is_favorite = photo.get("is_favorite", False)
        is_hidden = photo.get("is_hidden", False)
        persons = photo.get("persons", [])

        # Load image for contact sheet and fallback CV analysis
        img = load_image(photo["path"])
        photo["_img"] = img

        if img is None:
            results.append({
                "id": pid, "path": photo["path"],
                "machine_recommendation": "skip_unavailable",
                "apple_score": apple,
                "is_screenshot": is_screenshot_apple,
                "is_favorite": is_favorite,
                "is_hidden": is_hidden,
                "persons": persons,
                "persons_count": len(persons),
                "error": "file_not_found_or_decode",
            })
            summary["unavailable_count"] += 1
            continue

        # ── Quality scoring ──
        blur = compute_blur_score(img)
        exposure = compute_exposure(img)
        phash = compute_phash(img)
        screenshot_cv = is_screenshot(photo, img)
        screenshot = is_screenshot_apple or screenshot_cv

        rec = "keep"
        quality_score = 0.0

        if apple:
            # Primary: Apple's ML scores (end-to-end trained, vastly better than CV heuristics)
            quality_score = (
                apple["overall"] * 0.30 +
                apple["pleasant_composition"] * 0.15 +
                apple["sharply_focused_subject"] * 0.15 +
                apple["well_framed_subject"] * 0.10 +
                apple["well_timed_shot"] * 0.05 +
                apple["interesting_subject"] * 0.10 +
                apple["pleasant_lighting"] * 0.05 +
                apple["harmonious_color"] * 0.05 -
                apple["noise"] * 0.03 -
                apple["failure"] * 0.02
            )

            # Screenshot takes priority (Apple-native detection)
            if screenshot:
                rec = "reject_screenshot"
                summary["screenshot_count"] += 1
            elif apple["failure"] > 0.5:
                rec = "reject_blurry"
                summary["blurry_count"] += 1
            elif apple["overall"] < 0.3:
                rec = "maybe_low_quality"
                summary["overexposed_count"] += 1
            else:
                rec = "keep"

        else:
            # Fallback: classical CV heuristics (folder mode, no Photos DB)
            quality_score = blur / 500.0  # normalize Laplacian variance
            if blur < BLUR_THRESHOLD:
                rec = "reject_blurry"
                summary["blurry_count"] += 1
            elif screenshot:
                rec = "reject_screenshot"
                summary["screenshot_count"] += 1
            elif exposure["is_overexposed"]:
                rec = "maybe_overexposed"
                summary["overexposed_count"] += 1
            elif exposure["is_underexposed"]:
                rec = "maybe_underexposed"
                summary["underexposed_count"] += 1

        # Boost/demote based on user signals
        if is_favorite:
            quality_score += 0.3
            rec = "keep"  # user favorited → never auto-reject
        if is_hidden:
            quality_score -= 0.5
            if rec == "keep":
                rec = "maybe_hidden"

        # Social value: photos with people get a slight boost
        social_bonus = min(len(persons) * 0.02, 0.1)

        results.append({
            "id": pid,
            "path": photo["path"],
            "blur_score": round(blur, 2),
            "is_blurry": blur < BLUR_THRESHOLD,
            "is_screenshot": screenshot,
            "exposure_score": exposure,
            "phash": phash,
            "duplicate_group": None,
            "burst_group_id": None,
            "machine_recommendation": rec,
            "quality_score": round(quality_score + social_bonus, 4),
            "apple_score": apple,
            "is_favorite": is_favorite,
            "is_hidden": is_hidden,
            "persons": persons,
            "persons_count": len(persons),
            "error": None,
        })

    # Phase 2: duplicate/burst detection
    by_minute: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        if r.get("error"):
            continue
        dt_str = next((p.get("datetime", "") for p in manifest
                       if p["id"] == r["id"]), "")
        minute_bucket = dt_str[:16] if dt_str else "unknown"
        by_minute[minute_bucket].append(r)

    burst_gid = 1
    dup_gid = 1
    for minute, group in by_minute.items():
        if len(group) < 2:
            continue
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                if group[i].get("phash") and group[j].get("phash"):
                    dist = hamming_distance(group[i]["phash"], group[j]["phash"])
                    if dist < PHASH_HAMMING_DEDUP:
                        group[i]["duplicate_group"] = dup_gid
                        group[j]["duplicate_group"] = dup_gid
                        duplicate_groups.setdefault(str(dup_gid), []).extend(
                            [group[i]["id"], group[j]["id"]])
                        dup_gid += 1
                    elif dist < 20:
                        group[i]["burst_group_id"] = burst_gid
                        group[j]["burst_group_id"] = burst_gid
                        burst_groups.setdefault(str(burst_gid), []).extend(
                            [group[i]["id"], group[j]["id"]])
                        burst_gid += 1

    # Deduplicate group lists
    for gid in duplicate_groups:
        duplicate_groups[gid] = list(set(duplicate_groups[gid]))
    for gid in burst_groups:
        burst_groups[gid] = list(set(burst_groups[gid]))

    summary["duplicate_groups_count"] = len(duplicate_groups)
    summary["burst_groups_count"] = len(burst_groups)

    return results, summary, duplicate_groups, burst_groups


def collect_photos(diary: dict) -> list[dict]:
    """Flatten diary_data.json days→locations→photos into a flat list."""
    photos = []
    for day in diary.get("days", []):
        for loc in day.get("locations", []):
            for p in loc.get("photos", []):
                photos.append(p)
    return photos


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", type=Path, default=Path("diary_data.json"),
                    help="cluster.py 输出")
    ap.add_argument("--out", type=Path, default=Path("curation_manifest.json"))
    ap.add_argument("--contact-sheet", type=Path, default=None,
                    help="生成视觉 contact sheet 的路径（如 output/contact_sheet.jpg）")
    ap.add_argument("--thumb-size", type=int, default=THUMB_SIZE,
                    help=f"Contact sheet 缩略图尺寸（默认 {THUMB_SIZE}px）")
    ap.add_argument("--grid-cols", type=int, default=GRID_COLS,
                    help=f"Contact sheet 每行列数（默认 {GRID_COLS}）")
    args = ap.parse_args()

    if not args.inp.exists():
        sys.exit(f"找不到输入：{args.inp}（先跑 cluster.py）")

    diary = json.loads(args.inp.read_text(encoding="utf-8"))
    photos = collect_photos(diary)

    if not photos:
        sys.exit("diary_data.json 里没有照片——先跑 cluster.py")

    results, summary, dup_groups, burst_groups = curate(photos)

    manifest = {
        "version": 1,
        "generated_at": datetime.now().isoformat(),
        "photo_count": len(photos),
        "photos": results,
        "duplicate_groups": dup_groups,
        "burst_groups": burst_groups,
        "summary": summary,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(json.dumps({
        "out": str(args.out),
        "summary": summary,
    }, ensure_ascii=False, indent=2))

    if args.contact_sheet:
        generate_contact_sheet(photos, manifest, args.contact_sheet,
                              thumb_size=args.thumb_size)


if __name__ == "__main__":
    main()
