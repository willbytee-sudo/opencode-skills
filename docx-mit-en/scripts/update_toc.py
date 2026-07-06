#!/usr/bin/env python3
"""
Fills (updates) the table of contents and all fields of a .docx so the TOC is built without
pressing F9 in Word. Uses Word via COM (Windows) or LibreOffice; if neither is available, it
marks the document to update fields ON OPEN (updateFields=true). Own implementation (MIT).
Stdlib only.

Usage:
    python -X utf8 update_toc.py document.docx [output.docx]

If you omit the output, it updates the same file. **Close the .docx in Word before running**
(it can't be open). Work on files in a normal folder (Documents, etc.): Word blocks files
opened by automation from %TEMP% with "Protected View". Always run with `-X utf8` on Windows.
"""
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


# ---------- Word (COM via PowerShell) — Windows ----------
def word_available() -> bool:
    if os.name != "nt":
        return False
    ps = "try { $w=New-Object -ComObject Word.Application; $w.Quit(); 'OK' } catch { 'NO' }"
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       capture_output=True, encoding="utf-8", errors="replace")
    return "OK" in (r.stdout or "")


def with_word(inp: str, out: str):
    ip = str(Path(inp).resolve())
    op = str(Path(out).resolve())
    ps = f"""
$ErrorActionPreference='Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {{
  $d = $w.Documents.Open('{ip}', $false, $false)
  [void]$d.Fields.Update()
  foreach ($toc in $d.TablesOfContents) {{ [void]$toc.Update() }}
  $d.SaveAs([ref]'{op}', [ref]16)
  $d.Close($false)
}} finally {{ $w.Quit() }}
'DONE'
"""
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       capture_output=True, encoding="utf-8", errors="replace")
    return ("DONE" in (r.stdout or "")), (r.stderr or r.stdout or "")


# ---------- LibreOffice (macro) — cross-platform ----------
MACRO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Indexes" script:language="StarBasic">
Sub UpdateIndexes
  oDoc = ThisComponent
  oIdx = oDoc.getDocumentIndexes()
  For i = 0 To oIdx.Count - 1
    oIdx.getByIndex(i).update()
  Next i
  oDoc.getTextFields().refresh()
  oDoc.store()
  oDoc.close(True)
End Sub
</script:module>"""


def find_soffice():
    c = os.environ.get("SOFFICE_BIN") or shutil.which("soffice") or shutil.which("soffice.exe")
    if c:
        return c
    for p in (r"C:\Program Files\LibreOffice\program\soffice.exe",
              r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"):
        if Path(p).exists():
            return p
    return None


def with_libreoffice(soffice: str, inp: str, out: str):
    if Path(out).resolve() != Path(inp).resolve():
        shutil.copyfile(inp, out)
    appdata = os.environ.get("APPDATA", str(Path.home() / ".config"))
    folder = Path(appdata) / "LibreOffice" / "4" / "user" / "basic" / "Standard"
    if not folder.exists():
        try:
            subprocess.run([soffice, "--headless", "--terminate_after_init"], capture_output=True, timeout=30)
        except Exception:  # noqa: BLE001
            pass
        folder.mkdir(parents=True, exist_ok=True)
    (folder / "Indexes.xba").write_text(MACRO, encoding="utf-8")
    cmd = [soffice, "--headless", "--norestore",
           "vnd.sun.star.script:Standard.Indexes.UpdateIndexes?language=Basic&location=application",
           str(Path(out).resolve())]
    try:
        r = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace", timeout=60)
    except subprocess.TimeoutExpired:
        return False, "LibreOffice timed out"
    return r.returncode == 0, (r.stderr or "")


# ---------- Fallback: mark updateFields=true ----------
def mark_update_fields(inp: str, out: str) -> None:
    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    zin = zipfile.ZipFile(inp)
    names = zin.namelist()
    if "word/settings.xml" in names:
        s = zin.read("word/settings.xml").decode("utf-8")
        if "w:updateFields" not in s:
            i = s.find(">", s.find("<w:settings")) + 1
            s = s[:i] + '<w:updateFields w:val="true"/>' + s[i:]
    else:
        s = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             f'<w:settings xmlns:w="{W}"><w:updateFields w:val="true"/></w:settings>')
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        wrote = False
        for item in zin.infolist():
            if item.filename == "word/settings.xml":
                zout.writestr(item, s); wrote = True
            else:
                zout.writestr(item, zin.read(item.filename))
        if not wrote:
            zout.writestr("word/settings.xml", s)
    zin.close()


def main():
    if len(sys.argv) not in (2, 3):
        print("usage: python -X utf8 update_toc.py <document.docx> [output.docx]")
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) == 3 else inp
    tmp = str(Path(inp).with_suffix(".tmp.docx")) if out == inp else out

    if word_available():
        ok, msg = with_word(inp, tmp)
        engine = "Word"
    else:
        soffice = find_soffice()
        if soffice:
            ok, msg = with_libreoffice(soffice, inp, tmp)
            engine = "LibreOffice"
        else:
            mark_update_fields(inp, tmp if tmp != inp else out)
            print("⚠ No Word or LibreOffice found. The document was marked so Word updates the "
                  "TOC ON OPEN (updateFields=true). Open it once in Word to fill it.")
            if out == inp and Path(tmp).exists():
                os.replace(tmp, inp)
            sys.exit(0)

    if not ok:
        print(f"✗ Update failed with {engine}:\n{msg}", file=sys.stderr)
        sys.exit(1)
    if out == inp:
        os.replace(tmp, inp)
    print(f"✓ TOC and fields updated with {engine} -> {out}")


if __name__ == "__main__":
    main()
