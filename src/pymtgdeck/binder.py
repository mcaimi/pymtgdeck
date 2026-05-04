#! /usr/bin/env python

# Magic The Gathering Binder Builder

try:
    import json
    from .entry import Entry
    from pyscryfall import ScryfallCard
except ImportError as e:
    print(f"Error importing pyscryfall: {e}")


# Define the Binder class. This will contain the items in the binder and the number of copies of each item.
# The binder will be a list of Entry objects.
# Each item can be present any number of times in the binder.
class Binder:
    def __init__(self):
        self.entries = []

    # Add an item to the binder. If the item is already in the binder, increment the number of copies.
    # If the item is not in the binder, add it to the binder.
    def add_card(self, card: ScryfallCard, count: int = 1):
        for entry in self.entries:
            if entry.card.id == card.id:
                entry.count += count
                return
        self.entries.append(Entry(card, count))
    
    # Check if a card is in the deck.
    def has_card(self, card: ScryfallCard) -> bool:
        for entry in self.entries:
            if entry.card.id == card.id:
                return True
        return False
    
    # Remove a card from the deck. If the card is not in the deck, raise a ValueError.
    def remove_card(self, card: ScryfallCard, count: int = 1):
        for entry in self.entries:
            if entry.card.id == card.id:
                entry.count -= count
                if entry.count == 0:
                    self.entries.remove(entry)
                return
        raise ValueError(f"Card {card.name} not found in binder")
    
    # Get the number of copies of a card in the deck.
    def get_card_count(self, card: ScryfallCard) -> int:
        for entry in self.entries:
            if entry.card.id == card.id:
                return entry.count
        return 0

    # serialize binder to dictionary
    def to_dict(self) -> dict:
        return {
            "entries": [entry.to_dict() for entry in self.entries]
        }

    # deserialize binder from dictionary
    @classmethod
    def from_dict(cls, dump_dict: dict) -> 'Binder':
        if 'entries' not in dump_dict:
            raise ValueError("Binder dictionary must contain 'entries' key")

        # create binder
        binder = cls()

        # add entries to binder
        for entry in dump_dict['entries']:
            binder.add_card(Entry.from_dict(entry).card, Entry.from_dict(entry).count)

        return binder

# export the Binder class
__all__ = ['Binder']