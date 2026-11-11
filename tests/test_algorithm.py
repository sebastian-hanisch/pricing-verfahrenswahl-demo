"""Auswahlregel für k: jede Einheit an der Mini-Zelle von Hand, die acht Zellen von V8 gegen die Handwerte des unabhängigen Skripts `hand_16.py` (Rohausgabe `run_hand_16.log`)."""

import pytest

import pvw_algorithm as A


# ---- Mini-Zelle (Handrechnung in conftest.py) ------------------------------------------------------------------------------------------

def test_luecken_je_instanz_von_hand(mini):
    assert A.luecken(mini, 1) == [100.0 * 2 / 100, 100.0 * 3 / 200, 100.0 * 4 / 400]       # 2,0 / 1,5 / 1,0
    assert A.luecken(mini, 3) == [100 * 0.25 / 100, 100 * 0.5 / 200, 100 * 1 / 400]       # dreimal 0,25
    assert A.luecken(mini, 16) == [0.0, 0.0, 0.0]


def test_labels_median_von_hand(mini):
    assert (A.labels_median(mini, 1), A.labels_median(mini, 3), A.labels_median(mini, 16)) == (20, 40, 100)


def test_tabelle_von_hand(mini):
    t = {z.k: z for z in A.tabelle(mini)}
    assert (t[1].luecke_mittel, t[1].luecke_max, t[1].labels_median, t[1].instanzen) == ((2.0 + 1.5 + 1.0) / 3, 2.0, 20, 3)
    assert (t[3].luecke_mittel, t[3].luecke_max, t[3].labels_median) == (0.25, 0.25, 40)
    assert (t[16].luecke_mittel, t[16].luecke_max) == (0.0, 0.0)


@pytest.mark.parametrize("tm, tx, erwartet_k", [
    (0.25, 1.0, 3),     # k = 1 hat Mittel 1,5 > 0,25; k = 3 hat genau 0,25 und 0,25: die Grenze zählt als erfüllt
    (1.5, 2.0, 1),      # k = 1: Mittel genau 1,5 <= 1,5 und Maximum 2,0 <= 2,0
    (1.5, 1.99, 3),     # Maximum 2,0 > 1,99: k = 1 fällt durch das Einzelfall-Kriterium
    (0.2, 1.0, 16),     # k = 3 liegt mit 0,25 über 0,2: nur der Bezug bleibt
])
def test_waehle_k_von_hand(mini, tm, tx, erwartet_k):
    w = A.waehle_k(mini, tm, tx)
    assert w.k == erwartet_k
    assert w.kein_kleineres_k == (erwartet_k == 16)


def test_labels_verhaeltnis_von_hand(mini):
    w = A.waehle_k(mini, 0.25, 1.0)
    assert w.labels_verhaeltnis == 40 / 100
    assert (w.luecke_mittel, w.luecke_max, w.instanzen, w.bezug) == (0.25, 0.25, 3, 16)


def test_erfuellt_prueft_beide_schwellen(mini):
    t = {z.k: z for z in A.tabelle(mini)}
    assert A.erfuellt(t[3], 0.25, 0.25)
    assert not A.erfuellt(t[3], 0.24, 1.0)       # Mittel zu groß
    assert not A.erfuellt(t[3], 1.0, 0.24)       # Maximum zu groß


def test_alle_gleich_ist_falsch_fuer_die_mini_zelle_und_wahr_bei_gleichen_schranken(mini):
    assert not A.alle_gleich(mini)
    gleich = dict(mini, zeilen=[dict(z, schranke={0: 100.0, 1: 200.0, 2: 400.0}[z["seed"]]) for z in mini["zeilen"]])
    assert A.alle_gleich(gleich)


def test_abgebrochene_laeufe_fehlen_und_zaehlen_nicht(mini):
    """Instanz 1 ohne k = 3 (abgebrochen): die Lücken und die Zahl der Instanzen beziehen sich nur auf Instanzen mit beiden Läufen."""
    ohne = dict(mini, zeilen=[z for z in mini["zeilen"] if not (z["k"] == 3 and z["seed"] == 1)])
    assert A.luecken(ohne, 3) == [0.25, 0.25]
    assert A.waehle_k(ohne, 0.25, 1.0).instanzen == 2
    assert A.labels_median(ohne, 3) == (20 + 60) / 2        # Median aus zwei Werten


# ---- Die acht Zellen von V8: Handwerte aus run_hand_16.log ------------------------------------------------------------------------------
# (typ, n, breite): (k = 1 Mittel/Max, k = 3, k = 5, gewähltes k bei 0,25 % / 1 %, Labels(k)/Labels(16) auf zwei Stellen)
LOG = {
    ("gruppiert", 50, 40): ((0.845, 2.378), (0.156, 0.461), (0.045, 0.139), 3, 0.48),
    ("gruppiert", 50, 100): ((2.518, 3.651), (0.504, 0.981), (0.244, 0.666), 5, 0.43),
    ("gruppiert", 100, 20): ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), 1, 0.40),
    ("gruppiert", 100, 40): ((0.762, 1.405), (0.175, 0.544), (0.045, 0.179), 3, 0.41),
    ("zufällig", 50, 40): ((1.191, 4.293), (0.088, 0.288), (0.0, 0.0), 3, 0.55),
    ("zufällig", 50, 100): ((3.227, 4.811), (0.411, 1.181), (0.123, 0.304), 5, 0.55),
    ("zufällig", 100, 20): ((0.0, 0.0), (0.0, 0.0), (0.0, 0.0), 1, 0.50),
    ("zufällig", 100, 40): ((0.879, 1.528), (0.109, 0.240), (0.004, 0.029), 3, 0.44),
}


@pytest.mark.parametrize("schluessel", list(LOG))
def test_v8_zelle_gegen_die_handwerte_des_log(zellen, schluessel):
    typ, n, breite = schluessel
    zelle = next(z for z in zellen if (z["typ"], z["n"], z["breite"]) == schluessel)
    k1, k3, k5, gewaehlt, verhaeltnis = LOG[schluessel]
    t = {z.k: z for z in A.tabelle(zelle)}
    for k, (mittel, maximum) in ((1, k1), (3, k3), (5, k5)):
        assert t[k].luecke_mittel == pytest.approx(mittel, abs=0.0006)
        assert t[k].luecke_max == pytest.approx(maximum, abs=0.0006)
    w = A.waehle_k(zelle, 0.25, 1.0)
    assert w.k == gewaehlt
    assert round(w.labels_verhaeltnis, 2) == verhaeltnis
    assert w.instanzen == 12 and zelle["bezug"] == 16


def test_die_acht_zellen_sind_vollstaendig_vorhanden(zellen):
    v8 = [z for z in zellen if z["bezug"] == 16]
    assert sorted((z["typ"], z["n"], z["breite"]) for z in v8) == sorted(LOG)
    assert all(z["ks"] == [1, 3, 5, 8, 12, 16] for z in v8)
    # 12 Instanzen je Zelle und k, keine abgebrochenen Läufe in dieser Reihe
    for z in v8:
        for k in z["ks"]:
            assert len({r["seed"] for r in z["zeilen"] if r["k"] == k}) == 12


def test_worst_case_am_regler_maximum_ist_sofort_fertig(zellen):
    """Rechenaufwand am Maximum (alle Zellen, strengste Schwellen): eine kleine Tabelle, kein Rechenlauf. Timeout als Netz, keine Zeit-Behauptung."""
    import pvw_constants as C
    for tm in C.TAU_MITTEL_WERTE:
        for tx in C.TAU_MAX_WERTE:
            for z in zellen:
                assert A.waehle_k(z, tm, tx).k in z["ks"]
