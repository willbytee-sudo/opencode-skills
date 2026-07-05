---
name: pptx-mit
description: >-
  Úsala SIEMPRE que haya un .pptx de por medio: crear presentaciones / mazos de
  diapositivas, leer o extraer su texto, o editar presentaciones existentes. Construye las
  presentaciones con la librería python-pptx. Pensada para español (acentos á é í ó ú ñ
  intactos) sobre opencode en Windows, con revisión ortográfica antes de entregar. Dispara
  con "diapositivas", "presentación", "deck", "slides" o un nombre .pptx. NO usar para Word,
  Excel ni PDF.
metadata:
  origen: skill independiente (implementación propia, MIT) basada en la librería python-pptx (MIT) y el estándar abierto OOXML (ISO/IEC 29500). No deriva de skills propietarias de terceros.
  entorno: opencode en Windows — Python 3.13 + python-pptx (pip) + PyMuPDF; LibreOffice opcional
  licencia: MIT (ver LICENSE)
  regla_critica: correr TODOS los scripts con "python -X utf8"; revisar ortografía antes de entregar
---

# PowerPoint (.pptx) en opencode — crear, leer, editar (python-pptx)

## Overview

Esta skill crea y edita presentaciones con **python-pptx** (la librería estándar de Python
para `.pptx`, licencia MIT). El modelo escribe un script de Python que arma la presentación;
la lectura de texto se hace sin dependencias (leyendo el ZIP). Al terminar, **revisa la
ortografía** antes de entregar.

> **Instala python-pptx** (no viene por defecto en esta máquina): `pip install python-pptx`.
> Los scripts de lectura (`extraer_texto.py`, `revisar_ortografia.py`) NO lo necesitan.

## Cómo opencode ejecuta esta skill (adaptaciones clave — LEER PRIMERO)

1. **`SKILL_DIR` con ruta absoluta.** opencode corre desde el directorio del proyecto:
   ```bash
   SKILL_DIR="$HOME/.config/opencode/skills/pptx-mit"
   ```
2. **REGLA UTF-8: corre Python con `-X utf8` SIEMPRE.** Sin ella, los acentos se rompen (cp1252).
3. **El texto con acentos NUNCA viaja por la consola.** El `.py` que arma la presentación se
   escribe con la herramienta de archivos (UTF-8), no con echo/Set-Content/heredocs.
4. **`extract-text` del sandbox NO existe.** Usa `extraer_texto.py`.
5. **QA visual = LibreOffice (opcional, NO instalado).** `render_diapositivas.py` usa
   LibreOffice + PyMuPDF (sin Poppler). Sin LibreOffice, haz QA de texto con `extraer_texto.py`.

## Leer / extraer texto

```bash
python -X utf8 "$SKILL_DIR/scripts/extraer_texto.py" presentacion.pptx
```

## Crear una presentación (python-pptx)

Escribe el `.py` con la herramienta de archivos y córrelo con `python -X utf8`.

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width  = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]        # layout en blanco (control total)

# --- Diapositiva de portada ---
s = prs.slides.add_slide(BLANK)
s.background.fill.solid()
s.background.fill.fore_color.rgb = RGBColor(0x1E, 0x27, 0x61)   # fondo oscuro
caja = s.shapes.add_textbox(Inches(1), Inches(2.6), Inches(11), Inches(2))
tf = caja.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]; p.text = "Informe de gestión 2024"
p.font.size = Pt(44); p.font.bold = True; p.font.name = "Arial"
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

# --- Diapositiva de contenido ---
s = prs.slides.add_slide(BLANK)
t = s.shapes.add_textbox(Inches(0.7), Inches(0.5), Inches(12), Inches(1))
tp = t.text_frame.paragraphs[0]; tp.text = "Resultados"
tp.font.size = Pt(32); tp.font.bold = True
cuerpo = s.shapes.add_textbox(Inches(0.7), Inches(1.8), Inches(7), Inches(4)).text_frame
cuerpo.word_wrap = True
for i, linea in enumerate(["Los ingresos crecieron 15%.", "La región costa lideró.", "Sin errores de conciliación."]):
    par = cuerpo.paragraphs[0] if i == 0 else cuerpo.add_paragraph()
    par.text = "•  " + linea         # viñeta manual simple, o usa numeración del layout
    par.font.size = Pt(18)

prs.save("salida.pptx")
```

### Formas, tablas, imágenes, gráficos y notas
```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

# Forma con relleno y sombra suave
rect = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8), Inches(1.8), Inches(4), Inches(2.2))
rect.fill.solid(); rect.fill.fore_color.rgb = RGBColor(0xF0, 0xF9, 0xFB)
rect.line.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)

# Tabla
tab = s.shapes.add_table(2, 2, Inches(0.7), Inches(4.2), Inches(6), Inches(1.2)).table
tab.cell(0, 0).text, tab.cell(0, 1).text = "Año", "Ingresos"
tab.cell(1, 0).text, tab.cell(1, 1).text = "2024", "$1 234"

# Imagen (mantén proporción calculando el alto)
s.shapes.add_picture("grafico.png", Inches(8), Inches(4.2), height=Inches(2.5))

# Gráfico nativo (editable en PowerPoint) — no lo conviertas a imagen
datos = CategoryChartData()
datos.categories = ["Q1", "Q2", "Q3", "Q4"]
datos.add_series("Ventas", (4.5, 5.5, 6.2, 7.1))
s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(1.8), Inches(6), Inches(3.5), datos)

# Notas del orador
s.notes_slide.notes_text_frame.text = "Abrir con el titular de ingresos. Pausar tras el 15%."
```

## Diseño (principios generales, no reglas rígidas)

Estos son criterios de diseño de uso común; adáptalos al tema:

- **Una idea por diapositiva.** Título claro + un apoyo visual (imagen, gráfico, ícono o
  forma). Evita las diapositivas de solo texto y las viñetas interminables.
- **Jerarquía por tamaño:** título 36–44 pt, subtítulos 20–24 pt, cuerpo 14–18 pt.
- **Contraste real:** texto oscuro sobre fondo claro o claro sobre oscuro; nada de gris
  claro sobre crema. Fondos oscuros lucen bien en portada y cierre.
- **Paleta con intención:** un color dominante, uno o dos de apoyo y un acento; elige según
  el tema, no azul por defecto. Mantén la misma paleta en todo el mazo.
- **Fuentes seguras** (presentes en Office y de ancho estable): Arial, Calibri, Cambria,
  Times New Roman. Empareja una serif para títulos con una sans para el cuerpo si quieres contraste.
- **Aire:** márgenes ≥ 1.3 cm, espacio uniforme entre bloques; no llenes cada rincón.
- **Que el texto quepa** en su caja: si desborda, reduce el tamaño, divide en dos
  diapositivas o agranda el contenedor. Revísalo con `render_diapositivas.py` si tienes LibreOffice.
- **Gráficos nativos** (`add_chart`), no imágenes de gráficos: quedan editables.

## Editar una presentación existente

```python
from pptx import Presentation
prs = Presentation("existente.pptx")
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for run in p.runs:
                    if "borrador" in run.text.lower():
                        run.text = run.text.replace("Borrador", "Final")
prs.save("modificado.pptx")
```

## QA visual (requiere LibreOffice)

```bash
python -X utf8 "$SKILL_DIR/scripts/render_diapositivas.py" salida.pptx imgs/ 150
```
Genera `imgs/slide-1.png`, etc. Revisa solapes, texto cortado/desbordado, contraste bajo,
márgenes y alineación. Arregla y re-renderiza solo lo afectado.

## Revisión ortográfica (OBLIGATORIA antes de entregar)

Las presentaciones en español fallan por tildes (`funcion`→`función`,
`gestion`→`gestión`), mojibake (`posiciAn`) y typos. Antes de terminar:
```bash
python -X utf8 "$SKILL_DIR/scripts/revisar_ortografia.py" salida.pptx
```
Señala sospechosos por diapositiva y muestra el texto. Corrige, **lee el resto** buscando
faltas que la heurística no ve, y **regenera** si cambiaste algo.

## Scripts incluidos (todos MIT, correr con `-X utf8`)

| Script | Para qué |
|--------|----------|
| `extraer_texto.py` | texto por diapositiva (sin dependencias) |
| `revisar_ortografia.py` | señala posibles faltas y muestra el texto |
| `render_diapositivas.py` | .pptx → PNG por diapositiva (LibreOffice + PyMuPDF) |

## Dependencias (en esta máquina)

- **python-pptx** ⚠️ NO instalado — necesario para CREAR/editar: `pip install python-pptx`
- **PyMuPDF (fitz)** ✅ — usado por `render_diapositivas.py`
- **LibreOffice (`soffice`)** ⚠️ NO instalado — opcional, solo para QA visual
- Lectura de texto (`extraer_texto.py`, `revisar_ortografia.py`): **sin dependencias** (stdlib)

> **Licencia: MIT (ver `LICENSE`).** Skill **independiente**: guía y scripts propios sobre
> la librería **python-pptx** (MIT) y el estándar abierto **OOXML**. **Nota PyMuPDF (fitz):**
> AGPL-3.0 / comercial; solo lo usa `render_diapositivas.py`. Para redistribución propietaria,
> sustitúyelo por Poppler. No deriva de skills propietarias de terceros.
