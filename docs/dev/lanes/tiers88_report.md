# Lane tiers88 — report

**Task**: draft the pcrec-bench inbox item for plan row [FINDINGS-BENCH-TIERS]
(D125 phase-4 stock-take; Frank's ruling: numbers first — the bench produces
DEFAULT/DECLARED/PROFILED/ORACLE-BEST as a scratch-tier measurement before
any decision to touch a published bench config). DOCS ONLY, no `make` runs
(measurement-charter tier). Worktree `worktrees/tiers88`, branch
`lane/tiers88`.

## Deliverable

`docs/dev/lanes/tiers88_inbox_draft.md` — the drafted item, numbered **I-118**
(pcrec-bench's `docs/dev/inbox_from_pcrec.md` tail at draft time was I-117).
It is a draft only; the manager is the sole writer of that file in
pcrec-bench (D78) and commits it there as its own `[inbox]` commit.

## What the draft covers

- The four columns and which pcrec mechanism realizes each (DEFAULT = no
  `--analysis`; DECLARED/PROFILED = `--analysis`/`-I`/`config analysis`
  naming a bundle built by `build/pcrec-analyze`, differing only in where
  the counted corpus comes from; ORACLE-BEST = a sweep of `--engine=`,
  `--no-captures`, `--tune=`).
- Exact CLI spellings pulled from the as-built spec (`docs/spec/findings.md`
  B1/B2/B5/B6, `docs/spec/cli.md`, `docs/spec/tuning.md` §5,
  `docs/spec/rxt_format.md`, `analyze/CLAUDE.md`), not invented: the
  analyzer's four command forms, the three resolution stops and their
  refusal table, `--list-analysis`'s digest cross-check, the `<PREFIX>
  _FINDINGS`/`rx_info.findings` stamp as the way to prove which bundle
  actually answered a compile.
- The provenance/disjointness argument shape (pcrec's own R30 precedent —
  "RUNEST's bench use was evaluation-only", proven by a provenance review
  + grep, not a new mechanism), handed to the bench to prove with its own
  manifest per the plan row's own text.
- PROFILED's train/test split, tied to `docs/design/findings/design.md`
  §11.4's own split-discipline shape (RUNEST's four disjoint splits,
  ranking checked against an independent scorer) as the ARGUMENT FORM, not
  a mechanism the bench inherits — the bench's own subject generators are
  what would produce the two disjoint sets.
- ORACLE-BEST's configuration axes named explicitly (`--engine=dfa|vm|
  auto`, `--no-captures`, `--tune=-2..2`/aliases) with the ruling I made
  explicit in the draft (held findings fixed, sweep only engine/captures/
  tune) since the plan row itself doesn't literally pin that scope — flagged
  as my own reading rather than a re-derivation of something already ruled.
- A pointer at `testees/pcrec/configs.toml`'s existing 31 testees (already
  covering engine/captures/cflags/cc/emitted-size-cap axes) and that NONE
  of them names `--tune=` yet — ORACLE-BEST is the first customer for it.

## pcrec-side gaps named in the draft (filed, not built)

1. **`run-rarity`/`bigram`/`markov1` has no live reader.** [FINDINGS] B4 is
   HELD (Frank's ruling, 2026-09-28: no reader has a trigger yet, needs
   unbuilt [OPT-LITSCAN] S4). A bundle can carry a `bigram` block and it
   will parse, but nothing consumes it yet — named explicitly so the bench
   doesn't build a run-rarity-only DECLARED/PROFILED cell expecting it to
   move anything.
2. **The default-path utf8 lottery isn't fully fixed.** [FIND-TIE] fixed
   the PICK reader's tie-rule inconsistency (merged), but [FIND-UTF8-
   DEFAULT] (filed, not scheduled) — an ASCII-only bundle (including both
   shipped `weblog`/`log`) still can't discriminate non-ASCII bytes under
   `-e utf8`. Named so a `-e utf8` DECLARED/PROFILED cell against a mostly-
   ASCII corpus isn't misread as a measurement bug.
3. **No shipped bundle obviously matches every bench subject class**
   (`bench/capability`'s wild patterns, `bench/altwide`'s synthetic
   alternations) — `weblog`/`log` are candidates for `bench/loglines`/
   `bench/email`-shaped classes only; left as a bench-side judgment call
   (question 4 in the draft) rather than a build item.

Nothing above requires a pcrec build to start on `bench/loglines`/
`bench/email` — the analyzer, resolution, CLI and byte-rate readers are
all merged to main today.

## Questions for the bench dev (pcrecdev2), listed separately in the draft, not answered here

1. Existing train/test split primitive, or does PROFILED need new
   generator support?
2. Which existing report/reduce grain should the four-column table ride?
3. Scratch-tier sweep shape for the tune/engine/captures product — ad hoc
   `pcrec-local`/`quick`, or a dedicated script?
4. Is `weblog`/`log` close enough for `bench/loglines`/`bench/email`
   DECLARED, or does the bench want its own disjoint corpus?
5. Where should the disjointness manifest and any bench-authored bundles
   live?

## Not done, and why

- No `make` run of any kind (measurement-charter/docs-only lane; the brief
  explicitly excludes it).
- No bench-side file touched (read-only per the scope mandate — read
  `APPROACH.md`, `testees/pcrec/CLAUDE.md`/`configs.toml`, `bench/*/
  CLAUDE.md`, and the tail of `docs/dev/inbox_from_pcrec.md` there, wrote
  nothing there).
- The exact report/reduce grain and split-primitive existence are left as
  open questions rather than guessed at, per the "don't reverse-engineer
  the bench's ledgers" rule — I read `APPROACH.md` §4's architecture
  description of the reporter/reducer but did not go into
  `pcrecbench/reduce.py` to guess its exact grain.

## Files touched

- `docs/dev/lanes/tiers88_inbox_draft.md` (new)
- `docs/dev/lanes/tiers88_report.md` (this file, new)

No plan.md/journal edit made (the row is [FINDINGS-BENCH-TIERS], already
STATE:started with this lane named in it; the manager updates it at
delivery/merge per usual practice).
