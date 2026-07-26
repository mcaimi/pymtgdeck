#!/usr/bin/env python

# test the backend

try:
    import hashlib
    from pymtgdeck.persistence.backend import Backend
    from utils import _load_card_from_json_file, DATA_DIR
    from pymtgdeck import Deck, Binder
    import pytest
    from pathlib import Path
    import shutil
except ImportError as e:
    print(f"Error: {e}")
    exit(1)

# test backend save and load
def test_backend_save_and_load():
    tmp_dir = Path('/tmp/pymtgdeck_test')
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)

    # create a temporary directory
    # load cards
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')

    # create deck
    deck = Deck(name="Test Deck")
    deck.add_card(card)
    deck.add_card(card2)
    deck.add_card(card3)

    # create backend
    backend = Backend(file_path=tmp_dir)

    # save deck
    deck_file_name = backend.save(deck)
    file_name = deck_file_name
    assert file_name == f'{hashlib.sha256(deck.name.encode()).hexdigest()}.json'

    # load deck
    deck2 = backend.load(file_name)
    assert deck2.name == deck.name
    assert deck2.max_card_copy_count == deck.max_card_copy_count
    assert deck2.max_card_count == deck.max_card_count
    assert deck2.entries == deck.entries

    # create binder
    binder = Binder(name="Test Binder")
    binder.add_card(card)
    binder.add_card(card2, 10)
    binder.add_card(card3, 2)

    # save binder
    file_name = backend.save(binder)
    assert file_name == f'{hashlib.sha256(binder.name.encode()).hexdigest()}.json'

    # load binder
    binder2 = backend.load(file_name)
    assert binder2.name == binder.name
    assert binder2.entries == binder.entries

    # try to save deck again, should raise a OSError
    with pytest.raises(OSError):
        backend.save(deck)

    # try to save binder again, should raise a OSError
    with pytest.raises(OSError):
        backend.save(binder)

    # overwrite=True must succeed and preserve the same filename
    deck.add_card(card3)
    overwrite_file_name = backend.save(deck, overwrite=True)
    assert overwrite_file_name == deck_file_name  # same hash → same filename

    # verify overwritten data round-trips correctly
    deck_reloaded = backend.load(overwrite_file_name)
    assert deck_reloaded.name == deck.name
    assert deck_reloaded.entries == deck.entries

    # remove temporary directory, even if it is not empty
    shutil.rmtree(tmp_dir)