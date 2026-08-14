#!/usr/bin/env python3
"""Build E01 LTX production workflows (SD CLIP fallback + GEMMA fp8 CLIP)."""
import json, os

# Base nodes shared by both workflows
BASE_NODES = {
    "3940": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": "ltx-2.3-22b-distilled-1.1-Q2_K.gguf"}},
    "4922": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["3940", 0], "lora_name": "ltxv\\\\ltx2\\\\ltx-2.3-22b-distilled-lora-384-1.1-fresh.safetensors", "strength_model": 0.0}},
    "3059": {"class_type": "EmptyLTXVLatentVideo", "inputs": {"width": 576, "height": 1024, "length": ["4979", 0], "batch_size": 144}},
    "4978": {"class_type": "PrimitiveFloat", "inputs": {"value": 24}},
    "4979": {"class_type": "PrimitiveInt", "inputs": {"value": 144}},
    "4999": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
    "5000": {"class_type": "VAELoader", "inputs": {"vae_name": "taeltx2_3.safetensors"}},
    "1241": {"class_type": "LTXVConditioning", "inputs": {"positive": ["2483", 0], "negative": ["2612", 0], "frame_rate": ["4978", 0]}},
    "4966": {"class_type": "LTXVScheduler", "inputs": {"steps": 15, "max_shift": 2.05, "base_shift": 0.95, "stretch": True, "terminal": 0.1, "latent": ["3059", 0]}},
    "4971": {"class_type": "ManualSigmas", "inputs": {"sigmas": "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"}},
    "4964": {"class_type": "GuiderParameters", "inputs": {"modality": "VIDEO", "cfg": 3, "stg": 1, "perturb_attn": True, "rescale": 0.9, "modality_scale": 3, "skip_step": 0, "cross_attn": True}},
    "4828": {"class_type": "CFGGuider", "inputs": {"model": ["4922", 0], "positive": ["1241", 0], "negative": ["1241", 1], "cfg": 1}},
    "4832": {"class_type": "RandomNoise", "inputs": {"noise_seed": 42}},
    "4802": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["4832", 0], "guider": ["4828", 0], "sampler": ["4999", 0], "sigmas": ["4971", 0]}},
    "4982": {"class_type": "LTXVTiledVAEDecode", "inputs": {"vae": ["5000", 0], "latents": ["4802", 0], "horizontal_tiles": 2, "vertical_tiles": 2, "overlap": 6, "last_frame_fix": False, "working_device": "auto", "working_dtype": "auto"}},
    "4819": {"class_type": "CreateVideo", "inputs": {"images": ["4982", 0], "fps": ["4978", 0], "audio": None, "bit_depth": 8}},
    "4823": {"class_type": "SaveVideo", "inputs": {"video": ["4819", 0], "filename_prefix": "Terra7_LTX_", "format": "mp4", "codec": "h264", "prompt": "", "extra_pnginfo": "{}"}},
}

# SD CLIP nodes (workaround, 768-dim from dreamshaper_8)
SD_CLIP_NODES = {
    "6000": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "dreamshaper_8.safetensors"}},
    "2483": {"class_type": "CLIPTextEncode", "inputs": {"text": "korean manhwa style, thick black outline, cel shading, flat anime color, consistent painting texture, no photorealistic, [SCENE_CONTEXT]", "clip": ["6000", 1]}},
    "2612": {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, low quality, bad anatomy, watermark, text, ugly, deformed, photorealistic", "clip": ["6000", 1]}},
}

# GEMMA fp8 CLIP nodes (full quality, 4096-dim)
GEMMA_CLIP_NODES = {
    "5023": {"class_type": "LTXAVTextEncoderLoader", "inputs": {"text_encoder": "gemma-3-12b-it-heretic-fp8_scaled.safetensors", "ckpt_name": "dreamshaper_8.safetensors", "device": "default"}},
    "2483": {"class_type": "CLIPTextEncode", "inputs": {"text": "korean manhwa style, thick black outline, cel shading, flat anime color, consistent painting texture, no photorealistic, [SCENE_CONTEXT]", "clip": ["5023", 0]}},
    "2612": {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, low quality, bad anatomy, watermark, text, ugly, deformed, photorealistic", "clip": ["5023", 0]}},
}

import os
base = os.path.expanduser("~/Documents/comfy/ComfyUI/workflows")

# Build SD CLIP workflow
sd_nodes = {**BASE_NODES, **SD_CLIP_NODES}
with open(os.path.join(base, "terra7_ltx_sdclip.json"), "w") as f:
    json.dump(sd_nodes, f, indent=2)
print(f"terra7_ltx_sdclip.json: {len(sd_nodes)} nodes (SD CLIP workaround)")

# Build GEMMA fp8 CLIP workflow
gemma_nodes = {**BASE_NODES, **GEMMA_CLIP_NODES}
with open(os.path.join(base, "terra7_ltx_gemmaclip.json"), "w") as f:
    json.dump(gemma_nodes, f, indent=2)
print(f"terra7_ltx_gemmaclip.json: {len(gemma_nodes)} nodes (GEMMA fp8 CLIP)")
