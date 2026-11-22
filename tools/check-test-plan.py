"""Validate author ownership, IDs and shared documentation without importing test dependencies."""

from __future__ import annotations

import ast
from collections import Counter
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"\bTC-(?:API|UI)-(?:AK|LM)-\d{2}\b")


def marks(node: ast.FunctionDef | ast.ClassDef) -> set[str]:
    return {d.attr for d in node.decorator_list if isinstance(d, ast.Attribute)
            and isinstance(d.value, ast.Attribute) and d.value.attr == "mark"
            and isinstance(d.value.value, ast.Name) and d.value.value.id == "pytest"}


def collected_structure(path: Path) -> dict[str, tuple[str, set[str]]]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    found = {}
    for top in tree.body:
        candidates = [(n, marks(top)) for n in top.body if isinstance(n,ast.FunctionDef)] if isinstance(top,ast.ClassDef) and top.name.startswith("Test") else [(top,set())]
        for node, inherited in candidates:
            if not isinstance(node,ast.FunctionDef) or not node.name.startswith("test_"):
                continue
            match = ID.search(ast.get_docstring(node) or "")
            assert match is not None, f"Missing canonical ID: {path.name}::{node.name}"
            assert node.name not in found, f"Duplicate function: {node.name}"
            found[node.name] = (match.group(), inherited | marks(node))
    return found


def word_data(path: Path) -> tuple[set[str], bytes]:
    with ZipFile(path) as archive:
        tree = ET.fromstring(archive.read("word/document.xml"))
        ns = {"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        text = "\n".join(node.text or "" for node in tree.findall(".//w:t",ns))
        return set(ID.findall(text)), archive.read("word/styles.xml")


def api_logic(source: str) -> str:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body.pop(0)
        if isinstance(node, ast.FunctionDef):
            match = re.match(r"test_tc_api_lm_(\d{2})_(.*)",node.name)
            if match:
                node.name = f"test_luk_{int(match[1]):03}_{match[2]}"
    return ast.dump(tree, include_attributes=False)


def main() -> None:
    cases = json.loads((ROOT / "docs/test_cases.json").read_text(encoding="utf-8"))
    assert len(cases) == 24
    assert len({c["id"] for c in cases}) == 24
    counts = Counter((c["owner"],c["layer"]) for c in cases)
    assert counts == Counter({("aleksander","api"):8,("lukasz","api"):8,("aleksander","frontend"):4,("lukasz","frontend"):4})
    for name in sorted({c["test_file"] for c in cases}):
        implemented = collected_structure(ROOT / name)
        planned = [c for c in cases if c["test_file"] == name]
        assert len(implemented) == len(planned), f"Case count differs: {name}"
        for c in planned:
            identifier, decorators = implemented[c["function"]]
            assert identifier == c["id"], c["id"]
            assert c["owner"] in decorators, c["id"]
            assert ("frontend" in decorators) == (c["layer"] == "frontend"), c["id"]
            assert c["preconditions"] and c["steps"] and c["postconditions"]
        print(f"{name}: {len(planned)} cases; IDs and ownership OK")
    expected = {c["id"] for c in cases}
    for name in ["PLAN_TESTOW_API_UI.md", "PRZYPADKI_TESTOWE_API.md"]:
        text = (ROOT/name).read_text(encoding="utf-8")
        assert all(f"| **{case_id}** |" in text for case_id in expected), name
        assert not re.search(r"\bUI-LUK-\d{3}\b|\*\*LUK-\d{3}\*\*",text), name
    for name in ["Plan_Testow_ERPSystem_Nowy.docx","Przypadki_Testowe_API_ERPSystem.docx"]:
        ids, styles = word_data(ROOT/name)
        assert ids == expected, f"DOCX case IDs differ: {name}"
        with ZipFile(BytesIO(subprocess.check_output(["git","show",f"af43160fc201760d3d49d66c8f6a4a2b615c9ed0:{name}"],cwd=ROOT))) as baseline:
            assert styles == baseline.read("word/styles.xml"), f"Main Word style definitions changed: {name}"
    for name in ["tests/test_api_aleksander.py","tests/test_frontend_aleksander.py"]:
        baseline = subprocess.check_output(["git","show",f"af43160fc201760d3d49d66c8f6a4a2b615c9ed0:{name}"],cwd=ROOT)
        assert (ROOT/name).read_bytes() == baseline, f"Aleksander's test source changed: {name}"
    old_api = subprocess.check_output(["git","show","af43160fc201760d3d49d66c8f6a4a2b615c9ed0:tests/test_api_lukasz.py"],cwd=ROOT).decode("utf-8-sig")
    assert api_logic(old_api) == api_logic((ROOT/"tests/test_api_lukasz.py").read_text(encoding="utf-8")), "Lukasz API logic changed beyond IDs/function names"
    assert not (ROOT/"package.json").exists() and not (ROOT/"playwright.config.cjs").exists()
    assert not list((ROOT/"ui").rglob("*.cjs"))
    print("Shared plan/code/Word structure OK: 16 API + 8 UI; four UI belong to Lukasz.")
    print("Aleksander's test sources and main Word style definitions are unchanged. No runtime tests executed.")


if __name__ == "__main__":
    main()
