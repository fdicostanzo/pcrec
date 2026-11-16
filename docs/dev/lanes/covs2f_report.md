# covs2f report — cover_cap.md rev 5.2 (review r15 applied), review r15 filed, R-45 ready

Lane covs2f (opus), 2026-11-15, design and docs only (no build go; nothing under src/, cli/, lib/,
memfn/, tests/, docs/spec/; plan.md and decisions.md untouched).

## STATE AT HANDOFF

STATE: done. Branch `lane/covs2f`, four commits on local main `ca96e60df`: the merge of lane/covs2e
(`ada1e9cdc`), review r15 filed with the process changes (`3f3488b64`), rev 5.2 (`d96d533f2`),
this report. Rulings file `docs/dev/lanes/covs2f_rulings.md`: empty at every read (before each
commit and before this report). Validation at the branch head, all GREEN: `make test-plan-lint`
(checks passed 2, failed 0), `make test-spec-history` (11 passed, 0 failed),
`scripts/check_claudemd_size.sh --all` (370 files within limits); the pre-commit staged checks
passed on every commit (52 passed, 0 failed). Probes run (evening hold respected): one `nice make
-j2 build/pcrec` in the worktree (rc 0), 4 `--emit-facts` compiles, one `sizeof` probe. No suite,
no sweep, no timing, no box-queue job. Owed: none.

Mergeability: `git merge-tree --write-tree main HEAD` with main at `38f6db8db` (two COND-FAMILY
commits past this branch's base) is CLEAN; no conflict expected.

## MERGE OF lane/covs2e

`git merge --no-ff lane/covs2e` (run alone): one conflict, in the index file
`docs/dev/history/claude_md/docs__dev__lanes.md` (main's mcfixa/mcfixb/j4fix/pinfix lines vs
covs2e's covs2d line): BOTH sides kept, markers removed. No other conflict. `make
test-plan-lint` was then made GREEN: `docs/dev/lanes/covs2d_report.md` quoted PL14's message with a
plan line cite; respelled as a paraphrase (no `plan.md:<number>` left in the tree:
`git grep -nE 'plan\.md:[0-9]'` finds none in files this lane touched). `land1115c_report.md`:
the merge did not change it (`git diff --stat main -- docs/dev/lanes/land1115c_report.md`
empty), so main's version stands.

## REVIEW FILED

- `docs/dev/reviews/2026-11-15-r15-covs2e.md`: the coordinator's draft in the house shape, header
  respelled as filed, the frozen-rulings line respelled to tags (no decisions.md, plan.md or
  requests.md line numbers), and "DISPOSITIONS RULED (manager, 2026-11-15)" carrying the brief's
  text verbatim plus a pointer to where each was applied.
- `docs/dev/reviews/2026-11-15-r15-covs2e/`: `COMMON.md`, `fixinduced.md`, `readyA.md`,
  `readyB.md`, `process.md` (critic texts verbatim, except one respelling in fixinduced.md:
  `[SIZE-KNEE] (plan.md:608)` -> `(plan.md, row [SIZE-KNEE])`).
- Indexed in `docs/dev/reviews/CLAUDE.md` (now 8,902 B, under 12 KB, so no entries needed moving
  to NOTES.md).
- Process changes (all three accepted), worded as process.md proposes:
  `.claude/skills/pcrec-critic/SKILL.md` §5 reuse clause (pruned review worktree: reuse the
  kit scripts, rebuild once), lens table readiness row (re-run the design's reader-finding
  greps and diff against its hit lists), fix-induced row (drill "moves with X by construction"
  per row KIND at X's extremes); `docs/dev/guide/critics.md` "Lessons from review rounds" gains
  the r15 entry at the top. Framework notes appended to
  `docs/dev/meta/coordinator_framework.md` (section "2026-11-15 — critic round covs2e").

## FINDINGS FIXED

Every FIX-NOW applied; none stopped by the STOP RULE (every cite verified at this branch with
`sed -n` on the named lines; code is unchanged since r15's build tree except
`tests/memfn/simd_guarded_check.py`, which no finding cites).

| id | what rev 5.2 does | where (cover_cap.md) |
|---|---|---|
| FIND-1 | Size-cap refusal re-routes, never fails (`compile.c:1434-1444` drop-anchored, `size-cap-retry`, tuning.md §2.15¶4): criterion now reads the OUTCOME at the option (`RX_DFA_SCAN` not `cover`, or `size-cap-retry`, or a kill) with its command, SUSPECTED until the combined branch; the second, cap-driven cliff stated; prediction per sweep variant (`lowsize`/`lowboth` 60,000 B cap, `emit_sweep.py:662-666`, about 304 positions by linear extrapolation); caps and ~151 C B/position as a FACT in R-45 | §11.1 compile cost, §11.1 prediction, §11.2 "What it bounds", §11.5 FACT (cost) |
| FIND-2 | Default-arm `facts a{40}(?:b|cc)` moved to `a{600}(?:b|cc)` (reads `statement-fits|601|601` today, command given), S3220 REACH moved with it, S3223 REACH -> `[0-9a-f]{@D1}`, `reach.sh` joins A5; the "no re-pointing" sentences now state the drill per row kind and the 24..500 range | §11.1 A5/A7, §11.2 readers, §11.6.1, §11.6.2, §11.6.3, §11.7 Q3 |
| FIND-3 | A2 adds `limits_check.sh` part 4(b)'s second bespoke lever + header comment; `--warn-emit-bytes=`/`PCREC_DEFAULT_WARN_EMIT_BYTES` cited as the FLAG_D precedent | §11.1 A2, §11.2 Where, §11.2.1 intro + limits-table row |
| FIND-4 | Greps widened (`-- src cli lib tests`; mech pattern adds `MF_MAX_TERM|MF_WSPAN_POS|MF_WREACH|cc_fits`; writer grep adds `table_ref`; arena grep added), build diffs grep output against lists; S3223 (A4 plant text) and S526 (B6) added; `tests/memfn` pins listed; `run_cover.sh` key `:52`, harness call `:58` | §11.1 readers + A4 + B6, §11.6.2, §11.6.3 existing rows |
| FIND-5 | `proven[]` 1,312 of `mf_class` 2,932 B; `mf_result` 3,000 B (probe command); ~132,948 B per class at 4,104 offsets; 16 arena sites per attempt; `CandAsked` trace-build only | §11.1 holders bullet, §11.5 FACT (holds) |
| FIND-6 | `MF_WMAX_SPAN` named beside `MF_MAX_SPAN_POS`; `nspan`/`nterm` `uint8_t`; ASK (2) covers all three names | §11.1 memfn.h bullet, §11.5 FACT (coupling), ASK (2) |
| FIND-7 | Outcome table reordered: "declines the cover" first, then one re-run for a first void/missing regime; void twice reads SLOWER in rows 4/5; drill shown (twice-bimodal `hex32` -> 31) | §11.4 table + note, procedure |
| FIND-8 | Stage-1 movers timed in B on one binary (4 cells x 2 encodings); only B's cells enter the rule; A is the owed record with its own floor; the rule's floor is B's A/A cells | §11.2 rule, §11.4 A, B, procedure |
| FIND-9 | B5 states MEMBERSHIP only (`memfn.h:1320-1340`); `W` end-at-`k` answer rows per long shape; short-range error's control named (B2 if a constant, a kit-tree plant if a count; R-45 ASK (1) asks which) | §11.1 B5, B7, §11.6.2, §11.7 Q2, §11.5 FACT (proof) |
| FIND-10 | B1 covers all four writers (`:557-580`) and `table_ref[j]` (`:562`, `memfn.h:684`) | §11.1 readers, B1 |
| FIND-11 | ASK (1) asks per bound whether it covers every span or REPORT span 0 only, under which names; B4 names both callers (`:609`, `:618`) and the by-name read | §11.1 readers, B4, §11.5 ASK (1) + FACT (bounds) |
| FIND-12 | ASK (5): the carrier (new sizes or where storage lives) and whether an `MF_SITE_ABI`/`MF_CLASS_V` event | §11.5 ASK (5), §11.1 abi events, B6 |
| FIND-13 | "Inverted" dropped (it would be a BUILD-REFUSED row, `run_sabotage_matrix.sh:65`); scope = whole assertion; one-clause gap ACCEPTED with B4 as its only control | §11.6.3 seam row |
| FIND-14 | P1 defined by value: comparison cut at offset 33, a literal | §11.6.3 P1/P2 row |
| FIND-15 | (a) A3 states the C15 conjunct `k <= W`, 0 resolved at C15's read, range checked in `pcrec_compile`'s option checks; (b) `@LD`/`@LD1` generator spelling equal to today's rows `:37`/`:38` at 32; (c) fail-loud `--list-limits` read | §11.1 A3/A5, §11.6.2, D27 note |
| FIND-16 | A6: three edits (INTO predicate with the listing's `k`, expected-OUT set, listing inputs) on a COPY in the stage-2 lane's evidence; covs1's file untouched | §11.1 A6 |
| FIND-17 | Spec list adds limits.md [0¶1] (range -> §3.1-§3.12 and §8) and [8b¶1] (a knee with its own option is anchored where documented) | §11.2.1 spec row, A2 |
| FIND-18 | B2 records the ceiling's `-D` becoming lower-only (row desc, limits.h derivation, section 3.12 (new)); `refbuild` (`:272-275`) widened to `"${@:2}"`; §4b's no-warning rule noted | §11.1 B2 + reference builds, §11.2 range, §11.2.1 spec row |
| FIND-19 | Not a [SIZE-KNEE] member (withdrawn); family = "selection knee" rows / [OPT-DIAL] cells; width siblings `PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`; unlock (3) re-aimed at them with a trigger that has a population | §11.7 Q4 |
| FIND-20 | DOC: "SEVEN existing blocks" (`limits.h:746-766`); the stale "six" comment (`:732`) is A2's to correct | §11.2 Where, A2 |
| DRIFT-1 | Every "LEAN, OWNER QUESTION OPEN" replaced by "RULED, D198 addendum 1" (header R5 note, §0 G4 note, §1 table, §8, §11.2); §9 Q7 ANSWERED with "route-or-stretch: agree"; §9 Q9 cites the manager's option ruling as recorded in the same addendum; §11.5 GO cites it | header, §0, §1, §8, §9 Q2/Q7/Q9, §11.2, §11.5 |
| readyB-8 | `test-axes` arm is a `job_flags` arm beside `--vm-entry-shape=` (`run_axes.sh:1923`) | §11.1 answer identity |

Numbers rev 5.2 adds, with commands: sizes (`sizeof` probe compiled `gcc -std=gnu11 -I
memfn/include` at this branch: 2932 / 1312 / 3000); 16 arena sites (`git grep -nE 'mf_class
\*\w+ = pcrec_arena_alloc|mf_result \*\w+ = pcrec_arena_alloc' -- src | wc -l`); `a{600}(?:b|cc)`
reads `statement-fits|601|601` (`build/pcrec --features all --emit-facts --pattern
'a{600}(?:b|cc)'`, `cover` section; also re-read: `a{40}(?:b|cc)` 41, the 40-letter literal 40,
`[0-9a-f]{33}` 33); ~304 positions and ~630 KB are linear extrapolations from r13's two measured
points, labelled UNMEASURED in the text.

## KIT REQUEST TEXT

The final text, identical to cover_cap.md §11.5 rev 5.2 (there as a quoted block). FACTS ONLY
(D157) apart from the owner's direction, quoted verbatim as HIS.

## R-45 (2026-11-15, pcrec manager) — window spans of up to 4095 positions ([COVER-CAP] stage 2)
- GO: the owner's build go covers stage 2 ("Go on all stages", Frank 2026-11-15). pcrec's stage-2 design (docs/design/cover_cap.md §11, rev 5.2) passed its critic round (r13) and a readiness re-check (r15, docs/dev/reviews/2026-11-15-r15-covs2e.md); the owner ruled the reading of the width limit (D198 addendum 1, "route-or-stretch: agree"). Your reply's form comes before any build; one joint landing with pcrec's stage 2.
- FACT (statement). pcrec states one REPORT window site per cover: span 0 of `k` exact positions, `1 <= k <= 4095` (4095 = pcrec's anchored-machine ceiling, 4096 states, less one), with a context position at -1 and at `k` where they constrain. Today the statement stops at 32 positions. Nothing about repeats, runs or forms is stated: repeated sets are visible in the sets passed.
- FACT (the three bounds pcrec relies on). Today pcrec admits a cover only where all three of your bounds hold: `k <= MF_WSPAN_POS` (positions per span), `k + 1 <= MF_WREACH` (the after-context span sits at offset `k`), `k < MF_MAX_FWD` (offset `k` is inside the proof range). For `k` = 4095 that is: positions per span >= 4095, reach >= 4096, proof range forward >= 4096. pcrec will assert its ceiling against all three at its build time (a `_Static_assert`). pcrec checks every window statement against your bounds BY NAME in one function with no site kind (`window_bounds_check`, `src/gen/memfn_sites.c`, two callers: the site path and the part path); every non-cover window site states at most 32 positions and reach 64 today.
- FACT (how pcrec reads the proof). pcrec compares the reply's WHOLE counted proof range with its statement: the stated set at each of offsets 0..k-1, the stated context at -1 and `k`, and "nothing proven" (all 256 bytes) at every other offset, every offset past `k` included. A reply whose range ends before offset `k` is a pcrec internal error. The comparison reads membership only (`mf_class.proven`'s own definition): a text that needs a byte to exist past `k` without testing its value is invisible to it, and pcrec's answer checks against libpcre2 (subjects ending exactly at the match end) are what see it.
- FACT (how pcrec holds the reply). `sizeof(mf_class)` is 2,932 B today, of which `proven[]` is 41 offsets x 32 B = 1,312 B; `sizeof(mf_result)` is 3,000 B (gcc 15.2 x86-64). At 4,104 offsets (4096 - (-8)) `proven[]` alone would be 131,328 B (the class about 132,948 B). pcrec holds `mf_class` BY VALUE in its cover record, in `mf_result`, and on the C stack in 8 places (one local and 7 `CandScan` locals in `src/gen/emit_dfa.c`; a ninth holder, `CandAsked`, exists only in pcrec's trace build); and in its compile ARENA, one class (or one `mf_result` holding one) per class ask or define at 16 allocation sites, per compile attempt. pcrec's compile C stack budget is 442,368 B (`PCREC_COMPILE_STACK_BUDGET`).
- FACT (coupling). `MF_MAX_SPAN_POS` and `MF_WMAX_SPAN` are both defined as `MF_MAX_TERM`. pcrec reads `MF_MAX_TERM` at three sites of its own (the VM stride assertion, the term-count bound, the ADVANCE stride bound) and `MF_WMAX_SPAN` at one (spans per alternative, in `window_bounds_check`); `mf_walt.nspan` and `mf_pred.nterm` are `uint8_t`. pcrec's own checks pin the coupling and the proof range: `tests/memfn/proof_meta.h` (`PM_NPROOF 41`, asserted equal to `MF_MAX_FWD - MF_PROOF_LO`), `tests/memfn/form_checks.py` (parses `#define MF_MAX_TERM <number>`), and mech row S526 (lowers `MF_MAX_TERM` 32 -> 31 and expects the build refused through `MF_WSPAN_POS`).
- FACT (population, census of 11,738 compiles, both encodings, before pcrec's stage 1). 1,852 compiles took the cover; almost all are short. Beyond 32 today: `k` = 36 (two uuid shapes), 40, 49, 60, 500, 1000, mostly runs of one byte class; the bench's are `lit-l40` and two uuid shapes. pcrec states no span longer than its width limit (ruled by the owner as a limit on the route, with a cliff: such a pattern runs pcrec's engine route). The limit has a built-in default (32 until pcrec's stage-2 timing sets it, before the joint landing) and a per-compile option up to 4095 (`--window-search-width=N`, `pcrec_options.window_search_width`).
- FACT (cost). Stage 1: `[0-9a-f]{24}` -> `{32}` cover, `.text` 1,752 -> 1,960 B (+208, about 26 per position; gcc 15.2 `-O2 -std=gnu11 -c` on `pcrec -p rx --features all` output, `size -A`), emitted C 17,710 -> 18,918 B (about 151 per position; linear, about 630 KB at 4095, UNMEASURED). pcrec refuses an artifact above 1,000,000 emitted C bytes (`PCREC_MAX_EMIT_BYTES`; a warning at 250,000); on a DFA artifact a size-cap refusal does not fail the compile: pcrec's size-cap ladder drops the anchored machine the cover reads and emits the engine route (`<PREFIX>_ENGINE_SEL "size-cap-retry"`), so a cover whose text exceeds the cap is lost silently. pcrec's stage-2 build records, per legal width, whether the cover survives the cap, and reports a width that does not to you. Review r9 EMITTED-2: `dig-exact-32` on (31 digits + `g`) repeated, instructions:u 230.7 M (engine route) vs 1,534.8 M (cover), x6.65; +14 % on `z`*n. The statement gives every position's set.
- OWNER DIRECTION (Frank 2026-11-15 14:35, verbatim; HIS direction to the kit, amending D198 (e) for this request, D198 addendum 1 (3)): "we have a performance dial for pcrec. it could include some options for the kit. Also, I would default to sub span loops (excepting the measured head inline ) then measure if inline was faster than the other way around. Measure three: all inline, all loops, header inline then loops. Then the speed dial option can be always inline should it prove that is faster". And (15:00): "I predict most all rx will only have a short span and will inline due to being under the inline head portion of the prover. Therefore, this issue is mostly moot". pcrec's dial (`--tune=N`) is live and can carry a kit option as a cell once your cards show one faster.
- ASK. (1) Can the statement and the reply carry spans up to 4095 positions? Name the three bounds you declare (positions per span, reach, proof range forward), whether each applies to every window span or only to a REPORT site's span 0 (and, if only there, under which names the existing 32-position / 64-reach bounds stay for the other sites), and whether the reply's counted proof range is a build-time constant or a per-reply count. (2) Do `MF_MAX_SPAN_POS`, `MF_WMAX_SPAN` and `MF_MAX_TERM` stay equal? (3) The three forms' cards per the owner's direction, at lengths of your choosing within the population above. (4) Your reading of the dense near-miss regime above (no form asked). (5) How the statement and the reply carry the longer span (each type's new size, or where its storage lives and who owns it), and whether that is an `MF_SITE_ABI` / `MF_CLASS_V` event. Reply in responses.md before building.
- Deliver: a kit branch for merge review, for ONE joint landing with pcrec's stage 2 (one pcrec `abi` event).

## OPEN QUESTIONS

OWNER (plain words):
- `fifty-cover-cap` (FYI, no answer needed unless you object): a very long shortcut can also be
  dropped by pcrec's existing size cap on the generated C (1,000,000 bytes), which quietly sends
  that pattern to the engine instead of failing. At today's size per character that only happens
  past roughly 6,500 characters, beyond the 4095 limit, so in practice only builders who lower
  the cap see it; the spec will state both cliffs. Lean: state it, no action.

MANAGER:
- `stamp`: §11.2.1's "stamp NONE (MANAGER DECISION OPEN, lean none)" is still open; r15 did not
  touch it. Lean none.
- `size-knee-row`: rev 5.1 asked main to add the width to [SIZE-KNEE]'s member list; rev 5.2
  withdraws that (FIND-19). If main already filed it, that row needs reverting; otherwise nothing
  to file (an optional sibling note on [COVER-CAP]).
- `r45-check`: R-45 is ready to file from §11.5 after your by-id check; the request cites rev
  5.2 and review r15, so file it after this branch merges (or cite the branch).
- `limits-check-comment`: `tests/registry/limits_check.sh:703-704` cites a limits.md section
  ("the one size option that is not raise-only") that limits.md does not contain; a stale comment
  for the A2 lane (or a filed nit).
