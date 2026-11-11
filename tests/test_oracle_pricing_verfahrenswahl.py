"""Orakel-Tests: die Auswahlregel gegen zwei unabhängige Rechenwege.

1. Eine zweite Implementierung in diesem Test (reine Schleifen, `statistics`, Tabelle aus der Datei neu gelesen, kein Aufruf von `pvw_algorithm`).
2. Das Skript `hand_16.py` der Vormessung (liest die Rohdateien `out_v8_*.txt` selbst, anderer Code, andere Datenquelle): gleiche Wahl und gleiches Labels-Verhältnis in allen acht Zellen
   bei mehreren Schwellenpaaren. Wird nur ausgeführt, wenn der Ordner der Vormessung neben der Demo liegt (sonst übersprungen, nie geraten).
Laufzeit zusammen unter 10 Sekunden."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import pvw_algorithm as A
import pvw_constants as C

ROOT = Path(__file__).resolve().parent.parent
VORMESSUNG = ROOT.parent / "label-setting-planung" / "vormessung"
SCHWELLEN = [(0.25, 1.0), (0.1, 0.5), (1.0, 5.0), (0.05, 0.25), (0.5, 2.0)]


def _zweite_implementierung(zelle: dict, tau_mittel: float, tau_max: float):
    """(k, Labels(k)/Labels(Bezug)) mit einfachen Schleifen: kein Wörterbuch nach Seed, keine Hilfsfunktionen der Demo."""
    zeilen = zelle["zeilen"]
    bezug = zelle["bezug"]
    for k in sorted(zelle["ks"]):
        luecken = []
        for z in zeilen:
            if z["k"] != k:
                continue
            for b in zeilen:
                if b["k"] == bezug and b["seed"] == z["seed"]:
                    luecken.append(100.0 * (b["schranke"] - z["schranke"]) / b["schranke"])
        summe = 0.0
        for x in luecken:
            summe += x
        mittel = summe / len(luecken)
        if mittel <= tau_mittel and max(luecken) <= tau_max:
            def median(werte):
                werte = sorted(werte)
                m = len(werte) // 2
                return werte[m] if len(werte) % 2 else (werte[m - 1] + werte[m]) / 2
            return k, median([z["labels"] for z in zeilen if z["k"] == k]) / median([z["labels"] for z in zeilen if z["k"] == bezug])
    raise AssertionError("der Bezug erfüllt immer beide Schwellen")


@pytest.mark.parametrize("tm, tx", SCHWELLEN)
def test_zweite_implementierung_gibt_in_allen_elf_zellen_dasselbe(zellen, tm, tx):
    assert len(zellen) == 11
    for z in zellen:
        w = A.waehle_k(z, tm, tx)
        k, verh = _zweite_implementierung(z, tm, tx)
        assert w.k == k, z["id"]
        assert w.labels_verhaeltnis == pytest.approx(verh, rel=1e-12), z["id"]


def test_die_zweite_implementierung_stimmt_an_der_mini_zelle(mini):
    """Das Orakel selbst an der Handrechnung prüfen: bei 0,25 / 1,0 wählt es k = 3 mit Labels 40 / 100."""
    assert _zweite_implementierung(mini, 0.25, 1.0) == (3, 0.4)
    assert _zweite_implementierung(mini, 1.5, 2.0) == (1, 0.2)


@pytest.mark.skipif(not (VORMESSUNG / "hand_16.py").exists(), reason="Ordner der Vormessung liegt nicht neben der Demo")
@pytest.mark.parametrize("tm, tx", SCHWELLEN)
def test_hand_16_der_vormessung_waehlt_in_den_acht_zellen_dasselbe(zellen, tm, tx):
    quelltext = (VORMESSUNG / "hand_16.py").read_text(encoding="utf-8")
    quelltext = quelltext.replace("TAU_MITTEL = 0.25", f"TAU_MITTEL = {tm}").replace("TAU_MAX = 1.0", f"TAU_MAX = {tx}")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    lauf = subprocess.run([sys.executable, "-c", quelltext], cwd=VORMESSUNG, env=env, capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert lauf.returncode == 0, lauf.stderr
    gelesen = {}
    for zeile in lauf.stdout.splitlines():
        m = re.match(r"(cluster|zufall)\s+(\d+)\s+(\d+) \|.*\| (\d+) \| ([0-9.]+)$", zeile)
        if m:
            typ = {"cluster": "gruppiert", "zufall": "zufällig"}[m.group(1)]
            gelesen[(typ, int(m.group(2)), int(m.group(3)))] = (int(m.group(4)), float(m.group(5)))
    assert len(gelesen) == 8
    for z in zellen:
        schluessel = (z["typ"], z["n"], z["breite"])
        if schluessel not in gelesen:
            continue          # die drei Zellen mit 30 Kunden hat hand_16.py nicht
        w = A.waehle_k(z, tm, tx)
        k, verh = gelesen[schluessel]
        assert w.k == k, (schluessel, tm, tx)
        assert round(w.labels_verhaeltnis, 2) == verh, (schluessel, tm, tx)


def test_die_datei_k_zellen_hat_keine_doppelten_zeilen(zellen):
    for z in zellen:
        schluessel = [(r["seed"], r["k"]) for r in z["zeilen"]]
        assert len(schluessel) == len(set(schluessel)), z["id"]


def test_jede_zelle_der_datei_hat_ihren_bezug_und_alle_ks(zellen):
    for z in zellen:
        assert z["bezug"] in z["ks"] and max(z["ks"]) == z["bezug"]
        assert {r["k"] for r in z["zeilen"]} == set(z["ks"]), z["id"]
        assert all(r["schranke"] > 0 and r["labels"] > 0 for r in z["zeilen"])
    assert json.loads((ROOT / "data" / C.DATA_K_ZELLEN).read_text(encoding="utf-8"))["zellen"] == zellen
