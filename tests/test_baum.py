"""Entscheidungsbaum: je Schnellstart-Szenario die erwartete Status-Zeile (Verdikt-Texte sind Behauptungen), Zahlen im Text gegen die Daten, und die Eigenschaften
„jede Empfehlung hat Quelle und Voraussetzung“ sowie „ein Baustein ohne Messung wird nicht empfohlen“ über das ganze Raster der Regler."""

import itertools
import re

import pytest

import pvw_baum as B
import pvw_constants as C
import pvw_daten as D
from pvw_daten import de


def aufgabe(**kw) -> B.Aufgabe:
    basis = dict(n=30, breite=100, typ="zufällig", r=1, obere_schranke=False, pricing_dominiert=True, tau_mittel=0.25, tau_max=1.0)
    basis.update(kw)
    return B.Aufgabe(**basis)


def stati(a) -> dict:
    return {s.kennung: s.status for s in B.baum(a)}


def stufe(a, kennung) -> B.Stufe:
    return next(s for s in B.baum(a) if s.kennung == kennung)


def preset_aufgabe(name) -> B.Aufgabe:
    p = C.PRESETS[name]
    return B.Aufgabe(p["a_n"], p["a_breite"], p["a_typ"], p["a_r"], p["a_ub"], p["a_pricing"], p["a_tau_mittel"], p["a_tau_max"])


NG = "nicht_gemessen"
ERWARTET = {
    "Standardaufgabe: 30 Kunden, weite Fenster": dict(
        grundbausteine="grundlage", groesse="befund", elementar="nicht_empfohlen", k="empfohlen", grenzen="nicht_noetig", bidirektional="moeglich", kanten="nicht_anwendbar",
        heuristik="moeglich", eimer="moeglich", kzyklen="nicht_empfohlen", dssr="nicht_empfohlen", glaettung="nicht_empfohlen", gelernt="nicht_empfohlen", master="befund"),
    "Enge Fenster, 100 Kunden": dict(
        grundbausteine="grundlage", groesse=NG, elementar="nicht_empfohlen", k="empfohlen", grenzen="nicht_noetig", bidirektional=NG, kanten="nicht_anwendbar",
        heuristik=NG, eimer=NG, kzyklen=NG, dssr=NG, glaettung=NG, gelernt=NG, master="befund"),
    "50 Kunden, weite Fenster, vier Grenzen": dict(
        grundbausteine="grundlage", groesse=NG, elementar="nicht_empfohlen", k="empfohlen", grenzen=NG, bidirektional=NG, kanten="nicht_anwendbar",
        heuristik=NG, eimer=NG, kzyklen=NG, dssr=NG, glaettung=NG, gelernt=NG, master="befund"),
    "Obere Schranke bekannt, enge Fenster": dict(
        grundbausteine="grundlage", groesse="befund", elementar="moeglich", k="empfohlen", grenzen="nicht_noetig", bidirektional="moeglich", kanten="moeglich",
        heuristik=NG, eimer="moeglich", kzyklen=NG, dssr=NG, glaettung=NG, gelernt=NG, master="befund"),
    "Kleine Aufgabe, 15 Kunden": dict(
        grundbausteine="grundlage", groesse=NG, elementar="moeglich", k=NG, grenzen="nicht_noetig", bidirektional=NG, kanten="nicht_anwendbar",
        heuristik=NG, eimer=NG, kzyklen=NG, dssr=NG, glaettung=NG, gelernt=NG, master="befund"),
    "Aufgabe ohne passende Messung": dict(
        grundbausteine="grundlage", groesse=NG, elementar=NG, k=NG, grenzen=NG, bidirektional=NG, kanten=NG,
        heuristik=NG, eimer=NG, kzyklen=NG, dssr=NG, glaettung=NG, gelernt=NG, master="befund"),
}
ERWARTET_K = {"Standardaufgabe: 30 Kunden, weite Fenster": 4, "Enge Fenster, 100 Kunden": 1, "50 Kunden, weite Fenster, vier Grenzen": 5, "Obere Schranke bekannt, enge Fenster": 1}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_jedes_preset_hat_die_erwartete_status_zeile(name):
    assert stati(preset_aufgabe(name)) == ERWARTET[name]


@pytest.mark.parametrize("name, k", list(ERWARTET_K.items()))
def test_jedes_preset_nennt_das_erwartete_k(name, k):
    assert B.wahl_k(preset_aufgabe(name))[1].k == k
    assert stufe(preset_aufgabe(name), "k").empfehlung == f"ng-Gedächtnis k = {k}."


def test_die_stufen_haben_feste_reihenfolge_und_eindeutige_kennungen():
    kennungen = [s.kennung for s in B.baum(aufgabe())]
    assert kennungen == ["grundbausteine", "groesse", "elementar", "k", "grenzen", "bidirektional", "kanten", "heuristik", "eimer", "kzyklen", "dssr", "glaettung", "gelernt", "master"]


# ---- Handbeispiele: die drei Beispielaufgaben des Plans, Zahlen als Rechnung aus den Daten -----------------------------------------------------

def test_aufgabe_30_kunden_breite_100_nennt_die_zahlen_der_messzeilen():
    a = aufgabe()
    bidi = stufe(a, "bidirektional")
    assert f"{de(D.w('bdl_v9', 'zufaellig_b100_median'), 2)}-Fache" in bidi.belege[0].aussage          # 0,25
    assert f"{de(D.w('bdl_v9', 'paare_je_label_median'))}-Fache" in bidi.belege[1].aussage            # 9,8
    heur = stufe(a, "heuristik")
    assert "0,52 / 0,60 / 0,71" in heur.belege[0].aussage
    assert "+36 / +23 / +10" in heur.belege[1].aussage
    assert "0,36 / 0,39 / 0,46" in heur.belege[2].aussage and "96,2 %" in heur.belege[2].aussage
    assert "elementare Rechnung in 4 von 6" in stufe(a, "elementar").empfehlung


def test_aufgabe_100_kunden_breite_20_waehlt_k_1_weil_alle_k_gleich_sind():
    s = stufe(aufgabe(n=100, breite=20), "k")
    assert s.empfehlung == "ng-Gedächtnis k = 1."
    assert "für jedes gemessene k in jeder Instanz gleich hoch" in " ".join(s.hinweise)
    assert "Bezug ist k = 16" in s.hinweise[0]
    assert stufe(aufgabe(n=100, breite=20), "bidirektional").status == "nicht_gemessen"       # Beschleuniger nur bei 30 Kunden gemessen


def test_aufgabe_50_kunden_breite_100_mit_vier_grenzen_waehlt_k_5_und_nennt_die_grenzen_nicht_gemessen():
    a = aufgabe(n=50, breite=100, typ="gruppiert", r=4)
    assert stufe(a, "k").empfehlung == "ng-Gedächtnis k = 5."
    g = stufe(a, "grenzen")
    assert g.status == "nicht_gemessen" and g.belege == ()
    assert "Gemessen ist: 30 Kunden, Fensterbreite 100, zufällig" in g.empfehlung


def test_mehrere_grenzen_nennen_die_zahlen_der_zeile_mgr_v11():
    a = aufgabe(r=4)
    s = stufe(a, "grenzen")
    assert s.status == "befund"
    assert "von 91,0 % (nur Zeit) auf 81,0 %" in s.empfehlung and "von 2,8 auf 17,9" in s.empfehlung


def test_kantenstreichung_braucht_eine_obere_schranke():
    ohne = stufe(aufgabe(breite=40, obere_schranke=False), "kanten")
    mit = stufe(aufgabe(breite=40, obere_schranke=True), "kanten")
    assert ohne.status == "nicht_anwendbar" and ohne.belege == ()
    assert mit.status == "moeglich" and len(mit.belege) == 2
    assert "nur bei den Dualpreisen der Konvergenz" in " ".join(mit.hinweise)
    assert f"{de(D.w('ksp_n30', 'zufall_b40_exakt_gestrichen_mittel'), 0)} %" in mit.belege[0].aussage


def test_heuristisches_pricing_braucht_ein_dominierendes_pricing_fuer_den_zeitgewinn():
    ohne = stufe(aufgabe(pricing_dominiert=False), "heuristik")
    assert ohne.status == "nicht_gemessen" and ohne.belege == () and "96,2 %" in ohne.empfehlung
    b150 = stufe(aufgabe(breite=150), "heuristik")
    assert b150.status == "moeglich" and "nicht gemessen" in b150.empfehlung and "0,43 / 0,49 / 0,63" in b150.empfehlung


def test_elementar_je_breite_bei_30_kunden_nennt_die_abbrueche_der_neurechnung_und_der_fruehen_messung():
    b40, b100, b200 = (stufe(aufgabe(breite=b), "elementar") for b in (40, 100, 200))
    assert (b40.status, b100.status, b200.status) == ("moeglich", "nicht_empfohlen", "nicht_empfohlen")
    assert "0 von 6 abgebrochen" in b40.belege[0].aussage and "in der früheren Messung 0 von 6" in b40.belege[0].aussage
    assert "4 von 6 abgebrochen" in b100.belege[0].aussage and "früheren Messung 3 von 6" in b100.belege[0].aussage
    assert "6 von 6 abgebrochen" in b200.belege[0].aussage


def test_die_nicht_empfohlenen_nennen_ihre_messzahlen():
    a = aufgabe()
    assert "1,69-Fache" in stufe(a, "kzyklen").empfehlung and "0,469 %" in stufe(a, "kzyklen").empfehlung and "9 von 24" in stufe(a, "kzyklen").belege[0].aussage
    d = stufe(a, "dssr")
    assert "6,3-Fache" in d.empfehlung and "11,6-Fache" in d.empfehlung and "24 von 72" in d.belege[0].aussage and "0 von 24" in d.belege[0].aussage
    g = stufe(a, "glaettung")
    assert "20,5 Runden" in g.empfehlung and "34,2" in g.empfehlung and "6 bzw. 6 von 6" in g.belege[0].aussage
    l = stufe(a, "gelernt")
    assert "91,9 / 92,4 %" in l.empfehlung and "91,4 %" in l.empfehlung and "26,8 %" in l.belege[0].aussage and "4 von 30" in l.belege[0].aussage


def test_die_master_stufe_nennt_die_zahlen_von_crew_pairing():
    s = stufe(aufgabe(), "master")
    assert "5,2 / 4,1 / 3,4 %" in s.empfehlung
    assert "15,5 / 12,7 / 8,2 %" in s.belege[0].aussage and "64 / 73 / 76 %" in s.belege[0].aussage


def test_ein_anderes_k_als_gemessen_wird_im_hinweis_genannt():
    """Bei 30 Kunden, Breite 100, zufällig wählt die Regel k = 4; bidirektional ist mit k = 5 und 8 gemessen, die Eimer mit k = 5, Kantenstreichung und Etikettenlimit mit k = 8."""
    a = aufgabe(breite=100, obere_schranke=True)
    assert "bei dem gewählten k = 4 ist die Wirkung nicht eigens gemessen" in " ".join(stufe(a, "bidirektional").hinweise)
    assert "Gemessen mit ng-Gedächtnis k = 5" in " ".join(stufe(a, "eimer").hinweise)
    assert "Gemessen mit ng-Gedächtnis k = 8" in " ".join(stufe(a, "kanten").hinweise)
    a5 = aufgabe(breite=100, typ="gruppiert")                           # hier wählt die Regel k = 5
    assert "(gewählt: k = 5)" in " ".join(stufe(a5, "bidirektional").hinweise)


# ---- Eigenschaften über das ganze Raster -------------------------------------------------------------------------------------------------------

RASTER = list(itertools.product(C.N_WERTE, C.BREITE_WERTE, C.TYP_WERTE, C.GRENZEN_WERTE, (False, True), (True, False)))
MESSZEILE = {"groesse": "zfl_pricing", "grenzen": "mgr_v11", "bidirektional": "bdl_v9", "kanten": "ksp_n30", "eimer": "eml_v10", "kzyklen": "ngr_kzyklen", "dssr": "ngr_dssr",
             "glaettung": "pdp_glaettung", "gelernt": "v15_gelernt"}


def test_das_raster_hat_1120_aufgaben():
    assert len(RASTER) == 7 * 5 * 2 * 4 * 2 * 2 == 1120


def test_jede_stufe_jeder_aufgabe_hat_status_text_und_stimmige_belege():
    for n, breite, typ, r, ub, pd_ in RASTER:
        for s in B.baum(aufgabe(n=n, breite=breite, typ=typ, r=r, obere_schranke=ub, pricing_dominiert=pd_)):
            assert s.status in B.STATUS and s.empfehlung.strip()
            if s.status in ("empfohlen", "moeglich", "nicht_empfohlen"):
                assert s.belege, (s.kennung, n, breite, typ)                  # kein leerer Beleg
            if s.status == "nicht_gemessen":
                assert s.belege == (), (s.kennung, n, breite, typ)             # keine Zahl, wo nichts gemessen ist
            for beleg in s.belege:
                assert beleg.aussage.strip() and beleg.voraussetzung.strip() and beleg.quelle.strip()
                assert re.search(r"\d", beleg.aussage)                         # die Aussage nennt eine Messzahl


def test_ein_baustein_ohne_messung_wird_nicht_empfohlen():
    """Empfohlen, möglich oder nicht empfohlen (also mit Zahl) steht nur, wo die Aufgabe im gemessenen Bereich der Messzeile des Bausteins liegt."""
    for n, breite, typ, r, ub, pd_ in RASTER:
        a = aufgabe(n=n, breite=breite, typ=typ, r=r, obere_schranke=ub, pricing_dominiert=pd_)
        stufen = {s.kennung: s for s in B.baum(a)}
        for kennung, zid in MESSZEILE.items():
            if kennung == "grenzen" and r == 1:
                continue                                                       # eine Grenze: nichts zu messen, „nicht nötig“
            if stufen[kennung].status in ("empfohlen", "moeglich", "nicht_empfohlen", "befund"):
                assert D.im_bereich(D.zeile(zid), n, breite, typ), (kennung, n, breite, typ)
        if stufen["k"].status == "empfohlen":
            assert D.k_zelle(n, breite, typ) is not None
        if stufen["heuristik"].status in ("empfohlen", "moeglich"):
            assert pd_ and breite in (100, 150) and n == 30


def test_ohne_obere_schranke_wird_die_kantenstreichung_nicht_empfohlen_und_ohne_dominierendes_pricing_nicht_das_heuristische_pricing():
    for n, breite, typ, r, ub, pd_ in RASTER:
        s = {x.kennung: x.status for x in B.baum(aufgabe(n=n, breite=breite, typ=typ, r=r, obere_schranke=ub, pricing_dominiert=pd_))}
        if not ub:
            assert s["kanten"] == "nicht_anwendbar"
        if not pd_:
            assert s["heuristik"] in ("nicht_gemessen",)


def test_die_empfohlene_reihenfolge_ist_eine_teilfolge_der_stufen():
    stufen = B.baum(aufgabe(obere_schranke=True, breite=40))
    emp = B.empfohlene_reihenfolge(stufen)
    assert [s.kennung for s in emp] == [s.kennung for s in stufen if s.status in B.EMPFOHLEN]
    assert [s.kennung for s in emp] == ["elementar", "k", "bidirektional", "kanten", "eimer"]


def test_status_schluessel_haben_beschriftung():
    assert set(B.EMPFOHLEN) <= set(B.STATUS) and len(set(B.STATUS.values())) == len(B.STATUS)


# ---- Aussagen nach der unabhängigen Prüfung ------------------------------------------------------------------------------------------------------

def test_nur_das_gedaechtnis_k_heisst_empfohlen_die_beschleuniger_heissen_moeglich():
    """Die Messung der Beschleuniger stützt nur einen Teil der Frage (Gesamtaufwand, späte Aufrufe, Zeit, Zähleinheit): Sie werden nie „empfohlen“."""
    for n, breite, typ, r, ub, pd_ in RASTER:
        for s in B.baum(aufgabe(n=n, breite=breite, typ=typ, r=r, obere_schranke=ub, pricing_dominiert=pd_)):
            if s.kennung in ("bidirektional", "kanten", "heuristik", "eimer"):
                assert s.status != "empfohlen", (s.kennung, n, breite, typ)


def test_bidirektional_nennt_den_preis_in_der_kopfzeile_und_den_nicht_gemessenen_gesamtaufwand():
    s = stufe(aufgabe(), "bidirektional")
    assert s.empfehlung.startswith("Gemessen: fester Halbweg H/2") and "9,8-Fache dieser Label-Zahl an Verbindungspaaren" in s.empfehlung and "Gesamtaufwand ist nicht gemessen" in s.empfehlung
    hin = " ".join(s.hinweise)
    assert "dynD" in hin and "nicht das Verfahren von Tilk u. a." in hin and "nicht verwenden" not in hin
    assert "Gesamtaufwandsmaß" in hin


def test_kantenstreichung_nennt_schranke_aus_spalten_und_nicht_gemessene_kosten_und_nutzen():
    s = stufe(aufgabe(breite=40, obere_schranke=True), "kanten")
    assert "ganzzahligen Optimum als oberer Schranke" in s.empfehlung and "Schranke nur aus den Spalten" in s.empfehlung and "nicht gemessen" in s.empfehlung
    assert "Rückwärtslabels" in " ".join(s.hinweise)


def test_heuristisches_pricing_nennt_die_cpu_zeit_mit_voraussetzung_und_nicht_die_aussage_schneller():
    s = stufe(aufgabe(), "heuristik")
    assert s.status == "moeglich" and "schneller" not in s.empfehlung
    assert "Rechner ausgelastet, nur Größenordnung" in s.empfehlung and "etwa 380 Labels" in s.empfehlung and "Mittel der Instanz-Verhältnisse" in s.empfehlung
    assert "„heuristisches Pricing ist schneller“ dort nicht steht" in " ".join(s.hinweise)


def test_eimer_vergleichen_keine_einheiten_und_nennen_den_aufwand():
    s = stufe(aufgabe(), "eimer")
    assert "kleinsten Gewinn" not in s.empfehlung and "des Aufwands" in s.empfehlung and "Dominanzvergleiche plus 0,1 je Eimerschritt" in s.empfehlung


def test_gelernte_dominanz_ist_nur_bei_breite_100_gemessen():
    for breite in (20, 40, 150, 200):
        assert stufe(aufgabe(breite=breite), "gelernt").status == "nicht_gemessen", breite
    s = stufe(aufgabe(breite=100, typ="gruppiert"), "gelernt")
    assert s.status == "nicht_empfohlen" and "in 30 Testaufrufen verloren ging" in s.belege[0].aussage
    assert "Breite 100 und ng k = 8" in " ".join(s.hinweise)


def test_dssr_und_glaettung_sind_auf_das_gemessene_eingeschraenkt():
    a = aufgabe()
    d = stufe(a, "dssr")
    assert "im Mittel der Verhältnisse" in d.empfehlung and "nur in den ersten Runden" not in d.empfehlung and "schwacher Test" in d.empfehlung
    g = stufe(a, "glaettung")
    assert "spart bei α = 0,8 und 0,9 keine Runden" in g.empfehlung and "bei α = 0,5 sind es etwa gleich viele (19,8)" in g.empfehlung


def test_k_beleg_bildet_den_bezug_im_genitiv_und_der_hinweis_endet_mit_punkt():
    s = stufe(aufgabe(breite=40), "k")                     # Bezug: elementar
    text = s.belege[0].aussage
    assert "unter der Schranke der elementaren Rechnung" in text and "der Labels der elementaren Rechnung" in text and "von die" not in text
    assert s.hinweise[0] == "Bezug ist die elementare Schranke."
    s100 = stufe(aufgabe(), "k")                           # Bezug: k = 8
    assert "unter der Schranke von k = 8" in s100.belege[0].aussage and "der Labels von k = 8" in s100.belege[0].aussage
    assert "hängt an den Schwellen 0,25 % und 1,00 %" in " ".join(s100.hinweise)


def test_kopfzeile_der_elementaren_rechnung_bei_50_und_100_kunden_nennt_beide_kundenzahlen():
    s = stufe(aufgabe(n=100, breite=40), "elementar")
    assert s.empfehlung.startswith("Bei 50 und 100 Kunden brach die elementare Rechnung in 94 von 96 gemessenen Läufen ab")


def test_abhaengige_verbraeuche_sind_mit_zahlen_der_quell_demo_genannt():
    hin = " ".join(stufe(aufgabe(r=2), "grenzen").hinweise)
    assert "nicht gemessen" in hin                          # Kapazitätsgrenze: bei anderer Zahl von Grenzen nicht gemessen
    assert "Fahrerzeit gleich Last 84,4 % bei 2 bis 4 Grenzen" in hin and "83,3" in hin and "74,5" in hin and "88,8" in hin
    assert "wäre kein solches Sinken zu erwarten" not in hin
