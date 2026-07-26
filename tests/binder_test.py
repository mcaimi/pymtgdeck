from utils import _load_card_from_json_file, DATA_DIR
from pymtgdeck import Binder, Entry
import pytest

# test the Binder class
def test_binder_create():
    # create a Binder object
    binder = Binder(name="Test Binder")
    assert binder.name == "Test Binder"
    assert binder.entries == []

# test the Binder class
def test_binder_add_card():
    # create a Binder object
    binder = Binder(name="Test Binder")
    assert binder.name == "Test Binder"

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # add card to binder
    binder.add_card(card)
    assert binder.entries == [Entry(card=card, count=1)]

    # add card to binder again, should increment count by 1
    binder.add_card(card)
    assert binder.entries == [Entry(card=card, count=2)]

    # add card to binder with count
    binder.add_card(card, 3)
    assert binder.entries == [Entry(card=card, count=5)]

    # add another card to binder
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    binder.add_card(card2)
    assert binder.entries == [Entry(card=card, count=5), Entry(card=card2, count=1)]

    # add another card to binder with count
    binder.add_card(card2, 2)
    assert binder.entries == [Entry(card=card, count=5), Entry(card=card2, count=3)]

    # add another card to binder with count
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')
    binder.add_card(card3, 3)
    assert binder.entries == [Entry(card=card, count=5), Entry(card=card2, count=3), Entry(card=card3, count=3)]

# add card to binder and check if it is in the binder
def test_binder_has_card():
    # create a Binder object
    binder = Binder()

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # add card to binder
    binder.add_card(card)

    # check if card is in binder
    assert binder.has_card(card) == True

    # check if card is not in binder
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    assert binder.has_card(card2) == False

# test remove card from binder
def test_binder_remove_card():
    # create a Binder object
    binder = Binder()

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')

    # add card to binder
    binder.add_card(card)
    assert binder.entries == [Entry(card=card, count=1)]

    # remove card from binder
    binder.remove_card(card)
    assert binder.entries == []

    # try to remove card that is not in binder
    with pytest.raises(ValueError):
        binder.remove_card(card)

    # add card to binder again
    binder.add_card(card, 2)
    assert binder.entries == [Entry(card=card, count=2)]

    # remove card from binder, should decrement count by 1
    binder.remove_card(card)
    assert binder.get_card_count(card) == 1

    # remove card from binder, should remove card from binder
    binder.remove_card(card)
    assert binder.entries == []

    # add all three cards to binder
    binder.add_card(card)
    binder.add_card(card2)
    binder.add_card(card3)
    assert binder.entries == [Entry(card=card, count=1), Entry(card=card2, count=1), Entry(card=card3, count=1)]

    # remove card from binder, should remove card from binder
    binder.remove_card(card)
    assert binder.entries == [Entry(card=card2, count=1), Entry(card=card3, count=1)]

# test has_card method
def test_binder_has_card():
    # create a Binder object
    binder = Binder()

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # add card to binder
    binder.add_card(card)
    assert binder.has_card(card) == True

# test serialization
def test_binder_serialization():
    # create a Binder object
    binder = Binder(name="Test Binder")
    assert binder.name == "Test Binder"

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json') 

    # add cards to binder
    binder.add_card(card)
    binder.add_card(card2)
    binder.add_card(card3)
    assert binder.to_dict() == {'name': "Test Binder", 'entries': [Entry(card=card, count=1).to_dict(), Entry(card=card2, count=1).to_dict(), Entry(card=card3, count=1).to_dict()]}

# test deserialization
def test_binder_deserialization():
    # create a Binder object
    binder = Binder(name="Test Binder")
    assert binder.name == "Test Binder"

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')

    # add cards to binder
    binder.add_card(card)
    binder.add_card(card2)
    binder.add_card(card3)
    assert binder.to_dict() == {'name': "Test Binder", 'entries': [Entry(card=card, count=1).to_dict(), Entry(card=card2, count=1).to_dict(), Entry(card=card3, count=1).to_dict()]}

    # deserialize binder
    binder2 = Binder.from_dict(binder.to_dict())
    assert binder2.entries == binder.entries


# ---------------------------------------------------------------------------
# Binder.search
# ---------------------------------------------------------------------------

def test_binder_search_by_name():
    binder = Binder()
    card1 = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')  # Sengir Vampire
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')  # Counterspell
    binder.add_card(card1)
    binder.add_card(card2)
    results = binder.search(name="Sengir")
    assert len(results) == 1
    assert results[0].card.name == "Sengir Vampire"


def test_binder_search_by_card_type():
    binder = Binder()
    card1 = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')  # Creature
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')  # Instant
    binder.add_card(card1)
    binder.add_card(card2)
    creatures = binder.search(card_type="Creature")
    assert len(creatures) == 1
    assert creatures[0].card.name == "Sengir Vampire"


def test_binder_search_by_cmc_range():
    binder = Binder()
    card_cmc5 = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')  # CMC 5
    card_cmc2 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')  # CMC 2
    binder.add_card(card_cmc5)
    binder.add_card(card_cmc2)
    low = binder.search(cmc_max=3)
    assert len(low) == 1
    assert low[0].card.name == "Counterspell"
    high = binder.search(cmc_min=4)
    assert len(high) == 1
    assert high[0].card.name == "Sengir Vampire"


def test_binder_search_by_color():
    binder = Binder()
    card_black = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')  # Black
    card_blue = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')   # Blue
    binder.add_card(card_black)
    binder.add_card(card_blue)
    blue_cards = binder.search(color="U")
    assert len(blue_cards) == 1
    assert blue_cards[0].card.name == "Counterspell"


def test_binder_search_combined_filters():
    binder = Binder()
    card1 = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')  # Creature, CMC 5, Black
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')  # Instant, CMC 2, Blue
    binder.add_card(card1)
    binder.add_card(card2)
    results = binder.search(card_type="Instant", cmc_max=3)
    assert len(results) == 1
    assert results[0].card.name == "Counterspell"


def test_binder_search_no_match():
    binder = Binder()
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    binder.add_card(card)
    assert binder.search(name="Nonexistent Card") == []


def test_binder_search_empty_binder():
    assert Binder().search(name="anything") == []