import json
import os
import copy

WEB_BUILD_DIR = os.path.join('study', 'resume', 'web_build')
DATA_FILE = os.path.join(WEB_BUILD_DIR, 'data.json')

# 1. Load current data (which is Eric's data mixed with template meta)
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    current_data = json.load(f)

# 2. Extract Eric's data
eric_data = {
    "profile": current_data.get('profile', {}),
    "sections": current_data.get('sections', {}),
    "grades": current_data.get('grades', []),
    "attachments": current_data.get('attachments', []),
    "green_template_structure": current_data.get('green_template_structure', [])
}

# 3. Create Template Bot Data (张一一)
# Based on PDF analysis text
template_bot_data = {
    "profile": {
        "name": "张一一",
        "gender": "女", # Guessing based on "张一一" and tone, or just generic
        "birthday": "1999年",
        "height": "160cm",
        "school": "阳光小学",
        "hometown": "北京",
        "address": "北京市朝阳区示例小区",
        "phone": "13812345678",
        "avatar": "assets/template_pdf/bg_page_1_0.png" # Placeholder using sidebar bg or similar
    },
    "sections": {
        "intro": [
            "尊敬的Xx学校老师：",
            "您好，我是阳光小学的张一一，我非常有意愿地就读你们学校，希望您能使我梦想成真，非常感谢，下面说说我的自荐情况：",
            "我出生于1999年，于2006年进入Xx小学学习。在校期间，我学习成绩优异，多次获得三好学生荣誉称号。"
        ],
        "specialty": [
            "书法（八级）",
            "绘画（多次获奖）",
            "摄影"
        ],
        "awards": [
            "2008年 英语朗读比赛二等奖",
            "2009年 全国小百花杯儿童书画摄影大赛三等奖",
            "2010年 第十四届双龙杯全国少儿书画大赛优秀作品奖",
            "2011年 英语朗读比赛一等奖"
        ],
        "activities": [
            "校合唱团成员",
            "班级宣传委员"
        ],
        "parents_words": [
            "你聪明，你善良，你活泼。有时你也幻想，有时你也默然。在默然中沉思，在幻想中寻觅。小小的你会长大..."
        ]
    },
    "grades": [
        {"term": "五年级上", "chinese": "98", "math": "100", "english": "99"},
        {"term": "五年级下", "chinese": "99", "math": "98", "english": "100"}
    ],
    "attachments": [] # We can add some generic placeholders if needed
}

# Replicate the structure for Template Bot
# We need to update the green_template_structure to point to its own content
# But since the structure is generic (referring to 'sections.intro'), we can copy it
# However, the 'bg_image' in the structure refers to global assets or specific paths.
# Those paths are valid for everyone using this template.

template_bot_data["green_template_structure"] = copy.deepcopy(eric_data["green_template_structure"])

# 4. Construct New Root
new_root = {
    "users": {
        "eric": eric_data,
        "template_bot": template_bot_data
    },
    "pdf_assets": current_data.get('pdf_assets', [])
}

# Save
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(new_root, f, ensure_ascii=False, indent=2)

print("Refactored data.json for multi-user support.")

