import os


def load_data(filename):
    """Load a binary data."""
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path) as fptr:
        return fptr.read()
