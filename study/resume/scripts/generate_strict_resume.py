import os
import glob
import pandas as pd
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

# --- Helper Functions ---

def set_cell_background(cell, color_hex):
    """Set cell background color (e.g., 'E8F4FC')"""
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), color_hex)
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_run_font(run, font_name='微软雅黑', font_size=11, bold=False, color=None):
    """Set font properties"""
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_heading_paragraph(doc, text, font_size=22, bold=True, color=(0, 112, 192), align='center'):
    """Add a main heading"""
    para = doc.add_paragraph()
    if align == 'center':
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run(text)
    set_run_font(run, font_size=font_size, bold=bold, color=color)
    return para

def add_section_title(doc, text):
    """Add a section title with specific styling"""
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = para.add_run('◆ ' + text)
    set_run_font(run, font_size=14, bold=True, color=(0, 112, 192))
    para.paragraph_format.space_before = Pt(12)
    para.paragraph_format.space_after = Pt(6)
    return para

def excel_date_to_str(serial):
    try:
        if isinstance(serial, (int, float)):
            dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=serial)
            return dt.strftime('%Y年%m月')
        return str(serial)
    except:
        return str(serial)

# --- Data Loading ---

def load_data(base_dir):
    data = {}
    
    # 1. Profile
    profile_path = os.path.join(base_dir, 'profile.xlsx')
    if os.path.exists(profile_path):
        try:
            df = pd.read_excel(profile_path)
            vals = df.values.flatten()
            for i, val in enumerate(vals):
                s = str(val).strip().replace(' ', '')
                if s == '姓名' and i+1 < len(vals): data['Name'] = str(vals[i+1])
                if s == '性别' and i+1 < len(vals): data['Gender'] = str(vals[i+1])
                if s == '出生日期' and i+1 < len(vals): data['Birthday'] = excel_date_to_str(vals[i+1])
                if s == '身高' and i+1 < len(vals): data['Height'] = str(vals[i+1])
        except Exception as e:
            print(f"Error reading profile: {e}")

    # 2. V3 Resume Content (for detailed sections)
    v3_path = glob.glob(os.path.join(base_dir, '*v3*修改版.docx'))
    data['Content'] = []
    if v3_path:
        try:
            doc = Document(v3_path[0])
            for p in doc.paragraphs:
                if p.text.strip():
                    data['Content'].append(p.text.strip())
        except Exception as e:
            print(f"Error reading v3: {e}")
            
    # 3. Photos
    cert_dir = os.path.join(base_dir, 'certificate')
    data['Photos'] = []
    if os.path.exists(cert_dir):
        for root, _, files in os.walk(cert_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.png', '.jpeg')):
                    data['Photos'].append(os.path.join(root, f))
                    
    return data

# --- Resume Generation ---

def create_resume_strict():
    base_dir = os.path.join('study', 'resume')
    data = load_data(base_dir)
    
    doc = Document()
    
    # Margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2)
        section.right_margin = Cm(2)

    # Title
    add_heading_paragraph(doc, '【 个 人 简 历 】', font_size=28, bold=True, color=(0, 82, 148))
    
    # Divider
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run('━' * 40)
    set_run_font(run, font_size=10, color=(200, 200, 200))

    # 1. 基本信息 (Table)
    add_section_title(doc, '基本信息')
    table = doc.add_table(rows=4, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    info_rows = [
        ('姓    名', data.get('Name', '赵Eric'), '性    别', data.get('Gender', '男')),
        ('出生日期', data.get('Birthday', '2013年12月'), '身    高', data.get('Height', '165cm')),
        ('所在小学', '（请填写）', '户籍所在', '（请填写）'),
        ('联系电话', '（请填写）', '家庭住址', '（请填写）'),
    ]
    
    for i, r_data in enumerate(info_rows):
        row = table.rows[i]
        for j, text in enumerate(r_data):
            cell = row.cells[j]
            cell.text = ''
            p = cell.paragraphs[0]
            run = p.add_run(text)
            if j % 2 == 0: # Label
                set_run_font(run, font_size=11, bold=True, color=(0, 82, 148))
                set_cell_background(cell, 'E8F4FC')
            else: # Value
                set_run_font(run, font_size=11)
                
    # 2. 学业成绩 (Table)
    add_section_title(doc, '学业成绩')
    g_table = doc.add_table(rows=3, cols=4)
    g_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    g_data = [
        ('学期', '语文', '数学', '英语'),
        ('五年级上学期', '100', '96', '98'),
        ('五年级下学期', '98', '98', '96'),
    ]
    for i, r_data in enumerate(g_data):
        row = g_table.rows[i]
        for j, text in enumerate(r_data):
            cell = row.cells[j]
            cell.text = ''
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(text)
            if i == 0:
                set_run_font(run, font_size=11, bold=True, color=(255, 255, 255))
                set_cell_background(cell, '0070C0')
            else:
                set_run_font(run, font_size=11)
                if j == 0: set_cell_background(cell, 'E8F4FC')

    # 3. Dynamic Sections from V3 Content
    # We parse the V3 content to classify items if possible, otherwise list them carefully
    # Common headers in resumes: 特长, 荣誉, 活动, 介绍
    
    current_section = None
    
    # Pre-defined sections we want to populate
    sections = {
        '特长': [],
        '荣誉': [],
        '活动': [],
        '介绍': []
    }
    
    # Simple keyword classification of paragraphs from V3
    for line in data['Content']:
        if len(line) < 2: continue
        if any(k in line for k in ['姓名', '性别', '表格']): continue # Skip basic info
        
        if '围棋' in line or '特长' in line:
            sections['特长'].append(line)
        elif '奖' in line or '荣誉' in line or '证书' in line or '杯' in line:
            sections['荣誉'].append(line)
        elif '足球' in line or '活动' in line or '志愿者' in line:
            sections['活动'].append(line)
        elif '我' in line and len(line) > 20:
            sections['介绍'].append(line)
        else:
            # Fallback
            pass

    # Fill Sections
    if sections['特长']:
        add_section_title(doc, '特长与证书')
        for line in sections['特长']:
            p = doc.add_paragraph('◇ ' + line)
            set_run_font(p.runs[0], font_size=11)
            p.paragraph_format.left_indent = Cm(0.5)

    if sections['荣誉']:
        add_section_title(doc, '荣誉奖励')
        for line in sections['荣誉']:
            p = doc.add_paragraph('◇ ' + line)
            set_run_font(p.runs[0], font_size=11)
            p.paragraph_format.left_indent = Cm(0.5)

    if sections['活动']:
        add_section_title(doc, '课外活动')
        for line in sections['活动']:
            p = doc.add_paragraph('◇ ' + line)
            set_run_font(p.runs[0], font_size=11)
            p.paragraph_format.left_indent = Cm(0.5)

    add_section_title(doc, '自我介绍')
    intro_text = "\n".join(sections['介绍']) if sections['介绍'] else "（此处填写自我介绍）"
    # If empty, use a default good one or the one from v3 if we missed it
    if len(intro_text) < 10:
        # Try to find long paragraphs in content
        long_paras = [l for l in data['Content'] if len(l) > 50]
        if long_paras:
            intro_text = "\n".join(long_paras)
    
    p = doc.add_paragraph(intro_text)
    set_run_font(p.add_run(), font_size=11)
    p.paragraph_format.line_spacing = 1.5

    # Photos
    if data['Photos']:
        doc.add_page_break()
        add_heading_paragraph(doc, '【 证 书 与 风 采 】', font_size=18, bold=True, color=(0, 82, 148))
        
        # Table for photos
        rows = (len(data['Photos']) + 1) // 2
        p_table = doc.add_table(rows=rows, cols=2)
        p_table.autofit = True
        
        for i, photo_path in enumerate(data['Photos']):
            row_idx = i // 2
            col_idx = i % 2
            cell = p_table.rows[row_idx].cells[col_idx]
            
            # Add image
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            try:
                run.add_picture(photo_path, width=Inches(2.8))
                # Add caption
                caption = os.path.basename(photo_path).split('.')[0]
                p_cap = cell.add_paragraph(caption)
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_run_font(p_cap.add_run(caption), font_size=10, color=(100, 100, 100))
            except Exception as e:
                print(f"Skipping photo {photo_path}: {e}")

    output_path = os.path.join(base_dir, '赵Eric_小升初简历_新模板_2.docx')
    doc.save(output_path)
    print(f"Generated: {output_path}")

if __name__ == '__main__':
    create_resume_strict()

