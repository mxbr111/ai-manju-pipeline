# AutoDL.art 镜像上架 SOP

> 《苟住！》AI 漫剧生产镜像上架操作手册（2026-08-14 制定）

## 前置条件

- [ ] AutoDL.art 邀请码（公测期必填）：已获取 `cd4492`，存 `~/bin/autodl_art_invite.txt`
- [ ] GitHub 原创证明仓库：https://github.com/mxbr111/ai-manju-pipeline （已上线）
- [ ] AutoDL 云端实例（5090 32GB / 3090 48GB，ComfyUI v0.30+）

## 步骤

### 1. 环境确认

```
ComfyUI:  v0.32.0（端口 6006）
工作流:   33 个 zealman 模板（C16/G01-G10/H17-H41/U01-U04/N2）
模型:     Z-image / Wan 全系 / LTX 全系 / Qwen3-TTS 三模型
```

### 2. 注入自研资产（已完成）

```
云端目录: /root/ComfyUI/input/gouzhu_assets/
  characters/  角色参考图（苟仔/醒姐 ID + 三视图 + 表情）
  scenes/      场景图（街道/便利店/天台）
  voices/      角色音色（gouzai/xingjie/pangbai）
```

### 3. 功能验证（每项必须出片）

| 测试 | 工作流 | 预期 |
|---|---|---|
| 角色生图 | C16 短剧文生图 | 三视图角色图 |
| 场景生图 | C16 + 场景 prompt | 无人物场景图 |
| 视频生成 | H3 Ref2VA (U04) | 角色一致视频 |
| 音色克隆 | N2 FishAudio | 克隆音色 |

### 4. 保存镜像

AutoDL 控制台 → 实例 → 关机 → 保存镜像（普通实例需控制台手动操作，Pro 实例可用 API）

### 5. 提交上架

1. 登录 autodl.art
2. 提交镜像（`POST /api/v1/application/create`，需登录态）
3. 填创作激励表单：
   - 镜像：已审核上架
   - 算法类型：AIGC 算法镜像（文生图/文生视频）
   - 算法原创：是（GitHub 仓库证明）
   - 代码原创：是（工作流编排 + 脚本非 Fork）
   - 邀请码：cd4492
4. 等待审核

### 6. 持续维护（规则要求）

- 超 6 个月未更新 → 取消活动资格
- 自用套现 → 取消资格且不支持提现
- 版权纠纷 → 下架 + 取消奖励

## 收益计算

| 显卡 | 单价 | 24h 满跑 | 月收益 |
|---|---|---|---|
| NVIDIA GPU | ¥0.08/h | ¥1.92 | ~¥58 |
| 华为 NPU/摩尔线程 | ¥0.23/h | ¥5.52 | ~¥166 |

**定位：不是收入源，是「漫剧管线产品化」的获客入口。**
