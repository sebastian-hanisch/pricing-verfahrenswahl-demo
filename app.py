"""Verfahrenswahl im Pricing: welche Bausteine für welche Aufgabe? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Teil der Reihe „Ressourcenwege und Spaltenerzeugung“. Die Demo baut kein neues Verfahren: Ein Entscheidungsbaum liest feste Messwerte der anderen Demos der Reihe (data/*.json,
je Zeile mit Quelle) und nennt für jede Empfehlung Messzahl, Voraussetzung und Quelle; ein Baustein ohne Messung für Kundenzahl, Fensterbreite und Verteilung der Aufgabe wird nicht empfohlen, und die Messungen gelten bei ihrem eigenen ng-Gedächtnis (k = 5 oder 8). Gerechnet wird nur die Auswahlregel für das ng-Gedächtnis k.

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import pvw_baum as B
import pvw_constants as C
import pvw_daten as D
import pvw_evaluation as E
import pvw_texte as T
from pvw_daten import de
from pvw_layout import dunkles_design, kopf_css
from pvw_presets import choices, init_session_state_defaults, load_permalink_settings, sidebar_presets, sync_query_params
from pvw_visualization import build_ampel, build_crew, build_k_kurven, build_labels_verhaeltnis

st.set_page_config(page_title="Verfahrenswahl im Pricing – Sebastian Hanisch", layout="wide")

# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in pvw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Verfahrenswahl im Pricing: welche Bausteine für welche Aufgabe?")
st.markdown(T.INTRO)

with st.expander("So funktioniert die Verfahrenswahl", expanded=True):
    st.markdown(T.SO_FUNKTIONIERT)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()


def _prozent(x: float) -> str:
    return f"{x:g} %".replace(".", ",")


with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Szenario ist hervorgehoben
    st.header("⚙️ Aufgabe")
    st.markdown("**Größe und Form der Instanz**")
    n = st.select_slider("Kundenzahl n", options=choices("a_n"), key="a_n", help="Nur Kundenzahlen, zu denen es Messungen gibt.")
    breite = st.select_slider(
        "Fensterbreite (Horizont 300)", options=choices("a_breite"), key="a_breite", format_func=lambda b: f"{b} ({100 * b / C.HORIZONT:.0f} % des Horizonts)",
        help="Breite der Zeitfenster der Kunden in Zeiteinheiten. Der Horizont aller gemessenen Instanzen ist 300.")
    typ = st.radio("Verteilung der Kunden", options=choices("a_typ"), key="a_typ", horizontal=True, help="Zufällig im Quadrat verteilt oder in fünf Gruppen.")
    r = st.select_slider("Ressourcengrenzen (Zeit zählt mit)", options=choices("a_r"), key="a_r", format_func=lambda x: f"{x} (nur Zeit)" if x == 1 else str(x),
                         help="Zahl der Größen, die im Labeling begrenzt sind: Zeit, Last, weitere.")
    st.markdown("**Voraussetzungen**")
    ub = st.toggle("Obere Schranke vorhanden", key="a_ub", help="Eine zulässige ganzzahlige Lösung ist bekannt (Voraussetzung der Kantenstreichung).")
    pricing = st.toggle("Pricing dominiert die Rechenzeit", key="a_pricing", help="Das Pricing macht den Großteil der Rechenzeit aus (Voraussetzung für den Zeitgewinn des heuristischen Pricings).")
    st.markdown("**Auswahlregel für k**")
    tau_m = st.select_slider("Schwelle im Mittel", options=choices("a_tau_mittel"), key="a_tau_mittel", format_func=_prozent,
                             help="Größte erlaubte mittlere Lücke der Schranke zum Bezug (Einstellung der Demo, keine Aussage über die Wirklichkeit).")
    tau_x = st.select_slider("Schwelle im Einzelfall", options=choices("a_tau_max"), key="a_tau_max", format_func=_prozent,
                             help="Größte erlaubte Lücke in einer einzelnen Instanz.")

sync_query_params({"a_n": n, "a_breite": breite, "a_typ": typ, "a_r": r, "a_ub": ub, "a_pricing": pricing, "a_tau_mittel": tau_m, "a_tau_max": tau_x})

settings = E.Settings(int(n), int(breite), typ, int(r), bool(ub), bool(pricing), float(tau_m), float(tau_x))
aufgabe = settings.aufgabe()
stufen = B.baum(aufgabe)
empfohlen = B.empfohlene_reihenfolge(stufen)
zaehl = {s: sum(1 for x in stufen if x.status == s) for s in B.STATUS}
_zelle, k_wahl = B.wahl_k(aufgabe)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis: Bausteine für diese Aufgabe")
st.caption(
    f"Aufgabe: {settings.n} Kunden, Fensterbreite {settings.breite} ({de(100 * settings.breite / C.HORIZONT, 0)} % des Horizonts), {settings.typ} verteilt, {settings.r} "
    f"{'Grenze (nur Zeit)' if settings.r == 1 else 'Grenzen'}, obere Schranke {'vorhanden' if settings.ub else 'nicht vorhanden'}, "
    f"Pricing dominiert die Rechenzeit: {'ja' if settings.pricing else 'nein'}.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Empfohlen", f"{len(empfohlen)} von {len(stufen)}", delta="oder möglich", delta_color="off")
m2.metric("Nicht gemessen", f"{zaehl['nicht_gemessen']}", delta="Stufen", delta_color="off")
m3.metric("Nicht empfohlen", f"{zaehl['nicht_empfohlen']}", delta="mit Messzahl", delta_color="off")
m4.metric("ng-Gedächtnis k", f"{k_wahl.k}" if k_wahl else "nicht gemessen", delta=(f"Bezug k = {k_wahl.bezug}" if k_wahl else None), delta_color="off")
st.plotly_chart(build_ampel(stufen), width="stretch", key="ampel_chart", config={"displayModeBar": False})
st.caption("Jede Zeile ist eine Stufe des Baums; die Farbe zeigt den Status, ein Zeiger auf den Balken die Empfehlung.")

if empfohlen:
    st.markdown("**Reihenfolge der empfohlenen oder möglichen Bausteine:**")
    for i, s in enumerate(empfohlen, start=1):
        st.markdown(f"{i}. **{s.titel}** ({B.STATUS[s.status]}): {s.empfehlung}")
else:
    st.markdown("**Für diese Aufgabe wird kein Baustein empfohlen:** Es gibt keine passende Messung.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie weit reichen die Messungen für diese Aufgabe?")
kind, text = E.verdict_baum(stufen)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 1: der Entscheidungsbaum ---------------------------------------------------------------------------------------------------

st.subheader("🔬 Der Entscheidungsbaum, Stufe für Stufe")
st.caption("Jede Stufe nennt die Messzahl, die Voraussetzung dahinter und die Quelle. Stufen ohne passende Messung zeigen „nicht gemessen“ und den gemessenen Bereich.")
st.dataframe(pd.DataFrame(E.zusammenfassung(stufen)), hide_index=True, width="stretch", key="baum_tabelle")
for i, s in enumerate(stufen, start=1):
    with st.expander(f"{i}. {s.titel} – {B.STATUS[s.status]}", expanded=s.status in B.EMPFOHLEN):
        st.markdown(f"**{s.empfehlung}**")
        for beleg in s.belege:
            st.markdown(f"- {beleg.aussage}  \n  *Voraussetzung:* {beleg.voraussetzung}.  \n  *Quelle:* `{beleg.quelle}`.")
        for h in s.hinweise:
            st.caption("Hinweis: " + h)
st.info(
    "Die Stufen sind nach Voraussetzung und gemessener Wirkung geordnet. Die Wirkung mehrerer Bausteine zusammen ist in dieser Reihe nicht gemessen; "
    "die Zahlen der Stufen dürfen nicht miteinander multipliziert werden.")

st.markdown("---")

# --- Experiment 2: Auswahlregel für k ------------------------------------------------------------------------------------------------------

st.subheader("🔬 Die Auswahlregel für k an den Messdaten")
st.markdown(
    f"Regel: **das kleinste k, dessen Schranke im Mittel höchstens {de(settings.tau_mittel, 2)} % und in jeder Instanz höchstens {de(settings.tau_max, 2)} % unter der des Bezugs liegt** "
    "(Schwellen in der Seitenleiste verstellbar, Einstellung der Demo). **Bezug ist das größte gemessene k der Zelle**: bei 50 und 100 Kunden k = 16 (nicht die elementare Schranke, weil die elementare Rechnung dort in 94 von 96 Läufen abgebrochen wurde), bei 30 Kunden k = 8, bei Breite 40 (zufällig) die elementare Schranke selbst.")
uebersicht = E.k_uebersicht(settings.tau_mittel, settings.tau_max)
st.dataframe(
    pd.DataFrame(uebersicht), hide_index=True, width="stretch", key="k_tabelle",
    column_config={
        "Lücke Mittel (%)": st.column_config.NumberColumn(format="%.3f"),
        "Lücke Maximum (%)": st.column_config.NumberColumn(format="%.3f"),
        "Labels im Verhältnis zum Bezug": st.column_config.NumberColumn(format="%.2f"),
    })
st.plotly_chart(build_k_kurven(E.k_wahl_je_zelle(settings.tau_mittel, settings.tau_max), settings.tau_mittel), width="stretch", key="k_chart", config={"displayModeBar": False})
st.caption("Mittlere Lücke der Schranke zum Bezug je k; der Stern markiert das gewählte k, die gestrichelte Linie die Schwelle im Mittel. Bei Breite 20 und 100 Kunden liegen alle Punkte bei 0.")
kind, text = E.verdict_k(settings.tau_mittel, settings.tau_max)
getattr(st, kind)(text)
zellen = D.k_zellen()
ids = [z["id"] for z in zellen]
wahl = st.selectbox("Eine Zelle im Einzelnen ansehen", ids, key="k_zelle_wahl", format_func=lambda i: next(f"{z['n']} Kunden, Breite {z['breite']}, {z['typ']}" for z in zellen if z["id"] == i))
zelle = next(z for z in zellen if z["id"] == wahl)
st.dataframe(pd.DataFrame(E.k_detail(zelle)), hide_index=True, width="stretch", key="k_detail_tabelle")
q = zelle["quelle"]
st.caption(f"Quelle der Zelle: {'Vormessung' if q['demo'] == 'vormessung' else q['demo']}, {q['datei']} ({q['text']}).")

st.markdown("---")

# --- Experiment 3: was jeder Baustein kostet ---------------------------------------------------------------------------------------------------

st.subheader("🔬 Was jeder Baustein kostet")
st.caption("Eine Zeile je Baustein: Wirkung auf die Labels, Preis, gemessener Bereich und Quelle. Die Spalten lassen sich durch Anklicken der Kopfzeile sortieren.")
kosten = E.bausteine_tabelle()
st.dataframe(
    pd.DataFrame(kosten), hide_index=True, width="stretch", key="kosten_tabelle",
    column_config={"Labels im Verhältnis": st.column_config.NumberColumn(format="%.2f")})
st.plotly_chart(build_labels_verhaeltnis(kosten), width="stretch", key="kosten_chart", config={"displayModeBar": False})
st.caption("Labels im Verhältnis zur Vergleichsvariante der jeweiligen Zeile (grün: weniger Labels, rot: mehr; die gestrichelte Linie liegt bei 1). Nur Zeilen mit einem Verhältnis stehen im Diagramm.")
kind, text = E.verdict_kosten(kosten)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment 4: von der Schranke zur ganzen Lösung ------------------------------------------------------------------------------------------

st.subheader("🔬 Von der Schranke zur ganzen Lösung")
crew = D.zeile("crew_pairing")
st.markdown(
    "Das Pricing macht die **Schranke** (das lineare Programm), nicht die ganzzahlige Lösung. In der Fall-Demo `crew-pairing-demo` (Besatzungsplanung im Zugverkehr) liegt die ganzzahlige Lösung "
    f"im Mittel {de(crew['werte']['luecke_3'])} / {de(crew['werte']['luecke_4'])} / {de(crew['werte']['luecke_5'])} % über der Schranke (3 / 4 / 5 Züge, je 20 Netze), "
    f"das Pricing braucht dort {crew['werte']['pricing_3']} / {crew['werte']['pricing_4']} / {crew['werte']['pricing_5']} % der Rechenzeit der Spaltengenerierung.")
st.plotly_chart(build_crew(crew["werte"]), width="stretch", key="crew_chart", config={"displayModeBar": False})
st.caption(f"Quelle: {D.quelle_text(crew)}. Voraussetzung: {crew['voraussetzung']}.")
st.markdown("**Was die Master-Seite dazu tut** (nicht gebaut, nicht gemessen; nur Einordnung mit Prüfstand der Quelle):")
spalten = st.columns(len(T.MASTER_KARTEN))
for spalte, (titel, was, stand, pruefstand) in zip(spalten, T.MASTER_KARTEN):
    with spalte.container(border=True):
        st.markdown(f"**{titel}**")
        st.markdown(was)
        st.markdown(f"*In dieser Reihe:* {stand}")
        st.caption(f"Prüfstand: {pruefstand}")
st.info(
    "Der Abstand der ganzzahligen Lösung von der Schranke besteht aus der Ganzzahligkeitslücke und der Wahl unter den erzeugten Spalten. Die Zahlen oben sagen, wie groß der Abstand im Fall der Besatzungsplanung war; "
    "sie sagen nicht, wie viel davon Verzweigung, Schnitte oder Pfadaufzählung schließen würden.")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(T.ANNAHMEN_TABELLE)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(T.ANNAHMEN_ZEILEN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(T.MATH_LESEHILFE)
    st.markdown(T.MATH_FORMELN)

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Ressourcenwege: von der Grenze zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-ressourcenwege.html)."
)
