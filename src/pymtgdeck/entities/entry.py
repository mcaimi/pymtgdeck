#! /usr/bin/env python

try:
    import json
    from pyscryfall import ScryfallCard
except ImportError as e:
    print(f"Error importing library: {e}")


# Entry class. This will contain the item and the number of copies of the item.
class Entry:
    def __init__(self, card: ScryfallCard, count: int):
        self.card = card
        self.count = count

    # entry to dictionary
    def to_dict(self) -> dict:
        return {
            "card": self.card.to_dict(),
            "count": self.count
        }

    # entry to json
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    # entry from dictionary
    @classmethod
    def from_dict(cls, data: dict) -> 'Entry':
        return cls(ScryfallCard.from_dict(data['card']), data['count'])

    # entry from json
    @classmethod
    def from_json(cls, json_str: str) -> 'Entry':
        return cls.from_dict(json.loads(json_str))

    # entry to string
    def __str__(self):
        return f"{self.card.name} x{self.count}"

    def __repr__(self):
        return f"Entry(card={self.card.name}, count={self.count})"

    def __eq__(self, other):
        return self.card == other.card and self.count == other.count

    def __hash__(self):
        return hash((self.card.name, self.count))

# export the Entry class
__all__ = ['Entry']