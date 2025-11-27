import os
import glob
import json
import pandas as pd
from PIL import Image
import datetime
import shutil

# --- Configuration ---
BASE_DIR = os.path.join('study', 'resume')
OUTPUT_DIR = os.path.join(BASE_DIR, 'web_build')
IMG_DIR = os.path.join(OUTPUT_DIR, 'images')

if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

# --- Data Extraction ---
def load_data():
    data = {}
    
    # 1. Profile
    profile_path = os.path.join(BASE_DIR, 'profile.xlsx')
    if os.path.exists(profile_path):
        try:
            df = pd.read_excel(profile_path)
            vals = df.values.flatten()
            for i, val in enumerate(vals):
                s = str(val).strip().replace(' ', '')
                if s == '姓名' and i+1 < len(vals): data['Name'] = str(vals[i+1])
                if s == '性别' and i+1 < len(vals): data['Gender'] = str(vals[i+1])
                if s == '出生日期' and i+1 < len(vals): 
                    # Handle date formatting
                    d = vals[i+1]
                    if isinstance(d, (int, float)):
                        dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=d)
                        data['Birthday'] = dt.strftime('%Y-%m')
                    else:
                        data['Birthday'] = str(d)
                if s == '身高' and i+1 < len(vals): data['Height'] = str(vals[i+1])
        except Exception as e:
            print(f"Error reading profile: {e}")

    # 2. Extract content from V3 docx (using python-docx)
    from docx import Document
    v3_files = glob.glob(os.path.join(BASE_DIR, '*v3*修改版.docx'))
    data['Content'] = []
    if v3_files:
        try:
            doc = Document(v3_files[0])
            for p in doc.paragraphs:
                if p.text.strip():
                    data['Content'].append(p.text.strip())
        except:
            pass
            
    # Classify Content
    data['Sections'] = {
        '特长': [],
        '荣誉': [],
        '活动': [],
        '介绍': []
    }
    
    for line in data.get('Content', []):
        if len(line) < 2: continue
        if any(k in line for k in ['姓名', '性别', '表格', '出生']): continue
        
        if '围棋' in line or '特长' in line:
            data['Sections']['特长'].append(line)
        elif '奖' in line or '荣誉' in line or '证书' in line or '杯' in line:
            data['Sections']['荣誉'].append(line)
        elif '足球' in line or '活动' in line or '志愿者' in line:
            data['Sections']['活动'].append(line)
        elif len(line) > 30: # Long paragraphs assumed to be intro/desc
            data['Sections']['介绍'].append(line)

    return data

# --- Image Processing ---
def process_images():
    cert_dir = os.path.join(BASE_DIR, 'certificate')
    processed_images = []
    
    if os.path.exists(cert_dir):
        for root, _, files in os.walk(cert_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    src_path = os.path.join(root, f)
                    # Create a clean filename
                    safe_name = f.replace(' ', '_')
                    dst_path = os.path.join(IMG_DIR, safe_name)
                    
                    try:
                        with Image.open(src_path) as img:
                            # Resize if too large (max 1000px width)
                            max_width = 800
                            if img.width > max_width:
                                ratio = max_width / img.width
                                new_height = int(img.height * ratio)
                                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                            
                            # Convert to RGB if needed (for JPG)
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                                
                            # Save compressed
                            img.save(dst_path, quality=70, optimize=True)
                            processed_images.append({
                                'path': f'images/{safe_name}',
                                'name': os.path.splitext(f)[0]
                            })
                    except Exception as e:
                        print(f"Error processing {f}: {e}")
                        
    return processed_images

# --- HTML Generation ---
def generate_html(data, images):
    # CSS for A4 Paper look
    css = """
    <style>
        body {
            background: #f0f0f0;
            font-family: "Microsoft YaHei", sans-serif;
            margin: 0;
            padding: 20px;
        }
        .page {
            background: white;
            width: 210mm;
            min-height: 297mm;
            margin: 0 auto;
            padding: 20mm;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            box-sizing: border-box;
            position: relative;
        }
        @media print {
            body { background: none; margin: 0; padding: 0; }
            .page { width: 100%; box-shadow: none; margin: 0; padding: 20mm; page-break-after: always; }
            .no-print { display: none; }
        }
        
        /* Resume Styles matching the Template */
        h1.main-title {
            text-align: center;
            color: #005294;
            font-size: 24pt;
            margin-bottom: 5px;
            letter-spacing: 5px;
        }
        .divider {
            border-top: 2px solid #ccc;
            margin: 10px 0 20px 0;
        }
        
        .section-title {
            color: #0070c0;
            font-size: 14pt;
            font-weight: bold;
            border-bottom: 2px solid #0070c0;
            padding-bottom: 5px;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        .section-title::before {
            content: "◆ ";
        }
        
        /* Table Styles */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }
        td, th {
            border: 1px solid #999;
            padding: 8px;
            text-align: center;
            font-size: 11pt;
        }
        .label-cell {
            background-color: #e8f4fc;
            color: #005294;
            font-weight: bold;
            width: 15%;
        }
        .value-cell {
            width: 35%;
            text-align: left;
            padding-left: 15px;
        }
        
        /* Grade Table */
        .grade-header {
            background-color: #0070c0;
            color: white;
            font-weight: bold;
        }
        .grade-row-header {
            background-color: #e8f4fc;
        }
        
        /* List Styles */
        ul.custom-list {
            list-style: none;
            padding-left: 0;
        }
        ul.custom-list li {
            margin-bottom: 8px;
            padding-left: 20px;
            position: relative;
        }
        ul.custom-list li::before {
            content: "◇";
            position: absolute;
            left: 0;
            color: #0070c0;
        }
        
        /* Photo Grid */
        .photo-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        .photo-item {
            text-align: center;
            border: 1px solid #ddd;
            padding: 10px;
            break-inside: avoid;
        }
        .photo-item img {
            max-width: 100%;
            height: auto;
            max-height: 300px;
        }
        .photo-caption {
            margin-top: 8px;
            font-size: 10pt;
            color: #666;
        }
        
        /* Controls */
        .controls {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        button {
            background: #0070c0;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover { background: #005294; }
    </style>
    """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>赵Eric - 小升初简历</title>
        {css}
    </head>
    <body>
        <div class="controls no-print">
            <button onclick="window.print()">打印 / 另存为PDF</button>
            <div style="margin-top:10px; font-size:12px; color:#666;">
                提示: 打印时请勾选"背景图形"
            </div>
        </div>

        <!-- Page 1: Resume -->
        <div class="page">
            <h1 class="main-title">【 个 人 简 历 】</h1>
            <div class="divider"></div>
            
            <div class="section-title">基本信息</div>
            <table>
                <tr>
                    <td class="label-cell">姓 名</td>
                    <td class="value-cell">{data.get('Name', '赵Eric')}</td>
                    <td class="label-cell">性 别</td>
                    <td class="value-cell">{data.get('Gender', '男')}</td>
                </tr>
                <tr>
                    <td class="label-cell">出生日期</td>
                    <td class="value-cell">{data.get('Birthday', '')}</td>
                    <td class="label-cell">身 高</td>
                    <td class="value-cell">{data.get('Height', '')}</td>
                </tr>
                <tr>
                    <td class="label-cell">所在小学</td>
                    <td class="value-cell">（请填写）</td>
                    <td class="label-cell">户籍所在</td>
                    <td class="value-cell">（请填写）</td>
                </tr>
                <tr>
                    <td class="label-cell">联系电话</td>
                    <td class="value-cell">（请填写）</td>
                    <td class="label-cell">家庭住址</td>
                    <td class="value-cell">（请填写）</td>
                </tr>
            </table>
            
            <div class="section-title">学业成绩</div>
            <table>
                <tr class="grade-header">
                    <td>学期</td>
                    <td>语文</td>
                    <td>数学</td>
                    <td>英语</td>
                </tr>
                <tr>
                    <td class="grade-row-header">五年级上学期</td>
                    <td>100</td>
                    <td>96</td>
                    <td>98</td>
                </tr>
                <tr>
                    <td class="grade-row-header">五年级下学期</td>
                    <td>98</td>
                    <td>98</td>
                    <td>96</td>
                </tr>
            </table>
            
            <div class="section-title">特长与证书</div>
            <ul class="custom-list">
                {"".join(f'<li>{item}</li>' for item in data['Sections']['特长'])}
                <li>围棋业余二段</li>
            </ul>
            
            <div class="section-title">荣誉奖励</div>
            <ul class="custom-list">
                {"".join(f'<li>{item}</li>' for item in data['Sections']['荣誉'])}
                <li>钟书阁读书会获奖作文</li>
            </ul>
            
            <div class="section-title">课外活动</div>
            <ul class="custom-list">
                {"".join(f'<li>{item}</li>' for item in data['Sections']['活动'])}
                <li>校足球队队员</li>
            </ul>
            
            <div class="section-title">自我介绍</div>
            <div style="line-height: 1.6; text-indent: 2em;">
                {"<br>".join(data['Sections']['介绍']) if data['Sections']['介绍'] else "（自我介绍内容）"}
            </div>
        </div>
        
        <!-- Page 2+: Photos -->
        <div class="page">
            <h1 class="main-title" style="font-size: 18pt;">证书与风采展示</h1>
            <div class="divider"></div>
            
            <div class="photo-grid">
                {"".join(f'''
                <div class="photo-item">
                    <img src="{img['path']}" alt="{img['name']}">
                    <div class="photo-caption">{img['name']}</div>
                </div>
                ''' for img in images)}
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(OUTPUT_DIR, 'resume.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    return os.path.join(OUTPUT_DIR, 'resume.html')

def main():
    print("Step 1: Loading Data...")
    data = load_data()
    
    print("Step 2: Processing Images (Compression)...")
    images = process_images()
    
    print("Step 3: Generating Web Resume...")
    html_path = generate_html(data, images)
    
    print(f"Done! Web resume generated at: {html_path}")
    print("Images have been compressed and embedded.")

if __name__ == '__main__':
    main()

