from utils import _load_card_from_json_file, DATA_DIR
from pymtgdeck import Entry

# test the Entry class
def test_entry():
    # load a ScryfallCardList from a json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # create an Entry object
    entry = Entry(card, 1)
    assert entry.card.name == 'Sengir Vampire'
    assert entry.count == 1

# test Entry serialization
def test_entry_serialization():
    # load a ScryfallCardList from a json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # create an Entry object
    entry = Entry(card, 1)

    # serialize the Entry object to a dictionary
    dict = entry.to_dict()
    assert dict['card']['name'] == 'Sengir Vampire'
    assert dict['count'] == 1

# test equality
def test_entry_equality():
    # load a ScryfallCardList from a json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # create an Entry object
    entry1 = Entry(card, 1)
    entry2 = Entry(card, 1)
    assert entry1 == entry2

# test inequality (different card)
def test_entry_inequality():
    # load a ScryfallCardList from a json file
    card1 = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')

    # create an Entry object
    entry1 = Entry(card1, 1)
    entry2 = Entry(card2, 1)
    assert entry1 != entry2

# test inequality (different count)
def test_entry_inequality_different_count():
    # load a ScryfallCardList from a json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # create an Entry object
    entry1 = Entry(card, 1)
    entry2 = Entry(card, 2)
    assert entry1 != entry2

# test inequality (different card and count)
def test_entry_inequality_different_card_and_count():
    # load a ScryfallCardList from a json file
    card1 = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')

    # create an Entry object
    entry1 = Entry(card1, 1)
    entry2 = Entry(card2, 2)
    assert entry1 != entry2

# test hash
def test_entry_hash():
    # load a ScryfallCardList from a json file
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')

    # create an Entry object
    entry = Entry(card, 1)
    assert hash(entry) == hash((card.name, 1))