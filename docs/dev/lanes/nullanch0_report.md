# nullanch0 — [NULLABLE-ANCH] STEP 0, the compile-side census (2026-10-08)

Lane nullanch0 (sonnet), branch `lane/nullanch0` from main 9029f5db (abi 66).
MEASUREMENT ONLY: nothing under `src/`, `lib/`, `cli/`, `tests/` or
`docs/spec/` changed. Instruments and data: `docs/dev/optloop/nullanch/`
(own CLAUDE.md; `run_census.sh` rebuilds everything). Bench inputs were READ
from `pcrec-bench` (patterns, published reports, `NOTES.md`), never written.
Every timing below is SCRATCH TIER: this box (Ryzen 7 7700X), one core
(`taskset -c 3`), median of 5 batches. It is indicative, not a bench result.

## 1. The shape, defined

The plan row's words ("nullable/anchored nested-repeat patterns") describe
three different things. Measured, only one of them is the defect.

- **The decline.** `select_engine.c:839` `lang_nullable_declinable =
  pcrec_fact_nullable(cx) && !has_bref && !has_call && !force_on`. When it
  holds for a VM-chosen, un-rung compile, `fit->prefilter_declined_nullable_
  default` removes the hybrid's exact prefilter (`ESEL declined-nullable-
  default`, `RX_VM_PREFILTER none`). Its stated premise (internal.h /
  `--emit-ir` `no-nullable-exact`): the exact language "would admit a
  zero-length match at every position and could never dismiss one".
- **The premise is false when every EMPTY path crosses an absolute start
  assertion AND an absolute end assertion.** `pcrec_nullable` answers `true`
  for `A_BOL`/`A_EOL`/`A_END` ("an assertion that fails still consumes
  nothing"), so `^(\s+)*$` is nullable; but its only empty match needs
  offset 0 and offset n at once, i.e. a subject of at most one newline. On
  every other subject the exact DFA dismisses in linear time.
- **The corrected predicate (name proposed: `empty_admits`, an E1 fact beside
  `nullable`, owner `src/facts/widths.c`).** Compute the set of empty-path
  constraint masks per node: bit S = the path crosses `^`/`\A` non-multiline,
  bit E = it crosses `$`/`\Z`/`\z` non-multiline; every other zero-width node
  (lookaround, `A_CTX`, `\G`, `\K`, multiline `^`/`$`, backreference, call,
  variable) is mask 0, i.e. always satisfiable, which is today's answer.
  Concatenation ORs masks pairwise, alternation unions, a `{0,n}` repeat adds
  mask 0 and the OR-closure of its body, `{m>=1,..}` is the closure (or the
  body alone when `rmax == 1`), capture/atomic/WCLASS are transparent.
  `empty_admits` = some empty path has NOT both S and E. The decline then
  reads `empty_admits` instead of `nullable`; `nullable` itself stays for its
  other readers (the collapse gate `compile.c:1843`, `pcrec_startgate_needed`
  — both need BARE nullability for their own soundness, so the fact must be
  new, not an edit). It errs only toward declining (mask 0 by default), the
  safe direction every reader of this family takes.

`anch_probe.c` implements that and cross-checks its nullability against
`pcrec_nullable` on every pattern: **0 disagreements over 4,666 patterns.**

## 2. Census (docs/dev/optloop/nullanch/census_summary.txt)

Population: 4,666 distinct patterns (every `pattern`/`pattern-esc` line under
`tests/**/*.rxt` at byte encoding and `--features all`, emit_sweep's own
convention, plus 303 distinct bench patterns from every published set); 4,262
compile at default (404 refuse: module/encoding-gated, same as emit_sweep).
Per-block `flags`/`encoding`/`features` are NOT applied to corpus patterns —
the same limitation emit_sweep has; a utf8 arm was not run.

| row | count |
|---|---|
| nullable (any route) | 623 |
| declined on nullability (`ESEL declined-nullable[-default]`) | **114** (corpus 111, bench 3) |
| of which `RX_VM_START anchored` | 15 |
| of which `empty_admits` is FALSE (dismissable) | **14** |
| of those 14, killed by `has_var` regardless (module vars) | 9 |
| **LIVE movers under the corrected predicate** | **5** |

The 5, each confirmed by `-fprefilter` (which already overrides the decline;
it builds `RX_VM_PREFILTER "hybrid"`, `ESEL selected`):

| pattern | origin | notes |
|---|---|---|
| `^(([a-z]+)*)+$` | bench capability `evil-alt-nested` | 3 caps, rungs cursor+frames-unbounded, guard slot 6 |
| `^(\s+)*$` | bench capability `trim-nested-star` | 2 caps, rungs cursor+frames-unbounded, no guard slot |
| `^(a{2,4})?$` | corpus `d27_edge.rxt` | frames-bounded |
| `^(a?)(?1)*$` | corpus `recursion/d27/sr_define.rxt` | guard slot 4 |
| `^(?:(?<g>a?)){0}(?&g)*+$` | corpus `recursion/quantified.rxt` | guard slot 4 |

The other 9 dismissable declines are the `^${v...}$` family of module `vars`
(`-fprefilter` refuses them outright; `has_var` forces `fit->prefilter` false
at `select_engine.c:862`). Finding F1: they are STAMPED `declined-nullable-
default` although the nullable decline is not what turns their prefilter off —
`lang_nullable_declinable` has no `!has_var` conjunct, so `esel_of` arm 2
outranks the var reason. Harmless to behaviour, wrong in attribution; it is a
token-identity fact refactor B ([DEC-FALLBACK]) must decide on purpose (keep
the token, or let the corrected predicate carry `!has_var`).

The other 100 declines are RIGHT declines and stay: 99 are unanchored
(`(a*)*`, `(a|b*)*c?`-class: an empty match exists at offset 0 of every
subject, mask 0), 1 is start-anchored with an assertion-free or one-sided empty
path (`^a*`-class: always matches). Masks by hex set over the 114 declines:
`{mask0}` 89, `{mask3}` 14, `$`-only 6, `^`-only 2, mixed 3.

Shape neighbours that are NOT the defect (so the row should not widen to
them): the bench's own other four nested ReDoS members (`^(\d+)+$`,
`^(\d+\s*)+$`, `^([a-zA-Z0-9._%+-]+)+@`, `^(([0-9]+[-/])+)+$`) are
non-nullable and already get `vm selected, hybrid`. 133 nested nullable
patterns are DFA-engine (no captures) and have no problem. A census over
"nested" (308) or "nullbody" (398) alone would mostly count patterns the
decline never touches.

## 3. Stamps, prefilter/start, and the VM at the nested loop (witnesses)

Both witnesses at default (`-p rx --features all`): `RX_ENGINE vm`,
`ENGINE_WHY capture group at pattern offset 1`, `ENGINE_SEL declined-nullable-
default`, `RX_VM_PREFILTER none`, `RX_VM_START anchored`, `RX_END_WINDOW
none`, `RX_REQ_BYTE/RUN none`, `RX_VM_RUNGS 0x5` (cursor + frames-unbounded),
`RX_VM_STRATS 0x2` (backtracking), `RX_VM_POSS_ARMS 0x0`, possessify marked 0/3
(evil) and 0/2 (trim) — the inner `+` cannot be possessified because the
enclosing `*`/`+` loop's follow set includes its own class, so
[ART-POSS-ARMS] does not reach this shape. No counter rung, no revdet, not
frameless. `--no-captures` is already `dfa / selected` for both (the shipped
exact-DFA arm, f2_rescue_split §3).

`--emit-ir` at the nested loop (evil): the outer `+` is peeled once
(max-replicas 2); the inner `([a-z]+)*` is the frames-unbounded loop and the
outer copy carries the empty-iteration guard
("nullable body (empty-iteration guard)", slot 6 "where the current iteration
began"). trim's body `\s+` is not nullable, so its `*` is a plain
frames-unbounded loop with NO guard slot: the guard is not what makes either
witness slow. What does: each loop iteration pushes a resume frame, and a
nested loop over a run of n letters has ~2^n ways to partition it. The default
artifact has nothing in front of the VM, so a near-miss subject enumerates
them all.

## 4. Where the time goes (INDICATIVE local timing, `timing_results.tsv`)

Arms: default (VM, prefilter declined), `-fprefilter` (the hand twin of the
corrected predicate), `--no-captures` (shipped DFA arm). ns/call, median.

Near-miss subjects (the bench's P5 shape, stated for short nomatch as the
bench confirmed):

| subject | default | `-fprefilter` twin | `--no-captures` |
|---|---|---|---|
| trim, 12 spaces + `x` | 26,309 | 22.3 | 20.7 |
| trim, 16 spaces + `x` | 421,419 | 22.8 | 21.2 |
| trim, 19 spaces + `x` (bench `rd-trim-near-miss`) | 3,376,663 | 23.2 | 21.6 |
| evil, 12 `a` + `!` | 8,399,123 | 21.9 | 20.4 |
| evil, 16 `a` + `!` | 924,373,634 | 22.5 | 21.0 |
| evil, 17 `a` + `!` (bench `rd-evil-alt-near-miss`) | **-2 (STEPS give-up) after 2.21 s** | 22.8 (nomatch) | 21.1 |
| trim, 60,000 spaces + `x` | **-2 give-up after 1.59 s** | 22.0 | — |

The default cost doubles per added byte (trim ~8x per 3 bytes, ~4.4 ns per
resume step against the 500M-step budget), i.e. the x1081 vs re2 is this
exponential, not a constant factor. The give-up is also why the bench's short
cell excludes pcrec's evil row today (pass rate 97%): admitting the gate turns
a typed `PCREC_ERR_STEPS` into the correct `nomatch` — an answer
IMPROVEMENT of the K65 kind, never a wrong answer.

Throughput-shaped subjects (3 nomatch texts, rejected at the first non-class
byte): trim 22.3 default / 20.5 twin (no movement). evil default 3.9 µs on my
synthetic 64 KiB and 1 MiB lowercase-prose text against 21 ns with the gate
(the cost is the first word's length: 2^letters; the bench's own t-64k reads
10.4 µs, t-256k 45 ns, t-1m 1.2 µs, all dominated by the first word). That is
the x5.98 vs jit: the cell is the VM re-partitioning one leading word.

The cost side (matching subjects; the twin adds a forward DFA pass over a
subject the VM then also walks):

| subject | default | twin | nocaps DFA |
|---|---|---|---|
| trim, 4 spaces (match) | 22.8 | 24.7 | 19.6 |
| evil, `aaaa` (match) | 26.9 | 28.3 | 19.5 |
| trim, 4,000 spaces (match) | 1,557 | 3,024 | 2,196 |
| trim, 60,000 spaces (match) | 23,123 | 44,985 | 32,794 |
| evil, 60,000 `a` (match) | 10,954 | 32,786 | 21,924 |

So admission trades a ~+1.4-2 ns/call tax on tiny hits and a ~2-3x tax on LONG
MATCHING subjects (the DFA walk is the latency-bound ~0.37 ns/B chain of
[OPT-5]) for 10^3-10^5x on near-misses and the removal of the give-up. The
bench has no long matching subject for either pattern (hits are 4-24 B), so
its cells see only the win; a real consumer validating a long all-matching
field would see the tax. Artifact size: +645 B `.text` (evil) / +357 B (trim)
over the default; the nocaps arm is smaller than both (1.3 KB).

## 5. Answer safety (diff_results.txt)

Default vs `-fprefilter` twin, rc and every capture span, EVERY subject up to
a length bound over a small alphabet: 15 pattern/alphabet rows including the
five live patterns, `^(a|b*)*$`, `^(\s*\w*)*$` (the brief's examples),
`^(a*)*$` and `\A(a*)*\z`, with `\n` alphabets for `$`'s before-final-newline
arm: 8,191 to 88,573 subjects per row, **0 DIFFERENT, 0 give-ups either side**
at those lengths. Not a proof; it is the soundness evidence the build row
should re-run at full width (below).

## 6. Causes and mechanisms

1. **Anchor-blind nullability in the decline (THE ROW).** Population 5 live
   patterns (0.12% of the compiled population), which are exactly the two
   bench cells plus three corpus ones; the 9 `vars` rows are attribution only.
   Mechanism: the `empty_admits` fact above, read by `lang_nullable_declinable`
   (replacing `pcrec_fact_nullable` there only). One general fact, no special
   case for these two spellings; it also covers `^(a|b*)*$`, `^(\s*\w*)*$`,
   `\A(a*)*\z` and any `^...$` shape the corpus does not have (probe-checked).
   It is the "corrected predicate" D153 says refactor B folds: it is one
   conjunct input to the prefilter admission ternary (`select_engine.c:862`),
   so B's STEP 0 census should read it as a declared input. A `-fno-` deny is
   unnecessary for soundness (the twin is `-fprefilter`) but the row will want
   one for the answer-identity sweep; that is the build lane's call.
2. **The VM's exponential partitioning of a run by nested loops** (the actual
   time sink). Untouched by (1) for subjects the DFA admits, which on these
   patterns are exactly the matching ones, where the greedy first path
   succeeds linearly. It is D119's BACKTRACK-fundamental class for any shape
   the gate does not cover (an unanchored nullable nested loop is unreachable
   by any dismissal: it always matches). Not a row; named so the row's scope
   statement is honest.
3. **Capture-forcing is the door, not the cause.** Both witnesses are
   `dfa selected` without captures. The alternative mechanism — a match-here
   DFA verdict in front of the captures VM regardless of nullability — is
   [CAPTURES-DFA-MB]'s territory and round3_selection §7's ruling keeps it out
   of this row. This census gives that ruling its evidence: (1) alone already
   removes both cells' gap (22 ns vs 3.4 ms / give-up), so no case exists for
   widening the row.
4. **The matching-subject tax** (~2-3x at 60 KB on the twin) is not a cause of
   the losses; it is the regression side the alpha must measure. It is the
   known DFA-walk latency; an admission term in [SEL-COST] §4 is the place a
   subject-length-dependent answer would live. D77: no mechanism is proposed
   for it until a measured loss.
5. **Attribution drift (F1)** above, and one more: `ESEL declined-nullable-
   default` also covers `has_var` rows, so the token's count over the corpus
   (112) overstates the decline's own population by 9.

## 7. Plan-row text proposed (the lane does not edit plan.md)

[NULLABLE-ANCH] STEP 0 DONE (nullanch0): the shape is "the decline's bare
nullability vs a pattern whose every empty path crosses `^` and `$`"; live
population 5 of 4,262 (bench evil-alt-nested, trim-nested-star; corpus
d27_edge `^(a{2,4})?$`, sr_define `^(a?)(?1)*$`, quantified
`^(?:(?<g>a?)){0}(?&g)*+$`). Hand twin (`-fprefilter`) 22 ns vs 3.4 ms /
STEPS give-up on the near-misses; ~2-3x tax on long matching subjects.
Step 1: the E1 fact `empty_admits`, one conjunct change in
`lang_nullable_declinable`, an abi event (stamps move on 5 artifacts + any
that gain `RX_VM_PREFILTER`), docs/spec hunk (tuning/match_api §6.3 ESEL
wording), alpha on the bench's own cells after pcrecdev2's subjects question.

## 8. Build-row obligations the census surfaces (for the next lane)

- Mover manifest: exactly the 5 above by ID at `--features all` byte encoding;
  re-run `census.py` after the build: `ESEL declined-nullable-default` must
  fall from 112 to 107 (the 9 var rows stay stamped unless F1 is decided the
  other way) and the five must read `hybrid`.
- `gu`-style cells: none of the five has a `gu` expectation in the corpus
  (`grep` of the three corpus files); the bench evil short cell changes from
  give-up to answered.
- Re-aim: `run_search_pinned.sh`/`run_prechecks.sh` witnesses that use these
  spellings, if any (grep at build time); the answer differential of §5 at
  full width plus a libpcre2 10.46 transcript for the five.
- Both hat-style gates ([OPT-4.2]'s `rung-vs-default` fields) are untouched:
  the collapse gate keeps bare nullability.
- Do NOT reuse `pcrec_nullable` for the new fact: its `A_BOL/A_EOL/A_END`
  arms are `true` on purpose (the guard and start-gate readers need that).

## 9. Bench-only questions (for the manager to relay via pcrecdev2)

1. Would a new capability-set version add (a) a LONG near-miss for these two
   patterns and (b) a long MATCHING subject? Today's subjects cap near-misses
   at 20 B (NOTES.md P5) and hits at 24 B, so the bench shows only the win;
   the 2-3x matching tax (§4) has no bench cell and the 10^5x near-miss win is
   hidden behind the 20 B cap.
2. When pcrec stops giving up on `rd-evil-alt-near-miss`, does the bench's
   short cell (pass rate 97%, "auto EXCLUDED" in gapreport 10-03) re-enter the
   like-for-like population, and does the comparison need a pin note?
3. Which text and offset do `t-64k/t-256k/t-1m` open with (the 10.4 µs / 45 ns
   / 1.2 µs spread for evil is the first-word length)? Needed only to predict
   the throughput cell exactly rather than "tens of ns".

## 10. Validation and ownership

No suite was run: no `src/`, `tests/` or `docs/spec/` file changed, so there
is no `make test` to owe. Probe builds with `-Wall -Wextra` clean; the census
re-ran end to end from `run_census.sh`'s parts. Updated: this directory's
CLAUDE.md, `docs/dev/optloop/CLAUDE.md`, `docs/dev/lanes/CLAUDE.md`.
