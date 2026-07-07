# opencode-skills

> [!IMPORTANT]
> **Esto solo hace falta si usas [opencode](https://opencode.ai).**
> opencode no trae skills integradas para documentos, por eso estas son adaptaciones hechas para él.
> Si trabajas en **Claude Code, Codex, Antigravity** u otro asistente que ya incluye sus propias skills
> de Office (Word, PDF, PowerPoint, Excel) y un creador de skills, **no necesitas este repo**: usa las que
> ya vienen con tu herramienta. Clónalo únicamente si tu entorno es opencode.

Skills para [opencode](https://opencode.ai) en Windows. Cada skill vive en su carpeta con un
`SKILL.md` **en inglés** (los modelos lo siguen mejor) y un `README.md` **bilingüe** (español +
inglés) que explica qué hace y cómo se usa. **Cada carpeta tiene su propia licencia** (ver la
sección "Licencias" más abajo).

*opencode skills for Windows. Each skill folder has an English `SKILL.md` (models follow it best)
plus a bilingual `README.md`.*

## Skills MIT (documentos)

Implementaciones **independientes** para trabajar documentos, escritas desde cero sobre
librerías públicas de Python y el estándar abierto OOXML. Cada una incluye un paso de
**revisión** (`scripts/spellcheck.py`) que le muestra al modelo posibles faltas (mojibake tipo
`posiciAn`, palabras duplicadas, espacio antes de puntuación) antes de entregar.

*Independent, from-scratch document skills on top of public Python libraries + the open OOXML
standard, each with a built-in proofreading step.*

| Propósito / Purpose | Carpeta / Folder | Basada en / Based on | Licencia |
|---------------------|------------------|----------------------|----------|
| Word (.docx) | [`docx-mit`](docx-mit/) | python-docx | MIT |
| PDF | [`pdf-mit`](pdf-mit/) | pypdf · reportlab · pdfplumber · PyMuPDF · pikepdf | MIT |
| PowerPoint (.pptx) | [`pptx-mit`](pptx-mit/) | python-pptx | MIT |
| Excel (.xlsx) | [`xlsx-mit`](xlsx-mit/) | openpyxl | MIT |

> Antes cada skill tenía dos carpetas (`-mit` en español y `-mit-en` en inglés). Ahora es **una
> sola carpeta por skill**: el `SKILL.md` en inglés y el `README.md` en ambos idiomas.
> *Previously each skill had separate `-mit` / `-mit-en` folders; now there is one folder per skill.*

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
`SKILL.md` y `README.md` (por ejemplo `pip install python-pptx` para `pptx-mit`).

## Revisión (proofread)

Cada skill MIT trae `scripts/spellcheck.py`: extrae el texto del documento y **señala
sospechosos** (mojibake tipo `posiciAn`, palabras duplicadas, espacio antes de puntuación) y
luego imprime el texto completo para que el modelo lea el resto en busca de faltas que la
heurística no detecta. Es un paso **obligatorio** antes de entregar cualquier documento con
texto propio.

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
