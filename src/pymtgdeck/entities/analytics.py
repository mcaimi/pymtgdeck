#! /usr/bin/env python

# card/deck analytics

import re

try:
    from .binder import Binder
    from .deck import Deck
    from .types import CARD_TYPES, LEGAL_FORMATS, is_basic_land
except ImportError as e:
    print(f"Error importing library: {e}")

# dependency for numpy
try:
    import numpy as np
except ImportError as e:
    print(f"Error importing library: {e}")

_COLOR_SYMBOLS = frozenset({"W", "U", "B", "R", "G"})
_PIP_RE = re.compile(r'\{([^}]+)\}')

# maximum and minimum converted mana cost, ignoring basic lands
def deck_max_cmc(deck: Deck) -> int:
    """Return the highest integer CMC bucket present in the deck."""
    return max(int(entry.card.cmc) for entry in deck.entries if not is_basic_land(entry.card))

# minimum converted mana cost, ignoring basic lands
def deck_min_cmc(deck: Deck) -> int:
    """Return the lowest integer CMC bucket present in the deck."""
    return min(int(entry.card.cmc) for entry in deck.entries if not is_basic_land(entry.card))

# CMC values as an array of integers, weighted by copy count, ignoring basic lands
def _deck_cmc_values(deck: Deck) -> np.ndarray:
    non_land = [entry for entry in deck.entries if not is_basic_land(entry.card)]
    values = np.array([int(entry.card.cmc) for entry in non_land], dtype=int)
    counts = np.array([entry.count for entry in non_land], dtype=int)
    return np.repeat(values, counts)

# distribution of CMC values, ignoring basic lands
def deck_cmc_distribution(deck: Deck) -> tuple[np.ndarray, np.ndarray]:
    """Build a distribution of card counts by converted mana cost (CMC).

    Returns a tuple of counts and bin edges, in the same shape as :func:`numpy.histogram`.
    """
    buckets = np.bincount(_deck_cmc_values(deck))
    return buckets, np.arange(len(buckets) + 1)

# build a histogram of CMC values, ignoring basic lands
def deck_cmc_histogram(deck: Deck) -> tuple[np.ndarray, np.ndarray]:
    """Build a histogram of card counts by converted mana cost (CMC).

    Returns a tuple of counts and bin edges, in the same shape as :func:`numpy.histogram`.
    """
    cmc_values = _deck_cmc_values(deck)
    if len(cmc_values) == 0:
        return np.array([], dtype=int), np.array([0], dtype=int)
    max_cmc = int(cmc_values.max())
    bins = np.arange(max_cmc + 2)
    return np.histogram(cmc_values, bins=bins) 

# average converted mana cost, ignoring basic lands, weighted by copy count
def deck_average_cmc(deck: Deck) -> float:
    """Return the mean CMC of all non-land cards, weighted by copy count."""
    values = _deck_cmc_values(deck)
    if len(values) == 0:
        raise ValueError("Deck has no non-land cards")
    return float(np.mean(values))

def deck_type_distribution(deck: Binder) -> dict[str, int]:
    """Count cards by primary card type, weighted by copy count.

    A card matching multiple types (e.g. Artifact Creature) is counted in each.
    Cards matching no known type go into 'Other'.
    """
    dist: dict[str, int] = {t: 0 for t in CARD_TYPES}
    dist["Other"] = 0
    for entry in deck.entries:
        main = (entry.card.type_line or "").split("—")[0]  # strip subtype after em-dash
        matched = False
        for card_type in CARD_TYPES:
            if card_type.lower() in main.lower():
                dist[card_type] += entry.count
                matched = True
        if not matched:
            dist["Other"] += entry.count
    return {k: v for k, v in dist.items() if v > 0}


def _count_pips(mana_cost: str) -> dict[str, int]:
    pips: dict[str, int] = {}
    for symbol in _PIP_RE.findall(mana_cost):
        for part in symbol.split("/"):
            if part in _COLOR_SYMBOLS:
                pips[part] = pips.get(part, 0) + 1
    return pips


def deck_color_distribution(deck: Binder) -> dict[str, int]:
    """Count colored mana pips across all non-basic-land cards, weighted by copy count."""
    totals: dict[str, int] = {}
    for entry in deck.entries:
        if is_basic_land(entry.card):
            continue
        for color, count in _count_pips(entry.card.mana_cost or "").items():
            totals[color] = totals.get(color, 0) + count * entry.count
    return totals


def validate_legality(deck: Binder, format_name: str) -> list[str]:
    """Return card names that are not legal in the given format.

    Raises ValueError for unknown format names.
    Cards missing legality data are skipped.
    """
    fmt = format_name.lower()
    if fmt not in LEGAL_FORMATS:
        raise ValueError(f"Unknown format {format_name!r}. Valid formats: {LEGAL_FORMATS}")
    illegal = []
    for entry in deck.entries:
        legalities = entry.card.legalities
        if legalities is None:
            continue
        if legalities.get(fmt, "not_legal") not in ("legal", "restricted"):
            illegal.append(entry.card.name)
    return illegal


def deck_diff(deck_a: Binder, deck_b: Binder) -> dict:
    """Compare two decks and return added, removed, and count-changed entries.

    Returns:
        {
          "added":   [Entry, ...],   # in deck_b but not deck_a
          "removed": [Entry, ...],   # in deck_a but not deck_b
          "changed": [{"card": name, "from": old_count, "to": new_count}, ...]
        }
    """
    map_a = {e.card.id: e for e in deck_a.entries}
    map_b = {e.card.id: e for e in deck_b.entries}
    added, removed, changed = [], [], []
    for card_id in set(map_a) | set(map_b):
        in_a = map_a.get(card_id)
        in_b = map_b.get(card_id)
        if in_a is None:
            added.append(in_b)
        elif in_b is None:
            removed.append(in_a)
        elif in_a.count != in_b.count:
            changed.append({"card": in_a.card.name, "from": in_a.count, "to": in_b.count})
    return {"added": added, "removed": removed, "changed": changed}


_BASIC_LAND_COLOR_MAP = {
    "island": "U", "plains": "W", "swamp": "B", "mountain": "R", "forest": "G",
}


def mana_base_analysis(deck: Binder) -> dict:
    """Analyze the mana base health of a deck.

    Returns:
        {
          "pip_requirements": {color: total_pips},   # from non-land spells
          "mana_sources":     {color: total_sources}, # from lands
          "warnings":         [str, ...]
        }
    """
    pip_requirements: dict[str, int] = {}
    mana_sources: dict[str, int] = {}
    total_lands = 0

    for entry in deck.entries:
        card = entry.card
        is_land = "Land" in (card.type_line or "")
        if is_land:
            total_lands += entry.count
            sources = list(card.produced_mana or [])
            if not sources:
                color = _BASIC_LAND_COLOR_MAP.get((card.name or "").lower())
                if color:
                    sources = [color]
            for c in sources:
                cu = c.upper()
                if cu in _COLOR_SYMBOLS:
                    mana_sources[cu] = mana_sources.get(cu, 0) + entry.count
        else:
            for color, count in _count_pips(card.mana_cost or "").items():
                pip_requirements[color] = pip_requirements.get(color, 0) + count * entry.count

    warnings = []
    total_pips = sum(pip_requirements.values())
    for color in _COLOR_SYMBOLS:
        req = pip_requirements.get(color, 0)
        src = mana_sources.get(color, 0)
        if req == 0 and src == 0:
            continue
        if req > 0 and src == 0:
            warnings.append(f"No {color} mana sources but {req} pip(s) required")
        elif total_pips > 0 and total_lands > 0:
            pip_ratio = req / total_pips
            src_ratio = src / total_lands
            if pip_ratio > 0.15 and src_ratio < pip_ratio * 0.5:
                warnings.append(
                    f"{color}: {req} pip(s) needed ({pip_ratio:.0%} of total) "
                    f"but only {src}/{total_lands} land sources ({src_ratio:.0%} of lands)"
                )
    if total_lands == 0 and pip_requirements:
        warnings.append("No lands in deck")

    return {
        "pip_requirements": pip_requirements,
        "mana_sources": mana_sources,
        "warnings": warnings,
    }


__all__ = [
    "deck_cmc_distribution",
    "deck_cmc_histogram",
    "deck_max_cmc",
    "deck_min_cmc",
    "deck_average_cmc",
    "deck_type_distribution",
    "deck_color_distribution",
    "validate_legality",
    "deck_diff",
    "mana_base_analysis",
]
