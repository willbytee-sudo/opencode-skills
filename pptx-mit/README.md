# pptx-mit — PowerPoint (.pptx) · opencode

> [!IMPORTANT]
> Skill para **[opencode](https://opencode.ai)** en Windows. El `SKILL.md` está
> **en inglés** a propósito (los modelos lo siguen mejor); este README explica la
> skill en inglés y en español.
> *Skill for opencode on Windows. The `SKILL.md` instructions are intentionally in
> English; this README describes it in both English and Spanish.*

## 🇬🇧 English

**What it does.** Creates, reads and edits PowerPoint decks with **python-pptx**:
cover/content slides, shapes, tables, images, native (editable) charts and speaker
notes, with design guidance (hierarchy, contrast, palette, spacing). Optional
visual QA renders slides to PNG (LibreOffice + PyMuPDF). A **proofread** step runs
before delivering. UTF-8 pipeline (`python -X utf8`, text via the file tool).

**How to use.**
```bash
pip install python-pptx   # needed to create/edit (reading needs nothing)
SKILL_DIR="$HOME/.config/opencode/skills/pptx-mit"
# write a build script (build_deck.py) with the file tool, then:
python -X utf8 build_deck.py
python -X utf8 "$SKILL_DIR/scripts/spellcheck.py" output.pptx   # mandatory proofread
```

## 🇪🇸 Español

**Qué hace.** Crea, lee y edita presentaciones con **python-pptx**: diapositivas de
portada/contenido, formas, tablas, imágenes, gráficos nativos (editables) y notas
del orador, con guía de diseño (jerarquía, contraste, paleta, márgenes). El control
visual opcional renderiza las diapositivas a PNG (LibreOffice + PyMuPDF). Corre un
paso de **revisión** antes de entregar. Pipeline UTF-8 (`python -X utf8`, el texto
por la herramienta de archivos).

**Cómo se usa.** Instala `python-pptx`, escribe el script de construcción con la
herramienta de archivos, córrelo con `python -X utf8` y revisa con `spellcheck.py`
antes de entregar.

### Scripts (`python -X utf8`)
| Script | Purpose / Propósito |
|--------|---------------------|
| `extract_text.py` | text per slide (no deps) / texto por diapositiva |
| `spellcheck.py` | flag mistakes + print text / marcar faltas y mostrar el texto |
| `render_slides.py` | .pptx → PNG (LibreOffice + PyMuPDF) / a imágenes |

**Requires / Requiere:** `python-pptx` (`pip install python-pptx`). Render: `PyMuPDF` + LibreOffice (opcional).
**License / Licencia:** MIT (ver `LICENSE`). Nota: `render_slides.py` usa PyMuPDF (AGPL-3.0); cámbialo por Poppler para redistribución propietaria.
