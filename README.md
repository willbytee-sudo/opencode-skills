# opencode-skills

Skills para [opencode](https://opencode.ai) en Windows, en español. Cada skill vive en
su carpeta con un `SKILL.md` y sus recursos.

## Contenido

| Skill | Qué hace | Licencia |
|-------|----------|----------|
| [`skill-creator-opencode`](skill-creator-opencode/) | Crear, mejorar, validar y empaquetar skills de opencode | Apache-2.0 (obra derivada de Anthropic) |

## Instalación

Copia la carpeta de la skill a la ruta de skills de opencode y reinicia opencode:

```bash
# Windows
cp -r skill-creator-opencode "$HOME/.config/opencode/skills/"
# (ruta final: C:\Users\<usuario>\.config\opencode\skills\skill-creator-opencode\)
```

Los scripts se corren SIEMPRE con `python -X utf8` (en Windows la consola cp1252
corrompe los acentos si no).

## Licencias y atribución

- **`skill-creator-opencode` — Apache License 2.0.** Es una **obra derivada** de la skill
  [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator)
  de **Anthropic, PBC** (Apache-2.0). Fue traducida al español, adaptada al entorno
  opencode/Windows, reescrita para no depender de PyYAML y con el harness automático de
  evals reemplazado por un flujo manual. Ver los archivos `LICENSE` y `NOTICE` de la
  carpeta para el detalle de cambios y la atribución completa.

> **Nota sobre otras skills de documentos (docx / pdf / pptx / xlsx):**
> las skills oficiales de Anthropic para Word, PDF, PowerPoint y Excel son
> **propietarias** ("source-available, no open source": prohíben crear obras derivadas y
> redistribuir). Por eso **no** se incluyen aquí adaptaciones de ellas: hacerlo violaría su
> licencia. Solo se publica material derivado de skills con licencia permisiva (Apache-2.0).

"Anthropic" y "Claude" son marcas de Anthropic, PBC. Este proyecto no está afiliado a
Anthropic ni cuenta con su respaldo; el nombre se usa solo para describir el origen del
material derivado.
