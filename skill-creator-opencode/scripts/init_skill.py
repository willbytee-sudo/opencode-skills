#!/usr/bin/env python3
"""
Andamiaje de una skill nueva para opencode: crea la carpeta con un SKILL.md de plantilla
(frontmatter válido) y las subcarpetas opcionales scripts/ references/ assets/.

Archivo nuevo (no existe en el skill-creator original de Anthropic). Distribuido bajo
Apache-2.0 junto con el resto de la skill. Ver LICENSE y NOTICE.

Uso:
    python -X utf8 init_skill.py <nombre-kebab> [carpeta_destino]

Ejemplo:
    python -X utf8 init_skill.py conversor-facturas ./skills

Crea ./skills/conversor-facturas/SKILL.md (+ scripts/ references/ assets/).
Correr SIEMPRE con `-X utf8` en Windows.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quick_validate import validate_skill  # noqa: E402

TEMPLATE = """---
name: {name}
description: >-
  [Qué habilita esta skill Y cuándo debe dispararse. Incluye frases/contextos de
  usuario concretos. Sé un poco "insistente" para que se dispare cuando sea útil:
  "Úsala siempre que el usuario mencione X, Y o Z, aunque no diga explícitamente ...".]
  Pensada para español sobre opencode en Windows.
metadata:
  entorno: opencode en Windows
  licencia: MIT
---

# {title}

## Overview

[Qué hace la skill y por qué, en una o dos frases.]

## Cómo opencode ejecuta esta skill (si trae scripts)

- **`SKILL_DIR` con ruta absoluta.** opencode corre desde el directorio del proyecto,
  no desde el de la skill:
  ```bash
  SKILL_DIR="C:/Users/GIGABYTE/.config/opencode/skills/{name}"
  ```
- **REGLA UTF-8:** corre Python con `python -X utf8` SIEMPRE (la consola cp1252 de
  Windows corrompe los acentos).
- **El texto con acentos NUNCA viaja por la consola:** escríbelo con la herramienta de
  archivos (UTF-8), no con echo/Set-Content/heredocs.

## Instrucciones

[Pasos en imperativo. Explica el *porqué* de cada cosa importante; evita MUSTs rígidos.]

## Ejemplos

**Ejemplo 1:**
Entrada: [...]
Salida: [...]
"""


def main():
    if len(sys.argv) < 2:
        print("uso: python -X utf8 init_skill.py <nombre-kebab> [carpeta_destino]")
        sys.exit(1)

    name = sys.argv[1].strip()
    if not re.match(r"^[a-z0-9-]+$", name) or name.startswith("-") or name.endswith("-") or "--" in name:
        print(f"❌ '{name}' no es kebab-case válido (minúsculas, dígitos y guiones simples).")
        sys.exit(1)

    dest_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    skill_dir = dest_root / name
    if skill_dir.exists():
        print(f"❌ Ya existe: {skill_dir}")
        sys.exit(1)

    for sub in ("scripts", "references", "assets"):
        (skill_dir / sub).mkdir(parents=True, exist_ok=True)

    title = name.replace("-", " ").capitalize()
    (skill_dir / "SKILL.md").write_text(TEMPLATE.format(name=name, title=title), encoding="utf-8")

    ok, msg = validate_skill(skill_dir)
    print(f"✅ Skill creada en {skill_dir}")
    print(f"   Validación: {msg}")
    print("   Edita SKILL.md y borra las subcarpetas scripts/references/assets que no uses.")


if __name__ == "__main__":
    main()
