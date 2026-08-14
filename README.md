# AI 漫剧生产线（AI Manju Pipeline）

> 末日沙雕漫剧《苟住！》从剧本到成片的完整生产管线 —— 角色一致性、视频生成、音色克隆、字幕规范的全链路开源实现。

一套在 **AutoDL 云端 ComfyUI** 上跑通的 AI 竖屏短剧/漫剧生产系统。不是某个单点工具的封装，而是**把散装的 ComfyUI 工作流整合成一条"传分镜 → 出片"的工业流水线**。

## 这仓库是什么 / 不是什么

| 是 | 不是 |
|---|---|
| 自研的漫剧生产工作流编排（C16 生图 / LTX-2.3 / MiniMax H3 / Wan 2.2 / FishAudio 音色克隆） | 对某单个开源模型的二次封装（那些是"套壳"） |
| 角色一致性方案（参考图重排 / 风格锁定 / 尾帧链式生成 / 自动验收） | 无 |
| 漫剧专用提示词工程（LTX 官方规范落地 + H3 Ref2VA 六段式 + 台词防字幕铁律） | 无 |
| 云端批量调度脚本（SSH 客户端 / 批量提交 / 轮询 / SFTP 拉取） | 无 |
| 行业字幕规范（2026-08 定稿，9:16/16:9/4K） | 无 |

## 管线全景

```
剧本（含台词） ──► 提示词包生成器 ──► 角色参考图（C16 三视图）
                                     │
                                     ▼
                        视频生成（H3 Ref2VA 主 / LTX-2.3 MSR 备）
                                     │
                                     ▼
                        音色克隆（Qwen3-TTS / FishAudio S2-pro）
                                     │
                                     ▼
                        拼接 + 外挂字幕（.ass，不烧录）
```

## 目录

```
workflows/          ComfyUI 工作流 JSON（C16 / G02 / H41 / N2 / LTX T2V）
scripts/            自研 Python 脚本（SSH 客户端 / 批量生图 / 批量配音 / 一致性验收）
docs/               方法论文档（角色一致性 / H3 提示词 / LTX 提示词 / 字幕规范）
examples/           成品示例（《苟住！》第 1 集 H3 提示词包）
```

## 快速开始

1. 准备一台 AutoDL 实例（推荐 3090/4090 48GB，已装 ComfyUI v0.30+）
2. 上传 `workflows/` 到云端 `ComfyUI/user/default/workflows/`
3. 配置环境变量（见 `scripts/comfy_ssh_client.py` 头部）：
   ```bash
   export AUTODL_HOST=connect.<region>.seetacloud.com
   export AUTODL_PORT=17699
   export AUTODL_PASS=xxxxx
   ```
4. 生成角色参考图：
   ```bash
   python scripts/cloud_batch_gen_ref.py gouzi_sheet
   ```
5. 生成角色音色：
   ```bash
   python scripts/gen_voice.py gouzai
   ```
6. 视频生成 / 配音 / 拼接：按 `docs/` 中对应工作流执行

## 原创性声明（AutoDL.Art 镜像审核用）

- **工作流编排**：C16 生图链（Z-image + 蒸馏 LoRA + SeedVR2 超分）、H41 LTX MSR 多参考图链、N2 FishAudio 音色克隆链 —— 均为针对漫剧场景的原创编排
- **提示词工程**：LTX 官方规范中文落地版（六要素 / ≤200 词 / 台词引号内嵌）；H3 Ref2VA 六段式规范；台词防字幕铁律（提示词含台词文本必出字幕，需删除 + 负面词声明）
- **一致性方案**：参考图重排（ID→姿态→Sheet→场景基准）、风格锚定声明、尾帧链式生成（`<Picture T>` 续接）、自动验收（特征检查法，命中率 ≥80% 通过）
- **行业字幕规范**：2026-08-10 定稿（竖屏对白 36 号 / 金句 42 / 旁白 27 / 白字黑描边 1.5-2px / 底部距底 80px）

## License

MIT
