#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Markdown文件生成视频剧本PDF
使用reportlab生成彩色PDF文档
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
import sys
import re

# 注册中文字体
try:
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',
        'C:/Windows/Fonts/simhei.ttf',
        'C:/Windows/Fonts/simsun.ttc',
    ]
    
    chinese_font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            chinese_font = font_path
            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
            print(f"已注册字体: {font_path}")
            break
    
    if not chinese_font:
        print("警告: 未找到中文字体，将使用默认字体")
        chinese_font = 'Helvetica'
except Exception as e:
    print(f"字体注册失败: {e}")
    chinese_font = 'Helvetica'

# 创建样式
styles = getSampleStyleSheet()

# 标题样式
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='ChineseFont' if chinese_font else 'Helvetica-Bold'
)

# 章节标题样式
section_style = ParagraphStyle(
    'CustomSection',
    parent=styles['Heading2'],
    fontSize=18,
    textColor=colors.HexColor('#2196F3'),
    spaceAfter=20,
    spaceBefore=20,
    fontName='ChineseFont' if chinese_font else 'Helvetica-Bold'
)

# 小节标题样式
subsection_style = ParagraphStyle(
    'CustomSubsection',
    parent=styles['Heading3'],
    fontSize=14,
    textColor=colors.HexColor('#1976D2'),
    spaceAfter=12,
    fontName='ChineseFont' if chinese_font else 'Helvetica-Bold'
)

# 正文样式
body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=11,
    textColor=colors.HexColor('#333333'),
    spaceAfter=8,
    leading=16,
    alignment=TA_JUSTIFY,
    fontName='ChineseFont' if chinese_font else 'Helvetica'
)

# 强调样式
emphasize_style = ParagraphStyle(
    'EmphasizeStyle',
    parent=body_style,
    fontSize=12,
    textColor=colors.HexColor('#d63384'),
    fontName='ChineseFont' if chinese_font else 'Helvetica-Bold'
)

bullet_style = ParagraphStyle(
    'BulletStyle',
    parent=styles['Normal'],
    fontSize=11,
    textColor=colors.HexColor('#333333'),
    spaceAfter=8,
    leftIndent=20,
    fontName='ChineseFont' if chinese_font else 'Helvetica'
)

def parse_markdown_file(file_path):
    """解析Markdown文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = []
    lines = content.split('\n')
    
    current_section = None
    current_subsection = None
    
    for line in lines:
        # 检测主标题（##）
        if line.startswith('## '):
            title = line[3:].strip()
            if current_section:
                sections.append(current_section)
            current_section = {
                'title': title,
                'subsections': []
            }
        
        # 检测小标题（###）
        elif line.startswith('### '):
            title = line[4:].strip()
            if current_section:
                current_subsection = {
                    'title': title,
                    'content': []
                }
                current_section['subsections'].append(current_subsection)
        
        # 内容行
        elif current_subsection is not None and line.strip():
            # 提取【镜头】和【主持人讲解】
            if line.strip().startswith('**【镜头】**'):
                if '镜头' not in current_subsection:
                    current_subsection['镜头'] = []
                continue
            elif line.strip().startswith('**【主持人讲解】**'):
                if '讲解' not in current_subsection:
                    current_subsection['讲解'] = []
                continue
            elif line.strip() and (line.strip().startswith('-') or line.strip().startswith('1.')):
                current_subsection['content'].append(line)
            else:
                current_subsection['content'].append(line)
    
    if current_section:
        sections.append(current_section)
    
    return sections

def create_pdf_from_sections(sections, output_path):
    """从解析的章节创建PDF"""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    story = []
    
    # 封面
    if sections:
        first_title = sections[0]['title'] if sections else '视频剧本'
        story.append(Paragraph(first_title, title_style))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph('多传感器厨房空气监测系统', styles['Title']))
        story.append(Spacer(1, 2*cm))
    
    # 项目信息
    info_data = [
        ['项目名称', '多传感器厨房空气监测系统'],
        ['实验类型', 'Arduino + 多传感器 + Python Web应用'],
        ['录制时长', '20-25分钟'],
        ['传感器数量', '4个（DHT11、MQ7、MQ135、声音）'],
        ['创建日期', '2025-01-22'],
        ['版本', 'v2.0']
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if chinese_font else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(info_table)
    
    story.append(PageBreak())
    
    # 添加各章节内容（简化版）
    for section in sections[:8]:  # 只处理前8个主章节
        story.append(Paragraph(section['title'], section_style))
        
        for subsection in section['subsections'][:3]:  # 每个章节最多3个子节
            if subsection['title']:
                story.append(Paragraph(subsection['title'], subsection_style))
            
            # 添加内容
            for line in subsection.get('content', [])[:10]:  # 每节最多10行
                if line.strip() and not line.strip().startswith('**'):
                    # 移除Markdown标记
                    clean_line = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
                    clean_line = clean_line.replace('**', '')
                    if clean_line.strip():
                        story.append(Paragraph(clean_line.strip(), body_style))
        
        story.append(Spacer(1, 1*cm))
    
    # 生成PDF
    doc.build(story)
    print(f"\nPDF已生成: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path) / 1024:.2f} KB")

if __name__ == '__main__':
    print("=" * 50)
    print("从Markdown生成视频剧本PDF")
    print("=" * 50)
    
    markdown_file = 'docs/视频剧本.md'
    pdf_file = 'docs/视频剧本.pdf'
    
    if not os.path.exists(markdown_file):
        print(f"错误: 找不到文件 {markdown_file}")
        sys.exit(1)
    
    try:
        sections = parse_markdown_file(markdown_file)
        print(f"解析了 {len(sections)} 个章节")
        create_pdf_from_sections(sections, pdf_file)
        print("\n生成完成！")
    except Exception as e:
        print(f"\n生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

