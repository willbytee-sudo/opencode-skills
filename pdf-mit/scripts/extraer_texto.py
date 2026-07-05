#!/usr/bin/env python3
"""
Extrae el texto de un .pdf con pdfplumber (mejor conserva el layout que pypdf).
Reemplaza al binario `extract-text` del sandbox de Anthropic. Implementación propia (MIT).

Uso:
    python -X utf8 extraer_texto.py documento.pdf [--tablas]

Con `--tablas` intenta además extraer tablas. Correr SIEMPRE con `-X utf8` en Windows.
"""
import sys

import pdfplumber


def main():
    args = sys.argv[1:]
    tablas = "--tablas" in args
    args = [a for a in args if a != "--tablas"]
    if len(args) != 1:
        print("uso: python -X utf8 extraer_texto.py <documento.pdf> [--tablas]")
        sys.exit(1)

    with pdfplumber.open(args[0]) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            print(f"## Página {i}")
            print(page.extract_text() or "")
            if tablas:
                for j, tabla in enumerate(page.extract_tables(), 1):
                    print(f"\n[Tabla {j} en página {i}]")
                    for fila in tabla:
                        print("\t".join("" if c is None else c for c in fila))
            print()


if __name__ == "__main__":
    main()
