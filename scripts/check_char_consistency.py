#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
角色一致性验收脚本 v2（特征检查法，H3/漫剧通用）
用法:
  python check_char_consistency.py <视频或图片> --ref 苟仔ID.png --ref 醒姐ID.png --char 苟仔 醒姐 [--frames 5]

原理（比"是否同一人"可靠，7B 视觉模型可胜任）:
  1. 对每张角色参考图跑特征检查 → 得到参考特征集（有呆毛/大门牙/人字拖...）
  2. 对视频抽帧（开头/中/尾）→ 每帧跑同一特征检查
  3. 命中率 = 帧特征集 ∩ 参考特征集 / 参考特征集
  4. 判定: ≥80% 通过 / 60-80% 警告 / <60% 失败

内置特征清单（按角色）可 --features JSON 覆盖。
依赖: 本地 Ollama qwen2.5vl:7b（零 API 成本）、ffmpeg（~/bin）
坑位: ffmpeg.exe 不认 MSYS 路径 → win_path() 自动转换
"""
import os, sys, json, base64, argparse, subprocess, tempfile, urllib.request, re

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = os.environ.get("VISION_MODEL", "qwen2.5vl:7b")

DEFAULT_FEATURES = {
    "苟仔": ["呆毛", "大门牙", "人字拖", "腰挂饭盒", "圆胖身材"],
    "醒姐": ["三根刘海", "黑眼圈", "手里拿扫帚", "高瘦身材"],
}


def win_path(p):
    """MSYS/git-bash 路径转 Windows 路径（原生 exe 不认 /e/）"""
    if p.startswith("/"):
        m = re.match(r"^/([a-zA-Z])/(.*)$", p)
        if m:
            return f"{m.group(1).upper()}:/{m.group(2)}"
    return os.path.abspath(p)


def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def ask_ollama(img_b64s, prompt, num_predict=400):
    payload = json.dumps({
        "model": MODEL, "prompt": prompt, "images": img_b64s,
        "stream": False, "options": {"num_predict": num_predict, "temperature": 0.1},
    }).encode()
    req = urllib.request.Request(OLLAMA_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode()).get("response", "").strip()


def shrink(src, dst, w=512):
    subprocess.run(["ffmpeg", "-y", "-i", src, "-vf", f"scale={w}:-1", dst],
                   capture_output=True, timeout=60)
    return dst if os.path.exists(dst) else src


def extract_frames(video, outdir, count=5):
    """抽帧：开头 + 中间3等分 + 结尾，缩小到 512 宽"""
    frames = []
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", video], capture_output=True, text=True, timeout=30)
        duration = float(probe.stdout.strip())
    except Exception:
        duration = 5.0
    for i, p in enumerate([0.1, 0.3, 0.5, 0.7, 0.9][:count]):
        t = duration * p
        out = os.path.join(outdir, f"frame_{i:02d}.png")
        subprocess.run(["ffmpeg", "-y", "-ss", str(t), "-i", video,
                        "-frames:v", "1", "-vf", "scale=512:-1", out],
                       capture_output=True, timeout=60)
        if os.path.exists(out) and os.path.getsize(out) > 0:
            frames.append(out)
    return frames


def check_features(img_path, features):
    """对单张图跑特征检查，返回 {特征: 有/无} 字典"""
    f_list = "、".join(features)
    prompt = (
        "这是一张动画图片。逐项检查人物特征，严格按格式输出（每特征一行）：\n"
        f"待检查特征：{f_list}\n"
        "输出格式：特征名=有  或  特征名=无\n"
        "只输出检查结果，不要解释。"
    )
    resp = ask_ollama([img_b64(img_path)], prompt)
    result = {}
    for feat in features:
        # 兼容多种格式：特征名=有 / 特征名：有 / 有特征名 / - 有呆毛：有
        m = (re.search(rf"{re.escape(feat)}[^有无]{{0,8}}(有|无)", resp)
             or re.search(rf"(有|无)[^有无]{{0,4}}{re.escape(feat)}", resp))
        result[feat] = 1 if (m and m.group(1) == "有") else 0
    return result, resp


def main():
    ap = argparse.ArgumentParser(description="角色一致性验收（特征检查法）")
    ap.add_argument("media", help="视频文件或图片")
    ap.add_argument("--ref", action="append", required=True, help="角色参考图(可多次)")
    ap.add_argument("--char", nargs="*", help="角色名列表(与--ref顺序对应)")
    ap.add_argument("--frames", type=int, default=5)
    ap.add_argument("--features", help="自定义特征JSON: {\"角色名\": [\"特征1\",...]}")
    ap.add_argument("--min-pass", type=float, default=0.8, help="通过阈值(默认0.8)")
    args = ap.parse_args()

    refs = [win_path(p) for p in args.ref]
    chars = args.char if args.char else [f"角色{i+1}" for i in range(len(refs))]
    features = json.loads(args.features) if args.features else DEFAULT_FEATURES

    tmp = tempfile.mkdtemp(prefix="char_check_")
    is_img = args.media.lower().endswith((".png", ".jpg", ".jpeg"))
    if is_img:
        frames = [shrink(win_path(args.media), os.path.join(tmp, "media.png"))]
    else:
        frames = extract_frames(win_path(args.media), tmp, args.frames)

    print(f"🎬 角色一致性验收 v2 | 模型={MODEL}")
    print(f"📄 角色: {', '.join(chars)} | 帧数: {len(frames)}")
    print(f"⚠️  判定: ≥{args.min_pass:.0%} 通过 / {args.min_pass-0.2:.0%}-{args.min_pass:.0%} 警告 / <{args.min_pass-0.2:.0%} 失败\n")

    overall_ok = True
    for char, ref in zip(chars, refs):
        feats = features.get(char, [])
        if not feats:
            print(f"⚠️ 角色「{char}」无特征清单，跳过")
            continue
        ref_res, _ = check_features(ref, feats)
        ref_hit = sum(ref_res.values())
        print(f"──── {char} ────")
        print(f"  参考图特征: {ref_hit}/{len(feats)} 命中 ({', '.join(f for f in feats if ref_res[f])})")

        frame_rates = []
        for fi, frame in enumerate(frames):
            frame_res, _ = check_features(frame, feats)
            hit = sum(1 for f in feats if ref_res[f] and frame_res[f])
            rate = hit / len(feats) if feats else 0
            frame_rates.append(rate)
            missing = [f for f in feats if ref_res[f] and not frame_res[f]]
            mark = "✅" if rate >= args.min_pass else ("⚠️" if rate >= args.min_pass - 0.2 else "❌")
            print(f"  帧{fi+1}: {mark} 命中 {rate:.0%} 缺: {', '.join(missing) if missing else '无'}")

        avg = sum(frame_rates) / len(frame_rates) if frame_rates else 0
        verdict = "✅ 通过" if avg >= args.min_pass else ("⚠️ 警告" if avg >= args.min_pass - 0.2 else "❌ 失败")
        if avg < args.min_pass:
            overall_ok = False
        print(f"  → 平均命中率: {avg:.0%} | 判定: {verdict}\n")

    print("════════════════════════════════")
    print("🏁 总判定:", "✅ 全部角色通过" if overall_ok else "❌ 有角色不达标，需重渲或检查参考图")
    print("（提示：若参考图本身特征命中率低，先修参考图再测）")


if __name__ == "__main__":
    main()
