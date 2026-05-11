# diary-html-essentials · 区块池与 Token 协议

memoir **没有 HTML 模板**——每次生成时由 Claude 现场用前端能力设计。本文档定义两件事：

1. **区块池**：一份可用区块清单，每次从中选 2-4 种组合页面，不要固定套路
2. **Token 协议**：Claude 写的 HTML 如何与 `build_diary.py` 后处理器协作（base64 照片注入、Leaflet inline、JSON 数据注入）

设计风格 / 配色 / 字体 / 排版**完全由 Claude 自由发挥**——见 `references/diary-design-aesthetics.md`。

---

## 核心原则：结构服务表达

页面结构**不能重复**。不要每次都是 `Hero → 地图 → 每日区块 → 灯箱 → 页脚`。

问自己：**如果每页都必须换一种结构，这次会怎么做？**

- 如果只有 1 天 8 张照片 → 一张长卷滚动画廊就够了，不需要分天
- 如果是在东京跨年 → 一页照片的蓝色时间 + 霓虹 collage + 一行路线就够了，不要分章节
- 如果是公路旅行 → 路线图可以当主轴，照片挂在路线旁边
- 如果是探店 / 美食旅行 → 按食物类型分（早餐 / 食堂 / 宵夜），不要按地点

**结构也是设计决策**，和字体颜色一样重要。

---

## 区块池（每次选 2-4 个组合）

以下区块可用，但不是都用，更不是按这个顺序用。选什么取决于这次旅行的气质和照片结构。

### A · 开场 Hero

- 全屏 / 半屏视觉主图 或 文字排版 + 色块
- 旅行标题（`trip_summary.title`）
- 日期范围（`trip_summary.date_range`）
- 可选给出天数 / 城市数 / 照片数等摘要
- **不是必须全屏**——也可以是一个对角色块、一页大字幕、一组封面小图 mosaic

### B · 叙述章节

每日标题 + 每日叙述（`days[].title` + `days[].narrative`）+ 该日照片。

**不一定要按日期顺序**。可以是：

- 按视觉主题（青色的一天 / 金色的一天 / 蓝色黄昏）
- 按情绪线（到达 → 沉浸 → 离开）
- 跨天混编（把所有晴天照片并成一个"晴天"章节、雨天的并成另一个）
- 只写 2 个章节而非每天一段

照片展现方式可以是主图 + stills、并排 film strip、跨页画册、自由 collage、滚动横向走廊——**任何形式都行，不要重复上次的**。

### C · 路线索引（可选）

一张地图或一条路线示意。**不是必须的**：

- 一天都在一平方公里内走的（祇園 / 东山 / 下北泽）→ 不需要地图
- GPS 精度差或无轨迹 → 不要硬塞
- 跨城旅行（东京→大阪）→ 可以放小地图当索引
- 公路旅行 / 自驾 → 地图可以当主轴

如果用地图，仍用 Leaflet（Token 协议见下方）。地图可以后置、缩小、化身迷你路线图、或者干脆一行简单的时间路线文字替代。

### D · 灯箱（可选但不是摆设）

如果照片 ≤ 8 张，可以全部 inline 展示，不用灯箱。
如果照片 > 8 张，需要有放大看细节的机制，但不一定是全场灯箱——也可以是锚点跳转 / sidebar 大图切换 / accordion。

如果用灯箱，键盘 `← → Esc` 切换是**强推荐**（无障碍），但允许降级为点击箭头。
如果照片是全屏展示的（全屏 slideshow 形式），则不需要额外灯箱。

### E · 收尾（极简）

至少一行字标明生成工具 + 隐私说明。可以小到像 colophon 版权字一样不起眼。不用单独设计一整块。

### F · 间距与留白

空白本身也是区块。大留白、满出血、章节间的色彩过渡页（全色块/全黑/全图）——这些都是可选的结构元素。

---

## 结构多样性检查

写完 HTML 前过一遍：

- 这次的结构和上次**明显不同**。（如果是第一次生成，和假想的默认模板不同）
- 我选的 2-4 个区块有表达理由，不是"因为文档写了所以都放"。
- 这个结构是为这次旅行的照片定制的，不是套任何模板。
- 如果我把地图拿掉，页面还能成立吗？如果必须加地图才能支撑页面，说明结构太弱。

---

## Token 协议（与 build_diary.py 协作）

Claude 写 HTML 时**不能**手嵌 base64 照片（context 装不下）、**不能**复制 Leaflet 字节（156 KB 浪费 token）。改用 **token 占位**，由 `build_diary.py` 后处理替换。

### Token 类型

#### A · 照片引用 → `src="trip-design://photo_NNNN"`

```html
<img src="trip-design://photo_0001" alt="清晨的国際通り">
<img src="trip-design://photo_0002" alt="">
```

后处理把 `trip-design://photo_NNNN` 替换为：
- 默认（base64 模式）：`data:image/jpeg;base64,...` 完整 data URL
- relative 模式：`<out>.assets/photo_NNNN.jpg`

**规则**：只在 `<img src=>` 与 CSS `background: url(...)` 里用这个 scheme。**不要**在 JS 里拼字符串引用——见下方"灯箱里如何用"。

#### B · Leaflet 库注入 → 空标签 + data 属性

**只有决定用地图才加，不用地图就不加。**

```html
<style data-trip-design="leaflet-css"></style>
<script data-trip-design="leaflet-js"></script>
```

后处理把这两个空标签的 `textContent` 填为 Leaflet 1.9.4 的字节内容。

**位置约定**：
- `<style data-trip-design="leaflet-css">` 必须在 `<head>` 里（否则地图样式来不及生效）
- `<script data-trip-design="leaflet-js">` 必须在 `</body>` 之前 + 在你自己的地图初始化 JS **之前**

#### C · JSON 数据注入 → 空 script 标签

```html
<script type="application/json" data-trip-design="photos-index"></script>
<script type="application/json" data-trip-design="track"></script>
```

后处理把这两个空 script 的 `textContent` 填为：
- `photos-index`：`{ "photo_0001": {"src": "...", "caption": "...", "datetime": "..."}, ... }`
- `track`：`[ {"lat": 26.214, "lon": 127.681, "time": "10:23", "place": "..."}, ... ]`

Claude 自己写的 JS 这样读：

```javascript
const PHOTOS = JSON.parse(document.querySelector('[data-trip-design="photos-index"]').textContent);
const TRACK = JSON.parse(document.querySelector('[data-trip-design="track"]').textContent);
```

灯箱里要展示某张照片大图时，从 `PHOTOS[photo_id].src` 取 src（这个 src 已被后处理替换为 data URL 或相对路径），赋给 `<img>` 元素。**不要**自己拼 `trip-design://` 字符串。

### Token 一览表

| 用途 | 写法 | 后处理填什么 | 必须？ |
|------|------|-------------|--------|
| 照片 src | `<img src="trip-design://photo_0001">` | `data:image/jpeg;base64,...` 或 relative path | ✅ 必须 |
| 照片 CSS 背景 | `background: url("trip-design://photo_0001")` | 同上 | ✅ 必须 |
| Leaflet CSS | `<style data-trip-design="leaflet-css"></style>` | Leaflet 1.9.4 CSS 字节 | ❌ 只用地图才加 |
| Leaflet JS | `<script data-trip-design="leaflet-js"></script>` | Leaflet 1.9.4 JS 字节 | ❌ 只用地图才加 |
| 照片索引 JSON | `<script type="application/json" data-trip-design="photos-index"></script>` | 完整 photos 字典 | ✅ 必须（灯箱/JS 需要） |
| GPS 轨迹 JSON | `<script type="application/json" data-trip-design="track"></script>` | `all_gps_points` 数组 | ❌ 有地图或路线才加 |

---

## 数据契约（diary_data.json）

Claude 在策展和叙述步骤已经回填好入册照片、标题、叙述与 caption，HTML 设计阶段直接读这个 JSON 用：

```json
{
  "trip_summary": {
    "title": "冲绳七日，珊瑚礁与春风",
    "date_range": "2024-03-01 ~ 2024-03-07",
    "day_count": 7,
    "photo_count": 120,
    "cities": ["那覇市", "本部町", ...],
    "cover_photo_id": "photo_0001"
  },
  "days": [
    {
      "date": "2024-03-01",
      "day_number": 1,
      "title": "那覇漫步",
      "narrative": "清晨的国際通り还很安静...",
      "cover_photo_id": "photo_0001",
      "locations": [
        {
          "place_name": "国際通り",
          "place_detail": "国際通り, 那覇市, 沖縄県, 日本",
          "arrival_time": "10:23",
          "departure_time": "13:45",
          "center_gps": {"lat": 26.214, "lon": 127.681},
          "cover_photo_id": "photo_0001",
          "photos": [
            {"id": "photo_0001", "datetime": "2024-03-01T10:23:00",
             "gps": {...}, "caption": "..." (可选)}
          ]
        }
      ],
      "map_track": [...]
    }
  ],
  "all_gps_points": [...]
}
```

**字段说明**：
- `caption` 仅在 ≤ 30 张时由 Claude 写；缺失时 Claude 设计 HTML 时不展示文字
- `cover_photo_id` 是该层级的"代表照"
- `map_track` 已按时间排序，可直接喂给 Leaflet polyline（不用地图时不需读取）

---

## 自包含承诺（不可违反）

Claude 写的 HTML **必须**：

| 不允许 | 替代 |
|-------|------|
| `<script src="https://...">` | Token 注入 + 你自己的内联 `<script>` |
| `<link rel="stylesheet" href="https://...">` | Token 注入 + 你自己的内联 `<style>` |
| `<img src="https://...">` 引用网图 | 不需要——只用 `trip-design://` 引用真实照片 |
| `@import url(...)` 外部字体 | Web fonts 用 `data:` 编码或 system font stack |

**唯一允许的在线依赖**：地图底图 tile（Leaflet 默认 OSM tile 服务器），且只有决定放地图时才需要。

后处理脚本会**最终验证**：搜索 `<script src="http`、`<link ... href="http`、`<img src="http`，命中即报错（这是双保险，不替代 Claude 的自律）。

---

## 灯箱实现的最小约定（仅当使用灯箱时）

灯箱可以用任何视觉风格，但 JS 行为如适用：

```javascript
document.addEventListener('keydown', (e) => {
  if (!lightbox.classList.contains('open')) return;
  if (e.key === 'Escape') close();
  if (e.key === 'ArrowLeft') prev();
  if (e.key === 'ArrowRight') next();
});
```

切换上下一张时**全局有序**——所有照片按 day → location → 顺序串成一个数组。

---

## 后处理脚本如何使用

Claude 写完 HTML 后，跑：

```bash
python3 scripts/build_diary.py \
        --in diary_data.json \
        --html <Claude 写的 HTML 文件> \
        --out output/trip.diary.html
```

可选 `--embed-photos relative` 切换为相对路径模式（适合 > 200MB 时）。

build_diary.py 的职责（不做别的）：
1. 解析 Claude 的 HTML，找所有 token（`trip-design://...`、`data-trip-design=...`）
2. 处理照片（Pillow 缩放至 1600px、HEIC→JPEG q=85）
3. 替换 token：base64 / relative path / Leaflet 字节 / JSON 数据
4. 写出最终 HTML
5. 报告体积，> 200MB 建议切 relative
6. 验证自包含（搜外部 src/href）

它**不**做：HTML 解析、CSS 改写、JS 注入（除约定的注入点）。Claude 设计什么，它就吐什么。
