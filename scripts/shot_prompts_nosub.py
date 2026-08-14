#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《苟住!》镜头2-8 无字幕版提示词(台词已全部移除,只留口型动作,字幕后期加)"""
# ⚠️ 铁律:LTX 提示词正文零台词文本——任何 says in Chinese:「…」都会被模型渲染成画面字幕

NEG_COMMON = """worst quality, blurry, jittery, distorted, inconsistent appearance, extra fingers, deformed hands, text on screen, subtitles, captions, chinese characters, chinese text, letters, words, written words, watermark, logo, low resolution, mutated face, photorealistic, realistic, cinematic, film grain, 3d render"""

STYLE_CARTOON = "flat 2D cartoon style, clean lineart, flat colors, storybook illustration, no on-screen text, no subtitles, no captions, no letters, no characters on screen, subtitles added in post-production"

# 每镜: (名字, 提示词, 场景图, 参考图1, 参考图2)
# 参考图: 102=输入1(锁脸ID) 103=输入2 159=background
SHOTS = [
    # 镜头2 醒姐崩溃(双人:苟仔ID + 醒姐ID)
    ("shot2", f"""Medium shot. A tall thin girl with three strands of side bangs and dark circles under her eyes runs toward a chubby boy lying on the road, holding a broom, angry and exasperated, waving the broom at his face, shouting with mouth wide open, natural mouth movements. Behind them a small meteorite crashes into the road half a meter away, raising dust. The boy lies unbothered, eyes closed, relaxed. Camera follows her movement. {STYLE_CARTOON}""",
     "scene_street.png", "gou_zai_ID.png", "xing_jie_ID.png"),
    # 镜头3 饭盒梗(双人)
    ("shot3", f"""Medium shot. The chubby boy sits up slowly, takes the lunchbox from his belt, wipes dust off it but does not open it, grins proudly, talking cheerfully with natural mouth movements. The tall girl facepalms, shaking her head, exasperated but slightly amused. Static camera, two characters in frame. {STYLE_CARTOON}""",
     "scene_street.png", "gou_zai_ID.png", "xing_jie_ID.png"),
    # 镜头4 丧尸歪理(双人+丧尸)
    ("shot4", f"""Wide shot. A group of shambling zombies appears in the distance walking toward camera. A chubby boy stands in front of a tall thin girl, raises his hand to stop, speaking confidently with natural mouth movements. The girl looks doubtful. Camera static, zombies slowly approaching. {STYLE_CARTOON}""",
     "scene_street.png", "gou_zai_ID.png", "xing_jie_ID.png"),
    # 镜头5 镜子反转(双人+丧尸)
    ("shot5", f"""Wide shot. A lead zombie reaches a broken shop window with reflective glass, stops, stares at its own reflection, looks shocked, covers its face with both hands and turns away, walking off. The tall girl watches with wide eyes, amazed. The chubby boy crosses his arms proudly, chest puffed, smug grin, talking with natural mouth movements. Camera holds. {STYLE_CARTOON}""",
     "scene_street.png", "gou_zai_ID.png", "xing_jie_ID.png"),
    # 镜头6 辣条战略物资(双人,便利店)
    ("shot6", f"""Medium shot inside an empty convenience store. Bare shelves, one packet of spicy snacks on the counter. A chubby boy snatches the packet and hugs it protectively, speaking seriously with natural mouth movements. A tall thin girl protests, hands on hips, exasperated. Camera medium static, dim flickering light. {STYLE_CARTOON}""",
     "scene2_store.png", "gou_zai_ID.png", "xing_jie_ID.png"),
    # 镜头7 灵魂瞬间(双人,天台)
    ("shot7", f"""Medium shot on a rooftop at night, starry sky above, ruined city skyline behind. The chubby boy sits cross-legged looking up, unusually calm and soft, speaking gently with natural mouth movements. The tall thin girl sits beside him, sighs, answers softly, a small warm smile. Warm moonlight, touching moment, camera slowly pulls back. {STYLE_CARTOON}""",
     "scene3_rooftop.png", "gou_zai_ID.png", "xing_jie_ID.png"),
    # 镜头8 结尾钩子(双人剪影)
    ("shot8", f"""Extreme wide shot from behind. A chubby boy and a tall thin girl sit side by side on the rooftop edge, small silhouettes against the starry sky and ruined city, peaceful. Camera slowly dollies back revealing the full ruined skyline. Night scene, cool blue tones, ending shot. {STYLE_CARTOON}""",
     "scene3_rooftop.png", "gou_zai_ID.png", "xing_jie_ID.png"),
]
