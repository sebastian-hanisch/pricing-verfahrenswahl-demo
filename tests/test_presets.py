"""Presets (Schnellstart-Szenarien): Vollständigkeit, gültige Werte, Standard-Szenario = Standardeinstellungen, Permalink-Begrenzung, Hilfetexte gegen die Wirkung."""

import pytest

import pvw_baum as B
import pvw_constants as C
import pvw_presets as P
import test_baum as TB


def test_every_preset_has_help_and_sets_every_control():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.SETTING_SPECS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_valid_for_their_controls():
    for name, preset in C.PRESETS.items():
        for key, value in preset.items():
            assert value in P.SETTING_SPECS[key].choices, (name, key, value)


def test_default_preset_equals_the_default_settings():
    assert {k: spec.default for k, spec in P.SETTING_SPECS.items()} == next(iter(C.PRESETS.values()))


def test_presets_differ_from_each_other_in_at_least_one_control():
    werte = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(werte)) == len(werte)


def test_url_parameters_are_unique():
    params = [s.url_param for s in P.SETTING_SPECS.values()]
    assert len(params) == len(set(params))


@pytest.mark.parametrize("key, roh, erwartet", [
    ("a_n", "100", 100), ("a_n", "40", None), ("a_n", "abc", None), ("a_n", "-3", None),
    ("a_breite", "150", 150), ("a_breite", "70", None), ("a_breite", "", None),
    ("a_typ", "gruppiert", "gruppiert"), ("a_typ", "egal", None),
    ("a_r", "4", 4), ("a_r", "0", None), ("a_r", "5", None),
    ("a_ub", "True", True), ("a_ub", "False", False), ("a_ub", "ja", None), ("a_pricing", "false", None),
    ("a_tau_mittel", "0.25", 0.25), ("a_tau_mittel", "0.3", None), ("a_tau_mittel", "x", None),
    ("a_tau_max", "5", 5.0), ("a_tau_max", "7", None),
])
def test_permalink_values_are_accepted_or_rejected(key, roh, erwartet):
    assert P._begrenzt(P.SETTING_SPECS[key], roh) == erwartet


def test_every_control_value_has_a_measurement_or_is_a_documented_unmeasured_case():
    """Jeder Wert eines Reglers kommt in mindestens einer Zelle der Messdaten vor (die Regler bieten nur Werte, zu denen es etwas gibt)."""
    import pvw_daten as D
    zeilen = D.messzeilen()
    zellen = D.k_zellen()
    n_gemessen = {n for z in zeilen for n in (z["bereich"]["n"] or [])} | {z["n"] for z in zellen}
    breiten = {b for z in zeilen for b in (z["bereich"]["breite"] or [])} | {z["breite"] for z in zellen}
    assert set(C.N_WERTE) <= n_gemessen
    assert set(C.BREITE_WERTE) <= breiten


# ---- Die Hilfetexte der Presets sind Behauptungen: gegen den Baum prüfen -----------------------------------------------------------------------

def test_hilfetext_standardaufgabe_nennt_fast_jeden_baustein_gemessen():
    a = TB.preset_aufgabe("Standardaufgabe: 30 Kunden, weite Fenster")
    s = B.baum(a)
    assert sum(1 for x in s if x.status == "nicht_gemessen") == 0


def test_hilfetext_enge_fenster_k_1_und_alle_k_gleich():
    a = TB.preset_aufgabe("Enge Fenster, 100 Kunden")
    assert B.wahl_k(a)[1].k == 1


def test_hilfetext_vier_grenzen_k_gemessen_grenzen_und_beschleuniger_nicht():
    st = TB.stati(TB.preset_aufgabe("50 Kunden, weite Fenster, vier Grenzen"))
    assert st["k"] == "empfohlen" and st["grenzen"] == "nicht_gemessen" and st["bidirektional"] == "nicht_gemessen"


def test_hilfetext_obere_schranke_nennt_kantenstreichung_aber_nicht_das_etikettenlimit():
    st = TB.stati(TB.preset_aufgabe("Obere Schranke bekannt, enge Fenster"))
    assert st["kanten"] == "moeglich" and st["heuristik"] == "nicht_gemessen"
    assert "Breite 40" in C.PRESET_HELP["Obere Schranke bekannt, enge Fenster"]


def test_hilfetext_kleine_aufgabe_elementar_moeglich():
    assert TB.stati(TB.preset_aufgabe("Kleine Aufgabe, 15 Kunden"))["elementar"] == "moeglich"


def test_hilfetext_ohne_messung_empfiehlt_keinen_baustein():
    a = TB.preset_aufgabe("Aufgabe ohne passende Messung")
    assert B.empfohlene_reihenfolge(B.baum(a)) == []
