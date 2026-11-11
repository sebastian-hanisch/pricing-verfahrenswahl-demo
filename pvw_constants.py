"""Konstanten: Regler-Werte, Dateinamen, Farben und Schnellstart-Szenarien.

Die Demo rechnet fast nichts selbst: Sie liest feste Messwerte (`data/*.json`, Kopien aus den Messdateien der anderen Demos der Reihe) und wendet darauf einen
Entscheidungsbaum und eine Auswahlregel an. Der Rechenaufwand am Regler-Maximum ist daher konstant klein (eine Tabelle mit 11 Zellen, je etwa 12 Instanzen und 6 Werten von k)."""

DATA_MESSWERTE = "messwerte.json"
DATA_K_ZELLEN = "k_zellen.json"

# Werte, bei denen es Messungen gibt (Horizont aller Instanzen: 300 Zeiteinheiten). Jeder Regler lässt nur diese Werte zu.
N_WERTE = (10, 15, 20, 25, 30, 50, 100)
BREITE_WERTE = (20, 40, 100, 150, 200)
TYP_WERTE = ("zufällig", "gruppiert")
GRENZEN_WERTE = (1, 2, 3, 4)               # Zahl der Ressourcengrenzen im Labeling; die Zeit zählt als erste
HORIZONT = 300

# Schwellen der Auswahlregel für k (Einstellung der Demo, keine Aussage über die Wirklichkeit)
TAU_MITTEL_WERTE = (0.05, 0.1, 0.25, 0.5, 1.0)   # in Prozent: größte erlaubte mittlere Lücke zum Bezug
TAU_MAX_WERTE = (0.25, 0.5, 1.0, 2.0, 5.0)       # in Prozent: größte erlaubte Lücke in einer einzelnen Instanz
DEFAULT_TAU_MITTEL, DEFAULT_TAU_MAX = 0.25, 1.0

DEFAULT_N, DEFAULT_BREITE, DEFAULT_TYP, DEFAULT_GRENZEN = 30, 100, "zufällig", 1

COLOR_OK = "#2F6B65"
COLOR_WARN = "#b8860b"
COLOR_NEIN = "#a33a3a"
COLOR_NEUTRAL = "#6b7b8c"
CELL_COLORS = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#b279a2", "#9d755d", "#bab0ac", "#2F6B65", "#ff9da6", "#8c6d31"]

# Schnellstart-Szenarien: alle Regler werden gesetzt (Schlüssel wie in SETTING_SPECS des Presets-Moduls)
PRESETS = {
    "Standardaufgabe: 30 Kunden, weite Fenster": {
        "a_n": 30, "a_breite": 100, "a_typ": "zufällig", "a_r": 1, "a_ub": False, "a_pricing": True,
        "a_tau_mittel": DEFAULT_TAU_MITTEL, "a_tau_max": DEFAULT_TAU_MAX,
    },
    "Enge Fenster, 100 Kunden": {
        "a_n": 100, "a_breite": 20, "a_typ": "zufällig", "a_r": 1, "a_ub": False, "a_pricing": True,
        "a_tau_mittel": DEFAULT_TAU_MITTEL, "a_tau_max": DEFAULT_TAU_MAX,
    },
    "50 Kunden, weite Fenster, vier Grenzen": {
        "a_n": 50, "a_breite": 100, "a_typ": "gruppiert", "a_r": 4, "a_ub": False, "a_pricing": True,
        "a_tau_mittel": DEFAULT_TAU_MITTEL, "a_tau_max": DEFAULT_TAU_MAX,
    },
    "Obere Schranke bekannt, enge Fenster": {
        "a_n": 30, "a_breite": 40, "a_typ": "zufällig", "a_r": 1, "a_ub": True, "a_pricing": True,
        "a_tau_mittel": DEFAULT_TAU_MITTEL, "a_tau_max": DEFAULT_TAU_MAX,
    },
    "Kleine Aufgabe, 15 Kunden": {
        "a_n": 15, "a_breite": 100, "a_typ": "zufällig", "a_r": 1, "a_ub": False, "a_pricing": True,
        "a_tau_mittel": DEFAULT_TAU_MITTEL, "a_tau_max": DEFAULT_TAU_MAX,
    },
    "Aufgabe ohne passende Messung": {
        "a_n": 100, "a_breite": 150, "a_typ": "gruppiert", "a_r": 3, "a_ub": True, "a_pricing": False,
        "a_tau_mittel": DEFAULT_TAU_MITTEL, "a_tau_max": DEFAULT_TAU_MAX,
    },
}
PRESET_HELP = {
    "Standardaufgabe: 30 Kunden, weite Fenster": "30 zufällig verteilte Kunden, Zeitfenster der Breite 100 (ein Drittel des Horizonts von 300), nur die Zeit als Grenze (die Messungen der übrigen Bausteine haben neben der Zeit eine Kapazitätsgrenze), keine obere Schranke, das Pricing dominiert die Rechenzeit. Für diese Aufgabe liegen für fast jeden Baustein Messungen vor; sie gelten bei ihrem eigenen ng-Gedächtnis (k = 5 oder 8), nicht bei dem k, das die Auswahlregel nennt.",
    "Enge Fenster, 100 Kunden": "100 Kunden, Fensterbreite 20: Hier lag die Schranke für jedes gemessene k gleich hoch wie beim Bezug k = 16; die Auswahlregel wählt k = 1.",
    "50 Kunden, weite Fenster, vier Grenzen": "50 gruppierte Kunden, Breite 100 und vier Ressourcengrenzen. Für k gibt es eine Messung, für die Zahl der Grenzen und für die Beschleuniger nicht: Die App zeigt dort „nicht gemessen“ statt einer Empfehlung.",
    "Obere Schranke bekannt, enge Fenster": "30 zufällig verteilte Kunden, Breite 40 und eine bekannte obere Schranke: Die Kantenstreichung wird mit ihrer Messzahl genannt (als möglich, nicht als empfohlen: Der Nutzen in späteren Aufrufen ist nicht gemessen); für das Etikettenlimit gibt es bei dieser Breite keine Messung.",
    "Kleine Aufgabe, 15 Kunden": "15 Kunden: Die elementare Rechnung ist in allen gemessenen Läufen mit 10 bis 25 Kunden fertig geworden.",
    "Aufgabe ohne passende Messung": "100 gruppierte Kunden, Breite 150, drei Grenzen, obere Schranke vorhanden, das Pricing dominiert die Rechenzeit nicht: Für diese Größe gibt es keine Messung, und kein Baustein wird empfohlen.",
}
