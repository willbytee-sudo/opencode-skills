#!/usr/bin/env python3
"""
Utilidades compartidas para skill-creator-opencode. Parsea el frontmatter de un SKILL.md
sin depender de PyYAML (que NO está instalado en esta máquina).

Derivado y MODIFICADO de `utils.py` de la skill skill-creator de Anthropic (Apache-2.0):
reimplementado sin PyYAML y devolviendo también las claves de primer nivel. Ver LICENSE y NOTICE.
"""
import re
from pathlib import Path


def parse_skill_md(skill_path: Path):
    """Devuelve (name, description, top_level_keys, full_content) de un SKILL.md.

    `top_level_keys` es la lista de claves de primer nivel del frontmatter (para validar
    propiedades permitidas). Soporta description en una línea o en bloque YAML (>, |, >-, |-).
    """
    content = (Path(skill_path) / "SKILL.md").read_text(encoding="utf-8")
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md sin frontmatter (falta el --- de apertura)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise ValueError("SKILL.md sin frontmatter (falta el --- de cierre)")

    fm = lines[1:end_idx]
    name = ""
    description = ""
    top_level_keys = []

    i = 0
    while i < len(fm):
        line = fm[i]
        # Clave de primer nivel: empieza en columna 0 con "clave:"
        m = re.match(r"^([A-Za-z][\w-]*):(.*)$", line)
        if m:
            key, rest = m.group(1), m.group(2).strip()
            top_level_keys.append(key)
            if key == "name":
                name = rest.strip('"').strip("'")
            elif key == "description":
                if rest in (">", "|", ">-", "|-", ">+", "|+"):
                    cont = []
                    i += 1
                    while i < len(fm) and (fm[i].startswith("  ") or fm[i].startswith("\t") or fm[i].strip() == ""):
                        cont.append(fm[i].strip())
                        i += 1
                    description = " ".join(c for c in cont if c)
                    continue
                description = rest.strip('"').strip("'")
        i += 1

    return name, description, top_level_keys, content


if __name__ == "__main__":
    import sys
    n, d, keys, _ = parse_skill_md(sys.argv[1])
    print("name:", n)
    print("description:", d[:120], "...")
    print("keys:", keys)
