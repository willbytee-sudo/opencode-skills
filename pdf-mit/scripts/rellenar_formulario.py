#!/usr/bin/env python3
"""
Formularios PDF rellenables (AcroForm) con la API estándar de pypdf. Implementación propia (MIT).

Modos:
    # 1) Listar los campos del formulario (nombre y tipo)
    python -X utf8 rellenar_formulario.py listar entrada.pdf

    # 2) Rellenar desde un JSON {"campo": "valor", ...} (checkbox: "/Yes" para marcar)
    python -X utf8 rellenar_formulario.py rellenar entrada.pdf valores.json salida.pdf

El JSON de valores se escribe con la herramienta de archivos (UTF-8) para no romper acentos.
Correr SIEMPRE con `-X utf8` en Windows.

Si el PDF NO tiene campos rellenables, este script no aplica: hay que superponer texto
(ver la sección "Formularios no rellenables" en SKILL.md).
"""
import json
import sys

from pypdf import PdfReader, PdfWriter


def listar(pdf_path: str):
    campos = PdfReader(pdf_path).get_fields()
    if not campos:
        print("Este PDF NO tiene campos de formulario rellenables (AcroForm).")
        return
    print(f"{len(campos)} campo(s):")
    for nombre, f in campos.items():
        tipo = {"/Tx": "texto", "/Btn": "botón/checkbox", "/Ch": "selección"}.get(f.get("/FT"), f.get("/FT"))
        estados = f.get("/_States_")
        extra = f"  estados={list(estados)}" if estados else ""
        print(f"  - {nombre}  ({tipo}){extra}")


def rellenar(pdf_path: str, valores_json: str, salida: str):
    with open(valores_json, encoding="utf-8") as fh:
        valores = json.load(fh)

    reader = PdfReader(pdf_path)
    campos = reader.get_fields() or {}
    invalidos = [k for k in valores if k not in campos]
    if invalidos:
        print(f"ERROR: campos que no existen en el PDF: {invalidos}")
        print(f"Campos válidos: {list(campos)}")
        sys.exit(1)

    writer = PdfWriter(clone_from=reader)
    for page in writer.pages:
        writer.update_page_form_field_values(page, valores, auto_regenerate=False)
    writer.set_need_appearances_writer(True)

    with open(salida, "wb") as fh:
        writer.write(fh)
    print(f"Formulario rellenado -> {salida}")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "listar":
        listar(sys.argv[2])
    elif len(sys.argv) == 5 and sys.argv[1] == "rellenar":
        rellenar(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("uso:")
        print("  python -X utf8 rellenar_formulario.py listar <entrada.pdf>")
        print("  python -X utf8 rellenar_formulario.py rellenar <entrada.pdf> <valores.json> <salida.pdf>")
        sys.exit(1)


if __name__ == "__main__":
    main()
