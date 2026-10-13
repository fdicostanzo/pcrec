"""tests/lib/compound_art.py -- [COMPOUND] tests/lib/compound_art.sh's one
answer to "is this artifact a compound", for python sweeps (see that file
for why a machine-stamp sweep skips a compound and counts the skip)."""
import re

_ROW = re.compile(r'^#define \w*_COMPOUND "([^"]*)"$', re.M)


def compound_row(text):
    """The artifact's <PREFIX>_COMPOUND value, or "" (bytes or str)."""
    if isinstance(text, bytes):
        text = text.decode('latin-1')
    m = _ROW.search(text)
    return m.group(1) if m else ""


def is_compound(text):
    return compound_row(text) not in ("", "none", "forced-off")
