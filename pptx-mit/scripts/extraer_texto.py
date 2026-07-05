#!/usr/bin/env python3
"""
Extrae el texto de un .pptx, una sección `## Slide N` por diapositiva, leyendo el ZIP
directamente (los `<a:t>`). NO necesita python-pptx. Reemplaza al binario `extract-text`
del sandbox de Anthropic. Implementación propia (MIT). Solo stdlib.

Uso:
    python -X utf8 extraer_texto.py presentacion.pptx

Correr SIEMPRE con `-X utf8` en Windows.
"""
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


def main():
    if len(sys.argv) != 2:
        print("uso: python -X utf8 extraer_texto.py <presentacion.pptx>")
        sys.exit(1)

    with zipfile.ZipFile(sys.argv[1]) as z:
        slides = sorted(
            (n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)),
            key=lambda s: int(re.search(r"slide(\d+)", s).group(1)),
        )
        for i, name in enumerate(slides, 1):
            print(f"## Slide {i}")
            root = ET.fromstring(z.read(name))
            for t in root.iter(f"{{{A_NS}}}t"):
                if t.text and t.text.strip():
                    print(t.text)
            print()


if __name__ == "__main__":
    main()
