# docx-mit — Word (.docx) · opencode

> [!IMPORTANT]
> Skill para **[opencode](https://opencode.ai)** en Windows. El `SKILL.md` está
> **en inglés** a propósito (los modelos lo siguen mejor); este README explica la
> skill en inglés y en español.
> *Skill for opencode on Windows. The `SKILL.md` instructions are intentionally in
> English; this README describes it in both English and Spanish.*

## 🇬🇧 English

**What it does.** Creates, reads and edits Word documents with **python-docx**:
headings, tables, bullet/numbered lists, images, a **self-building table of
contents** (no manual F9), page numbers, headers/footers and APA reference lists.
Every deliverable goes through a mandatory **proofread** step that flags encoding
artifacts / mojibake (`posiciAn`) and other mistakes. It enforces a UTF-8 pipeline
(`python -X utf8`, text via the file tool, never the console) so Spanish accents
and `ñ` never break.

**How to use.**
```bash
SKILL_DIR="$HOME/.config/opencode/skills/docx-mit"
# 1) Write a build script (build_document.py) with the file tool, then generate:
python -X utf8 build_document.py
# 2) Validate and proofread (mandatory) before delivering:
python -X utf8 "$SKILL_DIR/scripts/validate_docx.py" output.docx
python -X utf8 "$SKILL_DIR/scripts/spellcheck.py"    output.docx
```

## 🇪🇸 Español

**Qué hace.** Crea, lee y edita documentos de Word con **python-docx**:
encabezados, tablas, listas con viñetas/numeradas, imágenes, **índice que se arma
solo** (sin F9 manual), números de página, encabezados/pies y referencias APA.
Todo pasa por un paso **obligatorio de revisión** que marca mojibake (`posiciAn`)
y otras faltas. Impone un pipeline UTF-8 (`python -X utf8`, el texto va por la
herramienta de archivos, nunca por la consola) para que no se rompan los acentos
ni la `ñ`.

**Cómo se usa.** Los mismos comandos de arriba: escribe el script de construcción
con la herramienta de archivos, genéralo con `python -X utf8`, y antes de entregar
corre `validate_docx.py` y `spellcheck.py`.

### Scripts (`python -X utf8`)
| Script | Purpose / Propósito |
|--------|---------------------|
| `extract_text.py` | dump text (paragraphs + tables) / volcar el texto |
| `validate_docx.py` | validate the .docx / validar el .docx |
| `spellcheck.py` | flag mistakes + print text / marcar faltas y mostrar el texto |
| `fix_page_breaks.py` | remove blank pages / quitar páginas en blanco |
| `update_toc.py` | fill TOC & page numbers / rellenar el índice |

**Requires / Requiere:** `python-docx`, `lxml` (instalados). Índice: Word o LibreOffice.
**License / Licencia:** MIT (ver `LICENSE`).
