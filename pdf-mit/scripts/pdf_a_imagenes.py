#!/usr/bin/env python3
"""
Convierte cada página de un .pdf a PNG con PyMuPDF (fitz) — NO necesita Poppler.
Implementación propia (MIT).

Uso:
    python -X utf8 pdf_a_imagenes.py entrada.pdf carpeta_salida/ [dpi]

Correr SIEMPRE con `-X utf8` en Windows.
"""
import os
import sys

import fitz  # PyMuPDF


def convertir(pdf_path, out_dir, dpi=200):
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = dpi / 72.0
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        dest = os.path.join(out_dir, f"pagina_{i}.png")
        pix.save(dest)
        print(f"Guardada {dest} ({pix.width}x{pix.height})")
    print(f"Convertidas {doc.page_count} páginas")


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        print("uso: python -X utf8 pdf_a_imagenes.py <entrada.pdf> <carpeta_salida> [dpi]")
        sys.exit(1)
    dpi = int(sys.argv[3]) if len(sys.argv) == 4 else 200
    convertir(sys.argv[1], sys.argv[2], dpi)
