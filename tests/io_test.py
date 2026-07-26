from unittest.mock import patch

import pytest

from utils import _load_card_from_json_file, DATA_DIR
from pymtgdeck import Deck
from pymtgdeck.io import deck_to_text, deck_from_text


def _card_lookup_factory(*card_files):
    """Return a mock side_effect that maps card names to pre-loaded cards."""
    cards = {_load_card_from_json_file(f).name: _load_card_from_json_file(f) for f in card_files}

    def lookup(name, **kwargs):
        if name not in cards:
            raise ValueError(f"Unknown card: {name!r}")
        return cards[name]

    return lookup, cards


def test_deck_to_text():
    lookup, cards = _card_lookup_factory(
        DATA_DIR / 'card-example-1.json',
        DATA_DIR / 'card-example-3.json',
    )
    card1 = cards['Sengir Vampire']
    card2 = cards['Counterspell']

    deck = Deck(max_card_count=10)
    deck.add_card(card1, 2)
    deck.add_card(card2, 3)

    text = deck_to_text(deck)
    assert text == "2 Sengir Vampire\n3 Counterspell"


def test_deck_to_text_empty():
    assert deck_to_text(Deck()) == ""


def test_deck_from_text_parses_entries():
    lookup, cards = _card_lookup_factory(
        DATA_DIR / 'card-example-1.json',
        DATA_DIR / 'card-example-3.json',
    )
    card1 = cards['Sengir Vampire']
    card2 = cards['Counterspell']

    text = "2 Sengir Vampire\n3 Counterspell"

    with patch('pymtgdeck.io.search_card_by_name_exact', side_effect=lookup):
        deck = deck_from_text(text, Deck(max_card_count=10))

    assert deck.get_card_copy_count(card1) == 2
    assert deck.get_card_copy_count(card2) == 3


def test_deck_from_text_skips_comments():
    lookup, cards = _card_lookup_factory(DATA_DIR / 'card-example-3.json')
    card = cards['Counterspell']

    text = "// This is a header\n4 Counterspell\n// trailing comment"

    with patch('pymtgdeck.io.search_card_by_name_exact', side_effect=lookup):
        deck = deck_from_text(text, Deck())

    assert deck.get_card_copy_count(card) == 4


def test_deck_from_text_skips_blank_lines():
    lookup, cards = _card_lookup_factory(DATA_DIR / 'card-example-1.json')
    card = cards['Sengir Vampire']

    text = "\n1 Sengir Vampire\n\n"

    with patch('pymtgdeck.io.search_card_by_name_exact', side_effect=lookup):
        deck = deck_from_text(text, Deck())

    assert deck.get_card_copy_count(card) == 1


def test_deck_from_text_invalid_line_raises():
    text = "Sengir Vampire"  # missing count prefix
    with patch('pymtgdeck.io.search_card_by_name_exact'):
        with pytest.raises(ValueError, match="Cannot parse"):
            deck_from_text(text, Deck())


def test_deck_from_text_default_deck():
    lookup, cards = _card_lookup_factory(DATA_DIR / 'card-example-3.json')
    card = cards['Counterspell']

    text = "1 Counterspell"

    with patch('pymtgdeck.io.search_card_by_name_exact', side_effect=lookup):
        deck = deck_from_text(text)  # no deck argument → creates default Deck

    assert isinstance(deck, Deck)
    assert deck.get_card_copy_count(card) == 1


def test_deck_to_text_then_import_roundtrip():
    lookup, cards = _card_lookup_factory(
        DATA_DIR / 'card-example-1.json',
        DATA_DIR / 'card-example-2.json',
    )
    card1 = cards['Sengir Vampire']
    card2 = cards['Mageta the Lion']

    deck = Deck(max_card_count=10)
    deck.add_card(card1, 3)
    deck.add_card(card2, 2)

    text = deck_to_text(deck)

    with patch('pymtgdeck.io.search_card_by_name_exact', side_effect=lookup):
        deck2 = deck_from_text(text, Deck(max_card_count=10))

    assert deck2.entries == deck.entries
