"""Auswertung: Tabellen und Verdikte aus dem Entscheidungsbaum und den Messdaten (reine Funktionen, keine Streamlit-Aufrufe).

Jede Zahl in einem Verdikt kommt aus `data/*.json` bzw. wird hier aus den Zellen der Auswahlregel gezählt; kein Wert ist von Hand eingetragen."""

from collections import Counter
from dataclasses import dataclass

import pvw_algorithm as A
import pvw_baum as B
import pvw_constants as C
import pvw_daten as D
from pvw_daten import de


@dataclass(frozen=True)
class Settings:
    """Die Regler der Aufgabe (Namen wie die Schlüssel im Session State ohne Präfix „a_“)."""
    n: int
    breite: int
    typ: str
    r: int
    ub: bool
    pricing: bool
    tau_mittel: float
    tau_max: float

    def aufgabe(self) -> B.Aufgabe:
        return B.Aufgabe(self.n, self.breite, self.typ, self.r, self.ub, self.pricing, self.tau_mittel, self.tau_max)


def zusammenfassung(stufen: list) -> list:
    """Eine Zeile je Stufe: Nummer, Baustein, Status, Kurzfassung (für die Übersichtstabelle)."""
    return [{"Nr.": i + 1, "Stufe": s.titel, "Status": B.STATUS[s.status], "Ergebnis": s.empfehlung} for i, s in enumerate(stufen)]


def verdict_baum(stufen: list) -> tuple:
    """(Art, Text) des Verdikts über den ganzen Baum: wie viele Stufen empfohlen, nicht gemessen usw. sind."""
    zaehl = Counter(s.status for s in stufen)
    n_emp = zaehl["empfohlen"] + zaehl["moeglich"]
    teile = [f"{len(stufen)} Stufen, davon: Grundlage {zaehl['grundlage']}; empfohlen oder möglich {n_emp}; nicht empfohlen (mit Messzahl) {zaehl['nicht_empfohlen']}; "
             f"nicht nötig oder nicht anwendbar {zaehl['nicht_noetig'] + zaehl['nicht_anwendbar']}; nicht gemessen {zaehl['nicht_gemessen']}; Befund {zaehl['befund']}."]
    anderes_k = any("nicht eigens gemessen" in h for s in stufen if s.status in B.EMPFOHLEN for h in s.hinweise)
    if anderes_k:
        teile.append("Die Messungen der Beschleuniger gelten bei ihrem eigenen ng-Gedächtnis (k = 5 oder 8), nicht bei dem k, das die Auswahlregel für diese Aufgabe nennt (siehe die Hinweise der Stufen).")
    nachsatz = " ".join(teile[1:])
    if zaehl["nicht_gemessen"] >= len(stufen) // 2:
        return "warning", "Für diese Aufgabe fehlen Messungen: " + teile[0] + " Ein Baustein ohne Messung wird nicht empfohlen." + (" " + nachsatz if nachsatz else "")
    if zaehl["nicht_gemessen"]:
        return "info", teile[0] + " Wo „nicht gemessen“ steht, wird der Baustein nicht empfohlen." + (" " + nachsatz if nachsatz else "")
    return "success", teile[0] + (" " + nachsatz if nachsatz else "")


def k_wahl_je_zelle(tau_mittel: float, tau_max: float) -> list:
    """Für jede Zelle: Zelle und Wahl der Auswahlregel bei den gegebenen Schwellen."""
    return [(z, A.waehle_k(z, tau_mittel, tau_max)) for z in D.k_zellen()]


def k_uebersicht(tau_mittel: float, tau_max: float) -> list:
    """Zeilen der Zellentabelle (Experiment 2): Zelle, Bezug, gewähltes k, Lücke Mittel und Maximum, Labels im Verhältnis zum Bezug."""
    zeilen = []
    for z, w in k_wahl_je_zelle(tau_mittel, tau_max):
        zeilen.append({
            "Aufgabe": f"{z['n']} Kunden, Breite {z['breite']}, {z['typ']}",
            "Bezug": "elementar" if z["bezug"] == z["n"] else f"k = {z['bezug']}",
            "Instanzen": w.instanzen,
            "gewähltes k": w.k,
            "Lücke Mittel (%)": round(w.luecke_mittel, 3),
            "Lücke Maximum (%)": round(w.luecke_max, 3),
            "Labels im Verhältnis zum Bezug": round(w.labels_verhaeltnis, 2),
            "Hinweis": ("kein kleineres k erfüllt die Schwellen" if w.kein_kleineres_k else ("jedes k gleich" if A.alle_gleich(z) else "")),
        })
    return zeilen


def k_detail(zelle: dict) -> list:
    """Zeilen je k einer Zelle: mittlere und größte Lücke, Median der Labels, Instanzen."""
    return [{"k": ("elementar" if t.k == zelle["n"] else t.k), "Lücke Mittel (%)": round(t.luecke_mittel, 3), "Lücke Maximum (%)": round(t.luecke_max, 3),
             "Labels (Median)": round(t.labels_median), "Instanzen": t.instanzen} for t in A.tabelle(zelle)]


def verdict_k(tau_mittel: float, tau_max: float) -> tuple:
    """Verdikt zur Auswahlregel: Zahl der Zellen je gewähltem k, Zahl der Zellen mit gleichen Schranken für alle k."""
    paare = k_wahl_je_zelle(tau_mittel, tau_max)
    zaehl = Counter(w.k for _, w in paare)
    je_k = ", ".join(f"k = {k} in {zaehl[k]}" for k in sorted(zaehl))
    gleich = [z for z, _ in paare if A.alle_gleich(z)]
    kein = sum(1 for _, w in paare if w.kein_kleineres_k)
    text = (f"Bei {de(tau_mittel, 2)} % im Mittel und {de(tau_max, 2)} % im Einzelfall wählt die Regel in den {len(paare)} Zellen: {je_k} (jeweils Zahl der Zellen). "
            f"In {len(gleich)} Zellen liegt die Schranke für jedes k gleich hoch (Breite 20 bei 100 Kunden)")
    text += f"; in {kein} Zellen erfüllt kein kleineres k als der Bezug die Schwellen." if kein else "; in keiner Zelle bleibt nur der Bezug selbst übrig."
    return ("warning" if kein else "info"), text


# ---------------------------------------------------------------------------------------------------------------------------------------
# Was jeder Baustein kostet (Experiment 3)
# ---------------------------------------------------------------------------------------------------------------------------------------

def bausteine_tabelle() -> list:
    """Eine Zeile je Baustein: Wirkung (Labels), Preis, gemessener Bereich, Quelle; dazu die Zahl, nach der man sortieren kann (Labels im Verhältnis zur Vergleichsvariante)."""
    dml, mgr, bdl, ksp = D.zeile("dml_regeln"), D.zeile("mgr_v11"), D.zeile("bdl_v9"), D.zeile("ksp_n30")
    hpr, hz, eml, epr = D.zeile("hpr_labels_b100"), D.zeile("hpr_zeit"), D.zeile("eml_v10"), D.zeile("epr_abbrueche")
    gross, kip, kz, dssr, pdp, v15 = D.zeile("ngr_elementar_gross"), D.zeile("kip_luecke"), D.zeile("ngr_kzyklen"), D.zeile("ngr_dssr"), D.zeile("pdp_glaettung"), D.zeile("v15_gelernt")
    zelle50 = D.k_zelle(50, 100, "zufällig")
    t50 = {t.k: t for t in A.tabelle(zelle50)}
    ksp_cells = [k for k in ksp["werte"] if k.endswith("_exakt_labels_mittel")]
    ksp_min, ksp_max = min(ksp["werte"][k] for k in ksp_cells), max(ksp["werte"][k] for k in ksp_cells)
    ksp_g = [ksp["werte"][k] for k in ksp["werte"] if k.endswith("_exakt_gestrichen_mittel")]
    mg, bv, hv, ev = mgr["werte"], bdl["werte"], hpr["werte"], eml["werte"]

    def zeile(name, demo, wirkung, preis, z, verhaeltnis=None, vergleich="", zusatz=None, bereich=None):
        quelle = D.quelle_text(z) if zusatz is None else zusatz
        return {
            "Baustein": name, "Demo der Reihe": demo, "Wirkung": wirkung, "Preis": preis, "Gemessen bei": bereich or B._bereich_text(z),
            "Labels im Verhältnis": verhaeltnis, "Verhältnis zu": vergleich, "Quelle": quelle,
        }

    return [
        zeile("Dominanz über alle Ressourcen", "dominanz-labels-demo",
              f"Ohne Dominanz im Median das {de(dml['werte']['faktor_ohne_dominanz_median'], 2)}-Fache der Labels; nur nach Kosten verfehlt sie den besten Weg in {dml['werte']['verfehlt_nur_kosten']} von {dml['werte']['faelle']} Fällen (7 Kunden)",
              f"{de(mg['r1_vergleiche_je_label_median'])} Vergleiche je Label bei nur der Zeit als Grenze (30 Kunden, Breite 100, ng k = 1; mehrere-grenzen-demo)", dml),
        zeile("ng-Gedächtnis k = 5 statt k = 1", "ng-routen-demo",
              f"Schranke höher: k = 1 liegt bei 50 Kunden, Breite 100, zufällig im Mittel {de(t50[1].luecke_mittel, 2)} % unter dem Bezug k = 16, k = 5 nur {de(t50[5].luecke_mittel, 2)} %",
              f"Das {de(t50[5].labels_median / t50[1].labels_median, 2)}-Fache der Labels von k = 1 (Median)", zelle50, t50[5].labels_median / t50[1].labels_median, "ng k = 1",
              zusatz=f"{zelle50['quelle']['demo']}, {zelle50['quelle']['datei']}", bereich="50 Kunden, Breite 100, zufällig, 12 Instanzen"),
        zeile("Kreise erlauben (k = 1) statt elementar", "kreise-im-pricing-demo",
              f"Weniger Labels, aber eine tiefere Schranke: bei Breite 100 im Mittel {de(kip['werte']['b100_mittel'], 2)} % unter der elementaren (größte {de(kip['werte']['b100_max'], 2)} %), bei Breite 40 {de(kip['werte']['b40_mittel'], 2)} %",
              "Elementare Läufe brechen ab: siehe nächste Zeile", kip),
        zeile("Elementar rechnen", "elementar-pricing-demo",
              "Schranke ohne Kreise, kein Kunde doppelt",
              f"Abgebrochene Läufe: Breite 100 bei 30 Kunden {epr['werte']['neu_b100_abgebrochen']} von {epr['werte']['neu_b100_laeufe']}, bei 50 und 100 Kunden {gross['werte']['abgebrochen']} von {gross['werte']['laeufe']}", epr),
        zeile("Mehr Ressourcengrenzen", "mehrere-grenzen-demo",
              f"Kein Beschleuniger: Der Anteil dominierter Labels sinkt von {de(mg['r1_dominiert_median'])} auf {de(mg['r4_dominiert_median'])} % (1 bis 4 Grenzen)",
              f"Vergleiche je Label von {de(mg['r1_vergleiche_je_label_median'])} auf {de(mg['r4_vergleiche_je_label_median'])}", mgr),
        zeile("Bidirektional (Halbweg H/2)", "bidirektional-labeling-demo",
              f"Im Median das {de(bv['verhaeltnis_median'], 2)}-Fache der Labels ({de(bv['verhaeltnis_min'], 2)} bis {de(bv['verhaeltnis_max'], 2)}), weniger Labels in {bv['weniger_labels']} von {bv['laeufe']} Läufen",
              f"Verbindungspaare im Median das {de(bv['paare_je_label_median'])}-Fache der einseitigen Label-Zahl", bdl, bv["verhaeltnis_median"], "einseitiges Labeling"),
        zeile("Kantenstreichung", "kantenstreichung-pricing-demo",
              f"Bei exakter Lücke das {de(ksp_min, 2)}- bis {de(ksp_max, 2)}-Fache der Vorwärtslabels, {de(min(ksp_g), 0)} bis {de(max(ksp_g), 0)} % der Kanten gestrichen (Mittel je Zelle)",
              "Setzt eine obere Schranke voraus; nur bei den Dualpreisen der Konvergenz gemessen", ksp, ksp_min, "voller Graph (kleinster Zellenmittelwert)"),
        zeile("Heuristisches Pricing (Limit 5 / 10 / 20)", "heuristisches-pricing-demo",
              f"{de(hv['L5_labels'], 2)} / {de(hv['L10_labels'], 2)} / {de(hv['L20_labels'], 2)} der Labels bei gleicher Endschranke in {hv['schranke_gleich']} von {hv['instanzen']} Instanzen; CPU-Zeit {de(hz['werte']['l5_cpu_verhaeltnis'], 2)} / {de(hz['werte']['l10_cpu_verhaeltnis'], 2)} / {de(hz['werte']['l20_cpu_verhaeltnis'], 2)}",
              f"Mehr Runden: +{de(hv['L5_iterationen_plus'], 0)} / +{de(hv['L10_iterationen_plus'], 0)} / +{de(hv['L20_iterationen_plus'], 0)} %", hpr, hv["L5_labels"], "immer exaktes Pricing (Limit 5)"),
        zeile("Eimer", "eimer-labeling-demo",
              f"Gleiches Ergebnis, {de(ev['zeit_ersparnis_min'])} bis {de(ev['zeit_ersparnis_max'])} % weniger Dominanzvergleiche (Zeit-Eimer), {de(ev['last_ersparnis_min'])} bis {de(ev['last_ersparnis_max'])} % (Last-Eimer)",
              f"Verwaltung: netto {de(ev['zeit_netto_min'])} bis {de(ev['zeit_netto_max'])} % bzw. {de(ev['last_netto_min'])} bis {de(ev['last_netto_max'])} % (Gewicht 0,1 angenommen)", eml),
        zeile("k-Zyklen statt ng (nicht empfohlen)", "ng-routen-demo",
              f"Schranke {de(kz['werte']['kcyc2_luecke_mittel'], 3)} % unter ng k = 8 (K = 2); ng k = 5 liegt {de(kz['werte']['ng5_luecke_mittel'], 3)} % darunter",
              f"Das {de(kz['werte']['kcyc2_labels_verhaeltnis'], 2)}-Fache der Labels von ng k = 8 (ng k = 5: {de(kz['werte']['ng5_labels_verhaeltnis'], 2)})", kz, kz["werte"]["kcyc2_labels_verhaeltnis"], "ng k = 8"),
        zeile("DSSR statt ng (nicht empfohlen)", "ng-routen-demo",
              f"Findet den exakten Weg; ng k = 5 verfehlt ihn in {dssr['werte']['ng5_verfehlt']} von {dssr['werte']['saetze']} Sätzen, am Ende der Spaltenerzeugung in {dssr['werte']['ng5_verfehlt_ende']}",
              f"Das {de(dssr['werte']['labels_dssr_zu_ng5'])}-Fache der Labels von ng k = 5", dssr, dssr["werte"]["labels_dssr_zu_ng5"], "ng k = 5"),
        zeile("Glättung der Dualpreise (nicht empfohlen)", "pricing-dualpreise-demo",
              f"Keine Ersparnis: {de(pdp['werte']['runden_mittel_a0'])} Runden ohne, {de(pdp['werte']['runden_mittel_a90'])} mit α = 0,9",
              f"Mehr Runden bei α = 0,8 in {pdp['werte']['mehr_runden_a80']} von {pdp['werte']['instanzen']} Instanzen", pdp),
        zeile("Gelernte Dominanz (nicht gebaut)", "Vormessung",
              f"{de(v15['werte']['gestrichen_gb'])} % der Labels streichbar, ohne dass der beste Weg in {v15['werte']['aufrufe']} Testaufrufen verloren ging (Schwelle 0,01)",
              f"Bei Schwelle 0,05 geht der beste Weg in {v15['werte']['zerstoerte_aufrufe_005']} von {v15['werte']['aufrufe']} Aufrufen verloren; Genauigkeit {de(v15['werte']['genauigkeit_gb'])} % gegen {de(v15['werte']['mehrheitsklasse'])} % der Mehrheitsklasse", v15),
    ]


def verdict_kosten(zeilen: list) -> tuple:
    """Verdikt zur Tabelle: wie viele Bausteine weniger Labels als ihre Vergleichsvariante brauchen und wie viele mehr (nur Zeilen mit Verhältnis)."""
    mit = [z for z in zeilen if z["Labels im Verhältnis"] is not None]
    weniger = [z["Baustein"] for z in mit if z["Labels im Verhältnis"] < 1]
    mehr = [z["Baustein"] for z in mit if z["Labels im Verhältnis"] > 1]
    return "info", (f"In {len(weniger)} von {len(mit)} Zeilen mit Verhältnis erzeugt der Baustein weniger Labels als seine Vergleichsvariante, in {len(mehr)} mehr. "
                    "Die Vergleichsvariante ist je Zeile eine andere; jede Zeile hat ihren Preis (Verbindungspaare, obere Schranke, Runden, Verwaltung). "
                    "Je Zeile ist ein einzelner Wert gewählt (Kantenstreichung: der kleinste Zellenmittelwert bei exakter Lücke, Limit: Limit 5); die Zählung vergleicht nur die Richtung, nicht die Größe.")
