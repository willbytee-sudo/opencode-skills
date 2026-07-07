---
name: docx-mit
description: >-
  Use ALWAYS when creating, reading, editing, or analyzing Word documents (.docx): reports,
  essays, letters, memos, templates, or any deliverable with headings, tables, lists, images,
  a table of contents, page numbers, headers/footers, or an APA reference list. Also for
  extracting text from a .docx. Builds documents with the python-docx library. Designed for
  opencode on Windows, with a proofread step before delivering. Triggers: "Word doc", ".docx",
  "report", "letter". Do NOT use for PDF, Excel (xlsx), or PowerPoint.
metadata:
  origin: independent skill (own implementation, MIT) based on the python-docx library (MIT) and the open OOXML standard (ISO/IEC 29500). Not derived from any proprietary third-party skill.
  environment: opencode on Windows — Python 3.13 + python-docx + lxml; Microsoft Word or LibreOffice for the TOC
  license: MIT (see LICENSE)
  critical_rule: run ALL scripts with "python -X utf8"; proofread before delivering
---

# Word (.docx) on opencode — create, read, edit (python-docx)

## Overview

This skill creates and edits Word documents with **python-docx** (the standard Python library
for `.docx`, MIT, already installed). The model writes a Python script that builds the
document; then you validate it and **proofread** it before delivering.

## How opencode runs this skill (key adaptations — READ FIRST)

In opencode the working directory is the project's, **not** the skill's, and the Windows
console corrupts UTF-8. Therefore:

1. **`SKILL_DIR` as an absolute path.** Set it at the start of any command:
   ```bash
   SKILL_DIR="$HOME/.config/opencode/skills/docx-mit"
   ```
2. **UTF-8 RULE (non-negotiable): run Python with `-X utf8` ALWAYS.**
   ```bash
   python -X utf8 build_document.py     # ✅
   python build_document.py             # ❌ breaks on non-ASCII text
   ```
   Without `-X utf8`, non-ASCII characters get corrupted (`'charmap' codec...`) because
   Windows uses cp1252.
3. **Text NEVER travels through the console.** Write the `.py` that builds the document with
   the file-writing tool (UTF-8), not with `echo`, `Set-Content`, or PowerShell here-strings.
   If the content comes as Markdown, save it with the file tool too.
4. **The sandbox `extract-text` does NOT exist here.** Use the bundled replacement
   (`extract_text.py`).

## Recommended flow

1. **Write** a `.py` script that builds the document with python-docx (see "Create").
2. **Generate:** `python -X utf8 build_document.py`
3. **Validate:** `python -X utf8 "$SKILL_DIR/scripts/validate_docx.py" output.docx`
4. **Proofread (MANDATORY):**
   `python -X utf8 "$SKILL_DIR/scripts/spellcheck.py" output.docx`
   Read the flagged suspects AND the full text; fix and regenerate if there are mistakes.

---

## Create a document (python-docx)

Write the script with the file tool and run it with `python -X utf8`.

### Base
```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Default font (Arial 12) — universal support
normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(12)

doc.add_heading("Document title", level=0)   # title
doc.add_heading("Introduction", level=1)     # H1 heading
p = doc.add_paragraph("Last year performance improved. ")
p.add_run("Bold text.").bold = True
p.add_run(" And italic.").italic = True

doc.save("output.docx")
```

### Page size and margins (US Letter / A4)
```python
from docx.shared import Inches
sec = doc.sections[0]
sec.page_width  = Inches(8.5)    # US Letter (A4: Inches(8.27) x Inches(11.69))
sec.page_height = Inches(11)
sec.top_margin = sec.bottom_margin = Inches(1)
sec.left_margin = sec.right_margin = Inches(1)
```

### Lists (bullets and numbered)
Use the built-in styles, NEVER a literal "•" character:
```python
doc.add_paragraph("First item", style="List Bullet")
doc.add_paragraph("Second item", style="List Bullet")
doc.add_paragraph("Step one", style="List Number")
doc.add_paragraph("Step two", style="List Number")
```

### Tables
```python
from docx.shared import Pt
table = doc.add_table(rows=1, cols=3)
table.style = "Table Grid"                 # visible borders
hdr = table.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text = "Year", "Revenue", "Notes"
row = table.add_row().cells
row[0].text, row[1].text, row[2].text = "2024", "$1,234", "stable"
for r in table.rows:
    r.cells[0].width = Inches(1.2)
```

### Images
```python
doc.add_picture("chart.png", width=Inches(5))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
```

### Page breaks (⚠️ avoid the blank page)
To **start a new section on a fresh page** (cover → TOC, TOC → content, chapter start), use
`page_break_before` on the FIRST paragraph of the section, NOT `add_page_break()`:
```python
h = doc.add_heading("Table of Contents", level=1)
h.paragraph_format.page_break_before = True     # ✅ clean break, no blank page
```
**Why:** `doc.add_page_break()` creates an EMPTY paragraph that only holds the break. If the
previous page is nearly full, that empty line overflows to the next page and the break jumps
again → an extra **blank page**. `page_break_before` adds no empty paragraph, so it never
creates that phantom page.
```python
doc.add_page_break()   # ⚠️ only for a break WITHIN the same text flow; to change sections
                       # prefer page_break_before (above)
```

### Alignment and line spacing
```python
p = doc.add_paragraph("Justified, double-spaced paragraph.")
p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p.paragraph_format.line_spacing = 2.0
p.paragraph_format.space_after = Pt(6)
```

### Header, footer, and page number
The page number is a Word *field*; insert it at the XML level (python-docx has no shortcut):
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def page_number(paragraph):
    run = paragraph.add_run()
    a = OxmlElement("w:fldChar"); a.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "end")
    run._r.append(a); run._r.append(instr); run._r.append(b)

sec = doc.sections[0]
sec.header.paragraphs[0].text = "Short title"
footer = sec.footer.paragraphs[0]; footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.add_run("Page "); page_number(footer)
```

### Table of contents (builds ITSELF, no manual F9)
python-docx does not compute page numbers (Word/LibreOffice does). To get the TOC **built
without asking the user to press F9**, do TWO things: insert the TOC field + mark the document
to **update fields on open**, and then **fill it once** with `update_toc.py`. Headings must use
`add_heading(..., level=1/2/3)`. The TOC *title* must NOT be a heading (or it lists itself).
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def insert_toc(doc, title="Table of Contents"):
    tp = doc.add_paragraph()
    tp.paragraph_format.page_break_before = True       # starts on a new page, no blank page
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = tp.add_run(title); r.bold = True; r.font.size = Pt(16)   # styled, NOT a heading
    p = doc.add_paragraph(); run = p.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = "Table of contents"
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    for el in (b, instr, sep, t, e):
        run._r.append(el)

def mark_update_fields(doc):
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        el = OxmlElement("w:updateFields"); el.set(qn("w:val"), "true")
        settings.insert(0, el)

insert_toc(doc); mark_update_fields(doc); doc.save("output.docx")
```
Then fill the TOC (recommended before delivering):
```bash
python -X utf8 "$SKILL_DIR/scripts/update_toc.py" output.docx
```
Uses LibreOffice if present, or Word (COM) on Windows. **Close the .docx in Word first.**

### APA reference list (hanging indent)
Each reference is a paragraph with a **hanging indent** (first line at the margin, the rest
indented) and double spacing. Do NOT use a table or bullets.
```python
def reference(doc, runs):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.5)
    pf.first_line_indent = Inches(-0.5)   # hanging
    pf.line_spacing = 2.0
    pf.space_after = Pt(6)
    for text, italic in runs:
        r = p.add_run(text); r.italic = italic
    return p

doc.add_heading("References", level=1)
reference(doc, [("Ministry of Finance. (2024). ", False),
                ("2024 budget execution report", True),
                (". Quito, Ecuador.", False)])
```

---

## Read / extract content

```bash
python -X utf8 "$SKILL_DIR/scripts/extract_text.py" document.docx
```

## Edit an existing document

Open with `Document("existing.docx")`, modify, save. To replace text while keeping formatting,
edit the `run` (not the whole paragraph):
```python
from docx import Document
doc = Document("existing.docx")
for p in doc.paragraphs:
    for run in p.runs:
        if "30 days" in run.text:
            run.text = run.text.replace("30 days", "60 days")
doc.save("modified.docx")
```

## Proofread (MANDATORY before delivering)

Before finishing a `.docx`, always run:
```bash
python -X utf8 "$SKILL_DIR/scripts/spellcheck.py" output.docx
```
It extracts the text and **flags suspects** (encoding artifacts/mojibake, doubled words, space
before punctuation), then **prints the full text**. Your job:
1. Fix each real issue.
2. **Read the full text** for mistakes the heuristics miss (agreement, wrong words, typos).
3. If you change anything, **regenerate** the `.docx` and re-check.

## Fixing a blank page in an existing .docx

If a document already has a phantom blank page from empty page-break paragraphs:
```bash
python -X utf8 "$SKILL_DIR/scripts/fix_page_breaks.py" input.docx output.docx
```

## Bundled scripts (all MIT, run with `-X utf8`)

| Script | Purpose |
|--------|---------|
| `extract_text.py` | dump the text (paragraphs + tables) |
| `validate_docx.py` | practical validation (ZIP/XML/parts + python-docx) |
| `spellcheck.py` | flag likely mistakes and show the text |
| `fix_page_breaks.py` | remove blank pages from empty page-break paragraphs |
| `update_toc.py` | fill the TOC and page numbers (Word or LibreOffice) |

## Dependencies (on this machine)

- **python-docx** ✅ — create, read, edit
- **lxml** ✅ — used by python-docx, `validate_docx.py`, and `fix_page_breaks.py`
- **Microsoft Word** ✅ (Windows) — used by `update_toc.py` (COM) to fill the TOC
- **LibreOffice** ⚠️ NOT installed — optional (alternative for `update_toc.py`; PDF/images)

> **License: MIT (see `LICENSE`).** Independent skill: the scripts and this guide are own
> implementation and writing, on top of the **python-docx** library (MIT) and the open
> **OOXML (ECMA-376 / ISO/IEC 29500)** standard. Not derived from any proprietary third-party
> skill; safe to publish under MIT.
