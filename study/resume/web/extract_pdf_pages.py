# -*- coding: utf-8 -*-
"""提取PDF各页预览"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

import fitz

pdf_path = Path(__file__).parent.parent / 'template' / '简历模板1.pdf'
output_dir = Path(__file__).parent / 'static' / 'pdf_pages'
output_dir.mkdir(exist_ok=True)

doc = fitz.open(pdf_path)

for page_num in range(min(len(doc), 10)):
    page = doc[page_num]
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
    output_path = output_dir / f'page_{page_num + 1}.png'
    pix.save(str(output_path))
    print(f"已保存: {output_path}")

doc.close()
print(f"\n共保存 {min(len(doc), 10)} 页预览图")

