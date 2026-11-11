"""Feste Messwerte laden und abfragen (Kopien aus den Messdateien der anderen Demos der Reihe, `data/*.json`).

Keine Rechnung hier: Nur Lesen, Auswählen nach Bereich (Kundenzahl, Fensterbreite, Typ) und Formatieren von Zahlen mit Dezimalkomma."""

import json
from functools import lru_cache
from pathlib import Path

import pvw_constants as C

DATA = Path(__file__).resolve().parent / "data"


@lru_cache(maxsize=None)
def _lade(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def messzeilen() -> list:
    return _lade(C.DATA_MESSWERTE)["zeilen"]


def k_zellen() -> list:
    return _lade(C.DATA_K_ZELLEN)["zellen"]


def zeile(zid: str) -> dict:
    """Messzeile nach Kennung."""
    return next(z for z in messzeilen() if z["id"] == zid)


def w(zid: str, key: str):
    """Ein Wert einer Messzeile."""
    return zeile(zid)["werte"][key]


def im_bereich(z: dict, n: int, breite: int, typ: str) -> bool:
    """Liegt die Aufgabe (Kundenzahl, Fensterbreite, Typ) im Bereich, für den die Zeile gemessen ist? Ein Eintrag None heißt: keine Einschränkung."""
    b = z["bereich"]
    return all(liste is None or wert in liste for liste, wert in ((b["n"], n), (b["breite"], breite), (b["typ"], typ)))


def k_zelle(n: int, breite: int, typ: str):
    """Zelle der Auswahlregel für die Aufgabe, oder None, wenn es keine gibt."""
    return next((z for z in k_zellen() if (z["n"], z["breite"], z["typ"]) == (n, breite, typ)), None)


def de(x: float, stellen: int = 1) -> str:
    """Zahl mit Dezimalkomma und Tausenderleerzeichen (schmales Leerzeichen entfällt: normales Leerzeichen)."""
    s = f"{x:,.{stellen}f}".replace(",", " ").replace(".", ",")
    return s


def quelle_text(z: dict) -> str:
    q = z["quelle"]
    ort = "Vormessung" if q["demo"] == "vormessung" else q["demo"]
    return f"{ort}, {q['datei']}"
