#! /usr/bin/env python

# Text-format import/export for Deck and Binder objects.
# Standard format: one line per entry — "<count> <card name>"
# Lines starting with "//" are treated as comments and ignored.

import re

try:
    import requests
    from pyscryfall.api import search_card_by_name_exact
    from .entities.binder import Binder
    from .entities.deck import Deck
except ImportError as e:
    print(f"Error importing library: {e}")

_COMMENT_RE = re.compile(r'\s*//.*$')
_ENTRY_RE = re.compile(r'^(\d+)\s+(.+)$')


def deck_to_text(collection: Binder) -> str:
    """Export a Binder or Deck to plain text format.

    Each entry is rendered as "<count> <card name>". Entries appear in the
    order they were added to the collection.
    """
    return "\n".join(f"{entry.count} {entry.card.name}" for entry in collection.entries)


def deck_from_text(
    text: str,
    deck: Deck | None = None,
    *,
    session: 'requests.Session | None' = None,
    set_code: str | None = None,
) -> Deck:
    """Import a deck from plain text format, looking up each card on Scryfall.

    Each non-comment line must be "<count> <card name>".
    Lines starting with "//" are ignored.
    Raises ValueError for lines that cannot be parsed.
    Raises pyscryfall.exceptions.ScryfallApiError if a card name is not found.
    """
    if deck is None:
        deck = Deck()

    for raw_line in text.splitlines():
        line = _COMMENT_RE.sub('', raw_line).strip()
        if not line:
            continue
        m = _ENTRY_RE.match(line)
        if not m:
            raise ValueError(f"Cannot parse deck line: {raw_line!r}")
        count, name = int(m.group(1)), m.group(2).strip()
        card = search_card_by_name_exact(name, session=session, set_code=set_code)
        deck.add_card(card, count)

    return deck


__all__ = ["deck_to_text", "deck_from_text"]
