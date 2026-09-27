#!/usr/bin/env python3
"""byte_rate_movers.py -- [FINDINGS] B5 sourcing half's R35 evidence
(docs/design/findings/design.md §13 B5's own acceptance line: "a bundle
whose byte-rate census is EMPTY does not ship yet").

WHAT THIS IS: a data-only, arithmetic comparison. It does NOT run
`pcrec --analysis <name>` (route resolution / B2 is not built yet, so there
is no CLI surface to select a non-default analysis), and it does NOT touch
`src/` or `tests/`. It reads:

  1. `src/findings/default.rxt`'s shipped `freq` block (the byte-rate table
     every compile uses today);
  2. this lane's two `generated_preview.rxt` files (weblog / log), produced
     by running the REAL analyzer, `scripts/pcrec_analyze.py`, over each
     exemplar;
  3. `docs/dev/optloop/c2/reqpos_census.tsv`'s `set_hex` column -- the WHOLE
     necessary byte SET per corpus/bench pattern (not just the rightmost
     pick that census's own `req_byte` column recorded, which predates
     `[OPT-FREQPICK]`'s argmin and is not used here).

...and it applies design.md §2.5's OWN normalization formula (counts -> ppm)
by hand, in Python, to each of the three tables, then computes
argmin(ppm) over each pattern's necessary-byte SET under each table -- the
same rule `[OPT-FREQPICK]`'s `src/core/findings.c` argmin applies -- and
reports how many patterns' PICK would move if the compile's byte-rate
source were `weblog` or `log` instead of `default`.

This is a PROXY for the real R35 census (which needs a real
`pcrec --analysis <name>` compile once B2 lands), stated as such. It answers
the same question -- would a bundle's byte-rate values move a real
decision -- using the same arithmetic the accessor uses, over real
corpus/bench candidate sets, with no compile. See the lane's report for the
limitations this stands in for.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_RXT = ROOT / "src" / "findings" / "default.rxt"
WEBLOG_PREVIEW = ROOT / "third_party" / "elastic-examples-apache-logs-bc53b584" / "generated_preview.rxt"
LOG_PREVIEW = ROOT / "third_party" / "synth-log-lines-v1" / "generated_preview.rxt"
REQPOS_CENSUS = ROOT / "docs" / "dev" / "optloop" / "c2" / "reqpos_census.tsv"

FLOOR = 2
ROW_RE = re.compile(r"^\s*row\s+([0-9a-fA-F]{2})\s+(\d+)\s*$")


def parse_freq_block(text: str) -> dict[int, int]:
    """Extract the FIRST `freq` block's byte->count rows from a `.rxt`
    bundle's text (design.md §2.3's row grammar: `row HH COUNT`, lowercase
    hex). Stops at the first non-`freq`-block line after `freq` that is not
    a `row` line and is indented less than a row (i.e. the block's own
    scope ends). This is a DELIBERATELY NARROW reader -- it knows nothing
    about `.rxt` syntax beyond "a `freq` line, then `row HH N` lines" -- it
    is not a substitute for the real parser and is used only to read counts
    back out of text this same lane generated or that ships as `default.rxt`.
    """
    counts: dict[int, int] = {}
    in_freq = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "freq":
            in_freq = True
            continue
        if in_freq:
            m = ROW_RE.match(line)
            if m:
                counts[int(m.group(1), 16)] = int(m.group(2))
                continue
            if stripped and not stripped.startswith(("question", "reader",
                                                       "analyzer", "encoding",
                                                       "serves")):
                # first non-row, non-header line after rows started -> block over
                if counts:
                    break
    return counts


def normalize_ppm(counts: dict[int, int]) -> list[int]:
    """design.md §2.5, verbatim: 256 counts -> 256 ppm values summing to
    1,000,000, every entry >= FLOOR."""
    c = [counts.get(b, 0) for b in range(256)]
    n = sum(c)
    if n == 0:
        raise ValueError("N == 0")
    z = sum(1 for x in c if x == 0)
    m = 1_000_000 - FLOOR * z
    ppm = []
    for x in c:
        if x == 0:
            ppm.append(FLOOR)
        else:
            ppm.append(max(FLOOR, (x * m) // n))
    r = 1_000_000 - sum(ppm)
    if r != 0:
        # ties go to the lowest byte (§2.5 step 4)
        best_val = max(ppm)
        idx = ppm.index(best_val)
        ppm[idx] += r
    assert sum(ppm) == 1_000_000, sum(ppm)
    assert all(p >= FLOOR for p in ppm)
    return ppm


def load_table(path: Path, label: str) -> list[int]:
    text = path.read_text()
    counts = parse_freq_block(text)
    if len(counts) < 2:
        raise ValueError(f"{label}: parsed only {len(counts)} freq rows from {path}")
    return normalize_ppm(counts)


def argmin_byte(ppm: list[int], byte_set: list[int]) -> tuple[int, int]:
    """[OPT-FREQPICK]'s rule: pick the byte with the LOWEST ppm (rarest);
    ties go to the rightmost member of the set, per c2design_report.md's
    "PCRE2's rightmost rule surviving as the tiebreak"."""
    best_b, best_p = None, None
    for b in byte_set:  # iterate in the set's own (ascending, by construction) order
        p = ppm[b]
        if best_p is None or p < best_p or (p == best_p):
            # <=' gives ties to the LAST (rightmost) member seen, matching
            # the rightmost tiebreak when iterating ascending byte order.
            if best_p is None or p <= best_p:
                best_b, best_p = b, p
    return best_b, best_p


def load_reqpos_sets() -> list[tuple[str, str, list[int]]]:
    rows = []
    with open(REQPOS_CENSUS) as f:
        header = None
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            fields = line.rstrip("\n").split("\t")
            if header is None:
                header = fields
                continue
            rec = dict(zip(header, fields))
            if rec.get("status") != "ok":
                continue
            set_hex = rec.get("set_hex", "-")
            if not set_hex or set_hex == "-":
                continue
            if len(set_hex) % 2 != 0:
                continue
            byte_set = [int(set_hex[i:i+2], 16) for i in range(0, len(set_hex), 2)]
            if len(byte_set) < 2:
                continue  # a singleton set can never move by a different table
            rows.append((rec["pop"], rec["id"], byte_set))
    return rows


def main() -> int:
    default_ppm = load_table(DEFAULT_RXT, "default")
    weblog_ppm = load_table(WEBLOG_PREVIEW, "weblog")
    log_ppm = load_table(LOG_PREVIEW, "log")

    print("=== §2.5 sanity: default identity (N=1e6, z=0 => ppm == count) ===")
    print(f"  default sum(ppm) = {sum(default_ppm)} (want 1000000)")

    print()
    print("=== ppm('-') = 0x2d across tables (requirements.md C4's named "
          "mover: iso-ts gains '-'@7 under log-measured frequencies) ===")
    for name, ppm in (("default", default_ppm), ("weblog", weblog_ppm), ("log", log_ppm)):
        print(f"  {name:8s} ppm(0x2d '-') = {ppm[0x2d]:>7d}   "
              f"rank among 256 (1=rarest) = "
              f"{sorted(ppm).index(ppm[0x2d]) + 1}")

    rows = load_reqpos_sets()
    print()
    print(f"=== reqpos_census.tsv: {len(rows)} rows with a necessary-byte SET "
          f"of size >= 2 (the only rows a table swap CAN move) ===")

    for cmp_name, cmp_ppm in (("weblog", weblog_ppm), ("log", log_ppm)):
        movers = []
        for pop, pid, byte_set in rows:
            b_def, _ = argmin_byte(default_ppm, sorted(byte_set))
            b_cmp, _ = argmin_byte(cmp_ppm, sorted(byte_set))
            if b_def != b_cmp:
                movers.append((pop, pid, byte_set, b_def, b_cmp))
        print()
        print(f"--- default vs {cmp_name}: {len(movers)} of {len(rows)} rows "
              f"move the argmin pick ---")
        for pop, pid, byte_set, b_def, b_cmp in movers[:25]:
            hexset = ",".join(f"{b:02x}" for b in sorted(byte_set))
            print(f"    {pop}/{pid}\tset={{{hexset}}}\t"
                  f"default picks {b_def:02x} ({chr(b_def) if 32<=b_def<127 else '?'})"
                  f" -> {cmp_name} picks {b_cmp:02x} ({chr(b_cmp) if 32<=b_cmp<127 else '?'})")
        if len(movers) > 25:
            print(f"    ... and {len(movers) - 25} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
