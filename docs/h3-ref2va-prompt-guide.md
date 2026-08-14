# H3 Ref2VA 六段式提示词规范

> 来源：MiniMax-AI/MiniMax-H3 官方仓库 + 官方 h3-prompt-writing 技能（ref-en.txt）
> MiniMax H3 是漫剧主力引擎（2026-08-14 定稿），LTX-2.3 降级为备用。
> 全片 8 镜 52s 实战验证。

## 六段式结构（Ref2VA，每镜必写）

1. **global description**（全局描述：风格/氛围/画风统一）
2. **subject definitions**（主体定义：角色+场景，引用参考图）
3. **detailed description**（详细描述：动作/表情/光线/镜头）
4. **camera**（镜头语言）
5. **audio / <d>**（台词走音频通道，不烧字幕）
6. **negative prompt**（负面词）

## 核心规则

### 风格统一（第一优先级）
- 每镜 `subject_definitions` 加：`All reference pictures share the same flat 2D cartoon style`
- 全局风格句升级：`must exactly match the reference images + NO gradients/airbrush/3D/painterly`
- **参考图风格分裂 → 视频必漂移**（角色图扁平、场景图写实 = 灾难）
  - 治本方案：用 H3 FL2VA/T2VA 以角色 ID 图为风格锚，重出全部场景图（风格自举统一）

### 台词走音频通道
- `<d>[Chinese]台词原文</d>` — H3 原生音频通道，不会烧字幕（与 LTX 相反）
- 台词文本必须规范化：**特殊标点（省略号/顿号/?!连用）会导致 Qwen3-TTS 语音重复含糊卡死**

### 跨镜连贯性（三管齐下）
1. **时序光照表**：每镜必写光照时段（镜1-5 overcast daylight / 镜6 室内暖光 / 镜7-8 夜晚月光），`detailed_description` 必写
2. **尾帧传图链式生成**：每镜生成 → ffmpeg 抽尾帧 → 作为下一镜输入图 1（权重最高），prompt 加 `<Picture T>` 定义 + `continues directly from` 前缀声明；场景跳变镜（换场景）只锚角色不加 Note 声明
3. **动作衔接声明**：明确上一镜结束状态 → 本镜延续

### 参考图（Ref2VA 模式）
- 参考图 **≤9 张**
- 顺序 = 权重：角色 ID → 姿态 → 人设 Sheet → 场景基准 → 场景细节
- 双人镜所有在场角色必须有参考图

## 参数基准（云端 3090-48G）

- 引擎：MiniMax H3 Ref2VA（U4 工作流 = H3 Ref2VA 模式）
- CLIP：qwen3vl-32B **int4**（int8 会永久卡死 >20min GPU 0%）
- 单镜 ~11min（编码 ~1min + 采样 ~8min + VAE/保存 ~2min）
- **逐镜提交、出片后再提交下一镜**（严禁批量排队 → 模型 stage 竞争爆显存卡死）
- 全片 ~2.5h（13 镜串行）

## 负面词模板（H3 版）

```
style drift, semi-realistic, 2.5D render, gradients, airbrush, 3D render, painterly,
duplicate character, cloned character, two same person, distorted face, oversized eyes,
exaggerated expression, no on-screen text, no subtitles, no words
```
