"""Jede Zahl im Baum zeigt auf eine Zeile in `data/` mit Quelle, und dieser Test liest die Quellzeile noch einmal aus der Datei der jeweiligen Demo (wenn der Ordner neben dieser Demo liegt) und vergleicht.

Drei Prüfungen je Zeile von `data/messwerte.json`:
1. Die Kopie gleicht dem, was die Auswertung der Quelldatei jetzt ergibt (`tools/pvw_quellen.py`).
2. Die Zahl steht im Wortlaut der README der Quell-Demo (bzw. der Ergebnisdatei der Vormessung): ein zweiter, von der Auswertung unabhängiger Beleg.
3. Die Zeile nennt Quelle, Voraussetzung und Bereich (kein leerer Beleg).
Fehlt der Ordner der Quelle, wird die Prüfung übersprungen (nie geraten)."""

import json

import pytest

import messwerte_bauen as MB
import pvw_constants as C
import pvw_daten as D
import pvw_quellen as Q

ZEILEN = {z["id"]: z for z in MB.ZEILEN}


def _quelle_da(z) -> bool:
    return Q.verfuegbar(z["quelle"]["demo"]) and Q.verfuegbar(z.get("readme_demo", z["quelle"]["demo"]))


def _gespeichert(zid: str) -> dict:
    return D.zeile(zid)


# ---- 3. Form -------------------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("zid", list(ZEILEN))
def test_jede_zeile_nennt_quelle_voraussetzung_und_bereich(zid):
    z = _gespeichert(zid)
    assert z["quelle"]["demo"] and z["quelle"]["datei"] and z["quelle"]["stelle"]
    assert len(z["voraussetzung"]) > 40
    assert set(z["bereich"]) == {"n", "breite", "typ"}
    assert z["werte"], "keine Werte"


def test_die_datei_hat_genau_die_zeilen_der_baufassung():
    assert [z["id"] for z in D.messzeilen()] == list(ZEILEN)
    assert len({z["id"] for z in D.messzeilen()}) == len(D.messzeilen())


def test_der_bereich_liegt_in_den_reglerwerten():
    for z in D.messzeilen():
        b = z["bereich"]
        if b["n"]:
            assert set(b["n"]) <= set(C.N_WERTE) | {7}, z["id"]       # die Dominanz-Messung hat 7 Kunden und ist keine Reglerstufe
        if b["breite"]:
            assert set(b["breite"]) <= set(C.BREITE_WERTE) | {30, 80}, z["id"]
        if b["typ"]:
            assert set(b["typ"]) <= set(C.TYP_WERTE), z["id"]


# ---- 1. Neu aus der Quelldatei gelesen -------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("zid", [i for i, z in ZEILEN.items() if z["extraktor"]])
def test_kopie_gleicht_der_quelldatei(zid):
    z = ZEILEN[zid]
    if not Q.verfuegbar(z["quelle"]["demo"]):
        pytest.skip(f"Ordner {z['quelle']['demo']} liegt nicht neben der Demo")
    neu = MB.zeile_werte(z)
    alt = _gespeichert(zid)["werte"]
    assert set(neu) == set(alt)
    for k in neu:
        assert alt[k] == pytest.approx(neu[k], abs=1e-6, rel=1e-9), (zid, k)


def test_festeingetragene_werte_stehen_in_der_baufassung_und_in_der_datei_gleich():
    for zid, z in ZEILEN.items():
        if z["extraktor"] is None:
            assert _gespeichert(zid)["werte"] == z["werte"]


# ---- 2. Wortlaut der README der Quell-Demo --------------------------------------------------------------------------------------------------

def _fragmente():
    for zid, z in ZEILEN.items():
        for f in z["readme"]:
            yield pytest.param(zid, f, id=f"{zid}:{f[:40]}")


@pytest.mark.parametrize("zid, fragment", list(_fragmente()))
def test_die_zahl_steht_in_der_readme_der_quell_demo(zid, fragment):
    z = ZEILEN[zid]
    if not _quelle_da(z):
        pytest.skip("Quelle liegt nicht neben der Demo")
    demo, datei = z.get("readme_demo", z["quelle"]["demo"]), z.get("readme_datei", "README.md")
    assert Q.enthaelt(demo, datei, fragment), f"Fragment fehlt in {demo}/{datei}: {fragment}"


def test_zusatzbelege_der_gelernten_dominanz_stehen_in_der_vormessung():
    if not Q.verfuegbar("vormessung"):
        pytest.skip("Vormessung liegt nicht neben der Demo")
    for demo, datei, fragment in ZEILEN["v15_gelernt"]["zusatz"]:
        assert Q.enthaelt(demo, datei, fragment)
    w = _gespeichert("v15_gelernt")["werte"]
    assert w["gestrichen_gb"] == pytest.approx(100 - w["in_dominanzpruefung_gb"])        # 100 - 73,2


# ---- Zellen der Auswahlregel (k_zellen.json) ------------------------------------------------------------------------------------------------

def test_die_k_zellen_gleichen_den_rohdateien_der_vormessung():
    if not Q.verfuegbar("vormessung"):
        pytest.skip("Vormessung liegt nicht neben der Demo")
    assert D.k_zellen()[:8] == Q.lese_v8_zellen()


def test_die_k_zellen_mit_30_kunden_gleichen_den_dateien_von_ng_routen():
    if not Q.verfuegbar("ng-routen-demo"):
        pytest.skip("ng-routen-demo liegt nicht neben der Demo")
    assert D.k_zellen()[8:] == Q.lese_n30_zellen()


def test_v8_zellen_gleichen_der_kopie_in_ng_routen_demo():
    """Zweite Quelle für dieselben Zeilen: `ng-routen-demo/data/skalierung.json` (Schranke und Labels je Instanz und k)."""
    if not Q.verfuegbar("ng-routen-demo"):
        pytest.skip("ng-routen-demo liegt nicht neben der Demo")
    skal = {(z["typ"], z["n"], z["breite"], z["seed"], z["k"]): z for z in Q._json("ng-routen-demo", "data/skalierung.json")["zeilen"] if not z["abgebrochen"]}
    typ_name = {"zufällig": "zufall", "gruppiert": "cluster"}
    gesehen = 0
    for zelle in D.k_zellen()[:8]:
        for r in zelle["zeilen"]:
            q = skal[(typ_name[zelle["typ"]], zelle["n"], zelle["breite"], r["seed"], r["k"])]
            assert q["schranke"] == pytest.approx(r["schranke"], abs=1e-6) and q["labels"] == r["labels"]
            gesehen += 1
    assert gesehen == 8 * 12 * 6


def test_gepoolte_luecken_der_30_kunden_gleichen_der_readme_von_ng_routen():
    """Die beiden Zellen mit 30 Kunden und Breite 100 zusammen (24 Instanzen, Bezug ng k = 8) ergeben die Zahlen der Tabelle in der README von ng-routen-demo."""
    if not Q.verfuegbar("ng-routen-demo"):
        pytest.skip("ng-routen-demo liegt nicht neben der Demo")
    import pvw_algorithm as A
    zellen = [z for z in D.k_zellen() if z["n"] == 30 and z["breite"] == 100]
    assert len(zellen) == 2
    erwartet = {1: "3,563 (7,157)", 2: "0,920 (2,365)", 3: "0,460 (1,116)", 4: "0,199 (0,938)", 5: "0,115 (0,898)"}
    for k, text in erwartet.items():
        alle = [g for z in zellen for g in A.luecken(z, k)]
        assert len(alle) == 24
        gelesen = f"{sum(alle) / 24:.3f}".replace(".", ",") + f" ({max(alle):.3f})".replace(".", ",")
        assert gelesen == text, k
        assert Q.enthaelt("ng-routen-demo", "README.md", f"| ng k = {k} | 24 / 0 | {text} |")


def test_heuristisches_pricing_der_quell_demo_gleicht_den_rohdateien_der_vormessung():
    """Die Kennzahlen aus der Neurechnung (`heuristisches-pricing-demo/data/laeufe_v13.json`, Quelle der Zeilen) gleichen denen aus den Rohdateien `out_v13_*.txt` der Vormessung."""
    if not (Q.verfuegbar("heuristisches-pricing-demo") and Q.verfuegbar("vormessung")):
        pytest.skip("Quelle liegt nicht neben der Demo")
    neu, roh = Q.hpr_v13(), Q.hpr_v13_vormessung()
    assert set(neu) == set(roh)
    for k in neu:
        assert neu[k] == pytest.approx(roh[k], abs=1e-4), k


# ---- Bau ---------------------------------------------------------------------------------------------------------------------------------------

def test_die_gebauten_dateien_gleichen_dem_ergebnis_des_bauwerkzeugs():
    if not all(Q.verfuegbar(d) for d in ("vormessung", "ng-routen-demo", "heuristisches-pricing-demo")):
        pytest.skip("nicht alle Quellen liegen neben der Demo")
    messwerte, k_zellen = MB.bauen()
    assert json.loads((D.DATA / C.DATA_MESSWERTE).read_text(encoding="utf-8")) == json.loads(MB.dumps(messwerte))
    assert json.loads((D.DATA / C.DATA_K_ZELLEN).read_text(encoding="utf-8")) == json.loads(MB.dumps(k_zellen))
