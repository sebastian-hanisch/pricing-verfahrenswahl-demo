"""Gemeinsame Fixtures: die Mini-Zelle, an der jede Einheit der Auswahlregel von Hand geprüft wird (DEMO-PLAYBOOK §1b), und Hilfen zum Laden der Messdaten."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def _zeilen(seed_werte: dict) -> list:
    """{k: [(schranke, labels), ...je Instanz mit Zufalls-Seed 0, 1, 2]} in die Zeilenform der Datei k_zellen.json bringen."""
    return [{"seed": seed, "k": k, "schranke": s, "labels": lab} for k, paare in seed_werte.items() for seed, (s, lab) in enumerate(paare)]


@pytest.fixture
def mini():
    """Mini-Zelle: 3 Instanzen, k = 1, 3 und der Bezug k = 16, Schranken und Labels von Hand gesetzt.

    Handrechnung der Lücken in Prozent des Bezugs (Bezug 100, 200, 400):
      k = 1:  (100 - 98) / 100 = 2,0 ; (200 - 197) / 200 = 1,5 ; (400 - 396) / 400 = 1,0   -> Mittel 1,5, Maximum 2,0
      k = 3:  (100 - 99,75) / 100 = 0,25 ; (200 - 199,5) / 200 = 0,25 ; (400 - 399) / 400 = 0,25   -> Mittel 0,25, Maximum 0,25
      k = 16: Bezug, Lücke 0
    Labels (Median über die drei Instanzen): k = 1: 10, 20, 30 -> 20 ; k = 3: 20, 40, 60 -> 40 ; k = 16: 50, 100, 150 -> 100."""
    return {
        "id": "mini", "typ": "zufällig", "n": 50, "breite": 40, "bezug": 16, "ks": [1, 3, 16],
        "quelle": {"demo": "handbeispiel", "datei": "-", "text": "von Hand"},
        "zeilen": _zeilen({
            1: [(98.0, 10), (197.0, 20), (396.0, 30)],
            3: [(99.75, 20), (199.5, 40), (399.0, 60)],
            16: [(100.0, 50), (200.0, 100), (400.0, 150)],
        }),
    }


@pytest.fixture(scope="session")
def zellen():
    import pvw_daten as D
    return D.k_zellen()
