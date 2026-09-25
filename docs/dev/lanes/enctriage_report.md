# enctriage — triage of `run_encoding_checks.sh`'s five reds (2026-09-25)

Lane enctriage (opus), branch `lane/enctriage` from main 4080ee34. Triage
of `tests/codegen/run_encoding_checks.sh` (`make test-encoding-checks`,
opt-in), which read `checks passed: 10 / checks failed: 5` on main.

## Findings first

1. **NO DD-12 (7) VIOLATION.** All five reds are CHECK GAPS. No emitted
   artifact, byte or utf8, carries a run-time encoding test in the hot
   path. The reporting lane guessed that [OPT-ENDWIN] might have put an
   encoding conditional into anchor-adjacent patterns. That is refuted by
   reading the artifacts. ENDWIN's clamp is a compile-time choice. It is
   emitted under `byte` and declined under `utf8` by design
   (`PcrecEnc.start_cls != NULL`, plan.md's [OPT-ENDWIN] row, "FOUR
   structural declines"). Both artifacts declare the choice in
   `<PREFIX>_END_WINDOW`.
2. **ONE CAUSE-CLASS, FOUR MECHANISMS, PLUS ONE PRE-EXISTING GAP.** Four
   emission changes landed between 2026-09-19 and 2026-09-22. That was a
   window when DD12a(i) compared ZERO pairs, because D118 on 2026-09-21
   killed its CLI call and nothing re-read it until varmvp's revival on
   2026-09-23. Each change moved encoding-owned or encoding-selected text
   out of reach of the check's named regions:

   | cause | landed | what the check lost | reds it produced |
   |---|---|---|---|
   | [EMIT-VERB] classed the K50 attempt-guard's marker comment NONESSENTIAL | 2026-09-19 (the [EMIT-VERB] WIP series, 404aa6f8..e82c7fbb) | `K50_CONT_OPEN` anchored on a comment the default `-fno-comments` artifact no longer carries | `startpos_attempt` never excised (red 1). `\A` and 16 more pairs showed the utf8 `continue` as hot-path text (part of red 5) |
   | [OPT-ANCHOR-VM] bounds an anchored VM retry loop by `attempt_max` | 2026-09-22 | the K49 advance anchor was the one literal `attempt_position >= subject_length` | `\A(cat|dog)`, `\Gcat\Kdog`, `(\Aa)+` …: the utf8 skip loop was compared as hot-path text (part of red 5) |
   | [OPT-ENDWIN] clamps under `byte` and declines under `utf8` | 2026-09-22 | no region for the clamp or its stamp | `b\z`, `\z`, `\Z`, `$` … strict divergences (red 5). Two K50 manifest rows (first `\z`) were pushed OUT of the gate class into strict, so they read STALE (red 2) |
   | [OPT-FREQPICK] reads its frequency prior only under `byte`, and [OPT-PRECHECK-ADMIT] G1 dominance reads the same prior | 2026-09-22 (47f697db) | no region for the scanned member, its offset or `REQ_WHY` | offset-0 specialization and `dominated`/`emitted` split: strict divergences (red 5). The integer-only member differences fell into the K50 DATA bar and read as UN-MANIFESTED gate pairs (red 3: 5 at slice 250, first `(?:\Gab)+`) |
   | `var_valid`'s CALL SITE (varmvp, 2026-09-23) | 2026-09-23 | only the definition was excised | the check's own `^${v}$` witness diverged in strict from the day it was added |

   Red 4 (the 11-row `#UNDECLARED` exact list "no longer matches") is a
   CONSEQUENCE, not a separate cause. That list is compared EXACTLY against
   the run's strict-diverging set (`STRICTPAT`). Every extra strict pair
   from the causes above made the list mismatch. With the causes handled,
   the 4 reached `#UNDECLARED` rows match exactly.
3. **THE THREE "[K50]" REDS HAVE THE SAME CAUSES.** The brief treated
   them as owned by `[K50-DD12AI-MANIFEST]`. They are not a manifest
   backlog: `startpos_attempt` is [EMIT-VERB], the stale rows are
   [OPT-ENDWIN], and the un-manifested pairs are [OPT-FREQPICK]. **The
   manifest was NOT touched and needs no re-derivation**. After the fix,
   every reached row is swept into its class and no un-manifested pair
   enters. The 22 pairs that entered the gate class after the first two
   re-anchorings were ALL non-nullable. Under the manifest's own
   membership rule ("EVERY ROW IS NULLABLE … a row appearing here that
   cannot match empty is a defect in the predicate") that ruled out K50
   as their cause before any diff was read. Every one was a FREQPICK
   member/offset difference. **Recommendation: close
   `[K50-DD12AI-MANIFEST]` as discharged by this lane**, subject to the
   full-population run below.
4. **SIDE FINDING (mech, K35-shaped, NOT fixed here).**
   `run_sabotage_matrix.sh`'s `encoding` arm scores the script's
   ABSOLUTE `checks failed` count, with no clean-tree baseline. The script
   has been red on a clean tree since D118 (2026-09-21: first the PAIRS
   floor, then these five). So every sabotage row whose `SAB_SUITES`
   includes `encoding` (S229, S-U8) has read that arm as DETECTED whatever
   the sabotage did. Their other arms and S-U8's `SAB_REACH_POP` are
   unaffected. This lane makes the clean baseline green again, which
   restores the arm's meaning. It does not stop a future standing red
   (the script is opt-in and rides no `TEST_SECTIONS` entry) from
   silently doing the same. It wants a ruling: subtract a clean-tree
   baseline in the arm, or wire the script into a gated section.
5. **OBSERVATIONS for the optimization lane (no defect, no change
   made).** (a) `reqbyte.c:585` and `emit_dfa.c`'s
   `req_byte_dominated_by` test `encoding == PCREC_ENC_BYTE` BY NAME.
   That is compile-time, not hot-path, so it is not a (7) violation. It
   is still the one place a `PcrecEnc` PROPERTY (for example "the
   frequency table this encoding is keyed to", NULL for utf8) would do
   what ENDWIN already does through `start_cls`. General-mechanism rule;
   no measured need yet. (b) ENDWIN's utf8 decline is a missed
   optimization rather than a necessity: a byte bound of
   `cwmax × max_code_units` plus a forward step to the next boundary would
   be sound. That is a D77 candidate only if a utf8 bench cell ever
   measures it.

## What changed (only `tests/codegen/run_encoding_checks.sh`; no `src/`)

Each cause became a NAMED, COUNTED, FLOORED region, held to the artifact's
own stamp. This follows the check's standing doctrine (K52's
"marker-delimited regions … normalized on both sides with the
normalization COUNTED"):

- **K49 advance**: `GUARD_RE` accepts both emitted forms
  (`subject_length` | `attempt_max`), `emit_vm.c`'s `attempt_position >= %s`.
- **K50 attempt guard**: `K50_CONT_RE` anchors on the statement itself
  (`if (start > search_from && !(…)) continue;`). A comment marker is
  something the verbosity axis can delete. The comment-anchored path is
  kept for `-fcomments` artifacts.
- **[OPT-ENDWIN]**: the two-line clamp is excised (`end_window`) and the
  stamp normalized (`end_window_stamp`). Per side, a clamp must be present
  iff the stamp is not `"none"`. Byte and utf8 may differ in ONE direction
  only: byte clamps, utf8 declines.
- **[OPT-FREQPICK]**: WHICH MEMBER is scanned is normalized, and nothing
  else. That covers the `memchr` byte in the run loop, the `REQ_BYTE`
  stamp, the offset `K` in the compare and the `@K` of `REQ_RUN`
  (`req_pick`). The offset-0 specialization is rewritten to the general
  form first (`req_run_offset0`), and only under an `@0` stamp. The RUN
  itself (hex bytes, length, loop) is still compared token for token.
  Coherence per side: the scanned byte must be the run's member at the
  stamped offset and must equal `REQ_BYTE`, on both pre-check forms.
- **[OPT-PRECHECK-ADMIT] G1**: the three-line single-byte pre-check is
  excised (`req_check`) and `REQ_WHY` normalized (`req_why_stamp`). Per
  side, a pre-check (single or run) must be present iff the stamp reads
  `"emitted"`. Verdicts may differ only as byte `dominated` / utf8
  `emitted`.
- **`var_valid` call site** (`var_valid_call`): the definition was
  already excised; the call site now is too. Coherence: a side may not
  call a `var_valid` it does not define.
- **`span_ci_*` helpers** now count under their own `span_ci_helper` key,
  so rule (b)'s per-pair symmetry no longer flags every caseless pair as
  "asymmetric (byte=1 utf8=4)". That was a false FINDING line introduced
  by varmvp's rename fold.
- The `#UNDECLARED` "not reached in this slice" count now reads its own
  reachable file. It used to print "11 not reached" beside "4 reached".
- All coherence violations are aggregated as `SELECT_BAD`, a FAIL checked
  OUTSIDE the section's `elif` chain so no earlier red can mask it. Every
  new counter joins the non-vacuity floor loop.

## Validation

- `bash tests/codegen/run_encoding_checks.sh` (default
  `ENC_MAX_BLOCKS=250`, the file `make test-encoding-checks` runs), on
  `lane/enctriage`: **`checks passed: 11 / checks failed: 0`** (was 10/5).
  New counters at slice 250: `startpos_attempt=17`, `advance=166` (was
  144), `end_window=70`, `req_run_offset0=42`, `req_check=90`,
  `req_pick=498`, `var_valid_call=1`, `span_ci_helper=3`, `SELECT_BAD=0`.
- **Attribution by A/B before any edit**: the ORIGINAL script over
  artifacts compiled `-fcomments -fno-end-window` took red 5 from 102 to
  39, cleared the `startpos_attempt` and stale reds, and left the
  FREQPICK/ANCHOR-VM residue. That separated the causes empirically
  before the regions were written.
- **Sabotage (scratch `git archive` tree of c36d3ff6, env-gated plants in
  `src/gen/emit_dfa.c`, all five runs from ONE build, never committed)**:

  | run | plant | DD12a(i) result |
  |---|---|---|
  | control | none | 11/0 GREEN |
  | 1 | a real hot-path encoding conditional: `if (search_from & 1) search_from++;` under utf8, beside the clamp site | RED, 239/244 strict pairs, FINDING names the planted line |
  | 2 | ENDWIN clamp emitted under utf8 with the stamp still `"none"` | RED, `SELECT_BAD` 254 pairs |
  | 3 | byte-side run `memchr` scans member+1 (stamp unchanged) | RED, `SELECT_BAD` 29 pairs |
  | 4 | utf8 dominance verdict forced (`dominated` where byte `emitted`) | RED, `SELECT_BAD` 8 pairs. **The ONLY red of the run**: this plant changes no answer, so `SELECT_BAD` is its sole witness |

  Plants 2 and 3 also turn §8.5 red, because they change answers. The
  DD12a(i) coherence arm catches them independently of §8.5.
- `make strict`: clean.
- `make test` NOT run and not needed: no `src/`, `cli/` or `lib/` change,
  and the edited script rides no `TEST_SECTIONS` entry.

## OWED

- **The full-population run** (`ENC_MAX_BLOCKS=0`, ~6,600 compiles). The
  manifest is calibrated there (164 gate rows, 11 `#UNDECLARED`), and a
  slice-250 green cannot certify rows the slice never reaches. It is the
  Linux-slot run the script's header names. On darwin it would be roughly
  30-40 min of this check alone. Command:
  `ENC_MAX_BLOCKS=0 bash tests/codegen/run_encoding_checks.sh > LOG 2>&1`.
  Completion line: `checks failed: N`. It is expected to be 0. A non-zero
  result names either a further emission change of the same class or a
  genuine manifest row, and the FINDING/STALE lines say which.
- A ruling on finding 4 (the mech `encoding` arm's missing baseline).
- `[K50-DD12AI-MANIFEST]` disposition (finding 3). This lane recommends
  closing it after the full-population run.
