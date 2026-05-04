#!/usr/bin/env python

# manage persistence of Decks and Binders to disk
# format is json-based, with a file per Deck or Binder
# the file name is the hash of the Deck or Binder
# the file contents are the Deck or Binder in json format

try:
    from pymtgdeck import Deck, Binder
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

    # look into self.path and glob all json files
    # for each file found, add it to the registry if it is a Deck or Binder
    def _load_registry(self) -> None:
        for file in self.path.glob('*.json'):
            if file.is_file():
                with open(file, 'r') as f:
                    data = json.load(f)
                    if data['type'] == 'Deck' or data['type'] == 'Binder':
                        self.registry.append({
                            'name': data['name'],
                            'type': data['type'],
                            'timestamp': data['timestamp']
                        })
                    # unload the file from memory
                    del data

    # load the specified file from the registry into a Deck or Binder object
    def load_file(self, file_name: str) -> typing.Union[Deck, Binder]:
        # check if the file is in the registry
        if file_name not in [entry['name'] for entry in self.registry]:
            raise ValueError(f"File {file_name} not found in registry")

        # load the file from the registry
        with open(self.path / file_name, 'r') as f:
            data = json.load(f)
            match data['type']:
                case 'Deck':
                    return Deck.from_dict(data['data'])
                case 'Binder':
                    return Binder.from_dict(data['data'])
                case _:
                    raise ValueError(f"Unknown type: {data['type']}")

    # pretty print the registry
    def __str__(self) -> str:
        return pprint.pformat(self.registry)

# export class
__all__ = ['Registry']