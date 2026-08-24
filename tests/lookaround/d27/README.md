# tests/lookaround/d27/ — the [M6.6.3] BLINDED corpus (D27)

Authored 2026-08-24 by a D27-blinded author (cell la27) from ONLY the
design extract (docs/design/la_d27_extract.md = lookaround_design.md
§2 + §7 + §10.1), la_oracle.py (libpcre2 10.46) and python3 `re`, per
docs/testing.md — never from src/ or tests/. 7 files, 457 blocks,
2,408 oracle-checked assertions; the author's own from-scratch checker
(checker.py, failing-direction-tested against four planted corruptions)
ran 0 failures. The generators (gen_matrix.py etc.) and checker are kept
for provenance; only the .rxt files are the corpus.

ACCEPTANCE (manager, without the author, per design §10.3 —
cells / failures / triage): first run 1,849 cases / 310 failed /
71 distinct compile failures; ALL failures were COMPILE failures — zero
answer mismatches, zero pcrec-wrong cells. Triage classes, all
corpus-wrong, fixed by the manager in place (the author's original is
preserved in the cell record within the journal):
1. `features` lines were placed BEFORE their `pattern` line; the harness
   attaches directives to the block already open (docs/testing.md:
   "given after its `pattern` line", features "block-scoped like
   `flags`"), so every list landed one block late — visible only at
   feature-transition boundaries. Mechanical move; no expectation edited.
2. Missing module names in feature lists (`classes` for \w,
   `assertions` for \A/\z, `atomic-groups` for possessive spellings) —
   rooted in the manager's brief naming only assertions/backrefs.
3. The `(?<=(a|ba))c` family asserted PCRE2's acceptance, but a grouped
   alternation is ONE top-level branch of width 1..2 — VARIABLE, refused
   by §2.5's ruled subset (G2: libpcre2 accepts). Converted to perr with
   the triage note inline — the exact boundary the design predicted
   readers would get wrong, caught by the acceptance in the predicted
   direction (a refusal, never a miscompile).
FINAL RUN: 1,819 cases / 0 failed / 0 compile failures / 0 pending-vm.
THE BLINDED CORPUS FOUND NO IMPLEMENTATION DIVERGENCE.

These files ride `make test` via the harness's recursive walk of
tests/. run_lookaround_diff.sh and run_expansion_diff.sh do NOT
enumerate this subdirectory (checked at landing); their population
guards are unaffected.
