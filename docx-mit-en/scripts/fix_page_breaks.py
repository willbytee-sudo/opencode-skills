#!/usr/bin/env python3
"""
Fixes BLANK PAGES caused by empty paragraphs that only contain a page break: it removes
them and instead sets "page break before" (pageBreakBefore) on the following paragraph with
text. That way the page break is clean, with no phantom page. Own implementation (MIT).
Stdlib + lxml only.

Usage:
    python -X utf8 fix_page_breaks.py input.docx output.docx

Always run with `-X utf8` on Windows. Does not modify the input file.
"""
import sys
import zipfile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def w(t):
    return f"{{{W}}}{t}"


def text(p):
    return "".join(t.text or "" for t in p.iter(w("t"))).strip()


def has_break(p):
    return any(br.get(w("type")) == "page" for br in p.iter(w("br")))


def fix(src, out):
    zin = zipfile.ZipFile(src)
    tree = etree.fromstring(zin.read("word/document.xml"))
    body = tree.find(w("body"))
    children = list(body)
    fixed = 0

    for i, p in enumerate(children):
        if p.tag != w("p"):
            continue
        if has_break(p) and text(p) == "":         # empty paragraph with ONLY the break
            j = i + 1
            while j < len(children) and (children[j].tag != w("p") or text(children[j]) == ""):
                j += 1
            if j < len(children):
                nxt = children[j]
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
                fixed += 1

    new = etree.tostring(tree, xml_declaration=True, encoding="UTF-8", standalone=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = new if item.filename == "word/document.xml" else zin.read(item.filename)
            zout.writestr(item, data)
    zin.close()
    return fixed


def main():
    if len(sys.argv) != 3:
        print("usage: python -X utf8 fix_page_breaks.py <input.docx> <output.docx>")
        sys.exit(1)
    n = fix(sys.argv[1], sys.argv[2])
    print(f"Fixed {n} empty page break(s) -> {sys.argv[2]}")
    if n == 0:
        print("(No empty-paragraph page breaks found; if you still see blank pages, check "
              "whether the cover page has too many empty paragraphs overflowing the page.)")


if __name__ == "__main__":
    main()
