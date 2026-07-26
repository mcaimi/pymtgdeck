#! /usr/bin/env python

# Magic The Gathering Deck Builder

try:
    from .entry import Entry    
    from .binder import Binder
    from .types import is_basic_land
    from pyscryfall import ScryfallCard
except ImportError as e:
    print(f"Error importing library: {e}")

# Maximum number of copies of a card that can be present in a deck.
MAX_CARD_COPY_COUNT = 4

# Maximum number of cards that can be present in a deck.
MAX_CARD_COUNT = 40

# Deck class. This will contain the items in the deck and the number of copies of each item.
# It is a subclass of Binder, but with the restrictions:
# - each item can be present at most MAX_CARD_COPY_COUNT times in the deck.
# - the total number of cards in the deck is at most MAX_CARD_COUNT.
class Deck(Binder):
    def __init__(self,
        max_card_copy_count: int = MAX_CARD_COPY_COUNT,
        max_card_count: int = MAX_CARD_COUNT,
        name: str = "MTG Deck (Default)"
    ):
        self.max_card_copy_count = max_card_copy_count
        self.max_card_count = max_card_count
        super().__init__(name=name)

    # check if the deck is full
    def is_full(self) -> bool:
        return self.get_card_count() >= self.max_card_count

    # check numnber of cards in the deck
    def get_card_count(self) -> int:
        return sum(entry.count for entry in self.entries)
    
    # check number of copies of a card in the deck
    def get_card_copy_count(self, card: ScryfallCard) -> int:
        return super().get_card_count(card)
    
    # check if the deck is empty
    def is_empty(self) -> bool:
        return self.get_card_count() == 0

    # add a card to the deck. If the card is already in the deck, increment the number of copies.
    # If the card is not in the deck, add it to the deck.
    # If the deck is full, raise a ValueError.
    def add_card(self, card: ScryfallCard, count: int = 1):
        # total-card limit applies to all cards, including basic lands
        if self.get_card_count() + count > self.max_card_count:
            raise ValueError(f"Deck cannot contain more than {self.max_card_count} cards")
        # basic lands are exempt from the per-card copy limit
        if not is_basic_land(card):
            if self.get_card_copy_count(card) + count > self.max_card_copy_count:
                raise ValueError(f"Card {card.name} cannot be present more than {self.max_card_copy_count} times in the deck")
        super().add_card(card, count)

    @classmethod
    def standard(cls, name: str = "MTG Standard Deck") -> 'Deck':
        """60-card deck, max 4 copies of any non-basic-land card."""
        return cls(max_card_copy_count=4, max_card_count=60, name=name)

    @classmethod
    def limited(cls, name: str = "MTG Limited Deck") -> 'Deck':
        """40-card deck, max 4 copies of any non-basic-land card."""
        return cls(max_card_copy_count=4, max_card_count=40, name=name)

    @classmethod
    def commander(cls, name: str = "MTG Commander Deck") -> 'Deck':
        """100-card singleton deck (max 1 copy per non-basic-land card)."""
        return cls(max_card_copy_count=1, max_card_count=100, name=name)

    # serialize deck to dictionary
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "entries": [entry.to_dict() for entry in self.entries],
            "max_card_copy_count": self.max_card_copy_count,
            "max_card_count": self.max_card_count
        }

    # deserialize deck from dictionary
    @classmethod
    def from_dict(cls, dump_dict: dict) -> 'Deck':
        if 'name' not in dump_dict or 'entries' not in dump_dict or 'max_card_copy_count' not in dump_dict or 'max_card_count' not in dump_dict:
            raise ValueError("Deck dictionary must contain 'name', 'entries', 'max_card_copy_count', and 'max_card_count' keys")

        # create deck
        deck = cls(dump_dict['max_card_copy_count'], dump_dict['max_card_count'], dump_dict['name'])

        # add entries to deck
        for entry in dump_dict['entries']:
            e = Entry.from_dict(entry)
            deck.add_card(e.card, e.count)

        return deck
    
# export the Deck class
__all__ = ['Deck']