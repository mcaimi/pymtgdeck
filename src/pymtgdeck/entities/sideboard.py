#! /usr/bin/env python

# Magic The Gathering Sideboard

try:
    from .entry import Entry
    from .deck import Deck
    from pyscryfall import ScryfallCard
except ImportError as e:
    print(f"Error importing library: {e}")


class Sideboard(Deck):
    """A 15-card sideboard with the same copy-limit rules as Deck."""

    MAX_SIDEBOARD_SIZE = 15

    def __init__(
        self,
        max_card_copy_count: int = 4,
        name: str = "MTG Sideboard (Default)",
    ):
        super().__init__(
            max_card_copy_count=max_card_copy_count,
            max_card_count=Sideboard.MAX_SIDEBOARD_SIZE,
            name=name,
        )

    @classmethod
    def from_dict(cls, dump_dict: dict) -> 'Sideboard':
        if 'name' not in dump_dict or 'entries' not in dump_dict or 'max_card_copy_count' not in dump_dict:
            raise ValueError("Sideboard dictionary must contain 'name', 'entries', and 'max_card_copy_count'")
        sb = cls(max_card_copy_count=dump_dict['max_card_copy_count'], name=dump_dict['name'])
        for entry_dict in dump_dict['entries']:
            e = Entry.from_dict(entry_dict)
            sb.add_card(e.card, e.count)
        return sb


__all__ = ['Sideboard']
