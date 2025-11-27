import pdfplumber
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = os.path.join('study', 'resume', 'template', '简历模板1.pdf')

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    
    print("--- FULL TEXT ---")
    print(page.extract_text())
    
    print("\n--- TABLES (Stream) ---")
    tables = page.extract_tables(table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"})
    for i, table in enumerate(tables):
        print(f"Table {i}:")
        for row in table:
            print(f"  {row}")

    print("\n--- COLORS ---")
    # Histogram of colors
    colors = {}
    for c in page.chars:
        color = str(c.get('non_stroking_color'))
        colors[color] = colors.get(color, 0) + 1
    
    print("Top colors:")
    for color, count in sorted(colors.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {color}: {count} chars")
        
    print("\n--- RECTS ---")
    # Check if there are colored bars
    for r in page.rects:
        if r['width'] > 100 and r['height'] > 5: # Horizontal bars
            print(f"Bar: {r['width']}x{r['height']} at y={r['top']} Color={r.get('non_stroking_color')}")

