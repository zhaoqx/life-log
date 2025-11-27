import os
import sys
import win32com.client

# Set encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

def convert_doc_to_docx(doc_path):
    word = None
    doc = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        abs_doc_path = os.path.abspath(doc_path)
        print(f"Opening: {abs_doc_path}")
        
        doc = word.Documents.Open(abs_doc_path)
        
        docx_path = abs_doc_path + "x"
        print(f"Saving as: {docx_path}")
        
        # FileFormat=12 is wdFormatXMLDocument (docx)
        doc.SaveAs2(docx_path, FileFormat=12)
        return docx_path
    except Exception as e:
        print(f"Error converting: {e}")
        return None
    finally:
        if doc:
            doc.Close()
        if word:
            word.Quit()

base_dir = os.path.join('study', 'resume', 'template')
doc_file = os.path.join(base_dir, '小升初简历模板1.doc')

if os.path.exists(doc_file):
    print("Found .doc file")
    new_path = convert_doc_to_docx(doc_file)
    if new_path:
        print(f"Conversion successful: {new_path}")
else:
    print(f"File not found: {doc_file}")

