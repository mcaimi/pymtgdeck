#!/usr/bin/env python

# manage persistence of Decks and Binders to disk
# format is json-based, with a file per Deck or Binder
# the file name is the hash of the Deck or Binder
# the file contents are the Deck or Binder in json format

try:
    from pymtgdeck import Deck, Binder, Sideboard
    import typing
    import json
    from pathlib import Path
    import pprint
except ImportError as e:
    print(f"Error: {e}")
    exit(1)

# default path for saving and loading files
DEFAULT_PATH = Path('~/.pymtgdeck').expanduser()

# class to manage persistence of Decks and Binders to disk
class Registry:
    def __init__(self, path: str = DEFAULT_PATH):
        self.path = Path(path)
        self.registry = []
        self.path.mkdir(parents=True, exist_ok=True)
        self._load_registry()

    # recursively look into self.path and glob all json files
    # for each file found, add it to the registry if it is a Deck or Binder
    def _load_registry(self) -> None:
        for file in self.path.rglob('*.json'):
            if file.is_file():
                with open(file, 'r') as f:
                    data = json.load(f)
                    if data['type'] in ('Deck', 'Binder', 'Sideboard'):
                        self.registry.append({
                            'name': data['name'],
                            'type': data['type'],
                            'timestamp': data['timestamp'],
                            'path': file,
                        })
                    # unload the file from memory
                    del data

    # load a Deck or Binder by its name from the registry
    def load_file(self, name: str) -> typing.Union[Deck, Binder]:
        for entry in self.registry:
            if entry['name'] == name:
                with open(entry['path'], 'r') as f:
                    data = json.load(f)
                    match data['type']:
                        case 'Deck':
                            return Deck.from_dict(data['data'])
                        case 'Binder':
                            return Binder.from_dict(data['data'])
                        case 'Sideboard':
                            return Sideboard.from_dict(data['data'])
                        case _:
                            raise ValueError(f"Unknown type: {data['type']}")
        raise ValueError(f"'{name}' not found in registry")

    # pretty print the registry
    def __str__(self) -> str:
        return pprint.pformat(self.registry)

# export class
__all__ = ['Registry']