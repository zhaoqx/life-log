import pdfplumber
import os
import json
from PIL import Image
import io

# Setup paths
base_dir = os.path.join('study', 'resume')
pdf_path = os.path.join(base_dir, 'template', '简历模板1.pdf')
output_dir = os.path.join(base_dir, 'web_build', 'assets', 'template_pdf')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Processing {pdf_path}...")

pdf_data = {
    "text": [],
    "images": [],
    "rects": []
}

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    
    # Extract Text with layout info
    words = page.extract_words()
    pdf_data["text"] = words
    print(f"Found {len(words)} text elements.")
    
    # Extract Rects (for layout lines/blocks)
    pdf_data["rects"] = page.rects
    print(f"Found {len(page.rects)} vector rectangles.")
    
    # Extract Images
    for i, img_obj in enumerate(page.images):
        try:
            # Extract raw image bytes
            # Note: pdfplumber extraction can be tricky. 
            # We often need to use the stream data if accessible.
            # Here we try a generic approach if possible or just note dimensions.
            
            # Simplified: We will try to crop the page area for the image 
            # or extraction if valid.
            # For strict templating, we often need the background graphics.
            
            rect = (img_obj['x0'], img_obj['top'], img_obj['x1'], img_obj['bottom'])
            print(f"Image {i}: {rect}")
            
            # Since direct stream extraction is complex without extra libs, 
            # we will crop the page to get the visual asset if it's substantial.
            # But pdfplumber's `to_image()` is best for this.
            pass
        except Exception as e:
            print(f"Error extracting image {i}: {e}")

    # Render page to image for analysis/debugging and potential background usage
    im = page.to_image(resolution=150)
    preview_path = os.path.join(output_dir, "page_preview.png")
    im.save(preview_path)
    print(f"Saved page preview to {preview_path}")
    
    # Try to extract the sidebar background or specific graphic elements
    # if they are large images.
    for i, img_obj in enumerate(page.images):
        if img_obj['width'] > 100:
            # Likely a background or photo
            # We crop this area from the rendered page to ensure we get the visual
            # (including transparency effects if any)
            bbox = (img_obj['x0'], img_obj['top'], img_obj['x1'], img_obj['bottom'])
            # Crop expects (x0, top, x1, bottom)
            cropped = page.crop(bbox).to_image(resolution=150)
            img_name = f"extracted_asset_{i}.png"
            img_path = os.path.join(output_dir, img_name)
            cropped.save(img_path)
            pdf_data["images"].append({
                "path": f"assets/template_pdf/{img_name}",
                "bbox": bbox,
                "width": img_obj['width'],
                "height": img_obj['height']
            })

# Save analysis
with open(os.path.join(output_dir, 'layout_analysis.json'), 'w', encoding='utf-8') as f:
    json.dump(pdf_data, f, default=str, indent=2)

print("Extraction complete.")

