import os
import glob
import zipfile
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def extract_text_from_docx(path):
    print(f"Extracting from: {path}")
    try:
        with zipfile.ZipFile(path) as zf:
            xml_content = zf.read('word/document.xml').decode('utf-8')
            # Remove XML tags
            text = re.sub('<[^>]+>', ' ', xml_content)
            # Normalize whitespace
            text = re.sub('\s+', ' ', text).strip()
            return text
    except Exception as e:
        return f"Error: {e}"

base_dir = os.path.join('study', 'resume')
files = glob.glob(os.path.join(base_dir, '*v3*修改版.docx'))
if files:
    print(f"Found file: {files[0]}")
    content = extract_text_from_docx(files[0])
    print(f"Content length: {len(content)}")
    print(f"Snippet: {content[:500]}")
else:
    print("File not found")

print("-" * 30)
templates = glob.glob(os.path.join(base_dir, 'template', '*01*升学*.docx'))
if templates:
    print(f"Found template: {templates[0]}")
    content = extract_text_from_docx(templates[0])
    print(f"Snippet: {content[:500]}")

