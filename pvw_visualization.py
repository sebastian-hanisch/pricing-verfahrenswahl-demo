"""Plotly-Figuren (alle Achsen fest, `fixedrange`; Kategorienachsen mit `type="category"`, keine Log-Achsen)."""

import plotly.graph_objects as go

import pvw_algorithm as A
import pvw_baum as B
import pvw_constants as C
import pvw_daten as D

STATUS_FARBE = {
    "grundlage": C.COLOR_NEUTRAL, "empfohlen": C.COLOR_OK, "moeglich": "#7aa874", "nicht_noetig": "#aab4be", "nicht_anwendbar": "#aab4be",
    "nicht_empfohlen": C.COLOR_NEIN, "nicht_gemessen": C.COLOR_WARN, "befund": "#4c78a8",
}


# Kurznamen der Stufen für die Beschriftung der Ampel (die vollen Titel stehen in der Tabelle und in den Expandern)
KURZ = {
    "grundbausteine": "Grundbausteine", "groesse": "Größe der Rechnung", "elementar": "Elementar?", "k": "Gedächtnis k", "grenzen": "Zahl der Grenzen",
    "bidirektional": "Bidirektional", "kanten": "Kantenstreichung", "heuristik": "Heuristisches Pricing", "eimer": "Eimer", "kzyklen": "k-Zyklen",
    "dssr": "DSSR", "glaettung": "Glättung", "gelernt": "Gelernte Dominanz", "master": "Master-Seite",
}


def _fest(fig: go.Figure, hoehe: int, unten: int = 10) -> go.Figure:
    """Gemeinsame Einstellungen: feste Höhe, durchsichtiger Hintergrund, keine Zoom- und Verschiebefunktion (Touch-Scrollen soll nicht am Diagramm hängen bleiben)."""
    fig.update_layout(height=hoehe, margin=dict(l=10, r=10, t=30, b=unten), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", dragmode=False)
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_ampel(stufen: list) -> go.Figure:
    """Eine Zeile je Stufe, gefärbt nach Status (Übersicht des Baums)."""
    titel = [f"{i + 1}. {KURZ[s.kennung]} – {B.STATUS[s.status]}" for i, s in enumerate(stufen)]
    fig = go.Figure(go.Bar(
        y=titel, x=[1] * len(stufen), orientation="h", marker_color=[STATUS_FARBE[s.status] for s in stufen],
        hovertext=[s.empfehlung for s in stufen], hoverinfo="text",
    ))
    fig.update_xaxes(range=[0, 1], visible=False)
    fig.update_yaxes(type="category", autorange="reversed", automargin=True, tickfont_size=11)
    fig.update_layout(showlegend=False, bargap=0.25)
    return _fest(fig, 30 * len(stufen) + 40)


def build_k_kurven(zellen_und_wahl: list, tau_mittel: float) -> go.Figure:
    """Mittlere Lücke zum Bezug je k und Zelle (Linien); das gewählte k ist ein Stern, die Schwelle eine gestrichelte Linie."""
    kategorien = ["1", "2", "3", "4", "5", "8", "12", "16", "elementar"]
    fig = go.Figure()
    for i, (z, w) in enumerate(zellen_und_wahl):
        farbe = C.CELL_COLORS[i % len(C.CELL_COLORS)]
        name = f"{z['n']} Kunden, B {z['breite']}, {z['typ']}"
        tab = {t.k: t for t in A.tabelle(z)}

        def kat(k, z=z):
            return "elementar" if k == z["n"] else str(k)

        xs = [kat(k) for k in sorted(tab)]
        fig.add_trace(go.Scatter(x=xs, y=[tab[k].luecke_mittel for k in sorted(tab)], mode="lines+markers", name=name, line=dict(color=farbe, width=2), marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=[kat(w.k)], y=[w.luecke_mittel], mode="markers", marker=dict(symbol="star", size=14, color=farbe, line=dict(color="black", width=1)),
                                 showlegend=False, hovertext=f"{name}: gewähltes k = {w.k}", hoverinfo="text"))
    fig.add_hline(y=tau_mittel, line_dash="dash", line_color="gray")
    fig.update_xaxes(type="category", categoryorder="array", categoryarray=kategorien, title="ng-Gedächtnis k")
    y_max = 1.08 * max(t.luecke_mittel for z, _ in zellen_und_wahl for t in A.tabelle(z))         # der größte Punkt (k = 1, 30 Kunden, Breite 100, zufällig: 3,646 %) liegt im Bild
    fig.update_yaxes(range=[-0.1, max(y_max, 3.9)], title="mittlere Lücke zum Bezug (%)")
    fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.16, font_size=10))
    return _fest(fig, 560, unten=170)


def build_labels_verhaeltnis(zeilen: list) -> go.Figure:
    """Labels im Verhältnis zur Vergleichsvariante je Baustein (Zeilen mit Zahl); Linie bei 1."""
    mit = [z for z in zeilen if z["Labels im Verhältnis"] is not None]
    farben = [C.COLOR_OK if z["Labels im Verhältnis"] < 1 else C.COLOR_NEIN for z in mit]
    namen = [f"{z['Baustein']}<br>{z['Labels im Verhältnis']:.2f}".replace(".", ",") + f" · {z['Verhältnis zu']}" for z in mit]
    fig = go.Figure(go.Bar(y=namen, x=[z["Labels im Verhältnis"] for z in mit], orientation="h", marker_color=farben))
    fig.add_vline(x=1, line_dash="dash", line_color="gray")
    fig.update_xaxes(range=[0, 7])   # ohne Achsentitel: Titel an der x-Achse einer Balkenreihe mit umgekehrter Kategorienachse löst beim ersten Zeichnen Konsolenfehler aus
    fig.update_yaxes(type="category", autorange="reversed", automargin=True)
    fig.update_layout(showlegend=False)
    return _fest(fig, 60 * len(mit) + 70)


def build_crew(werte: dict) -> go.Figure:
    """Lücke der ganzzahligen Lösung zur LP-Schranke (Mittel und größte) bei 3, 4, 5 Zügen; die Zahlen stehen im Namen der Kategorie."""
    mittel = [werte["luecke_3"], werte["luecke_4"], werte["luecke_5"]]
    groesste = [werte["max_3"], werte["max_4"], werte["max_5"]]
    zuege = [f"{z} Züge<br>Mittel {str(m).replace('.', ',')} %, größte {str(g).replace('.', ',')} %" for z, m, g in zip((3, 4, 5), mittel, groesste)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=zuege, y=mittel, name="Mittel über 20 Netze", marker_color=C.COLOR_OK))
    fig.add_trace(go.Bar(x=zuege, y=groesste, name="größte Lücke eines Netzes", marker_color=C.COLOR_WARN))
    fig.update_xaxes(type="category")
    fig.update_yaxes(range=[0, 19], title="ganzzahlige Lösung über der LP-Schranke (%)")
    fig.update_layout(barmode="group", legend=dict(orientation="h", yanchor="top", y=-0.25))
    return _fest(fig, 400, unten=60)
