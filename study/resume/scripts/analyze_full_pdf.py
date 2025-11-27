import pdfplumber
import os
import json

# Setup paths
base_dir = os.path.join('study', 'resume')
pdf_path = os.path.join(base_dir, 'template', '简历模板1.pdf')
output_dir = os.path.join(base_dir, 'web_build', 'assets', 'template_pdf')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Analyzing full PDF: {pdf_path}")

pdf_meta = {
    "pages": []
}

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total Pages: {len(pdf.pages)}")
    
    for i, page in enumerate(pdf.pages):
        print(f"Processing Page {i+1}...")
        page_info = {
            "page_num": i + 1,
            "width": float(page.width),
            "height": float(page.height),
            "images": [],
            "text_blocks": []
        }
        
        # Extract Text (to understand structure/headings per page)
        text = page.extract_text()
        if text:
            page_info["text_preview"] = text[:100].replace('\n', ' ')
            # Heuristic to guess page type
            if "简历" in text or "姓名" in text:
                page_info["type"] = "profile"
            elif "证书" in text or "作品" in text:
                page_info["type"] = "gallery"
            else:
                page_info["type"] = "content"
        
        # Extract Background/Images
        # We assume the largest image on the page might be the background
        largest_img = None
        max_area = 0
        
        for j, img in enumerate(page.images):
            w = float(img['width'])
            h = float(img['height'])
            area = w * h
            
            # If image covers significant part of page (e.g. > 20%), treat as layout asset
            if area > (page.width * page.height * 0.1):
                # Crop and save
                bbox = (
                    max(0, float(img['x0'])),
                    max(0, float(img['top'])),
                    min(float(page.width), float(img['x1'])),
                    min(float(page.height), float(img['bottom']))
                )
                
                img_name = f"bg_page_{i+1}_{j}.png"
                img_save_path = os.path.join(output_dir, img_name)
                
                try:
                    # Render just this area from the page to capture visual context
                    cropped = page.crop(bbox).to_image(resolution=150)
                    cropped.save(img_save_path)
                    
                    img_data = {
                        "path": f"assets/template_pdf/{img_name}",
                        "width": w,
                        "height": h,
                        "bbox": bbox,
                        "is_background": area > (page.width * page.height * 0.8) # Full page bg?
                    }
                    page_info["images"].append(img_data)
                except Exception as e:
                    print(f"  Error extracting image {j}: {e}")

        pdf_meta["pages"].append(page_info)

# Save full analysis
with open(os.path.join(output_dir, 'full_template_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(pdf_meta, f, indent=2)

print("Full analysis complete.")

