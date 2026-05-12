#!/usr/bin/env python

# Magic The Gathering Types

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

# export the constants
__all__ = [
    "CARD_TYPES",
    "BASIC_LAND_NAMES",
    "MODIFIERS",
]