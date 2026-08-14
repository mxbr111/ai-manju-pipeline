import requests, json, time, sys, os

# 输出路径可配置：环境变量 LTX_OUTPUT_PATH 或 --output 参数
OUTPATH = os.environ.get("LTX_OUTPUT_PATH", "ltx_pure_video_workflow.json")

prompt = {}

prompt["1"] = {  # UnetLoaderGGUF - LTX GGUF
    "class_type": "UnetLoaderGGUF",
    "inputs": {"unet_name": "ltx-2.3-22b-distilled-1.1-Q2_K.gguf"}
}
prompt["2"] = {  # ModelSamplingLTXV - configure model
    "class_type": "ModelSamplingLTXV",
    "inputs": {"model": ["1", 0], "max_shift": 2.05, "base_shift": 0.95}
}
prompt["3"] = {  # VAELoader - video VAE
    "class_type": "VAELoader",
    "inputs": {"vae_name": "LTX23_video_vae_bf16.safetensors"}
}
prompt["4"] = {  # CheckpointLoaderSimple - just for CLIP from SD1.5
    "class_type": "CheckpointLoaderSimple",
    "inputs": {"ckpt_name": "dreamshaper_8.safetensors"}
}
prompt["5"] = {  # CLIPTextEncode - positive prompt
    "class_type": "CLIPTextEncode",
    "inputs": {
        "text": "A futuristic city at night, neon lights, cinematic quality, detailed",
        "clip": ["4", 1]  # CLIP output from CheckpointLoader is index 1
    }
}
prompt["6"] = {  # CLIPTextEncode - negative prompt
    "class_type": "CLIPTextEncode",
    "inputs": {
        "text": "blurry, low quality, distorted, ugly",
        "clip": ["4", 1]
    }
}
prompt["7"] = {  # CFGGuider - doesn't need skip_block_list
    "class_type": "CFGGuider",
    "inputs": {
        "model": ["2", 0],
        "positive": ["5", 0],
        "negative": ["6", 0],
        "cfg": 4.0
    }
}
prompt["8"] = {  # KSamplerSelect
    "class_type": "KSamplerSelect",
    "inputs": {"sampler_name": "euler"}
}
prompt["9"] = {  # LTXVScheduler
    "class_type": "LTXVScheduler",
    "inputs": {
        "steps": 20,
        "max_shift": 2.05,
        "base_shift": 0.95,
        "stretch": True,
        "terminal": 0.1
    }
}
prompt["10"] = {  # RandomNoise
    "class_type": "RandomNoise",
    "inputs": {"noise_seed": 42}
}
prompt["11"] = {  # EmptyLTXVLatentVideo
    "class_type": "EmptyLTXVLatentVideo",
    "inputs": {"width": 576, "height": 1024, "length": 25, "batch_size": 1}
}
prompt["12"] = {  # LTXVBaseSampler
    "class_type": "LTXVBaseSampler",
    "inputs": {
        "model": ["1", 0],
        "vae": ["3", 0],
        "width": 576,
        "height": 1024,
        "num_frames": 25,
        "guider": ["7", 0],
        "sampler": ["8", 0],
        "sigmas": ["9", 0],
        "noise": ["10", 0]
    }
}
prompt["13"] = {  # LTXVTiledVAEDecode
    "class_type": "LTXVTiledVAEDecode",
    "inputs": {
        "vae": ["3", 0],
        "latents": ["12", 0],
        "horizontal_tiles": 2,
        "vertical_tiles": 2,
        "overlap": 1,
        "last_frame_fix": False
    }
}
prompt["14"] = {  # CreateVideo
    "class_type": "CreateVideo",
    "inputs": {"images": ["13", 0], "fps": 24}
}
prompt["15"] = {  # SaveVideo
    "class_type": "SaveVideo",
    "inputs": {
        "video": ["14", 0],
        "filename_prefix": "Terra7_pure_video_test",
        "format": "mp4",
        "codec": "h264"
    }
}

# Save workflow JSON
with open(OUTPATH, "w") as f:
    json.dump(prompt, f, indent=2)
print(f"Workflow saved to {OUTPATH}")

# Queue
print("Queueing prompt...")
r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": prompt}, timeout=30)
print(f"Status: {r.status_code}")
resp = r.json()
print(json.dumps(resp, indent=2)[:1000])

if "error" in resp:
    print(f"\nERROR: {resp['error']}")
    if "node_errors" in resp:
        for nid, err in resp["node_errors"].items():
            print(f"  Node {nid}: {err}")
    sys.exit(1)

pid = resp.get("prompt_id")
if not pid:
    print("No prompt_id")
    sys.exit(1)
print(f"\nPrompt ID: {pid}")

# Monitor
print("\nMonitoring execution...")
while True:
    r = requests.get(f"http://127.0.0.1:8188/history/{pid}", timeout=10)
    hist = r.json()
    if pid in hist:
        st = hist[pid]["status"]
        print(f"\n=== COMPLETED === Status: {json.dumps(st, indent=2)}")
        outputs = hist[pid].get("outputs", {})
        for nid, out in outputs.items():
            print(f"Node {nid}: {json.dumps(out, indent=2)[:500]}")
        break
    r2 = requests.get("http://127.0.0.1:8188/queue", timeout=10)
    q = r2.json()
    running = q.get("queue_running", False)
    pending = len(q.get("queue_pending", []))
    print(f"  Running: {running}, Pending: {pending}")
    time.sleep(10)
