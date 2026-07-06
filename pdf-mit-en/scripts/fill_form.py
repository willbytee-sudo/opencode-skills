#!/usr/bin/env python3
"""
Fillable PDF forms (AcroForm) with pypdf's standard API. Own implementation (MIT).

Modes:
    # 1) List the form fields (name and type)
    python -X utf8 fill_form.py list input.pdf

    # 2) Fill from a JSON {"field": "value", ...} (checkbox: "/Yes" to check)
    python -X utf8 fill_form.py fill input.pdf values.json output.pdf

Write the values JSON with the file tool (UTF-8). Always run with `-X utf8` on Windows.

If the PDF has NO fillable fields, this script does not apply: overlay text instead (see the
"Non-fillable forms" section in SKILL.md).
"""
import json
import sys

from pypdf import PdfReader, PdfWriter


def list_fields(pdf_path: str):
    fields = PdfReader(pdf_path).get_fields()
    if not fields:
        print("This PDF has NO fillable form fields (AcroForm).")
        return
    print(f"{len(fields)} field(s):")
    for name, f in fields.items():
        kind = {"/Tx": "text", "/Btn": "button/checkbox", "/Ch": "choice"}.get(f.get("/FT"), f.get("/FT"))
        states = f.get("/_States_")
        extra = f"  states={list(states)}" if states else ""
        print(f"  - {name}  ({kind}){extra}")


def fill(pdf_path: str, values_json: str, output: str):
    with open(values_json, encoding="utf-8") as fh:
        values = json.load(fh)
    reader = PdfReader(pdf_path)
    fields = reader.get_fields() or {}
    invalid = [k for k in values if k not in fields]
    if invalid:
        print(f"ERROR: fields not present in the PDF: {invalid}")
        print(f"Valid fields: {list(fields)}")
        sys.exit(1)
    writer = PdfWriter(clone_from=reader)
    for page in writer.pages:
        writer.update_page_form_field_values(page, values, auto_regenerate=False)
    writer.set_need_appearances_writer(True)
    with open(output, "wb") as fh:
        writer.write(fh)
    print(f"Form filled -> {output}")


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "list":
        list_fields(sys.argv[2])
    elif len(sys.argv) == 5 and sys.argv[1] == "fill":
        fill(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("usage:")
        print("  python -X utf8 fill_form.py list <input.pdf>")
        print("  python -X utf8 fill_form.py fill <input.pdf> <values.json> <output.pdf>")
        sys.exit(1)


if __name__ == "__main__":
    main()
