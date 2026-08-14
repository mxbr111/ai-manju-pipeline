#!/usr/bin/env python
"""
LTX 12镜批量提交脚本 — 第1集《孢子》
向 ComfyUI API (127.0.0.1:8188) 提交12个LTX渲染任务
输出目录: ComfyUI/output/ (默认)
"""

import json, urllib.request, sys, time, os, re, glob

API_URL = "http://127.0.0.1:8188"
WORKFLOW_PATH = r"C:\Users\Administrator\Desktop\ltx_pure_video_v3.json"
PROMPTS_FILE = r"C:\Users\Administrator\Desktop\ltx_shot_prompts.json"

# ========== 12个LTX镜的prompt数据 ==========
shots = [
    {
        "id": "S01",
        "desc": "space orbital overlook, planet Terra-7 blue-green surface, huge gray silicon network stone net structure, transparent dome city Gaia Nest embedded on the planet surface, cosmic silent atmosphere",
        "neg": "photorealistic, deformed, blurry, extra limbs, messy lines",
        "bgm": "深空低频环境氛围音，空灵微弱",
        "seed": 1001
    },
    {
        "id": "S02",
        "desc": "dusk inside Gaia Nest dome, observation window overlook desolate wilderness outside, stone net structure faint glowing, silhouette of a short-haired woman standing by the window holding data pad",
        "neg": "photorealistic, deformed, blurry",
        "bgm": "压抑低沉铺垫纯音乐",
        "seed": 1002
    },
    {
        "id": "S03",
        "desc": "biological laboratory daytime, microscope on desktop, young man rushing into the room out of breath, indoor cold white light",
        "neg": "photorealistic, deformed hands, distorted facial features",
        "bgm": "轻微紧张心跳背景音",
        "seed": 1003
    },
    {
        "id": "S05",
        "desc": "close-up of tablet screen, data curve soaring seven times in three months, laboratory desktop close shot, trembling hand holding the tablet",
        "neg": "garbled text, distorted interface",
        "bgm": "紧张氛围加重",
        "seed": 1005
    },
    {
        "id": "S07",
        "desc": "Gaia Nest colonial square daytime, huge public screen playing commander speech, crowds clapping neatly, all residents overly rigid smiling",
        "neg": "photorealistic, chaotic crowd, deformed faces",
        "bgm": "宏大虚伪管弦乐，表层昂扬内里压抑",
        "seed": 1007
    },
    {
        "id": "S08",
        "desc": "Lin Mei dormitory night, lying on bed staring ceiling, fluorescent spore particles floating in the air outside the window, dim night room lighting",
        "neg": "overexposure, messy particle effect",
        "bgm": "孤寂夜晚低频氛围音",
        "seed": 1008
    },
    {
        "id": "S09",
        "desc": "female finger reaching out to touch floating glowing spore light spot, light spot dispersing through fingertip, window glass reflection",
        "neg": "deformed fingers, abnormal light effects",
        "bgm": "空灵细碎粒子音效",
        "seed": 1009
    },
    {
        "id": "S10",
        "desc": "bedroom ceiling close-up, faint neural network stone net pattern projected on the wall, dim night ambient light",
        "neg": "chaotic pattern, over-bright flash",
        "bgm": "诡异低频震动音效",
        "seed": 1010
    },
    {
        "id": "S11",
        "desc": "Lin Mei suddenly sitting up on bed, night dormitory indoor static shot, ceiling pattern completely disappear",
        "neg": "distorted body posture",
        "bgm": "短暂心跳骤停音效",
        "seed": 1011
    },
    {
        "id": "S12",
        "desc": "window overlook wild land outside the dome at night, stone net structure faint pulsating glow on the horizon, dark night wilderness vast shot",
        "neg": "over-dark screen, lost details",
        "bgm": "悬念收尾低沉长音，渐弱收尾",
        "seed": 1012
    },
    {
        "id": "S13",
        "desc": "static wide shot of Terra-7 night wilderness, glowing stone net spreading to the end of the horizon, lonely Gaia Nest dome in the distance",
        "neg": "photorealistic, deformed, blurry",
        "bgm": "余韵悬疑铺垫音",
        "seed": 1013
    },
    {
        "id": "S14",
        "desc": "text overlay final frame: Episode 1 Spore Suspense Teaser, dark night planet background",
        "neg": "photorealistic, deformed, blurry",
        "bgm": "单音收尾定格音效",
        "seed": 1014
    }
]

def load_workflow():
    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

BASE_NEGATIVE = "blurry, low quality, distorted, ugly, deformed, bad anatomy, extra limbs, fused fingers, watermark, text, signature, photorealistic, realistic, 3d render, photograph, photoshop, painting"

def make_workflow(shot):
    """为单镜构建workflow JSON"""
    wf = load_workflow()
    
    # 构建完整正向prompt = 前缀 + 场景描述
    prefix = "korean manhwa style, thick black outline, cel shading, flat anime color, consistent painting texture, no photorealistic"
    positive_text = f"{prefix}, {shot['desc']}"
    
    # 节点3: 正向prompt CLIPTextEncode
    wf["3"]["inputs"]["text"] = positive_text
    
    # 节点4: 负向prompt = 通用负面 + 镜特定负面
    full_neg = f"{BASE_NEGATIVE}, {shot['neg']}"
    wf["4"]["inputs"]["text"] = full_neg
    
    # 节点11: RandomNoise种子
    wf["11"]["inputs"]["noise_seed"] = shot["seed"]
    
    # 节点21: SaveVideo文件名前缀
    wf["21"]["inputs"]["filename_prefix"] = f"Terra7_E01_{shot['id']}_"
    
    return wf

def queue_prompt(workflow):
    """提交workflow到ComfyUI队列"""
    payload = json.dumps({"prompt": workflow}).encode('utf-8')
    req = urllib.request.Request(
        f"{API_URL}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        return result.get("prompt_id"), None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return None, str(e)

def wait_for_completion(prompt_id, shot_id, timeout=1800):
    """等待单镜渲染完成，返回输出信息"""
    start = time.time()
    last_status = ""
    while time.time() - start < timeout:
        elapsed = int(time.time() - start)
        try:
            req = urllib.request.Request(f"{API_URL}/history/{prompt_id}")
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            
            if prompt_id in data:
                result = data[prompt_id]
                status = result.get("status", {})
                
                if status.get("completed") or status.get("status_str") == "completed":
                    # 检查输出
                    outputs = result.get("outputs", {})
                    output_info = []
                    for node_id, node_output in outputs.items():
                        if "videos" in node_output:
                            for v in node_output["videos"]:
                                output_info.append(v.get("filename", v.get("video", "unknown")))
                        if "gifs" in node_output:
                            for g in node_output["gifs"]:
                                output_info.append(g.get("filename", "unknown"))
                    
                    duration = int(time.time() - start)
                    return {
                        "success": True,
                        "duration_sec": duration,
                        "prompt_id": prompt_id,
                        "outputs": output_info,
                        "node_outputs": outputs
                    }
                
                # 进度信息
                progress = status.get("progress", {})
                if progress:
                    cur = progress.get("current", 0)
                    total = progress.get("total", 0)
                    pct = cur / total * 100 if total > 0 else 0
                    msg = f"  ⏳ {shot_id}: {cur}/{total} step ({pct:.0f}%) [{elapsed}s]"
                    if msg != last_status:
                        print(msg)
                        last_status = msg
        except Exception as e:
            pass
        
        time.sleep(5)
    
    return {"success": False, "error": f"Timed out after {timeout}s"}

def main():
    print("=" * 60)
    print("🚀 Terra-7 E01 LTX 12镜批量渲染开始")
    print(f"⏰ {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = []
    total_start = time.time()
    
    for i, shot in enumerate(shots):
        print(f"\n[{i+1}/12] 提交 {shot['id']}: seed={shot['seed']}")
        print(f"  📝 {shot['desc'][:60]}...")
        
        wf = make_workflow(shot)
        prompt_id, error = queue_prompt(wf)
        
        if error:
            print(f"  ❌ 提交失败: {error}")
            results.append({"id": shot["id"], "status": "failed", "error": error})
            continue
        
        print(f"  ✅ 已入队列: {prompt_id[:12]}...")
        
        # 等待本镜完成
        result = wait_for_completion(prompt_id, shot["id"])
        results.append({"id": shot["id"], **result})
        
        if result.get("success"):
            outputs = result.get("outputs", [])
            print(f"  ✅ {shot['id']} 完成! {result['duration_sec']}s")
            print(f"  📁 输出: {outputs}")  
        else:
            print(f"  ❌ {shot['id']} 失败: {result.get('error', 'unknown')}")
    
    total_elapsed = int(time.time() - total_start)
    
    print("\n" + "=" * 60)
    print(f"📊 批量渲染完成！总耗时: {total_elapsed//60}分{total_elapsed%60}秒")
    
    successes = sum(1 for r in results if r.get("success"))
    failures = sum(1 for r in results if r.get("status") == "failed" or not r.get("success"))
    
    print(f"  ✅ 成功: {successes}/12")
    print(f"  ❌ 失败: {failures}/12")
    
    # 保存结果到桌面
    result_path = r"C:\Users\Administrator\Desktop\ltx_batch_results.json"
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump({"total_elapsed_sec": total_elapsed, "results": results}, f, indent=2, ensure_ascii=False)
    print(f"  📁 结果存: {result_path}")

if __name__ == "__main__":
    main()
