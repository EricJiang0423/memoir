# demos/

放置示例 `.diary.html` 文件，便于潜在用户在不真正跑流水线的情况下预览 memoir 的输出风格。

## 在线预览

- **京都三日，坂道与黄昏** —— https://ericjiang0423.github.io/memoir/
  （GitHub Pages 由 `main` 分支根目录提供；根目录 `index.html` 是个落地页，点进去就是这份 demo）

## 当前 demo

| 文件 | 说明 |
|------|------|
| `kyoto-3-days.diary.html` | 3 天京都行（2026-03），30 张照片里精选 23 张；单文件、完全自包含（照片 base64 内嵌、Leaflet inline），约 22 MB，双击浏览器即可打开 |
| `photos/kyoto/` | 上面这份 demo 的输入照片（30 张，全部由 **OpenAI GPT Image 2.0** 生成的合成图——非真实照片，可公开；详见该目录下的 `README.md`） |

> 这些京都照片全部由 GPT Image 2.0 生成（合成图，不对应真实拍摄、不涉及真实人物 / 隐私）——这也是为什么可以放进公开仓库。**真实旅行照片（含家人、住址、行程的）不要放进 demos/。**

## 复现这份 demo

```bash
python3 scripts/check_deps.py
python3 scripts/extract_photos.py --folder demos/photos/kyoto --out raw_photos.json
python3 scripts/geocode.py        --in  raw_photos.json      --out geocoded_photos.json
python3 scripts/cluster.py        --in  geocoded_photos.json --out diary_data.json
# Claude 在这里做：多模态策展（剔弱图/重复图）→ 回填 diary_data.json 的 title / narrative / caption
#                  → 现场设计一份带 token 占位的 HTML
python3 scripts/build_diary.py    --in  diary_data.json      --html output/kyoto.diary.draft.html \
                                  --out output/kyoto.diary.html
```

`build_diary.py` 只做 token 后处理（base64 / Leaflet 注入 / JSON 数据注入 / 缩放 / 自包含校验）；旅行标题、每日叙述、照片 caption、HTML 设计都由 Claude 现场产出——所以每次复现的文字和视觉都会不一样（这是 skill 的设计：NEVER converge）。

## 命名约定

```
demos/
├── README.md
├── kyoto-3-days.diary.html         ← 当前 demo（~22 MB，自包含）
└── photos/kyoto/                   ← demo 输入照片（AI 生成）
```

新增 demo 建议控制体积；体积大的可以用 `python3 scripts/build_diary.py ... --embed-photos relative`（HTML ~1 MB + 同名 `.assets/` 照片目录），或放外部（Gist / Pages）再用 link 在此引用。
