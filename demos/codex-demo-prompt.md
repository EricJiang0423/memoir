# Codex Demo Prompt: 用 GPT-image-2 生成旅行照片 → 跑 memoir skill

将此 prompt 发送给 Codex（或任何支持 tool-use + 图像生成的 agent），
它会自动生成一组带元数据的虚拟旅行照片，然后调用 memoir skill 生成日记 HTML。

---

## Prompt

```
你需要在本地生成一组虚拟旅行照片，然后用 memoir skill 把它们做成一份旅行日记 HTML。

## 第一步：生成照片

用 GPT-image-2 生成 30 张照片，模拟一次「京都三日」的旅行。要求：

1. **照片规格**：JPEG 格式，1024x768 或 3:2 比例，画面自然——像真人用 iPhone 拍的照片，
   不是商业图库风格。不需要太完美：可以有轻微倾斜、自然光过曝、随意的构图。

2. **内容分布**（每天 10 张）：
   - Day 1（2026-03-15）：抵达京都 — 京都站、酒店房间窗外、傍晚的鸭川、便利店晚饭
   - Day 2（2026-03-16）：东山 — 清水寺及周边坂道、二年坂的陶器店、抹茶碗、午后的庭院、
     黄昏时八坂塔的剪影
   - Day 3（2026-03-17）：岚山 — 竹林小径、渡月桥、岚山电车沿途、豆腐料理、离开前的京都站

3. **元数据写入**：每生成一张照片，立即用 exiftool 写入 EXIF 元数据：
   ```bash
   exiftool \
     -DateTimeOriginal="YYYY-MM-DD HH:MM:SS" \
     -GPSLatitude="XX.XXXXXX" \
     -GPSLongitude="XXX.XXXXXX" \
     -GPSLatitudeRef="N" \
     -GPSLongitudeRef="E" \
     /path/to/photo.jpg
   ```
   - 时间：分布在该天的 09:00-21:00 之间，每张间隔至少 5 分钟
   - GPS：使用京都真实坐标范围 — 纬度 34.98-35.02，经度 135.73-135.78
   - Day 1 集中在京都站附近（34.985, 135.758）
   - Day 2 集中在东山/清水寺附近（34.995, 135.780）
   - Day 3 集中在岚山附近（35.010, 135.675）

4. **保存路径**：所有照片保存到 `demos/photos/kyoto/` 目录下，
   文件名为 `IMG_0001.jpg` 到 `IMG_0030.jpg`

## 第二步：运行 memoir skill

照片生成完毕后，运行 memoir skill 的完整流水线：

```bash
# 1. 提取 EXIF
python3 scripts/extract_photos.py --folder demos/photos/kyoto --out raw_photos.json

# 2. 地理编码
python3 scripts/geocode.py --in raw_photos.json --out geocoded_photos.json

# 3. 聚类
python3 scripts/cluster.py --in geocoded_photos.json --out diary_data.json

# 4. 品质预检
python3 scripts/curate.py --in diary_data.json --out curation_manifest.json

# 5. 策展：基于 curation_manifest.json 的指标，手动筛选 15-20 张最佳照片，
#    写入 diary_data.json（移除 reject 的照片，保留 keep）

# 6. 撰写叙述：在 diary_data.json 中填写 trip_summary.title、
#    days[].title、days[].narrative（参考 references/narrative-craft.md）

# 7. 设计 HTML：按 SKILL.md Step 7a 的 huashu-design 范式，
#    现场设计一份 demo HTML，保存到 output/kyoto.diary.draft.html

# 8. 后处理
python3 scripts/build_diary.py \
  --in diary_data.json \
  --html output/kyoto.diary.draft.html \
  --out demos/kyoto-demo.html
```

## 第三步：清理

按 SKILL.md Step 8 的安全清理流程（先列出 → 等用户批准 → 再删除），清理临时文件。

## 注意事项

- 照片质量不用太高——真实旅行照有瑕疵才像真的
- 叙述语言用中文
- HTML 设计选「日式极简」（东方诗意）方向——见 references/diary-design-aesthetics.md
- 最终 demo HTML 放在 `demos/kyoto-demo.html`，方便直接在浏览器打开
```
