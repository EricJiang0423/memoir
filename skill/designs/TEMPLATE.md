# [方向名称]（[English Name]）

使用这个模板创建新的设计方向，供 `import_design.py` 注册。

## 必填字段

### 气质

一句话描述这个方向的视觉情绪。2-4 个关键词，逗号分隔。

### 适用场景

什么类型的旅行适合这个方向？什么不适合？

### 布局 Archetype

用 ASCII art + 文字描述页面的结构流。每一步写明照片怎么放、文字怎么排。

```
[页面结构流——用框图和箭头]
```

**关键要求**：布局 archetype 必须和现有所有方向的布局**结构上不同**（不能只是换配色）。现有方向已有的布局结构见 `README.md`。

### 色彩

- 底色 / 前景色 / 文字色 / accent 色，至少 4 个值
- 用 `oklch()` 或色名描述
- 说明从照片取色的规则（如果有）

### 字体

- 标题 / 正文 / 标签的字体栈（优先 system font stack）
- 字号、字重、字距参考

### 照片处理

- 边框（有/无、颜色、宽度）
- 滤镜（有/无、参数）
- 是否允许重叠 / 旋转 / 出血
- 照片尺寸策略

### 地图策略

- 用 Leaflet 地图？还是纯文字路线？还是不要地图？

### 灯箱策略

- 用灯箱？还是 inline 展示？如果用小图模式的照片数阈值是多少？

### 动画

- 入场动画 / hover 反馈 / 滚动触发
- 风格节奏（快/慢/安静/活泼）

### 严禁清单

- 这个方向不允许出现的元素

---

## 元数据（import 用）

以下字段在文件末尾，`import_design.py` 读取：

```yaml
name: 方向名称（中文）
name_en: Direction Name (English)
vibe: 2-4 个关键词
tags: 逗号分隔的标签，用于自动匹配推荐
best_for: 适用的旅行场景
layout_type: 布局类型（spread / scroll / grid / slide / collage / single）
has_map: true/false
has_lightbox: true/false
has_narrative: true/false
```
