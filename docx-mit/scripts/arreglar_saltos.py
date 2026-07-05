#!/usr/bin/env python3
"""
Arregla las PÁGINAS EN BLANCO causadas por párrafos vacíos que solo contienen un salto de
página: los elimina y, en su lugar, pone "salto de página antes" (pageBreakBefore) en el
siguiente párrafo con texto. Así el corte de página queda limpio, sin página fantasma.
Implementación propia (MIT). Solo stdlib + lxml.

Uso:
    python -X utf8 arreglar_saltos.py entrada.docx salida.docx

Correr SIEMPRE con `-X utf8` en Windows. No modifica el archivo de entrada.
"""
import sys
import zipfile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def w(t):
    return f"{{{W}}}{t}"


def texto(p):
    return "".join(t.text or "" for t in p.iter(w("t"))).strip()


def tiene_salto(p):
    return any(br.get(w("type")) == "page" for br in p.iter(w("br")))


def arreglar(src, out):
    zin = zipfile.ZipFile(src)
    tree = etree.fromstring(zin.read("word/document.xml"))
    body = tree.find(w("body"))
    hijos = list(body)
    arreglados = 0

    for i, p in enumerate(hijos):
        if p.tag != w("p"):
            continue
        if tiene_salto(p) and texto(p) == "":     # párrafo vacío con SOLO el salto
            j = i + 1
            while j < len(hijos) and (hijos[j].tag != w("p") or texto(hijos[j]) == ""):
                j += 1
            if j < len(hijos):
                nxt = hijos[j]
                ppr = nxt.find(w("pPr"))
                if ppr is None:
                    ppr = etree.Element(w("pPr"))
                    nxt.insert(0, ppr)
                if ppr.find(w("pageBreakBefore")) is None:
                    pbb = etree.Element(w("pageBreakBefore"))
                    pstyle = ppr.find(w("pStyle"))
                    idx = list(ppr).index(pstyle) + 1 if pstyle is not None else 0
                    ppr.insert(idx, pbb)
                body.remove(p)
                arreglados += 1

    nuevo = etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = nuevo if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    return arreglados


def main():
    if len(sys.argv) != 3:
        print("uso: python -X utf8 arreglar_saltos.py <entrada.docx> <salida.docx>")
        sys.exit(1)
    n = arreglar(sys.argv[1], sys.argv[2])
    print(f"Arreglados {n} salto(s) de página vacíos -> {sys.argv[2]}")
    if n == 0:
        print("(No se encontraron párrafos-vacíos-con-salto; si aún ves páginas en blanco, "
              "revisa si la portada tiene demasiados párrafos vacíos que desbordan la página.)")


if __name__ == "__main__":
    main()
