import pdfplumber
import os
import json
from PIL import Image

# Setup paths
base_dir = os.path.join('study', 'resume')
pdf_path = os.path.join(base_dir, 'template', '简历模板1.pdf')
output_dir = os.path.join(base_dir, 'web_build', 'assets', 'template_pdf')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

pdf_data = {"images": []}

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    page_bbox = page.bbox
    print(f"Page BBox: {page_bbox}")

    for i, img_obj in enumerate(page.images):
        if img_obj['width'] > 50:
            # Safe crop: clamp to page bounds
            x0 = max(0, float(img_obj['x0']))
            top = max(0, float(img_obj['top']))
            x1 = min(float(page.width), float(img_obj['x1']))
            bottom = min(float(page.height), float(img_obj['bottom']))
            
            # Ensure valid rect
            if x1 > x0 and bottom > top:
                bbox = (x0, top, x1, bottom)
                print(f"Extracting image {i} with safe bbox: {bbox}")
                
                try:
                    cropped = page.crop(bbox).to_image(resolution=150)
                    img_name = f"extracted_asset_{i}.png"
                    img_path = os.path.join(output_dir, img_name)
                    cropped.save(img_path)
                    
                    pdf_data["images"].append({
                        "path": f"assets/template_pdf/{img_name}",
                        "bbox": bbox,
                        "type": "background" if i == 0 else "photo" 
                    })
                except Exception as e:
                    print(f"Error extracting image {i}: {e}")

# Save meta
with open(os.path.join(output_dir, 'meta.json'), 'w', encoding='utf-8') as f:
    json.dump(pdf_data, f)

