"""Feste Texte der App (Einleitung, Erklärungen, Karten der Master-Seite, Annahmen, Formeln). Zahlen, die Befunde sind, stehen hier nicht: Sie kommen aus `data/*.json` (siehe `pvw_baum.py`).

`ASSUMPTIONS_MARKDOWN` steht wortgleich in der README (Abschnitt „Ehrliche Grenzen“); `tests/test_readme.py` vergleicht beide."""

INTRO = """
Das **Pricing** ist der Teil der Spaltenerzeugung, der mit den Dualpreisen des Masters (der Auswahl der bisher bekannten Routen) einen neuen Weg sucht, meist mit einem **Label-Verfahren**: Ein **Label** steht für einen Teilweg mit seinen Kosten und
Ressourcenverbräuchen, und ein Label **dominiert** ein anderes, wenn es nicht mehr kostet und nicht mehr verbraucht. Die anderen Demos dieser Reihe haben jeden **Baustein** einzeln gezeigt. Diese Demo fragt: **Für eine gegebene Aufgabe, welche Bausteine schaltet man in
welcher Reihenfolge zu, und wann lohnt einer sich nicht?**

Sie baut kein neues Verfahren und rechnet fast nichts selbst. Ein **Entscheidungsbaum** liest **feste Messwerte** der anderen Demos und nennt bei jeder Empfehlung die **Messzahl**, die **Voraussetzung** (Kundenzahl, Fensterbreite, Verteilung, Zahl der Instanzen) und die **Quelle**.
Wo es keine Messung gibt, steht „nicht gemessen“, und der Baustein wird nicht empfohlen. Alle Instanzen sind eigene, Solomon-artige (nicht die Originalinstanzen) und in Python gemessen; gezählt werden meist erzeugte Labels (bei Eimern Dominanzvergleiche, bei der Kantenstreichung Kanten und Vorwärtslabels), Sekunden nur zur Information.

Unten folgen die Experimente **🔬 Der Entscheidungsbaum**, **🔬 Die Auswahlregel für k an den Messdaten**, **🔬 Was jeder Baustein kostet** und **🔬 Von der Schranke zur ganzen Lösung**, dann **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""

SO_FUNKTIONIERT = """
1. **Aufgabe beschreiben** (Seitenleiste): Kundenzahl, Fensterbreite (der Horizont aller Instanzen ist 300), Verteilung der Kunden, Zahl der Ressourcengrenzen (die Zeit zählt mit), ob eine obere Schranke bekannt ist und ob das Pricing den Großteil der Rechenzeit ausmacht.
2. **Der Baum geht von der Grundlage zur Feinabstimmung:** Grundbausteine, Größe der Rechnung, elementar oder nicht, Gedächtnis k, Zahl der Grenzen, dann die Beschleuniger (bidirektional, Kantenstreichung, heuristisches Pricing, Eimer), danach das, was nicht empfohlen wird, und die Master-Seite.
3. **Jede Stufe nennt Messzahl, Voraussetzung und Quelle.** Liegt die Aufgabe außerhalb des gemessenen Bereichs, steht dort „nicht gemessen“ und der gemessene Bereich; der Baustein wird dann nicht empfohlen.
4. **Was die Messungen zur Reihenfolge sagen:** Aus ihnen folgt keine allgemeine Reihenfolge der Bausteine. Gemessen ist je Baustein, bei welcher Kundenzahl, Fensterbreite und Verteilung er Labels spart oder kostet, und was mehr Grenzen kosten; in den Zellen der Auswahlregel kommt Breite 20 nur bei 100 Kunden vor (Breite und Kundenzahl sind dort nicht getrennt), die Beschleuniger sind nur bei 30 Kunden gemessen. Bei engen Fenstern (Breite 20, 100 Kunden) liegt die Schranke für jedes gemessene k gleich hoch; mit den Voreinstellungen der Schwellen (0,25 % im Mittel, 1 % im Einzelfall) wählt die Regel bei Breite 100 in 4 von 4 Zellen k = 4 oder 5; jeder Beschleuniger erzeugt weniger Labels (bei der Kantenstreichung weniger Vorwärtslabels) und hat einen eigenen Preis; ein Gesamtaufwand ist nicht gemessen. Die Messungen der Beschleuniger gelten bei ihrem eigenen ng-Gedächtnis (k = 5 oder 8), nicht bei dem k, das die Regel nennt.

**Begriffe in einem Satz.** *Schranke*: der Wert des Masters am Ende der Spaltenerzeugung (untere Schranke der ganzzahligen Lösung). *ng-Gedächtnis k*: Jedes Label merkt sich, welche der k nächsten Nachbarn jedes besuchten Kunden schon dran waren; k = 1 verbietet nur die sofortige Wiederholung,
größeres k kommt der Regel „jeder Kunde höchstens einmal“ (elementar) näher. *Bezug*: die Schranke, gegen die die Lücke gemessen wird; bei 50 und 100 Kunden ist es k = 16, weil die elementare Rechnung dort fast immer abgebrochen wurde.
"""

ANNAHMEN_TABELLE = """
| Annahme | Was passiert, wenn sie nicht gilt | Wer setzt an |
|---|---|---|
| **Die Instanzen sind eigene, Solomon-artige** (Horizont 300, Bedienzeit 10, meist Kapazität 70) | Für die Originalinstanzen, andere Horizonte oder echte Daten ist keine Zahl gemessen; der Baum sagt darüber nichts. | keine |
| **Die Aufgabe liegt im gemessenen Bereich** (die Beschleuniger sind bei 30 Kunden gemessen) | Bei 50 und 100 Kunden gibt es nur die Messung für k und die Abbrüche; für alles andere zeigt der Baum „nicht gemessen“, nicht eine übertragene Zahl. | keine |
| **Bezug der Auswahlregel ist k = 16** (bei 30 Kunden k = 8 bzw. elementar) | Gegen die elementare Schranke ist die Lücke mindestens so groß wie gegen k = 16 (die Schranke sinkt nicht, wenn k wächst). | `ng-routen-demo` |
| **Die Schwellen der Auswahlregel sind eine Einstellung** | Andere Schwellen wählen ein anderes k; die Regel ist kein Beleg, dass sie auf anderen Instanzen gilt. | Regler „Schwellen“ |
| **Jede Messzahl gilt bei dem ng-Gedächtnis, mit dem sie gemessen wurde** (k = 5, 8) | Bei einem anderen k, etwa dem, das die Auswahlregel nennt, ist die Wirkung nicht eigens gemessen; die App weist darauf hin. | keine |
| **Die Messungen der übrigen Bausteine haben Zeit und eine Kapazitätsgrenze** (meist 70) | Bei einer anderen Zahl von Grenzen ist die Wirkung der Bausteine nicht gemessen; nur die Kosten mehrerer Grenzen stehen in der Stufe „Wie viele Ressourcengrenzen?“ (eine Zelle, unabhängige Verbräuche). | `mehrere-grenzen-demo` |
| **Bausteine wurden einzeln gemessen** | Die Wirkung mehrerer Bausteine zusammen ist in dieser Reihe nicht gemessen; die Zahlen dürfen nicht miteinander multipliziert werden. | keine |
| **Gezählt werden meist Labels** (bei Eimern Dominanzvergleiche, bei der Kantenstreichung Kanten und Vorwärtslabels) | Sekunden hängen von Rechner, Sprache und Last ab; nur das heuristische Pricing hat eine Zeitmessung (Größenordnung, ausgelasteter Rechner), bei den Eimern steht ein Laufzeitverhältnis als Hinweis. | `heuristisches-pricing-demo` |
| **Das Pricing macht nur die Schranke** | Die ganzzahlige Lösung liegt darüber (Besatzungsplanung: 3,4 bis 5,2 %); Verzweigung, Schnitte und Pfadaufzählung sind nicht gebaut. | `branch-and-price-demo` (anderes Problem) |
"""

MASTER_KARTEN = (
    ("Stabilisierung der Dualpreise",
     "Dualpreise springen von Runde zu Runde; die stabilisierte Spaltenerzeugung (du Merle u. a. 1999) bestraft Abweichungen von einem Zentrum im Dualraum.",
     "Gemessen ist nur die einfache Glättung zur Vorrunde, bei α = 0,8 und 0,9 ohne Ersparnis an Runden (siehe Stufe „Glättung der Dualpreise“); die Strafen im Dualraum sind nicht nachgebaut.",
     "Abstract gelesen (Suchtreffer); keine Zahl übernommen."),
    ("Subset-Row-Schnitte",
     "Schnitte über Teilmengen der Master-Zeilen (Jepsen u. a. 2008; Pecin u. a. 2017). Jeder Schnitt fügt dem Label einen zusätzlichen Zustand hinzu und schwächt voraussichtlich die Dominanz.",
     "Die Zahlen zu mehreren Grenzen (Obergrenzen wie die Last) sind nicht auf Schnitte übertragbar; für Schnitte nicht gemessen.",
     "Abstracts gelesen; keine Zahl übernommen."),
    ("Verzweigung und Pfadaufzählung",
     "Aufzählung aller Wege, deren reduzierte Kosten unter der Lücke liegen (Pessoa u. a. 2020); danach lässt sich das Pricing nachschlagen. Die Kantenstreichung ist die Vorstufe.",
     "Die Kantenstreichung ist gemessen (Stufe „Kantenstreichung“), die Aufzählung selbst nicht gebaut; Verzweigung am Cutting Stock zeigt `branch-and-price-demo` (anderes Problem).",
     "Pessoa u. a. 2020: Volltext gelesen; keine Zahl übernommen."),
)

ANNAHMEN_ZEILEN = """
**Annahmen**

- **Messdaten:** Der Baum liest feste Messwerte aus den Messdateien der anderen Demos der Reihe (Kopie in `data/messwerte.json` und `data/k_zellen.json`, je Zeile mit Quelle). Wo die Quell-Demo die Reihe neu gerechnet hat, gilt ihre neue Zahl; die Vormessung ist die Quelle für die gelernte Dominanz und die 8 Zellen mit 50 und 100 Kunden; das Etikettenlimit stammt aus der Neurechnung der Quell-Demo (mit der Vormessung verglichen), seine Zeit aus der Zeitmessung der Vormessung.
- **Instanzen:** eigene Solomon-artige Instanzen (nicht die Originalinstanzen), zufällig verteilt oder gruppiert, Horizont 300, Python.
- **Messgröße:** meist erzeugte Labels, bei Eimern Dominanzvergleiche, bei der Kantenstreichung Kanten und Vorwärtslabels. Sekunden stehen beim heuristischen Pricing (nur als Größenordnung) und als Hinweis bei den Eimern.
- **Auswahlregel:** kleinstes k, dessen Schranke im Mittel höchstens die erste Schwelle und in jeder Instanz höchstens die zweite Schwelle unter dem Bezug liegt; die Schwellen sind eine Einstellung der Demo.

**Grenzen**

- Ein Baustein wird nur genannt, wenn Kundenzahl, Fensterbreite und Verteilung der Aufgabe in seinem gemessenen Bereich liegen; sonst steht „nicht gemessen“. Das ist eine Vorsichtsregel, kein Urteil, dass er dort nicht wirkt. Auch im gemessenen Bereich gilt eine Zahl nur bei dem ng-Gedächtnis, mit dem sie gemessen wurde.
- Die Zahl der Instanzen je Zelle ist klein: 6 bis 12 in den meisten Reihen, 10 beim bidirektionalen Labeling und bei den Eimern, 15 je Typ beim Etikettenlimit (Breite 100; Breite 150: 8 je Typ); die gelernte Dominanz hat 20 Trainings- und 5 Testinstanzen. Mittel, Median und Maximum sagen über andere Instanzen der Verteilung wenig; eine Konfidenzaussage gibt es nicht.
- Die Wirkung der Bausteine zusammen ist nicht gemessen. Die Reihenfolge der Stufen ordnet nach Voraussetzung und gemessener Wirkung, nicht nach einer gemessenen Gesamtwirkung.
- Die Master-Seite (Stabilisierung, Subset-Row-Schnitte, Verzweigung, Pfadaufzählung) ist nicht gebaut und nicht gemessen; die Karten sind Einordnung mit Prüfstand der Quelle.

**Bekannte Probleme und Unsicherheiten**

- Die Zelle mit 30 Kunden, Breite 40, zufällig, liegt mit einer mittleren Lücke von 0,24 % knapp unter der Voreinstellung von 0,25 %; bei der nächsthöheren Strenge wählt die Regel dort ein größeres k (6 Instanzen).
- Die Zahl der Abbrüche der elementaren Läufe hängt von Rechner und Last ab (Zeitgrenze 30 Sekunden je Pricing-Aufruf): Die Neurechnung der Quell-Demo zeigt bei Breite 100 4 von 6, die frühere Messung 3 von 6.
- Die Ansichten wurden mit Streamlits Testwerkzeug und im Browser (Desktop und Telefonbreite) durchgesehen, nicht auf allen Geräten.
"""

MATH_LESEHILFE = """
**Lesehilfe.** Gegeben ist eine Aufgabe (Kundenzahl, Fensterbreite, Verteilung) und für jede Zelle der Messdaten, für jedes ng-Gedächtnis $k$ und jede Instanz $i$ die Schranke $z_{k,i}$ der Spaltenerzeugung. Gesucht ist das kleinste $k$, dessen Schranke
nur wenig unter der des Bezugs liegt. Die Schranken sind Untergrenzen: größeres $k$ gibt eine höhere (bessere) Schranke.

| Symbol | Bedeutung |
|---|---|
| $k$ | ng-Gedächtnis (Zahl der Nachbarn je Kunde) |
| $k^{\\mathrm{ref}}$ | Bezug: größtes gemessenes $k$ der Zelle (16, 8 oder elementar) |
| $i$ | Instanz einer Zelle, $I_k$ die Menge der Instanzen mit fertigen Läufen für $k$ und den Bezug |
| $z_{k,i}$ | Schranke der Spaltenerzeugung bei $k$ in Instanz $i$ |
| $g_{k,i}$ | Lücke in Prozent |
| $\\tau_{\\mathrm{m}}, \\tau_{\\max}$ | Schwellen für mittlere und größte Lücke (Einstellung) |
| $\\ell_k$ | Median der erzeugten Labels bei $k$ über die Instanzen |
"""

MATH_FORMELN = r"""
**Lücke.** Für jede Instanz, in der beide Läufe fertig wurden:

$$g_{k,i} = 100 \cdot \frac{z_{k^{\mathrm{ref}},i} - z_{k,i}}{z_{k^{\mathrm{ref}},i}}$$

**Auswahlregel.** Gewählt wird

$$k^{*} = \min \left\{ k : \frac{1}{|I_k|} \sum_{i \in I_k} g_{k,i} \le \tau_{\mathrm{m}} \ \text{ und } \ \max_{i \in I_k} g_{k,i} \le \tau_{\max} \right\}$$

Der Bezug erfüllt beide Bedingungen immer ($g = 0$); erfüllt kein kleineres $k$ sie, ist $k^{*} = k^{\mathrm{ref}}$, und die App weist darauf hin.

**Labels im Verhältnis zum Bezug.**

$$\rho = \frac{\ell_{k^{*}}}{\ell_{k^{\mathrm{ref}}}}$$

**Monotonie.** Werden beide Schwellen kleiner, so wird $k^{*}$ nie kleiner: Die Menge der erlaubten $k$ schrumpft, und die Regel nimmt das kleinste verbleibende (Test `test_eigenschaften`).

**Ohne Formel, nur Zuordnung.** Der Entscheidungsbaum selbst ist keine Formel, sondern eine Zuordnung: Jede Stufe prüft, ob (Kundenzahl, Fensterbreite, Verteilung) in der Menge liegt, für die ihre Messzeile gilt, und nennt dann die gespeicherten Zahlen dieser Zeile.

**Literatur.** Prüfstand der Quellen: Costa, Contardo, Desaulniers (2019), *Exact Branch-Price-and-Cut Algorithms for Vehicle Routing*, Transportation Science 53(4):946–985 (Abstract gelesen); Pessoa, Sadykov, Uchoa, Vanderbeck (2020), *A Generic Exact Solver for Vehicle Routing and Related Problems*,
Mathematical Programming 183:483–523 (Volltext gelesen); du Merle, Villeneuve, Desrosiers, Hansen (1999), Discrete Mathematics 194(1–3):229–237 (Abstract gelesen); Jepsen, Petersen, Spoorendonk, Pisinger (2008), Operations Research 56(2):497–511 (Abstract gelesen);
Pecin, Pessoa, Poggi, Uchoa (2017), *Improved branch-cut-and-price for capacitated vehicle routing*, Mathematical Programming Computation 9(1):61–100 (Abstract gelesen). Keine Zahl dieser Quellen ist übernommen.
"""
