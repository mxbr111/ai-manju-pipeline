#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cloud_batch_gen_ref.py — AutoDL 云端 C16 批量生成角色/场景参考图（脱敏版）

原创点: 角色三视图/场景图的提示词工程 + 云端批量调度封装。
凭据从环境变量读取（AUTODL_HOST/AUTODL_PORT/AUTODL_PASS，见 comfy_ssh_client.py）。

用法:
  python cloud_batch_gen_ref.py <job_name>        # 生成单个 job
  python cloud_batch_gen_ref.py --all             # 批量生成全部
  python cloud_batch_gen_ref.py --check           # 检查输出目录
  python cloud_batch_gen_ref.py --add name "prompt" --width 768 --height 1344   # 自定义 job

云端工作流路径可用环境变量 C16_WORKFLOW_PATH 覆盖。
"""
import os, sys, json, hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comfy_ssh_client import ComfyClient

WF_PATH = os.environ.get("C16_WORKFLOW_PATH", "/root/zealman-app/workflows/C16-短剧文生图专用-支持场景-角色.json")
OUT_ROOT = "/root/ComfyUI/output"

# 提示词集: name -> prompt (角色三视图 / 场景图) — 原创《苟住！》IP 资产
JOBS = {
    "gouzi_sheet": {
        "prefix": "xq_ref/gouzi_sheet",
        "width": 768, "height": 1344,
        "prompt": "character design sheet, three views (front, side, back) of the same character, chubby cute Q-version boy, single ahoge hair strand sticking up, big front buck teeth, wearing casual flip-flops, a lunchbox hanging from his belt, round belly, lazy relaxed posture, cartoon style, clean lineart, flat colors, plain white background, consistent design, full body",
    },
    "xingjie_sheet": {
        "prefix": "xq_ref/xingjie_sheet",
        "width": 768, "height": 1344,
        "prompt": "character design sheet, three views (front, side, back) of the same character, tall thin paper-thin girl, three strands of side bangs, dark circles under eyes, holding a broom, tired but sharp expression, cartoon style, clean lineart, flat colors, plain white background, consistent design, full body",
    },
    "scene_street": {
        "prefix": "xq_ref/scene_street",
        "width": 832, "height": 1472,
        "prompt": "abandoned city street, cracked asphalt road, collapsed buildings in background, broken streetlights, overgrown weeds, overcast sky, post-apocalyptic atmosphere, empty street, no people, wide angle, cartoon style, muted colors, cinematic lighting, background only",
    },
    "scene_store": {
        "prefix": "xq_ref/scene_store",
        "width": 832, "height": 1472,
        "prompt": "empty convenience store interior, bare shelves, one packet of spicy snacks left on the counter, broken glass door, dim flickering light, post-apocalyptic mood, no people, cartoon style, muted colors, cinematic lighting, background only",
    },
    "scene_rooftop": {
        "prefix": "xq_ref/scene_rooftop",
        "width": 832, "height": 1472,
        "prompt": "rooftop at night, starry sky, ruined city skyline in distance, gentle moonlight, peaceful atmosphere, post-apocalyptic setting, no people, cartoon style, cool blue tones, cinematic wide shot, background only",
    },
}


def random_seed(prefix):
    """确定性 seed: 同一 job 每次结果可复现"""
    return int(hashlib.md5(prefix.encode()).hexdigest()[:12], 16)


def submit_job(client, job_name, job):
    """读取云端模板工作流 -> 注入提示词/尺寸/seed -> 提交"""
    wf = client.get_workflow(WF_PATH)
    wf = {k: v for k, v in wf.items() if v.get("class_type")}  # 过滤元数据节点
    wf['49']['inputs']['text'] = job['prompt']
    wf['60']['inputs']['value'] = job['width']
    wf['61']['inputs']['value'] = job['height']
    wf['58']['inputs']['filename_prefix'] = job['prefix']
    wf['22']['inputs']['seed'] = random_seed(job['prefix'])
    pid, raw = client.submit(wf, client_id="hermes_ref_gen")
    return pid, raw


def check_all(client):
    for name, job in JOBS.items():
        print(f"{name} -> {client.list_output(job['prefix']) or '(还没出)'}")


def main():
    args = sys.argv[1:]
    if '--check' in args:
        client = ComfyClient()
        check_all(client)
        client.close()
        sys.exit(0)

    # --add name "prompt" [--width W --height H --prefix P]
    if '--add' in args:
        i = args.index('--add')
        name = args[i + 1]
        prompt = args[i + 2]
        w = int(args[args.index('--width') + 1]) if '--width' in args else 768
        h = int(args[args.index('--height') + 1]) if '--height' in args else 1344
        prefix = args[args.index('--prefix') + 1] if '--prefix' in args else f"xq_ref/{name}"
        JOBS[name] = {"prefix": prefix, "width": w, "height": h, "prompt": prompt}
        print(f"新增 job: {name} ({w}x{h})")

    client = ComfyClient()
    if '--all' in args:
        for name, job in JOBS.items():
            pid, raw = submit_job(client, name, job)
            print(f"提交 {name}: {raw[:200]}")
    else:
        job_name = args[0] if args else 'gouzi_sheet'
        if job_name not in JOBS:
            print(f"未知 job: {job_name}，可用: {list(JOBS)}")
            client.close()
            sys.exit(1)
        pid, raw = submit_job(client, job_name, JOBS[job_name])
        print(f"提交 {job_name}: {raw[:300]}")
    client.close()


if __name__ == '__main__':
    main()
