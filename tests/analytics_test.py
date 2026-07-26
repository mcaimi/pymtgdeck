import numpy as np
import pytest

from utils import _load_card_from_json_file, DATA_DIR

from pymtgdeck import Deck
from pymtgdeck.entities.analytics import (
    deck_cmc_distribution,
    deck_cmc_histogram,
    deck_max_cmc,
    deck_min_cmc,
    deck_average_cmc,
)


def _deck_with_mixed_cmc_entries() -> Deck:
    deck = Deck(max_card_count=10)
    card_cmc_5 = _load_card_from_json_file(DATA_DIR / "card-example-1.json")
    card_cmc_2 = _load_card_from_json_file(DATA_DIR / "card-example-3.json")
    deck.add_card(card_cmc_5, 2)
    deck.add_card(card_cmc_2, 3)
    return deck


def test_deck_cmc_distribution_empty():
    deck = Deck()
    counts, bin_edges = deck_cmc_distribution(deck)
    assert np.array_equal(counts, np.array([], dtype=int))
    assert np.array_equal(bin_edges, np.array([0], dtype=int))


def test_deck_cmc_distribution_weighted_by_count():
    # 2 copies at CMC 5, 3 copies at CMC 2 → counts reflect copy counts
    deck = _deck_with_mixed_cmc_entries()
    counts, bin_edges = deck_cmc_distribution(deck)
    assert np.array_equal(counts, np.array([0, 0, 3, 0, 0, 2], dtype=int))
    assert np.array_equal(bin_edges, np.array([0, 1, 2, 3, 4, 5, 6], dtype=int))


def test_deck_cmc_distribution_counts_copies():
    # 4 copies at CMC 2 → count bucket should be 4
    deck = Deck()
    card = _load_card_from_json_file(DATA_DIR / "card-example-3.json")
    deck.add_card(card, 4)
    counts, _ = deck_cmc_distribution(deck)
    assert np.array_equal(counts, np.array([0, 0, 4], dtype=int))


def test_deck_cmc_distribution_single_bucket():
    deck = Deck()
    card = _load_card_from_json_file(DATA_DIR / "card-example-3.json")
    deck.add_card(card)
    counts, bin_edges = deck_cmc_distribution(deck)
    assert np.array_equal(counts, np.array([0, 0, 1], dtype=int))
    assert np.array_equal(bin_edges, np.array([0, 1, 2, 3], dtype=int))


def test_deck_cmc_distribution_truncates_fractional_cmc():
    deck = Deck(max_card_count=10)
    card = _load_card_from_json_file(DATA_DIR / "card-example-3.json")
    card.cmc = 2.9
    deck.add_card(card, 2)
    counts, bin_edges = deck_cmc_distribution(deck)
    assert np.array_equal(counts, np.array([0, 0, 2], dtype=int))
    assert np.array_equal(bin_edges, np.array([0, 1, 2, 3], dtype=int))


def test_deck_cmc_histogram_empty():
    deck = Deck()
    counts, bin_edges = deck_cmc_histogram(deck)
    assert np.array_equal(counts, np.array([], dtype=int))
    assert np.array_equal(bin_edges, np.array([0], dtype=int))


def test_deck_cmc_histogram_from_distribution():
    # 2 copies at CMC 5, 3 copies at CMC 2
    deck = _deck_with_mixed_cmc_entries()
    counts, bin_edges = deck_cmc_histogram(deck)
    assert np.array_equal(counts, np.array([0, 0, 3, 0, 0, 2], dtype=int))
    assert np.array_equal(bin_edges, np.array([0, 1, 2, 3, 4, 5, 6], dtype=int))


def test_deck_cmc_histogram_single_bucket():
    deck = Deck()
    card = _load_card_from_json_file(DATA_DIR / "card-example-3.json")
    deck.add_card(card)
    counts, bin_edges = deck_cmc_histogram(deck)
    assert np.array_equal(counts, np.array([0, 0, 1], dtype=int))
    assert np.array_equal(bin_edges, np.array([0, 1, 2, 3], dtype=int))


def test_deck_min_max_cmc():
    deck = _deck_with_mixed_cmc_entries()
    assert deck_min_cmc(deck) == 2
    assert deck_max_cmc(deck) == 5


def test_deck_min_max_cmc_single_bucket():
    deck = Deck()
    card = _load_card_from_json_file(DATA_DIR / "card-example-3.json")
    deck.add_card(card)
    assert deck_min_cmc(deck) == 2
    assert deck_max_cmc(deck) == 2


def test_deck_min_max_cmc_empty_raises():
    deck = Deck()
    with pytest.raises(ValueError):
        deck_min_cmc(deck)
    with pytest.raises(ValueError):
        deck_max_cmc(deck)


def test_deck_average_cmc():
    # 2 copies at CMC 5, 3 copies at CMC 2 → (5+5+2+2+2)/5 = 16/5 = 3.2
    deck = _deck_with_mixed_cmc_entries()
    assert deck_average_cmc(deck) == pytest.approx(3.2)


def test_deck_average_cmc_single_card():
    deck = Deck()
    card = _load_card_from_json_file(DATA_DIR / "card-example-3.json")
    deck.add_card(card, 4)
    assert deck_average_cmc(deck) == pytest.approx(2.0)


def test_deck_average_cmc_empty_raises():
    deck = Deck()
    with pytest.raises(ValueError):
        deck_average_cmc(deck)
