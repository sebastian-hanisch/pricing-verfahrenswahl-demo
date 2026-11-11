"""Verdikte (reine Funktionen in pvw_evaluation.py) an handgesetzten Werten: Schwellen und jede Zahl im Text."""

import re

import pytest

import pvw_algorithm as A
import pvw_baum as B
import pvw_constants as C
import pvw_daten as D
import pvw_evaluation as E


def _stufen(*stati) -> list:
    return [B.Stufe(f"s{i}", f"Stufe {i}", s, "text") for i, s in enumerate(stati)]


def test_verdikt_nennt_das_andere_k_der_beschleuniger_wie_die_hinweise_der_stufen():
    import test_baum as TB
    stufen = B.baum(TB.preset_aufgabe("Standardaufgabe: 30 Kunden, weite Fenster"))       # die Regel wählt k = 4; gemessen sind die Beschleuniger mit k = 5 oder 8
    assert any("nicht eigens gemessen" in h for s in stufen for h in s.hinweise)
    assert "nicht bei dem k, das die Auswahlregel für diese Aufgabe nennt" in E.verdict_baum(stufen)[1]
    gleich = B.baum(TB.aufgabe(n=100, breite=20))                                         # nur k und Elementar: keine Beschleuniger empfohlen
    assert "nicht bei dem k" not in E.verdict_baum(gleich)[1]


def test_verdikt_baum_zaehlt_jeden_status():
    art, text = E.verdict_baum(_stufen("grundlage", "empfohlen", "moeglich", "nicht_empfohlen", "nicht_noetig", "nicht_anwendbar", "befund", "befund"))
    assert art == "success"
    assert text == "8 Stufen, davon: Grundlage 1; empfohlen oder möglich 2; nicht empfohlen (mit Messzahl) 1; nicht nötig oder nicht anwendbar 2; nicht gemessen 0; Befund 2."


@pytest.mark.parametrize("anzahl_nicht_gemessen, art", [(0, "success"), (1, "info"), (3, "info"), (4, "warning"), (8, "warning")])
def test_verdikt_baum_art_an_der_schwelle_der_haelfte(anzahl_nicht_gemessen, art):
    """Bei 8 Stufen ist die Schwelle 4 (die Hälfte): ab 4 nicht gemessenen Stufen warnt die App."""
    stati = ["nicht_gemessen"] * anzahl_nicht_gemessen + ["befund"] * (8 - anzahl_nicht_gemessen)
    assert E.verdict_baum(_stufen(*stati))[0] == art


def test_verdikt_baum_warnung_nennt_die_regel_ohne_messung():
    art, text = E.verdict_baum(_stufen(*["nicht_gemessen"] * 6))
    assert art == "warning" and text.startswith("Für diese Aufgabe fehlen Messungen: 6 Stufen, davon:") and "wird nicht empfohlen" in text and "nicht gemessen 6;" in text


def test_verdikt_k_bei_den_voreinstellungen_zaehlt_die_zellen():
    art, text = E.verdict_k(0.25, 1.0)
    assert art == "info"
    assert "Bei 0,25 % im Mittel und 1,00 % im Einzelfall wählt die Regel in den 11 Zellen: k = 1 in 3, k = 3 in 4, k = 4 in 1, k = 5 in 3" in text
    assert "In 2 Zellen liegt die Schranke für jedes k gleich hoch" in text and "in keiner Zelle bleibt nur der Bezug selbst übrig" in text


def test_verdikt_k_zaehlt_die_summe_der_zellen_immer_auf_11():
    for tm in C.TAU_MITTEL_WERTE:
        for tx in C.TAU_MAX_WERTE:
            _, text = E.verdict_k(tm, tx)
            zahlen = [int(x) for x in re.findall(r"k = \d+ in (\d+)", text)]
            assert sum(zahlen) == 11, (tm, tx)


def test_verdikt_k_warnt_wenn_nur_der_bezug_uebrig_bleibt(monkeypatch):
    mini = {"id": "m", "typ": "zufällig", "n": 50, "breite": 40, "bezug": 16, "ks": [1, 16], "quelle": {}, "zeilen": [
        {"seed": 0, "k": 1, "schranke": 90.0, "labels": 1}, {"seed": 0, "k": 16, "schranke": 100.0, "labels": 2}]}
    monkeypatch.setattr(D, "k_zellen", lambda: [mini])
    art, text = E.verdict_k(0.25, 1.0)
    assert art == "warning" and "in 1 Zellen erfüllt kein kleineres k als der Bezug die Schwellen" in text and "k = 16 in 1" in text
    assert A.waehle_k(mini, 0.25, 1.0).kein_kleineres_k


def test_verdikt_kosten_zaehlt_weniger_und_mehr_labels():
    zeilen = [{"Baustein": "a", "Labels im Verhältnis": 0.5, "Verhältnis zu": "x"}, {"Baustein": "b", "Labels im Verhältnis": 1.0, "Verhältnis zu": "x"},
              {"Baustein": "c", "Labels im Verhältnis": 2.0, "Verhältnis zu": "x"}, {"Baustein": "d", "Labels im Verhältnis": None, "Verhältnis zu": ""}]
    art, text = E.verdict_kosten(zeilen)
    assert art == "info" and text.startswith("In 1 von 3 Zeilen mit Verhältnis erzeugt der Baustein weniger Labels als seine Vergleichsvariante, in 1 mehr.")


def test_verdikt_kosten_an_den_echten_zeilen():
    z = E.bausteine_tabelle()
    assert len(z) == 13
    _, text = E.verdict_kosten(z)
    assert text.startswith("In 3 von 6 Zeilen mit Verhältnis erzeugt der Baustein weniger Labels als seine Vergleichsvariante, in 3 mehr.")
    weniger = {r["Baustein"] for r in z if r["Labels im Verhältnis"] is not None and r["Labels im Verhältnis"] < 1}
    assert weniger == {"Bidirektional (Halbweg H/2)", "Kantenstreichung", "Heuristisches Pricing (Limit 5 / 10 / 20)"}


def test_zusammenfassung_hat_eine_zeile_je_stufe_mit_nummer_und_status():
    z = E.zusammenfassung(_stufen("grundlage", "empfohlen"))
    assert [r["Nr."] for r in z] == [1, 2] and z[1]["Status"] == B.STATUS["empfohlen"] and z[0]["Stufe"] == "Stufe 0"


def test_k_uebersicht_hat_elf_zeilen_und_den_hinweis_jedes_k_gleich_zweimal():
    u = E.k_uebersicht(0.25, 1.0)
    assert len(u) == 11 and sum(1 for r in u if r["Hinweis"] == "jedes k gleich") == 2
    assert {r["Bezug"] for r in u} == {"k = 16", "k = 8", "elementar"}


def test_k_detail_nennt_elementar_statt_der_kundenzahl():
    d = E.k_detail(D.k_zelle(30, 40, "zufällig"))
    assert [r["k"] for r in d] == [1, 3, 5, 8, 12, "elementar"] and d[-1]["Lücke Mittel (%)"] == 0
