# AGENTS.md

This file contains essential information for agents working with this pymtgdeck repository. It answers: "Would an agent likely miss this without help?"

## Project Overview
This is a Python library for maintaining Magic: The Gathering virtual binders and constrained decks, using pyscryfall for card data handling.

## Core Architecture
- **Entry**: Wraps a ScryfallCard with a count
- **Binder**: Collection of entries with unlimited card counts
- **Deck**: Subclass of Binder with deck-specific constraints (max 40 cards, max 4 copies per card)

## Key Commands
- Run tests: `pytest` (from repo root)
- Install dev dependencies: `uv sync` (uses pyproject.toml)

## Important Files
- `src/pymtgdeck/` - Main source code
- `tests/` - Test directory with synthetic JSON fixtures
- `pyproject.toml` - Build config, dependencies, and pytest configuration
- `README.md` - Complete documentation

## Key Constraints
- Each card can appear at most 4 times in a deck (Deck.max_card_copy_count = 4)
- Total deck size is limited to 40 cards (Deck.max_card_count = 40)
- The library requires Python 3.12+
- Dependencies managed via uv with `pyscryfall==0.1.2`

## Testing Setup
- Tests use pytest with configuration in pyproject.toml
- Test fixtures loaded from `tests/data/` directory
- Tests run from repository root (pytest config sets pythonpath = ["."])

## Import Structure
- Use `from pymtgdeck import Entry, Binder, Deck`
- All classes are properly exported via `__all__` in __init__.py
