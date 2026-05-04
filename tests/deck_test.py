from utils import _load_card_from_json_file, DATA_DIR
from pymtgdeck import Deck, Entry
import pytest

# test the Deck class
def test_deck_create():
    # create a Deck object
    deck = Deck()

    # check deck attributes
    assert deck.name == "MTG Deck (Default)"
    assert deck.entries == []
    assert deck.max_card_copy_count == 4
    assert deck.max_card_count == 40

# test the Deck class
def test_deck_add_card():
    # create a Deck object
    deck = Deck(name="Test Deck")
    assert deck.name == "Test Deck"

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # add card to deck
    deck.add_card(card)
    assert deck.has_card(card) == True and deck.get_card_copy_count(card) == 1

    # add card to deck again, should increment count by 1
    deck.add_card(card)
    assert deck.has_card(card) == True and deck.get_card_copy_count(card) == 2

    # add card to deck with count
    with pytest.raises(ValueError):
        deck.add_card(card, 3)

# test remove card from deck
def test_deck_remove_card():
    # create a Deck object
    deck = Deck(name="Test Deck")
    assert deck.name == "Test Deck"

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')

    # add card to deck
    deck.add_card(card)
    assert deck.has_card(card) == True and deck.get_card_copy_count(card) == 1

    # remove card from deck
    deck.remove_card(card)
    assert deck.has_card(card) == False and deck.get_card_copy_count(card) == 0

    # try to remove card that is not in deck
    with pytest.raises(ValueError):
        deck.remove_card(card)

    # add card to deck again
    deck.add_card(card, 2)
    assert deck.has_card(card) == True and deck.get_card_copy_count(card) == 2

    # remove card from deck, should decrement count by 1
    deck.remove_card(card)
    assert deck.has_card(card) == True and deck.get_card_copy_count(card) == 1

    # remove card from deck, should remove card from deck
    deck.remove_card(card)
    assert deck.has_card(card) == False and deck.get_card_copy_count(card) == 0

    # add all three cards to deck
    deck.add_card(card)
    deck.add_card(card2)
    deck.add_card(card3)
    assert deck.has_card(card) == True and deck.get_card_copy_count(card) == 1
    assert deck.has_card(card2) == True and deck.get_card_copy_count(card2) == 1
    assert deck.has_card(card3) == True and deck.get_card_copy_count(card3) == 1

    # remove card from deck, should remove card from deck
    deck.remove_card(card)
    assert deck.has_card(card) == False and deck.get_card_copy_count(card) == 0
    assert deck.has_card(card2) == True and deck.get_card_copy_count(card2) == 1
    assert deck.has_card(card3) == True and deck.get_card_copy_count(card3) == 1

# test exceed max card copy count
def test_deck_exceed_max_card_copy_count():
    # create a Deck object
    deck = Deck(name="Test Deck")
    assert deck.name == "Test Deck"

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # add card to deck
    deck.add_card(card)
    assert deck.has_card(card) == True and deck.get_card_copy_count(card) == 1

    # try to add card to deck with count that exceeds max card copy count
    with pytest.raises(ValueError):
        deck.add_card(card, 5)

# test exceed max card count
def test_deck_exceed_max_card_count():
    # create a Deck object
    deck = Deck(max_card_count=2, name="Test Deck")
    assert deck.name == "Test Deck"

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')

    # add card to deck
    deck.add_card(card)
    deck.add_card(card2)

    # try to add card to deck, should raise ValueError
    with pytest.raises(ValueError):
        deck.add_card(card3)

# test is full
def test_deck_is_full():
    # create a Deck object
    deck = Deck(max_card_count=3)

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')

    # add cards to deck
    deck.add_card(card)
    deck.add_card(card2)
    deck.add_card(card3)

    # check if deck is full
    assert deck.is_full() == True

    # try to add card to deck, should raise ValueError
    with pytest.raises(ValueError):
        deck.add_card(card)

    # remove card from deck
    deck.remove_card(card)
    assert deck.is_full() == False

    # remove remaining cards from deck
    deck.remove_card(card2)
    deck.remove_card(card3)
    assert deck.is_full() == False
    assert deck.is_empty() == True

# test serialization
def test_deck_serialization():
    # create a Deck object
    deck = Deck()

    # load card from json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')

    # add cards to deck
    deck.add_card(card)
    deck.add_card(card2, 2)
    deck.add_card(card3, 3)

    # serialize deck
    deck_dict = deck.to_dict()
    assert deck_dict['entries'] == [Entry(card=card, count=1).to_dict(), Entry(card=card2, count=2).to_dict(), Entry(card=card3, count=3).to_dict()]
    assert deck_dict['max_card_copy_count'] == 4
    assert deck_dict['max_card_count'] == 40

    # deserialize deck
    deck2 = Deck.from_dict(deck_dict)
    assert deck2.entries == deck.entries
    assert deck2.max_card_copy_count == deck.max_card_copy_count
    assert deck2.max_card_count == deck.max_card_count