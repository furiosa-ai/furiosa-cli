import os

def test_data(relative_path) -> str:
    return os.path.dirname(__file__) + "/../test_data/" + relative_path