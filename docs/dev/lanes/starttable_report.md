# Lane `starttable` — report

**Brief:** design the unified start-strategy table (Frank, 2026-10-06: "So are we
going to reorganize around a single start strategy decision table?" then "Agree
with direction"). DESIGN ONLY: nothing under `src/`, `cli/`, `lib/` or `tests/`
changed. Branch `lane/starttable` off main `74379fe0` (abi 64).

## Delivered

- `docs/design/start_table.md`, the design note:
  - §1 the row contract;
  - §2 the complete inventory, with the disagreements;
  - §3 the no-mover refactor plan;
  - §4 the new-row sockets;
  - §5 the standing questions plus the SIBLING-OF-A-FAMILY table;
  - §6 nine questions for Frank, each with a recommendation;
  - §7 the lenses.
- `docs/design/start_table/`: four read-only instruments and their outputs
  (own CLAUDE.md).
- `docs/design/CLAUDE.md`: entries for both.

## The design in five lines

1. ONE array `cand_rows[]` of ONE row type `CandRow`. A SLOT column (the
   question a row answers: window, presence, width, first, next, retry, bound,
   recover) joins today's `routes` column. The walk is first-match per (slot,
   route), the existing `cand_routed` mechanism along a second axis, never a
   planner, never product rows.
2. Inventory: 37 rows in 8 slots over 3 routes. They replace 5 arrays and 5
   inline decisions. Every predicate is today's function by pointer, so
   selection identity holds by construction (§2.3). The sweep is the
   measurement of that argument.
3. Disagreements found (none changes an answer; all preserved by the refactor,
   each fix a separate ruled change):
   - D-1: ENG_ATTEMPT's `"memchr"` (a predecessor byte) is read by G1 as a
     start byte. 33 artifacts.
   - D-2: `RX_DFA_START "reverse-pass"` is stamped on 452 ATTEMPT and
     empty-engine artifacts that carry no reverse machine. The spec at
     `match_api.md#stamp-dfa-start` contradicts itself on this.
   - D-2b: the machine's and the `start_anchor` fact's one-start proofs differ
     on 1 of 388 patterns, `(?(DEFINE)(?<g>\Ga))(?&g)`.
   - D-3: `--list-axes`' `first-memchr-bounded` desc still says `T = S & E*`
     (`axes_dump.c:106`), stale since D148 addendum 3.
4. Refactor:
   - **Commits:** eight (C0 instrument, C1 trace, C2 implement, C3-C5 replace
     slot by slot with D148 Q2's rename in C3, C6 the listing reads the table,
     C7 a declared stream-5-only listing fix). Functions stay byte-stable; only
     tables and walks move.
   - **Sabotage rows:** 6 re-aimed (S283, S284, S462, S473, S372, S441), 47 re-run.
   - **Held:** abi 64, every stamp vocabulary, and every deny bit, with fact
     denies kept on their facts (bit 28 empties `start_anchor` for four readers,
     not only the bound rows).
5. Sockets:
   - D151 reverse-walk → two NEXT rows plus FIRST `handoff-rev`. Needs the new
     fact `inner_split`, a prefix reverse machine, and a memfn FIND that
     resumes at `hit + 1`.
   - I5 → a context column on the VM hat row (fact `start_ctx`, a memfn
     two-position FIND).
   - K90 → RETRY's `adaptive*` rows gain the VM-only route (K90's "density
     disarm" IS [OPT-HYB-RESEED]'s rule), plus a first-position peel shared
     with K88.

## Findings worth the manager's attention

- **`emit_sweep.py` cannot prove the no-mover claim as-is.**
  - Its argv streams never pass `-e utf8` (`compile_stream_c`, `:429`).
  - Nothing compares `--emit-facts`. Its `used` column shows which facts a
    predicate ASKED, and a reordered or eager walk moves it with no emitted
    byte moving (unless the byte rate's first ask moves, which `RX_FINDINGS`
    shows: `pcrec_find_stamp` is ask-dependent).
  - Plan commit C0 adds both arms (`--extra ARG`, a sixth stream).
- **Rows the corpus cannot prove by bytes:**
  - `set-leads` is invisible to stamps (it stamps `"emitted"`).
  - `fixed` has population 0 at default.
  - `run-pinned-bounded` and `window` are 0 under utf8.
  - Small populations: `ceiling` 6, `gstart` 5/20, `adaptive-dense` 13,
    count-collapsed 1-2.
  - §3.4 names each row's witness. C2's trace build adds a per-row hit counter.
- **The census is stamp-read and shares `emit_sweep`'s own population**
  (`enumerate_corpus` imported): 3,595 distinct patterns, 3,221-3,230 compiling
  per arm.

## Validation

No build validation applies: nothing under `src/` changed. Instruments were run
on this lane's own `make -j4 CC=gcc-16` build of `74379fe0` (Mac):

- `row_census.py`: 4 arms, complete (`row_census.txt`).
- `anchor_agree.py`: 388 ATTEMPT artifacts, complete.
- `site_census.sh` and `sabotage_anchors.py`: complete (207 gen-file rows, 53
  start-family).

No owed runs.

## For a resuming agent

The note is self-contained. The open items are Frank's §6 Q1-Q9, chiefly Q1:
D151 Q5 timing, fold now as a D151 addendum. Next is the light D6 panel (§6 Q9:
two critics, sound + checks). Commit C0 (the `emit_sweep` arms) is independent
of the rulings and could be chartered first.
