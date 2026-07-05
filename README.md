# opencode-skills

> [!IMPORTANT]
> **Esto solo hace falta si usas [opencode](https://opencode.ai).**
> opencode no trae skills integradas para documentos, por eso estas son adaptaciones hechas para él.
> Si trabajas en **Claude Code, Codex, Antigravity** u otro asistente que ya incluye sus propias skills
> de Office (Word, PDF, PowerPoint, Excel) y un creador de skills, **no necesitas este repo**: usa las que
> ya vienen con tu herramienta. Clónalo únicamente si tu entorno es opencode.

Skills para [opencode](https://opencode.ai) en Windows, en español. Cada skill vive en su
carpeta con un `SKILL.md` y sus recursos, y **cada una tiene su propia licencia** (ver la
sección "Licencias" más abajo).

## Skills MIT (documentos)

Implementaciones **independientes** para trabajar documentos, escritas desde cero sobre
librerías públicas de Python y el estándar abierto OOXML. Cada una incluye un paso de
**revisión ortográfica** que le muestra al modelo posibles faltas (tildes, mojibake tipo
`posiciAn`, terminaciones `-ción`/`-sión`/`-tión`) antes de entregar.

| Skill | Qué hace | Basada en | Licencia |
|-------|----------|-----------|----------|
| [`docx-mit`](docx-mit/) | Crear/leer/editar Word (.docx) | python-docx | MIT |
| [`pdf-mit`](pdf-mit/) | Leer/crear/editar PDF, formularios, imágenes | pypdf · reportlab · pdfplumber · PyMuPDF · pikepdf | MIT |
| [`pptx-mit`](pptx-mit/) | Crear/leer/editar presentaciones (.pptx) | python-pptx | MIT |
| [`xlsx-mit`](xlsx-mit/) | Crear/leer/editar hojas de cálculo (.xlsx) | openpyxl | MIT |

## Otras skills

| Skill | Qué hace | Licencia |
|-------|----------|----------|
| [`skill-creator-opencode`](skill-creator-opencode/) | Crear, mejorar, validar y empaquetar skills de opencode | Apache-2.0 (obra derivada de Anthropic) |

## Instalación

Copia la carpeta de la skill a la ruta de skills de opencode y reinicia opencode:

```bash
cp -r docx-mit "$HOME/.config/opencode/skills/"
# (ruta final en Windows: C:\Users\<usuario>\.config\opencode\skills\docx-mit\)
```

Los scripts se corren **siempre** con `python -X utf8` (en Windows la consola cp1252
corrompe los acentos si no). Algunas skills piden dependencias extra que se indican en su
`SKILL.md` (por ejemplo `pip install python-pptx` para `pptx-mit`).

## Revisión ortográfica

Cada skill MIT trae `scripts/revisar_ortografia.py`: extrae el texto del documento y
**señala sospechosos** para el español (palabras que sin tilde no existen, terminaciones
`consonante+ion` que deberían llevar tilde, y mojibake de codificación), respetando los
plurales (`funciones`), `guion` y las palabras ya acentuadas. Luego imprime el texto completo
para que el modelo lea el resto en busca de faltas que la heurística no detecta.

## Licencias

Este repositorio usa **licencias por carpeta**:

- **`docx-mit`, `pdf-mit`, `pptx-mit`, `xlsx-mit` — MIT.** Implementación y redacción
  propias sobre librerías de terceros de licencia permisiva (python-docx, pypdf, reportlab,
  pdfplumber, pikepdf, python-pptx, openpyxl) y el estándar abierto **OOXML (ECMA-376 /
  ISO/IEC 29500)**. **No** derivan de skills propietarias de terceros. La licencia MIT de la
  raíz aplica a estas skills, al README y al andamiaje del repo.
  > Nota: `pdf-mit` y `pptx-mit` incluyen un script opcional que usa **PyMuPDF (fitz)**,
  > que es AGPL-3.0. Solo se usa para renderizar a imagen; para redistribución propietaria,
  > sustitúyelo por `pypdfium2` (Apache/BSD) o Poppler. El resto es de licencia permisiva.

- **`skill-creator-opencode` — Apache License 2.0.** Es una **obra derivada** de la skill
  [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) de
  **Anthropic, PBC** (Apache-2.0), traducida y adaptada. Su carpeta contiene su propia
  `LICENSE` (Apache-2.0) y un `NOTICE` con la atribución y la lista de cambios, que rigen esa
  skill.

> Las skills oficiales de Anthropic para Word, PDF, PowerPoint y Excel son **propietarias**
> (prohíben derivar y redistribuir); por eso las `-mit` de este repo se escribieron de forma
> independiente y **no** son adaptaciones de ellas.

"Anthropic" y "Claude" son marcas de Anthropic, PBC. Este proyecto no está afiliado a
Anthropic ni cuenta con su respaldo.
