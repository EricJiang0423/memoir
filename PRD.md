# trip-design · 产品需求文档

> **实现状态（2026-05-11）**：V1.3 已交付，V1.4 设计中。
>
> - **V1.0**：SKILL.md + scripts/（5 个）+ Jinja2 template + references/（7 个）+ test-prompts.json
> - **V1.1**：Photos.app 「一键时间范围模式」（相对日期 today / last-week / last-month / YYYY-MM 等 + `--list-recent-trips` 启发式发现潜在旅行段）
> - **V1.2**：架构重构——**移除 HTML 模板**，改为 Claude 现场设计 + `build_diary.py` 做 token 后处理（base64 / Leaflet / JSON 注入）。新增 `references/diary-html-essentials.md`（必备元素 + Token 协议）与 `references/diary-design-aesthetics.md`（美学方向 + 反前端 slop）。设计哲学参考 [Claude Code frontend-design skill](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design/skills/frontend-design)：「NEVER converge on common choices」
> - **V1.3**：多模态策展增强（`curate.py` 品质预检 + contact sheet）+ huashu-design 设计范式深化（四定位提问 / Junior Designer Mode / 字体配对 / CSS 技术升级）
> - **V1.4**（当前）：设计方向池（`skill/designs/`）——将设计多样性从"Claude 每次靠灵感"升级为"系统性地储备差异化的方向.md"，每次执行推荐 2-3 个让用户选。仓库结构重构：skill 核心移入 `skill/` 自包含目录，demo/部署文件留在根层。

## 产品概述

**trip-design** 是一个 Claude Code skill，用途单一且明确：给定一组旅行照片，自动分析其 EXIF 元数据（拍摄时间、GPS 坐标），通过反向地理编码转化为可读地名，再由 Claude 撰写旅行叙述，最终生成一个**完全自包含的旅行日记 HTML 网页**，无需任何服务器或外部依赖即可打开和分享。

---

## 用户与场景

**目标用户**：有旅行摄影习惯、希望将照片整理成有故事感记录的个人用户（macOS 平台）。

**核心场景**：
- 旅行结束后，从 Apple Photos.app 相册或照片文件夹一键生成旅行日记
- 生成的 HTML 文件可直接发给朋友、上传博客，或在本地浏览留存

**非目标场景**：
- 多人协作编辑
- 服务器部署 / 云同步
- 视频内容

---

## 功能需求

### F1 · 照片输入（两种模式）

| 模式 | 输入方式 | 适用场景 |
|------|---------|---------|
| 文件夹模式 | `--folder /path/to/photos` | 照片已导出为文件 |
| Photos.app 模式 | `--album "相册名"` 或 `--date-range <range>` | iCloud 照片库直读 |

**`--date-range` 支持的格式**（V1.1 增强）：
- `2024-03-01 2024-03-07` — 经典两段日期
- `2024-03-15` — 单日
- `2024-03` — 整月
- `today` / `yesterday` / `this-week` / `last-week` / `this-month` / `last-month` — 相对关键词

**Photos.app 辅助子命令**：
- `--list-albums` — 列出所有相册（标题 / 照片数 / 日期范围）
- `--list-recent-trips [--days 90]` — 启发式发现近 N 天潜在旅行段
- `--dry-run` — 预检（不写文件，仅报告 total / local / optimized / cloud_only / with_gps）

**支持格式**：JPEG、HEIC、PNG、RAW（DNG、ARW 等）

**iCloud 照片状态处理**：
- 本地已下载：直接处理
- 优化存储（缩略图本地）：提示用户，可触发下载后处理
- 仅云端：默认跳过，告知数量，询问是否等待下载

### F2 · 元数据提取

- 拍摄时间：优先读 `DateTimeOriginal`，回退到 `CreateDate`，再回退到文件修改时间
- GPS 坐标：读 `GPSLatitude/Ref` + `GPSLongitude/Ref`，转换为十进制度
- 无 GPS 照片：不丢弃，按时间归入邻近地点组

### F3 · 地点识别

- 使用 Nominatim（OpenStreetMap，免费，无需 API Key）进行反向地理编码
- 速率：≤ 1 请求/秒（自动限速）
- 本地磁盘缓存：相同区域（精度 ~111m）只查一次，避免重复请求
- 提取层级：细分地名 + 城市 + 地区 + 国家，用于标题和 tooltip

### F4 · 照片聚类

按以下规则自动组织照片结构：
1. 按拍摄日期分"天"
2. 同一天内按 GPS 距离分"地点"（相邻 < 500m 同组，> 2km 新开一组）
3. 无 GPS 照片继承前一张的地点
4. 每天、每地点自动选出"封面照"（文件最大的，启发式代表质量最高）

### F5 · 旅行叙述（Claude 生成）

Claude 负责：
- **旅行标题**：诗意命名，如"冲绳七日，追风逐浪"
- **每日标题**：≤ 10 字/词的简短日标题
- **每日叙述**：150-250 词，第一人称，以感官细节开头，不虚构活动
- **照片 caption**（可选）：≤ 30 张时，Claude 视觉分析每张照片写一句描述

**策展增强（V1.3）**：在 Claude 视觉采样前，`curate.py` 预计算每张照片的模糊度、曝光质量、感知哈希（去重）、连拍分组，并生成视觉 contact sheet（缩略图网格 + 色边标记）。Claude 用**一次**多模态调用（Read contact sheet）完成全部视觉策展，而非逐张 Read 原始照片。

叙述语言：跟随用户语言，不指定则默认中文。

### F6 · HTML 输出

**核心要求**：完全自包含，单文件，拖入浏览器即可打开

**架构**（V1.2 重构 + V1.4 方向池）：**没有固定 HTML 模板**——用户从 `skill/designs/` 选择一个设计方向，Claude 按该方向的 spec 现场设计 HTML，`build_diary.py` 只做 token 后处理。

| 特性 | 实现方式 |
|------|---------|
| HTML 设计 | 用户从 `skill/designs/` 选方向 → Claude 按该方向的 .md spec 执行（布局 archetype / 色彩 / 字体 / 照片处理 / 动画） |
| 照片嵌入 | Claude HTML 写 `src="trip-design://photo_NNNN"` token；后处理替换为 base64 或相对路径 |
| Leaflet | Claude HTML 留 `<style data-trip-design="leaflet-css"></style>` 等空标签；后处理注入 1.9.4 字节 |
| 数据注入 | Claude HTML 留 `<script type="application/json" data-trip-design="track"></script>` 等空标签；后处理注入 JSON |
| 图片处理 | Pillow 缩放至 1600px 宽，HEIC 转 JPEG，quality=85 |
| 地图底图 | OpenStreetMap CDN（唯一允许的在线依赖） |
| 体积预警 | > 200MB 自动提示切换 relative 模式 |
| 自包含验证 | 后处理脚本搜外部 src/href 引用，命中即警告（`--strict-self-contained` 改为 fail）|

---

## 页面结构

**不限定固定页面结构**。结构由用户选择的设计方向决定。`skill/designs/` 中的每个方向定义了独立的布局 archetype，方向之间结构必须不同。

参考方向示例的结构差异：

| 方向 | 核心布局 | 地图 | 灯箱 | 叙述段落 |
|------|---------|------|------|---------|
| 大画册 | 跨页对开 + 章节衬页 | ❌ 无 | ❌ 无 | ✅ 短 |
| 旅行手帐 | 跨页日记 + 拼贴资料页 | ❌ 无 | ❌ 无 | ✅ 有 |
| 宽银幕 | 黑场 → 宽画幅 → 三连帧 | 可选收尾 | 可选 | ❌ 无散文 |
| 暗房 | 接触印相网格 ↔ 全幅单页 | ❌ 无 | ❌ 无 | ❌ 无 |
| Zine 小志 | 照片重叠拼贴 + 文字浮动 | ❌ 无 | ❌ 无 | ✅ 穿插 |
| 极简白 | 单张照片独占一页 | ❌ 无 | ❌ 无 | ✅ 短 |

**硬约束**（所有方向统一遵守）：
- 单文件 HTML，照片 base64 内嵌（或 relative 模式）
- 无外部 script/link/img src 引用（除 OSM 瓦片）
- `trip-design://photo_NNNN` Token 协议 + `photos-index` JSON 注入

---

## 非功能需求

| 维度 | 要求 |
|------|------|
| 平台 | macOS（Apple Silicon / Intel），Python 3.10+ |
| 隐私 | 所有处理在本地完成，照片文件不上传任何服务器（仅 GPS 坐标发送至 Nominatim） |
| 性能 | 100 张照片完整处理时间 < 5 分钟（地理编码为主要瓶颈） |
| 离线 | 地图底图需联网，其余功能完全离线可用 |
| 体积 | 100 张照片生成 HTML 约 50-100MB，浏览器可流畅打开 |

---

## 技术依赖

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| `exiftool` | EXIF 完整提取（含 HEIC/RAW） | `brew install exiftool` |
| `libheif` | HEIC 格式解码（Pillow 需要） | `brew install libheif` |
| `PyExifTool >= 0.5.6` | exiftool Python 封装 | `pip install PyExifTool` |
| `osxphotos >= 0.68.0` | Photos.app SQLite 直读 | `pip install osxphotos` |
| `geopy >= 2.4.0` | Nominatim 反向地理编码 | `pip install geopy` |
| `Pillow >= 10.0.0` | 图片缩放 + HEIC→JPEG | `pip install Pillow` |
| `opencv-python-headless >= 4.8.0` | 模糊检测（Laplacian 方差）+ 直方图分析 | `pip install opencv-python-headless` |
| `imagehash >= 4.3.1` | 感知哈希去重 + 连拍分组 | `pip install imagehash` |
| `scipy >= 1.10.0` | Laplacian 方差数值计算 | `pip install scipy` |

> V1.2 移除 `Jinja2` 依赖。V1.3 新增 `opencv-python-headless`、`imagehash`、`scipy` 用于品质预检。

---

## 对话交互流程

### 标准 7 步（默认；本地文件夹 / 首次使用）

```
用户：  "给我的冲绳旅行照片创建旅行日记"

Claude: 询问输入源（文件夹 / Photos.app 相册）
        ↓
        检查依赖（check_deps.py）→ 提示安装缺失依赖
        ↓
        提取照片元数据（extract_photos.py）
        → 报告：X 张照片，Y 张本地可用，Z 张仅云端
        → 🛑 若有云端照片：询问下载 or 跳过
        ↓
        反向地理编码（geocode.py）→ 报告进度（限速 1 req/s）
        ↓
        聚类（cluster.py）→ 🛑 展示行程概览，请用户确认
        ↓
        Claude 分析数据 + 视觉采样照片 → 撰写叙述，填写 diary_data.json
        ↓
        从 skill/designs/ 推荐 2-3 个设计方向 → 用户选择
        ↓
        Claude 按选中的 design.md 执行（布局 / 色彩 / 字体 / 照片处理 / 动画）
        ↓
        生成 HTML（build_diary.py）→ 🛑 报告路径和体积；> 200MB 询问切 relative
```

### 一键时间范围模式（V1.1 增强；推荐 Photos.app 用户）

触发：用户给定明确日期（「3/1-3/7 的照片」）或相对时间（「最近一周」「上个月」「最近的旅行」）。

```
用户：  "分析我最近一周的旅行照片"

Claude: 自动 dry-run 预检（--date-range last-week --dry-run）
        ↓
        🛑 智能检查点 (a) - iCloud
          · cloud_only ≤ 5 且 optimized ≤ 10：自动跳过（量小，影响微）
          · 否则停下问下载/跳过
        ↓
        自动连跑 extract → geocode → cluster（不打断用户）
        ↓
        🛑 检查点 (b) - 聚类（始终保留：聚类是创意决定，必须人为审核）
        ↓
        Claude 自动撰写叙述 + 跑 build_diary
        ↓
        🛑 检查点 (c) - 体积（条件触发）
          · ≤ 200MB：直接报告路径
          · > 200MB：停下问 relative
```

模糊触发（「最近的那次旅行」）时先跑 `--list-recent-trips` 列候选段让用户选。详细决策见 SKILL.md 的「一键时间范围模式」一节。

---

## 超出范围（V1 不做）

- 多语言地图（仅英文/中文地名，取决于 Nominatim 返回）
- 天气数据集成
- 社交媒体一键分享
- 旅行统计（总里程、平均每天照片数等）
- Windows / Linux 支持（osxphotos 仅 macOS）
- 视频文件处理

---

## 成功指标

- 用户可以在 10 分钟内（不含 iCloud 下载等待）从提出需求到拿到完整 HTML 文件
- 生成的 HTML 在 Safari 和 Chrome 最新版中无错误打开
- 地名识别准确率 > 90%（有 GPS 的照片）
- 日期聚类正确率 > 98%（同一天的照片归到同一天）

---

## V1.3 实现交付清单（2026-05-11）

| 模块 | 文件 | 状态 |
|------|------|------|
| 主控文档 | `SKILL.md` | ✓ V1.3 升级：Step 6A 重写为 curate.py 预检 + contact sheet 两阶段；Step 7a 融入 huashu-design 四定位提问 + Junior Designer Mode + CSS 技术标准 |
| 品质预检 | `scripts/curate.py` | ✓ 新增：模糊/截图/曝光/去重/连拍检测 + contact sheet 生成 |
| 多模态策展 | `references/multimodal-curation.md` | ✓ 新增：contact sheet 读取协议 + 视觉策展维度 + keep/maybe/reject 决策格式 |
| 设计范式 | `references/diary-design-aesthetics.md` | ✓ V1.3 升级：四定位提问 / 字体配对表 / Junior Designer Mode / CSS 技术标准 / 反 slop 扩充 |
| 艺术策展 | `references/art-direction.md` | ✓ V1.3 升级：多模态策展流水线章节 + UI 截图检测 |
| 依赖 | `requirements.txt` | ✓ 新增 opencv-python-headless / imagehash / scipy |

**V1.2 已删除**：`assets/diary-template.html`（固定模板，违背"NEVER converge"）。

## V1.4 交付清单（当前）

| 模块 | 文件 | 状态 |
|------|------|------|
| 设计方向池 | `skill/designs/*.md` | ✓ 新增 6 个设计方向（大画册/旅行手帐/宽银幕/暗房/Zine 小志/极简白），每个含独立布局 archetype + 色彩/字体/动画 spec |
| 方向推荐流程 | `SKILL.md` Step 7a | ✓ 新增"设计方向推荐"子步骤：推荐 → 用户选 → 按 spec 执行 |
| HTML 必备放宽 | `references/diary-html-essentials.md` | ✓ 5 个硬性必备区块 → 6 个可选区块池，选 2-4 个组合 |
| 仓库重构 | 根层 | ✓ skill 核心移入 `skill/` 自包含目录；demo/部署/dev 文档留在根层 |
| 响应式修复 | `demos/kyoto-3-days.diary.html` | ✓ 图片高度固定→max-height + auto；1100px / 780px / 520px 三断点；移动端触摸滑动 |

**待真实环境验证**：HEIC/RAW 解码（依赖 `brew install libheif` + `pip install pillow-heif`）；Photos.app 模式（需「完全磁盘访问」授权）；跨 agent dry-run（Codex / Cursor）。
