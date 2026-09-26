# tests/findings/ — the [FINDINGS] analyzer's own checks (step B3)

`docs/design/findings/design.md` §13's build plan, step B3: the analyzer
PROTOTYPE (`scripts/pcrec_analyze.py`, §10). This directory carries ONLY
what B3 alone can discharge — determinism, sharding/merging, the k=1 shard
exception and the cpfreq lead-byte-ownership seam ([r2 A-1]/[r2 A-2]),
`--check`, R26, and the collision-free declaration split ([r2 M-B1]).

B0 (the `.rxt` schema's `analysis` bundle), B1 (the accessor + default +
gate move) and B2 (resolution + CLI + `--list-analysis`) have **not
landed**. There is therefore no `pcrec` schema support for an `analysis`
bundle, no accessor to check answer identity against, and no
`--list-analysis` to round-trip the analyzer's own output through — see
`docs/dev/lanes/findb3_report.md` for exactly which design.md §11.8
acceptance items are OWED to those later steps (R27a; the python≡C item,
owed to B6) rather than skipped.

## Files

- `run_analyzer_tests.py` — the checks, run directly with
  `python3 tests/findings/run_analyzer_tests.py` (also `make
  test-findings`). PASS:/FAIL:/INFO: lines + a `checks passed: N` /
  `checks FAILED: N` trailer, matching the house convention the bash
  suites use. INFO lines are OWED items, never a silent skip (design.md
  §9's "never" — the analyzer's own `--check` fails closed on a missing
  source for the same reason).
- `fixtures/` — small, committed, deterministic inputs. Not generated at
  test time, so they diff cleanly if ever changed:
  - `basic.txt` — general-purpose ASCII sample (determinism, stdin ≡ file,
    freq+bigram shard/merge).
  - `ascii_only.txt` / `utf8_mixed.txt` — the two `serves`-collision-free
    observed rows from design.md §10.2's table (every byte < 0x80; valid
    UTF-8 with non-ASCII).
  - `invalid_utf8.bin` — a lone continuation byte with no lead byte (R26).
  - `shard1_first_byte.bin` — [r2 A-1]'s fixture: byte 0 occurs at offset 0
    ONLY, so its freq count must read exactly 1 under every shard count N.
  - `cpfreq_seam.txt` — [r2 A-2]'s fixture: repeated 2-, 3- and 4-byte code
    points at varying run lengths, so that many different N values land a
    nominal shard cut on a continuation byte of every width in turn.

## Why this target is light and unwired from `TEST_SECTIONS`

`make test-findings` needs no `make all` (the analyzer touches no pcrec C
source; it is a standalone counting + provenance tool) and is
deliberately NOT one of `TEST_SECTIONS`'s battery members — B0/B1/B2
have not landed, so there is nothing here yet that checks the compiler's
OWN behaviour (answer identity, give-up identity, the stamp). Folding it
into the full battery is B1/B2's own delivery-bar item, once the
accessor and `--list-analysis` exist for a heavier suite to exercise
(design.md §13's B1/B2 rows both name `make test-findings` as part of
their own verdict).

Maintenance: update this file when files are added/removed or their
roles change.
