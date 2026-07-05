#!/usr/bin/env python3
"""
Validación rápida de una skill: comprueba SKILL.md, frontmatter, propiedades permitidas,
nombre en kebab-case y longitudes de name/description. NO depende de PyYAML (usa el parser
propio de utils.py).

Derivado y MODIFICADO del script `quick_validate.py` de la skill skill-creator de
Anthropic (Apache-2.0). Cambios: eliminada la dependencia de PyYAML, mensajes en español.
Ver LICENSE y NOTICE.

Uso:
    python -X utf8 quick_validate.py <carpeta_de_la_skill>

Correr SIEMPRE con `-X utf8` en Windows.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils import parse_skill_md  # noqa: E402

# Propiedades de frontmatter permitidas (compatibles con opencode y Claude skills).
ALLOWED_PROPERTIES = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def validate_skill(skill_path):
    skill_path = Path(skill_path)
    if not (skill_path / "SKILL.md").exists():
        return False, "No se encontró SKILL.md"

    try:
        name, description, keys, _ = parse_skill_md(skill_path)
    except ValueError as e:
        return False, str(e)

    unexpected = set(keys) - ALLOWED_PROPERTIES
    if unexpected:
        return False, (f"Clave(s) inesperada(s) en el frontmatter: {', '.join(sorted(unexpected))}. "
                       f"Permitidas: {', '.join(sorted(ALLOWED_PROPERTIES))}")

    if "name" not in keys:
        return False, "Falta 'name' en el frontmatter"
    if "description" not in keys:
        return False, "Falta 'description' en el frontmatter"

    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, f"El nombre '{name}' debe ser kebab-case (minúsculas, dígitos y guiones)"
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return False, f"El nombre '{name}' no puede empezar/terminar en guion ni tener guiones dobles"
        if len(name) > 64:
            return False, f"El nombre es muy largo ({len(name)} caracteres). Máximo 64."

    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "La description no puede contener < ni > (rompe el parseo del frontmatter)"
        if len(description) > 1024:
            return False, f"La description es muy larga ({len(description)} caracteres). Máximo 1024."

    return True, "¡La skill es válida!"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python -X utf8 quick_validate.py <carpeta_de_la_skill>")
        sys.exit(1)
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)
