import sqlite3
import os
import json
import shutil
import glob
import pandas as pd
import datetime

# Configuration
WEB_BUILD_DIR = os.path.join('study', 'resume', 'web_build')
DB_PATH = os.path.join(WEB_BUILD_DIR, 'db', 'resume.db')
ATTACHMENTS_DIR = os.path.join(WEB_BUILD_DIR, 'attachments')
BASE_RESUME_DIR = os.path.join('study', 'resume')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Profile table
    c.execute('''CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY,
        key TEXT UNIQUE,
        value TEXT,
        section TEXT
    )''')
    
    # Sections table (Education, Awards, etc.)
    c.execute('''CREATE TABLE IF NOT EXISTS resume_sections (
        id INTEGER PRIMARY KEY,
        section_name TEXT,
        content TEXT,
        order_index INTEGER
    )''')
    
    # Attachments table
    c.execute('''CREATE TABLE IF NOT EXISTS attachments (
        id INTEGER PRIMARY KEY,
        filename TEXT,
        filepath TEXT,
        type TEXT,
        description TEXT
    )''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def import_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Import Profile
    profile_path = os.path.join(BASE_RESUME_DIR, 'profile.xlsx')
    if os.path.exists(profile_path):
        try:
            df = pd.read_excel(profile_path)
            vals = df.values.flatten()
            profile_map = {}
            for i, val in enumerate(vals):
                s = str(val).strip().replace(' ', '')
                if s == '姓名' and i+1 < len(vals): profile_map['Name'] = str(vals[i+1])
                if s == '性别' and i+1 < len(vals): profile_map['Gender'] = str(vals[i+1])
                if s == '出生日期' and i+1 < len(vals): 
                    d = vals[i+1]
                    if isinstance(d, (int, float)):
                        dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=d)
                        profile_map['Birthday'] = dt.strftime('%Y-%m')
                    else:
                        profile_map['Birthday'] = str(d)
                if s == '身高' and i+1 < len(vals): profile_map['Height'] = str(vals[i+1])
            
            for k, v in profile_map.items():
                c.execute("INSERT OR REPLACE INTO profile (key, value, section) VALUES (?, ?, ?)", (k, v, 'basic'))
        except Exception as e:
            print(f"Profile import error: {e}")

    # 2. Import Resume Content (V3)
    # Parse V3 content into DB sections
    from docx import Document
    v3_files = glob.glob(os.path.join(BASE_RESUME_DIR, '*v3*修改版.docx'))
    
    sections_content = {'特长': [], '荣誉': [], '活动': [], '介绍': []}
    
    if v3_files:
        try:
            doc = Document(v3_files[0])
            for p in doc.paragraphs:
                txt = p.text.strip()
                if len(txt) < 2: continue
                if any(k in txt for k in ['姓名', '性别', '表格']): continue
                
                if '围棋' in txt or '特长' in txt: sections_content['特长'].append(txt)
                elif '奖' in txt or '荣誉' in txt or '证书' in txt: sections_content['荣誉'].append(txt)
                elif '足球' in txt or '活动' in txt or '志愿者' in txt: sections_content['活动'].append(txt)
                elif len(txt) > 30: sections_content['介绍'].append(txt)
        except Exception as e:
            print(f"Content import error: {e}")

    # Save sections to DB
    order = 1
    for sec, items in sections_content.items():
        if items:
            content_json = json.dumps(items, ensure_ascii=False)
            c.execute("INSERT OR REPLACE INTO resume_sections (section_name, content, order_index) VALUES (?, ?, ?)", 
                      (sec, content_json, order))
            order += 1

    # 3. Import Attachments
    # Copy images to attachments folder and record in DB
    cert_dir = os.path.join(BASE_RESUME_DIR, 'certificate')
    if os.path.exists(cert_dir):
        for root, _, files in os.walk(cert_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    src = os.path.join(root, f)
                    safe_name = f.replace(' ', '_')
                    dst = os.path.join(ATTACHMENTS_DIR, safe_name)
                    
                    # Copy file
                    shutil.copy2(src, dst)
                    
                    # DB Entry
                    rel_path = f"attachments/{safe_name}"
                    desc = os.path.splitext(f)[0]
                    c.execute("INSERT INTO attachments (filename, filepath, type, description) VALUES (?, ?, ?, ?)",
                              (safe_name, rel_path, 'image', desc))

    conn.commit()
    conn.close()
    print("Data import completed.")

if __name__ == '__main__':
    if not os.path.exists(WEB_BUILD_DIR):
        os.makedirs(WEB_BUILD_DIR)
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    if not os.path.exists(ATTACHMENTS_DIR):
        os.makedirs(ATTACHMENTS_DIR)
        
    init_db()
    import_data()

