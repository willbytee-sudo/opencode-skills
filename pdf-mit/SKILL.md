---
name: pdf-mit
description: >-
  Use ALWAYS when doing anything with PDF files: reading or extracting text/tables, creating
  new PDFs, merging/splitting, rotating, watermarking, encrypting/decrypting, extracting or
  rendering images, filling forms, and OCR of scans. Built on public Python libraries (pypdf,
  reportlab, pdfplumber, PyMuPDF, pikepdf). Designed for opencode on Windows, with a proofread
  step before delivering. Triggers: "PDF", ".pdf", "merge PDF", "fill form". Do NOT use for
  Word, Excel, or PowerPoint.
metadata:
  origin: independent skill (own implementation, MIT) on top of permissively licensed third-party libraries (pypdf BSD, reportlab BSD, pdfplumber MIT, pikepdf MPL, PyMuPDF AGPL). Not derived from proprietary skills.
  environment: opencode on Windows — Python 3.13 + pypdf + reportlab + pdfplumber + PyMuPDF(fitz) + pikepdf + Pillow
  license: MIT (see LICENSE)
  critical_rule: run ALL scripts with "python -X utf8"; proofread before delivering
---

# PDF on opencode — read, create, edit, forms (public libraries)

## Overview

This skill handles PDFs with the standard Python libraries: **pypdf** (merge/split/rotate/
encrypt/forms), **reportlab** (create), **pdfplumber** (extract text/tables), **PyMuPDF/fitz**
(render to image), and **pikepdf** (repair/optimize). When you create a PDF with your own text,
**proofread** it before delivering.

## How opencode runs this skill (key adaptations — READ FIRST)

1. **`SKILL_DIR` as an absolute path.** opencode runs from the project directory:
   ```bash
   SKILL_DIR="$HOME/.config/opencode/skills/pdf-mit"
   ```
2. **UTF-8 RULE: run Python with `-X utf8` ALWAYS.** Without it, non-ASCII text breaks on Windows (cp1252).
3. **Text NEVER travels through the console.** The `.py` that creates the PDF (reportlab) and
   the form JSON files are written with the file tool (UTF-8), not with echo/here-strings.
4. **The sandbox `extract-text` does NOT exist.** Use `extract_text.py`.
5. **Missing on this machine (plan for it):** OCR (`pytesseract`, `pdf2image`) and Tesseract are
   NOT installed; Poppler and qpdf are NOT installed. The scripts don't need them: image
   conversion uses **PyMuPDF**, and repair/optimize uses **pikepdf** (not qpdf).

## Read / extract text

```bash
python -X utf8 "$SKILL_DIR/scripts/extract_text.py" document.pdf            # text per page
python -X utf8 "$SKILL_DIR/scripts/extract_text.py" document.pdf --tables   # + tables
```

## Create a PDF (reportlab)

Write the `.py` with the file tool (UTF-8) and run it with `python -X utf8`.
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

doc = SimpleDocTemplate("output.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = [
    Paragraph("Management report 2024", styles["Title"]),
    Spacer(1, 12),
    Paragraph("Last year the organization improved its performance.", styles["Normal"]),
    Spacer(1, 12),
    Table([["Year", "Revenue"], ["2024", "$1,234"]],
          style=TableStyle([("GRID", (0, 0), (-1, -1), 1, colors.grey),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)])),
    PageBreak(),
]
doc.build(story)
```
**Sub/superscripts:** do NOT use Unicode characters (₂, ²) — reportlab base fonts lack those
glyphs and they render as black boxes. Use XML markup: `Paragraph("H<sub>2</sub>O", styles["Normal"])`.

## Common operations (pypdf / pikepdf)

```python
from pypdf import PdfReader, PdfWriter

# Merge
w = PdfWriter()
for f in ["a.pdf", "b.pdf"]:
    for pg in PdfReader(f).pages: w.add_page(pg)
w.write("merged.pdf")

# Split (one page per file)
for i, pg in enumerate(PdfReader("input.pdf").pages):
    o = PdfWriter(); o.add_page(pg); o.write(f"page_{i+1}.pdf")

# Rotate 90°, watermark, encrypt
r = PdfReader("input.pdf"); o = PdfWriter()
pg = r.pages[0]; pg.rotate(90); o.add_page(pg); o.write("rotated.pdf")

wm = PdfReader("watermark.pdf").pages[0]; o = PdfWriter()
for pg in PdfReader("doc.pdf").pages:
    pg.merge_page(wm); o.add_page(pg)
o.write("watermarked.pdf")

o = PdfWriter()
for pg in PdfReader("doc.pdf").pages: o.add_page(pg)
o.encrypt("user_pw", "owner_pw"); o.write("encrypted.pdf")
```
```python
import pikepdf  # repair / optimize / decrypt (replaces qpdf, which isn't installed)
with pikepdf.open("input.pdf") as pdf:
    pdf.save("optimized.pdf", linearize=True)
with pikepdf.open("encrypted.pdf", password="secret") as pdf:
    pdf.save("decrypted.pdf")
```

## Render to image (visual review)

```bash
python -X utf8 "$SKILL_DIR/scripts/pdf_to_images.py" document.pdf images/ 200
```
Uses PyMuPDF (fitz), no Poppler. Produces `images/page_1.png`, etc.

## PDF forms

**Fillable (AcroForm):**
```bash
python -X utf8 "$SKILL_DIR/scripts/fill_form.py" list form.pdf
# write values.json with the file tool: {"name": "Israel", "agree": "/Yes"}
python -X utf8 "$SKILL_DIR/scripts/fill_form.py" fill form.pdf values.json output.pdf
```

**Non-fillable (scans or flat PDFs):** you must **overlay text** at the right coordinates.
Standard approach: (1) render the page with `pdf_to_images.py` to locate each field; (2) create
a layer with reportlab (`canvas`) the same page size and draw text at those coordinates (origin
bottom-left, in points); (3) merge with pypdf's `page.merge_page()`:
```python
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
import io
buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=(612, 792))
c.setFont("Helvetica", 10); c.drawString(120, 650, "Israel Mosquera"); c.save()
buf.seek(0)
layer = PdfReader(buf).pages[0]
base = PdfReader("flat.pdf"); out = PdfWriter()
pg = base.pages[0]; pg.merge_page(layer); out.add_page(pg)
out.write("filled.pdf")
```

## OCR of scans (requires installing)

`pip install pytesseract` + install Tesseract and add it to PATH. Render to image with
`pdf_to_images.py` and pass it to Tesseract:
```python
import pytesseract
from PIL import Image
print(pytesseract.image_to_string(Image.open("images/page_1.png")))
```

## Proofread (MANDATORY before delivering a PDF with your own text)

When **you** generate the PDF's text (reportlab, overlay), proofread it before finishing:
```bash
python -X utf8 "$SKILL_DIR/scripts/spellcheck.py" output.pdf
```
It flags suspects (encoding artifacts, doubled words, space before punctuation) and prints the
full text. Fix, **read the rest**, and **regenerate** if you changed anything. (For PDFs you only
read/extract, this is informational.)

## Bundled scripts (all MIT, run with `-X utf8`)

| Script | Purpose |
|--------|---------|
| `extract_text.py` | text (and tables) per page with pdfplumber |
| `pdf_to_images.py` | PDF → PNG with PyMuPDF (no Poppler) |
| `fill_form.py` | list/fill AcroForm forms (pypdf) |
| `spellcheck.py` | flag likely mistakes and show the text |

## Dependencies (on this machine)

- **pypdf** ✅ · **reportlab** ✅ · **pdfplumber** ✅ · **PyMuPDF (fitz)** ✅ · **pikepdf** ✅ · **Pillow** ✅
- **pytesseract + Tesseract** ⚠️ NOT installed — only for OCR
- **Poppler / qpdf** ⚠️ NOT installed — not needed (we use PyMuPDF and pikepdf)

> **License: MIT (see `LICENSE`).** Independent skill: own guide and scripts on top of
> permissively licensed third-party libraries. **PyMuPDF (fitz) note:** AGPL-3.0 / commercial;
> only `pdf_to_images.py` uses it. For proprietary redistribution, swap it for `pypdfium2`
> (Apache/BSD) or Poppler. Not derived from proprietary third-party skills.
