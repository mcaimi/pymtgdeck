#!/usr/bin/env python

# pymtgdeck package

from .entities.entry import Entry
from .entities.binder import Binder
from .entities.deck import Deck
from .entities.sideboard import Sideboard
from .entities.analytics import (
    deck_cmc_distribution,
    deck_cmc_histogram,
    deck_max_cmc,
    deck_min_cmc,
    deck_average_cmc,
    deck_type_distribution,
    deck_color_distribution,
    validate_legality,
    deck_diff,
    mana_base_analysis,
)
from .entities.types import CARD_TYPES, BASIC_LAND_NAMES, MODIFIERS, LEGAL_FORMATS, is_basic_land
from .io import deck_to_text, deck_from_text
# Registry and Backend must be imported last — they do `from pymtgdeck import ...`
from .persistence.registry import Registry
from .persistence.backend import Backend

__all__ = [
    'Entry',
    'Binder',
    'Deck',
    'Sideboard',
    'deck_cmc_distribution',
    'deck_cmc_histogram',
    'deck_max_cmc',
    'deck_min_cmc',
    'deck_average_cmc',
    'deck_type_distribution',
    'deck_color_distribution',
    'validate_legality',
    'deck_diff',
    'mana_base_analysis',
    'CARD_TYPES',
    'BASIC_LAND_NAMES',
    'MODIFIERS',
    'LEGAL_FORMATS',
    'is_basic_land',
    'deck_to_text',
    'deck_from_text',
    'Registry',
    'Backend',
]