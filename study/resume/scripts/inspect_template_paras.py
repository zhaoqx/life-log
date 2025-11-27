import os
from docx import Document
import sys

# Set encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

def analyze_template_paras(path):
    print(f"Analyzing template: {path}")
    doc = Document(path)
    
    print("\n--- PARAGRAPHS ---")
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip():
            print(f"P{i}: {p.text.strip()}")

base_dir = os.path.join('study', 'resume', 'template')
template_path = os.path.join(base_dir, '（01）升学简历word【小升初】.docx')

analyze_template_paras(template_path)

