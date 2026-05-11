# memoir

> **把旅行照片变成一件作品。不是相册——是回忆录。**

你拍了 2000 张照片回来。它们躺在相机胶卷里，和登机牌截图、昨天的表情包混在一起。你说「等有空了整理」——半年过去了。

memoir 不整理照片。它帮你**写一段记忆**：一份双击就能打开的 HTML 网页，有标题、有章节、有散文般的叙述、有策展过的照片。没有服务器，没有「记得把 assets 文件夹也拷过去」。

> 想先看看它生成什么样的东西？在线 demo：[**京都三日，坂道与黄昏**](https://ericjiang0423.github.io/memoir/)（30 张照片 → 23 张精选 + 3 天叙述 + 地图 + 灯箱，单文件自包含 HTML；demo 用图由 OpenAI GPT Image 2.0 生成）

---

## 你能得到什么

| | |
|---|---|
| **封面** | 主图或文字排版 + 诗意标题 + 日期范围（形态由设计方向决定） |
| **章节叙述** | 每天 150-250 词散文，感官细节开头——不是「今天我们来到了美丽的...」 |
| **精选照片** | 2000 张进，40-60 张出。模糊的、截图的、重复的、口袋误触——全删了 |
| **可选地图** | Leaflet 轨迹线 + 地点标记，但不是每次必需（依设计方向决定） |
| **灯箱 / 内联展示** | 大图查看方式由设计方向决定：灯箱、全屏 slideshow 或 inline 展示 |
| **自包含** | 单文件 HTML，照片 base64 内嵌。拖到哪都能打开 |

---

## 工作流程

memoir 是一个 **Claude Code skill**——AI agent 读取指令文件，驱动 Python 流水线。你用自然语言跟它对话。

```
Photos.app / 文件夹
      ↓
  EXIF 提取（时间 + GPS）
      ↓
  Apple Photos AI 评分（美学质量、截图检测、人物识别）
      ↓
  智能预筛选 — 按 Apple 评分 + GPS 多样性排序，
  只下载最好的 ~5% 云端照片
      ↓
  反向地理编码（OpenStreetMap Nominatim）
      ↓
  日期 + GPS 聚类
      ↓
  品质预检（模糊、曝光、去重、连拍检测）
      ↓
  Claude 撰写叙述 + 现场设计 HTML（没有模板，每次不同）
      ↓
  后处理（base64 内嵌、Leaflet 注入、自包含验证）
      ↓
  自包含 HTML → 双击打开
```

## 安装

memoir 是一个 Claude Code skill。使用方式：

```bash
# 克隆仓库
git clone https://github.com/EricJiang0423/memoir.git
cd memoir

# 方式 A：symlink skill/ 到 .claude/skills/
ln -sf $(pwd)/skill ~/.claude/skills/memoir

# 方式 B：或直接复制（无视 demo/ 部署文件）
cp -r skill/ /path/to/.claude/skills/memoir/
```

`skill/` 是**完全自包含的**——SKILL.md、scripts/、references/、requirements.txt、CLAUDE.md 全在目录里，不依赖仓库根层的 demo 和部署文件。装好后在新对话中触发即可。

---

## 设计哲学

### NEVER converge（永不趋同）

没有 HTML 模板，没有固定布局。memoir 维护了一套**设计方向池**（`skill/designs/`）——大画册、旅行手帐、宽银幕、暗房、Zine 小志、极简白……每次执行时 agent 根据旅行气质推荐 2-3 个方向，让用户选择后落地。

同一个京都行程，在「大画册」方向下是一本深棕底的博物馆图录，在「宽银幕」方向下是一部黑底电影分镜。**这是强制性的设计纪律，不是可选开关。** 方向之间不能只是换配色——布局 archetype、照片处理、动画哲学、哪些元素保留/砍掉——都得不同。

不了解可用方向？执行中 agent 会让用户从 `designs/README.md` 一览表中选择。

### 自定义设计方向

如果内置方向都不对，你可以自己写或从外部导入新的设计方向。memoir 提供了 `skill/scripts/import_design.py` 工具：

```bash
# 从本地文件导入
python3 skill/scripts/import_design.py my-design.md

# 从 GitHub raw URL 导入
python3 skill/scripts/import_design.py https://raw.githubusercontent.com/user/repo/main/designs/retrowave.md

# 查看已注册方向及布局类型
python3 skill/scripts/import_design.py --list
```

导入的设计会校验 9 个必填章节和 `layout_type` 唯一性（确保结构差异），然后自动注册到 `skill/designs/README.md` 索引中。下次执行时 agent 就能推荐它。

> 参考 `skill/designs/TEMPLATE.md` 了解设计方向文件的格式要求。

### 隐私是架构，不是功能

照片字节**绝不离开本机**。唯一发出的数据是 GPS 坐标（两位小数精度）→ OpenStreetMap Nominatim 做地名查询。EXIF 解析、图片缩放、聚类、base64 编码、Claude 多模态视觉采样全部在本地完成。

### 自包含承诺

交付物就是一个 HTML 文件。没有服务器、没有外部 JS、没有 assets 目录、没有使用说明。AirDrop 给朋友、放进 U 盘、挂到任何静态托管——在哪都能打开。

### 借力 Apple Photos 原生智能

Photos.app 模式下，memoir 直接读取 Apple 端侧 ML 评分：27 维美学评分、截图标记、收藏、隐藏、已命名人物。这些数据在下载前就能用——云端照片还没下载，memoir 已经知道哪些值得留。

---

## 快速开始

### 前置条件（仅 macOS）

```bash
brew install exiftool libheif
pip install -r requirements.txt
```

### 验证

```bash
python3 scripts/check_deps.py
```

### 在 Claude Code 中使用

把 `memoir/` 目录放到 skills 路径下，然后说任意一句：

> 「整理我上次旅行的照片」
> 「把这周的相册做成旅行日记」
> "Make a travel diary from my recent photos"

Claude 会加载 skill，驱动整条流水线——从询问照片来源到交付 HTML。

### 或手动跑

```bash
python3 scripts/extract_photos.py --date-range 2024-03-01 2024-03-07 --out raw_photos.json
python3 scripts/prefilter.py --in raw_photos.json --out download_list.json
# ... 用 AppleScript 仅下载筛选后的照片（见 references/osxphotos-tips.md）...
python3 scripts/geocode.py --in raw_photos.json --out geocoded_photos.json
python3 scripts/cluster.py --in geocoded_photos.json --out diary_data.json
python3 scripts/curate.py --in diary_data.json --out curation_manifest.json
# ... Claude 撰写叙述 + 设计 HTML ...
python3 scripts/build_diary.py --in diary_data.json --html draft.html --out final.html
```

---

## 流水线脚本

| 脚本 | 职责 |
|------|------|
| `check_deps.py` | 检查系统/Python 依赖，输出 JSON |
| `extract_photos.py` | EXIF 提取（文件夹模式用 exiftool，Photos.app 模式用 osxphotos + Apple 评分） |
| `prefilter.py` | 用 Apple 美学评分 + GPS 多样性预筛选云端照片，选每地 top N |
| `geocode.py` | 反向地理编码 GPS → 地名（Nominatim，1 req/s，磁盘缓存） |
| `cluster.py` | 按日期 + GPS 距离分组（500m 同组 / 2km 新地点） |
| `curate.py` | 品质指标（Apple 评分或 Laplacian 回退）+ 去重/连拍检测 + contact sheet |
| `build_diary.py` | Token 后处理：`trip-design://photo_NNNN` → base64，Leaflet 内嵌，JSON 注入，自包含验证 |

---

## 项目结构

```
memoir/
├── README.md                   ← 本文件
├── PRD.md                      ← 产品需求文档
├── index.html                  ← GitHub Pages 落地页
├── .nojekyll                   ← Pages 配置
├── demos/                      ← 示例输出 + 预览照片
│   ├── kyoto-3-days.diary.html
│   └── photos/kyoto/
└── skill/                      ← 技能核心（可复制到 .claude/skills/）
    ├── SKILL.md                ← Agent 主控文档（核心）
    ├── CLAUDE.md               ← skill 级别的 project instructions
    ├── requirements.txt
    ├── test-prompts.json
    ├── designs/                ← 8 个设计方向（用户选择后执行）
    │   ├── README.md           ← 方向一览表
    │   ├── heritage-album.md   ← 大画册
    │   ├── traveler-notebook.md ← 旅行手帐
    │   ├── cinemascope.md      ← 宽银幕
    │   ├── darkroom.md         ← 暗房
    │   ├── zine.md             ← Zine 小志
    │   └── white-space.md      ← 极简白
    ├── scripts/                ← 7 个 Python 流水线脚本
    └── references/             ← 11 个深度参考文档
```

---

## 技术栈

| 层 | 技术 |
|----|------|
| 平台 | macOS（osxphotos 限制） |
| Agent | Claude Code / Codex / Cursor |
| EXIF | exiftool + PyExifTool + osxphotos |
| 图片处理 | Pillow + pillow-heif + OpenCV |
| 品质评分 | Apple Photos ML 评分（主力）+ Laplacian 方差（回退） |
| 去重 | 感知哈希（imagehash）+ Hamming 距离 |
| 地理编码 | geopy + Nominatim（OpenStreetMap，免费） |
| 地图 | Leaflet 1.9.4（内嵌）+ OSM 瓦片 |
| 输出 | 单文件 HTML，base64 内嵌照片 |

---

## 设计来源

memoir 的设计哲学来自以下项目：

- **[huashu-design](https://github.com/alchaincyf/huashu-design/)** ——「HTML 是工具不是媒介」、四定位提问、Junior Designer Mode、反 AI slop 清单
- **[Claude Code frontend-design skill](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design/skills/frontend-design)** ——「NEVER converge on common choices」、BOLD 美学执行
- **[awesome-design-md](https://github.com/VoltAgent/awesome-design-md)** —— 73 个品牌设计系统的 `DESIGN.md` 格式，启发了 `skill/designs/` 方向池的结构化方式
- **[guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill)** —— 锁定模板 · 瑞士国际主义布局系统，启发了方向池的严格边界思维

## License

MIT
