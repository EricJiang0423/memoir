# demo 输入照片 — 京都（合成图）

这个目录里的 30 张 `IMG_00NN.jpg` **全部由 OpenAI GPT Image 2.0 生成**，是为 memoir skill 的演示而造的合成图：

- 不对应任何真实地点的实拍，不涉及任何真实人物 —— 所以可以放进公开仓库。
- 带有为 demo 设定的合成 EXIF：拍摄时间 2026-03-15 ~ 2026-03-17、京都各处的 GPS 坐标（京都駅 / 京都タワー / 鴨川 / 清水寺 / 産寧坂・二年坂 / 八坂の塔・祇園 / 嵐山竹林 / 渡月橋・桂川 / 嵐電沿线）。
- 用来跑通完整流水线：`extract_photos.py` → `geocode.py` → `cluster.py` → `curate.py` →（Claude 策展 + 叙述 + 现场设计 HTML）→ `build_diary.py`。

对应的成品：[`demos/kyoto-3-days.diary.html`](../../kyoto-3-days.diary.html) · 在线预览：https://ericjiang0423.github.io/memoir/

> 注意：这是 **demo 专用**的合成数据。真实用户跑 memoir 时用的是自己的真实照片，照片字节绝不离开本机（只有 GPS 坐标会发往 Nominatim 反查地名）。
