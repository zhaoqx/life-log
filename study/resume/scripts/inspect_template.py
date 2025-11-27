import os
import glob
from docx import Document
import sys

# Set encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

def analyze_template(path):
    print(f"Analyzing template: {path}")
    doc = Document(path)
    
    print("\n--- TABLES ---")
    for i, table in enumerate(doc.tables):
        print(f"Table {i} ({len(table.rows)}x{len(table.columns)}):")
        for r_idx, row in enumerate(table.rows):
            row_txt = []
            for cell in row.cells:
                row_txt.append(cell.text.strip())
            print(f"  R{r_idx}: {row_txt}")

base_dir = os.path.join('study', 'resume', 'template')
template_path = os.path.join(base_dir, '（01）升学简历word【小升初】.docx')

analyze_template(template_path)

