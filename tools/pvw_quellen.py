"""Quellen der Messwerte: liest die festen Messreihen der anderen Demos der Linie (und der Vormessung) und bildet die Kennzahlen, die der Entscheidungsbaum nennt.

Diese Datei gehört nicht zur App. Sie wird vom Bauwerkzeug `tools/messwerte_bauen.py` (schreibt `data/messwerte.json` und `data/k_zellen.json`) und von
`tests/test_quellen.py` benutzt: Der Test liest dieselben Quellzeilen noch einmal aus den Dateien der jeweiligen Demo und vergleicht sie mit der Kopie in `data/`.
Jede Funktion bekommt nichts und liest ihre Quelle selbst; sie liefert ein Wörterbuch Name -> Zahl. Ist der Ordner der Demo nicht vorhanden, gibt `verfuegbar` False zurück.

Bewusst nur Standardbibliothek. Die Auswertung ist je Quelle so gewählt, dass sie die Zahl der README der Quell-Demo ergibt (Test `test_quellen.py` prüft zusätzlich,
dass diese Zahl im Wortlaut der README der Quell-Demo steht)."""

import json
import re
from pathlib import Path
from statistics import mean, median

PROJEKTE = Path(__file__).resolve().parents[2]
VORMESSUNG = PROJEKTE / "label-setting-planung" / "vormessung"


def demo_ordner(demo: str) -> Path:
    return PROJEKTE / demo


def verfuegbar(demo: str) -> bool:
    """Gibt es den Ordner der Quell-Demo (bzw. der Vormessung für den Namen „vormessung“)?"""
    return (VORMESSUNG if demo == "vormessung" else demo_ordner(demo)).is_dir()


def _json(demo: str, rel: str):
    return json.loads((demo_ordner(demo) / rel).read_text(encoding="utf-8"))


def readme_text(demo: str) -> str:
    return (demo_ordner(demo) / "README.md").read_text(encoding="utf-8")


def _prozent(zaehler: float, nenner: float) -> float:
    return 100.0 * zaehler / nenner


# ---------------------------------------------------------------------------------------------------------------------------------------
# Stück 1 bis 5: Grundbausteine
# ---------------------------------------------------------------------------------------------------------------------------------------

def wmg_fensterbreite() -> dict:
    """weg-mit-grenzen: Median der Labels einer ganzen Spaltenerzeugung (30 Kunden, 6 Instanzen) je Fensterbreite, k = 1 und k = 5."""
    d = _json("weg-mit-grenzen-demo", "data/baender_fensterbreite.json")
    out = {}
    for z in d["zeilen"]:
        out[f"b{z['breite']}_k{z['k']}"] = z["labels_median"]
    return out


def zfl_pricing_aufruf() -> dict:
    """zeitfenster-labeling: Median der Labels eines Pricing-Aufrufs (30 Kunden, k = 5, 12 Instanzen) je Typ und Fensterbreite."""
    d = _json("zeitfenster-labeling-demo", "data/band_p03.json")
    ascii_typ = {"zufällig": "zufaellig", "gruppiert": "gruppiert"}
    return {f"{ascii_typ[z['typ']]}_b{z['breite']}": z["median"] for z in d["zeilen"]}


def dml_regeln() -> dict:
    """dominanz-labels: 180 Fälle mit 7 Kunden; wie oft verfehlt Dominanz nur nach Kosten den besten Weg, und wie viel mehr Labels ohne Dominanz."""
    d = _json("dominanz-labels-demo", "data/regeltabelle.json")
    return {
        "faelle": d["faelle"],
        "verfehlt_nur_kosten": d["verfehlung_nur_kosten"]["faelle"],
        "faktor_ohne_dominanz_median": d["verhaeltnis_keine_zu_voll"]["median"],
    }


def pdp_glaettung() -> dict:
    """pricing-dualpreise: Runden der Spaltenerzeugung bei Glättung α (30 Kunden, Breite 100, k = 5, 6 Instanzen): Mittel und Zahl der Instanzen mit mehr Runden als bei α = 0."""
    d = _json("pricing-dualpreise-demo", "data/baender_glaettung.json")
    zeilen = {z["alpha"]: z["instanzen"] for z in d["zeilen"] if z["n"] == 30}
    basis = {i["seed"]: i["runden"] for i in zeilen[0]}
    out = {"instanzen": len(zeilen[0])}
    for alpha, inst in zeilen.items():
        out[f"runden_mittel_a{alpha}"] = mean(i["runden"] for i in inst)
        out[f"mehr_runden_a{alpha}"] = sum(1 for i in inst if i["runden"] > basis[i["seed"]])
    return out


# ---------------------------------------------------------------------------------------------------------------------------------------
# Stück 6, 7, 9: Kreise, Elementarität, ng-Routen
# ---------------------------------------------------------------------------------------------------------------------------------------

def kip_kreisanteil() -> dict:
    """kreise-im-pricing: neue Spalten mit und ohne Kreis (30 Kunden, zufällig, k = 1, 6 Instanzen je Breite)."""
    d = _json("kreise-im-pricing-demo", "data/baender_kreise.json")
    out = {}
    for z in d["zellen"]:
        if z["n"] == 30 and z["typ"] == "zufall" and z["k"] == 1:
            b = z["breite"]
            out[f"b{b}_mit_kreis"] = sum(r["mit_kreis"] for r in z["zeilen"])
            out[f"b{b}_neue_spalten"] = sum(r["neue_spalten"] for r in z["zeilen"])
    return out


def kip_luecke() -> dict:
    """kreise-im-pricing: Lücke der Schranke von k = 1 zur elementaren Schranke in % (30 Kunden, zufällig, 6 Instanzen, alle elementaren Läufe fertig)."""
    d = _json("kreise-im-pricing-demo", "data/baender_luecke.json")
    out = {}
    for z in d["zellen"]:
        if z["bezug"] == "elementar" and z["n"] == 30:
            fertig = [r for r in z["zeilen"] if not r["abgebrochen"]]
            luecken = [_prozent(r["schranke_ref"] - r["schranke_k1"], r["schranke_ref"]) for r in fertig]
            b = z["breite"]
            out[f"b{b}_mittel"] = mean(luecken)
            out[f"b{b}_max"] = max(luecken)
            out[f"b{b}_instanzen"] = len(fertig)
    return out


def epr_abbrueche() -> dict:
    """elementar-pricing: abgebrochene elementare Läufe bei 30 Kunden (Neurechnung der Demo, Zeitgrenze 30 s je Pricing-Aufruf) und in der früheren Messung; 50 und 100 Kunden aus der Vormessung."""
    laeufe = _json("elementar-pricing-demo", "data/laeufe.json")["zeilen"]
    out = {}
    for b in (40, 100, 200):
        el = [z for z in laeufe if z["n"] == 30 and z["breite"] == b and z["k"] == 30]
        out[f"neu_b{b}_laeufe"] = len(el)
        out[f"neu_b{b}_abgebrochen"] = sum(1 for z in el if z["abgebrochen"])
    for z in _json("elementar-pricing-demo", "data/vormessung.json")["abbrueche"]:
        if z["gruppe"] == "V1":
            out[f"v1_b{z['breite']}_abgebrochen"] = z["abgebrochen"]
            out[f"v1_b{z['breite']}_laeufe"] = z["laeufe"]
    return out


def ngr_elementar_gross_und_klein() -> dict:
    """ng-routen: elementare Läufe bei 50 und 100 Kunden (94 von 96 abgebrochen) und bei 10 bis 25 Kunden (alle fertig)."""
    sk = _json("ng-routen-demo", "data/skalierung.json")["zeilen"]
    el = [z for z in sk if z["k"] == z["n"]]
    kl = [z for z in _json("ng-routen-demo", "data/elementar.json")["zeilen"] if z["n"] <= 25 and z["k"] == z["n"]]
    return {
        "gross_laeufe": len(el),
        "gross_abgebrochen": sum(1 for z in el if z["abgebrochen"]),
        "klein_laeufe": len(kl),
        "klein_abgebrochen": sum(1 for z in kl if z["abgebrochen"]),
    }


def _knick_je_instanz() -> dict:
    """ng-routen, 24 Instanzen mit 30 Kunden, Breite 100: {(typ, seed): {("ng"|"kcyc", k): Zeile}}."""
    d = _json("ng-routen-demo", "data/knick_n30.json")["zeilen"]
    inst: dict = {}
    for z in d:
        inst.setdefault((z["typ"], z["seed"]), {})[(z["art"], z["k"])] = z
    return inst


def ngr_k_zyklen() -> dict:
    """ng-routen: k-Zyklen gegen ng (30 Kunden, Breite 100, 24 Instanzen, Bezug ng k = 8): Lücke der Schranke und Labels im Verhältnis zu ng k = 8, Abbrüche."""
    inst = _knick_je_instanz()
    out = {}
    for art, k in (("kcyc", 2), ("kcyc", 3), ("kcyc", 4), ("ng", 5)):
        luecken, verh, abbr = [], [], 0
        for z in inst.values():
            x, bez = z[(art, k)], z[("ng", 8)]
            if x["abgebrochen"]:
                abbr += 1
                continue
            luecken.append(_prozent(bez["schranke"] - x["schranke"], bez["schranke"]))
            verh.append(x["labels"] / bez["labels"])
        name = f"{art}{k}"
        out[f"{name}_luecke_mittel"] = mean(luecken)
        out[f"{name}_labels_verhaeltnis"] = mean(verh)
        out[f"{name}_abgebrochen"] = abbr
        out[f"{name}_instanzen"] = len(inst)
    return out


def ngr_dssr() -> dict:
    """ng-routen: DSSR gegen ng k = 5 an 72 festen Dualpreis-Sätzen (30 Kunden, Breite 100). DSSR ist exakt; die elementare Rechnung brach in 6 Sätzen ab, dort fehlt der Vergleich.
    „ng k = 5 verfehlt den besten Weg“ heißt: sein Zielwert liegt unter dem von DSSR (er ist eine Relaxation und findet dann einen Weg mit Wiederholung)."""
    z = _json("ng-routen-demo", "data/dssr.json")["zeilen"]
    tol = 1e-6
    ende = [r for r in z if r["duals"] == "ende"]
    mit_elem = [r for r in z if r["elem"]["rc"] is not None]
    return {
        "saetze": len(z),
        "dssr_abgebrochen": sum(r["dssr"]["abgebrochen"] for r in z),
        "saetze_mit_elementar": len(mit_elem),
        "dssr_gleich_elementar": sum(1 for r in mit_elem if abs(r["dssr"]["rc"] - r["elem"]["rc"]) <= tol),
        "labels_dssr_zu_ng5": mean(r["dssr"]["labels"] / r["ng5"]["labels"] for r in z),
        "ng5_verfehlt": sum(1 for r in z if r["ng5"]["rc"] < r["dssr"]["rc"] - tol),
        "ng5_verfehlt_ende": sum(1 for r in ende if r["ng5"]["rc"] < r["dssr"]["rc"] - tol),
        "saetze_ende": len(ende),
        "labels_dssr_zu_ng5_ende": mean(r["dssr"]["labels"] / r["ng5"]["labels"] for r in ende),
    }


# ---------------------------------------------------------------------------------------------------------------------------------------
# Stück 4: mehrere Grenzen
# ---------------------------------------------------------------------------------------------------------------------------------------

def mgr_v11() -> dict:
    """mehrere-grenzen: ganze Spaltenerzeugung, 30 Kunden, zufällig, Breite 100, k = 1, Grenze 70 je Zusatzgröße (r = 1 nur Zeit): Median über 12 Instanzen von Anteil dominiert und Vergleichen je Label."""
    d = _json("mehrere-grenzen-demo", "data/baender_v11.json")
    sp = d["spalten"]
    il, idom, ivgl, iab = sp.index("labels"), sp.index("dominiert"), sp.index("vergleiche"), sp.index("abgebrochen")
    out = {}
    for z in d["zellen"]:
        if z["typ"] == "zufall" and z["breite"] == 100 and z["k"] == 1 and z["art"] == "colgen" and z["grenze"] in ("nur Zeit", "bindend (70)"):
            zeilen = [r for r in z["zeilen"] if not r[iab]]
            r = z["r"]
            out[f"r{r}_dominiert_median"] = median(_prozent(x[idom], x[il]) for x in zeilen)
            out[f"r{r}_vergleiche_je_label_median"] = median(x[ivgl] / x[il] for x in zeilen)
            out[f"r{r}_instanzen"] = len(zeilen)
    return out


# ---------------------------------------------------------------------------------------------------------------------------------------
# Stück 11: bidirektional
# ---------------------------------------------------------------------------------------------------------------------------------------

def bdl_v9() -> dict:
    """bidirektionales Labeling: 480 Läufe mit 30 Kunden; fester Halbweg H/2 gegen einseitig (Labels), Verbindungspaare je einseitigem Label, je Typ und Breite."""
    d = _json("bidirektional-labeling-demo", "data/baender_v9.json")
    f = d["felder"]
    il, ip = f.index("labels"), f.index("paare")
    alle, je_zelle, paare, dyn, dyn_besser = [], {}, [], [], 0
    for z in d["zeilen"]:
        for lauf in z["laeufe"]:
            uni, fest, dynd = lauf["v"]["uni"], lauf["v"]["fest0.5"], lauf["v"]["dynD"]
            q = fest[il] / uni[il]
            alle.append(q)
            dyn.append(dynd[il] / uni[il])
            dyn_besser += dynd[il] < fest[il]
            je_zelle.setdefault((z["typ"], z["breite"]), []).append(q)
            paare.append(fest[ip] / uni[il])
    out = {
        "laeufe": len(alle),
        "weniger_labels": sum(1 for q in alle if q < 1),
        "verhaeltnis_median": median(alle),
        "verhaeltnis_min": min(alle),
        "verhaeltnis_max": max(alle),
        "paare_je_label_median": median(paare),
        "dynamisch_median": median(dyn),
        "dynamisch_besser_als_fest": dyn_besser,
    }
    for (typ, b), qs in je_zelle.items():
        out[f"{typ}_b{b}_median"] = median(qs)
        out[f"{typ}_b{b}_laeufe"] = len(qs)
    return out


# ---------------------------------------------------------------------------------------------------------------------------------------
# Stück 12: Eimer
# ---------------------------------------------------------------------------------------------------------------------------------------

def eml_v10() -> dict:
    """Eimer-Labeling: 320 Läufe (30 Kunden, k = 5); Dualpreise am Ende, je Kapazität 40 Läufe. Ersparnis an Dominanzvergleichen (Median des Verhältnisses je Lauf) und netto nach Verwaltung (Gewicht 0,1, Annahme)."""
    laeufe = _json("eimer-labeling-demo", "data/laeufe_v10.json")["laeufe"]
    gewicht = 0.1

    def vergleiche(e):
        return e[2] + e[3]

    def aufwand(e):
        return e[2] + e[3] + gewicht * e[4]

    out = {"laeufe_gesamt": len(laeufe)}
    zeit_ersparnis, last_ersparnis, zeit_netto, last_netto = [], [], [], []
    for q in (70, 120):
        lq = [x for x in laeufe if x["Q"] == q and x["runde"] == "ende"]
        out[f"q{q}_laeufe_ende"] = len(lq)
        for einst in ("1,0", "80,0", "0,5", "0,10", "20,0", "40,0"):
            r_v = median(vergleiche(x["einstellungen"][einst]) / vergleiche(x["einstellungen"]["0,0"]) for x in lq)
            r_a = median(aufwand(x["einstellungen"][einst]) / aufwand(x["einstellungen"]["0,0"]) for x in lq)
            out[f"q{q}_{einst.replace(',', '_')}_vergleiche"] = r_v
            out[f"q{q}_{einst.replace(',', '_')}_aufwand"] = r_a
        for einst in ("1,0", "2,0", "5,0", "10,0", "20,0", "40,0", "80,0"):
            zeit_ersparnis.append(100 * (1 - median(vergleiche(x["einstellungen"][einst]) / vergleiche(x["einstellungen"]["0,0"]) for x in lq)))
        for einst in ("20,0", "40,0", "80,0"):
            zeit_netto.append(100 * (1 - median(aufwand(x["einstellungen"][einst]) / aufwand(x["einstellungen"]["0,0"]) for x in lq)))
        for einst in ("0,5", "0,10"):
            last_ersparnis.append(100 * (1 - median(vergleiche(x["einstellungen"][einst]) / vergleiche(x["einstellungen"]["0,0"]) for x in lq)))
            last_netto.append(100 * (1 - median(aufwand(x["einstellungen"][einst]) / aufwand(x["einstellungen"]["0,0"]) for x in lq)))
    out.update(
        zeit_ersparnis_min=min(zeit_ersparnis), zeit_ersparnis_max=max(zeit_ersparnis),
        last_ersparnis_min=min(last_ersparnis), last_ersparnis_max=max(last_ersparnis),
        zeit_netto_min=min(zeit_netto), zeit_netto_max=max(zeit_netto),
        last_netto_min=min(last_netto), last_netto_max=max(last_netto),
    )
    return out


# ---------------------------------------------------------------------------------------------------------------------------------------
# Stück 13: Kantenstreichung
# ---------------------------------------------------------------------------------------------------------------------------------------

def ksp_n30() -> dict:
    """Kantenstreichung (30 Kunden, ng k = 8, Partitionierungs-Master, 12 Instanzen je Zelle): gestrichene Kanten (in % der Kanten mit zulässiger Route) und Vorwärtslabels im gestrichenen gegen den vollen Graphen,
    bei der exakten Lücke (nur Instanzen mit bewiesenem Optimum) und bei der oberen Schranke aus den Spalten."""
    d = _json("kantenstreichung-pricing-demo", "data/baender_kanten.json")
    out = {}
    for z in d["zellen"]:
        if z["n"] != 30:
            continue
        name = f"{z['typ']}_b{z['breite']}"
        fertig = [r for r in z["zeilen"] if r["fertig"]]
        exakt = [r for r in fertig if r["ub3_exakt"]]
        out[f"{name}_instanzen"] = len(fertig)
        out[f"{name}_exakt_instanzen"] = len(exakt)
        out[f"{name}_exakt_gestrichen_mittel"] = mean(_prozent(r["wirkung"]["ub3"]["entfernt"], r["kanten_mit_route"]) for r in exakt)
        out[f"{name}_exakt_labels_mittel"] = mean(r["wirkung"]["ub3"]["labels"] / r["labels_vorwaerts"] for r in exakt)
        out[f"{name}_exakt_luecke_mittel"] = mean(_prozent(r["ub3"] - r["lb"], r["lb"]) for r in exakt)
        out[f"{name}_spalten_gestrichen_mittel"] = mean(_prozent(r["wirkung"]["ub1"]["entfernt"], r["kanten_mit_route"]) for r in fertig)
        out[f"{name}_spalten_labels_mittel"] = mean(r["wirkung"]["ub1"]["labels"] / r["labels_vorwaerts"] for r in fertig)
        out[f"{name}_spalten_luecke_mittel"] = mean(_prozent(r["ub1"] - r["lb"], r["lb"]) for r in fertig)
    return out


# ---------------------------------------------------------------------------------------------------------------------------------------
# Stück 14: heuristisches Pricing (vorläufig aus der Vormessung)
# ---------------------------------------------------------------------------------------------------------------------------------------

def _v13_je_instanz(zeilen) -> dict:
    """{(typ, seed): {konfig: (schranke, runden, labels, abgebrochen)}} je Breite getrennt gehalten über den Schlüssel (breite, typ, seed)."""
    inst: dict = {}
    for z in zeilen:
        inst.setdefault((z["breite"], z["typ"], z["seed"]), {})[z["konfig"]] = (z["schranke"], z["runden"], z["labels"], z["abgebrochen"])
    return inst


def _v13_kennzahlen(inst: dict, breite: int) -> dict:
    """Kennzahlen des heuristischen Pricings für eine Breite aus {(breite, typ, seed): {konfig: (schranke, runden, labels, abgebrochen)}}."""
    zeilen = {k: v for k, v in inst.items() if k[0] == breite}
    out = {
        "instanzen": len(zeilen),
        "schranke_gleich": sum(1 for z in zeilen.values() if max(abs(v[0] - z["exakt"][0]) for v in z.values()) < 1e-5),
        "abgebrochen": sum(int(v[3]) for z in zeilen.values() for v in z.values()),
    }
    for konf in ("L5", "L10", "L20"):
        out[f"{konf}_labels"] = mean(z[konf][2] / z["exakt"][2] for z in zeilen.values())
        out[f"{konf}_iterationen_plus"] = 100 * (mean(z[konf][1] for z in zeilen.values()) / mean(z["exakt"][1] for z in zeilen.values()) - 1)
        out[f"{konf}_weniger_labels"] = sum(1 for z in zeilen.values() if z[konf][2] < z["exakt"][2])
    return out


def hpr_v13() -> dict:
    """Heuristisches Pricing (n = 30, ng k = 8, Überdeckungs-Master; Breite 100: 15 zufällige und 15 gruppierte Instanzen, Breite 150: 8 + 8): Labels der Varianten L5, L10, L20 im Verhältnis zu exakt (Mittel der Instanz-Verhältnisse),
    Runden der Spaltenerzeugung (Mittel je Variante gegen exakt), gleiche Endschranke je Instanz. Quelle: Neurechnung in `heuristisches-pricing-demo/data/laeufe_v13.json` (mit der Rohausgabe der Vormessung verglichen: 184 von 184 Zeilen gleich)."""
    zeilen = _json("heuristisches-pricing-demo", "data/laeufe_v13.json")["laeufe"]
    inst = _v13_je_instanz({"breite": z["breite"], "typ": z["typ"], "seed": z["seed"], "konfig": z["variante"], "schranke": z["schranke"], "runden": z["iterationen"], "labels": z["labels"], "abgebrochen": z["abgebrochen"]} for z in zeilen)
    return {f"b{b}_{k}": v for b in (100, 150) for k, v in _v13_kennzahlen(inst, b).items()}


def hpr_v13_vormessung() -> dict:
    """Dieselben Kennzahlen aus den Rohdateien `out_v13_*.txt` der Vormessung (Gegenprobe zu `hpr_v13`; Spalten: typ n breite seed k konfig schranke iter spalten labels ... abgebr)."""
    zeilen = []
    for name in ("out_v13_zufall.txt", "out_v13_cluster.txt", "out_v13_zufall_b150.txt", "out_v13_cluster_b150.txt"):
        for zeile in (VORMESSUNG / name).read_text(encoding="utf-8").splitlines():
            p = zeile.split()
            if not p or p[0] == "typ" or len(p) != 16:
                continue
            zeilen.append({"breite": int(p[2]), "typ": p[0], "seed": int(p[3]), "konfig": p[5], "schranke": float(p[6]), "runden": int(p[7]), "labels": int(p[9]), "abgebrochen": int(p[15])})
    inst = _v13_je_instanz(zeilen)
    return {f"b{b}_{k}": v for b in (100, 150) for k, v in _v13_kennzahlen(inst, b).items()}


def hpr_zeit() -> dict:
    """Heuristisches Pricing, Zeit (30 Instanzen, n = 30, Breite 100, k = 8, 3 Wiederholungen, Rechner ausgelastet): CPU-Zeit je Variante als Summe der Instanz-Mediane im Verhältnis zu exakt; Anteil des Pricings an der CPU-Zeit von exakt.
    Quelle: run_p14_zeit.log der Vormessung in der Kopie `heuristisches-pricing-demo/data/zeit_vormessung.json`. Zeiten sind nur Größenordnungen."""
    zeilen = _json("heuristisches-pricing-demo", "data/zeit_vormessung.json")["zeilen"]
    je: dict = {}
    for z in zeilen:
        je.setdefault((z["typ"], z["seed"], z["variante"]), []).append(z)
    summe = {}
    for (typ, seed, var), reps in je.items():
        summe[var] = summe.get(var, 0.0) + median(r["cpu"] for r in reps)
    out = {f"{v.lower()}_cpu_verhaeltnis": summe[v] / summe["exakt"] for v in ("L5", "L10", "L20")}
    exakt = [z for z in zeilen if z["variante"] == "exakt"]
    # Median der Wiederholungen je Instanz, dann Summe: wie in run_p14_zeit_auswertung.log
    je_ex: dict = {}
    for z in exakt:
        je_ex.setdefault((z["typ"], z["seed"]), []).append(z)
    pricing = sum(median(r["exakt_cpu"] for r in reps) for reps in je_ex.values())
    gesamt = sum(median(r["cpu"] for r in reps) for reps in je_ex.values())
    out["pricing_anteil_exakt"] = _prozent(pricing, gesamt)
    out["instanzen"] = len(je_ex)
    out["wiederholungen"] = max(z["wiederholung"] for z in zeilen)
    return out


# ---------------------------------------------------------------------------------------------------------------------------------------
# k-Zellen für die Auswahlregel (Experiment 2)
# ---------------------------------------------------------------------------------------------------------------------------------------

V8_TYPEN = {"zufall": "zufällig", "cluster": "gruppiert"}


def lese_v8_zellen() -> list:
    """Die acht Zellen von V8 aus den Rohdateien out_v8_<typ>_n<n>_w<breite>.txt der Vormessung (ohne _elem; abgebrochene Läufe fehlen), wie `hand_16.py` sie liest."""
    zellen = []
    for pfad in sorted(VORMESSUNG.glob("out_v8_*_n*_w*.txt")):
        if pfad.name.endswith("_elem.txt") or pfad.name.endswith("_auswertung.txt"):
            continue
        zeilen = []
        typ = n = w = None
        for zeile in pfad.read_text(encoding="utf-8").splitlines():
            p = zeile.split()
            if not p or p[0] == "typ" or len(p) != 12:
                continue
            if p[5] == "NA" or int(p[11]):
                continue
            typ, n, w = p[0], int(p[1]), int(p[2])
            zeilen.append({"seed": int(p[3]), "k": int(p[4]), "schranke": float(p[5]), "labels": int(p[9])})
        zellen.append({
            "id": f"{typ}_n{n}_b{w}", "typ": V8_TYPEN[typ], "n": n, "breite": w, "bezug": 16, "ks": [1, 3, 5, 8, 12, 16],
            "quelle": {"demo": "vormessung", "datei": pfad.name, "text": f"Rohdatei V8, Spalten typ n breite seed k schranke ... labels ... abgebr; abgebrochene Läufe fehlen"},
            "zeilen": zeilen,
        })
    return zellen


def lese_n30_zellen() -> list:
    """Drei Zellen mit 30 Kunden aus den Messdateien von `ng-routen-demo`: Breite 100 zufällig und gruppiert (Bezug ng k = 8, 12 Instanzen, `knick_n30.json`),
    Breite 40 zufällig (Bezug elementar, 6 Instanzen, `elementar.json`)."""
    zellen = []
    knick = _json("ng-routen-demo", "data/knick_n30.json")["zeilen"]
    for typ in ("zufall", "cluster"):
        zeilen = [{"seed": z["seed"], "k": z["k"], "schranke": z["schranke"], "labels": z["labels"]}
                  for z in knick if z["typ"] == typ and z["art"] == "ng" and not z["abgebrochen"]]
        zellen.append({
            "id": f"{typ}_n30_b100", "typ": V8_TYPEN[typ], "n": 30, "breite": 100, "bezug": 8, "ks": [1, 2, 3, 4, 5, 8],
            "quelle": {"demo": "ng-routen-demo", "datei": "data/knick_n30.json", "text": "Zeilen art = ng, k = 1 bis 5 und 8"},
            "zeilen": zeilen,
        })
    elem = _json("ng-routen-demo", "data/elementar.json")["zeilen"]
    zeilen = [{"seed": z["seed"], "k": z["k"], "schranke": z["schranke"], "labels": z["labels"]}
              for z in elem if z["n"] == 30 and z["breite"] == 40 and not z["abgebrochen"]]
    zellen.append({
        "id": "zufall_n30_b40", "typ": "zufällig", "n": 30, "breite": 40, "bezug": 30, "ks": [1, 3, 5, 8, 12, 30],
        "quelle": {"demo": "ng-routen-demo", "datei": "data/elementar.json", "text": "Zeilen n = 30, Breite 40, k = 1, 3, 5, 8, 12 und 30 (= elementar)"},
        "zeilen": zeilen,
    })
    return zellen


# ---------------------------------------------------------------------------------------------------------------------------------------
# Textbelege (Zahlen, die nur im Text einer README oder Ergebnisdatei stehen)
# ---------------------------------------------------------------------------------------------------------------------------------------

def enthaelt(demo: str, datei: str, fragment: str) -> bool:
    """Steht das Fragment (Leerräume vereinheitlicht) im Text der Datei? Für die README ist `datei` „README.md“; für die Vormessung ein Dateiname dort."""
    pfad = (VORMESSUNG / datei) if demo == "vormessung" else (demo_ordner(demo) / datei)
    text = re.sub(r"\s+", " ", pfad.read_text(encoding="utf-8"))
    return re.sub(r"\s+", " ", fragment) in text


EXTRAKTOREN = {
    "wmg_fensterbreite": wmg_fensterbreite,
    "zfl_pricing_aufruf": zfl_pricing_aufruf,
    "dml_regeln": dml_regeln,
    "pdp_glaettung": pdp_glaettung,
    "kip_kreisanteil": kip_kreisanteil,
    "kip_luecke": kip_luecke,
    "epr_abbrueche": epr_abbrueche,
    "ngr_elementar_gross_und_klein": ngr_elementar_gross_und_klein,
    "ngr_k_zyklen": ngr_k_zyklen,
    "ngr_dssr": ngr_dssr,
    "mgr_v11": mgr_v11,
    "bdl_v9": bdl_v9,
    "eml_v10": eml_v10,
    "ksp_n30": ksp_n30,
    "hpr_v13": hpr_v13,
    "hpr_zeit": hpr_zeit,
}
