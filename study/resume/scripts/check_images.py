import pdfplumber
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
pdf_path = os.path.join('study', 'resume', 'template', '简历模板1.pdf')

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    print(f"Images: {len(page.images)}")
    if page.images:
        print(page.images[0])

