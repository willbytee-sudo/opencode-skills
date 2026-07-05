---
name: docx-mit
description: >-
  Úsala SIEMPRE que se quiera crear, leer, editar o analizar documentos de Word (.docx):
  informes, ensayos, monografías, cartas, memos, plantillas o cualquier entregable con
  encabezados, tablas, listas, imágenes, índice, numeración de página, encabezados/pies o
  bibliografía en formato APA. También para extraer texto de un .docx. Construye los
  documentos con la librería python-docx. Pensada para español (acentos á é í ó ú ñ ¿ ¡ «»
  intactos) sobre opencode en Windows, con revisión ortográfica antes de entregar. Triggers
  EN: "Word doc", ".docx", "report", "letter". NO usar para PDF, Excel (xlsx) ni PowerPoint.
metadata:
  origen: skill independiente (implementación propia, MIT) basada en la librería python-docx (MIT) y el estándar abierto OOXML (ISO/IEC 29500). No deriva de skills propietarias de terceros.
  entorno: opencode en Windows — Python 3.13 + python-docx + lxml
  licencia: MIT (ver LICENSE)
  regla_critica: correr TODOS los scripts con "python -X utf8"; revisar ortografía antes de entregar
---

# Word (.docx) en opencode — crear, leer, editar (python-docx)

## Overview

Esta skill crea y edita documentos de Word con **python-docx** (la librería estándar de
Python para `.docx`, licencia MIT, ya instalada). El modelo escribe un script de Python
que arma el documento; luego se valida y se **revisa la ortografía** antes de entregar.

## Cómo opencode ejecuta esta skill (adaptaciones clave — LEER PRIMERO)

En opencode el directorio de trabajo es el del proyecto, **no** el de la skill, y la
consola de Windows corrompe UTF-8. Por eso:

1. **`SKILL_DIR` con ruta absoluta.** Fija la variable al principio de cualquier comando:
   ```bash
   SKILL_DIR="$HOME/.config/opencode/skills/docx-mit"
   # (ajústala si trabajas desde el repo)
   ```
2. **REGLA UTF-8 (no negociable): corre Python con `-X utf8` SIEMPRE.**
   ```bash
   python -X utf8 crear_documento.py     # ✅
   python crear_documento.py             # ❌ se rompe con acentos
   ```
   Sin `-X utf8`, los acentos se corrompen (`'charmap' codec...`) porque Windows usa cp1252.
3. **El texto con acentos NUNCA viaja por la consola.** Escribe el `.py` que arma el
   documento con la herramienta de *escribir archivo* (UTF-8), no con `echo`, `Set-Content`
   ni heredocs de PowerShell. Así la `ñ` y las tildes llegan intactas a python-docx.
   Si el contenido viene en Markdown, guárdalo también con la herramienta de archivos.
4. **`extract-text` del sandbox NO existe aquí.** Usa el reemplazo incluido
   (`extraer_texto.py`).

## Flujo recomendado

1. **Escribe** un script `.py` que arme el documento con python-docx (ver "Crear").
2. **Genera:** `python -X utf8 crear_documento.py`
3. **Valida:** `python -X utf8 "$SKILL_DIR/scripts/validar_docx.py" salida.docx`
4. **Revisa la ortografía (OBLIGATORIO):**
   `python -X utf8 "$SKILL_DIR/scripts/revisar_ortografia.py" salida.docx`
   Lee los sospechosos Y el texto completo; corrige y regenera si hay faltas.

---

## Crear un documento (python-docx)

Escribe el script con la herramienta de archivos y córrelo con `python -X utf8`.

### Base
```python
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Fuente por defecto (Arial 12) — soporte universal
normal = doc.styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(12)

doc.add_heading("Título del documento", level=0)   # título
doc.add_heading("Introducción", level=1)           # encabezado H1
p = doc.add_paragraph("El año pasado la función mejoró. ")
p.add_run("Texto en negrita.").bold = True
p.add_run(" Y en cursiva.").italic = True

doc.save("salida.docx")
```

### Tamaño de página y márgenes (US Letter / A4)
```python
from docx.shared import Inches
sec = doc.sections[0]
sec.page_width  = Inches(8.5)    # US Letter (A4: Inches(8.27) x Inches(11.69))
sec.page_height = Inches(11)
sec.top_margin = sec.bottom_margin = Inches(1)
sec.left_margin = sec.right_margin = Inches(1)
```

### Listas (viñetas y numeradas)
Usa los estilos integrados, NUNCA el carácter "•" a mano:
```python
doc.add_paragraph("Primer ítem", style="List Bullet")
doc.add_paragraph("Segundo ítem", style="List Bullet")
doc.add_paragraph("Paso uno", style="List Number")
doc.add_paragraph("Paso dos", style="List Number")
```

### Tablas
```python
from docx.shared import Pt
tabla = doc.add_table(rows=1, cols=3)
tabla.style = "Table Grid"                 # bordes visibles
hdr = tabla.rows[0].cells
hdr[0].text, hdr[1].text, hdr[2].text = "Año", "Ingresos", "Notas"
fila = tabla.add_row().cells
fila[0].text, fila[1].text, fila[2].text = "2024", "$1 234", "función estable"
# ancho de columnas
for fila in tabla.rows:
    fila.cells[0].width = Inches(1.2)
```

### Imágenes
```python
doc.add_picture("grafico.png", width=Inches(5))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
```

### Saltos de página
```python
doc.add_page_break()
```

### Alineación e interlineado
```python
p = doc.add_paragraph("Párrafo justificado a doble espacio.")
p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
p.paragraph_format.line_spacing = 2.0
p.paragraph_format.space_after = Pt(6)
```

### Encabezado, pie y número de página
El número de página es un *campo* de Word; se inserta a nivel XML (python-docx no trae un
atajo). Función utilitaria:
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def numero_de_pagina(paragraph):
    run = paragraph.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)

sec = doc.sections[0]
enc = sec.header.paragraphs[0]; enc.text = "Título corto"
pie = sec.footer.paragraphs[0]; pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
pie.add_run("Página ")
numero_de_pagina(pie)
```

### Índice / tabla de contenido (campo TOC)
python-docx no rellena el índice; se inserta el campo y Word lo genera al abrir el
documento (clic derecho → "Actualizar campo", o F9). Requiere que los encabezados usen
`add_heading(..., level=1/2/3)`.
```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def insertar_toc(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    sep = OxmlElement("w:fldChar"); sep.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t"); txt.text = "Actualiza el índice con F9 en Word."
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    for el in (b, instr, sep, txt, e):
        run._r.append(el)
```

### Referencias / bibliografía en APA (sangría francesa)
Cada referencia es un párrafo con **sangría francesa** (la 1.ª línea al margen, el resto
indentado) y doble espacio. NO uses tabla ni viñetas.
```python
def referencia(doc, runs):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.left_indent = Inches(0.5)
    pf.first_line_indent = Inches(-0.5)   # francesa
    pf.line_spacing = 2.0
    pf.space_after = Pt(6)
    for texto, cursiva in runs:
        r = p.add_run(texto); r.italic = cursiva
    return p

doc.add_heading("Referencias", level=1)
referencia(doc, [("Ministerio de Finanzas. (2024). ", False),
                 ("Informe de ejecución presupuestaria 2024", True),
                 (". Quito, Ecuador.", False)])
```
Las citas en el texto (autor-año) van como texto normal: `"(Ministerio de Finanzas, 2024)"`.

---

## Leer / extraer contenido

```bash
python -X utf8 "$SKILL_DIR/scripts/extraer_texto.py" documento.docx
```
O en Python: `from docx import Document; d = Document("x.docx"); [p.text for p in d.paragraphs]`.

## Editar un documento existente

Abre con `Document("existente.docx")`, modifica y guarda. Para reemplazar texto conservando
formato, edita el `run` (no el párrafo entero):
```python
from docx import Document
doc = Document("existente.docx")
for p in doc.paragraphs:
    for run in p.runs:
        if "30 días" in run.text:
            run.text = run.text.replace("30 días", "60 días")
doc.save("modificado.docx")
```
Para inserciones estructurales complejas (mover secciones, control de cambios), edita el XML
crudo del `.docx` (es un ZIP): descomprime, edita `word/document.xml` y vuelve a comprimir.

---

## Revisión ortográfica (OBLIGATORIA antes de entregar)

Los documentos en español fallan sobre todo por **tildes** (`funcion`→`función`,
`decision`→`decisión`), por el mojibake de la consola (`posiciAn` en vez de `posición`) y
por typos. Antes de dar por terminado un `.docx`, **siempre**:

```bash
python -X utf8 "$SKILL_DIR/scripts/revisar_ortografia.py" salida.docx
```

El script extrae el texto y **señala sospechosos** (palabras que sin tilde no existen,
terminaciones `-cion`/`-sion` sin tilde, mojibake) y luego **imprime el texto completo**.
Tu trabajo:
1. Corrige cada sospechoso real (algunos pueden ser correctos; usa criterio).
2. **Lee el texto completo** buscando faltas que la heurística no detecta (concordancia,
   palabras cambiadas, signos `¿` `¡` faltantes, dobles espacios).
3. Si corriges algo, **regenera** el `.docx` y vuelve a revisar.

No entregues un documento sin haber hecho esta pasada.

## Scripts incluidos (todos MIT, correr con `-X utf8`)

| Script | Para qué |
|--------|----------|
| `extraer_texto.py` | vuelca el texto (párrafos + tablas) |
| `validar_docx.py` | validación práctica (ZIP/XML/partes + python-docx) |
| `revisar_ortografia.py` | señala posibles faltas ortográficas y muestra el texto |

## Dependencias (en esta máquina)

- **python-docx** ✅ — crear, leer, editar
- **lxml** ✅ — usado por python-docx y por `validar_docx.py`
- **LibreOffice** ⚠️ NO instalado — opcional (convertir a PDF/imágenes con `soffice`)

> **Licencia: MIT (ver `LICENSE`).** Skill **independiente**: los scripts y esta guía son
> implementación y redacción propias, sobre la librería **python-docx** (MIT) y el estándar
> abierto **OOXML (ECMA-376 / ISO/IEC 29500)**. No deriva de skills propietarias de terceros;
> es seguro publicarla bajo MIT.
