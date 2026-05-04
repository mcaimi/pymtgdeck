# pymtgdeck

Python library for maintaining **Magic: The Gathering** virtual binders and constrained decks. Card data is represented with [pyscryfall](https://pypi.org/project/pyscryfall/) `ScryfallCard` objects (Scryfall-shaped JSON in and out).

- **License:** GNU General Public License v3.0 (see `LICENSE`)
- **Python:** 3.12+

## Project structure

The package uses a **src layout** (importable code under `src/`), tests and fixtures beside the tree root, and **uv** for lockfile and dev dependencies. Domain types live under `entities/`; disk persistence under `persistence/`.

```text
pymtgdeck/
├── LICENSE
├── README.md                 # this file
├── pyproject.toml            # project metadata, pytest config, hatchling build
├── uv.lock                   # locked dependency versions (uv)
├── src/
│   └── pymtgdeck/
│       ├── __init__.py       # public exports: Entry, Binder, Deck, Registry, Backend
│       ├── entities/
│       │   ├── entry.py      # Entry (card + quantity)
│       │   ├── binder.py     # Binder (unlimited collection semantics)
│       │   └── deck.py       # Deck (subclass with size / copy limits)
│       └── persistence/
│           ├── backend.py    # save/load Deck and Binder to JSON files
│           └── registry.py   # scan a folder of saved JSON and list metadata
└── tests/
    ├── utils.py              # helpers: load Scryfall list JSON → first card
    ├── entry_test.py
    ├── binder_test.py
    ├── deck_test.py
    ├── backend_test.py
    ├── registry_test.py
    └── data/
        ├── card-example-1.json
        ├── card-example-2.json
        └── card-example-3.json   # Scryfall API “list” JSON fixtures
```

## Class diagram

Relationships: a **Binder** holds a list of **Entry** instances; **Deck** subclasses **Binder** and adds validation and aggregate card counting. **Backend** writes and reads JSON envelopes for **Deck** and **Binder**; **Registry** rescans a directory of those files for a lightweight index. **ScryfallCard** comes from **pyscryfall**, not from pymtgdeck.

```mermaid
classDiagram
    direction TB

    class ScryfallCard {
        <<pyscryfall>>
        +from_dict(data) ScryfallCard$
        +to_dict() dict
    }

    class Entry {
        +ScryfallCard card
        +int count
        +to_dict() dict
        +to_json() str
        +from_dict(data) Entry$
        +from_json(s) Entry$
    }

    class Binder {
        +str name
        +list entries
        +add_card(card, count=1)
        +has_card(card) bool
        +remove_card(card, count=1)
        +get_card_count(card) int
        +to_dict() dict
        +from_dict(data) Binder$
    }

    class Deck {
        +str name
        +int max_card_copy_count
        +int max_card_count
        +is_full() bool
        +get_card_count() int
        +get_card_copy_count(card) int
        +is_empty() bool
        +add_card(card, count=1)
        +to_dict() dict
        +from_dict(data) Deck$
    }

    class Backend {
        +Path file_path
        +save(obj) str
        +load(file_name) Deck|Binder
    }

    class Registry {
        +Path path
        +list registry
        +load_file(file_name) Deck|Binder
    }

    Entry --> ScryfallCard : card
    Binder "1" o-- "*" Entry : entries
    Binder <|-- Deck
    Backend ..> Deck : load/save
    Backend ..> Binder : load/save
    Registry ..> Deck : load_file
    Registry ..> Binder : load_file
```

**Note:** On **Deck**, `get_card_count()` (no arguments) returns the **total** number of cards in the deck. On **Binder**, `get_card_count(card)` returns copies of **that** card. Deck uses `get_card_copy_count(card)` for per-card counts.

## Installation

From the repository root, using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Or install the package in editable mode with your preferred tool (example with pip):

```bash
pip install -e .
```

Runtime dependency: `pyscryfall==0.1.2` (declared in `pyproject.toml`).

## Usage examples

### Binder (no deck limits)

```python
from pyscryfall import search_cards_by_name
from pymtgdeck import Binder

binder = Binder(name="Trade binder")  # name is optional; used in serialization and persistence
results = search_cards_by_name("Sengir Vampire")
card = results.data[0]

binder.add_card(card, count=2)
assert binder.has_card(card)
assert binder.get_card_count(card) == 2

binder.remove_card(card, count=1)
assert binder.get_card_count(card) == 1
```

### Deck (default limits: 40 cards, 4 copies per card)

```python
from pyscryfall import search_cards_by_name
from pymtgdeck import Deck

deck = Deck(name="Sealed pool")  # or Deck(max_card_count=60, max_card_copy_count=4, name="...")
results = search_cards_by_name("Forest")
forest = results.data[0]

deck.add_card(forest, count=4)
assert deck.get_card_count() == 4  # total cards
assert deck.get_card_copy_count(forest) == 4
assert not deck.is_full()
```

Default limits match the module constants `MAX_CARD_COUNT` and `MAX_CARD_COPY_COUNT` in `entities/deck.py` (40 and 4); you can override them per deck via the constructor.

### Serialization

`Binder.to_dict()` / `Binder.from_dict()` include an optional `name` plus `entries`. `Deck.to_dict()` / `Deck.from_dict()` also persist `max_card_copy_count` and `max_card_count`.

```python
from pymtgdeck import Binder, Deck

binder = Binder(name="My binder")
# ... add cards ...

dump = binder.to_dict()
binder2 = Binder.from_dict(dump)

deck = Deck(name="My deck")
# ... add cards ...

deck_dump = deck.to_dict()
deck2 = Deck.from_dict(deck_dump)
```

### Persistence (`Backend`)

`Backend` writes each deck or binder to a single JSON file under a configurable directory (default `~/.pymtgdeck`). The on-disk shape is an **envelope** with `timestamp`, `type` (`"Deck"` or `"Binder"`), `name` (same as the object’s `name`), and `data` (the result of `to_dict()` on the deck or binder).

The file basename is the SHA-256 hex digest of the UTF-8 encoded `name`, with a `.json` suffix. Saving again for the same `name` raises `OSError` so you do not silently overwrite an existing file.

```python
from pymtgdeck import Deck, Backend
from pathlib import Path

store = Path("/tmp/mtg-store")
backend = Backend(file_path=store)

deck = Deck(name="FNM")
# ... add cards ...

filename = backend.save(deck)          # returns e.g. "<hex>.json"
restored = backend.load(filename)
```

Use a non-`None` **`name`** on the deck or binder before `save`, so the filename is stable and hashing is defined.

### Registry scan (`Registry`)

`Registry` reads every `*.json` file in its directory (default `~/.pymtgdeck`). For each file whose envelope has `type` `"Deck"` or `"Binder"`, it records `name`, `type`, and `timestamp` in an in-memory list. `str(registry)` pretty-prints that index. For round-tripping files written by `Backend`, use `Backend.load` with the basename returned from `save`; `Registry` also exposes `load_file` for reloading (see `persistence/registry.py` for the exact argument semantics).

### Entry and JSON fixtures

`Entry` wraps one `ScryfallCard` and a quantity, and can round-trip through dict/JSON shapes compatible with pyscryfall:

```python
from pymtgdeck import Entry

entry = Entry(card, count=3)
data = entry.to_dict()
restored = Entry.from_dict(data)
```

Tests load cards from files shaped like Scryfall’s **card list** response (see `tests/data/*.json`), using `ScryfallCardList.from_json_string` and taking `data[0]`.

## Test procedure

Tests use **pytest** (dev dependency). Configuration lives in `pyproject.toml` under `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `pythonpath = ["."]` so `src` resolves when running from the repo root).

**Run the full suite** from the repository root:

```bash
uv run pytest
```

If a virtual environment is already activated with dev dependencies installed:

```bash
pytest tests/
```

**Useful variants:**

```bash
pytest tests/ -q              # quiet
pytest tests/deck_test.py     # single module
pytest tests/ -k serialization  # tests whose name contains the substring
```

The suite covers `Entry`, `Binder`, and `Deck` (add/remove, limits, serialization, optional `name`), plus `Backend` save/load and collision behavior. Fixtures are offline JSON files; tests that call `search_cards_by_name` would need network access and are not part of the default suite.

## AI Disclosure

Part of this project has been developed with the help of an AI Model. Specifically I used a locally-hosted [QWEN3-CODER](https://ollama.com/library/qwen3-coder) using [Ollama](https://ollama.ai).
