"""Jede Zahl der README („Befunde“, Kernfrage, Korrekturen): Der Test bildet den Satz aus den Daten in `data/` und prüft, dass er wörtlich in der README steht.

Die Buchstaben A bis K sind die der Spalte „Test“ in der README. Nichts hier ist von Hand abgeschrieben: Jede Zahl wird aus den Messzeilen bzw. den Zellen der Auswahlregel gerechnet
und mit `pvw_daten.de` (Dezimalkomma) formatiert. Zeiten werden nicht festgeschrieben."""

from pathlib import Path

import pytest

import pvw_algorithm as A
import pvw_daten as D
import pvw_evaluation as E
from pvw_daten import de

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")


def im_readme(satz: str):
    assert satz in README, f"nicht in der README: {satz}"


def w(zid, key):
    return D.w(zid, key)


def zelle(n, breite, typ):
    return D.k_zelle(n, breite, typ)


def tab(z):
    return {t.k: t for t in A.tabelle(z)}


def test_a_auswahlregel_an_elf_zellen_bei_den_voreinstellungen():
    paare = E.k_wahl_je_zelle(0.25, 1.0)
    assert len(paare) == 11
    je_k = {k: sum(1 for _, x in paare if x.k == k) for k in (1, 3, 4, 5)}
    assert sum(je_k.values()) == 11
    im_readme(f"k = 1 in {je_k[1]} Zellen, k = 3 in {je_k[3]}, k = 4 in {je_k[4]}, k = 5 in {je_k[5]}")
    wahl = {(z["typ"], z["n"], z["breite"]): x for z, x in paare}
    # Zeilen der Tabelle: k = 3 bei Breite 40 (50 und 100 Kunden, beide Verteilungen), k = 5 bei Breite 100 (50 Kunden), k = 1 bei Breite 20 (100 Kunden)
    assert {wahl[(t, n, 40)].k for t in ("zufällig", "gruppiert") for n in (50, 100)} == {3}
    assert {wahl[(t, 50, 100)].k for t in ("zufällig", "gruppiert")} == {5}
    assert {wahl[(t, 100, 20)].k for t in ("zufällig", "gruppiert")} == {1}
    im_readme("k = 3 bei Breite 40 (50 und 100 Kunden, beide Verteilungen), k = 5 bei Breite 100 (50 Kunden), k = 1 bei Breite 20 (100 Kunden)")
    assert (wahl[("zufällig", 30, 100)].k, wahl[("gruppiert", 30, 100)].k, wahl[("zufällig", 30, 40)].k) == (4, 5, 1)
    im_readme("k = 4 (zufällig) und k = 5 (gruppiert)")
    im_readme("bei 30 Kunden, Breite 40, zufällig (6 Instanzen, Bezug elementar): k = 1")
    assert wahl[("zufällig", 30, 40)].instanzen == 6 and zelle(30, 40, "zufällig")["bezug"] == 30
    assert all(wahl[k].instanzen == 12 and wahl[k].bezug == 16 for k in wahl if k[1] in (50, 100))
    assert all(wahl[(t, 30, 100)].instanzen == 12 and wahl[(t, 30, 100)].bezug == 8 for t in ("zufällig", "gruppiert"))
    # Kernfrage: bei Breite 40 in 4 von 5 Zellen k = 3 (in der fünften k = 1), bei Breite 100 in 4 von 4 Zellen k = 4 oder 5
    b40 = [x.k for (t, n, b), x in wahl.items() if b == 40]
    b100 = [x.k for (t, n, b), x in wahl.items() if b == 100]
    assert (len(b40), b40.count(3), b40.count(1)) == (5, 4, 1) and (len(b100), sum(1 for k in b100 if k in (4, 5))) == (4, 4)
    im_readme("bei Breite 40 wählt die Regel in 4 von 5 Zellen k = 3 (in der fünften k = 1), bei Breite 100 in 4 von 4 Zellen k = 4 oder 5")
    # Labels im Verhältnis zum Bezug
    v8 = [x.labels_verhaeltnis for (t, n, b), x in wahl.items() if n in (50, 100)]
    assert len(v8) == 8
    im_readme(f"{de(min(v8), 2)} bis {de(max(v8), 2)} in den 8 Zellen mit 50 und 100 Kunden")
    im_readme(f"{de(wahl[('zufällig', 30, 100)].labels_verhaeltnis, 2)} (zufällig) und {de(wahl[('gruppiert', 30, 100)].labels_verhaeltnis, 2)} (gruppiert) bei 30 Kunden und Breite 100")
    im_readme(f"{de(wahl[('zufällig', 30, 40)].labels_verhaeltnis, 2)} bei 30 Kunden und Breite 40 (zufällig)")


def test_b_alle_k_gleich_und_die_luecke_von_k_1():
    gleich = [z for z in D.k_zellen() if A.alle_gleich(z)]
    assert {(z["n"], z["breite"]) for z in gleich} == {(100, 20)} and len(gleich) == 2
    assert all(len(A.luecken(z, 1)) == 12 for z in gleich)
    assert sum(1 for z in D.k_zellen() if not A.alle_gleich(z)) == 9
    im_readme("in jeder der 24 Instanzen (2 Zellen mit je 12) gleich hoch wie bei k = 16")
    im_readme("In keiner der 9 anderen Zellen ist das so.")
    g, z_ = tab(zelle(50, 100, "gruppiert"))[1], tab(zelle(50, 100, "zufällig"))[1]
    im_readme(f"Mittlere Lücke bei 50 Kunden und Breite 100: {de(g.luecke_mittel, 2)} % (gruppiert, größte Instanz {de(g.luecke_max, 2)} %) und {de(z_.luecke_mittel, 2)} % (zufällig, {de(z_.luecke_max, 2)} %)")
    a, b = tab(zelle(100, 40, "gruppiert"))[1], tab(zelle(100, 40, "zufällig"))[1]
    im_readme(f"bei 100 Kunden und Breite 40: {de(a.luecke_mittel, 2)} % und {de(b.luecke_mittel, 2)} %")


def test_c_elementare_rechnung():
    kl, gr, ep = D.zeile("ngr_elementar_klein")["werte"], D.zeile("ngr_elementar_gross")["werte"], D.zeile("epr_abbrueche")["werte"]
    im_readme(f"{kl['abgebrochen']} von {kl['laeufe']} Läufen abgebrochen")
    im_readme(f"Breite 40 {ep['neu_b40_abgebrochen']} von {ep['neu_b40_laeufe']}, Breite 100 {ep['neu_b100_abgebrochen']} von {ep['neu_b100_laeufe']}, Breite 200 {ep['neu_b200_abgebrochen']} von {ep['neu_b200_laeufe']} abgebrochen")
    im_readme(f"frühere Messung {ep['v1_b40_abgebrochen']}, {ep['v1_b100_abgebrochen']} und {ep['v1_b200_abgebrochen']} von 6")
    assert ep["v1_b40_laeufe"] == ep["v1_b100_laeufe"] == ep["v1_b200_laeufe"] == 6
    im_readme(f"{gr['abgebrochen']} von {gr['laeufe']} Läufen abgebrochen")


def test_d_groesse_eines_pricing_aufrufs():
    z = D.zeile("zfl_pricing")["werte"]
    im_readme(f"zufällig {de(z['zufaellig_b20'], 0)} (Breite 20), {de(z['zufaellig_b100'], 0)} (Breite 100) und {de(z['zufaellig_b200'], 0)} (Breite 200); "
              f"gruppiert {de(z['gruppiert_b20'], 0)}, {de(z['gruppiert_b100'], 0)} und {de(z['gruppiert_b200'], 0)}")


def test_e_mehrere_grenzen():
    v = D.zeile("mgr_v11")["werte"]
    dom = " → ".join(de(v[f"r{r}_dominiert_median"]) for r in (1, 2, 3, 4))
    vgl = " → ".join(de(v[f"r{r}_vergleiche_je_label_median"]) for r in (1, 2, 3, 4))
    im_readme(f"Anteil dominierter Labels {dom} %, Vergleiche je Label {vgl}")
    assert all(v[f"r{r}_instanzen"] == 12 for r in (1, 2, 3, 4))


def test_f_bidirektional():
    v = D.zeile("bdl_v9")["werte"]
    assert v["laeufe"] == 480 and v["weniger_labels"] == 480
    im_readme(f"fester Halbweg H/2 im Median das {de(v['verhaeltnis_median'], 2)}-Fache der Labels des einseitigen Laufs (kleinster Wert {de(v['verhaeltnis_min'], 2)}, größter {de(v['verhaeltnis_max'], 2)}), in {v['weniger_labels']} von {v['laeufe']} Läufen weniger")
    assert {v[f"{t}_b{b}_laeufe"] for t in ("zufaellig", "gruppiert") for b in (40, 100)} == {120}
    im_readme(f"zufällig {de(v['zufaellig_b40_median'], 2)} (Breite 40) und {de(v['zufaellig_b100_median'], 2)} (Breite 100); gruppiert {de(v['gruppiert_b40_median'], 2)} und {de(v['gruppiert_b100_median'], 2)}")
    im_readme(f"Verbindungspaare im Median das {de(v['paare_je_label_median'])}-Fache der einseitigen Label-Zahl")
    im_readme(f"erzeugt in {v['dynamisch_besser_als_fest']} von {v['laeufe']} Läufen weniger Labels als der feste (Median {de(v['dynamisch_median'], 2)})")


def test_g_kantenstreichung():
    v = D.zeile("ksp_n30")["werte"]
    zellen = ("zufall_b40", "zufall_b100", "gruppiert_b40", "gruppiert_b100")
    assert all(v[f"{z}_instanzen"] == 12 and v[f"{z}_exakt_instanzen"] == 12 for z in zellen)

    def bereich(suffix, stellen):
        xs = [v[f"{z}_{suffix}"] for z in zellen]
        return f"{de(min(xs), stellen)} bis {de(max(xs), stellen)}"
    im_readme(f"im Mittel je Zelle {bereich('exakt_gestrichen_mittel', 0)} % der Kanten mit zulässiger Route gestrichen, die Vorwärtslabels sinken auf das {bereich('exakt_labels_mittel', 2).replace(' bis ', '- bis ')}-Fache")
    im_readme(f"nur aus den Spalten {bereich('spalten_gestrichen_mittel', 0)} % und das {bereich('spalten_labels_mittel', 2).replace(' bis ', '- bis ')}-Fache")


def test_h_heuristisches_pricing():
    b100, b150, t = D.zeile("hpr_labels_b100")["werte"], D.zeile("hpr_labels_b150")["werte"], D.zeile("hpr_zeit")["werte"]
    assert b100["instanzen"] == 30 and b100["schranke_gleich"] == 30 and b150["instanzen"] == 16
    im_readme(f"Endschranke gleich in {b100['schranke_gleich']} von {b100['instanzen']}, Labels das {de(b100['L5_labels'], 2)}-, {de(b100['L10_labels'], 2)}- und {de(b100['L20_labels'], 2)}-Fache des immer exakten Pricings (Limit 5, 10, 20)")
    im_readme(f"+{de(b100['L5_iterationen_plus'], 0)}, +{de(b100['L10_iterationen_plus'], 0)} und +{de(b100['L20_iterationen_plus'], 0)} % Runden")
    im_readme(f"CPU-Zeit {de(t['l5_cpu_verhaeltnis'], 2)}, {de(t['l10_cpu_verhaeltnis'], 2)} und {de(t['l20_cpu_verhaeltnis'], 2)} der exakten (3 Wiederholungen")
    assert t["wiederholungen"] == 3 and t["instanzen"] == 30
    im_readme(f"weil das Pricing dort {de(t['pricing_anteil_exakt'])} % der CPU-Zeit ausmacht")
    im_readme(f"Bei Breite 150 (16 Instanzen): {de(b150['L5_labels'], 2)}, {de(b150['L10_labels'], 2)} und {de(b150['L20_labels'], 2)} der Labels")


def test_i_eimer():
    v = D.zeile("eml_v10")["werte"]
    assert v["laeufe_gesamt"] == 320 and v["q70_laeufe_ende"] == v["q120_laeufe_ende"] == 40
    im_readme(f"Zeit-Eimer sparen im Median {de(v['zeit_ersparnis_min'])} bis {de(v['zeit_ersparnis_max'])} % der Dominanzvergleiche, Last-Eimer {de(v['last_ersparnis_min'])} bis {de(v['last_ersparnis_max'])} %")
    im_readme(f"{de(v['zeit_netto_min'])} bis {de(v['zeit_netto_max'])} % (Zeit-Eimer der Breite 20 bis 80) und {de(v['last_netto_min'])} bis {de(v['last_netto_max'])} % (Last-Eimer)")


def test_j_nicht_empfohlen():
    kz, ds, gl, ge = D.zeile("ngr_kzyklen")["werte"], D.zeile("ngr_dssr")["werte"], D.zeile("pdp_glaettung")["werte"], D.zeile("v15_gelernt")["werte"]
    im_readme(f"k-Zyklen (K = 2) liegen im Mittel {de(kz['kcyc2_luecke_mittel'], 3)} % der Schranke von ng k = 8 unter dieser Schranke bei dem {de(kz['kcyc2_labels_verhaeltnis'], 2)}-Fachen der Labels, "
              f"ng k = 5 liegt {de(kz['ng5_luecke_mittel'], 3)} % darunter bei dem {de(kz['ng5_labels_verhaeltnis'], 2)}-Fachen; K = 4 brach in {kz['kcyc4_abgebrochen']} von {kz['kcyc4_instanzen']} Läufen ab")
    im_readme(f"DSSR braucht im Mittel der Verhältnisse das {de(ds['labels_dssr_zu_ng5'])}-Fache der Labels von ng k = 5 ({de(ds['labels_dssr_zu_ng5_ende'])}-Fache am Ende der Spaltenerzeugung), "
              f"ng k = 5 verfehlt den besten Weg in {ds['ng5_verfehlt']} von {ds['saetze']} Dualpreis-Sätzen, am Ende in {ds['ng5_verfehlt_ende']} von {ds['saetze_ende']}")
    assert gl["instanzen"] == 6
    im_readme(f"{de(gl['runden_mittel_a0'])} Runden ohne, {de(gl['runden_mittel_a50'])} / {de(gl['runden_mittel_a80'])} / {de(gl['runden_mittel_a90'])} bei α = 0,5 / 0,8 / 0,9")
    assert gl["mehr_runden_a80"] == gl["mehr_runden_a90"] == gl["instanzen"] == 6 and gl["runden_mittel_a50"] < gl["runden_mittel_a0"]
    im_readme("bei α = 0,8 und 0,9 brauchen alle 6 Instanzen mehr Runden, bei α = 0,5 sind es etwa gleich viele")
    im_readme(f"Genauigkeit {de(ge['genauigkeit_logreg'])} / {de(ge['genauigkeit_gb'])} % gegen {de(ge['mehrheitsklasse'])} % der Mehrheitsklasse; {de(ge['gestrichen_gb'])} % der Labels streichbar, ohne dass der beste Weg in {ge['aufrufe']} Testaufrufen verloren ging, "
              f"bei der größeren Schwelle in {ge['zerstoerte_aufrufe_005']} von {ge['aufrufe']} Aufrufen ein Verlust")
    im_readme(f"Training an 20, Test an {ge['testinstanzen']} Instanzen mit 30 Kunden, Breite 100, ng k = 8")
    assert D.zeile("v15_gelernt")["bereich"]["breite"] == [100]


def test_k_schranke_und_ganze_loesung():
    v = D.zeile("crew_pairing")["werte"]
    im_readme(f"im Mittel {de(v['luecke_3'])} / {de(v['luecke_4'])} / {de(v['luecke_5'])} % über der LP-Schranke (größte Lücke eines Netzes {de(v['max_3'])} / {de(v['max_4'])} / {de(v['max_5'])} %)")
    im_readme(f"das Pricing braucht {v['pricing_3']} / {v['pricing_4']} / {v['pricing_5']} % der Rechenzeit der Spaltengenerierung")
    assert v["netze"] == 20


def test_korrekturen_gegenueber_dem_plan_nennen_die_neuen_zahlen():
    v = D.zeile("bdl_v9")["werte"]
    im_readme(f"fester Halbweg im Median {de(v['verhaeltnis_median'], 2)} der Labels (früher 0,28), Verbindungspaare das {de(v['paare_je_label_median'])}-Fache (früher 8,6)")
    k = D.zeile("kip_luecke")["werte"]
    im_readme(f"bei 30 Kunden und Breite 100 im Mittel {de(k['b100_mittel'], 2)} % (früher 4,82 %")
    e = D.zeile("eml_v10")["werte"]
    im_readme(f"Eimer {de(e['zeit_ersparnis_min'])} bis {de(e['zeit_ersparnis_max'])} % (Zeit) und {de(e['last_ersparnis_min'])} bis {de(e['last_ersparnis_max'])} % (Last)")
    ng5 = tab(zelle(30, 100, "zufällig"))[5]
    gepoolt = [g for t in ("zufällig", "gruppiert") for g in A.luecken(zelle(30, 100, t), 5)]
    im_readme(f"ng k = 5 gegen k = 8 bei 30 Kunden im Mittel {de(sum(gepoolt) / len(gepoolt), 3)} % (früher 0,00 / 0,05 / 0,04 % für zufällig / gruppiert / lang, je 5 Instanzen)")
    assert len(gepoolt) == 24 and ng5.instanzen == 12
    im_readme("Die Auswahlregel hat elf Zellen statt acht.")
    assert len(D.k_zellen()) == 11 and len(D.zeile("ngr_kzyklen")["werte"]) > 0


def test_modell_nennt_14_stufen_und_die_reglerwerte():
    import pvw_baum as B
    import pvw_constants as C
    assert len(B.STUFEN) == 14
    im_readme("Der **Baum** besteht aus 14 Stufen")
    im_readme("Kundenzahl (" + ", ".join(str(n) for n in C.N_WERTE) + ")")
    im_readme("Fensterbreite (" + ", ".join(str(b) for b in C.BREITE_WERTE) + " bei einem Horizont von " + str(C.HORIZONT) + ")")
    im_readme(f"(Voreinstellung {de(C.DEFAULT_TAU_MITTEL, 2)} % und {de(C.DEFAULT_TAU_MAX, 0)} %")


def test_instanzzahlen_der_grenzen_und_des_modells():
    """Die Zahl der Instanzen je Zelle in „Ehrliche Grenzen“ und „Bewusst nicht umgesetzt“, die Grenzenstufen im Modell."""
    import pvw_constants as C
    zellen = D.k_zellen()
    zahlen = {len({r["seed"] for r in z["zeilen"]}) for z in zellen}
    assert (min(zahlen), max(zahlen)) == (6, 12) and all(len(z["ks"]) == 6 for z in zellen)
    im_readme("6 bis 12 in den meisten Reihen, 10 beim bidirektionalen Labeling und bei den Eimern, 15 je Typ beim Etikettenlimit (Breite 100; Breite 150: 8 je Typ)")
    im_readme("(11 Zellen, je 6 bis 12 Instanzen und 6 Werte von k)")
    assert "je 10 Instanzen" in D.zeile("bdl_v9")["voraussetzung"] and "je 10 Instanzen" in D.zeile("eml_v10")["voraussetzung"]
    assert (D.w("hpr_labels_b100", "instanzen"), D.w("hpr_labels_b150", "instanzen")) == (2 * 15, 2 * 8)
    assert C.GRENZEN_WERTE == (1, 2, 3, 4)
    im_readme("Zahl der Ressourcengrenzen (1 bis 4, die Zeit zählt mit)")


# ---- Einschränkungen nach der unabhängigen Prüfung ---------------------------------------------------------------------------------------------

def test_kernfrage_behauptet_keine_reihenfolge_und_nennt_die_voraussetzungen():
    im_readme("Aus diesen Messungen folgt keine allgemeine Reihenfolge der Bausteine")
    im_readme("Die Wirkung mehrerer Bausteine zusammen ist nicht gemessen.")
    im_readme("mit den Voreinstellungen der Schwellen (0,25 % im Mittel, 1 % im Einzelfall) gilt: bei Breite 40 wählt die Regel")
    im_readme("erzeugen weniger Labels (bei der Kantenstreichung weniger Vorwärtslabels), jeder mit einem eigenen Preis (Verbindungspaare, eine obere Schranke, mehr Runden); ein Gesamtaufwand ist nicht gemessen")
    im_readme("Die Messungen der Beschleuniger gelten bei ihrem eigenen ng-Gedächtnis (k = 5 oder 8), nicht bei dem k, das die Auswahlregel nennt.")
    # Breite 20 kommt in den Zellen der Auswahlregel nur bei 100 Kunden vor; die Beschleuniger sind nur bei 30 Kunden gemessen
    assert {z["n"] for z in D.k_zellen() if z["breite"] == 20} == {100}
    for zid in ("bdl_v9", "ksp_n30", "hpr_labels_b100", "hpr_labels_b150", "eml_v10"):
        assert D.zeile(zid)["bereich"]["n"] == [30]
    im_readme("In den Zellen der Auswahlregel kommt Breite 20 nur bei 100 Kunden vor")


def test_bidirektional_nennt_dynd_als_eine_eigene_fassung():
    im_readme("Eine einfache dynamische Wahl des Halbwegs (dynD, eine von vier eigenen Fassungen der Quell-Demo, nicht das Verfahren von Tilk u. a.)")
    assert "nicht verwenden" not in README


def test_abhaengige_verbraeuche_und_bindende_grenze_stehen_in_der_zeile_zu_den_grenzen():
    k = D.zeile("mgr_korreliert")["werte"]
    assert k["instanzen"] == 12
    assert k["gleich_last_r2"] == k["gleich_last_r3"] == k["gleich_last_r4"]                       # kein weiteres Sinken
    assert k["unabhaengig_r4"] < k["rauschen_r4"] < k["gleich_last_r4"]                          # schwächer als bei unabhängigen Verbräuchen
    assert k["gegenlaeufig_r4"] < k["unabhaengig_r4"]                                            # stärker
    im_readme("Grenze 70 je Zusatzgröße (bindend; bei nie bindender Grenze ist es eine andere Aufgabe mit anderen Zahlen)")
    im_readme("sinkt der Anteil dominierter Labels bei Fahrerzeit gleich Last nicht weiter, bei Last plus Rauschen schwächer und bei gegenläufigen Verbräuchen stärker als bei unabhängigen")


def test_pricing_aufruf_nennt_die_dualpreise_der_ersten_runde():
    assert "Dualpreisen der ersten Runde" in D.zeile("zfl_pricing")["voraussetzung"]
    im_readme("ein Pricing-Aufruf mit den Dualpreisen der ersten Runde, 12 Instanzen je Zelle")


def test_etikettenlimit_nennt_mittel_der_verhaeltnisse_und_den_master_preis():
    assert "Mittel der Instanz-Verhältnisse" in D.zeile("hpr_labels_b100")["voraussetzung"]
    im_readme("30 Instanzen (Mittel der Instanz-Verhältnisse): Endschranke gleich in")
    im_readme("und ein Master-LP nur etwa 380 Labels kostet")
    im_readme("„heuristisches Pricing ist schneller“ dort nicht steht")


def test_eimer_nennen_die_80_laeufe_mit_dualpreisen_am_ende():
    v = D.zeile("eml_v10")["werte"]
    im_readme(f"{v['q70_laeufe_ende'] + v['q120_laeufe_ende']} Läufe mit Dualpreisen am Ende der Spaltenerzeugung ({v['q70_laeufe_ende']} je Kapazität; die Reihe hat {v['laeufe_gesamt']} Läufe)")


def test_messgroesse_nennt_die_ausnahmen_der_zaehleinheit():
    im_readme("meist erzeugte Labels, bei Eimern Dominanzvergleiche, bei der Kantenstreichung Kanten und Vorwärtslabels. Sekunden stehen beim heuristischen Pricing (nur als Größenordnung) und als Hinweis bei den Eimern.")
