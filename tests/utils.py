from pathlib import Path
from pyscryfall import ScryfallCard, ScryfallCardList

# tests synthetic data directory
DATA_DIR = Path(__file__).parent / 'data'

# load card from ScryfallCardList
def _load_card_from_json_file(json_file_path: str) -> ScryfallCard:
    with open(json_file_path, 'r') as f:
        data_str: str = f.read()
    card_list = ScryfallCardList.from_json_string(data_str)
    return card_list.data[0]