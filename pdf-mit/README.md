# pdf-mit — PDF · opencode

> [!IMPORTANT]
> Skill para **[opencode](https://opencode.ai)** en Windows. El `SKILL.md` está
> **en inglés** a propósito (los modelos lo siguen mejor); este README explica la
> skill en inglés y en español.
> *Skill for opencode on Windows. The `SKILL.md` instructions are intentionally in
> English; this README describes it in both English and Spanish.*

## 🇬🇧 English

**What it does.** Everything with PDFs, on public Python libraries: extract
text/tables (**pdfplumber**), create (**reportlab**), merge/split/rotate/watermark/
encrypt and fill AcroForm forms (**pypdf**), render pages to PNG (**PyMuPDF**, no
Poppler), repair/optimize (**pikepdf**), and OCR of scans (optional, needs
Tesseract). When you generate the text yourself, a **proofread** step runs before
delivering. UTF-8 pipeline (`python -X utf8`, text via the file tool).

**How to use.**
```bash
SKILL_DIR="$HOME/.config/opencode/skills/pdf-mit"
python -X utf8 "$SKILL_DIR/scripts/extract_text.py"  document.pdf --tables
python -X utf8 "$SKILL_DIR/scripts/pdf_to_images.py" document.pdf images/ 200
python -X utf8 "$SKILL_DIR/scripts/fill_form.py" list form.pdf
python -X utf8 "$SKILL_DIR/scripts/spellcheck.py"    output.pdf   # proofread your own text
```

## 🇪🇸 Español

**Qué hace.** Todo con PDFs, sobre librerías públicas de Python: extraer
texto/tablas (**pdfplumber**), crear (**reportlab**), unir/dividir/rotar/marca de
agua/encriptar y rellenar formularios AcroForm (**pypdf**), renderizar páginas a
PNG (**PyMuPDF**, sin Poppler), reparar/optimizar (**pikepdf**) y OCR de escaneos
(opcional, requiere Tesseract). Cuando el texto lo generas tú, corre un paso de
**revisión** antes de entregar. Pipeline UTF-8 (`python -X utf8`, el texto por la
herramienta de archivos).

**Cómo se usa.** Los mismos comandos de arriba, ajustando el archivo. Para crear un
PDF, escribe el script de reportlab con la herramienta de archivos y córrelo con
`python -X utf8`; revisa con `spellcheck.py` antes de entregar.

### Scripts (`python -X utf8`)
| Script | Purpose / Propósito |
|--------|---------------------|
| `extract_text.py` | text (and tables) per page / texto y tablas por página |
| `pdf_to_images.py` | PDF → PNG (PyMuPDF) / PDF a imágenes |
| `fill_form.py` | list/fill AcroForm forms / listar y rellenar formularios |
| `spellcheck.py` | flag mistakes + print text / marcar faltas y mostrar el texto |

**Requires / Requiere:** `pypdf`, `reportlab`, `pdfplumber`, `PyMuPDF`, `pikepdf`, `Pillow` (instalados). OCR: Tesseract (opcional).
**License / Licencia:** MIT (ver `LICENSE`). Nota: `pdf_to_images.py` usa PyMuPDF (AGPL-3.0); para redistribución propietaria, cámbialo por `pypdfium2` o Poppler.
