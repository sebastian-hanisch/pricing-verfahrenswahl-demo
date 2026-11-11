"""Permalink (Begrenzen), Schnellstart-Szenarien (Presets) und aktives Szenario (Standardmuster aus dem Demo-Portfolio).

Alle Regler stehen in SETTING_SPECS (Name im Session State -> Adressparameter, Typ, Standard, zulässige Werte). Das aktive Beispielszenario wird zustandslos bestimmt:
eines ist aktiv, wenn jeder Regler dem Wert des Szenarios entspricht. Es gibt keinen Zufalls-Seed und keinen Zufallsknopf: Die Demo rechnet nichts mit Zufall,
sie liest feste Messwerte."""

from dataclasses import dataclass

import streamlit as st

import pvw_constants as C


def _bool(roh) -> bool:
    if str(roh) not in ("True", "False"):
        raise ValueError(roh)
    return str(roh) == "True"


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: object
    default: object
    choices: tuple          # zulässige Werte; jeder Regler lässt nur Werte zu, zu denen es Messungen gibt


SETTING_SPECS = {
    "a_n": SettingSpec("n", int, C.DEFAULT_N, C.N_WERTE),
    "a_breite": SettingSpec("w", int, C.DEFAULT_BREITE, C.BREITE_WERTE),
    "a_typ": SettingSpec("typ", str, C.DEFAULT_TYP, C.TYP_WERTE),
    "a_r": SettingSpec("r", int, C.DEFAULT_GRENZEN, C.GRENZEN_WERTE),
    "a_ub": SettingSpec("ub", _bool, False, (False, True)),
    "a_pricing": SettingSpec("pd", _bool, True, (True, False)),
    "a_tau_mittel": SettingSpec("tm", float, C.DEFAULT_TAU_MITTEL, C.TAU_MITTEL_WERTE),
    "a_tau_max": SettingSpec("tx", float, C.DEFAULT_TAU_MAX, C.TAU_MAX_WERTE),
}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def choices(state_key) -> tuple:
    return SETTING_SPECS[state_key].choices


def _begrenzt(spec: SettingSpec, raw):
    """Wert aus der Adresszeile auf Typ und zulässige Werte bringen; None, wenn er unbrauchbar ist."""
    try:
        value = spec.caster(raw)
    except (ValueError, TypeError):
        return None
    return value if value in spec.choices else None


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen; unbrauchbare Werte bleiben beim Standard."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            value = _begrenzt(spec, qp[spec.url_param])
            if value is not None:
                st.session_state[state_key] = value
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    for state_key in SETTING_SPECS:
        if state_key in C.PRESETS[name]:
            st.session_state[state_key] = C.PRESETS[name][state_key]


def aktives_preset():
    """Name des Szenarios, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None.

    Zustandslos: verglichen wird jeder Regler aus SETTING_SPECS (ein Szenario ohne Eintrag für einen Regler meint dessen Standardwert) mit dem Session State.
    Ein später ergänzter Regler braucht nur seinen Eintrag in SETTING_SPECS, dann hebt auch seine Änderung die Markierung auf (tests/test_layout.py prüft das für jeden Regler)."""
    for name, preset in C.PRESETS.items():
        if all(st.session_state.get(state_key, spec.default) == preset.get(state_key, spec.default) for state_key, spec in SETTING_SPECS.items()):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Szenario ist hervorgehoben (`type="primary"`)."""
    if not C.PRESETS:
        return
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispielszenario laden (setzt alle Regler):")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )
