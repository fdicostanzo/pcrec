#!/usr/bin/env python3
"""tests/knowledge/kfixtures.py DIR -- writes the analysis-kind ROUND-TRIP
fixtures ([KNOW-SRC] K3; docs/design/measure_sets.md rev 3 §9.6) into DIR,
one bundle per `DIR/<name>.rxt`, for run_knowledge_tests.sh to put through
R1-R3 and R5.

Written fresh per run, never committed: a committed `.rxt` under tests/ joins
the rxtsource corpus census (lane ksrc's K0 finding). Each bundle is VALID
(pcrec loads it) and each exercises a shape the shipped bundles and the
findings fixtures do not reach, so the canonical writer and both readers are
tested on it:

    kfull   cpfreq BEFORE freq (file order is the item digest's order); an
            `include <default>`; a block-scalar `description` whose opener
            carries a trailing space, with a ragged deeper line, a trailing
            space kept, and a whitespace-only line inside (an empty line of
            the value); all eleven provenance fields, `license-note` and
            `attribution` as block scalars (the latter's value is the single
            byte `|`, which a one-line writer would turn into an opener), a
            one-line `adaptation` with a trailing space; a TAB inside a
            `question`; code points of every UTF-8 length
    kline   a one-line `description` with trailing spaces (rest-of-line);
            a two-encoding `serves` list; comments and blank lines around
    kprov   a non-authored data block with `fidelity verbatim` (no
            adaptation), `url`/`ref`/`license`
"""
import os
import sys

KFULL = (
    "# a comment above the bundle\n"
    "\n"
    "analysis kfull\n"
    "    include <default>\n"
    "    description | \n"
    "        A block-scalar description, line one\n"
    "          a deeper continuation with a trailing space \n"
    "    \n"
    "        after a whitespace-only line\n"
    "    cpfreq\n"
    "        question How often does each code point occur?\n"
    "        reader byte-rate\n"
    "        analyzer authored for tests/knowledge/kfixtures.py\n"
    "        encoding utf8\n"
    "        serves byte-rate when utf8 via encode-utf8\n"
    "        row U+0041 5\n"
    "        row U+00E9 4\n"
    "        row U+20AC 3\n"
    "        row U+1F600 2\n"
    "        provenance\n"
    "            source corpus-x\n"
    "            url https://example.invalid/x\n"
    "            ref abc123\n"
    "            retrieved 2026-10-17\n"
    "            license MIT\n"
    "            license-note |\n"
    "                a note across\n"
    "                two lines\n"
    "            fidelity adapted\n"
    "            adaptation stripped of headers \n"
    "            attribution |\n"
    "                |\n"
    "            bytes 1234\n"
    "            sha256 00000000000000000000000000000000000000000000000000000000000000ab\n"
    "    freq\n"
    "        question has\ta tab\n"
    "        reader byte-rate\n"
    "        analyzer authored\n"
    "        encoding bytes\n"
    "        serves byte-rate when byte via unigram\n"
    "        row 0a 9\n"
    "        row 61 100\n"
    "        row ff 1\n"
    "        provenance\n"
    "            source authored\n"
    "            retrieved 2026-10-17\n"
    "# a comment below\n"
)

KLINE = (
    "\n"
    "# leading comment\n"
    "analysis kline\n"
    "    description one line with trailing spaces   \n"
    "    freq\n"
    "        question q\n"
    "        reader r\n"
    "        analyzer a\n"
    "        encoding ascii\n"
    "        serves byte-rate when byte,utf8 via unigram\n"
    "        row 20 5\n"
    "        row 41 7\n"
    "        provenance\n"
    "            source authored\n"
    "            retrieved 2026-10-17\n"
    "\n"
)

KPROV = (
    "analysis kprov\n"
    "    freq\n"
    "        question an exemplar's bytes\n"
    "        reader byte-rate\n"
    "        analyzer pcrec-analyze 0.1 --scan freq\n"
    "        encoding ascii\n"
    "        serves byte-rate when byte via unigram\n"
    "        row 2e 11\n"
    "        row 7a 13\n"
    "        provenance\n"
    "            source my-exemplar\n"
    "            url https://example.invalid/e\n"
    "            ref v1\n"
    "            retrieved 2026-10-17\n"
    "            license CC0-1.0\n"
    "            fidelity verbatim\n"
    "            bytes 24\n"
    "            sha256 1111111111111111111111111111111111111111111111111111111111111111\n"
)


def main(d):
    os.makedirs(d, exist_ok=True)
    for name, text in (("kfull", KFULL), ("kline", KLINE), ("kprov", KPROV)):
        with open(os.path.join(d, name + ".rxt"), "w", newline="") as f:
            f.write(text)


if __name__ == "__main__":
    main(sys.argv[1])
