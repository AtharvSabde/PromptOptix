"""Convert results_section.md to PDF using markdown + xhtml2pdf."""
import markdown
from xhtml2pdf import pisa

# Read the markdown file
with open("results_section.md", "r", encoding="utf-8") as f:
    md_content = f.read()

# Convert markdown to HTML with table support
html_body = markdown.markdown(md_content, extensions=["tables", "fenced_code"])

# Wrap in a styled HTML document
html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    @page {{
        size: A4;
        margin: 2cm 2.5cm;
    }}
    body {{
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 11pt;
        line-height: 1.5;
        color: #1a1a1a;
    }}
    h1 {{
        font-size: 20pt;
        font-weight: bold;
        margin-top: 0;
        margin-bottom: 10pt;
        color: #111;
        border-bottom: 2px solid #333;
        padding-bottom: 5pt;
    }}
    h2 {{
        font-size: 15pt;
        font-weight: bold;
        margin-top: 18pt;
        margin-bottom: 8pt;
        color: #222;
    }}
    h3 {{
        font-size: 12pt;
        font-weight: bold;
        margin-top: 12pt;
        margin-bottom: 5pt;
        color: #333;
    }}
    p {{
        margin-bottom: 7pt;
        text-align: justify;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 10pt 0;
        font-size: 9pt;
    }}
    th {{
        background-color: #e8e8e8;
        border: 1px solid #999;
        padding: 4pt 6pt;
        text-align: center;
        font-weight: bold;
    }}
    td {{
        border: 1px solid #bbb;
        padding: 3pt 6pt;
        text-align: center;
    }}
    strong {{
        color: #111;
    }}
    em {{
        font-style: italic;
    }}
    hr {{
        border: none;
        border-top: 1px solid #ccc;
        margin: 14pt 0;
    }}
    ol, ul {{
        margin-bottom: 7pt;
        padding-left: 18pt;
    }}
    li {{
        margin-bottom: 3pt;
    }}
    code {{
        font-family: Consolas, 'Courier New', monospace;
        font-size: 9pt;
        background-color: #f4f4f4;
        padding: 1pt 2pt;
    }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

# Generate PDF
output_path = "results_section.pdf"
with open(output_path, "wb") as pdf_file:
    status = pisa.CreatePDF(html_doc, dest=pdf_file)

if status.err:
    print(f"Error generating PDF: {status.err}")
else:
    print(f"PDF generated successfully: {output_path}")
