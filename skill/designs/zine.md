# Zine 小志

## 气质

复印机美学、DIY、拼贴。像在咖啡店 photocopier 上自己印的小册子。粗颗粒、边缘裁切不齐、照片与文字重叠、半色调整流的图像。反精致，反"设计"。

## 适用场景

数码过剩的短途旅行、和朋友逛街、音乐节、快闪记忆。照片本身质量不高（手机拍、有噪点）时最适合——zine 不追求画质，追求态度。

## 布局 Archetype

```
[封面——一张照片放大到出血 110%，标题叠在它上面，字块衬纯白底色]
  ↓
[拼贴跨页——照片旋转重叠 + 文字浮在照片上]
  - 2-4 张照片，各旋转 -3deg ~ 4deg
  - 照片之间部分重叠（margin/padding 负值）
  - 文字横跨拍照之间，背景衬半透明白块
  ↓
[文字页——密集段落 + 一张小图嵌在文字流里，左/右浮动]
  ↓
[全页图像——一张照片占整页，上面叠一句话，字超大（6rem），衬黑色块]
  ↓
[拼贴跨页] → [文字页] → [全页图像] 重复
  ↓
[封底——小字 + 粗糙装饰线]
```

**不用地图。不用灯箱。** 照片本身就暴露在页面上，不用"浏览模式"。

## 色彩

- 底：`oklch(0.97 0.005 80)`（粗面纸白）
- 文字：纯黑 `oklch(0 0 0)`
- 可选 1 个 accent：亮荧光色 `oklch(0.70 0.20 40)`（橙）/ `oklch(0.65 0.22 300)`（紫）/ `oklch(0.75 0.18 120)`（绿）
- accent 只用于：标题底色块、封底装饰线、分隔符

不要从照片取色——zine 的 accent 应该和人造荧光色接近。

## 字体

- 标题：无衬线压缩字体 `"Arial Narrow"` / `"Impact"` / `"Helvetica Neue"` condensed 或 `"Noto Sans SC"` compressed
- 正文：系统衬线 `"Times New Roman"` / `"STSong"`，单栏密集
- 引用/标签：`"Courier New"` / `"SF Mono"`
- 不要 Web font——用 system stack 的"复印机质感"

## 照片处理

- 模拟复印机效果：`filter: contrast(1.15) saturate(0.85) brightness(1.05)`
- 照片边框：`1px solid oklch(0.85 0 0)`（灰虚线框，模拟裁切标记）
- 随机轻微旋转
- 照片可以切成非矩形吗？用 `clip-path: polygon()` 模拟剪刀裁切
- 允许图片和文字重叠：`mix-blend-mode: multiply` 或文字衬白底

## 地图

不需要 Leaflet。如果需要路线，用手绘风格 CSS 折线（`border-bottom: 2px dashed` 折行）。纯文字路线 + 时间戳列表。

## 动画

- 不需要入场动画
- 唯一动效：拼贴页面的照片 hover 时放大到 `scale(1.02)`，持续 0.2s

## 严禁

- ❌ 平滑渐变 / 毛玻璃 / 高级阴影
- ❌ 灯箱 / 图片浏览模式
- ❌ 完美对齐的网格
- ❌ Leaflet 地图
- ❌ 手写体 / 楷体（太温柔）
- ❌ 留白/空行/呼吸感——zine 要填满

## 推荐理由

选这个方向当且仅当：用户的照片是随性的、不是认真拍的、旅行本身是和朋友一起的松散活动。如果用户说"不想太正式"、"想要点态度"——这是那个方向。

<!--META-->
name: Zine 小志
name_en: zine
vibe: 复印感、拼贴、逆向
layout_type: collage
has_map: false
has_lightbox: false
has_narrative: true
tags: 拼贴,DIY,实验,快闪
best_for: 短途旅行·音乐节·朋友逛街
