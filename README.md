# Verfahrenswahl im Pricing: welche Bausteine für welche Aufgabe? – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-pricing-verfahrenswahl-demo.streamlit.app/)**

Demo der Reihe „Ressourcenwege und Spaltenerzeugung“ in der „Konzepte“-Reihe der Website „Sebastian Hanisch – Operations Research und Machine Learning“. Sie ist das Ende der Reihe: Die anderen Demos haben die **Bausteine des Pricings** einzeln gezeigt, diese fragt, **für eine gegebene Aufgabe in welcher Reihenfolge man welchen Baustein zuschaltet und wann er sich nicht lohnt.** Sie baut kein neues Verfahren und rechnet fast nichts selbst: Ein **Entscheidungsbaum** liest feste Messwerte der anderen Demos und nennt bei jeder Empfehlung die Messzahl, die Voraussetzung (Kundenzahl, Fensterbreite, Verteilung, Zahl der Instanzen) und die Quelle. Ein Baustein ohne Messung für Kundenzahl, Fensterbreite und Verteilung der Aufgabe wird nicht empfohlen; die Messungen der Bausteine gelten bei ihrem eigenen ng-Gedächtnis (k = 5 oder 8), nicht bei dem k, das die Auswahlregel nennt. Gerechnet wird nur eine **Auswahlregel** für das ng-Gedächtnis k.

Die Bausteine stehen in diesen Demos der Reihe: [weg-mit-grenzen-demo](https://github.com/sebastian-hanisch/weg-mit-grenzen-demo) (Ressourcenweg), [dominanz-labels-demo](https://github.com/sebastian-hanisch/dominanz-labels-demo) (Dominanz), [zeitfenster-labeling-demo](https://github.com/sebastian-hanisch/zeitfenster-labeling-demo) (Zeitfenster und Warten), [mehrere-grenzen-demo](https://github.com/sebastian-hanisch/mehrere-grenzen-demo) (mehrere Grenzen), [pricing-dualpreise-demo](https://github.com/sebastian-hanisch/pricing-dualpreise-demo) (Dualpreise und Glättung), [kreise-im-pricing-demo](https://github.com/sebastian-hanisch/kreise-im-pricing-demo) (Kreise), [elementar-pricing-demo](https://github.com/sebastian-hanisch/elementar-pricing-demo) (elementar), [ng-routen-demo](https://github.com/sebastian-hanisch/ng-routen-demo) (ng-Gedächtnis, k-Zyklen, DSSR), [bidirektional-labeling-demo](https://github.com/sebastian-hanisch/bidirektional-labeling-demo), [eimer-labeling-demo](https://github.com/sebastian-hanisch/eimer-labeling-demo), [kantenstreichung-pricing-demo](https://github.com/sebastian-hanisch/kantenstreichung-pricing-demo) und [heuristisches-pricing-demo](https://github.com/sebastian-hanisch/heuristisches-pricing-demo). Die Anwendung in einem Fall zeigt [crew-pairing-demo](https://github.com/sebastian-hanisch/crew-pairing-demo) (Besatzungsplanung im Zugverkehr, Pricing als Label-Verfahren).

**Abgrenzung:** [hub-labeling-demo](https://github.com/sebastian-hanisch/hub-labeling-demo) (Kürzeste-Wege-Reihe) meint mit „Label“ etwas anderes: Einträge in Listen für schnelle Abfragen kürzester Wege. Hier ist ein Label ein Teilweg mit Kosten und Ressourcenverbräuchen im Pricing der Spaltenerzeugung.

## Kernfrage

**Aus diesen Messungen folgt keine allgemeine Reihenfolge der Bausteine; gemessen ist je Baustein, bei welcher Kundenzahl, Fensterbreite und Verteilung er Labels spart oder kostet, und was mehr Grenzen kosten.** Die Wirkung mehrerer Bausteine zusammen ist nicht gemessen. In den Zellen der Auswahlregel kommt Breite 20 nur bei 100 Kunden vor (Breite und Kundenzahl sind dort nicht getrennt), und die Beschleuniger sind nur bei 30 Kunden gemessen. Bei engen Fenstern (Breite 20, 100 Kunden) liegt die Schranke für jedes gemessene k gleich hoch; mit den Voreinstellungen der Schwellen (0,25 % im Mittel, 1 % im Einzelfall) gilt: bei Breite 40 wählt die Regel in 4 von 5 Zellen k = 3 (in der fünften k = 1), bei Breite 100 in 4 von 4 Zellen k = 4 oder 5; und die Beschleuniger (bidirektional, Kantenstreichung, heuristisches Pricing) erzeugen weniger Labels (bei der Kantenstreichung weniger Vorwärtslabels), jeder mit einem eigenen Preis (Verbindungspaare, eine obere Schranke, mehr Runden); ein Gesamtaufwand ist nicht gemessen. Die Messungen der Beschleuniger gelten bei ihrem eigenen ng-Gedächtnis (k = 5 oder 8), nicht bei dem k, das die Auswahlregel nennt. Alle Aussagen gelten für **eigene, Solomon-artige Instanzen** (nicht die Originalinstanzen) in Python; gezählt werden meist erzeugte Labels (bei Eimern Dominanzvergleiche, bei der Kantenstreichung Kanten und Vorwärtslabels), Sekunden nur zur Information.

## Befunde und Korrekturen gegenüber dem Plan

- **Neu gerechnete Zahlen gehen vor.** Wo die Quell-Demo eine Messreihe mit ihrem eigenen Kern neu gerechnet hat, steht ihre Zahl hier, nicht die der früheren Messreihe: fester Halbweg im Median 0,27 der Labels (früher 0,28), Verbindungspaare das 9,8-Fache (früher 8,6), Lücke von k = 1 zur elementaren Schranke bei 30 Kunden und Breite 100 im Mittel 3,33 % (früher 4,82 % aus nur drei fertigen elementaren Läufen), Eimer 6,8 bis 19,2 % (Zeit) und 26,9 bis 30,9 % (Last), elementare Läufe bei Breite 100 4 von 6 abgebrochen (früher 3 von 6), ng k = 5 gegen k = 8 bei 30 Kunden im Mittel 0,115 % (früher 0,00 / 0,05 / 0,04 % für zufällig / gruppiert / lang, je 5 Instanzen).
- **Quelle der Vormessung:** Für die gelernte Dominanz und die acht Zellen mit 50 und 100 Kunden ist die Quelle die Rohausgabe der Vormessung. Für das Etikettenlimit (Labels, Runden) ist es die Neurechnung in `heuristisches-pricing-demo` (Stand dieser Demo: Datei und README fertig), die mit der Rohausgabe der Vormessung übereinstimmt (Test); für seine Zeit die Zeitmessung der Vormessung in der Kopie von `heuristisches-pricing-demo`.
- **Die Auswahlregel hat elf Zellen statt acht.** Der Plan nannte die acht Zellen mit 50 und 100 Kunden. Dazu kommen drei Zellen mit 30 Kunden aus `ng-routen-demo` (Breite 100 zufällig und gruppiert mit Bezug k = 8, Breite 40 zufällig mit Bezug elementar), damit die Standardaufgabe mit 30 Kunden eine Antwort hat. Die Bezüge sind deshalb verschieden und stehen in jeder Zeile.
- **Jede Messzahl nennt das ng-Gedächtnis, mit dem sie gemessen wurde** (k = 5 oder 8). Wählt die Auswahlregel ein anderes k, steht dort, dass die Wirkung bei diesem k nicht eigens gemessen ist; das stand im Plan nicht.
- **Die Spalte „Labels im Verhältnis“ der Kostentabelle ist sortierbar, hat aber je Zeile eine andere Vergleichsvariante** (einseitig, voller Graph, immer exaktes Pricing, ng k = 8, ng k = 5); die Spalte „Verhältnis zu“ nennt sie. Zeilen ohne Labels-Verhältnis (Eimer: Vergleiche, Elementar: Abbrüche) haben dort keinen Wert.

## Modell

Eine **Aufgabe** ist ein Tupel aus Kundenzahl (10, 15, 20, 25, 30, 50, 100), Fensterbreite (20, 40, 100, 150, 200 bei einem Horizont von 300), Verteilung der Kunden (zufällig oder gruppiert), Zahl der Ressourcengrenzen (1 bis 4, die Zeit zählt mit), ob eine obere Schranke bekannt ist und ob das Pricing den Großteil der Rechenzeit ausmacht. Jeder Regler lässt nur Werte zu, zu denen es in den Messdaten etwas gibt. Der **Baum** besteht aus 14 Stufen (Grundbausteine, Größe der Rechnung, elementar, Gedächtnis k, Zahl der Grenzen, bidirektional, Kantenstreichung, heuristisches Pricing, Eimer, vier nicht empfohlene Bausteine, Master-Seite). Jede Stufe hat eine **Messzeile** in `data/messwerte.json` mit Quelle, Voraussetzung und dem Bereich (Kundenzahl, Breite, Verteilung), für den sie gemessen ist. Liegt die Aufgabe außerhalb, steht „nicht gemessen“. Die **Auswahlregel** wählt das kleinste k, dessen Schranke im Mittel höchstens τ_m und in jeder Instanz höchstens τ_max unter der Schranke des Bezugs liegt (Voreinstellung 0,25 % und 1 %; Einstellung der Demo, keine Aussage). Die Formeln stehen im Expander **📐 Mathematische Formulierung** der App mit Lesehilfe und Symboltabelle.

## Methodik

Fünf Abschnitte in der App: Ergebnis (Ampel der 14 Stufen und die Reihenfolge der empfohlenen Bausteine), (1) der Entscheidungsbaum Stufe für Stufe, (2) die Auswahlregel für k an den elf Zellen mit verstellbaren Schwellen und einer Einzelansicht je Zelle, (3) eine Tabelle, was jeder Baustein kostet (Wirkung, Preis, gemessener Bereich, Quelle, sortierbar), (4) die Lücke zwischen Schranke und ganzzahliger Lösung in `crew-pairing-demo` mit drei Karten zur Master-Seite. Die Quelle der Zahlen ist je Zeile angegeben; `tools/messwerte_bauen.py` baut `data/messwerte.json` und `data/k_zellen.json` aus den Dateien der Quell-Demos, und `tests/test_quellen.py` liest die Quellzeilen noch einmal und vergleicht.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an festen Instanzen der Quell-Demos (Python, eigene Solomon-artige Instanzen; Voraussetzung in jeder Zeile), keine Messungen dieser Demo. Die Auswahlregel selbst ist ihre einzige Rechnung. Die Zahl-zu-Test-Tabelle steht unten.

| Frage | Befund (Voraussetzung im Satz) | Test |
|---|---|---|
| Welches k wählt die Regel? | In den 11 Zellen mit den Voreinstellungen 0,25 % im Mittel und 1 % im Einzelfall: k = 1 in 3 Zellen, k = 3 in 4, k = 4 in 1, k = 5 in 3. Bei 50 und 100 Kunden (8 Zellen mit je 12 Instanzen, Bezug k = 16) k = 3 bei Breite 40 (50 und 100 Kunden, beide Verteilungen), k = 5 bei Breite 100 (50 Kunden), k = 1 bei Breite 20 (100 Kunden). Bei 30 Kunden, Breite 100 (je 12 Instanzen, Bezug k = 8): k = 4 (zufällig) und k = 5 (gruppiert); bei 30 Kunden, Breite 40, zufällig (6 Instanzen, Bezug elementar): k = 1. | A |
| Wie viele Labels braucht das gewählte k? | Median der Labels von k geteilt durch den Median der Labels des Bezugs: 0,40 bis 0,55 in den 8 Zellen mit 50 und 100 Kunden, 0,82 (zufällig) und 0,83 (gruppiert) bei 30 Kunden und Breite 100, 0,42 bei 30 Kunden und Breite 40 (zufällig). | A |
| Wann sind alle k gleich? | Bei 100 Kunden und Breite 20 liegt die Schranke für jedes gemessene k in jeder der 24 Instanzen (2 Zellen mit je 12) gleich hoch wie bei k = 16; k = 1 genügt dort. In keiner der 9 anderen Zellen ist das so. | B |
| Wie weit liegt k = 1 unter dem Bezug? | Mittlere Lücke bei 50 Kunden und Breite 100: 2,52 % (gruppiert, größte Instanz 3,65 %) und 3,23 % (zufällig, 4,81 %); bei 100 Kunden und Breite 40: 0,76 % und 0,88 %. Bezug ist k = 16, nicht die elementare Schranke. | B |
| Wo ist die elementare Rechnung möglich? | Bei 10 bis 25 Kunden (zufällig, Breite 40 und 100, 6 Instanzen je Zelle) 0 von 48 Läufen abgebrochen. Bei 30 Kunden, zufällig, 6 Instanzen je Breite: Breite 40 0 von 6, Breite 100 4 von 6, Breite 200 6 von 6 abgebrochen (Neurechnung der Quell-Demo; frühere Messung 0, 3 und 6 von 6; Zeitgrenze 30 Sekunden je Pricing-Aufruf, hängt von Rechner und Last ab). Bei 50 und 100 Kunden 94 von 96 Läufen abgebrochen. | C |
| Wie groß ist ein Pricing-Aufruf? | 30 Kunden, ng-Gedächtnis 5, ein Pricing-Aufruf mit den Dualpreisen der ersten Runde, 12 Instanzen je Zelle, Median der erzeugten Labels: zufällig 1 413 (Breite 20), 10 911 (Breite 100) und 42 510 (Breite 200); gruppiert 2 870, 20 414 und 68 216. | D |
| Was kosten mehrere Grenzen? | 30 Kunden, zufällig, Breite 100, ng-Gedächtnis 1, ganze Spaltenerzeugung, Grenze 70 je Zusatzgröße (bindend; bei nie bindender Grenze ist es eine andere Aufgabe mit anderen Zahlen), unabhängige Zufallsverbräuche, Median über 12 Instanzen, 1 bis 4 Grenzen: Anteil dominierter Labels 91,0 → 87,6 → 83,7 → 81,0 %, Vergleiche je Label 2,8 → 7,4 → 13,6 → 17,9. Bei abhängigen Verbräuchen (anderer Aufbau der Quell-Demo: ein Pricing-Aufruf, ng k = 5, nie bindende Grenzen) sinkt der Anteil dominierter Labels bei Fahrerzeit gleich Last nicht weiter, bei Last plus Rauschen schwächer und bei gegenläufigen Verbräuchen stärker als bei unabhängigen. | E |
| Was bringt das bidirektionale Labeling? | 30 Kunden, 480 Läufe: fester Halbweg H/2 im Median das 0,27-Fache der Labels des einseitigen Laufs (kleinster Wert 0,11, größter 0,79), in 480 von 480 Läufen weniger. Je Zelle (120 Läufe): zufällig 0,22 (Breite 40) und 0,25 (Breite 100); gruppiert 0,26 und 0,48. Der Preis: Verbindungspaare im Median das 9,8-Fache der einseitigen Label-Zahl. Eine einfache dynamische Wahl des Halbwegs (dynD, eine von vier eigenen Fassungen der Quell-Demo, nicht das Verfahren von Tilk u. a.) erzeugt in 0 von 480 Läufen weniger Labels als der feste (Median 0,68); ob ein Verbindungspaar billiger ist als ein Label, ist nicht gemessen, ein Gesamtaufwand ist nicht festgelegt. | F |
| Was bringt die Kantenstreichung? | 30 Kunden, 12 Instanzen je Zelle, bei den Dualpreisen der Konvergenz: Bei der exakten Lücke werden im Mittel je Zelle 46 bis 61 % der Kanten mit zulässiger Route gestrichen, die Vorwärtslabels sinken auf das 0,34- bis 0,52-Fache; mit einer oberen Schranke nur aus den Spalten 22 bis 42 % und das 0,56- bis 0,80-Fache. Setzt eine obere Schranke voraus. | G |
| Was bringt das heuristische Pricing? | 30 Kunden, ng k = 8, Breite 100, 30 Instanzen (Mittel der Instanz-Verhältnisse): Endschranke gleich in 30 von 30, Labels das 0,52-, 0,60- und 0,71-Fache des immer exakten Pricings (Limit 5, 10, 20), dafür +36, +23 und +10 % Runden; CPU-Zeit 0,36, 0,39 und 0,46 der exakten (3 Wiederholungen, ausgelasteter Rechner, nur Größenordnung), weil das Pricing dort 96,2 % der CPU-Zeit ausmacht und ein Master-LP nur etwa 380 Labels kostet; die Zeitreihe ist nicht neu gemessen, und die Quell-Demo hält fest, dass die Aussage „heuristisches Pricing ist schneller“ dort nicht steht. Bei Breite 150 (16 Instanzen): 0,43, 0,49 und 0,63 der Labels. | H |
| Was bringen Eimer? | 30 Kunden, ng k = 5, 80 Läufe mit Dualpreisen am Ende der Spaltenerzeugung (40 je Kapazität; die Reihe hat 320 Läufe), Ergebnis unverändert: Zeit-Eimer sparen im Median 6,8 bis 19,2 % der Dominanzvergleiche, Last-Eimer 26,9 bis 30,9 %. Netto nach Verwaltung (angenommenes Gewicht 0,1): 3,0 bis 6,6 % (Zeit-Eimer der Breite 20 bis 80) und 13,5 bis 20,1 % (Last-Eimer). | I |
| Was wird nicht empfohlen? | 30 Kunden, Breite 100, 24 Instanzen: k-Zyklen (K = 2) liegen im Mittel 0,469 % der Schranke von ng k = 8 unter dieser Schranke bei dem 1,69-Fachen der Labels, ng k = 5 liegt 0,115 % darunter bei dem 0,80-Fachen; K = 4 brach in 9 von 24 Läufen ab. DSSR braucht im Mittel der Verhältnisse das 6,3-Fache der Labels von ng k = 5 (11,6-Fache am Ende der Spaltenerzeugung), ng k = 5 verfehlt den besten Weg in 24 von 72 Dualpreis-Sätzen, am Ende in 0 von 24 (gemessen sind Runde 2, Runde 4 und das Ende; am Ende ist das ein schwacher Test, weil der ng-Master dort schon konvergiert ist). Einfache Glättung (6 Instanzen): 20,5 Runden ohne, 19,8 / 24,3 / 34,2 bei α = 0,5 / 0,8 / 0,9; bei α = 0,8 und 0,9 brauchen alle 6 Instanzen mehr Runden, bei α = 0,5 sind es etwa gleich viele. Gelernte Dominanz (Vormessung, nicht gebaut; Training an 20, Test an 5 Instanzen mit 30 Kunden, Breite 100, ng k = 8): Genauigkeit 91,9 / 92,4 % gegen 91,4 % der Mehrheitsklasse; 26,8 % der Labels streichbar, ohne dass der beste Weg in 30 Testaufrufen verloren ging, bei der größeren Schwelle in 4 von 30 Aufrufen ein Verlust. | J |
| Wie weit liegt die Schranke von der ganzen Lösung? | Besatzungsplanung (`crew-pairing-demo`, je 20 Netze mit 3, 4 und 5 Zügen): ganzzahlige Lösung im Mittel 5,2 / 4,1 / 3,4 % über der LP-Schranke (größte Lücke eines Netzes 15,5 / 12,7 / 8,2 %); das Pricing braucht 64 / 73 / 76 % der Rechenzeit der Spaltengenerierung. | K |

**Zahl → Test.** Jede Zahl der Tabelle steht in `tests/test_claims.py` (Buchstabe der Spalte „Test“ = Funktion `test_<Buchstabe>_…`): Der Test bildet den Satz aus den Daten (`data/*.json`) und prüft, dass er wörtlich in dieser README steht. Dass die Daten den Quelldateien der Quell-Demos gleichen und die Zahlen im Wortlaut der README der Quell-Demo stehen, prüft `tests/test_quellen.py` (nur, wenn der Ordner der Quell-Demo neben dieser Demo liegt). Nicht im Test, nur Messung dieser README: nichts.

## Ehrliche Grenzen

Annahmen, Grenzen und bekannte Probleme (derselbe Wortlaut wie im Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** der App):

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

## Literatur

Prüfstand der Quellen; keine Zahl daraus ist übernommen.

- Costa, Contardo, Desaulniers (2019): *Exact Branch-Price-and-Cut Algorithms for Vehicle Routing*, Transportation Science 53(4):946–985. Übersicht über Branch-Price-and-Cut. Prüfstand: Abstract gelesen.
- Pessoa, Sadykov, Uchoa, Vanderbeck (2020): *A Generic Exact Solver for Vehicle Routing and Related Problems*, Mathematical Programming 183:483–523. Pfadaufzählung, Verzweigung, Bucket-Graph. Prüfstand: Volltext gelesen.
- du Merle, Villeneuve, Desrosiers, Hansen (1999): stabilisierte Spaltenerzeugung, Discrete Mathematics 194(1–3):229–237. Prüfstand: Abstract gelesen.
- Jepsen, Petersen, Spoorendonk, Pisinger (2008): Subset-Row-Schnitte, Operations Research 56(2):497–511, und Pecin, Pessoa, Poggi, Uchoa (2017): *Improved branch-cut-and-price for capacitated vehicle routing*, Mathematical Programming Computation 9(1):61–100. Prüfstand: Abstracts gelesen.
- Irnich, Desaulniers, Desrosiers, Hadjar (2010): Streichen von Kanten mit Pfad-reduzierten Kosten. Prüfstand: Titel und Fundstelle in Katalogeinträgen geprüft, Zusammenfassung gelesen, Volltext nicht gelesen.
- Tilk, Rothenbächer, Gschwind, Irnich (2017), European Journal of Operational Research 261(2):530–539: dynamischer Halbweg im bidirektionalen Labeling. Prüfstand: Abstract gelesen.

## Tests

310 Tests, Laufzeit der Suite mit `-n 4` zwischen 13 Sekunden (ruhiger Rechner) und 190 Sekunden (Rechner durch andere Sitzungen stark ausgelastet), je Lauf gemessen (Windows). Zusammensetzung: Auswahlregel gegen Handrechnung an der Mini-Zelle und gegen die Handwerte der acht Zellen aus dem Log der Vormessung (`tests/test_algorithm.py`); **Orakel** gegen eine zweite Implementierung in elf Zellen und fünf Schwellenpaaren und gegen das Skript `hand_16.py` der Vormessung, das die Rohdateien selbst liest (`tests/test_oracle_pricing_verfahrenswahl.py`); Baum je Schnellstart-Szenario mit erwarteter Status-Zeile und die Eigenschaften „jede Empfehlung hat Quelle und Voraussetzung“, „ein Baustein ohne Messung wird nicht empfohlen“ über das Raster von 1 120 Aufgaben (`tests/test_baum.py`); Monotonie der Auswahlregel (`tests/test_eigenschaften_pricing_verfahrenswahl.py`); Randfälle (`tests/test_edge_cases.py`); jede Zahl der README (`tests/test_claims.py`); Kopie gegen Quelldateien und README der Quell-Demos (`tests/test_quellen.py`); Verdikte, Schnellstart-Szenarien, Oberfläche (AppTest), Layout, Footer, Laufzeit-Importe, README (`tests/test_verdicts.py`, `test_presets.py`, `test_app.py`, `test_layout.py`, `test_footer.py`, `test_runtime_imports.py`, `test_readme.py`).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `pvw_algorithm.py` | Kern: Auswahlregel für k (Lücke, Tabelle, Wahl) |
| `pvw_baum.py` | Entscheidungsbaum: 14 Stufen mit Messzahl, Voraussetzung, Quelle |
| `pvw_constants.py` | Regler-Werte, Schwellen, Farben, Schnellstart-Szenarien |
| `pvw_daten.py` | Messdaten laden, Bereich prüfen, Zahlen formatieren |
| `pvw_evaluation.py` | Tabellen und Verdikte |
| `pvw_layout.py` | Fester Kopf (Stylesheet), Tabellen im Telefonfenster scrollbar |
| `pvw_presets.py` | Permalink, Schnellstart in der Seitenleiste, aktives Szenario hervorgehoben |
| `pvw_texte.py` | Feste Texte, Karten der Master-Seite, Annahmen, Formeln |
| `pvw_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `data/messwerte.json` | Kopie der Zahlen des Baums, je Zeile Quelle, Voraussetzung, Bereich |
| `data/k_zellen.json` | Zellen der Auswahlregel: Schranke und Labels je Instanz und k |
| `tools/pvw_quellen.py` | Liest die Messdateien der Quell-Demos und bildet die Kennzahlen |
| `tools/messwerte_bauen.py` | Baut die beiden JSON-Dateien (`--pruefen` vergleicht nur) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | siehe Abschnitt Tests |

## Bewusst nicht umgesetzt

- **Eine eigene Messung.** Die Demo misst nichts neu und baut kein neues Verfahren; die Alternative „kleine Live-Messung für höchstens 30 Kunden“ ist nicht gebaut. Der Rechenaufwand am Regler-Maximum ist daher klein (11 Zellen, je 6 bis 12 Instanzen und 6 Werte von k).
- **Die Wirkung mehrerer Bausteine zusammen** und eine Reihenfolge, die aus einer Gesamtmessung folgt.
- **Die Master-Seite** (Stabilisierung, Subset-Row-Schnitte, Verzweigung, Pfadaufzählung): nur Karten mit Prüfstand der Quelle, keine Zahl, keine Empfehlung.
- **Zufalls-Seed, Zufallsknopf und PDF-Export:** Es wird nichts zufällig erzeugt, und die Seite besteht aus Tabellen und Texten der Quellen.
- **Messungen für alle Kombinationen von Kundenzahl und Fensterbreite:** Wo keine Messung vorliegt, steht „nicht gemessen“.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Die CI läuft mit Python 3.12; die festen Messreihen der Quell-Demos sind überwiegend mit Python 3.14 gerechnet. Die Streamlit-Cloud-Einstellung der Python-Version ist beim Deploy zu prüfen und hier einzutragen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Ressourcenwege: von der Grenze zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-ressourcenwege.html).
