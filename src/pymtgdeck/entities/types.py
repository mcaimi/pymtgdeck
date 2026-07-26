#!/usr/bin/env python

# Magic The Gathering Types

try:
    from pyscryfall import ScryfallCard
except ImportError as e:
    print(f"Error importing pyscryfall: {e}")

CARD_TYPES: list[str] = [
    "Land",
    "Creature",
    "Instant",
    "Sorcery",
    "Enchantment",
    "Artifact",
    "Planeswalker"
]

BASIC_LAND_NAMES: list[str] = ["Island", "Plains", "Swamp", "Mountain", "Forest"]

MODIFIERS: list[str] = [
    "Snow",
    "Snow-Covered",
    "Legendary",
    "Mythic",
]

# card is a basic land?
def is_basic_land(card: ScryfallCard) -> bool:
    return card.name.lower() in [land.lower() for land in BASIC_LAND_NAMES]

LEGAL_FORMATS: list[str] = [
    "standard", "future", "historic", "timeless", "gladiator",
    "pioneer", "modern", "legacy", "pauper", "vintage", "penny",
    "commander", "oathbreaker", "standardbrawl", "brawl", "alchemy",
    "paupercommander", "duel", "oldschool", "premodern", "predh", "tlr",
]

# export the constants
__all__ = [
    "CARD_TYPES",
    "BASIC_LAND_NAMES",
    "MODIFIERS",
    "LEGAL_FORMATS",
    "is_basic_land",
]