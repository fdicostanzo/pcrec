#!/usr/bin/env python3
"""Concatenates the three JSONPlaceholder responses and trims to 1MB,
byte-for-byte the same transform fetch_corpora.sh's committed sha256 in
manifest.tsv was taken from (comments + '\\n' + posts + '\\n' + users,
first 1,000,000 bytes)."""
import sys


def main() -> None:
    j1, j2, j3, out = sys.argv[1:5]
    d1 = open(j1, 'rb').read()
    d2 = open(j2, 'rb').read()
    d3 = open(j3, 'rb').read()
    data = d1 + b'\n' + d2 + b'\n' + d3
    open(out, 'wb').write(data[:1_000_000])


if __name__ == '__main__':
    main()
