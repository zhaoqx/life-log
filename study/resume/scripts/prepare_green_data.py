import json
import os
import copy

# --- Configuration ---
WEB_BUILD_DIR = os.path.join('study', 'resume', 'web_build')
DATA_FILE = os.path.join(WEB_BUILD_DIR, 'data.json')
TEMPLATE_META_FILE = os.path.join(WEB_BUILD_DIR, 'assets', 'template_pdf', 'full_template_meta.json')

# Load existing data
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Load template meta to get assets
with open(TEMPLATE_META_FILE, 'r', encoding='utf-8') as f:
    template_meta = json.load(f)

# Map assets to easy keys
assets = {}
for page in template_meta['pages']:
    for img in page['images']:
        # Key by page num and index
        key = f"p{page['page_num']}_{os.path.basename(img['path'])}"
        assets[key] = img['path']

# Create a structured multi-page layout data for the green template
# We will use the existing profile/sections data but map them to specific pages
green_layout = [
    # Page 1: Cover / Profile
    {
        "type": "cover",
        "bg_image": assets.get("p1_bg_page_1_0.png", ""),
        "sidebar_width": "35%", # Approx
        "content": "profile_summary"
    },
    # Page 2: Family & Grades
    {
        "type": "table_page",
        "title": "基本信息与成绩",
        "content": "grades_family"
    },
    # Page 3: Self Intro
    {
        "type": "text_page",
        "title": "自荐信",
        "content": "intro"
    },
    # Page 4: Awards List
    {
        "type": "list_page",
        "title": "获奖经历",
        "content": "awards_list"
    },
    # Page 5: Certificates (Gallery)
    {
        "type": "gallery_page",
        "title": "获奖证书",
        "content": "certificates",
        "images": data['attachments'][:4] if data['attachments'] else []
    },
    # Page 6: Hobbies
    {
        "type": "text_page",
        "title": "兴趣爱好",
        "content": "hobbies"
    },
    # Page 7: Social Practice
    {
        "type": "mixed_page",
        "title": "社会实践",
        "content": "activities",
        "images": data['attachments'][4:6] if len(data['attachments']) > 4 else []
    },
    # Page 8: Life Photos
    {
        "type": "gallery_page",
        "title": "我的生活",
        "content": "life",
        "images": data['attachments'][6:] if len(data['attachments']) > 6 else []
    },
    # Page 9: Comments
    {
        "type": "text_page",
        "title": "寄语",
        "content": "comments"
    },
    # Page 10: Back Cover
    {
        "type": "back_cover",
        "bg_image": assets.get("p10_bg_page_10_0.png", "")
    }
]

data['green_template_structure'] = green_layout

# Ensure we have an avatar separate from attachments if possible
# For now, use the first attachment as avatar if not explicit
if data['attachments']:
    data['profile']['avatar'] = data['attachments'][0]['path']
else:
    data['profile']['avatar'] = ""

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated data.json with green_template_structure.")

