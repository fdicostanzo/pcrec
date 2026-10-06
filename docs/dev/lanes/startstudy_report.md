# Lane startstudy — report (2026-10-06)

Branch `lane/startstudy` off main `6816f839`. STUDY ONLY: nothing under `src/`,
`cli/`, `lib/`, `tests/` changed; no `make test` run (a plain `make -j4 CC=gcc-16`
built the worktree's compiler for the census).

## Delivered

- `docs/design/where_to_start.md` — the study note answering Frank's three
  questions (A inventory + unification, B Q2 soundness, C prefilter form,
  D census, E recommendation + six questions, standing questions, lenses).
- `docs/design/where_to_start/` — `rinner_model.py` (soundness model vs
  libpcre2 10.48, mutation table), `census.py` (landmark census, controls
  C1-C3), committed transcripts/outputs, own CLAUDE.md.
- `REFERENCES.md` — new entry `[RArevinner]` (rust regex-automata reverse-inner
  and its July-2026 leftmost fix, issue #1354 / commit 64ad0b6).
- `docs/design/CLAUDE.md` — index entries for both.

## Validation (complete; nothing owed by this lane)

- Model, byte (seed 1, 6,000 patterns): gated tactic 0 / 192,079 single
  searches, 0 / 33,228 find-alls; handoff, fallback and rust-guard forms 0;
  tactic (c) end 0 / 5,380. Mutations detected: max_start 636, lo0 1,531,
  slice 382, noverify 11,811, skipL 37, restart_s1 329 (find-all). Ungated:
  19 wrong on split-ambiguous; erased-atomic walk 11 wrong. `--selftest` PASS.
- Model, utf8 (seed 2, 4,000): gated 0 / 137,692 + 0 / 23,976; all mutations
  detected; `--selftest` PASS.
- Census: corpus 3,333 compiled / 2,448 parsed, bench 321 / 274. Controls:
  C1 11/11, C2 0 violations (2,258 + 331 bytes), C3 0 disagreements.

## Headline answers

1. Yes: every start mechanism is a row (landmark, scanner, mapping, verifier);
   the missing mapping is EXACT behind an UNBOUNDED prefix.
2. Yes: the reverse walk records the smallest accepting start; exact iff P is
   backref/atomic-free and the split unambiguous (fixed-width P, or P cannot
   consume every byte of L). Without the gate it is wrong — the bug rust fixed.
3. Yes: candidates feed any anchored verifier; only P must be backref-free, so
   the VM backref population (no DFA prefilter today) gets one. 5 corpus / 3
   bench VM-only patterns qualify (dup-param-detect, bak-1, bak-g-rel, the
   K65/K66 witnesses).

## Resume notes for a follow-up

- Owed before any build: re-run `rinner_model.py` against the 10.46 reference
  over ssh (light, ~30 s CPU), and the §5.2 item-1 hand twin of
  `capability/dup-param-detect` (the row's D77 trigger).
- The census reader's coverage is 85% bench / 73% corpus; VM-only parses worst.
