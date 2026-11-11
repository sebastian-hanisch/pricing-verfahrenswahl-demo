"""Randfälle: alle k gleich (Breite 20), kein kleineres k erfüllt die Schwellen (dann der Bezug und ein Hinweis), eine Instanz, fehlende Läufe, Aufgabe ohne zusätzliche Grenze, strengste und lockerste Schwellen."""

import pytest

import pvw_algorithm as A
import pvw_baum as B
import pvw_constants as C
import pvw_daten as D
import test_baum as TB


def test_alle_k_gleich_gilt_genau_in_den_zwei_zellen_mit_100_kunden_und_breite_20(zellen):
    gleich = sorted((z["typ"], z["n"], z["breite"]) for z in zellen if A.alle_gleich(z))
    assert gleich == [("gruppiert", 100, 20), ("zufällig", 100, 20)]


def test_breite_20_bei_100_kunden_waehlt_bei_jeder_schwelle_k_1(zellen):
    for tm in C.TAU_MITTEL_WERTE:
        for tx in C.TAU_MAX_WERTE:
            for typ in C.TYP_WERTE:
                zelle = D.k_zelle(100, 20, typ)
                w = A.waehle_k(zelle, tm, tx)
                assert w.k == 1 and not w.kein_kleineres_k and w.luecke_mittel == 0 == w.luecke_max


def test_kein_kleineres_k_erfuellt_die_schwellen_dann_ist_es_der_bezug_mit_hinweis(mini, monkeypatch):
    monkeypatch.setattr(D, "k_zelle", lambda n, breite, typ: mini)
    a = TB.aufgabe(n=50, breite=40, tau_mittel=0.2, tau_max=1.0)           # k = 3 liegt mit 0,25 über 0,2
    s = TB.stufe(a, "k")
    assert s.status == "empfohlen" and s.empfehlung == "ng-Gedächtnis k = 16."
    assert any("Kein kleineres k erfüllt beide Schwellen" in h for h in s.hinweise)


def test_eine_einzige_instanz(mini):
    eine = dict(mini, zeilen=[z for z in mini["zeilen"] if z["seed"] == 0])
    w = A.waehle_k(eine, 0.25, 1.0)
    assert (w.k, w.instanzen, w.luecke_mittel, w.luecke_max) == (3, 1, 0.25, 0.25)


def test_ein_k_ohne_fertige_laeufe_faellt_aus_der_tabelle_und_wird_nie_gewaehlt(mini):
    ohne_k3 = dict(mini, zeilen=[z for z in mini["zeilen"] if z["k"] != 3])
    assert [t.k for t in A.tabelle(ohne_k3)] == [1, 16]
    assert A.waehle_k(ohne_k3, 0.25, 1.0).k == 16


def test_nur_der_bezug_in_der_zelle(mini):
    nur = dict(mini, ks=[16], zeilen=[z for z in mini["zeilen"] if z["k"] == 16])
    w = A.waehle_k(nur, 0.05, 0.25)
    assert w.k == 16 and w.kein_kleineres_k and w.labels_verhaeltnis == 1.0


def test_gleichstand_der_schranke_gilt_als_erfuellt_und_zaehlt_nicht_als_lücke(mini):
    gleich = dict(mini, zeilen=[dict(z, schranke=100.0 if z["seed"] == 0 else z["schranke"]) for z in mini["zeilen"] if z["k"] != 1])
    assert A.luecken(gleich, 3)[0] == 0.0


def test_aufgabe_ohne_zusaetzliche_grenze_hat_keinen_mehraufwand_und_keine_belege():
    s = TB.stufe(TB.aufgabe(r=1), "grenzen")
    assert s.status == "nicht_noetig" and s.belege == ()


def test_strengste_schwellen_waehlen_nie_ein_kleineres_k_als_die_lockersten(zellen):
    for z in zellen:
        streng = A.waehle_k(z, min(C.TAU_MITTEL_WERTE), min(C.TAU_MAX_WERTE))
        locker = A.waehle_k(z, max(C.TAU_MITTEL_WERTE), max(C.TAU_MAX_WERTE))
        assert streng.k >= locker.k, z["id"]


def test_die_zelle_30_kunden_breite_40_liegt_knapp_unter_der_voreinstellung(zellen):
    """Bekanntes Problem aus der App: mittlere Lücke 0,24 % bei k = 1 gegen die Schwelle 0,25 %; bei 0,1 % wählt die Regel dort ein größeres k."""
    z = D.k_zelle(30, 40, "zufällig")
    t = {x.k: x for x in A.tabelle(z)}
    assert 0.24 <= t[1].luecke_mittel < 0.25
    assert A.waehle_k(z, 0.25, 1.0).k == 1 and A.waehle_k(z, 0.1, 1.0).k > 1


def test_kein_regler_wert_laesst_den_baum_abstuerzen_und_jede_stufe_hat_text():
    for tm in C.TAU_MITTEL_WERTE:
        for tx in C.TAU_MAX_WERTE:
            for n in (30, 50, 100):
                for s in B.baum(TB.aufgabe(n=n, tau_mittel=tm, tau_max=tx)):
                    assert s.empfehlung
