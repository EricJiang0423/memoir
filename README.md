# memoir

> **Your travel photos, turned into a keepsake. Not an album — a memoir.**

You came back with 2,000 photos. They're buried in your camera roll between screenshots of boarding passes and yesterday's meme. You meant to do something with them. Six months later, they're still there.

memoir doesn't organize your photos. It writes a story from them: a single, self-contained HTML page with a title, chapters, prose that reads like an essay, and curated photos that earned their place. Double-click to open. No server, no setup, no "make sure you also copy the assets folder."

---

## What you get

| | |
|---|---|
| **Hero cover** | Full-bleed photo + poetic title + date range |
| **Narrative chapters** | 150-250 words per day, written by Claude — sensory details, not "today we visited the beautiful..." |
| **Curated photos** | 2,000 in, 40-60 out. Blurry shots, screenshots, duplicates, accidental pocket photos — all removed |
| **GPS map** | Leaflet-powered track with place markers (OpenStreetMap tiles) |
| **Lightbox** | Click any photo to zoom; ← → Esc keyboard navigation |
| **Self-contained** | Single HTML file, photos embedded as base64. Drag it anywhere — it just works |

---

## How it works

memoir is a **Claude Code skill** — an AI agent reads instruction files and drives a Python pipeline. You talk to it in natural language.

```
Photos.app / folder
      ↓
  EXIF extraction (time + GPS)
      ↓
  Apple Photos AI scoring (aesthetic quality, screenshots, persons)
      ↓
  Smart prefilter — rank by Apple score + GPS diversity,
  download only the best ~5% of cloud photos
      ↓
  Reverse geocoding (OpenStreetMap Nominatim)
      ↓
  Date + GPS clustering
      ↓
  Quality pre-check (blur, exposure, duplicate, burst detection)
      ↓
  Claude writes narrative + designs HTML live (no template, every time different)
      ↓
  Post-processing (base64 embedding, Leaflet injection, self-containment verification)
      ↓
  Self-contained HTML → double-click to open
```

## Design philosophy

### Curation over coverage

The default is to delete most of your photos. A memoir with 15 strong images outweighs an album dump with 200 weak ones. Blurry, screenshots, duplicates, feet, accidental shutter — gone. Final keep rate: 10-30%.

### NEVER converge

There is no HTML template. Claude designs the page from scratch every time — fonts, colors, layout, rhythm — matched to the trip's character. A Renaissance Italy trip reads like a heritage art book; a neon Tokyo night reads like an editorial magazine. This is enforced design discipline, not a feature toggle.

### Privacy by architecture

Photo bytes never leave your machine. The only data sent out is GPS coordinates (two-decimal precision) to OpenStreetMap Nominatim for reverse geocoding. EXIF parsing, image resizing, clustering, base64 encoding, and Claude's multimodal vision all happen locally.

### Self-contained by default

The deliverable is one HTML file. No server, no external JS, no assets directory, no instructions. AirDrop it, put it on a USB stick, host it anywhere — it opens.

### Apple Photos native intelligence

When using Photos.app mode, memoir taps directly into Apple's on-device ML scores: 27-dimension aesthetic ratings, screenshot detection, favorites, hidden flags, and named persons. These feed into smart prefiltering — before a single cloud photo is downloaded, memoir already knows which ones are worth keeping.

---

## Quick start

### Prerequisites (macOS only)

```bash
brew install exiftool libheif
pip install -r requirements.txt
```

### Verify

```bash
python3 scripts/check_deps.py
```

### Use in Claude Code

Drop the `memoir/` directory into your skills path, then say any of:

> 「整理我上次旅行的照片」
> 「把这周的相册做成旅行日记」
> "Make a travel diary from my recent photos"

Claude loads the skill and drives the entire pipeline — from asking where your photos are to handing you the HTML.

### Or run manually

```bash
python3 scripts/extract_photos.py --date-range 2024-03-01 2024-03-07 --out raw_photos.json
python3 scripts/prefilter.py --in raw_photos.json --out download_list.json
# ... download selected photos via AppleScript (see references/osxphotos-tips.md) ...
python3 scripts/geocode.py --in raw_photos.json --out geocoded_photos.json
python3 scripts/cluster.py --in geocoded_photos.json --out diary_data.json
python3 scripts/curate.py --in diary_data.json --out curation_manifest.json
# ... Claude writes narrative + designs HTML ...
python3 scripts/build_diary.py --in diary_data.json --html draft.html --out final.html
```

---

## Pipeline scripts

| Script | Role |
|--------|------|
| `check_deps.py` | Verify system/Python dependencies, output JSON |
| `extract_photos.py` | EXIF extraction (folder via exiftool, Photos.app via osxphotos + Apple scores) |
| `prefilter.py` | Rank cloud-only photos by Apple aesthetic score + GPS diversity; select top N per location |
| `geocode.py` | Reverse geocode GPS → place names (Nominatim, 1 req/s, disk-cached) |
| `cluster.py` | Group by date + GPS distance (500m same / 2km new location) |
| `curate.py` | Quality metrics (Apple scores or Laplacian fallback) + duplicate/burst detection + contact sheet |
| `build_diary.py` | Token post-processor: `trip-design://photo_NNNN` → base64, Leaflet inline, JSON injection, self-containment verification |

---

## Project structure

```
memoir/
├── SKILL.md                    ← Agent control document (the core)
├── README.md                   ← This file
├── PRD.md                      ← Product requirements
├── requirements.txt
├── scripts/                    ← 7 Python pipeline scripts
├── references/                 ← 11 deep-dive reference docs
└── demos/                      ← Demo output + Codex prompt
```

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Platform | macOS (osxphotos constraint) |
| Agent | Claude Code / Codex / Cursor |
| EXIF | exiftool + PyExifTool + osxphotos |
| Image processing | Pillow + pillow-heif + OpenCV |
| Quality metrics | Apple Photos ML scores (primary) + Laplacian variance (fallback) |
| Dedup | perceptual hash (imagehash) + Hamming distance |
| Geocoding | geopy + Nominatim (OpenStreetMap, free) |
| Map | Leaflet 1.9.4 (inlined) + OSM tiles |
| Output | Single-file HTML, base64-embedded photos |

---

## Design credits

memoir's design philosophy draws from two upstream projects:

- **[huashu-design](https://github.com/alchaincyf/huashu-design/)** — "HTML is a tool, not the medium"; Position Four Questions; Junior Designer Mode; anti-AI-slop checklist
- **[Claude Code frontend-design skill](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design/skills/frontend-design)** — "NEVER converge on common choices"; BOLD aesthetic execution

## License

MIT
