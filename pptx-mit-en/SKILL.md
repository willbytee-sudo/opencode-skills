---
name: pptx-mit-en
description: >-
  Use ALWAYS when a .pptx is involved: creating presentations / slide decks, reading or
  extracting their text, or editing existing presentations. Builds presentations with the
  python-pptx library. Designed for opencode on Windows, with a proofread step before
  delivering. Triggers: "slides", "presentation", "deck", or a .pptx filename. Do NOT use for
  Word, Excel, or PDF. (Spanish version: pptx-mit.)
metadata:
  origin: independent skill (own implementation, MIT) based on the python-pptx library (MIT) and the open OOXML standard (ISO/IEC 29500). Not derived from any proprietary third-party skill.
  environment: opencode on Windows — Python 3.13 + python-pptx (pip) + PyMuPDF; LibreOffice optional
  license: MIT (see LICENSE)
  critical_rule: run ALL scripts with "python -X utf8"; proofread before delivering
---

# PowerPoint (.pptx) on opencode — create, read, edit (python-pptx)

## Overview

This skill creates and edits presentations with **python-pptx** (the standard Python library
for `.pptx`, MIT). Text reading needs no dependencies (it reads the ZIP). When done, **proofread**
before delivering.

> **Install python-pptx** (not present by default here): `pip install python-pptx`. The reading
> scripts (`extract_text.py`, `spellcheck.py`) do NOT need it.

## How opencode runs this skill (key adaptations — READ FIRST)

1. **`SKILL_DIR` as an absolute path.** opencode runs from the project directory:
   ```bash
   SKILL_DIR="$HOME/.config/opencode/skills/pptx-mit-en"
   ```
2. **UTF-8 RULE: run Python with `-X utf8` ALWAYS.** Without it, non-ASCII text breaks on Windows (cp1252).
3. **Text NEVER travels through the console.** The `.py` that builds the deck is written with the
   file tool (UTF-8), not with echo/Set-Content/here-strings.
4. **The sandbox `extract-text` does NOT exist.** Use `extract_text.py`.
5. **Visual QA = LibreOffice (optional, NOT installed).** `render_slides.py` uses LibreOffice +
   PyMuPDF (no Poppler). Without LibreOffice, do text QA with `extract_text.py`.

## Read / extract text

```bash
python -X utf8 "$SKILL_DIR/scripts/extract_text.py" presentation.pptx
```

## Create a presentation (python-pptx)

Write the `.py` with the file tool and run it with `python -X utf8`.
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation()
prs.slide_width  = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]        # blank layout (full control)

# Cover slide
s = prs.slides.add_slide(BLANK)
s.background.fill.solid(); s.background.fill.fore_color.rgb = RGBColor(0x1E, 0x27, 0x61)
box = s.shapes.add_textbox(Inches(1), Inches(2.6), Inches(11), Inches(2))
tf = box.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Management report 2024"
p.font.size = Pt(44); p.font.bold = True; p.font.name = "Arial"
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

# Content slide
s = prs.slides.add_slide(BLANK)
t = s.shapes.add_textbox(Inches(0.7), Inches(0.5), Inches(12), Inches(1))
tp = t.text_frame.paragraphs[0]; tp.text = "Results"; tp.font.size = Pt(32); tp.font.bold = True
body = s.shapes.add_textbox(Inches(0.7), Inches(1.8), Inches(7), Inches(4)).text_frame
body.word_wrap = True
for i, line in enumerate(["Revenue grew 15%.", "The coast region led.", "No reconciliation errors."]):
    par = body.paragraphs[0] if i == 0 else body.add_paragraph()
    par.text = "•  " + line; par.font.size = Pt(18)

prs.save("output.pptx")
```

### Shapes, tables, images, charts, notes
```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

rect = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8), Inches(1.8), Inches(4), Inches(2.2))
rect.fill.solid(); rect.fill.fore_color.rgb = RGBColor(0xF0, 0xF9, 0xFB)

tab = s.shapes.add_table(2, 2, Inches(0.7), Inches(4.2), Inches(6), Inches(1.2)).table
tab.cell(0, 0).text, tab.cell(0, 1).text = "Year", "Revenue"
tab.cell(1, 0).text, tab.cell(1, 1).text = "2024", "$1,234"

s.shapes.add_picture("chart.png", Inches(8), Inches(4.2), height=Inches(2.5))

data = CategoryChartData()
data.categories = ["Q1", "Q2", "Q3", "Q4"]; data.add_series("Sales", (4.5, 5.5, 6.2, 7.1))
s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(1.8), Inches(6), Inches(3.5), data)

s.notes_slide.notes_text_frame.text = "Open with the revenue headline. Pause after 15%."
```

## Design (general principles, not rigid rules)

- **One idea per slide.** Clear title + one visual (image, chart, icon, or shape). Avoid text-only slides.
- **Hierarchy by size:** title 36–44 pt, subheads 20–24 pt, body 14–18 pt.
- **Real contrast:** dark text on light or light on dark; dark backgrounds look good for cover/closing.
- **Intentional palette:** one dominant color, one or two supporting, one accent; pick by topic, not blue by default.
- **Safe fonts** (in Office, stable widths): Arial, Calibri, Cambria, Times New Roman.
- **Breathing room:** margins ≥ 0.5", even gaps; don't fill every corner.
- **Text must fit** its box: if it overflows, shrink the size, split slides, or enlarge the box.
- **Native charts** (`add_chart`), not chart images: they stay editable.

## Edit an existing presentation

```python
from pptx import Presentation
prs = Presentation("existing.pptx")
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for run in p.runs:
                    if "draft" in run.text.lower():
                        run.text = run.text.replace("Draft", "Final")
prs.save("modified.pptx")
```

## Visual QA (requires LibreOffice)

```bash
python -X utf8 "$SKILL_DIR/scripts/render_slides.py" output.pptx images/ 150
```
Produces `images/slide-1.png`, etc. Check for overlaps, cut/overflowing text, low contrast,
margins, and alignment. Fix and re-render only the affected slides.

## Proofread (MANDATORY before delivering)

```bash
python -X utf8 "$SKILL_DIR/scripts/spellcheck.py" output.pptx
```
Flags suspects per slide and prints the text. Fix, **read the rest**, and **regenerate** if you changed anything.

## Bundled scripts (all MIT, run with `-X utf8`)

| Script | Purpose |
|--------|---------|
| `extract_text.py` | text per slide (no dependencies) |
| `spellcheck.py` | flag likely mistakes and show the text |
| `render_slides.py` | .pptx → PNG per slide (LibreOffice + PyMuPDF) |

## Dependencies (on this machine)

- **python-pptx** ⚠️ NOT installed — needed to CREATE/edit: `pip install python-pptx`
- **PyMuPDF (fitz)** ✅ — used by `render_slides.py`
- **LibreOffice (`soffice`)** ⚠️ NOT installed — optional, only for visual QA
- Text reading (`extract_text.py`, `spellcheck.py`): **no dependencies** (stdlib)

> **License: MIT (see `LICENSE`).** Independent skill: own guide and scripts on top of the
> **python-pptx** library (MIT) and the open **OOXML** standard. **PyMuPDF (fitz) note:** AGPL-3.0 /
> commercial; only `render_slides.py` uses it. For proprietary redistribution, swap it for Poppler.
> Not derived from proprietary third-party skills.
