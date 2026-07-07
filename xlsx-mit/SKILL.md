---
name: xlsx-mit
description: >-
  Use whenever a spreadsheet is the primary input or output: open, read, edit, or fix an
  .xlsx/.xlsm/.csv (add columns, formulas, formatting, clean data); create a sheet from scratch;
  or convert tabular data. Built on openpyxl. Designed for opencode on Windows, with a proofread
  step for text cells before delivering. Triggers when the user mentions a spreadsheet file. Do
  NOT use when the main deliverable is Word, PDF, or PowerPoint.
metadata:
  origin: independent skill (own implementation, MIT) based on the openpyxl library (MIT) and the open OOXML standard (ISO/IEC 29500). Not derived from any proprietary third-party skill.
  environment: opencode on Windows — Python 3.13 + openpyxl; pandas and LibreOffice optional
  license: MIT (see LICENSE)
  critical_rule: run ALL scripts with "python -X utf8"; use formulas (don't hardcode); proofread before delivering
---

# Excel (.xlsx) on opencode — create, edit, analyze (openpyxl)

## Overview

This skill creates and edits spreadsheets with **openpyxl** (the standard Python library for
`.xlsx`, MIT, already installed). When the workbook has text, **proofread** the text cells before delivering.

## How opencode runs this skill (key adaptations — READ FIRST)

1. **`SKILL_DIR` as an absolute path.** opencode runs from the project directory:
   ```bash
   SKILL_DIR="$HOME/.config/opencode/skills/xlsx-mit"
   ```
2. **UTF-8 RULE: run Python with `-X utf8` ALWAYS.** Without it, non-ASCII text breaks on Windows (cp1252).
3. **Text NEVER travels through the console.** The `.py` that builds the workbook (and source `.csv`)
   are written with the file tool in UTF-8, not with echo/Set-Content/here-strings.
4. **The sandbox `extract-text` does NOT exist.** Use `extract_text.py`.
5. **`recalc.py` needs LibreOffice (NOT installed).** openpyxl writes formulas but NOT their values;
   Excel calculates them on open. **pandas is NOT installed** (`pip install pandas`); for most things use openpyxl (✅).

## CRITICAL: formulas, not hardcoded values

Use Excel formulas instead of computing in Python and pasting the number. That keeps the sheet dynamic.
```python
# ❌ BAD: sheet['B10'] = df['Sales'].sum()      # hardcodes 5000
# ✅ GOOD:
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5']  = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

## Read / analyze

```bash
python -X utf8 "$SKILL_DIR/scripts/extract_text.py" workbook.xlsx | head -50           # formulas
python -X utf8 "$SKILL_DIR/scripts/extract_text.py" workbook.xlsx --values | head -50   # cached values
```
```python
from openpyxl import load_workbook
wb = load_workbook('workbook.xlsx')                       # formulas and formatting
wb_val = load_workbook('workbook.xlsx', data_only=True)   # cached values (if present)
```
pandas (⚠️ `pip install pandas`): `import pandas as pd; df = pd.read_excel('workbook.xlsx')`.

## Create a workbook (openpyxl)

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook(); ws = wb.active; ws.title = "Budget"
ws["A1"] = "Year"; ws["B1"] = "Revenue ($)"; ws["C1"] = "Description"
ws.append([2024, 1234, "coast region management"])
ws.append([2025, 1500, "year-over-year change"])
ws["B4"] = "=SUM(B2:B3)"                 # formula, not the number

for cell in ws[1]:
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", start_color="1E2761")
    cell.alignment = Alignment(horizontal="center")
ws.column_dimensions["C"].width = 32
ws["B2"].number_format = '"$"#,##0'

wb.save("output.xlsx")
```

### Financial models (useful conventions)
- **Text colors:** blue = inputs/scenarios; black = formulas; green = links to other sheets.
- **Numbers:** years as text ("2024"); currency `$#,##0` with units in the header; percentages `0.0%`;
  negatives in parentheses; zeros as "-" (`"$#,##0;($#,##0);-"`).
- **Assumptions in separate cells**, referenced: `=B5*(1+$B$6)`, not `=B5*1.05`.
- **Document hardcodes** with a note/adjacent cell (source, date, reference).

### Edit an existing workbook
```python
from openpyxl import load_workbook
wb = load_workbook("existing.xlsx"); ws = wb.active   # or wb["SheetName"]
ws["A1"] = "New value"; ws.insert_rows(2); ws.delete_cols(3)
wb.create_sheet("Summary")["A1"] = "Data"
wb.save("modified.xlsx")
```
`data_only=True` reads cached values, but **saving that way loses the formulas**. For large files use `read_only=True` / `write_only=True`.

## Recalculate and check errors (requires LibreOffice)

```bash
python -X utf8 "$SKILL_DIR/scripts/recalc.py" output.xlsx
```
Returns JSON; if `status` is `errors_found`, check `error_summary` (#REF!, #DIV/0!, ...), fix and
repeat. Without LibreOffice: deliver with formulas (Excel calculates on open) and review the ranges.

## Proofread (MANDATORY before delivering)

When the workbook has **text** (headers, labels, descriptions), proofread it:
```bash
python -X utf8 "$SKILL_DIR/scripts/spellcheck.py" output.xlsx
```
It only looks at text cells (ignores numbers and formulas). Flags suspects with their cell
(`Sheet!B3`) and lists the texts. Fix, **read the rest**, and **regenerate** if you changed anything.

## Bundled scripts (all MIT, run with `-X utf8`)

| Script | Purpose |
|--------|---------|
| `extract_text.py` | dump each sheet as TSV (formulas or values) |
| `spellcheck.py` | flag likely mistakes in text cells |
| `recalc.py` | recalculate formulas and scan errors (requires LibreOffice) |

## Dependencies (on this machine)

- **openpyxl** ✅ — create, read, edit, formulas, formatting (main tool)
- **pandas** ⚠️ NOT installed — only for analysis (`pip install pandas`)
- **LibreOffice (`soffice`)** ⚠️ NOT installed — only for `recalc.py`

> **License: MIT (see `LICENSE`).** Independent skill: own guide and scripts on top of the
> **openpyxl** library (MIT) and the open **OOXML (ECMA-376 / ISO/IEC 29500)** standard. Not derived
> from any proprietary third-party skill; safe to publish under MIT.
