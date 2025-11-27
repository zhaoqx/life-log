import pdfplumber
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.join('study', 'resume', 'template')
original_pdf = os.path.join(base_dir, '简历模板1.pdf')
generated_pdf = os.path.join(base_dir, '生成的网站.pdf')

def analyze_page(page):
    return {
        "width": float(page.width),
        "height": float(page.height),
        "text": page.extract_text() or "",
        "images": len(page.images),
        "rects": len(page.rects)
    }

def compare(path1, path2):
    if not os.path.exists(path1):
        print(f"File not found: {path1}")
        return
    if not os.path.exists(path2):
        print(f"File not found: {path2}")
        return

    print(f"Comparing:\n A: {os.path.basename(path1)}\n B: {os.path.basename(path2)}\n")

    with pdfplumber.open(path1) as pdf1, pdfplumber.open(path2) as pdf2:
        print(f"Total Pages: A={len(pdf1.pages)}, B={len(pdf2.pages)}")
        
        min_pages = min(len(pdf1.pages), len(pdf2.pages))
        
        for i in range(min_pages):
            print(f"\n--- Page {i+1} ---")
            p1 = analyze_page(pdf1.pages[i])
            p2 = analyze_page(pdf2.pages[i])
            
            # Dimension Check
            print(f"Dimensions: A={p1['width']:.1f}x{p1['height']:.1f}, B={p2['width']:.1f}x{p2['height']:.1f}")
            
            # Text Content Similarity (Simple Jaccard or length)
            text1 = p1['text'].replace('\n', '').replace(' ', '')
            text2 = p2['text'].replace('\n', '').replace(' ', '')
            print(f"Text Length: A={len(text1)}, B={len(text2)}")
            
            # Visual Elements
            print(f"Images: A={p1['images']}, B={p2['images']}")
            print(f"Vectors (Rects): A={p1['rects']}, B={p2['rects']}")
            
            # Content sample
            if len(text1) > 0 and len(text2) > 0:
                print(f"Sample Text A: {text1[:30]}...")
                print(f"Sample Text B: {text2[:30]}...")

compare(original_pdf, generated_pdf)

