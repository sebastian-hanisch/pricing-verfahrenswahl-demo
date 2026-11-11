"""README: Testzahl stimmt mit der Suite überein, die Annahmen stehen wortgleich in README und App, Verweise auf Demos nur, wenn der Ordner existiert, Wortwahl nach DEMO-PLAYBOOK §7."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

import pvw_texte as T

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_testzahl_in_der_readme_gleicht_der_suite():
    lauf = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests", "-p", "no:cacheprovider"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=300)
    m = re.search(r"(\d+) tests? collected", lauf.stdout)
    assert m, lauf.stdout[-400:] + lauf.stderr[-400:]
    assert f"\n{m.group(1)} Tests, Laufzeit" in README, f"README nennt nicht {m.group(1)} Tests"


def test_annahmen_text_der_app_steht_wortgleich_in_der_readme():
    assert T.ANNAHMEN_ZEILEN.strip() in README


def test_verlinkte_demos_der_reihe_existieren_als_ordner():
    namen = set(re.findall(r"https://github\.com/sebastian-hanisch/([a-z0-9-]+-demo)\b", README))
    assert {"crew-pairing-demo", "ng-routen-demo", "heuristisches-pricing-demo", "hub-labeling-demo"} <= namen
    if not (ROOT.parent / "crew-pairing-demo").is_dir():
        pytest.skip("die anderen Demos liegen nicht neben dieser (CI)")
    fehlt = sorted(n for n in namen if not (ROOT.parent / n).is_dir())
    assert not fehlt, f"verlinkt, aber kein Ordner: {fehlt}"


def test_jede_demo_der_reihe_die_hier_genannt_wird_ist_verlinkt_und_umgekehrt():
    verlinkt = set(re.findall(r"\]\(https://github\.com/sebastian-hanisch/([a-z0-9-]+-demo)\)", README))
    reihe = {"weg-mit-grenzen-demo", "dominanz-labels-demo", "zeitfenster-labeling-demo", "mehrere-grenzen-demo", "pricing-dualpreise-demo", "kreise-im-pricing-demo", "elementar-pricing-demo",
             "ng-routen-demo", "bidirektional-labeling-demo", "eimer-labeling-demo", "kantenstreichung-pricing-demo", "heuristisches-pricing-demo"}
    assert reihe <= verlinkt


VERBOTEN = [r"\bträgt\b", r"\btragen\b", r"\btragend", r"läuft lokal", r"Saatwert", r"Phase 0", r"\bStück\b", r"\bPreset", r"\bVolk\b"]


@pytest.mark.parametrize("datei", ["README.md", "pvw_texte.py", "pvw_baum.py", "pvw_evaluation.py", "app.py"])
def test_wortwahl(datei):
    text = (ROOT / datei).read_text(encoding="utf-8")
    if datei == "app.py":
        text = re.sub(r"sidebar_presets|apply_preset|preset_", "", text)
    for muster in VERBOTEN:
        assert not re.search(muster, text), (datei, muster)


def test_keine_ascii_umlaute_in_den_texten():
    for datei in ("README.md", "pvw_texte.py", "pvw_baum.py"):
        text = (ROOT / datei).read_text(encoding="utf-8")
        for wort in ("fuer ", "ueber ", "Schluessel", "Loesung", "waehle ", "koennen"):
            assert wort not in text.replace("waehle_k", ""), (datei, wort)
