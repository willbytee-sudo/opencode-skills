#!/usr/bin/env python3
"""
Validación práctica de un .docx: comprueba que el ZIP esté íntegro, que las partes XML
estén bien formadas, que existan las partes obligatorias y que python-docx lo abra.
Implementación propia (MIT). Solo stdlib + lxml + python-docx.

Uso:
    python -X utf8 validar_docx.py documento.docx

Correr SIEMPRE con `-X utf8` en Windows.
"""
import sys
import zipfile

from lxml import etree

REQUERIDAS = ("[Content_Types].xml", "word/document.xml")


def main():
    if len(sys.argv) != 2:
        print("uso: python -X utf8 validar_docx.py <documento.docx>")
        sys.exit(1)

    path = sys.argv[1]
    errores = []

    try:
        z = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        print(f"✗ No es un .docx/ZIP válido: {e}")
        sys.exit(2)

    if z.testzip():
        errores.append("ZIP corrupto")

    nombres = set(z.namelist())
    for req in REQUERIDAS:
        if req not in nombres:
            errores.append(f"Falta la parte obligatoria: {req}")

    for name in z.namelist():
        if name.endswith((".xml", ".rels")):
            try:
                etree.fromstring(z.read(name))
            except etree.XMLSyntaxError as e:
                errores.append(f"XML mal formado en {name}: {e}")

    parrafos = None
    try:
        from docx import Document
        parrafos = len(Document(path).paragraphs)
    except Exception as e:  # noqa: BLE001
        errores.append(f"python-docx no pudo abrirlo: {e}")

    if errores:
        print("✗ VALIDACIÓN FALLÓ:")
        for e in errores:
            print("  -", e)
        sys.exit(1)

    print(f"✓ VALIDACIÓN OK — ZIP íntegro, XML bien formado, partes obligatorias "
          f"presentes, python-docx lo abre ({parrafos} párrafos)")


if __name__ == "__main__":
    main()
