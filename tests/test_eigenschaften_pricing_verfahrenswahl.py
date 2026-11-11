"""Eigenschaften der Auswahlregel und des Baums (über alle Zellen und alle Schwellenpaare): Monotonie, Bezug immer zulässig, Wahl liegt in den gemessenen k."""

import itertools

import pvw_algorithm as A
import pvw_baum as B
import pvw_constants as C
import pvw_daten as D
import test_baum as TB

PAARE = list(itertools.product(C.TAU_MITTEL_WERTE, C.TAU_MAX_WERTE))


def test_engere_schwellen_waehlen_nie_ein_kleineres_k(zellen):
    """Monotonie: Sind beide Schwellen nicht größer, ist das gewählte k nicht kleiner."""
    for z in zellen:
        for (tm1, tx1), (tm2, tx2) in itertools.product(PAARE, PAARE):
            if tm1 <= tm2 and tx1 <= tx2:
                assert A.waehle_k(z, tm1, tx1).k >= A.waehle_k(z, tm2, tx2).k, (z["id"], tm1, tx1, tm2, tx2)


def test_der_bezug_erfuellt_immer_beide_schwellen(zellen):
    for z in zellen:
        bezug = next(t for t in A.tabelle(z) if t.k == z["bezug"])
        assert (bezug.luecke_mittel, bezug.luecke_max) == (0.0, 0.0)
        assert all(A.erfuellt(bezug, tm, tx) for tm, tx in PAARE)


def test_das_gewaehlte_k_ist_das_kleinste_das_die_schwellen_erfuellt(zellen):
    for z in zellen:
        for tm, tx in PAARE:
            w = A.waehle_k(z, tm, tx)
            assert w.k in z["ks"] and w.luecke_mittel <= tm and w.luecke_max <= tx
            assert all(not A.erfuellt(t, tm, tx) for t in A.tabelle(z) if t.k < w.k)


def test_das_labels_verhaeltnis_liegt_zwischen_0_und_1(zellen):
    for z in zellen:
        for tm, tx in PAARE:
            w = A.waehle_k(z, tm, tx)
            assert 0 < w.labels_verhaeltnis <= 1.0 + 1e-12, (z["id"], w)


def test_luecken_sind_nie_negativ_ausser_im_rundungsrauschen(zellen):
    for z in zellen:
        for k in z["ks"]:
            assert min(A.luecken(z, k)) > -1e-9, (z["id"], k)


def test_die_mittlere_luecke_sinkt_mit_k_in_jeder_zelle(zellen):
    """Größeres k gibt im Mittel eine nicht tiefere Schranke (ng-Relaxationen sind geschachtelt); über alle benachbarten k jeder Zelle gezählt."""
    for z in zellen:
        mittel = [t.luecke_mittel for t in A.tabelle(z)]
        assert all(a >= b - 1e-9 for a, b in zip(mittel, mittel[1:])), z["id"]


def test_engere_schwellen_nennen_im_baum_nie_ein_kleineres_k():
    for z in D.k_zellen():
        kw = dict(n=z["n"], breite=z["breite"], typ=z["typ"])
        locker = B.wahl_k(TB.aufgabe(tau_mittel=max(C.TAU_MITTEL_WERTE), tau_max=max(C.TAU_MAX_WERTE), **kw))[1].k
        streng = B.wahl_k(TB.aufgabe(tau_mittel=min(C.TAU_MITTEL_WERTE), tau_max=min(C.TAU_MAX_WERTE), **kw))[1].k
        assert streng >= locker, z["id"]
