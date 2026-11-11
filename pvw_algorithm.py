"""Auswahlregel für das ng-Gedächtnis k, angewendet auf feste Messdaten (der einzige Rechenkern dieser Demo).

Regel (Einstellung der Demo, keine Aussage über die Wirklichkeit): Gewählt wird das **kleinste k**, dessen Schranke der Spaltenerzeugung im Mittel höchstens `tau_mittel` Prozent
und in jeder einzelnen Instanz höchstens `tau_max` Prozent unter der Schranke des **Bezugs** liegt. Bezug ist das größte gemessene k der Zelle (k = 16 bei 50 und 100 Kunden, k = 8 bzw. elementar
bei 30 Kunden), **nicht** die elementare Schranke, weil die elementare Rechnung bei 50 und 100 Kunden fast immer abgebrochen wurde.

Jede Regel ist eine eigene Funktion ohne versteckten Zustand; eine Zelle ist ein Wörterbuch mit `bezug`, `ks` und `zeilen` (je Zeile `seed`, `k`, `schranke`, `labels`), wie `data/k_zellen.json` sie hält.
Nur Standardbibliothek."""

from dataclasses import dataclass
from statistics import mean, median


def zeilen_von(zelle: dict, k: int) -> dict:
    """Zeilen der Zelle für ein k, nach Zufalls-Seed der Instanz: {seed: zeile}."""
    return {z["seed"]: z for z in zelle["zeilen"] if z["k"] == k}


def luecken(zelle: dict, k: int) -> list:
    """Lücke der Schranke von k zur Schranke des Bezugs je Instanz in Prozent des Bezugs; nur Instanzen, in denen beide Läufe fertig wurden. Positiv heißt: k liegt unter dem Bezug."""
    bez = zeilen_von(zelle, zelle["bezug"])
    zk = zeilen_von(zelle, k)
    return [100.0 * (bez[s]["schranke"] - zk[s]["schranke"]) / bez[s]["schranke"] for s in sorted(zk) if s in bez]


def labels_median(zelle: dict, k: int) -> float:
    """Median der erzeugten Labels der ganzen Spaltenerzeugung über die fertigen Instanzen mit diesem k."""
    return median(z["labels"] for z in zelle["zeilen"] if z["k"] == k)


@dataclass(frozen=True)
class KZeile:
    k: int
    luecke_mittel: float
    luecke_max: float
    labels_median: float
    instanzen: int


def tabelle(zelle: dict) -> list:
    """Eine Zeile je k der Zelle (aufsteigend): mittlere und größte Lücke zum Bezug, Median der Labels, Zahl der Instanzen mit Lücke."""
    zeilen = []
    for k in sorted(zelle["ks"]):
        ls = luecken(zelle, k)
        if not ls:                      # für dieses k gibt es keine Instanz mit zwei fertigen Läufen: k bleibt aus der Tabelle
            continue
        zeilen.append(KZeile(k, mean(ls), max(ls), labels_median(zelle, k), len(ls)))
    return zeilen


def erfuellt(zeile: KZeile, tau_mittel: float, tau_max: float) -> bool:
    """Erfüllt dieses k beide Schwellen?"""
    return zeile.luecke_mittel <= tau_mittel and zeile.luecke_max <= tau_max


@dataclass(frozen=True)
class KWahl:
    k: int
    luecke_mittel: float
    luecke_max: float
    labels_verhaeltnis: float      # Median der Labels bei k geteilt durch den Median der Labels beim Bezug
    kein_kleineres_k: bool         # nur der Bezug selbst erfüllt die Schwellen
    instanzen: int
    bezug: int


def waehle_k(zelle: dict, tau_mittel: float, tau_max: float) -> KWahl:
    """Kleinstes k, das beide Schwellen erfüllt. Erfüllt kein kleineres k sie, ist es der Bezug selbst (Hinweis `kein_kleineres_k`)."""
    zeilen = tabelle(zelle)
    bezug_zeile = next(z for z in zeilen if z.k == zelle["bezug"])
    wahl = next(z for z in zeilen if erfuellt(z, tau_mittel, tau_max))
    return KWahl(
        k=wahl.k, luecke_mittel=wahl.luecke_mittel, luecke_max=wahl.luecke_max,
        labels_verhaeltnis=wahl.labels_median / bezug_zeile.labels_median,
        kein_kleineres_k=wahl.k == zelle["bezug"], instanzen=wahl.instanzen, bezug=zelle["bezug"],
    )


def alle_gleich(zelle: dict) -> bool:
    """Liegt die Schranke für jedes k in jeder Instanz gleich hoch wie beim Bezug (Lücke kleiner als 1e-9 Prozent)? Dann sagt die Zelle nichts über die Wirkung von k."""
    return all(abs(l) < 1e-9 for k in zelle["ks"] for l in luecken(zelle, k))
