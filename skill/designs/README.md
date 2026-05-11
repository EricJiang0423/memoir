# 设计方向池（Design Pool）

memoir 没有固定模板——HTML 每次由 Claude 现场设计。这个目录提供一组**设计方向参考**，每次执行时 agent 从中推荐 2-3 个适合这次旅行的方向，由用户选择后再落地。

## 使用方式

1. Claude 读完 diary_data.json 后，根据旅行气质（城市/节奏/光线/照片情绪）从下方匹配 2-3 个方向
2. 向用户简短推荐（各用一句话说明气质差异）
3. 用户选一个 → Claude 按该方向的 `design.md` 描述现场设计 HTML

## 当前方向总览

| # | 方向 | 气质 | 布局类型 | 适合场景 |
|---|------|------|---------|----------|
| 01 | [大画册](heritage-album.md) | 厚重、典藏、深色底 | `spread` 跨页 | 历史城市、博物馆、人文深度游 |
| 02 | [旅行手帐](traveler-notebook.md) | 手写、毛边、私人感 | `collage` 拼贴 | 独自旅行、田野笔记、公路旅行 |
| 03 | [宽银幕](cinemascope.md) | 电影感、宽幅、叙事 | `slide` 幻灯片 | 自然风光、城市天际线、黄昏夜景 |
| 04 | [暗房](darkroom.md) | 高反差、黑底、粗粝 | `grid` 网格 | 城市夜行、地下音乐、黑白摄影 |
| 05 | [极简白](white-space.md) | 留白、克制、空气感 | `single` 独幅 | 美术馆、寺院、极简建筑、一日散步 |
| 06 | [Zine 小志](zine.md) | 复印感、拼贴、逆向 | `collage` 拼贴 | 实验性旅行、数码过剩、快闪记忆 |


## 高级功能：导入自定义设计方向

通过 `scripts/import_design.py` 可以从本地文件或 GitHub URL 注册新的设计方向：

```bash
# 从本地文件
python3 scripts/import_design.py path/to/my-design.md

# 从 GitHub raw URL
python3 scripts/import_design.py https://raw.githubusercontent.com/user/repo/main/designs/retrowave.md

# 查看已注册的方向及布局类型
python3 scripts/import_design.py --list
```

**导入要求**：
- 设计文件必须包含 9 个必要概念章节（见 `TEMPLATE.md`）
- 文件末尾需包含 `<!--META-->` 元数据块（name / name_en / vibe / layout_type / tags / best_for / has_map / has_lightbox / has_narrative）
- **布局类型必须独一无二**——`import_design.py` 会检查 `layout_type` 不与现有方向重复，确保每个方向有结构差异

**给设计贡献者**：参考现有 design.md 的写法。布局 archetype 是核心——它定义页面的结构流，决定了这个方向读起来像什么。

## 原则

- **方向之间结构必须不同**，不能只是换配色。每个方向有独特的布局 archetype（画册跨页 vs 手帐拼贴 vs 宽银幕横滚）。
- Claude 执行时根据设计方向描述做具体决策，**不复制上次用过的实现**。
- 用户可以拒绝推荐、自己描述想要的气质 → Claude 现场生成方向。
