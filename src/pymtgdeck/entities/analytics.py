#! /usr/bin/env python

# card/deck analytics

try:
    from .deck import Deck
    from .types import is_basic_land
except ImportError as e:
    print(f"Error importing library: {e}")

# dependency for numpy
try:
    import numpy as np
except ImportError as e:
    print(f"Error importing library: {e}")

# maximum and minimum converted mana cost, ignoring basic lands
def deck_max_cmc(deck: Deck) -> int:
    """Return the highest integer CMC bucket present in the deck."""
    return max(int(entry.card.cmc) for entry in deck.entries if not is_basic_land(entry.card))

# minimum converted mana cost, ignoring basic lands
def deck_min_cmc(deck: Deck) -> int:
    """Return the lowest integer CMC bucket present in the deck."""
    return min(int(entry.card.cmc) for entry in deck.entries if not is_basic_land(entry.card))

# CMC values as an array of integers, ignoring basic lands
def _deck_cmc_values(deck: Deck) -> np.ndarray:
    return np.array([entry.card.cmc for entry in deck.entries if not is_basic_land(entry.card)], dtype=int)

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
        return np.array([], dtype=int), np.array([], dtype=int)
    max_cmc = int(cmc_values.max())
    bins = np.arange(max_cmc + 2)
    return np.histogram(cmc_values, bins=bins) 

__all__ = ["deck_cmc_distribution", "deck_cmc_histogram", "deck_max_cmc", "deck_min_cmc"]
