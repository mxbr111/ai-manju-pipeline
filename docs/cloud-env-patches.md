# 云端环境补丁清单（镜像打包必须固化）

> 5090 新实例从 zealman 官方镜像启动后，FishAudio 音色克隆无法使用，需按此清单修复。
> 这些补丁是镜像可用的关键，保存镜像前必须确保已应用。

## 背景

zealman 官方镜像的 ComfyUI v0.32.0 环境缺少 fish_speech 运行时依赖，
且新版 torchaudio (2.11+) 移除了 `list_audio_backends` API。

## 修复步骤

### 1. 安装 fish_speech 缺失依赖

```bash
/root/miniconda3/bin/pip install pyrootutils natsort hydra-core omegaconf \
  lightning loralib kui einx opencc-python-reimplemented silero-vad \
  descript-audio-codec descript-audiotools pydub modelscope
```

（跳过 torch/torchaudio —— ComfyUI 管理；protobuf 版本冲突可忽略）

### 2. 打 torchaudio 兼容补丁

文件：`fish_speech_src/fish_speech/inference_engine/reference_loader.py`

```python
# 旧代码（torchaudio 2.11 报 AttributeError）
backends = torchaudio.list_audio_backends()

# 新代码（try/except 兼容）
try:
    backends = torchaudio.list_audio_backends()
except AttributeError:
    backends = []  # torchaudio >= 2.9 removed list_audio_backends
```

备份：`reference_loader.py.bak`

### 3. 重启 ComfyUI

```bash
pkill -f '/root/ComfyUI/main.py'
nohup /root/zealman-app/start-comfyui-9cu.sh > /root/comfy_start.log 2>&1 &
```

### 4. 验证

```bash
/root/miniconda3/bin/python -c '
import sys; sys.path.insert(0, "/root/ComfyUI/custom_nodes/ComfyUI-fish-audio-s2/fish_speech_src")
import fish_speech; print("fish_speech OK")'
```

## 2026-08-14 实测记录

- 缺失依次暴露：pyrootutils → natsort → lightning → loralib（依赖链逐个补）
- 每次装完必须重启 ComfyUI 才生效
- 补丁后 N2 工作流正常进入推理阶段（不再报 ImportError）
