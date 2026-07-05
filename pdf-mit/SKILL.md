---
name: pdf-mit
description: >-
  Úsala SIEMPRE que se quiera hacer algo con archivos PDF: leer o extraer texto/tablas,
  crear PDFs nuevos, combinar/separar, rotar, marca de agua, cifrar/descifrar, extraer o
  renderizar imágenes, rellenar formularios y OCR de escaneos. Construida sobre librerías
  públicas de Python (pypdf, reportlab, pdfplumber, PyMuPDF, pikepdf). Pensada para español
  (acentos á é í ó ú ñ intactos) sobre opencode en Windows, con revisión ortográfica antes
  de entregar. Triggers EN: "PDF", ".pdf", "merge PDF", "fill form". NO usar para Word,
  Excel ni PowerPoint.
metadata:
  origen: skill independiente (implementación propia, MIT) sobre librerías de terceros de licencia permisiva (pypdf BSD, reportlab BSD, pdfplumber MIT, pikepdf MPL, PyMuPDF AGPL). No deriva de skills propietarias.
  entorno: opencode en Windows — Python 3.13 + pypdf + reportlab + pdfplumber + PyMuPDF(fitz) + pikepdf + Pillow
  licencia: MIT (ver LICENSE)
  regla_critica: correr TODOS los scripts con "python -X utf8"; revisar ortografía antes de entregar
---

# PDF en opencode — leer, crear, editar, formularios (librerías públicas)

## Overview

Esta skill trabaja PDFs con las librerías estándar de Python: **pypdf** (combinar/separar/
rotar/cifrar/formularios), **reportlab** (crear), **pdfplumber** (extraer texto/tablas),
**PyMuPDF/fitz** (renderizar a imagen) y **pikepdf** (reparar/optimizar). Al crear un PDF con
texto en español, **revisa la ortografía** antes de entregar.

## Cómo opencode ejecuta esta skill (adaptaciones clave — LEER PRIMERO)

1. **`SKILL_DIR` con ruta absoluta.** opencode corre desde el directorio del proyecto:
   ```bash
   SKILL_DIR="$HOME/.config/opencode/skills/pdf-mit"
   ```
2. **REGLA UTF-8: corre Python con `-X utf8` SIEMPRE.** Sin ella, los acentos se rompen en Windows (cp1252).
3. **El texto con acentos NUNCA viaja por la consola.** El `.py` que crea el PDF (reportlab)
   y los JSON de formularios se escriben con la herramienta de archivos (UTF-8), no con echo/heredocs.
4. **`extract-text` del sandbox NO existe.** Usa `extraer_texto.py`.
5. **Faltan en esta máquina (planéalo):** OCR (`pytesseract`, `pdf2image`) y Tesseract NO
   instalados; Poppler y qpdf NO instalados. Los scripts no los necesitan: la conversión a
   imagen usa **PyMuPDF**, y la reparación/optimización usa **pikepdf** (no qpdf).

## Leer / extraer texto

```bash
python -X utf8 "$SKILL_DIR/scripts/extraer_texto.py" documento.pdf            # texto por página
python -X utf8 "$SKILL_DIR/scripts/extraer_texto.py" documento.pdf --tablas   # + tablas
```
En una línea: `python -X utf8 -c "import pdfplumber; print(pdfplumber.open('x.pdf').pages[0].extract_text())"`

## Crear un PDF (reportlab)

Escribe el `.py` con la herramienta de archivos (UTF-8) y córrelo con `python -X utf8`.

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

doc = SimpleDocTemplate("salida.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = [
    Paragraph("Informe de gestión 2024", styles["Title"]),
    Spacer(1, 12),
    Paragraph("El año pasado la organización mejoró su función.", styles["Normal"]),
    Spacer(1, 12),
    Table([["Año", "Ingresos"], ["2024", "$1 234"]],
          style=TableStyle([("GRID", (0, 0), (-1, -1), 1, colors.grey),
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)])),
    PageBreak(),
]
doc.build(story)
```
**Subíndices/superíndices:** NO uses caracteres Unicode (₂, ²) — las fuentes base de reportlab
no los traen y salen como cuadros negros. Usa el marcado XML: `Paragraph("H<sub>2</sub>O", styles["Normal"])`.

## Operaciones comunes (pypdf / pikepdf)

```python
from pypdf import PdfReader, PdfWriter

# Combinar
w = PdfWriter()
for f in ["a.pdf", "b.pdf"]:
    for pg in PdfReader(f).pages: w.add_page(pg)
w.write("combinado.pdf")

# Separar (una página por archivo)
for i, pg in enumerate(PdfReader("entrada.pdf").pages):
    o = PdfWriter(); o.add_page(pg); o.write(f"pagina_{i+1}.pdf")

# Rotar 90°
r = PdfReader("entrada.pdf"); o = PdfWriter()
pg = r.pages[0]; pg.rotate(90); o.add_page(pg); o.write("rotado.pdf")

# Marca de agua
marca = PdfReader("marca.pdf").pages[0]; o = PdfWriter()
for pg in PdfReader("doc.pdf").pages:
    pg.merge_page(marca); o.add_page(pg)
o.write("con_marca.pdf")

# Cifrar con contraseña
o = PdfWriter()
for pg in PdfReader("doc.pdf").pages: o.add_page(pg)
o.encrypt("clave_usuario", "clave_propietario"); o.write("cifrado.pdf")
```

```python
import pikepdf  # reparar / optimizar / descifrar (reemplaza a qpdf, que no está instalado)
with pikepdf.open("entrada.pdf") as pdf:
    pdf.save("optimizado.pdf", linearize=True)
with pikepdf.open("cifrado.pdf", password="secreto") as pdf:
    pdf.save("descifrado.pdf")
```

## Renderizar a imagen (revisar visualmente)

```bash
python -X utf8 "$SKILL_DIR/scripts/pdf_a_imagenes.py" documento.pdf imagenes/ 200
```
Usa PyMuPDF (fitz), sin Poppler. Genera `imagenes/pagina_1.png`, etc.

## Formularios PDF

**Rellenables (AcroForm):**
```bash
python -X utf8 "$SKILL_DIR/scripts/rellenar_formulario.py" listar formulario.pdf
# crea valores.json con la herramienta de archivos: {"nombre": "Israel", "acepta": "/Yes"}
python -X utf8 "$SKILL_DIR/scripts/rellenar_formulario.py" rellenar formulario.pdf valores.json salida.pdf
```

**No rellenables (escaneos o PDFs planos):** hay que **superponer texto** sobre las
coordenadas correctas. Enfoque estándar: (1) renderiza la página a imagen con
`pdf_a_imagenes.py` para ubicar visualmente dónde va cada dato; (2) crea una capa con
reportlab (`canvas`) del mismo tamaño de página y dibuja el texto en esas coordenadas
(origen abajo-izquierda, en puntos); (3) fusiónala con `page.merge_page()` de pypdf:
```python
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
import io

buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=(612, 792))   # tamaño de la página destino
c.setFont("Helvetica", 10); c.drawString(120, 650, "Israel Mosquera"); c.save()
buf.seek(0)
capa = PdfReader(buf).pages[0]
base = PdfReader("plano.pdf"); out = PdfWriter()
pg = base.pages[0]; pg.merge_page(capa); out.add_page(pg)
out.write("relleno.pdf")
```

## OCR de escaneos (requiere instalar)

`pip install pytesseract` + instalar Tesseract y ponerlo en el PATH. Renderiza a imagen con
`pdf_a_imagenes.py` (o fitz) y pásala a Tesseract con `lang="spa"` (para acentos):
```python
import pytesseract
from PIL import Image
print(pytesseract.image_to_string(Image.open("imagenes/pagina_1.png"), lang="spa"))
```

## Revisión ortográfica (OBLIGATORIA antes de entregar un PDF con texto propio)

Cuando **tú** generas el texto de un PDF (reportlab, superposición), revísalo antes de dar
por terminado — sobre todo tildes (`funcion`→`función`), terminaciones `-cion`/`-sion` y
mojibake (`posiciAn`):
```bash
python -X utf8 "$SKILL_DIR/scripts/revisar_ortografia.py" salida.pdf
```
Señala sospechosos y muestra el texto completo. Corrige, **lee el resto** buscando faltas
que la heurística no ve, y **regenera** si hiciste cambios. (Para PDFs que solo lees/extraes,
esta revisión es informativa.)

## Scripts incluidos (todos MIT, correr con `-X utf8`)

| Script | Para qué |
|--------|----------|
| `extraer_texto.py` | texto (y tablas) por página con pdfplumber |
| `pdf_a_imagenes.py` | PDF → PNG con PyMuPDF (sin Poppler) |
| `rellenar_formulario.py` | listar/rellenar formularios AcroForm (pypdf) |
| `revisar_ortografia.py` | señala posibles faltas ortográficas y muestra el texto |

## Dependencias (en esta máquina)

- **pypdf** ✅ · **reportlab** ✅ · **pdfplumber** ✅ · **PyMuPDF (fitz)** ✅ · **pikepdf** ✅ · **Pillow** ✅
- **pytesseract + Tesseract** ⚠️ NO instalados — solo para OCR
- **Poppler / qpdf** ⚠️ NO instalados — no hacen falta (usamos PyMuPDF y pikepdf)

> **Licencia: MIT (ver `LICENSE`).** Skill **independiente**: guía y scripts propios sobre
> librerías de terceros de licencia permisiva. **Nota PyMuPDF (fitz):** AGPL-3.0 / comercial;
> solo lo usa `pdf_a_imagenes.py`. Para redistribución propietaria, sustitúyelo por
> `pypdfium2` (Apache/BSD) o Poppler. No deriva de skills propietarias de terceros.
