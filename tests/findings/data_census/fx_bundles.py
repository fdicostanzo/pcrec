#!/usr/bin/env python3
"""tests/findings/data_census/fx_bundles.py DIR — writes the [KNOW-SRC] K0
findings fixture change into DIR: DIR/old/fx.rxt and DIR/new/fx.rxt, one
analysis bundle `fx` in two versions. `old` makes `Z` rare and `@` common,
`new` the reverse; every other count is identical, so every other byte's
normalized rate is too.

Written per run (res_fixtures.py's precedent) rather than committed, because
a committed `.rxt` joins the corpus every population pin counts; the
`-I DIR/<name>.rxt` lookup the census drives needs the `.rxt` name."""
import os
import sys


def bundle(z, at):
    rows = {0x61: 5000, 0x62: 4000, 0x63: 3000, 0x78: 2000, 0x79: 1500,
            0x7a: 1200, 0x20: 900, 0x5a: z, 0x40: at}
    out = ["analysis fx", "    freq",
           "        question data-census fixture: Z and @ trade rarity",
           "        reader byte-rate",
           "        analyzer tests/findings/data_census (hand-written)",
           "        encoding bytes",
           "        serves byte-rate when byte,utf8 via unigram"]
    out += [f"        row {b:02x} {rows[b]}" for b in sorted(rows)]
    out += ["        provenance", "            source authored",
            "            retrieved 2026-10-16"]
    return "\n".join(out) + "\n"


def main(d):
    for side, (z, at) in (("old", (1, 700)), ("new", (700, 1))):
        os.makedirs(os.path.join(d, side), exist_ok=True)
        with open(os.path.join(d, side, "fx.rxt"), "w") as fh:
            fh.write(bundle(z, at))


if __name__ == "__main__":
    main(sys.argv[1])
