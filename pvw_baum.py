"""Entscheidungsbaum: für eine Pricing-Aufgabe die Bausteine nennen, jeden mit Messzahl, Voraussetzung und Quelle.

Regeln (Entscheidung E16.5): Es gibt keine Regel „immer X“. Ein Baustein wird nur genannt, wenn die Aufgabe (Kundenzahl, Fensterbreite, Typ) im gemessenen Bereich seiner Messzeile liegt
(`pvw_daten.im_bereich`); sonst steht dort „nicht gemessen“ mit dem gemessenen Bereich. Die Zahlen der Belege kommen aus `data/messwerte.json` bzw. `data/k_zellen.json`; wenige Zahlen in Hinweisen (30 Sekunden, 7 Kunden, Laufzeitverhältnis der Eimer) stehen im Wortlaut der README der Quell-Demo.
„Empfohlen“ steht nur für das ng-Gedächtnis k (Ergebnis der Auswahlregel, eine Einstellung der Demo); ein Beschleuniger heißt „möglich“, weil seine Messung nur einen Teil der Frage stützt (Gesamtaufwand, späte Aufrufe, Zeit). Jede Stufe ist eine eigene Funktion
ohne versteckten Zustand; `baum` ruft sie nur der Reihe nach auf. Nur Standardbibliothek."""

from dataclasses import dataclass

import pvw_algorithm as A
import pvw_constants as C
import pvw_daten as D
from pvw_daten import de


@dataclass(frozen=True)
class Aufgabe:
    n: int
    breite: int
    typ: str
    r: int
    obere_schranke: bool
    pricing_dominiert: bool
    tau_mittel: float
    tau_max: float


@dataclass(frozen=True)
class Beleg:
    aussage: str          # was gemessen wurde, mit Zahl
    voraussetzung: str    # unter welchen Bedingungen
    quelle: str           # Demo und Datei


@dataclass(frozen=True)
class Stufe:
    kennung: str
    titel: str
    status: str           # Schlüssel von STATUS
    empfehlung: str
    belege: tuple = ()
    hinweise: tuple = ()


STATUS = {
    "grundlage": "🧱 Grundlage",
    "empfohlen": "✅ empfohlen",
    "moeglich": "🟢 möglich",
    "nicht_noetig": "➖ nicht nötig",
    "nicht_anwendbar": "➖ nicht anwendbar",
    "nicht_empfohlen": "⛔ nicht empfohlen",
    "nicht_gemessen": "❔ nicht gemessen",
    "befund": "ℹ️ Befund",
}
# Stufen, deren Baustein die Aufgabe tatsächlich bekommt (Reihenfolge der Empfehlung)
EMPFOHLEN = ("empfohlen", "moeglich")


def _beleg(zid: str, aussage: str) -> Beleg:
    z = D.zeile(zid)
    return Beleg(aussage, z["voraussetzung"], D.quelle_text(z))


def _bereich_text(z: dict) -> str:
    b = z["bereich"]
    teile = []
    if b["n"]:
        teile.append(" oder ".join(str(x) for x in b["n"]) + " Kunden")
    if b["breite"]:
        teile.append("Fensterbreite " + " / ".join(str(x) for x in b["breite"]))
    if b["typ"]:
        teile.append(" oder ".join(b["typ"]))
    return ", ".join(teile) if teile else "ohne Einschränkung"


def _ungemessen(kennung: str, titel: str, zid: str, grund: str = "") -> Stufe:
    """Stufe „nicht gemessen“: nennt den Bereich, in dem die Zeile gemessen ist."""
    z = D.zeile(zid)
    text = f"Für diese Aufgabe gibt es keine Messung; der Baustein wird nicht empfohlen. Gemessen ist: {_bereich_text(z)}."
    if grund:
        text = grund + " " + text
    return Stufe(kennung, titel, "nicht_gemessen", text, (), (f"Quelle des gemessenen Bereichs: {D.quelle_text(z)}.",))


def _typ_schluessel(typ: str) -> str:
    return {"zufällig": "zufaellig", "gruppiert": "gruppiert"}[typ]


# ---------------------------------------------------------------------------------------------------------------------------------------
# Stufen
# ---------------------------------------------------------------------------------------------------------------------------------------

def stufe_grundlage(a: Aufgabe) -> Stufe:
    """Ressourcenweg mit Labels, Dominanz über alle Ressourcen, Dualpreise: Voraussetzung jeder weiteren Stufe, keine Wahl."""
    z = D.zeile("dml_regeln")
    beleg = Beleg(
        f"Dominanz nur nach Kosten verfehlt den besten Weg in {z['werte']['verfehlt_nur_kosten']} von {z['werte']['faelle']} Fällen; ganz ohne Dominanz entstehen im Median "
        f"das {de(z['werte']['faktor_ohne_dominanz_median'], 2)}-Fache der Labels der vollen Regel.",
        z["voraussetzung"], D.quelle_text(z))
    return Stufe(
        "grundbausteine", "Ressourcenweg mit Labels und Dominanz über alle Ressourcen", "grundlage",
        "Bei jeder Aufgabe dieser Art: Labels mit Kosten und allen Ressourcenverbräuchen (Zeit, Last, …), Dominanz über alle diese Größen, Dualpreise aus dem Master.",
        (beleg,), ("Gemessen an Aufgaben mit 7 Kunden; für größere Aufgaben ist diese Zahl nicht eigens gemessen.",))


def stufe_groesse(a: Aufgabe) -> Stufe:
    """Wie groß ist ein Pricing-Aufruf bei dieser Fensterbreite? (Befund, keine Wahl.)"""
    titel = "Wie groß wird ein Pricing-Aufruf?"
    z = D.zeile("zfl_pricing")
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("groesse", titel, "zfl_pricing", f"Die Größe eines einzelnen Pricing-Aufrufs ist für {a.n} Kunden, Breite {a.breite}, {a.typ} nicht gemessen.")
    s = _typ_schluessel(a.typ)
    wert = z["werte"][f"{s}_b{a.breite}"]
    klein, gross = z["werte"][f"{s}_b{min(C.BREITE_WERTE)}"], z["werte"][f"{s}_b{max(C.BREITE_WERTE)}"]
    return Stufe(
        "groesse", titel, "befund",
        f"Ein Pricing-Aufruf mit den Dualpreisen der ersten Runde erzeugt bei Breite {a.breite} (30 Kunden, ng k = 5) im Median {de(wert, 0)} Labels (Horizont {C.HORIZONT}, die Breite ist {de(100 * a.breite / C.HORIZONT, 0)} % davon).",
        (_beleg("zfl_pricing", f"Der Median der Labels steigt bei {a.typ} verteilten Kunden von {de(klein, 0)} (Breite {min(C.BREITE_WERTE)}) auf {de(gross, 0)} (Breite {max(C.BREITE_WERTE)})."),),
        ("Die Zahl der Labels wächst hier mit der Fensterbreite; das gilt für diese Messreihe, nicht als Gesetz für alle Instanzen.",))


def stufe_elementar(a: Aufgabe) -> Stufe:
    """Elementar rechnen (jeder Kunde höchstens einmal)? Nur wo die Messung fertige Läufe zeigt."""
    titel = "Elementar rechnen (jeder Kunde höchstens einmal)?"
    klein, gross, epr = D.zeile("ngr_elementar_klein"), D.zeile("ngr_elementar_gross"), D.zeile("epr_abbrueche")
    if D.im_bereich(klein, a.n, a.breite, a.typ):
        v = klein["werte"]
        return Stufe(
            "elementar", titel, "moeglich",
            f"Bei 10 bis 25 Kunden (zufällig, Breite 40 und 100) war die elementare Rechnung in {v['laeufe'] - v['abgebrochen']} von {v['laeufe']} gemessenen Läufen fertig.",
            (_beleg("ngr_elementar_klein", f"Elementare Läufe mit 10 bis 25 Kunden: {v['abgebrochen']} von {v['laeufe']} abgebrochen."),),
            ("Fertig heißt nicht billig: Die Wand steht in `elementar-pricing-demo` (Vergleiche je Label wachsen mit der Kundenzahl).",))
    if D.im_bereich(epr, a.n, a.breite, a.typ):
        v = epr["werte"]
        ab, la = v[f"neu_b{a.breite}_abgebrochen"], v[f"neu_b{a.breite}_laeufe"]
        frueher = f"; in der früheren Messung {v[f'v1_b{a.breite}_abgebrochen']} von {v[f'v1_b{a.breite}_laeufe']}"
        beleg = _beleg("epr_abbrueche", f"Elementare Läufe bei {a.n} Kunden und Breite {a.breite}: {ab} von {la} abgebrochen (Neurechnung der Quell-Demo){frueher}.")
        if ab == 0:
            return Stufe("elementar", titel, "moeglich", f"Bei Breite {a.breite} war die elementare Rechnung in {la} von {la} Läufen fertig.", (beleg,),
                         ("Die Zeitgrenze von 30 Sekunden je Pricing-Aufruf und der Rechner bestimmen mit, ob ein Lauf abbricht.",))
        hin = ["Die Zahl der Abbrüche hängt von Rechner und Last ab (Zeitgrenze 30 Sekunden je Pricing-Aufruf)."]
        if a.breite == 100:
            hin.append("Die Lücke von k = 1 zur elementaren Schranke (Stufe „Welches ng-Gedächtnis k?“) stammt aus einer anderen Messung mit einer Obergrenze von Dominanztests statt der Zeitgrenze; dort wurden alle 6 elementaren Läufe fertig.")
        return Stufe("elementar", titel, "nicht_empfohlen", f"Bei Breite {a.breite} brach die elementare Rechnung in {ab} von {la} Läufen ab.", (beleg,), tuple(hin))
    if D.im_bereich(gross, a.n, a.breite, a.typ) and D.k_zelle(a.n, a.breite, a.typ):
        v = gross["werte"]
        return Stufe(
            "elementar", titel, "nicht_empfohlen",
            f"Bei 50 und 100 Kunden brach die elementare Rechnung in {v['abgebrochen']} von {v['laeufe']} gemessenen Läufen ab (alle 8 Zellen zusammen).",
            (_beleg("ngr_elementar_gross", f"Elementare Läufe bei 50 und 100 Kunden: {v['abgebrochen']} von {v['laeufe']} abgebrochen."),),
            ("Bezug der Auswahlregel für k ist deshalb k = 16, nicht die elementare Schranke.",))
    return Stufe("elementar", titel, "nicht_gemessen",
                 f"Für {a.n} Kunden mit Breite {a.breite} ({a.typ}) gibt es keine Messung der elementaren Rechnung; sie wird nicht empfohlen. "
                 f"Gemessen ist: {_bereich_text(klein)} (alle fertig); 30 Kunden mit Breite 40 / 100 / 200 zufällig; 50 und 100 Kunden in den Zellen der Auswahlregel.", (), ())


def wahl_k(a: Aufgabe):
    """(Zelle, Wahl) der Auswahlregel für die Aufgabe, oder (None, None)."""
    zelle = D.k_zelle(a.n, a.breite, a.typ)
    return zelle, (A.waehle_k(zelle, a.tau_mittel, a.tau_max) if zelle else None)


def stufe_k(a: Aufgabe) -> Stufe:
    """Welches ng-Gedächtnis k? Auswahlregel auf den Messdaten der Zelle."""
    titel = "Welches ng-Gedächtnis k?"
    zelle, w = wahl_k(a)
    if zelle is None:
        zellen = ", ".join(f"{z['n']} Kunden / Breite {z['breite']} / {z['typ']}" for z in D.k_zellen())
        return Stufe("k", titel, "nicht_gemessen",
                     f"Für diese Aufgabe gibt es keine Zelle der Auswahlregel; kein k wird empfohlen. Zellen mit Messdaten: {zellen}.", (), ())
    elementar = w.bezug == a.n
    bezug = "die elementare Schranke" if elementar else f"k = {w.bezug}"
    bezug_von = "der elementaren Rechnung" if elementar else f"von k = {w.bezug}"       # „unter der Schranke …“, „der Labels …“ (Genitiv)
    q = zelle["quelle"]
    ort = "Vormessung" if q["demo"] == "vormessung" else q["demo"]
    beleg = Beleg(
        f"Bei k = {w.k} liegt die Schranke im Mittel {de(w.luecke_mittel, 3)} % und in der ungünstigsten Instanz {de(w.luecke_max, 3)} % unter der Schranke {bezug_von}; "
        f"die ganze Spaltenerzeugung erzeugt im Median {de(w.labels_verhaeltnis, 2)} der Labels {bezug_von}.",
        f"{a.n} Kunden, Breite {a.breite}, {a.typ}, {w.instanzen} Instanzen, Überdeckungs-Master; Schwellen {de(a.tau_mittel, 2)} % im Mittel und {de(a.tau_max, 2)} % im Einzelfall (Einstellung der Demo)",
        f"{ort}, {q['datei']}")
    hinweise = [f"Bezug ist {bezug}" + ("." if elementar else ", nicht die elementare Schranke (die elementare Rechnung ist bei 50 und 100 Kunden fast immer abgebrochen)." if w.bezug == 16 else ", nicht die elementare Schranke.")]
    if w.kein_kleineres_k:
        hinweise.append("Kein kleineres k erfüllt beide Schwellen; gewählt ist der Bezug selbst.")
    if A.alle_gleich(zelle):
        hinweise.append("In dieser Zelle liegt die Schranke für jedes gemessene k in jeder Instanz gleich hoch wie beim Bezug k = 16; k = 1 genügt gegen diesen Bezug, und die Zelle sagt nichts über die Wirkung eines größeren k.")
    if w.k == 1:
        hinweise.append("k = 1 verbietet nur die sofortige Wiederholung eines Kunden; Kreise über mehrere Kunden bleiben möglich.")
    belege = [beleg]
    if (a.n, a.typ) == (30, "zufällig") and a.breite in (40, 100):
        z = D.zeile("kip_luecke")
        pre = f"b{a.breite}"
        belege.append(_beleg("kip_luecke", f"k = 1 liegt bei Breite {a.breite} im Mittel {de(z['werte'][pre + '_mittel'], 2)} % (größte {de(z['werte'][pre + '_max'], 2)} %) unter der elementaren Schranke."))
    hinweise.append(f"Die Wahl ist eine Einstellung der Demo: Sie hängt an den Schwellen {de(a.tau_mittel, 2)} % und {de(a.tau_max, 2)} % und an den {w.instanzen} Instanzen der Zelle; bei anderen Schwellen oder Instanzen kann die Regel ein anderes k nennen.")
    return Stufe("k", titel, "empfohlen", f"ng-Gedächtnis k = {w.k}.", tuple(belege), tuple(hinweise))


def stufe_grenzen(a: Aufgabe) -> Stufe:
    """Wie viele Ressourcengrenzen? Mehr Grenzen schwächen die Dominanz."""
    titel = "Wie viele Ressourcengrenzen?"
    z = D.zeile("mgr_v11")
    kapazitaet = ("Die Messungen der übrigen Stufen haben neben der Zeit eine Kapazitätsgrenze (meist 70, beim bidirektionalen Labeling und bei den Eimern auch 120); "
                  "bei einer anderen Zahl von Grenzen ist ihre Wirkung nicht gemessen.")
    if a.r == 1:
        return Stufe("grenzen", titel, "nicht_noetig", "Nur die Zeit ist begrenzt: Es kommt kein Mehraufwand durch weitere Ressourcen hinzu.", (),
                     ("Was zwei bis vier Grenzen kosten, steht in dieser Stufe, sobald der Regler „Ressourcengrenzen“ größer ist und die Aufgabe im gemessenen Bereich liegt (30 Kunden, zufällig, Breite 100).",
                      kapazitaet))
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("grenzen", titel, "mgr_v11", f"Der Preis von {a.r} Ressourcengrenzen ist für diese Aufgabe nicht gemessen.")
    v = z["werte"]
    r = a.r
    k_ = D.zeile("mgr_korreliert")["werte"]
    return Stufe(
        "grenzen", titel, "befund",
        f"Mit {r} Grenzen sinkt der Anteil dominierter Labels von {de(v['r1_dominiert_median'])} % (nur Zeit) auf {de(v[f'r{r}_dominiert_median'])} %, und die Vergleiche je Label steigen "
        f"von {de(v['r1_vergleiche_je_label_median'])} auf {de(v[f'r{r}_vergleiche_je_label_median'])}.",
        (_beleg("mgr_v11", f"Median über {v[f'r{r}_instanzen']} Instanzen: Anteil dominiert {de(v['r1_dominiert_median'])} → {de(v['r2_dominiert_median'])} → {de(v['r3_dominiert_median'])} → "
                           f"{de(v['r4_dominiert_median'])} %, Vergleiche je Label {de(v['r1_vergleiche_je_label_median'])} → {de(v['r2_vergleiche_je_label_median'])} → "
                           f"{de(v['r3_vergleiche_je_label_median'])} → {de(v['r4_vergleiche_je_label_median'])} für 1 bis 4 Grenzen."),),
        ("Gemessen sind in dieser Stufe nur unabhängige Zufallsverbräuche, mit einer bindenden Grenze 70 je Zusatzgröße; bei nie bindender Grenze ist es eine andere Aufgabe mit anderen Zahlen.",
         f"Abhängige Verbräuche sind in einer anderen Zelle der Quell-Demo gemessen (ein Pricing-Aufruf, 30 Kunden, Breite 100, ng k = 5, nie bindende Grenzen, {k_['instanzen']} Instanzen, vier Verbrauchsmodelle): "
         f"Anteil dominierter Labels bei 1 bis 4 Grenzen unabhängig {de(k_['unabhaengig_r1'])} → {de(k_['unabhaengig_r2'])} → {de(k_['unabhaengig_r3'])} → {de(k_['unabhaengig_r4'])} %; "
         f"Fahrerzeit gleich Last {de(k_['gleich_last_r2'])} % bei 2 bis 4 Grenzen (ohne weiteres Sinken); Last plus Rauschen {de(k_['rauschen_r2'])} → {de(k_['rauschen_r3'])} → {de(k_['rauschen_r4'])} % (schwächer); "
         f"gegenläufig {de(k_['gegenlaeufig_r2'])} → {de(k_['gegenlaeufig_r3'])} → {de(k_['gegenlaeufig_r4'])} % (stärker).",
         kapazitaet))


def _k_hinweis(a: Aufgabe, zid: str) -> list:
    """Hinweis, wenn der Baustein mit einem anderen ng-Gedächtnis gemessen wurde als dem, das die Auswahlregel nennt."""
    ks = D.zeile(zid)["k_gemessen"]
    _, w = wahl_k(a)
    gem = " oder ".join(str(k) for k in ks)
    if w is None:
        return [f"Gemessen mit ng-Gedächtnis k = {gem}."]
    if w.k not in ks:
        return [f"Gemessen mit ng-Gedächtnis k = {gem}; bei dem gewählten k = {w.k} ist die Wirkung nicht eigens gemessen."]
    return [f"Gemessen mit ng-Gedächtnis k = {gem} (gewählt: k = {w.k})."]


def stufe_bidirektional(a: Aufgabe) -> Stufe:
    """Bidirektionales Labeling mit festem Halbweg H/2."""
    titel = "Bidirektionales Labeling (von beiden Enden, Halbweg H/2)"
    z = D.zeile("bdl_v9")
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("bidirektional", titel, "bdl_v9")
    v = z["werte"]
    s = _typ_schluessel(a.typ)
    zelle = v[f"{s}_b{a.breite}_median"]
    belege = (
        _beleg("bdl_v9", f"Fester Halbweg H/2 erzeugt bei {a.typ} verteilten Kunden und Breite {a.breite} im Median das {de(zelle, 2)}-Fache der Labels des einseitigen Laufs "
                         f"({v[f'{s}_b{a.breite}_laeufe']} Läufe); über alle {v['laeufe']} Läufe {de(v['verhaeltnis_median'], 2)} (kleinster Wert {de(v['verhaeltnis_min'], 2)}, größter {de(v['verhaeltnis_max'], 2)}), "
                         f"in {v['weniger_labels']} von {v['laeufe']} Läufen weniger Labels."),
        _beleg("bdl_v9", f"Preis: Das Verbinden der beiden Hälften braucht im Median das {de(v['paare_je_label_median'])}-Fache der einseitigen Label-Zahl an Verbindungspaaren."),
    )
    hin = [f"Ein einfacher dynamischer Halbweg (dynD, eine von vier eigenen Fassungen der Quell-Demo, nicht das Verfahren von Tilk u. a.) erzeugte in {v['dynamisch_besser_als_fest']} von {v['laeufe']} Läufen weniger Labels als der feste Halbweg H/2 "
           f"(Median {de(v['dynamisch_median'], 2)} des einseitigen Laufs); gemessen ist nur dieser Vergleich mit H/2, nicht das Verfahren der Literatur.",
           "Ob ein Verbindungspaar billiger ist als ein Label, ist nicht gemessen, und ein Gesamtaufwandsmaß aus Labels und Verbindungspaaren ist nicht festgelegt."]
    hin += _k_hinweis(a, "bdl_v9")
    return Stufe("bidirektional", titel, "moeglich",
                 f"Gemessen: fester Halbweg H/2 erzeugt im Median das {de(zelle, 2)}-Fache der Labels des einseitigen Laufs, braucht aber im Median das {de(v['paare_je_label_median'])}-Fache dieser Label-Zahl an Verbindungspaaren; der Gesamtaufwand ist nicht gemessen.",
                 belege, tuple(hin))


def stufe_kanten(a: Aufgabe) -> Stufe:
    """Kantenstreichung: setzt eine obere Schranke voraus."""
    titel = "Kantenstreichung (mit oberer Schranke)"
    z = D.zeile("ksp_n30")
    if not a.obere_schranke:
        return Stufe("kanten", titel, "nicht_anwendbar",
                     "Die Kantenstreichung setzt eine obere Schranke (zulässige ganzzahlige Lösung) voraus; ohne sie ist sie nicht anwendbar.", (), ())
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("kanten", titel, "ksp_n30")
    v = z["werte"]
    p = f"{'zufall' if a.typ == 'zufällig' else 'gruppiert'}_b{a.breite}"
    belege = (
        _beleg("ksp_n30", f"Bei der exakten Lücke (ganzzahliges Optimum als obere Schranke, im Mittel {de(v[p + '_exakt_luecke_mittel'])} % über der unteren) werden im Mittel {de(v[p + '_exakt_gestrichen_mittel'], 0)} % der Kanten "
                          f"mit zulässiger Route gestrichen, die Vorwärtslabels sinken auf das {de(v[p + '_exakt_labels_mittel'], 2)}-Fache ({v[p + '_exakt_instanzen']} Instanzen)."),
        _beleg("ksp_n30", f"Mit einer oberen Schranke nur aus den Spalten der Spaltenerzeugung (im Mittel {de(v[p + '_spalten_luecke_mittel'])} % über der unteren) sind es {de(v[p + '_spalten_gestrichen_mittel'], 0)} % der Kanten "
                          f"und das {de(v[p + '_spalten_labels_mittel'], 2)}-Fache der Labels."),
    )
    hin = ["Die Wirkung ist nur bei den Dualpreisen der Konvergenz der Spaltenerzeugung gemessen; der Nutzen in späteren Pricing-Aufrufen (nach Verzweigen oder Schnitten) ist nicht gemessen.",
           "Gezählt sind nur Vorwärtslabels im gestrichenen gegen den vollen Graphen; die Rückwärtslabels und das Verbinden, die für die Kantenwerte nötig sind, sind nicht eingerechnet.",
           "Je besser die obere Schranke, desto mehr Kanten fallen weg; die „exakte Lücke“ nimmt das ganzzahlige Optimum selbst als obere Schranke, die man in der Praxis nicht hat."] + _k_hinweis(a, "ksp_n30")
    return Stufe("kanten", titel, "moeglich",
                 f"Gemessen bei den Dualpreisen der Konvergenz: Mit dem ganzzahligen Optimum als oberer Schranke entfallen im Mittel {de(v[p + '_exakt_gestrichen_mittel'], 0)} % der Kanten, die Vorwärtslabels sinken auf das {de(v[p + '_exakt_labels_mittel'], 2)}-Fache; "
                 f"mit einer Schranke nur aus den Spalten {de(v[p + '_spalten_gestrichen_mittel'], 0)} % und das {de(v[p + '_spalten_labels_mittel'], 2)}-Fache. Die Kosten der Kantenwerte und der Nutzen in späteren Aufrufen sind nicht gemessen.",
                 belege, tuple(hin))


def stufe_heuristik(a: Aufgabe) -> Stufe:
    """Heuristisches Pricing (Etikettenlimit, exakt nur zum Beweis)."""
    titel = "Heuristisches Pricing (Etikettenlimit, exakt nur zum Beweis)"
    z100, z150, zt = D.zeile("hpr_labels_b100"), D.zeile("hpr_labels_b150"), D.zeile("hpr_zeit")
    if not (D.im_bereich(z100, a.n, a.breite, a.typ) or D.im_bereich(z150, a.n, a.breite, a.typ)):
        return _ungemessen("heuristik", titel, "hpr_labels_b100")
    if not a.pricing_dominiert:
        return Stufe("heuristik", titel, "nicht_gemessen",
                     "Der Zeitgewinn ist nur gemessen, wo das Pricing den Großteil der CPU-Zeit ausmacht "
                     f"({de(zt['werte']['pricing_anteil_exakt'])} % bei immer exaktem Pricing). Ohne diese Voraussetzung ist er nicht gemessen und der Baustein wird nicht empfohlen.", (),
                     (f"Quelle: {D.quelle_text(zt)}.",))
    zl = z100 if D.im_bereich(z100, a.n, a.breite, a.typ) else z150
    v = zl["werte"]
    labels = " / ".join(de(v[f"L{L}_labels"], 2) for L in (5, 10, 20))
    iters = " / ".join(f"+{de(v[f'L{L}_iterationen_plus'], 0)}" for L in (5, 10, 20))
    belege = [
        _beleg(zl["id"], f"Labels im Verhältnis zum immer exakten Pricing: {labels} (Limit 5 / 10 / 20); in {v['L5_weniger_labels']} von {v['instanzen']} Instanzen weniger Labels (Limit 5); "
                         f"Endschranke gleich in {v['schranke_gleich']} von {v['instanzen']} Instanzen."),
        _beleg(zl["id"], f"Preis: mehr Runden (Master-Aufgaben), {iters} % (Limit 5 / 10 / 20)."),
    ]
    hin = []
    if zl["id"] == "hpr_labels_b100":
        t = zt["werte"]
        belege.append(_beleg("hpr_zeit", f"CPU-Zeit im Verhältnis zum immer exakten Pricing: {de(t['l5_cpu_verhaeltnis'], 2)} / {de(t['l10_cpu_verhaeltnis'], 2)} / {de(t['l20_cpu_verhaeltnis'], 2)}; "
                                         f"das Pricing macht dort {de(t['pricing_anteil_exakt'])} % der CPU-Zeit aus."))
        hin.append("Die Zeitmessung ist bei ausgelastetem Rechner entstanden, nur eine Größenordnung und nicht mit dem Kern der Quell-Demo neu gemessen; bei einem teureren Master wäre der Gewinn kleiner.")
        hin.append("Die Quell-Demo sagt ausdrücklich, dass die Aussage „heuristisches Pricing ist schneller“ dort nicht steht: Gemessen ist nur diese CPU-Zeit unter diesen Voraussetzungen (Breite 100, ng k = 8, Pricing überwiegt, ein Master-LP kostet etwa 380 Labels).")
        status = "moeglich"
        text = (f"Gemessen (30 Kunden, ng k = 8, Breite 100): Etikettenlimit statt immer exaktem Pricing, {labels} der Labels (Limit 5 / 10 / 20, Mittel der Instanz-Verhältnisse), {iters} % Runden; "
                f"CPU-Zeit {de(t['l5_cpu_verhaeltnis'], 2)} bis {de(t['l20_cpu_verhaeltnis'], 2)} der exakten (Summe über 30 Instanzen, Rechner ausgelastet, nur Größenordnung), "
                f"weil das Pricing dort {de(t['pricing_anteil_exakt'])} % der CPU-Zeit ausmacht und ein Master-LP nur etwa 380 Labels kostet.")
    else:
        hin.append("Für Breite 150 ist die Zeit nicht gemessen, nur Labels und Runden.")
        status, text = "moeglich", f"Gemessen (30 Kunden, ng k = 8, Breite 150): Etikettenlimit erzeugt {labels} der Labels (Limit 5 / 10 / 20, Mittel der Instanz-Verhältnisse) und kostet Runden ({iters} %); die Zeit ist bei dieser Breite nicht gemessen."
    hin += _k_hinweis(a, zl["id"])
    return Stufe("heuristik", titel, status, text, tuple(belege), tuple(hin))


def stufe_eimer(a: Aufgabe) -> Stufe:
    """Eimer für die Dominanzprüfung: letzte Stufe der Beschleuniger."""
    titel = "Eimer für die Dominanzprüfung"
    z = D.zeile("eml_v10")
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("eimer", titel, "eml_v10")
    v = z["werte"]
    belege = (
        _beleg("eml_v10", f"Das Ergebnis bleibt gleich; Zeit-Eimer sparen im Median {de(v['zeit_ersparnis_min'])} bis {de(v['zeit_ersparnis_max'])} % der Dominanzvergleiche, Last-Eimer {de(v['last_ersparnis_min'])} bis {de(v['last_ersparnis_max'])} %."),
        _beleg("eml_v10", f"Netto nach Verwaltung (angenommenes Gewicht 0,1 je Eimerschritt): Zeit-Eimer der Breite 20 bis 80 sparen {de(v['zeit_netto_min'])} bis {de(v['zeit_netto_max'])} %, "
                          f"Last-Eimer {de(v['last_netto_min'])} bis {de(v['last_netto_max'])} %; Zeit-Eimer der Breite 1 bis 10 kosten netto mehr als gar keine."),
    )
    hin = ["Das Verwaltungsgewicht ist eine Annahme, keine Messung.",
           "Gemessen sind hier nur Dualpreise am Ende der Spaltenerzeugung (40 Läufe je Kapazität von 320 Läufen der Quell-Reihe); die Werte der Runden 1, 3 und 8 sind nicht übernommen.",
           "In Python ändert sich die Laufzeit mit Eimern kaum (Median-Verhältnisse 0,86 bis 1,10 in der Quell-Demo, Rechner ausgelastet)."] + _k_hinweis(a, "eml_v10")
    return Stufe("eimer", titel, "moeglich",
                 f"Gemessen (30 Kunden, ng k = 5, Dualpreise am Ende der Spaltenerzeugung): Netto sparen Zeit-Eimer {de(v['zeit_netto_min'])} bis {de(v['zeit_netto_max'])} % und Last-Eimer {de(v['last_netto_min'])} bis {de(v['last_netto_max'])} % des Aufwands "
                 "(Dominanzvergleiche plus 0,1 je Eimerschritt, Gewicht angenommen).", belege, tuple(hin))


def stufe_k_zyklen(a: Aufgabe) -> Stufe:
    titel = "k-Zyklen statt ng-Gedächtnis"
    z = D.zeile("ngr_kzyklen")
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("kzyklen", titel, "ngr_kzyklen")
    v = z["werte"]
    return Stufe(
        "kzyklen", titel, "nicht_empfohlen",
        f"k-Zyklen (K = 2) erzeugen das {de(v['kcyc2_labels_verhaeltnis'], 2)}-Fache der Labels von ng k = 8 und liefern eine Schranke {de(v['kcyc2_luecke_mittel'], 3)} % darunter; ng k = 5 liegt bei dem {de(v['ng5_labels_verhaeltnis'], 2)}-Fachen der Labels nur {de(v['ng5_luecke_mittel'], 3)} % darunter.",
        (_beleg("ngr_kzyklen", f"K = 3: {v['kcyc3_abgebrochen']} von {v['kcyc3_instanzen']} Läufen abgebrochen, K = 4: {v['kcyc4_abgebrochen']} von {v['kcyc4_instanzen']}; Labels im Verhältnis zu ng k = 8: {de(v['kcyc3_labels_verhaeltnis'], 2)} (K = 3), {de(v['kcyc4_labels_verhaeltnis'], 2)} (K = 4)."),),
        ("Gemessen ist die eigene Dominanzregel der Quell-Demo, nicht die von Irnich und Villeneuve (2006); die Aussage gilt für diese Regel.",))


def stufe_dssr(a: Aufgabe) -> Stufe:
    titel = "DSSR statt ng-Gedächtnis"
    z = D.zeile("ngr_dssr")
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("dssr", titel, "ngr_dssr")
    v = z["werte"]
    return Stufe(
        "dssr", titel, "nicht_empfohlen",
        f"DSSR braucht im Mittel der Verhältnisse das {de(v['labels_dssr_zu_ng5'])}-Fache der Labels von ng k = 5, am Ende der Spaltenerzeugung das {de(v['labels_dssr_zu_ng5_ende'])}-Fache; "
        f"ng k = 5 verfehlt den besten Weg in {v['ng5_verfehlt']} von {v['saetze']} Sätzen, am Ende in {v['ng5_verfehlt_ende']} von {v['saetze_ende']} (ein schwacher Test, weil dort der ng-Master schon konvergiert ist).",
        (_beleg("ngr_dssr", f"ng k = 5 verfehlt den besten Weg in {v['ng5_verfehlt']} von {v['saetze']} Sätzen, am Ende der Spaltenerzeugung in {v['ng5_verfehlt_ende']} von {v['saetze_ende']}; DSSR stimmt in {v['dssr_gleich_elementar']} von {v['saetze_mit_elementar']} Sätzen mit fertiger elementarer Rechnung überein."),),
        ("Gemessen sind nur drei Stellen der Spaltenerzeugung (Runde 2, Runde 4, Ende), je Pricing-Aufruf und nicht in der Schleife; das Verhältnis ist ein Mittel der Verhältnisse je Satz; eigene Variante nach dem Abstract von Righini und Salani (2008).",))


def stufe_glaettung(a: Aufgabe) -> Stufe:
    titel = "Glättung der Dualpreise"
    z = D.zeile("pdp_glaettung")
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("glaettung", titel, "pdp_glaettung")
    v = z["werte"]
    return Stufe(
        "glaettung", titel, "nicht_empfohlen",
        f"Die einfache Glättung spart bei α = 0,8 und 0,9 keine Runden: im Mittel {de(v['runden_mittel_a0'])} Runden ohne Glättung gegen {de(v['runden_mittel_a80'])} (α = 0,8) und {de(v['runden_mittel_a90'])} (α = 0,9); "
        f"bei α = 0,5 sind es etwa gleich viele ({de(v['runden_mittel_a50'])}).",
        (_beleg("pdp_glaettung", f"Bei α = 0,8 und 0,9 brauchten {v['mehr_runden_a80']} bzw. {v['mehr_runden_a90']} von {v['instanzen']} Instanzen mehr Runden als ohne Glättung."),),
        ("Gemessen ist nur die einfache Glättung zur Vorrunde, nicht die Verfahren von Wentges oder du Merle u. a.; über Stabilisierung im Allgemeinen sagt die Messung nichts.",))


def stufe_gelernt(a: Aufgabe) -> Stufe:
    titel = "Gelernte Dominanz (nicht gebaut)"
    z = D.zeile("v15_gelernt")
    if not D.im_bereich(z, a.n, a.breite, a.typ):
        return _ungemessen("gelernt", titel, "v15_gelernt")
    v = z["werte"]
    return Stufe(
        "gelernt", titel, "nicht_empfohlen",
        f"Ein Modell trifft „nützlich oder nicht“ mit {de(v['genauigkeit_logreg'])} / {de(v['genauigkeit_gb'])} % Genauigkeit, die Mehrheitsklasse allein mit {de(v['mehrheitsklasse'])} %.",
        (_beleg("v15_gelernt", f"Vor der Dominanzprüfung ließen sich {de(v['gestrichen_gb'])} % der Labels streichen, ohne dass der beste Weg in {v['aufrufe']} Testaufrufen verloren ging (Schwelle 0,01); bei Schwelle 0,05 ging der beste Weg in {v['zerstoerte_aufrufe_005']} von {v['aufrufe']} Aufrufen verloren."),),
        (f"Nur {v['testinstanzen']} Testinstanzen (Training an 20 anderen), nur Breite 100 und ng k = 8; „kein Verlust in {v['aufrufe']} Aufrufen“ ist nach der Vormessung mit Verlustanteilen bis etwa 10 % verträglich (95-%-Niveau, nicht geprüft). Die Spaltenerzeugung mit Modell ist nicht gerechnet, die Rechenzeit des Modells nicht gemessen; kein Baustein dieser Linie.",
         *_k_hinweis(a, "v15_gelernt")))


def stufe_master(a: Aufgabe) -> Stufe:
    """Von der Schranke zur ganzen Lösung: Einordnung der Master-Seite (nicht gebaut, nicht gemessen)."""
    z = D.zeile("crew_pairing")
    v = z["werte"]
    return Stufe(
        "master", "Von der Schranke zur ganzen Lösung", "befund",
        f"Das Pricing liefert die untere Schranke, nicht die ganzzahlige Lösung. Im Fall der Besatzungsplanung liegt die ganzzahlige Lösung {de(v['luecke_3'])} / {de(v['luecke_4'])} / {de(v['luecke_5'])} % über der Schranke (3 / 4 / 5 Züge).",
        (_beleg("crew_pairing", f"Größte Lücke in einem Netz: {de(v['max_3'])} / {de(v['max_4'])} / {de(v['max_5'])} %; das Pricing braucht {v['pricing_3']} / {v['pricing_4']} / {v['pricing_5']} % der Rechenzeit der Spaltengenerierung."),),
        ("Der Abstand besteht aus der Ganzzahligkeitslücke und der Wahl unter den erzeugten Spalten (in `crew-pairing-demo` fehlt ein Branch-and-Price): Er ist eine obere Grenze der Ganzzahligkeitslücke und enthält eine Wirkung des Pricings.",
         "Verzweigung, Schnitte und Pfadaufzählung baut diese Reihe nicht und misst sie nicht; die Karten dazu stehen im vierten Abschnitt der App."))


STUFEN = (stufe_grundlage, stufe_groesse, stufe_elementar, stufe_k, stufe_grenzen, stufe_bidirektional, stufe_kanten, stufe_heuristik, stufe_eimer,
          stufe_k_zyklen, stufe_dssr, stufe_glaettung, stufe_gelernt, stufe_master)


def baum(a: Aufgabe) -> list:
    """Alle Stufen für die Aufgabe, in der Reihenfolge, in der man die Bausteine zuschaltet."""
    return [f(a) for f in STUFEN]


def empfohlene_reihenfolge(stufen: list) -> list:
    """Die Stufen, deren Baustein die Aufgabe bekommt (empfohlen oder möglich), in Reihenfolge."""
    return [s for s in stufen if s.status in EMPFOHLEN]
