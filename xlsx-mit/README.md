# xlsx-mit — Excel (.xlsx) · opencode

> [!IMPORTANT]
> Skill para **[opencode](https://opencode.ai)** en Windows. El `SKILL.md` está
> **en inglés** a propósito (los modelos lo siguen mejor); este README explica la
> skill en inglés y en español.
> *Skill for opencode on Windows. The `SKILL.md` instructions are intentionally in
> English; this README describes it in both English and Spanish.*

## 🇬🇧 English

**What it does.** Creates, edits and analyzes spreadsheets with **openpyxl**:
sheets from scratch, formatting, number formats, and **real Excel formulas** (never
hardcoded values, so the sheet stays dynamic), plus financial-model conventions.
Optional recalculation and error scan via LibreOffice. When the workbook has text,
a **proofread** step checks the text cells before delivering. UTF-8 pipeline
(`python -X utf8`, text/CSV via the file tool).

**How to use.**
```bash
SKILL_DIR="$HOME/.config/opencode/skills/xlsx-mit"
# write a build script (build_workbook.py) with the file tool, then:
python -X utf8 build_workbook.py
python -X utf8 "$SKILL_DIR/scripts/extract_text.py" output.xlsx --values
python -X utf8 "$SKILL_DIR/scripts/spellcheck.py"   output.xlsx   # proofread text cells
```

## 🇪🇸 Español

**Qué hace.** Crea, edita y analiza hojas de cálculo con **openpyxl**: hojas desde
cero, formato, formatos de número y **fórmulas reales de Excel** (nunca valores
fijos, para que la hoja quede dinámica), más convenciones de modelos financieros.
Recalculo y detección de errores opcionales vía LibreOffice. Cuando el libro tiene
texto, un paso de **revisión** revisa las celdas de texto antes de entregar.
Pipeline UTF-8 (`python -X utf8`, el texto/CSV por la herramienta de archivos).

**Cómo se usa.** Escribe el script de construcción con la herramienta de archivos,
córrelo con `python -X utf8`, y revisa con `extract_text.py`/`spellcheck.py` antes
de entregar.

### Scripts (`python -X utf8`)
| Script | Purpose / Propósito |
|--------|---------------------|
| `extract_text.py` | each sheet as TSV (formulas/values) / cada hoja como TSV |
| `spellcheck.py` | flag mistakes in text cells / marcar faltas en celdas de texto |
| `recalc.py` | recalc formulas + scan errors (LibreOffice) / recalcular y revisar errores |

**Requires / Requiere:** `openpyxl` (instalado). Recalc: LibreOffice (opcional). Análisis: `pandas` (opcional).
**License / Licencia:** MIT (ver `LICENSE`).
