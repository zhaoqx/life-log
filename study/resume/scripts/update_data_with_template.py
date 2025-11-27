import json
import os
import shutil

# --- Configuration ---
WEB_BUILD_DIR = os.path.join('study', 'resume', 'web_build')
DATA_FILE = os.path.join(WEB_BUILD_DIR, 'data.json')
PDF_META_FILE = os.path.join(WEB_BUILD_DIR, 'assets', 'template_pdf', 'meta.json')

# --- 1. Load Data ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
else:
    print("Error: data.json not found.")
    exit(1)

if os.path.exists(PDF_META_FILE):
    with open(PDF_META_FILE, 'r', encoding='utf-8') as f:
        pdf_meta = json.load(f)
else:
    pdf_meta = {"images": []}

# --- 2. Create Template Sample User ---
# We create a specific "user profile" in the data for the Template PDF
template_profile = {
    "profile": {
        "name": "我的简历",
        "gender": "男",
        "birthday": "2013年05月",
        "height": "160cm",
        "school": "示例小学",
        "hometown": "北京",
        "address": "北京市海淀区...",
        "phone": "13800138000"
    },
    "sections": {
        "intro": ["这里是自我介绍的示例文本..."],
        "specialty": ["围棋五段", "钢琴十级"],
        "awards": ["奥数一等奖", "英语演讲比赛冠军"],
        "activities": ["校足球队队长", "科技社团团长"]
    },
    "grades": [
        {"term": "五年级上", "chinese": "100", "math": "100", "english": "100"}
    ],
    "attachments": [] # Template images as attachments?
}

# Add extracted PDF images as assets
if pdf_meta['images']:
    template_profile['background_image'] = pdf_meta['images'][0]['path']
    if len(pdf_meta['images']) > 1:
         template_profile['photo_image'] = pdf_meta['images'][1]['path']

# Store in data.json under a specific key or list
# For now, let's keep the single-user structure but add a "template_sample" key
data['template_sample'] = template_profile
data['pdf_assets'] = pdf_meta['images']

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated data.json with template sample data.")

