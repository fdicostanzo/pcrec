# docs/dev/lanes/predspec24_evidence/ — rev 24 of predicates_draft.md, its evidence engine

Lane predspec24 (2026-11-17), DESIGN EVIDENCE: every answer revision 24 of `docs/design/predicates_draft.md` states
(§R) is a line of `predspec24_model.out`. Rules nothing.

## Files

- `predspec24_model.py` — the engine. Loads lane lastpass's engine (`../lastpass_evidence/lastpass_model.py`, up to
  its PART A) in memory, and through it pathimpact's PCRE path enumerator and rxmodel's libpcre2-8 ctypes harness
  (`../rxmodel_evidence/pcre2h.py`); adds rev 24's nodes (two-valued conditions, the last pass, the one-pattern
  `occurrences`, the committed hit list, atomic, the first row before the filter, the complement over every path,
  `when` as `x & (NOT c | p)`) and a switch back to rev 23.2's rules. PARTS:
  A the catalogue (68 lines, NOW = rev 24, BEFORE = rev 23.2, PRINTED CHECK against rev 23.2's printed answers);
  B the ways to write the old meanings (lastpass's table, 20 rows + a value read + CONTROLS that must differ);
  C callout models run on libpcre2 (20 models, every mode); D properties (distributivity, admits, the `&` LAW,
  De Morgan, the SQL picture, last-pass moves); E the open items, every candidate; F whole-text legality.
- `predspec24_model.out` — the forward run (committed).

## Run (one engine process at a time; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec24 && timeout 1800 python3 -I \
        <worktree>/docs/dev/lanes/predspec24_evidence/predspec24_model.py > fwd.out)

Switches (environment): `PREDSPEC24_SWAP=1` enumerates PCRE's path order by another route (output identical but
the ORDER line); `PREDSPEC24_SABOTAGE=1` makes a bare looped label read the FIRST pass and, with SWAP, reverses
the path order (the PCRE2 checks then fail); `PREDSPEC24_RULES=23.2` runs NOW under rev 23.2's rules (MOVED 0,
printed mismatches 0). The lane report lists each run's command and counts.

Needs libpcre2-8 (the system library; rxmodel's harness finds it) and Python 3. Each run takes about a minute.
