#!/usr/bin/env python

# save/load Decks and Binders to/from disk

try:
    import hashlib
    import json
    import time
    import typing
    from pymtgdeck import Deck, Binder
    from pathlib import Path
except ImportError as e:
    print(f"Error: {e}")
    exit(1)

# default path for saving and loading files
DEFAULT_PATH = Path('~/.pymtgdeck').expanduser()

# class to manage persistence of Decks and Binders
class Backend:
    def __init__(self, file_path: str = DEFAULT_PATH):
        self.file_path = Path(file_path)
        self.file_path.mkdir(parents=True, exist_ok=True)

    # save a Deck or Binder to disk
    # the file name is the hash of the Deck or Binder
    # the file contents are the Deck or Binder in json format plus a timestamp and a field to indicate the type of the object
    def save(self, obj: typing.Union[Deck, Binder]) -> str:
        data = {
            'timestamp': time.time(),
            'type': type(obj).__name__,
            'data': obj.to_dict(),
            'name': obj.name,
        }

        # build file name from hash. same deck name, same file name.
        file_name = f'{hashlib.sha256(data['name'].encode()).hexdigest()}.json'

        # check if file already exists, if so raise a OSError
        if (self.file_path / file_name).exists():
            raise OSError(f"File {file_name} already exists")

        # save data to file
        with open(self.file_path / file_name, 'w') as f:
            json.dump(data, f)
        return file_name

    # load a Deck or Binder from disk
    # the file name is the hash of the Deck or Binder
    # the file contents are the Deck or Binder in json format plus a timestamp and a field to indicate the type of the object
    def load(self, file_name: str) -> typing.Union[Deck, Binder]:
        with open(self.file_path / file_name, 'r') as f:
            data = json.load(f)
            match data['type']:
                case 'Deck':
                    return Deck.from_dict(data['data'])
                case 'Binder':
                    return Binder.from_dict(data['data'])
                case _:
                    raise ValueError(f"Unknown type: {data['type']}")

# export class
__all__ = ['Backend']