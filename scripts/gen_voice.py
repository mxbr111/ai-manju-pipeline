#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_voice.py — Qwen3-TTS VoiceDesign 角色音色生成（脱敏版）

在 AutoDL 云端 ComfyUI 上，用 Qwen3-TTS VoiceDesign 工作流为角色生成专属音色。
凭据从环境变量读取，见 comfy_ssh_client.py 头注释。

用法:
  python gen_voice.py <role>            # role: gouzai / xingjie / pangbai
  python gen_voice.py --list            # 列出内置角色音色描述

输出: 本地 <桌面>/苟住_音色_<role>.wav
"""
import os, sys, json, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comfy_ssh_client import ComfyClient

DESKTOP = os.environ.get("DESKTOP_DIR", r"C:/Users/Administrator/Desktop")

# 角色音色描述 v3 (text=台词样本, instruct=音色设计描述) — 原创 IP《苟住！》
VOICES = {
    'gouzai': {
        'text': '哎呀,问题不大嘛!天塌下来有高个子顶着,咱先把这个辣条吃了再说!嘿嘿嘿~',
        'instruct': '奶龙，圆滚滚幼年小龙，软糯小胖幼龙声，厚实奶音，偏低频，圆润浑厚，轻微闷鼻音，憨憨呆萌，语气天真慵懒，带一点点吃货撒娇感，语速偏缓，人声饱满，没有尖锐高音，口腔闷闷的，可爱治愈，自然口语，清晰咬字，幼态声线，Q弹憨憨童声。避免：尖细，刺耳，清亮尖童音，夹子音，少女音，沙哑，苍老，机械音，回声杂音，嘶吼，大喊，纤细单薄声线，尖锐高频，御姐音，成人粗嗓',
    },
    'xingjie': {
        'text': '你醒醒吧!都世界末日了还惦记辣条?!行行行,你吃,我看着你吃,我看你能憨到什么时候!',
        'instruct': '清亮犀利的年轻女声,约24岁,语速快、吐字干脆,像吐槽役姐姐,每句话都带着嫌弃感和"你醒醒吧"的无奈,刀子嘴豆腐心,无奈时会轻叹气',
    },
    'pangbai': {
        'text': '末日第一天,世界乱成了一锅粥。可我们的主角苟仔,正蹲在便利店门口,思考一个哲学问题:辣条,到底算不算战略物资?',
        'instruct': '沉稳浑厚的磁性中年男声,约45岁,像纪录片解说员,语速适中字正腔圆,带着看透一切的幽默感,讲末日故事时有种反差萌的喜感',
    },
}


def build_workflow(text, instruct, role):
    """基于 Qwen3-TTS VoiceDesign 工作流模板构造提交负载（需本地模板 qwen3tts_api.json）"""
    tpl_path = os.environ.get("TTS_WORKFLOW_TEMPLATE", r"C:/Users/Administrator/tmp_frames/qwen3tts_api.json")
    with open(tpl_path, encoding='utf-8') as f:
        wf = json.load(f)
    wf['22']['inputs']['model_path'] = 'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign'
    wf['23']['inputs']['text'] = text
    wf['23']['inputs']['instruct'] = instruct
    wf['23']['inputs']['language'] = 'Chinese'
    # PreviewAudio -> SaveAudio 保存到文件
    wf['10'] = {'class_type': 'SaveAudio', 'inputs': {
        'audio': ['23', 0],
        'filename_prefix': f'voice_{role}'
    }}
    # 移除可能缺依赖的分支
    for k in ['7', '12', '15', '17', '19', '20', '21', '24', '30', '31']:
        wf.pop(k, None)
    wf.pop('_api_config', None)
    return wf


def main():
    if '--list' in sys.argv:
        for name, v in VOICES.items():
            print(f"[{name}] {v['instruct'][:60]}...")
        return
    if len(sys.argv) < 2:
        print("用法: python gen_voice.py <role> | --list")
        sys.exit(1)
    role = sys.argv[1]
    if role not in VOICES:
        print(f"未知角色: {role}，可用: {list(VOICES)}")
        sys.exit(1)
    v = VOICES[role]

    client = ComfyClient()
    print(f"已连接云端，生成音色 role={role} ...")
    wf = build_workflow(v['text'], v['instruct'], role)
    pid, raw = client.submit(wf, client_id="hermes_voice_gen")
    if not pid:
        print("提交失败:", raw[:300])
        client.close()
        sys.exit(1)
    print("PID:", pid)
    result = client.wait_done(pid, timeout=600)
    if "error" in result:
        print("执行失败:", result["error"])
        client.close()
        sys.exit(1)
    for nid, node_out in result.get("outputs", {}).items():
        for g in node_out.get("audio", []):
            remote = f"/root/ComfyUI/output/{g['filename']}"
            local = os.path.join(DESKTOP, f"苟住_音色_{role}.wav")
            client.download(remote, local)
            print("下载完成:", local)
    client.close()


if __name__ == '__main__':
    main()
