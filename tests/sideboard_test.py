import hashlib
import shutil
from pathlib import Path

import pytest

from utils import _load_card_from_json_file, DATA_DIR
from pymtgdeck import Sideboard, Entry
from pymtgdeck.persistence.backend import Backend
from pyscryfall import ScryfallCard


def _basic_island() -> ScryfallCard:
    return ScryfallCard(
        object="card",
        id="island-id",
        name="Island",
        type_line="Basic Land — Island",
        cmc=0.0,
        mana_cost=None,
        produced_mana=["U"],
        colors=[],
        color_identity=["U"],
        legalities=None,
    )


def test_sideboard_create():
    sb = Sideboard(name="Test Sideboard")
    assert sb.name == "Test Sideboard"
    assert sb.max_card_count == 15
    assert sb.max_card_copy_count == 4
    assert sb.entries == []


def test_sideboard_add_card():
    sb = Sideboard(name="Test Sideboard")
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    sb.add_card(card)
    assert sb.get_card_copy_count(card) == 1
    sb.add_card(card)
    assert sb.get_card_copy_count(card) == 2


def test_sideboard_exceeds_15_cards():
    sb = Sideboard(name="Full Board")
    card1 = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-2.json')
    card3 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')
    # fill to 15 using copies of 3 cards (5+5+5)
    sb.add_card(card1, 4)
    sb.add_card(card2, 4)
    sb.add_card(card3, 4)
    # add 3 more to reach 15 via a different approach:
    # reset and fill properly
    sb2 = Sideboard(name="Full Board 2")
    # 15 slots with three cards × 4 copies each = 12, then 3 more
    sb2.add_card(card1, 4)
    sb2.add_card(card2, 4)
    sb2.add_card(card3, 4)
    # 12 cards so far; add 3 more basic lands (bypass copy limit)
    island = _basic_island()
    sb2.add_card(island, 3)
    assert sb2.get_card_count() == 15
    assert sb2.is_full()
    with pytest.raises(ValueError):
        sb2.add_card(island)


def test_sideboard_copy_limit():
    sb = Sideboard(name="Copy Test")
    card = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    sb.add_card(card, 4)
    with pytest.raises(ValueError):
        sb.add_card(card)


def test_sideboard_basic_land_bypasses_copy_limit():
    sb = Sideboard(name="Basic Test")
    island = _basic_island()
    # basic lands can exceed the normal copy limit
    for _ in range(8):
        sb.add_card(island)
    assert sb.get_card_copy_count(island) == 8


def test_sideboard_serialization_roundtrip():
    card1 = _load_card_from_json_file(DATA_DIR / 'card-example-1.json')
    card2 = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')
    sb = Sideboard(name="Round-trip Board")
    sb.add_card(card1, 2)
    sb.add_card(card2, 3)

    data = sb.to_dict()
    sb2 = Sideboard.from_dict(data)
    assert sb2.name == sb.name
    assert sb2.max_card_copy_count == sb.max_card_copy_count
    assert sb2.max_card_count == 15
    assert sb2.entries == sb.entries


def test_sideboard_backend_roundtrip():
    tmp_dir = Path('/tmp/pymtgdeck_sideboard_test')
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir()

    card = _load_card_from_json_file(DATA_DIR / 'card-example-3.json')
    sb = Sideboard(name="Backend Board")
    sb.add_card(card, 4)

    backend = Backend(file_path=tmp_dir)
    file_name = backend.save(sb)
    expected = f'{hashlib.sha256(sb.name.encode()).hexdigest()}.json'
    assert file_name == expected

    loaded = backend.load(file_name)
    assert isinstance(loaded, Sideboard)
    assert loaded.name == sb.name
    assert loaded.max_card_count == 15
    assert loaded.entries == sb.entries

    shutil.rmtree(tmp_dir)
