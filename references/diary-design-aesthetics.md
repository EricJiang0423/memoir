# diary-design-aesthetics · 旅行日记美学指南

trip-design 的 HTML 由 Claude 现场设计——**不复用 template，每次不同**。本文档不给完整代码示例，只给：

1. **设计思维框架**：开工前要做的美学决定
2. **几个适合旅行记录的方向**：作为灵感库，不是必选项
3. **反前端 slop 速查**：杀掉 AI 默认审美

> 参考 [Claude Code frontend-design skill](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design/skills/frontend-design) 的核心原则：**Bold maximalism 与 refined minimalism 都行，关键是 intentionality 而非 intensity**。

---

## 设计思维：四定位提问（开工前必答，写入 HTML 注释）

参考 huashu-design 的「Position Four Questions」——每次写 HTML 前，在 `<!-- 设计假设 -->` 注释里回答这四个问题。这一步比写代码重要。

### 定位 1 · 叙事角色（Narrative Role）

这份页面是什么？

- **私人回忆录**：给自己看的，不需要解释地名，只需唤起感受 → 亲密、克制、留白多
- **分享给朋友的游记**：需要一点上下文（日期、路线），但不能太"正式" → 温暖、可读、节奏轻快
- **公开博客 / 作品**：需要完整信息（地图、日期、城市名），排版更精致 → 编辑风、有章节感

### 定位 2 · 观众距离（Audience Distance）

读者需要多少背景信息？

- **近（自己/密友）**：不需要地图首页、不需要日期引导——可以直接从一张照片开始
- **中（朋友/家人）**：需要日期锚点 + 地名提示，但不需要逐张解释
- **远（公众）**：需要完整的时间线、地图、地点标注——但这不意味着模板化

### 定位 3 · 视觉温度（Visual Temperature）

这次旅行的情绪温度是什么？

- **冷静深沉**：蓝/灰/阴影色调、generous whitespace、慢滚动节奏
- **温暖亲近**：金/橙/米色调、饱和 accent、照片更满版、节奏更快
- **高反差**：黑白 + 单点强烈色彩（如雪地里的红围巾、沙漠里的蓝天）

### 定位 4 · 容量估算（Capacity Estimation）

X 天 / Y 张入册照片 / Z 字叙述——这决定了每张照片能分到多少"空间"：

- **短旅行（1-2 天，< 20 张）**：可以做 maximalist——每张照片都有专属的排版处理
- **中旅行（3-5 天，20-40 张）**：需要节奏交替——有些满版、有些 stills 网格
- **长旅行（7+ 天，40-60 张）**：需要高效结构——scannable、章节分明、不要每次都"开篇"

---

### 1. 这次旅行的"气质"是什么？

不是"很美"、"很难忘"——这些是空话。是：

- **高反差**（沙漠 vs 城市 / 雪山 vs 海滩 / 喧嚣 vs 寂静）
- **温度**（夏日热带、冬日北欧、春日江南、秋日山野）
- **节奏**（一日多地的赶场 / 长居一城的慢游 / 公路自驾的流动）
- **主题**（建筑、美食、博物馆、徒步、历史、朋友聚会）

气质决定字体、色调、空间节奏。**先 vocalize 一句**：「这次旅行的核心气质是 X」，再开工。

同时先判断：这份作品是“行程记录”还是“艺术回忆”。默认是艺术回忆：少量强图、章节表达、地图降级为索引。不要让 GPS 聚类决定设计结构。

### 2. 选择一个 BOLD 的美学方向

旅行日记尤其忌讳「中庸」——温吞的暖灰底 + 系统字体 + 圆角卡片是 AI slop 标配。**敢于走极端**：极简到只剩字体与留白；浓烈到铺满色块；复古到像旧画册。

**关键**：选一个方向**全力执行**，不要"少一点这个、加一点那个"地折中——折中产物总是无个性的。

### 3. 字体选择

字体是旅行日记的灵魂。**绝不**用 Inter / Roboto / Arial / system-ui 当 display——这些字体在网页里出现得太多，看见就联想到"普通后台"，没有"作品"感。

倾向：
- 衬线 display + sans body 的经典组合（杂志感）
- 单一漂亮字体贯穿（极简感）
- 中文用「PingFang SC」「Songti SC」「LXGW WenKai」「Noto Serif SC」
- 显示字体用 Google Fonts 时**用 data: 编码内嵌**（自包含承诺）或确认在 system font stack 里

### 推荐字体配对

每次从以下配对中选择（或自创，但不要重复上一份的设计）。自包含约束下优先 system font stack；如果某字体对表达至关重要，用 base64 内嵌 woff2 子集。

| 方向 | Display（标题） | Body（正文） | 气质 |
|------|----------------|-------------|------|
| 编辑风 | Instrument Serif | Geist Sans | 杂志、文学、评论感 |
| 经典人文 | Cormorant Garamond | Inter Tight | 古典、稳重、适合长文 |
| 技术/田野笔记 | JetBrains Mono | Geist Sans | 干净、当代、数据感 |

中文环境加配：

| 方向 | Display | Body | 气质 |
|------|---------|------|------|
| 宋体编辑 | Songti SC / Noto Serif SC | PingFang SC | 中文杂志、散文 |
| 楷体人文 | LXGW WenKai | PingFang SC | 温和、手写感、私人 |

**字体硬约束**：标题与正文字体必须看得出来不同（除非是统一字体的极简风）；正文最小 16px（web）/ 14px（caption）；标题至少正文的 2.5x 大小。

### 4. 色彩

旅行日记的色彩**应该呼应旅行本身**：

- 海岛/海洋 → 冷蓝 + 暖珊瑚
- 沙漠/秋季 → 赤土橙 + 深棕
- 北欧/冬季 → 冷灰 + 单一暖 accent
- 春日/和风 → 米白 + 樱粉 + 墨黑
- 都市/夜行 → 深底 + 单点霓虹

**不要**用通用的"温暖橙色"或"清新蓝色"——这些是空话。从首张照片里**取一个色**当 accent，比凭空发明色稳。

---

## 几种适合旅行记录的方向（灵感库）

不是必选项。**禁止每次都选同一个**——参考 frontend-design 的「NEVER converge」。

### A · 杂志编辑（Editorial）

灵感：Cereal、Kinfolk、Monocle 旅行栏目。
- 衬线 display（Tiempos Headline / GT Sectra / 中文 Songti SC）
- 大量留白 + 偶尔满版图片
- 文字优先，照片是配图
- 常见 2-3 列文字流，照片打破列宽
- 色：纸白 + 墨黑 + 一点单色 accent

适合：以叙述为主、照片精选不多的旅行（如博物馆/建筑游）。

### B · 胶片复古（Analog Film）

灵感：胶片相册、旧风景明信片。
- 米黄底（如 #f4ecdf）+ 棕墨字
- 衬线字体（Playfair / Cardo / 中文 Noto Serif）
- 照片加细边框 + 轻微旋转 + 投影
- 标签像手写或打字机字体（Special Elite / IBM Plex Mono）
- 色：低饱和 + 暖偏色

适合：怀旧主题、胶片感强的旅行（如公路、欧洲老城）。

### C · Wes Anderson 对称

灵感：《布达佩斯大饭店》《月升王国》。
- 高度对称的布局
- 一组特定的暖色（米黄、藕粉、薄荷绿、灰蓝）三色循环
- 标签居中、对仗工整
- 字体偏古典 sans 或装饰衬线（Futura / Domaine）

适合：建筑感强、画面有戏剧张力的旅行。

### D · 日式极简（东方诗意）

灵感：原研哉、深泽直人、wabi-sabi。
- 极大留白
- 唯一颜色：墨黑 / 米白 / 一点朱红
- 衬线字体（Noto Serif SC / Songti SC / EB Garamond）
- 照片小且克制
- 标题用日文/中文古典排印

适合：禅意主题、和风、自然山野旅行。

### E · Brutalism 粗野

灵感：Drudge Report 美学复兴、最近设计圈的"反精致"潮流。
- 单一系统等宽字体（Mono / Courier）
- 锐利无圆角 + 高对比黑白
- 网格密集 + 无装饰
- 偶有一处巨大色块当视觉锚

适合：硬核旅行（探险、攀登、田野调查）、技术/极客气质。

### F · Maximalism 满版彩印

灵感：Sagmeister、80s 旅游海报。
- 多色重叠
- 文字与图像混排
- 大胆 grid 打破
- 装饰性几何

适合：节庆、嘉年华、东南亚 / 拉美 / 印度的色彩浓烈地区。

### G · 厚重画册（Heritage Album）

灵感：旧博物馆藏品图录、皇家地理学会的探险记录。
- 深棕/深绿底 + 米黄前景
- 衬线 display + 古朴 ornament
- 照片像贴在册页上 + 手写标签
- 章节首字下沉

适合：历史/文化主题旅行、长跨度回顾。

---

## 反前端 slop 速查（必读）

以下东西**几乎总是错的**——AI 默认会产出，识别 + 杀掉。

| 元素 | 为什么是 slop | 何时可破例 |
|------|-------------|----------|
| **紫渐变背景**（135deg, #667eea, #764ba2 之类）| 2020s SaaS / AI 落地页烂大街 | 旅行去了真有紫色霓虹的场景（如东京、香港夜景）|
| **Inter / Roboto / Arial / system-ui 当 display** | 太常见，瞬间感觉"无设计" | 极简风刻意只用一种 system font，且全页统一 |
| **圆角卡片 + 左侧彩色 border accent** | Tailwind / Material 滥用 | 几乎不破例 |
| **每段标题配 emoji**（📍 ✈️ 📷）| 装饰性，不增加信息 | 用户气质本就活泼，且 emoji 是叙事一部分 |
| **统一圆角 + 阴影 + 卡片**（"Notion 化"）| 中性、没有气质 | 极简风刻意为之 |
| **彩虹 grid placeholder**（渐变方块假装是图）| 设计原型遗物，正式输出不该有 | 永不 |
| **全量照片瀑布流 / 均匀网格** | 相册导出感，缺少策展与节奏 | 用户明确要归档页 |
| **hero + map + timeline + grid 套路** | 看似完整，实则每次同质化 | 只有在结构被重新设计时 |
| **居中对齐所有内容** | 视觉层级缺失，处处平均 | 极少；某些极简风可全居中 |
| **「✨ 让你的 X 焕然一新」式文案**（连 trip-design 不写文案，但 hero badge 也别用这种）| AI 默认营销腔 | 永不 |
| **过多 micro-interactions**（每个按钮都 hover 弹起、每个标题都 fade-in）| 散乱无主旨 | 一次 well-orchestrated 的页面入场 = 多次散落微互动的体验 |
| **bento grid 布局** | Apple/线代设计过度使用，缺乏个性 | 几乎不破例——旅行日记不是产品页 |
| **hero + 3-panels + testimonials 模板** | SaaS landing page 遗毒 | 旅行日记根本不该出现 |
| **全 CSS 渐变背景（无照片）** | 偷懒不用真实照片 | 永不——用 trip-design:// 引用真实照片做 hero |
| **「✨ 探索 X 的秘密」式营销标题** | AI 默认营销腔 | 永不——叙述性标题，不是 slogan |

**正向做什么**（参考 frontend-design）：

- ✅ `text-wrap: pretty` + 高级 CSS（grid 子区域、container queries、`oklch()` 色）
- ✅ 字体加 `font-feature-settings`（小型大写、连字、文本数字）
- ✅ 一处 hero 动效做到 120%，其它处保持安静
- ✅ 配色从首张照片里"取色"，而非凭空发明
- ✅ 先选主图，再围绕主图设计章节；不要先铺 grid
- ✅ 让地图退到索引位置，除非路线本身就是作品主角
- ✅ 中文用「」引号，不用 `""` 直引号（排印细节）
- ✅ 标题与正文用不同字体；不同就要看得出来
- ✅ 用真实照片当 hero（trip-design://photo_NNNN），不要 SVG 画风景
- ✅ 留白比塞满好——一张好照片旁边的空白比"再塞一张"有力

### CSS 技术标准（V1.3 升级）

写 HTML 时主动使用现代 CSS 提升排版和执行质量：

| 技术 | 用途 | 示例 |
|------|------|------|
| `text-wrap: balance` | 多行标题防止孤行 | `h1, h2 { text-wrap: balance; }` |
| `text-wrap: pretty` | 正文换行更均匀 | `p { text-wrap: pretty; }` |
| `hanging-punctuation: first` | 中文引号悬挂 | `p { hanging-punctuation: first; }` |
| `oklch()` 色彩空间 | 感知均匀，取色直观 | `--accent: oklch(0.65 0.18 25);` |
| `color-mix()` | hover 状态自动推导 | `color-mix(in oklch, var(--accent) 80%, white)` |
| CSS Grid `subgrid` | 跨行卡片内容对齐 | `grid-template-rows: subgrid;` |
| `@container` 查询 | 组件级响应式 | `@container (min-width: 500px) { ... }` |
| `:has()` 选择器 | 上下文感知样式 | `.gallery:has(> img:only-child) { ... }` |
| `backdrop-filter` | 灯箱毛玻璃蒙层 | `backdrop-filter: blur(20px) saturate(150%);` |
| `font-feature-settings` | 小型大写、连字 | `"ss01", "liga", "calt"` |
| `@view-transition` | 页面间导航过渡 | `{ navigation: auto; }` |

**一处 120% 细节**：选一个动效做到精致（hero 视差、标题 letter-spacing 渐入、照片 reveal 动画），其余保持安静。一个打磨过的动效 > 十个散落的 micro-interaction。

---

## 多变性检查（每次都必做）

**NEVER converge**——不要每次生成的 HTML 都长得像。开工前问自己：

- 上次（如果有上次）选了什么字体？这次故意选不同流派
- 上次主色是什么？这次反着来（暖 → 冷 / 浓 → 淡）
- 上次布局是什么？这次试别的（左右栏 → 全宽 / 网格 → 流式）

旅行本身就是多样的——每段旅行的日记**应该有自己的视觉指纹**。

---

## 复杂度匹配

参考 frontend-design 的「Match implementation complexity to the aesthetic vision」：

- **Maximalist 设计**需要复杂代码：大量动效、自定义 SVG 装饰、嵌套 grid、复杂 keyframes
- **Minimalist 设计**需要克制：每个像素都精心；间距、字号、字重的微调；不要"为了显得做了事"加无意义的 hover 反馈

**优雅来自把方向执行到位**，不是把所有 trick 都用上。

---

## Junior Designer Mode（写 HTML 前的策略）

参考 huashu-design 的「Junior Designer Mode」——先假设、再占位、再填内容。

### 1. 写设计假设注释

在 HTML 开头用 `<!-- 设计假设 -->` 注释写清你的美学决定和推理链条，**不要一上来就铺代码**：

```html
<!--
  设计假设：
  - 这次旅行是京都红叶季，气质 = 温润的秋日静谧
  - 叙事角色 = 私人回忆录（给自己看的）
  - 观众距离 = 近（不需要解释地名）
  - 视觉温度 = 暖但克制（枫叶红/米棕，不高饱和）
  - 容量 = 3天 / 28张入册 / 每张有caption
  
  字体：Cormorant Garamond + Inter Tight（经典人文配对）
  色彩：从 photo_0003（枫叶特写）取色 oklch(0.55 0.18 45)
  布局：左右不对称——左宽文 + 右窄图列
  
  不确定的地方：
  - 地图放哪？→ 先放页脚，写完如果叙事需要再移到首屏
  - 灯箱动画？→ 先 fade + scale，视觉效果对了再考虑别的
-->
```

### 2. 灰色占位优先

layout 先出来（灰块代表照片、灰条代表文字），确认节奏和留白 OK，再替换为真实 token 和文案。先用 div 确认结构，再填照片。

### 3. Placeholder > Bad Implementation

不确定某个区域时，留 HTML 注释说明意图，不要硬塞一个不成立的实现：

```html
<!-- TODO: 这里计划放视差封面，但不确定照片选择。
     暂时用静态 hero 占位，确认照片后再加 parallax。 -->
```

### 4. 给变体，不给唯一答案

拿不准两个方向时（如「全宽 hero vs 侧栏 hero」），在注释里简短说明备选，选一个先做。用户看到后可以要求换方案。

---

## 自检清单（写完每段后过一遍）

- [ ] 四定位提问已回答（叙事角色 / 观众距离 / 视觉温度 / 容量估算）并写入 HTML 注释？
- [ ] 设计假设 + 推理在 HTML 注释中可见？
- [ ] 字体不是 Inter / Roboto / Arial / system-ui 当 display
- [ ] 没有紫渐变（除非真的合主题）
- [ ] 没有"圆角卡片 + 左 border accent"
- [ ] 没有 bento grid / hero+3-panels 模板
- [ ] 标题与正文字体不同（除非是统一字体的极简风）
- [ ] 主色 ≤ 3 个；其中 1 个是从照片"取"出来的，且用 oklch()
- [ ] 使用了至少 2 项 CSS 技术标准（text-wrap: balance, subgrid, :has(), color-mix()...）
- [ ] 一处 120% 动效精致打磨 + 其余安静
- [ ] hero 区有视觉冲击（不是"标题居中 + 副标题灰色"）
- [ ] 照片的展现方式与气质匹配（杂志风用大图满版，画册风用小图边框）
- [ ] 没有把所有照片均匀罗列成相册导出
- [ ] 每个照片区块都有表达作用，不只是展示数量
- [ ] 灯箱键盘导航（←→ Esc）已实现
- [ ] 自包含承诺：无 `<script src="http`、无 `<link href="http`、无 `<img src="http`
- [ ] 这个设计**和上一份不一样**
