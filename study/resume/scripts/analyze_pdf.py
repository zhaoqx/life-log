import pdfplumber
import sys
import os

# Set encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

pdf_path = os.path.join('study', 'resume', 'template', '简历模板1.pdf')

print(f"Analyzing {pdf_path}...")

try:
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        
        print(f"Page size: {page.width} x {page.height}")
        
        print("\n--- TEXT EXTRACT ---")
        text = page.extract_text()
        print(text[:500] + "..." if len(text) > 500 else text)
        
        print("\n--- TABLES (Lattice) ---")
        # Lattice finds tables using lines
        tables = page.extract_tables(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})
        for i, table in enumerate(tables):
            print(f"Table {i}: {len(table)} rows")
            for row in table[:3]: # Show first 3 rows
                clean_row = [str(cell).strip().replace('\n', ' ') if cell else '' for cell in row]
                print(f"  {clean_row}")
        
        print("\n--- GRAPHICS (Lines/Rects) ---")
        print(f"Lines: {len(page.lines)}")
        print(f"Rects: {len(page.rects)}")
        
        if page.rects:
            print("Sample Rects (Color/Position):")
            for r in page.rects[:5]:
                print(f"  Pos: ({r['x0']:.1f}, {r['top']:.1f}), Size: {r['width']:.1f}x{r['height']:.1f}, Color: {r.get('non_stroking_color')}")

        print("\n--- COLORS FROM CHARS ---")
        # Sample some characters to see colors (headers usually colored)
        chars = page.chars[:100]
        colors = set()
        for c in page.chars:
            if 'size' in c and c['size'] > 12: # Likely header
                color = c.get('non_stroking_color')
                if color: colors.add(str(color))
        print(f"Header Colors found: {colors}")

except Exception as e:
    print(f"Error: {e}")

