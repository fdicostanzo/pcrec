# tests/mech — GENERATE the sabotage detection tables ([MECH-1])

Every "disabling X fails N cases" figure that used to live by hand in
`tests/*/CLAUDE.md` goes stale silently, and every attempt to maintain one by
hand in this project has failed at least once — including twice inside the
same review, and once inside the paragraph written specifically to warn about
it (see `tests/reject/CLAUDE.md`). This directory owns the sabotage EDITS
themselves, applies each to a pristine tree, and prints a matrix instead of a
copied number. Docs should cite this script's output, not a hand-typed count.

## Files

- **run_sabotage_matrix.sh** — the driver. For each sabotage: build a FRESH
  tree from `git archive HEAD` (never a copy of the real working tree, never a
  reused/reverted tree — the [MECH-2] lesson), apply the edit through
  `lib/replace.py`, build it (`make all` inside the scratch tree only — this
  never runs `make` in the real repository), run the suites the sabotage's own
  table says are relevant, and print one row of the matrix. Supports running a
  single sabotage by id prefix: `bash tests/mech/run_sabotage_matrix.sh S13`.
  Env: `CC`, `KEEP=1` (keep scratch trees + suite logs instead of deleting
  them), `MECH_SCRATCH` (scratch root), `JOBS`.
- **lib/replace.py** — the ONLY thing that edits a sabotaged file. Takes a
  target file plus literal BEFORE/AFTER text and a required occurrence count;
  refuses to run if the anchor text is not found exactly that many times
  (source drifted since the sabotage was written — this is the anchor-mismatch
  failure mode this tool exists to make loud instead of silent), refuses if
  BEFORE == AFTER (a no-op sabotage is a bug in the definition), and refuses to
  trust the result unless the AFTER text is actually present afterward. One
  mechanism for every sabotage, whether it is a substitution, an insertion
  (BEFORE is a prefix of AFTER), or a deletion (AFTER is empty).
- **sabotages/S\*.sh** — one file per sabotage, sourced by the driver. Sets
  `SAB_ID`, `SAB_FILE`, `SAB_SUITES` (space-separated: `codegen` `trie`
  `reject` `harness`), `SAB_DESC`, `SAB_BEFORE`, `SAB_AFTER`, and optionally
  `SAB_COUNT` (default 1) and `SAB_HARNESS_TARGET` (an .rxt file or dir to
  scope the `harness` suite to, instead of the whole corpus). Each file also
  carries `SAB_DOC_FIGURE`, a comment-and-string record of what the source
  documentation claimed, purely for humans diffing a re-run against the docs —
  the matrix itself does not read it.

## What "suites" means here

- `codegen` → `tests/codegen/run_codegen_tests.sh` (OS-0b/OS-1/TS-1/skip
  checks, ~28 structural checks bundled in one script).
- `trie` → `tests/codegen/run_trie_identity.sh` (the M2.8 differential check,
  default 500 patterns x 2 sweeps, plus 3 positive controls).
- `reject` → `tests/reject/run_reject_tests.sh` (the "requires module 'X'"
  mandate, hand-written + iterated + accept-control rows).
- `harness` → `tests/harness/run.sh`, optionally scoped to
  `SAB_HARNESS_TARGET` for speed (most sabotages here only need
  `tests/base/caseless.rxt`, not the full corpus).

`make bench` is deliberately NOT wired in here — R3.1 already measured that
S01's skip-state sabotage also fails bench case (e)'s throughput budget, but
running bench per-sabotage would make a ~10-sabotage sweep minutes slower for
a signal the codegen suite's structural check already gives for free. Add a
`bench` suite case here if a future sabotage's ONLY signal is a throughput
budget.

## A sabotage that zero checks catch is the finding, not a bug

If every suite a sabotage lists comes back with 0 failures, the matrix marks
that row `**UNDETECTED**` and calls it out again in a summary block at the
end. `S19-new-wrong-row` is EXPECTED to land there — it is the SR-4 blind spot
`tests/reject/CLAUDE.md` documents by hand ("iteration reads the same table
the parser renders from... a NEW row with a plausible wrong module and no
hand-written entry" is caught by nothing in this repository except PC-3, which
needs libpcre2 and is out of scope for this matrix). An UNDETECTED verdict on
any OTHER row means a guard regressed and is the thing to go fix.

## Sabotages NOT encoded here, and why

Two sabotages documented in `tests/codegen/CLAUDE.md`'s `run_trie_identity.sh`
table are deliberately absent from `sabotages/`:

- **The naive rule-1 sabotage** ("skip the accept split, change nothing
  else"). The table itself says not to use it: it leaves items with
  `len == depth` in the list for rule 2, which then reads past the allocated
  key — a 32-byte arena over-read, so the failure count is UNSTABLE between
  builds (171 and 176 observed for the same edit). This tool refuses to encode
  a sabotage whose own documentation says its count is not reproducible;
  encoding it would print a number that looks authoritative and isn't.
- **The memory-safe replacement rule-1 sabotage** ("hoist every accept to the
  front instead of partitioning the list around each, keep removing them from
  the list"). This is a real, encodable edit, but the table describes it in
  PROSE — a restructuring of `trie_build`'s rule-1 loop in `src/ir/nfa.c`
  (around the `has_acc` block) — not as literal before/after text. Every other
  row in every sabotage table in this project IS literal text, which is what
  makes `lib/replace.py`'s anchor mechanism honest: it can assert the edit
  landed because it knows exactly what "landed" means. Turning this one
  sabotage into a literal patch would mean writing the actual accept-hoisting
  C code myself and asserting *that specific rewrite* landed — a choice with
  more than one honest implementation, unlike every other row here. Left for
  whoever touches `trie_build` next to encode alongside the code change, the
  way the project's convention already asks ("add its check here in the same
  change").

One sabotage was ADAPTED rather than copied literally: `S15-drop-d-row`
translates `tests/reject/CLAUDE.md`'s "drop `{'d', \"classes\"},` from
`esc_modules`" — `esc_modules` as a distinct table no longer exists; the SR-2
registry refactor folded it into the `ESC(...)` rows in `src/parse/registry.c`
that `S16`/`S17`/`S19` already sabotage. The functionally equivalent edit
today is deleting the `ESC('d', ...)` row outright, which is what `S15` does.

## Conventions

Anchors are copied from `git show HEAD:<path>`, not from a live working-tree
read — this repository routinely has other in-flight work editing the same
files this tool sabotages, and `run_sabotage_matrix.sh` always measures
committed HEAD via `git archive` regardless of what the working tree looks
like at run time. When source drifts enough that an anchor's occurrence count
changes, the run fails LOUDLY on that one sabotage (`APPLY-FAILED`, anchor
mismatch reported by `lib/replace.py`) rather than silently applying to the
wrong place or skipping. Re-derive the anchor from `git show HEAD:<path>` when
that happens; do not weaken the count check.

Maintenance: when a codegen/reject/trie sabotage table gains a new row with an
exact literal edit, add a matching `sabotages/S<NN>_*.sh` here in the same
change, per the project's own sabotage-validation convention.
