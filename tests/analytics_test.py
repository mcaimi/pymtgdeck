import numpy as np
import pytest

from utils import _load_card_from_json_file, DATA_DIR
from pyscryfall import ScryfallCard

from pymtgdeck import Deck, Binder
from pymtgdeck.entities.analytics import (
    deck_cmc_distribution,
    deck_cmc_histogram,
    deck_max_cmc,
    deck_min_cmc,
    deck_average_cmc,
    deck_type_distribution,
    deck_color_distribution,
    validate_legality,
    deck_diff,
    mana_base_analysis,
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


# ---------------------------------------------------------------------------
# Helpers for new analytics tests
# ---------------------------------------------------------------------------

def _make_card(
    card_id: str,
    name: str,
    type_line: str,
    mana_cost: str | None = None,
    cmc: float = 0.0,
    colors: list[str] | None = None,
    legalities: dict | None = None,
    produced_mana: list[str] | None = None,
) -> ScryfallCard:
    return ScryfallCard(
        object="card",
        id=card_id,
        name=name,
        type_line=type_line,
        mana_cost=mana_cost,
        cmc=cmc,
        colors=colors or [],
        color_identity=colors or [],
        legalities=legalities,
        produced_mana=produced_mana,
    )


# ---------------------------------------------------------------------------
# deck_type_distribution
# ---------------------------------------------------------------------------

def test_deck_type_distribution_basic():
    creature = _make_card("c1", "Vampire", "Creature — Vampire", mana_cost="{3}{B}{B}", cmc=5.0, colors=["B"])
    instant = _make_card("c2", "Counter", "Instant", mana_cost="{U}{U}", cmc=2.0, colors=["U"])
    deck = Deck(max_card_count=10)
    deck.add_card(creature, 2)
    deck.add_card(instant, 3)
    dist = deck_type_distribution(deck)
    assert dist["Creature"] == 2
    assert dist["Instant"] == 3
    assert "Land" not in dist


def test_deck_type_distribution_multitype():
    artifact_creature = _make_card("c1", "Golem", "Artifact Creature — Golem", mana_cost="{5}", cmc=5.0)
    deck = Deck()
    deck.add_card(artifact_creature, 4)
    dist = deck_type_distribution(deck)
    assert dist["Artifact"] == 4
    assert dist["Creature"] == 4


def test_deck_type_distribution_unknown_type():
    # "Scheme" is a real MTG type not in CARD_TYPES → should land in "Other"
    weird = _make_card("c1", "My Scheme", "Scheme", mana_cost=None, cmc=0.0)
    deck = Deck()
    deck.add_card(weird)
    dist = deck_type_distribution(deck)
    assert dist.get("Other", 0) == 1


def test_deck_type_distribution_empty():
    dist = deck_type_distribution(Deck())
    assert dist == {}


# ---------------------------------------------------------------------------
# deck_color_distribution
# ---------------------------------------------------------------------------

def test_deck_color_distribution_single_color():
    card = _load_card_from_json_file(DATA_DIR / "card-example-1.json")  # {3}{B}{B}
    deck = Deck(max_card_count=10)
    deck.add_card(card, 2)
    dist = deck_color_distribution(deck)
    assert dist["B"] == 4  # 2 pips × 2 copies


def test_deck_color_distribution_multi_color():
    card = _make_card("c1", "Spell", "Instant", mana_cost="{W}{U}", cmc=2.0, colors=["W", "U"])
    deck = Deck()
    deck.add_card(card, 3)
    dist = deck_color_distribution(deck)
    assert dist["W"] == 3
    assert dist["U"] == 3


def test_deck_color_distribution_hybrid():
    card = _make_card("c1", "Hybrid", "Instant", mana_cost="{W/U}", cmc=1.0, colors=["W", "U"])
    deck = Deck()
    deck.add_card(card)
    dist = deck_color_distribution(deck)
    assert dist["W"] == 1
    assert dist["U"] == 1


def test_deck_color_distribution_excludes_colorless():
    card = _make_card("c1", "Rock", "Artifact", mana_cost="{3}", cmc=3.0)
    deck = Deck()
    deck.add_card(card)
    dist = deck_color_distribution(deck)
    assert dist == {}


def test_deck_color_distribution_empty():
    assert deck_color_distribution(Deck()) == {}


# ---------------------------------------------------------------------------
# validate_legality
# ---------------------------------------------------------------------------

def _legalities(fmt: str, status: str) -> dict:
    from pymtgdeck import LEGAL_FORMATS
    return {f: ("legal" if f == fmt and status == "legal" else "not_legal") for f in LEGAL_FORMATS}


def test_validate_legality_all_legal():
    card = _make_card("c1", "Bolt", "Instant", legalities=_legalities("modern", "legal"))
    deck = Deck()
    deck.add_card(card)
    assert validate_legality(deck, "modern") == []


def test_validate_legality_returns_illegal_cards():
    legal_card = _make_card("c1", "Legal", "Instant", legalities=_legalities("modern", "legal"))
    banned = _legalities("modern", "not_legal")
    illegal_card = _make_card("c2", "Banned", "Sorcery", legalities=banned)
    deck = Deck()
    deck.add_card(legal_card)
    deck.add_card(illegal_card)
    illegal = validate_legality(deck, "modern")
    assert "Banned" in illegal
    assert "Legal" not in illegal


def test_validate_legality_unknown_format_raises():
    deck = Deck()
    with pytest.raises(ValueError, match="Unknown format"):
        validate_legality(deck, "nonexistent_format")


def test_validate_legality_skips_cards_without_legality_data():
    card = _make_card("c1", "NoData", "Creature", legalities=None)
    deck = Deck()
    deck.add_card(card)
    assert validate_legality(deck, "modern") == []


# ---------------------------------------------------------------------------
# deck_diff
# ---------------------------------------------------------------------------

def test_deck_diff_added():
    card = _load_card_from_json_file(DATA_DIR / "card-example-1.json")
    a = Binder()
    b = Binder()
    b.add_card(card, 2)
    diff = deck_diff(a, b)
    assert len(diff["added"]) == 1
    assert diff["added"][0].card.name == card.name
    assert diff["removed"] == []
    assert diff["changed"] == []


def test_deck_diff_removed():
    card = _load_card_from_json_file(DATA_DIR / "card-example-1.json")
    a = Binder()
    a.add_card(card, 2)
    b = Binder()
    diff = deck_diff(a, b)
    assert len(diff["removed"]) == 1
    assert diff["added"] == []
    assert diff["changed"] == []


def test_deck_diff_changed_count():
    card = _load_card_from_json_file(DATA_DIR / "card-example-1.json")
    a = Binder()
    a.add_card(card, 2)
    b = Binder()
    b.add_card(card, 4)
    diff = deck_diff(a, b)
    assert diff["added"] == []
    assert diff["removed"] == []
    assert len(diff["changed"]) == 1
    assert diff["changed"][0] == {"card": card.name, "from": 2, "to": 4}


def test_deck_diff_identical():
    card = _load_card_from_json_file(DATA_DIR / "card-example-3.json")
    a = Binder()
    a.add_card(card, 3)
    b = Binder()
    b.add_card(card, 3)
    diff = deck_diff(a, b)
    assert diff == {"added": [], "removed": [], "changed": []}


# ---------------------------------------------------------------------------
# mana_base_analysis
# ---------------------------------------------------------------------------

def test_mana_base_analysis_basic():
    spell = _make_card("c1", "Spell", "Instant", mana_cost="{U}{U}", cmc=2.0, colors=["U"])
    island = _make_card("isl", "Island", "Basic Land — Island", produced_mana=["U"], colors=[])
    deck = Deck(max_card_count=20)
    deck.add_card(spell, 4)
    deck.add_card(island, 8)
    result = mana_base_analysis(deck)
    assert result["pip_requirements"]["U"] == 8   # 2 pips × 4 copies
    assert result["mana_sources"]["U"] == 8
    assert result["warnings"] == []


def test_mana_base_analysis_missing_sources_warning():
    spell = _make_card("c1", "Spell", "Instant", mana_cost="{B}{B}", cmc=2.0, colors=["B"])
    deck = Deck(max_card_count=10)
    deck.add_card(spell, 4)
    result = mana_base_analysis(deck)
    assert result["pip_requirements"]["B"] == 8
    assert "B" not in result["mana_sources"]
    assert any("B" in w and "sources" in w for w in result["warnings"])


def test_mana_base_analysis_basic_land_fallback():
    island = _make_card("isl", "Island", "Basic Land — Island",
                        produced_mana=None, colors=[])  # produced_mana absent
    deck = Deck(max_card_count=10)
    deck.add_card(island, 5)
    result = mana_base_analysis(deck)
    assert result["mana_sources"].get("U", 0) == 5


def test_mana_base_analysis_empty():
    result = mana_base_analysis(Deck())
    assert result["pip_requirements"] == {}
    assert result["mana_sources"] == {}
    assert result["warnings"] == []
