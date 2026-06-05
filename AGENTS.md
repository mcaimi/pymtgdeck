# AGENTS.md

This file contains essential information for agents working with this pymtgdeck repository. It answers: "Would an agent likely miss this without help?"

## Project Overview
This is a Python library for maintaining Magic: The Gathering virtual binders and constrained decks, using pyscryfall for card data handling.

## Core Architecture
- **Entry**: Wraps a ScryfallCard with a count
- **Binder**: Collection of entries with unlimited card counts
- **Deck**: Subclass of Binder with deck-specific constraints (max 40 cards, max 4 copies per card)
- **Analytics** (`entities/analytics.py`): CMC helpers for decks — `deck_min_cmc`, `deck_max_cmc`, `deck_cmc_distribution`, `deck_cmc_histogram` (numpy)
- **Types** (`entities/types.py`): `is_basic_land`, `BASIC_LAND_NAMES`, and related constants (not re-exported from package root)

## Key Commands
- Run tests: `pytest` (from repo root)
- Install dev dependencies: `uv sync` (uses pyproject.toml)

## Important Files
- `src/pymtgdeck/` - Main source code
- `src/pymtgdeck/entities/analytics.py` - Deck CMC analytics
- `src/pymtgdeck/entities/types.py` - Basic land detection used by analytics
- `tests/` - Test directory with synthetic JSON fixtures
- `tests/analytics_test.py` - CMC distribution, histogram, min/max
- `pyproject.toml` - Build config, dependencies, and pytest configuration
- `README.md` - Complete documentation

## Key Constraints
- Each card can appear at most 4 times in a deck (Deck.max_card_copy_count = 4)
- Total deck size is limited to 40 cards (Deck.max_card_count = 40)
- The library requires Python 3.12+
- Runtime dependencies: `pyscryfall==0.1.2`, `numpy>=2.4.6` (managed via uv)

## Analytics behavior (easy to get wrong)
- CMC stats consider **one value per deck entry** (distinct card row), not weighted by `Entry.count`
- **Basic lands** (five names in `BASIC_LAND_NAMES`) are excluded from all analytics functions
- CMC is taken as `int(entry.card.cmc)` (fractional CMC truncates toward zero)
- Empty deck or only basic lands: distribution/histogram return empty numpy arrays; `deck_min_cmc` / `deck_max_cmc` raise `ValueError`

## Testing Setup
- Tests use pytest with configuration in pyproject.toml
- Test fixtures loaded from `tests/data/` directory
- Tests run from repository root (pytest config sets pythonpath = ["."])

## Import Structure
- Prefer: `from pymtgdeck import Entry, Binder, Deck, deck_cmc_distribution, deck_cmc_histogram, deck_max_cmc, deck_min_cmc, Registry, Backend`
- Analytics can also be imported from `pymtgdeck.entities.analytics` (as in tests)
- `is_basic_land` is available from `pymtgdeck.entities.types` if needed
- Public API is listed in `__all__` in `src/pymtgdeck/__init__.py`
