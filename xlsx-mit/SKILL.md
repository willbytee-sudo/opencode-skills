---
name: xlsx-mit
description: >-
  Úsala siempre que una hoja de cálculo sea la entrada o la salida principal: abrir, leer,
  editar o arreglar un .xlsx/.xlsm/.csv (agregar columnas, fórmulas, formato, limpiar
  datos); crear una hoja desde cero; o convertir datos tabulares. Construida sobre openpyxl.
  Pensada para español (acentos á é í ó ú ñ intactos) sobre opencode en Windows, con revisión
  ortográfica de las celdas de texto antes de entregar. Dispara cuando el usuario menciona un
  archivo de hoja de cálculo. NO usar cuando el entregable principal es Word, PDF o PowerPoint.
metadata:
  origen: skill independiente (implementación propia, MIT) basada en la librería openpyxl (MIT) y el estándar abierto OOXML (ISO/IEC 29500). No deriva de skills propietarias de terceros.
  entorno: opencode en Windows — Python 3.13 + openpyxl; pandas y LibreOffice opcionales
  licencia: MIT (ver LICENSE)
  regla_critica: correr TODOS los scripts con "python -X utf8"; usar fórmulas (no hardcodear); revisar ortografía antes de entregar
---

# Excel (.xlsx) en opencode — crear, editar, analizar (openpyxl)

## Overview

Esta skill crea y edita hojas de cálculo con **openpyxl** (la librería estándar de Python
para `.xlsx`, licencia MIT, ya instalada). Al crear texto en español, **revisa la ortografía**
de las celdas de texto antes de entregar.

## Cómo opencode ejecuta esta skill (adaptaciones clave — LEER PRIMERO)

1. **`SKILL_DIR` con ruta absoluta.** opencode corre desde el directorio del proyecto:
   ```bash
   SKILL_DIR="$HOME/.config/opencode/skills/xlsx-mit"
   ```
2. **REGLA UTF-8: corre Python con `-X utf8` SIEMPRE.** Sin ella, los acentos se rompen (cp1252).
3. **El texto con acentos NUNCA viaja por la consola.** El `.py` que arma el libro (y los
   `.csv` de origen) se escriben con la herramienta de archivos en UTF-8, no con echo/heredocs.
4. **`extract-text` del sandbox NO existe.** Usa `extraer_texto.py`.
5. **`recalcular.py` necesita LibreOffice (NO instalado).** openpyxl escribe las fórmulas pero
   NO sus valores; Excel las calcula al abrir. **pandas NO está instalado** (`pip install pandas`);
   para casi todo usa openpyxl (✅).

## CRÍTICO: fórmulas, no valores hardcodeados

Usa fórmulas de Excel en vez de calcular en Python y pegar el número. Así la hoja sigue
siendo dinámica y recalculable.
```python
# ❌ MAL: sheet['B10'] = df['Ventas'].sum()      # hardcodea 5000
# ✅ BIEN:
sheet['B10'] = '=SUM(B2:B9)'
sheet['C5']  = '=(C4-C2)/C2'
sheet['D20'] = '=AVERAGE(D2:D19)'
```

## Leer / analizar

```bash
python -X utf8 "$SKILL_DIR/scripts/extraer_texto.py" libro.xlsx | head -50           # fórmulas
python -X utf8 "$SKILL_DIR/scripts/extraer_texto.py" libro.xlsx --valores | head -50  # valores cacheados
```
```python
from openpyxl import load_workbook
wb = load_workbook('libro.xlsx')                       # fórmulas y formato
wb_val = load_workbook('libro.xlsx', data_only=True)   # valores cacheados (si existen)
```
pandas (⚠️ `pip install pandas`): `import pandas as pd; df = pd.read_excel('libro.xlsx')`.

## Crear un libro (openpyxl)

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = Workbook(); ws = wb.active; ws.title = "Presupuesto"
ws["A1"] = "Año"; ws["B1"] = "Ingresos ($)"; ws["C1"] = "Descripción"
ws.append([2024, 1234, "gestión de la región costa"])
ws.append([2025, 1500, "variación interanual"])
ws["B4"] = "=SUM(B2:B3)"                 # fórmula, no el número

# Formato de encabezados
for celda in ws[1]:
    celda.font = Font(bold=True, color="FFFFFF")
    celda.fill = PatternFill("solid", start_color="1E2761")
    celda.alignment = Alignment(horizontal="center")
ws.column_dimensions["C"].width = 32
ws["B2"].number_format = '"$"#,##0'      # formato de moneda

wb.save("salida.xlsx")
```

### Modelos financieros (convenciones útiles)
- **Colores de texto:** azul = inputs/escenarios; negro = fórmulas; verde = enlaces a otra hoja.
- **Números:** años como texto ("2024"); moneda `$#,##0` con unidades en el encabezado;
  porcentajes `0.0%`; negativos entre paréntesis; ceros como "-" (`"$#,##0;($#,##0);-"`).
- **Supuestos aparte** y referenciados: `=B5*(1+$B$6)`, no `=B5*1.05`.
- **Documenta los hardcodes** con una nota/celda al lado (fuente, fecha, referencia).

### Editar un libro existente
```python
from openpyxl import load_workbook
wb = load_workbook("existente.xlsx")
ws = wb.active                          # o wb["NombreHoja"]
ws["A1"] = "Nuevo valor"
ws.insert_rows(2); ws.delete_cols(3)
wb.create_sheet("Resumen")["A1"] = "Datos"
wb.save("modificado.xlsx")
```
`data_only=True` lee valores cacheados, pero **si guardas así pierdes las fórmulas**. Para
archivos grandes usa `read_only=True` / `write_only=True`.

## Recalcular y verificar errores (requiere LibreOffice)

```bash
python -X utf8 "$SKILL_DIR/scripts/recalcular.py" salida.xlsx
```
Devuelve JSON; si `status` es `errors_found`, revisa `error_summary` (#REF!, #DIV/0!, ...),
corrige y repite. Sin LibreOffice: entrega con fórmulas (Excel calcula al abrir) y revisa los rangos.

## Revisión ortográfica (OBLIGATORIA antes de entregar)

Cuando el libro trae **texto** (encabezados, etiquetas, descripciones), revísalo — sobre
todo tildes (`gestion`→`gestión`), terminaciones `-ción`/`-sión`/`-tión` y mojibake (`posiciAn`):
```bash
python -X utf8 "$SKILL_DIR/scripts/revisar_ortografia.py" salida.xlsx
```
Solo mira celdas de texto (ignora números y fórmulas). Señala sospechosos con su celda
(`Hoja!B3`) y lista los textos. Corrige, **lee el resto** y **regenera** si cambiaste algo.

## Scripts incluidos (todos MIT, correr con `-X utf8`)

| Script | Para qué |
|--------|----------|
| `extraer_texto.py` | vuelca cada hoja como TSV (fórmulas o valores) |
| `revisar_ortografia.py` | señala posibles faltas en las celdas de texto |
| `recalcular.py` | recalcula fórmulas y escanea errores (requiere LibreOffice) |

## Dependencias (en esta máquina)

- **openpyxl** ✅ — crear, leer, editar, fórmulas, formato (herramienta principal)
- **pandas** ⚠️ NO instalado — solo para análisis (`pip install pandas`)
- **LibreOffice (`soffice`)** ⚠️ NO instalado — solo para `recalcular.py`

> **Licencia: MIT (ver `LICENSE`).** Skill **independiente**: guía y scripts propios sobre la
> librería **openpyxl** (MIT) y el estándar abierto **OOXML (ECMA-376 / ISO/IEC 29500)**. No
> deriva de skills propietarias de terceros; es seguro publicarla bajo MIT.
