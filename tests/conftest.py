from pathlib import Path


def gather_data_files(match: str):
    data_dir = Path(__file__).parent / "data"
    return list(data_dir.glob(match))