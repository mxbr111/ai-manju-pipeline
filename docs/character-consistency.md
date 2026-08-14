# 角色一致性方案（Character Consistency Playbook）

> 漫剧最痛的问题：镜头与镜头之间角色"变脸"、风格漂移、双人镜复制角色、画面出现字幕。
> 本方案经过《苟住！》第一集实战验证，四层叠加根治。

## 第 0 层：参考图风格必须统一（先于一切）

**风格分裂是变脸的根因。** 实测：角色 ID 图是扁平 2D 卡通、场景图是半写实渲染 → 视频必然在两种风格间漂移，被用户两次打回"太写实"。

**检查清单（任何新参考图必须过）**：
1. 本地视觉模型（qwen2.5vl:7b，零成本）检查每张图：A 扁平卡通 / B 半写实 / C 写实
2. 角色图和场景图必须同属一个风格档位
3. 风格分裂 → 不硬用 → 用风格锚定重出（见第 4 节）

## 第 1 层：参考图重排（H3 Ref2VA / LTX MSR 通用）

多参考图工作流的输入顺序 = 权重顺序，**图 1 权重最高**：

```
角色ID基准图（权重最高） → 姿态参考 → 人设 Sheet → 场景基准 → 场景细节
```

- 每角色固定 1 张 ID 基准图，全剧不换
- 双人/多人镜：**所有在场角色都必须有参考图**（S03 漏挂小雨 → 小雨显老走样）
- Sheet 参考图**必须裁掉底部文字标签**（LTX 会学样生成字幕条）

## 第 2 层：提示词约束

### 全局风格句
```
All reference pictures share the same flat 2D cartoon style.
must exactly match the reference images.
NO gradients / airbrush / 3D render / painterly.
```

### 数量锁定（防复制角色）
```
exactly two human characters + one zombie, do not duplicate any character
```
负面词：`duplicate character, cloned character, two same person`

### 幼态角色年龄强化（防显老）
```
tiny 10-year-old child, babyish face, big bright innocent eyes
```

### 表情克制（防夸张崩脸）
```
normal natural facial proportions, natural calm expression
```
负面词：`exaggerated expression, distorted face, oversized eyes`
少用 shouting / screaming 等强动作词。

### 时序光照（跨镜一致）
每镜 prompt 必写当前光照时段（overcast daylight / 室内暖光 / 夜晚月光），全局统一。

## 第 3 层：参数与种子

- CFG：单人 3.2 / 双人 3.0 / 空镜 3.4
- Seed：固定 base，变化 +1~+3，**禁随机**
- 参考图统一 1024 长边，开 `enable_ref_emb_cache`
- 多图参考**不要并行加载**（48GB 显存也扛不住，串行）

## 第 4 层：尾帧链式生成（跨镜衔接终极方案）

每镜生成 → ffmpeg 抽尾帧 → 作为下一镜输入图 1（权重最高）→ prompt 加 `<Picture T>` 定义 + `continues directly from` 前缀声明。

- 场景跳变镜（换场景）只锚角色不加 Note 声明
- 这是官方 Ref2VA 分镜锚能力的应用，需首镜实测验证

## 后期兜底

- 0.3-0.5s dissolve 转场
- 统一 LUT
- 声音桥接（配音连续性）

## 自动验收（check_char_consistency.py）

特征检查法（比"是否同一人"可靠，7B 视觉模型可胜任）：
1. 对每张角色参考图跑特征检查 → 参考特征集（呆毛/大门牙/人字拖…）
2. 视频抽帧（开头/中/尾）→ 每帧跑同一检查
3. 命中率 = 帧特征集 ∩ 参考特征集 / 参考特征集
4. ≥80% 通过 / 60-80% 警告 / <60% 失败
