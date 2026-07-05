#!/usr/bin/env python3
"""
Empaqueta una carpeta de skill en un .zip distribuible (valida antes con quick_validate).
Para instalar en opencode: descomprime el .zip dentro de `~/.config/opencode/skills/`
(en Windows: `C:\\Users\\<usuario>\\.config\\opencode\\skills\\`) y reinicia opencode.

Derivado y MODIFICADO del script `package_skill.py` de la skill skill-creator de
Anthropic (Apache-2.0). Cambios: salida .zip para opencode, mensajes en español,
import por sys.path. Ver LICENSE y NOTICE.

Uso:
    python -X utf8 package_skill.py <carpeta_de_la_skill> [carpeta_salida]

Correr SIEMPRE con `-X utf8` en Windows.
"""
import fnmatch
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quick_validate import validate_skill  # noqa: E402

EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git"}
EXCLUDE_GLOBS = {"*.pyc"}
EXCLUDE_FILES = {".DS_Store"}
ROOT_EXCLUDE_DIRS = {"evals"}  # las evals no se distribuyen con la skill


def should_exclude(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(part in EXCLUDE_DIRS for part in parts):
        return True
    if len(parts) > 1 and parts[1] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_path.name
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_GLOBS)


def package_skill(skill_path, output_dir=None):
    skill_path = Path(skill_path).resolve()
    if not skill_path.is_dir():
        print(f"❌ No es una carpeta: {skill_path}")
        return None
    if not (skill_path / "SKILL.md").exists():
        print(f"❌ No se encontró SKILL.md en {skill_path}")
        return None

    print("🔍 Validando la skill...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ Validación fallida: {message}")
        return None
    print(f"✅ {message}\n")

    out = Path(output_dir).resolve() if output_dir else Path.cwd()
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / f"{skill_path.name}.zip"

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in skill_path.rglob("*"):
                if not f.is_file():
                    continue
                arc = f.relative_to(skill_path.parent)
                if should_exclude(arc):
                    print(f"  Omitido: {arc}")
                    continue
                zf.write(f, arc)
                print(f"  Añadido: {arc}")
        print(f"\n✅ Skill empaquetada en: {zip_path}")
        print(f"   Para instalar: descomprímela en ~/.config/opencode/skills/ y reinicia opencode.")
        return zip_path
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error creando el .zip: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("uso: python -X utf8 package_skill.py <carpeta_de_la_skill> [carpeta_salida]")
        sys.exit(1)
    result = package_skill(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    sys.exit(0 if result else 1)
