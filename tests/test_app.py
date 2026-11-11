"""AppTest: Standard, jedes Preset (mit der erwarteten Verdikt-Zeile), Permalink, jeder Regler an seinen Rändern und Schlüssel. Expander werden nie per Index angesprochen."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import pvw_constants as C
import pvw_presets as P

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _expander(at, anfang):
    return next(e for e in at.expander if e.label.startswith(anfang))


def _markdown(at) -> str:
    return "\n".join(m.value for m in at.markdown)


def _info(at) -> list:
    return [x.value for x in list(at.info) + list(at.warning) + list(at.success)]


def test_standard_laedt_ohne_fehler_und_zeigt_die_kernelemente():
    at = _app()
    assert at.title[0].value.startswith("🧩")
    labels = [e.label for e in at.expander]
    assert any(l.startswith("So funktioniert") for l in labels)
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels
    assert len(at.dataframe) == 4                      # Baum, Zellen, Zelle im Einzelnen, Bausteine
    kopf = [h.value for h in at.subheader]
    assert any("Der Entscheidungsbaum" in h for h in kopf) and any("Auswahlregel für k" in h for h in kopf) and any("Was jeder Baustein kostet" in h for h in kopf) and any("Von der Schranke zur ganzen Lösung" in h for h in kopf)
    assert any("Wo die Annahmen enden" in h for h in kopf)


def test_standard_ergebnis_nennt_k_4_und_die_reihenfolge():
    at = _app()
    text = _markdown(at)
    assert "ng-Gedächtnis k = 4." in text
    assert "Reihenfolge der empfohlenen oder möglichen Bausteine" in text
    metrik = {m.label: m.value for m in at.metric}
    assert metrik["ng-Gedächtnis k"] == "4" and metrik["Empfohlen"] == "4 von 14" and metrik["Nicht gemessen"] == "0" and metrik["Nicht empfohlen"] == "5"


@pytest.mark.parametrize("name, k_text", [
    ("Standardaufgabe: 30 Kunden, weite Fenster", "4"),
    ("Enge Fenster, 100 Kunden", "1"),
    ("50 Kunden, weite Fenster, vier Grenzen", "5"),
    ("Obere Schranke bekannt, enge Fenster", "1"),
    ("Kleine Aufgabe, 15 Kunden", "nicht gemessen"),
    ("Aufgabe ohne passende Messung", "nicht gemessen"),
])
def test_jedes_preset_laeuft_und_zeigt_die_erwartete_verdikt_zeile(name, k_text):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    metrik = {m.label: m.value for m in at.metric}
    assert metrik["ng-Gedächtnis k"] == k_text
    kernfrage = [w.value for w in at.warning if w.value.startswith("Für diese Aufgabe fehlen Messungen")]
    assert bool(kernfrage) == (name in ("Enge Fenster, 100 Kunden", "50 Kunden, weite Fenster, vier Grenzen", "Kleine Aufgabe, 15 Kunden", "Aufgabe ohne passende Messung"))
    if name == "Standardaufgabe: 30 Kunden, weite Fenster":
        assert any("nicht gemessen 0;" in t for t in _info(at))
    if name == "Aufgabe ohne passende Messung":
        assert any("nicht gemessen 12;" in t for t in kernfrage)
        assert "Für diese Aufgabe wird kein Baustein empfohlen" in _markdown(at)


def test_expander_der_stufen_oeffnen_nach_status():
    at = _app()
    offen = {e.label: e.proto.expanded for e in at.expander if e.label[:1].isdigit()}
    assert offen["4. Welches ng-Gedächtnis k? – ✅ empfohlen"] is True
    assert offen["9. Eimer für die Dominanzprüfung – 🟢 möglich"] is True
    assert offen["3. Elementar rechnen (jeder Kunde höchstens einmal)? – ⛔ nicht empfohlen"] is False
    assert len(offen) == 14


def test_stufen_expander_nennt_voraussetzung_und_quelle():
    at = _app()
    text = "\n".join(m.value for m in _expander(at, "6. Bidirektionales").markdown)
    assert "Voraussetzung:" in text and "Quelle:" in text and "`bidirektional-labeling-demo, data/baender_v9.json`" in text


def test_permalink_uebernimmt_werte_und_verwirft_unbrauchbare():
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    at.query_params["n"] = "100"
    at.query_params["w"] = "20"
    at.query_params["typ"] = "gruppiert"
    at.query_params["ub"] = "True"
    at.query_params["tm"] = "9"         # unbrauchbar: bleibt beim Standard
    at.run()
    assert not at.exception
    assert at.sidebar.select_slider(key="a_n").value == 100 and at.sidebar.select_slider(key="a_breite").value == 20
    assert at.sidebar.radio(key="a_typ").value == "gruppiert" and at.sidebar.toggle(key="a_ub").value is True
    assert at.sidebar.select_slider(key="a_tau_mittel").value == C.DEFAULT_TAU_MITTEL


def test_die_adresszeile_spiegelt_die_einstellungen():
    at = _app()
    at.sidebar.select_slider(key="a_n").set_value(50).run()
    assert at.query_params["n"] == ["50"] or at.query_params["n"] == "50"


@pytest.mark.parametrize("key", list(P.SETTING_SPECS))
def test_jeder_regler_an_seinen_raendern_ohne_fehler(key):
    spec = P.SETTING_SPECS[key]
    for wert in (spec.choices[0], spec.choices[-1]):
        at = _app()
        regler = next(getattr(at.sidebar, art)(key=key) for art in ("select_slider", "radio", "toggle") if _hat(at, art, key))
        regler.set_value(wert).run()
        assert not at.exception, (key, wert, [str(e) for e in at.exception])


def _hat(at, art, key) -> bool:
    try:
        getattr(at.sidebar, art)(key=key)
        return True
    except KeyError:
        return False


def test_alle_minima_und_alle_maxima_zusammen_ohne_fehler():
    for index in (0, -1):
        at = _app()
        for key, spec in P.SETTING_SPECS.items():
            art = next(a for a in ("select_slider", "radio", "toggle") if _hat(at, a, key))
            getattr(at.sidebar, art)(key=key).set_value(spec.choices[index])
        at.run()
        assert not at.exception, [str(e) for e in at.exception]


def test_die_hauptseite_endet_mit_dem_footer():
    at = _app()
    assert at.main.caption[-1].value.startswith("Diese Demo ist Teil des Portfolios")
