# 《苟住!》第1集 — H3 官方 Ref2VA 提示词包（完整版 8 镜 · v3 风格统一升级）

> 配套剧本：苟住_快手版_第1集剧本.md
> 引擎：**MiniMax H3（H3-Base-Ref2VA 全参考模式）** — 官方规范 2026-08-13 开源
> 云端工作流：U4（MiniMaxH3ReferenceToVideo），CLIP 必须 int4，逐镜串行提交
> 参数：832×1472（竖屏9:16）/ 24fps / 每镜 5-8s / seed 固定
> 参考图重排铁律：**苟仔ID → 醒姐ID → 场景图**（图1权重最高）
> 配音方案 v2：台词保留 `<d>[Chinese] 原文</d>`（H3 原生语音+口型）；若云端 U4 工作流支持音频参考，提交 `<Audio 1/2/3>` 音色文件锁角色音色（满足音色铁律）；若不支持则走 H3 默认音色（需用户拍板）
> **v2 升级（2026-08-14）**：跨镜连贯性三管齐下 = 时序光照表 + 尾帧传图链式生成 + 动作衔接声明
> **v3 升级（2026-08-14）**：风格统一三保险 = 全参考图同风格声明 + 强化负面 + 全局风格句升级（见「风格统一控制」章节；⚠️ 视觉实测：醒姐ID与3张场景图为半写实渲染风，苟仔ID为扁平卡通风，风格分裂风险已标记）

---

## 参考资产映射（全镜通用）

| 标签 | 文件 | 用途 |
|------|------|------|
| `<Picture 1>` | 角色图片/gou_zai_ID.png | 苟仔 ID 基准图 |
| `<Picture 2>` | 角色图片/xing_jie_ID.png | 醒姐 ID 基准图 |
| `<Picture 3>` | 场景图片/苟住_场景测试1_废弃街道.png | 场景1 废弃街道（镜头1-5） |
| `<Picture 4>` | 场景图片/scene2_store.png | 场景2 便利店（镜头6） |
| `<Picture 5>` | 场景图片/scene3_rooftop.png | 场景3 天台星空（镜头7-8） |
| `<Audio 1>` | 音色配音/苟住_音色_gouzai.wav | 苟仔音色（音频参考，锁音色+口型） |
| `<Audio 2>` | 音色配音/苟住_音色_xingjie.wav | 醒姐音色（音频参考，锁音色+口型） |
| `<Audio 3>` | 音色配音/苟住_音色_pangbai.wav | 旁白音色（音频参考，镜头8旁白） |

**全局风格句（每镜 detailed_description 开头必带）**：
```
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
```

**全局负面（U4 工作流负面节点）**：
```
worst quality, blurry, jittery, distorted, inconsistent appearance, extra fingers, deformed hands, text on screen, subtitles, watermark, low resolution, mutated face, 3D render, CGI, realistic render, photorealistic, serious anime style, detailed realistic shading, cel shading mismatch, soft airbrush shading, gradient shading, painterly texture, mixed art style, style drift, semi-realistic, 2.5D render, anime shading, glossy plastic look
```

---

## ⭐ 跨镜连贯性控制（v2 升级核心，2026-08-14）

> H3 Ref2VA 是 8 次独立生成，连贯性 = 参考图锚定 + 时序光照声明 + 尾帧传图三管齐下。

### A. 时序光照表（每镜 prompt 头部必须带光照声明，防跳光）

| 镜头 | 时间 | 光照声明（写入 detailed_description 开头） |
|------|------|------|
| 1-5 | 白天阴天 | overcast daylight, consistent soft grey sky light, same lighting as previous shot |
| 6 | 白天（室内） | dim warm indoor lighting, consistent with the overcast daylight outside |
| 7-8 | 夜晚 | night scene, cool blue moonlight, starry sky, consistent night lighting |

> ⚠️ 光照声明 = **所有镜头的详细描述里都写全光照状态**，不是只在第一镜写。写"same lighting as previous shot"建立显式连续。

### B. 尾帧传图链式生成（v2 核心方案！）

**原理**：每镜生成完后 ffmpeg 抽取最后一帧 → 作为下一镜的第一张参考图（权重最高）→ H3 从上一镜的**实际画面**延续，而非从零猜。

**参考图提交槽位规则（每镜）：**
```
输入1 = 上一镜尾帧（权重最高，画面延续锚点）← 镜头1 无尾帧，用场景图替代
输入2 = 苟仔ID（角色锁）
输入3 = 醒姐ID（双人镜才加，单人镜不加）
输入4 = 场景图（画风/环境锁）
```

**执行步骤：**
```
镜1 → 生成 → ffmpeg 抽尾帧 shot1_tail.png → 镜2 输入1=shot1_tail.png
镜2 → 生成 → 抽尾帧 shot2_tail.png → 镜3 输入1=shot2_tail.png
...（每镜如此）
```

**prompt 中的尾帧锚定写法（每镜 subject_definitions 开头加一行）：**
```
<Picture T> is the final frame of the previous shot, showing the exact last composition and lighting state to continue from.
```
**并在 summary/detailed_description 加衔接句：**
```
The target video continues directly from <Picture T>: same characters, same position, same lighting, same camera distance, seamless continuity.
```

### D. 风格统一控制（v3 新增，2026-08-14）

> ⚠️ 视觉实测结论：苟仔ID=扁平卡通 ✅；醒姐ID + 3张场景图=半写实渲染风 ⚠️。参考图风格分裂是画面漂移的最大风险源。

**每镜三保险（已写入全部 8 镜）：**
1. **全参考图同风格声明**（subject_definitions 内加一行）：
```
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
```
2. **强化负面**：cel shading mismatch, soft airbrush shading, gradient shading, painterly texture, mixed art style, style drift, semi-realistic, 2.5D render, anime shading, glossy plastic look（已并入全局负面）
3. **强化风格句**：每镜 detailed_description 开头风格句已升级为「must exactly match the reference images + NO gradients / NO airbrush / NO 3D / NO painterly」

**治本方案（云端开机后执行）— 风格自举：**
用 H3 的 FL2VA/T2VA 模式，以苟仔ID为风格锚，让 H3 重新生成风格统一的：
- 醒姐 ID 新图（flat 2D cartoon 版）
- 场景1/2/3 新图（flat 2D cartoon 版）
→ 全部参考图风格天然统一（H3 自己出的），v3 提示词包直接复用，无需改 prompt。

### C. 动作/空间衔接声明（防动作跳变）

跨镜动作连续时（如镜头2 醒姐冲来 → 镜头3 她站在旁边），**后一镜 prompt 显式写承接**：
```
This shot continues the scene from the previous shot: <Subject 2> has just run in from the right and is now standing beside <Subject 1>.
```

> ⚠️ 3 个场景切换点（镜头5→6 街道→便利店、镜头6→7 便利店→天台）是**剧本设计的场景跳变**，尾帧传图在场景切换处**不传场景尾帧**（否则 H3 会延续旧场景），只传角色尾帧+新场景图。

---

## 镜头 1（5s）开场即梗 — 苟仔躺平

**参考图提交**：Picture 1（苟仔ID）+ Picture 3（废弃街道）← 首镜无尾帧，场景图占输入1位

```text
subject_definitions:
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
<Subject 1> is the chubby cute Q-version boy in <Picture 1>, with a single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly.
<Subject 3> is the abandoned city street in <Picture 3>, with cracked asphalt road, collapsed cartoon buildings, broken streetlight, a few stylized weeds, overcast sky.

summary:
[reference generation] The target video shows <Subject 1> lying relaxed in the middle of <Subject 3>, lazily eating imaginary food, declaring the end of the world is no big deal.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - the chubby Q-version body, ahoge, buck teeth, flip-flops, and belt lunchbox are all retained.
<Subject 3> (appears in [Shot 1]): fully_preserved - the cracked road, collapsed buildings, and overcast sky are retained.

detailed_description:
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
Lighting: overcast daylight, consistent soft grey sky light, no hard shadows.
[Shot 1] An establish shot of <Subject 3>, the abandoned city street. <Subject 1> (S1), a chubby cute Q-version boy with an ahoge hair strand, front buck teeth and flip-flops, lies on his back in the middle of the cracked road, legs crossed, hands behind his head, eyes closed, relaxed and lazy, munching on imaginary food with a silly grin, a lunchbox hanging from his belt. He says with a relaxed lazy tone, <d>[Chinese] 末日第一天,问题不大!</d> The camera slowly pushes in with small amplitude at slow speed toward him. Overcast sky, ruined cartoon buildings in the background.

overall_soundscape:
A quiet post-apocalyptic city atmosphere, faint wind blowing over the empty street, distant rubble settling.

non_diegetic_music:
Light comedic ukulele plucking, bouncy and carefree.
```

---

## 镜头 2（5s）醒姐崩溃

**参考图提交**：Picture T（镜1尾帧 shot1_tail.png）+ Picture 1（苟仔ID）+ Picture 2（醒姐ID）+ Picture 3（废弃街道）

```text
subject_definitions:
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
<Picture T> is the final frame of the previous shot, showing the exact last composition and lighting state to continue from: <Subject 1> lying on the cracked road.
<Subject 1> is the chubby cute Q-version boy in <Picture 1>, with a single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly.
<Subject 2> is the tall thin paper-thin girl in <Picture 2>, with three strands of side bangs, dark circles under her eyes, holding a broom, tired but sharp expression.
<Subject 3> is the abandoned city street in <Picture 3>, with cracked asphalt road, collapsed cartoon buildings, broken streetlight, a few stylized weeds, overcast sky.

summary:
[reference generation] The target video continues directly from <Picture T>. <Subject 2> runs furiously toward the lying <Subject 1> with her broom, shouting that a meteorite just crashed beside him, while he stays unbothered.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - chubby body, ahoge, buck teeth, flip-flops, belt lunchbox retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - tall thin body, three side bangs, dark circles, broom in hand retained.
<Subject 3> (appears in [Shot 1]): fully_preserved - cracked road, collapsed buildings, overcast sky retained.

detailed_description:
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
Lighting: overcast daylight, consistent soft grey sky light, same lighting as the previous shot, no hard shadows.
[Shot 1] A medium shot on the abandoned city street. <Subject 2> (S2), a tall thin paper-thin girl with three strands of side bangs and dark circles under her eyes, runs toward camera holding a broom, furious and exasperated, her hair flying. She points the broom at the face of <Subject 1> (S1), the chubby boy still lying on the road, and shouts with a shrill desperate voice, <d>[Chinese] 你醒醒吧!陨石都砸到你脚边了!</d> Behind them a small meteorite crashes into the road half a meter away with a small explosion of dust. The boy stays unbothered with a silly grin, eyes closed. The camera follows her running movement with medium amplitude at medium speed.

overall_soundscape:
Rapid running footsteps, a small boom of the meteorite impact, dust and gravel scattering, the girl's panting.

non_diegetic_music:
Fast comedic chase music, bouncy brass stabs.
```

---

## 镜头 3（6s）饭盒梗

**参考图提交**：Picture T（镜2尾帧 shot2_tail.png）+ Picture 1（苟仔ID）+ Picture 2（醒姐ID）+ Picture 3（废弃街道）

```text
subject_definitions:
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
<Picture T> is the final frame of the previous shot, showing the exact last composition and lighting state to continue from.
<Subject 1> is the chubby cute Q-version boy in <Picture 1>, with a single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly.
<Subject 2> is the tall thin paper-thin girl in <Picture 2>, with three strands of side bangs, dark circles under her eyes, holding a broom, tired but sharp expression.
<Subject 3> is the abandoned city street in <Picture 3>, with cracked asphalt road, collapsed cartoon buildings, broken streetlight, a few stylized weeds, overcast sky.

summary:
[reference generation] The target video continues directly from <Picture T>. It shows <Subject 1> sitting up calmly, wiping dust off his belt lunchbox without opening it, defending his optimism with silly logic while <Subject 2> facepalms in disbelief.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - chubby body, ahoge, buck teeth, flip-flops, belt lunchbox retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - tall thin body, three side bangs, dark circles, broom retained.
<Subject 3> (appears in [Shot 1]): fully_preserved - cracked road and ruined buildings retained.

detailed_description:
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
Lighting: overcast daylight, consistent soft grey sky light, same lighting as the previous shot, no hard shadows.
[Shot 1] A medium shot, two characters in frame on the abandoned street. <Subject 1> (S1), the chubby boy, sits up slowly with a calm lazy expression, takes the lunchbox from his belt, wipes dust off it with his sleeve but does not open it. He grins with an easygoing tone and says, <d>[Chinese] 问题不大!陨石又不是冲我来的,它冲地来的,我俩都是受害者</d> <Subject 2> (S2), the tall girl standing beside him, facepalms hard and mutters with a stunned, almost convinced tone, <d>[Chinese] 你这逻辑……居然有点道理?!</d> Static camera, both characters fully in frame.

overall_soundscape:
Quiet street, faint wind, the boy wiping dust off the lunchbox, the girl's exasperated sigh.

non_diegetic_music:
Playful comedic pizzicato strings, light and silly.
```

---

## 镜头 4（7s）丧尸歪理

**参考图提交**：Picture T（镜3尾帧 shot3_tail.png）+ Picture 1（苟仔ID）+ Picture 2（醒姐ID）+ Picture 3（废弃街道）

```text
subject_definitions:
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
<Picture T> is the final frame of the previous shot, showing the exact last composition and lighting state to continue from.
<Subject 1> is the chubby cute Q-version boy in <Picture 1>, with a single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly.
<Subject 2> is the tall thin paper-thin girl in <Picture 2>, with three strands of side bangs, dark circles under her eyes, holding a broom, tired but sharp expression.
<Subject 3> is the abandoned city street in <Picture 3>, with cracked asphalt road, collapsed cartoon buildings, broken streetlight, a few stylized weeds, overcast sky.

summary:
[reference generation] The target video continues directly from <Picture T>. It shows a shambling zombie horde approaching in the distance, while <Subject 1> confidently raises his hand to stop them and explains his absurd theory that zombies are afraid of mirrors because they are too ugly.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - chubby body, ahoge, buck teeth, flip-flops retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - tall thin body, three side bangs, dark circles, broom retained.
<Subject 3> (appears in [Shot 1]): partially_preserved - the street and ruined buildings retained, zombies newly added in the distance.

detailed_description:
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
Lighting: overcast daylight, consistent soft grey sky light, same lighting as the previous shot, no hard shadows.
[Shot 1] A wide shot on the abandoned street. A group of shambling cartoon zombies with torn clothes and blank eyes appears in the distance, slowly walking toward camera with dragging steps. <Subject 1> (S1), the chubby boy, stands in front of <Subject 2> (S2), the tall girl with the broom, raises his hand in a stop gesture with a confident grin and says, <d>[Chinese] 别慌!听说丧尸怕镜子——</d> <Subject 2> tilts her head and asks with curiosity, <d>[Chinese] 真的?</d> <Subject 1> replies with a sly smug grin, <d>[Chinese] 对啊,他们一照镜子,发现自己这么丑,直接吓死自己!</d> Camera static, zombies slowly approaching in the background, the two characters in the foreground.

overall_soundscape:
Dragging footsteps of the zombie horde, low distant moans, the boy's confident voice, the girl's doubtful question.

non_diegetic_music:
Tense comedic suspense strings, then a silly slide-whistle accent on the punchline.
```
# 《苟住!》第1集 — H3 官方 Ref2VA 提示词包（下半：镜头5-8）

> 接上半部（镜头1-4），参考资产映射与全局风格句见上半部开头

---

## 镜头 5（8s）镜子反转

**参考图提交**：Picture T（镜4尾帧 shot4_tail.png）+ Picture 1（苟仔ID）+ Picture 2（醒姐ID）+ Picture 3（废弃街道）

```text
subject_definitions:
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
<Picture T> is the final frame of the previous shot, showing the exact last composition and lighting state to continue from.
<Subject 1> is the chubby cute Q-version boy in <Picture 1>, with a single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly.
<Subject 2> is the tall thin paper-thin girl in <Picture 2>, with three strands of side bangs, dark circles under her eyes, holding a broom, tired but sharp expression.
<Subject 3> is the abandoned city street in <Picture 3>, with cracked asphalt road, collapsed cartoon buildings, broken streetlight, a few stylized weeds, overcast sky.

summary:
[reference generation] The target video continues directly from <Picture T>. It shows the lead zombie stopping at a broken shop window with reflective glass, staring at its own reflection, covering its face in shock and walking away, while the two heroes react in disbelief and triumph.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - chubby body, ahoge, buck teeth, flip-flops retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - tall thin body, three side bangs, dark circles, broom retained.
<Subject 3> (appears in [Shot 1]): partially_preserved - the street retained, a broken shop window with reflective glass added.

detailed_description:
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
Lighting: overcast daylight, consistent soft grey sky light, same lighting as the previous shot, no hard shadows.
[Shot 1] A wide shot on the abandoned street. The lead cartoon zombie, with torn clothes and blank eyes, reaches a broken shop window with reflective glass, stops, and stares at its own reflection. Its blank eyes widen in shock, it covers its face with both hands and turns away, shuffling off in disgust. <Subject 2> (S2), the tall girl, watches with wide eyes and stammers in disbelief, <d>[Chinese] 居、居然有用?!</d> <Subject 1> (S1), the chubby boy, crosses his arms proudly with a smug grin and says, <d>[Chinese] 问题不大!我就说嘛——</d> Camera holds steady, the zombie retreating in the background, the two characters reacting in the foreground.

overall_soundscape:
The zombie's dragging footsteps stopping, a surprised grunt, the girl's stammering voice, the boy's proud voice.

non_diegetic_music:
A comedic "record scratch" moment of silence, then a triumphant goofy brass fanfare.
```

---

## 镜头 6（7s）辣条战略物资

**参考图提交**：Picture T（镜头5尾帧（角色锚定））+ Picture 1（苟仔ID）+ Picture 2（醒姐ID）+ Picture 4（便利店）

```text
subject_definitions:
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
<Picture T> is the final frame of the previous shot, showing the exact last composition and lighting state to continue from. Note: the target shot takes place in a NEW location, so <Picture T> anchors only the characters' appearance and poses, not the background.
<Subject 1> is the chubby cute Q-version boy in <Picture 1>, with a single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly.
<Subject 2> is the tall thin paper-thin girl in <Picture 2>, with three strands of side bangs, dark circles under her eyes, holding a broom, tired but sharp expression.
<Subject 4> is the empty convenience store interior in <Picture 4>, with bare cartoon shelves, one packet of spicy snacks on the counter, broken glass door, dim warm light.

summary:
[reference generation] The target video continues directly from <Picture T>. It shows the two characters inside the empty convenience store, where <Subject 1> snatches the last packet of spicy snacks and declares it strategic supplies with absurd seriousness.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - chubby body, ahoge, buck teeth, flip-flops retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - tall thin body, three side bangs, dark circles, broom retained.
<Subject 4> (appears in [Shot 1]): fully_preserved - bare shelves, spicy snack packet on counter, dim warm light retained.

detailed_description:
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
Lighting: dim warm indoor lighting inside the convenience store, consistent with the overcast daylight outside, soft fluorescent glow, no hard shadows.
[Shot 1] A medium shot inside the empty convenience store. Bare shelves line the walls, one packet of spicy snacks sits on the counter, dim flickering warm light. <Subject 1> (S1), the chubby boy, snatches the packet and hugs it protectively to his chest with a serious determined face. <Subject 2> (S2), the tall girl, protests with her hands on her hips in exasperation, <d>[Chinese] 就剩一包辣条了你还要抢?</d> <Subject 1> replies with utmost seriousness and a deadpan tone, <d>[Chinese] 辣条是战略物资!末日它不辣,咱们怎么扛?</d> Camera medium static, both characters in frame.

overall_soundscape:
Dim store interior hum, the packet rustling as the boy snatches it, the girl's exasperated sigh.

non_diegetic_music:
Quirky comedic marimba, playful and bouncy.
```

---

## 镜头 7（10s）灵魂瞬间

**参考图提交**：Picture T（镜头6尾帧（角色锚定））+ Picture 1（苟仔ID）+ Picture 2（醒姐ID）+ Picture 5（天台星空）

```text
subject_definitions:
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
<Picture T> is the final frame of the previous shot, showing the exact last composition and lighting state to continue from. Note: the target shot takes place in a NEW location, so <Picture T> anchors only the characters' appearance and poses, not the background.
<Subject 1> is the chubby cute Q-version boy in <Picture 1>, with a single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly.
<Subject 2> is the tall thin paper-thin girl in <Picture 2>, with three strands of side bangs, dark circles under her eyes, holding a broom, tired but sharp expression.
<Subject 5> is the rooftop at night in <Picture 5>, with a big starry sky, ruined cartoon city skyline in the distance, gentle moonlight, cool blue palette.

summary:
[reference generation] The target video continues directly from <Picture T>. It shows the two characters sitting side by side on the rooftop at night, sharing a rare sincere moment about what they are living for, ending with the boy's signature optimism.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - chubby body, ahoge, buck teeth, flip-flops retained.
<Subject 2> (appears in [Shot 1]): fully_preserved - tall thin body, three side bangs, dark circles retained.
<Subject 5> (appears in [Shot 1]): fully_preserved - starry sky, ruined skyline, gentle moonlight, cool blue palette retained.

detailed_description:
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
Lighting: night scene, cool blue moonlight, starry sky, consistent night lighting, gentle blue rim light on the characters.
[Shot 1] A medium shot on the rooftop at night, starry sky above, ruined city skyline behind, gentle moonlight, cool blue tones. <Subject 1> (S1), the chubby boy, sits cross-legged looking up at the stars, unusually calm and quiet, and asks softly with a genuine tone, <d>[Chinese] 姐,你说……末日了,咱们图啥?</d> <Subject 2> (S2), the tall girl, sits beside him, pauses for a moment, sighs gently and answers with a warm tired tone, <d>[Chinese] 图……明天还能一起抢辣条呗</d> <Subject 1> turns to her and grins widely, his usual silly optimism returning, <d>[Chinese] 那问题不大!</d> The camera slowly pulls back with small amplitude at slow speed, a touching quiet moment.

overall_soundscape:
Gentle night breeze, distant ruins creaking softly, two calm voices under the stars.

non_diegetic_music:
Soft warm acoustic guitar, gentle and nostalgic, swelling slightly on the final line.
```

---

## 镜头 8（6s）结尾钩子

**参考图提交**：Picture T（镜7尾帧 shot7_tail.png）+ Picture 5（天台星空）为主，可加 Picture 1 + Picture 2（两人背影）

```text
subject_definitions:
All reference pictures share the same flat 2D cartoon style: flat cel shading, bold outlines, no gradients, no realistic rendering.
<Picture T> is the final frame of the previous shot, showing the exact last composition and lighting state to continue from.
<Subject 1> is the chubby cute Q-version boy in <Picture 1>, with a single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly.
<Subject 2> is the tall thin paper-thin girl in <Picture 2>, with three strands of side bangs, dark circles under her eyes, holding a broom, tired but sharp expression.
<Subject 5> is the rooftop at night in <Picture 5>, with a big starry sky, ruined cartoon city skyline in the distance, gentle moonlight, cool blue palette.

summary:
[reference generation] The target video continues directly from <Picture T>. It shows the two characters as small silhouettes sitting on the rooftop edge against the starry sky and ruined city, as a narrator teases bigger trouble tomorrow.

retention_analysis:
<Subject 1> (appears in [Shot 1]): partially_preserved - visible as a small silhouette, key features simplified at distance.
<Subject 2> (appears in [Shot 1]): partially_preserved - visible as a small silhouette, key features simplified at distance.
<Subject 5> (appears in [Shot 1]): fully_preserved - starry sky, ruined skyline, cool blue palette retained.

detailed_description:
The target video is in a flat 2D cartoon sticker meme style, simple shapes, bold clean outlines, bright flat colors, exaggerated comedic expressions, chibi big-head proportions, consistent character design. The art style must exactly match the reference images: flat cel shading, NO gradients, NO soft airbrush shading, NO 3D render look, NO painterly texture, NO realistic lighting, characters and background drawn in the same flat cartoon manner.
Lighting: night scene, cool blue moonlight, starry sky, consistent night lighting, same as the previous shot.
[Shot 1] An extreme wide shot from behind. <Subject 1> and <Subject 2> sit side by side on the rooftop edge, small silhouettes against the big starry sky and the ruined city skyline. A narrator says in an off-screen voiceover with a teasing dramatic tone, <d>[Chinese] 明天……还有更大的麻烦</d> The camera slowly dollies back with small amplitude at slow speed, revealing the full ruined skyline under the night sky. The screen holds for a moment on the vast starry night. Night scene, cool blue tones, ending shot.

overall_soundscape:
Quiet night wind over the ruins, the faint distant sound of something rumbling on the horizon.

non_diegetic_music:
A mysterious low synth drone builds slowly, ending on an unresolved note for the cliffhanger.
```

---

## 七、H3 配音方案说明（用户定稿前需确认）

H3 与 LTX 最大不同：**H3 原生支持语音生成**（`<d>[Chinese] 原文</d>` 会生成带情绪的语音+口型），可一步出片。

| 方案 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| **A. H3 原生语音** | 提示词 `<d>` 直接生成 | 口型完美同步、零后期 | 音色不可控（非苟仔/醒姐固定音色） |
| **B. 音色克隆后期（原流程）** | 视频生成时 `<d>` 仅驱动口型，成片用 Qwen3-TTS VoiceClone 音色文件配音 | 音色锁定不漂移（用户铁律） | 口型可能略不同步 |

> ⚠️ 用户铁律（2026-08-10）：人物对话配音必须用音色文件克隆。若 H3 原生语音音质/音色达标，可评估放宽；否则默认方案 B——视频 `<d>` 保留用于口型与情绪，成片换音色克隆配音。

## 八、渲染清单

| 镜头 | 时长 | 参考图 | 场景 |
|------|------|--------|------|
| 1 | 5s | 苟仔ID + 街道 | 场景1 |
| 2 | 5s | 苟仔ID + 醒姐ID + 街道 | 场景1 |
| 3 | 6s | 苟仔ID + 醒姐ID + 街道 | 场景1 |
| 4 | 7s | 苟仔ID + 醒姐ID + 街道 | 场景1 |
| 5 | 8s | 苟仔ID + 醒姐ID + 街道 | 场景1 |
| 6 | 7s | 苟仔ID + 醒姐ID + 便利店 | 场景2 |
| 7 | 8s | 苟仔ID + 醒姐ID + 天台 | 场景3 |
| 8 | 6s | 天台 + (可选)双角色 | 场景3 |
| 合计 | **52s 视频** | — | 8 镜 |

> 60s 成片可加 2 镜补足（如丧尸群正面特写 + 辣条包装特写），或保持 52s 配片头片尾。
> 渲染纪律：CLIP int4 → 逐镜串行 → 先 1 镜验收 → 批量 → 抽帧查字幕/角色复制 → 逐镜重渲坏的。
