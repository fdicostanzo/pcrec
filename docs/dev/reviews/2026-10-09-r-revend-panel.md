# 2026-10-09 — light D6 panel on [OPT-REVEND] (docs/design/revend.md, merge 7a6c7d50)

Two read-only critics, session 102: **rvcrit1** (opus, exactness vs libpcre2 10.46,
built ~70 new form-B twins in its scratchpad) and **rvcrit2** (sonnet, architecture
fit + checks, at main 7a6c7d50). Plus Frank's own Q1 remark ("W1 doesn't have to go
reverse then forwards whereas the rev would") — measurement lane `revq1` in flight.

Verdict: the core idea (one WINDOW row, a seeded reverse walk, s* handed as LOWER)
is UPHELD on exactness — 47 new shapes, 0 twin diffs, 0 vs libpcre2 beyond K74 — but
the row as specified has four defects that would fail the table's own checks or
crash, and the bounded-pattern parity and two timing cells are unmeasured.

## Findings and dispositions

| id | sev | finding | disposition |
|---|---|---|---|
| X1 (rvcrit1 F1) | HIGH | A speculative seed (n or n-1) can be a DEAD reverse state; the first view lookup reads `view[row(dead)]` — ASan SEGV on `\d+$(?=\n)`, `\d$(?!\n)`, `a\Z(?=\n)` etc. `ew_walk`'s A_CAT treats cwmax==0 A_LOOK as transparent, so end_pin ADMITS them (contradicts §0/§3 "trailing lookarounds declined"). W1 serves the bounded members correctly today. Corpus population 0. | FIX: `if (<p>_reverse_is_dead(reverse_state)) continue;` after the seed (measured: 9 shapes, 0 diffs); correct §3.1/§3.4; make "seed may be dead" an obligation of the §8 family helper (rev-inner shares it); answer-net cells + a sabotage row |
| X2 (rvcrit2 F1) | HIGH | `hands = CT_LOWER\|CT_VERDICT` fails `table-hands-unaccepted`: WINDOW's successors accept only LOWER\|HIT; VERDICT only CALLER. "No new edge" is false. | FIX: declare WINDOW->CALLER (13th edge, start_table.md §1.6/§4.4) or drop VERDICT (designer's call, justify) |
| X3 (rvcrit2 F2) | HIGH | R2b (`cand_read(WINDOW, RECOVER, ...)`) dereferences `.d = NULL` in start_pinned_applies; also an equivalent mutant (can never be false). | FIX: drop R2b, assert as start_pinned_assert_routing does |
| X4 (rvcrit2 F3) | HIGH | `.routes = CR_DFA` breaks WINDOW's route-independence invariant — trace build aborts `row-differs-on-route` on every admitted artifact. | FIX: `.routes = CAND_ALL_ROUTES` |
| X5 (rvcrit2 F6) | HIGH (gates) | §5.3 lists abi-number readers only; the END_WINDOW stamp-VALUE readers are missing: run_encoding_checks.sh DD12a(i) (522, 706, 1106-1112, 1334-1336, and its "utf8 always declines" premise 505-521), run_prechecks.sh §2.1/2.1b/2.2, emit_sweep.py DIFFER pin / `<W>` collapse ~692 / ASSERT_ZERO utf8 cells, S295/S297/S551; spec: facts_listing.md, cli.md, registry.md axis counts, lib/pcrec.h bit 52 + axes.def. | FIX: reader list by grep in the design; build lane re-pins all |
| X6 (rvcrit2 F9, rvcrit1 F3, Frank) | MED→decides Q1 | Form B is 3 passes vs W1's 2 (`[a-z]{0,1024}\z`: ~3072 vs 2048 steps, not "the same"); bounded parity is asserted, never timed; class-B absent from the twin population (rvcrit1 twinned 15 bounded shapes: exactness 0 diffs). Counter-force: very wide W (`[a-z]{0,60000}\z` on 1 MiB) where W1 scans W bytes and REVEND is O(match). Also: W1-first needs NO width conjunct — table order alone gives "REVEND where W1 declines", so the design's special-case argument for REVEND-first fails. | Q1 RE-OPENED to Frank with numbers: lane revq1 (bounded cells; wide-W cell to add if not covered) |
| X7 (rvcrit1 F2) | MED | The twin inserts the walk AFTER the PRESENCE pre-check, not at W1's position (§5.1). The `.txt` cells' O(1) timing depended on the stand-in subject containing an early "file.txt"; REQ_HANDOFF artifacts can't be twinned. A head-placed variant: 9 patterns, 0 diffs. | FIX: re-run the two `.txt` timing rows with the walk at the head before relaying predictions; correct "the twin is §5.1's text" |
| X8 (rvcrit2 F5) | MED | S264's reach probe `abc$` goes UNREACHED under REVEND-first (stamps "reverse", no clamp); the design says the opposite. | FIX: re-aim S264 to a W1-served pattern, or its witnesses under `-fno-rev-end` (moot if Q1 = W1 first) |
| X9 (rvcrit2 F7, rvcrit1 F4/F5) | MED | Sabotage plan lacks rows for R2a, R3, `\G` decline, lookaround transparency; row 4's witness `(?:a$)?b` is never admitted (use `(?:a$)?` or `(?:a$)?\b`); the twin's eol column is hand-entered so end_pin itself is never exercised. R2a carries the weight: witnesses `(?m:^)\w+$`, `^\w+$\|\d+$`, `(?:^\|,)\w*$` (attempt route, no reverse machine). The mover-vs-stamp check shares a source with the row selection — the independent controls are the libpcre2 answer net and the `-fno-rev-end` arm; floor the emitted `revend_seed` text, not just the stamp. | FIX in the sabotage plan |
| X10 (rvcrit2 F4) | MED | Stamp token spelled "reverse" in §5.2/§6 but the writer prints `cand_listed_name(row)` = "rev-end". | FIX: one spelling |
| X11 (rvcrit2 F8) | LOW | Empty engine (`[^\x00-\xff]$`) admitted, stamp "reverse", no walk emitted. | FIX: add `!dfa_engine_is_empty` |
| X12 (rvcrit1 F6) | LOW | K74 is wider: under utf8 `$`-ended shapes (`[^a]*$`, `\B.*$` on "a\xce") also diverge at an ill-formed end, pre-existing. | FIX: answer-net K74 exclusion covers `$` cells; note on K74 |
| X13 (rvcrit2 item 4) | LOW | test-axes has no automatic per-flag mover floor; REVEND's floor arm is new work. REVEND adds loop text near emit caps (axis12_scripts.rxt:296 is 75 B under) — add a refusal-set check. | FIX in build plan |

## Upheld
- §3.1 leftmost start under leftmost-first (PCRE2 takes the smallest start, priority only among ends at that start); form B self-heals on over-acceptance (a too-small s* costs time only).
- 47 new shapes incl. `$`/`\Z`/`\z` mixes, nullable bodies, empty matches at n/n-1, find-all after an empty match, lookbehinds, `\b`/`\B` both edges, possessives, caseless, utf8 KELVIN, startpos-guard/utf-check axes: 0 twin diffs, 0 vs libpcre2 except K74.
- Code citations in §2/§4/§5 verified at 7a6c7d50 (except limits_check.sh:348 is prose).
- Family claim (RECOVER / REVEND / rev-inner share the reverse-block helper; REVEND first) upheld; W1 shares the fact; K82's `lo` and the `(?:P)\z` bucket are siblings not members.

## Held
- Relaying the O-91 ask-2 predictions to the bench: HELD until X7's re-run and the Q1 ruling.
