# LTX-2.3 官方提示词规范（落地版）

> 来源：Lightricks/LTX-2 README + ltx.io/blog/prompting-guide-for-ltx-2（官方规范全文）
> 这是漫剧 LTX 工作流的提示词结构标准，逐镜提示词按此生成。

## 官方结构：单段流畅叙述

- **现在时**，**主动作开头**
- **六要素**按顺序：
  1. Establish shot（建立镜头/场景）
  2. Set scene（交代环境）
  3. Define characters（定义角色）
  4. Action（动作）
  5. Camera（运镜）
  6. Audio（声音）
- **≤200 词**，4-8 句
- 对白引号内嵌：`Name says in Chinese: 「...」`

## 漫剧落地规则

### 双人镜（防混淆）
- `<Picture N> shown in` → 直接写角色名
- 例：`The first picture shows 苟仔. The second picture shows 醒姐. They look at each other.`

### 删除项（v3 起废弃）
- `preserving` 子句（LTX 自己保持一致性，不用写）
- `S(N)` 标签
- 破坏叙述流畅性的分段

### 台词与字幕（铁律，见 subtitle-standard.md）
- **提示词含台词文本必出画面字幕**（`no on-screen text` 声明挡不住）
- 对白镜去掉说话/口型描述，只写动作+氛围
- 台词保留在剧本，配音+字幕后期加

## 参数（LTX-2.3 22B distilled 官方参数）

| 档位 | 分辨率 | steps | sampler | CFG |
|---|---|---|---|---|
| 48G 满血 | 832×1472 / 25fps / 5s | 32 | dpmpp_2m | 单人 3.2 / 双人 3.0 / 空镜 3.4 |
| 24G 降配 | 768×1344 | 32 | dpmpp_2m | 同上 |

- shift：人物 1.9 / 空镜 2.1；flow_shift 1.6；noise_shift 1.0
- Seed 固定 base，变化 +1~+3 禁随机
- 模型 bf16 加载（3090 不原生支持 FP8 会噪点崩脸）
- VAE 分片关闭

## 负面词模板（统一）

```
duplicate character, cloned character, two same person, exaggerated expression,
distorted face, oversized eyes, no speech, no dialogue, no writing anywhere in the image,
no subtitles, no words, no on-screen text, style drift, semi-realistic, 2.5D render
```
