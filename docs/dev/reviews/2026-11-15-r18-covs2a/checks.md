# checks findings

Budget: matrix = 3 plants x (reach + ~4 cases rows) x 2 compilers ~= 30, plus default-move probes ~= 40; total planned <= 120 of the 300-compile cap.

## Findings

### CHECKS-1 — CONFIRMED — the DEFAULT's reach into C15 is unwitnessed at stage A (every past-default witness declines at the kit conjunct anyway)
- Severity: maintenance (test-coverage); no answer/speed effect at stage A; becomes answer-relevant only once the kit raises its bounds (B). Effort: small. Blast radius: C15's `cover_width_limit` fallback (src/gen/known.c:332-336) and S3223's REACH pin.
- At D = 32 the width conjunct and the kit-bound conjuncts (`MF_WSPAN_POS` etc., 32) coincide, and C15 names both `width-limit`. So `[0-9a-f]{@D1}`, `@LD1`, `a{600}(?:b|cc)`, `a{4095}` all decline `width-limit` whatever the default reads.
- Repro (stand-in for a misread default): `build/pcrec --features all --window-search-width=32` vs `=4095` on `[0-9a-f]{33}` -> both `scan=unanchored`, facts `width-limit|33|33|...`; on `a{600}(?:b|cc)` -> both `width-limit|601|601|...` (4 compiles + 4 listings). So a plant `return w ? w : PCREC_ANCHORED_MAX_STATES - 1;` (or any fallback >= 32) leaves every verdict/facts row, S3223's REACH (`REACH-DECLINE`, `REACH-WHY=[width-limit]`: the pin cannot tell WHICH conjunct declined), width_opt.c (only explicit widths 23/24 route-checked; `legal(0)` checks compile only) and the registry green. Only the `@D` side (`[0-9a-f]{32}` cover) constrains it, from below.
- Fix options: record it as a known stage-A gap that B7's raised bounds close; or one lowered-default reference build (run_b3_checks.sh's `refbuild` already exists: `-DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=24`, then `[0-9a-f]{25}` must decline and `[0-9a-f]{24}` cover) — the one input that makes this check fail.

### CHECKS-2 — CONFIRMED — the CLI lever `--window-search-width` has no behavioural witness; the one `W` row does not reach its site
- Severity: maintenance (test-coverage) / doc (spec promises "out of range refused, CLI and library"). Effort: small. Blast radius: cli/main.c:1455-1463, loader.sh `kp_flags` W arm, cases.tsv `verdict W [0-9a-f]{24} cover`.
- The only `W` row expects `cover` for `[0-9a-f]{24}`, which is ALSO `cover` on the default arm (probe: default `cover|24|24`). So deleting loader.sh's `*W*)` line, or cli/main.c:1462 storing nothing, leaves kitproof green. width_opt.c exercises the LIBRARY field only. limits_check.sh 4(b) is a string-presence grep of `"--window-search-width=` (it stays green with the assignment deleted). No tests/cli case covers the CLI's refusal of 0 / 4096 / -1 (grep of tests/: no CLI hit).
- The design defers the discriminating `W` twins (n >= 33) to B7, but nothing at stage A checks the CLI path at all, and the branch is otherwise shipped (the flag is in cli.md/tuning.md).
- Fix: one cases row on a NARROWER width (e.g. a letter mapping `--window-search-width=<D - 1>` with `[0-9a-f]{@D}` expecting decline; it fails if the CLI drops the value), plus one tests/cli refusal line (`--window-search-width=4096` exits nonzero).

### CHECKS-3 — CONFIRMED — loader.sh is not fail-loud on malformed rows: an unknown FLAGS letter is ignored, and a malformed `width=N` reads `decline`
- Severity: maintenance. Effort: trivial (two `case` refusals). Blast radius: every cases.tsv row; loader.sh:30-37, :55-57.
- Repro (pure bash, no compile): `KP_D=32; kp_width_verdict 4O` -> `decline`; `kp_width_verdict ""` -> `decline` (the `[ -le ]` error goes to stderr, then the `||` arm). `kp_flags w` -> empty (a typo'd `w` row runs on the default arm silently). A row `width=4O` on a pattern past D therefore passes without testing anything about N.
- This is the same K35 hole loader.sh's header says it closes for `--list-limits` ("never an empty substitution"), left open for the rows themselves. Also an unsubstituted `@` form cannot happen (all four are replaced), held.
- Fix: in `kp_width_verdict` refuse a non-decimal N (FAIL line); in `kp_flags` refuse letters outside `-iuRW`.

### CHECKS-4 — CONFIRMED (pre-existing shape, in the rewritten map) — a DELETED FLAGS-map line goes red in `make test` only for `u`; `R` and `W` deletions are silent there
- Severity: maintenance. Effort: small. Blast radius: loader.sh `kp_flags` (now the ONE map: run_cover.sh's `flags()` and reach.sh both call it, so there is no second copy to drift; held).
- `R`: the only R row is `verdict R cat$ decline` (S1139). Probe: `cat$` default -> `RX_DFA_SCAN "rev-end"`, with `-fno-rev-end` -> `"unanchored"`: both read `decline`, so deleting `*R*)` is green in make test; it would surface only as S1139 MISSED in a mech run (REACH reads `REACH-DECLINE` either way). `W`: silent, CHECKS-2. `u`: the two `facts u` rows key the listing on `utf8` and would go NOROW/differ -> red. `i`: no row uses `i` (population count by FLAGS: verdict - 41, u 6, R 1, W 1; facts - 17, u 2; answer - 92, u 13), so a deleted `i` line is silent and an `i` row added later is untested by construction.
- INVENTED map line: silent (no row uses it); harmless.
- Fix: make the R witness exact (`verdict` reading the stamp value, or a facts R row), and either drop `i` or give it a row.

## PROBED-AND-HELD

Compile count: ~165 pcrec invocations (compile + --emit-facts listing counted separately), all done by 23:49, under the 300 cap. Note: the plant trees have no build/pcrec-harness, so `reach.sh <plant>` reads REACH-FAILED for every pattern (an artifact of the kit, not of the rows; mech runs REACH on the CLEAN tree anyway). Plant compares were therefore run by hand with `<plant>/build/pcrec --features all -p rx` (RX_DFA_SCAN) and `--emit-facts` (cover row); the harness lever renders the default build's text since D172 S3.

(a) Sabotage rows, plant vs review at the shipped default D = 32:
- S3223 (bypass): `[0-9a-f]{@D1}` = {33} and `@LD1` -> LOUD (compile fails: "a window span of 33 positions at 0 lies outside the kit's shape bounds"); review reads unanchored / width-limit. `a{600}(?:b|cc)` facts -> SILENT-MOVE to `end-at-k|601|601|...` (detected by the facts row too); `a{4095}` -> LOUD. `[0-9a-f]{32}`, `{24}`, `{25}`, `\b[0-9a-f]{32}\b` -> SAME (cover). Detected.
- S3234 (off by one): `[0-9a-f]{@D}`, `@LD`, `\b[0-9a-f]{32}\b` -> SILENT-MOVE cover -> unanchored/`width-limit|32` (detected by those verdict rows); {24}/{25} SAME; {33} SAME. Detected; REACH on the clean tree REACH-COVER / [cover] as pinned.
- S1131 (pointer fill): `ac|bd`, `a[xy]c|b[xy]d`, `[a-z0-9_ ]\b[a-z ]` facts -> SILENT-MOVE `exact/machine-inexact` -> `end-at-k` (all three facts rows detect); `ab|abc|ad`, `abcd|abce` SAME. Width-independent. Detected.
- S3220 (j < 32, no plant tree; by reasoning): `a{600}(?:b|cc)` record cut to 32 vs `width-limit|601` -> facts DIFFER; REACH on the clean tree REACH-FACTS-EQUAL/[width-limit] (review compiler: `width-limit|601|601|...`, held).
- Clean-tree REACH (review tree, reach.sh): `[0-9a-f]{@D1}` REACH-DECLINE [width-limit]; `[0-9a-f]{@D}` REACH-COVER [cover]; `@LD` COVER [cover]; `@LD1` DECLINE [width-limit]. All match the rows' SAB_REACH_EXPECT.

(a) Moved default, stand-in `--window-search-width=N` with the @-forms expanded at N (widths 1, 24, 31; 3 compilers):
- S3223 at N = 1/24/31: `[0-9a-f]{N+1}` review decline width-limit, plant COVER -> SILENT-MOVE, detected by the @D1 row. At N = 32: LOUD. Held.
- S3234 at N = 1/24/31: `[0-9a-f]{N}` (and `a` at 1, the 31-letter literal at 31) review cover, plant decline width-limit -> detected by @D/@LD. Held.
- Verdict rows `width=N` at N <= 31 read the right side (e.g. {25} at 24 declines). Held.
- D in 33..500 (the rule's range) BEFORE the kit: the CLEAN tree goes red (`[0-9a-f]{@D}` expects cover, kit bound declines) -- loud, and the design's own B-step. Not silent. D in 601..4095 (legal for -D, outside the rule): the facts `a{600}` row goes red on the clean tree -- loud, acknowledged by cover_cap.md §11.6.1. The only SILENT direction is CHECKS-1 (the default misread upward at stage A).
- kp_limits: missing/non-decimal/out-of-range rows return 1 with a FAIL line in both readers (read; not run).

(b) Declared lists:
- limits_check.sh 4(b) bespoke levers: DELETING the width block -> PCREC_DEFAULT_WINDOW_SEARCH_WIDTH (renders `flag+-D`) has no lever -> `[override-honesty] ... stale claim` bad, AND the pass count drops 44 -> 43 -> run_registry_tests.sh's pin red. Two reds. INVENTING a block for a flag absent from cli/main.c -> its own `bad`; inventing one for a present flag naming a plain `-D` row -> "hidden lever" bad; naming a non-FLAG_D/BUILD_D row -> ignored by (c) (scope, by the arm's charter), but the extra `ok` moves the 44 pin -> red. Held. Weakness only: presence grep, CHECKS-2.
- cloud_mech_shards.tsv: cloud_mech_check.sh compares rows to on-disk ids EXACTLY (DROPPED / EXTRA / DUPLICATED / out-of-range / empty shard), with a selftest. Deleted or invented line -> red. It runs as the mech kind's dispatch check (cloud_kinds.tsv:32), not in make test -- which is how S3170/S3198 were missing at main 4456e9127 unseen until this branch. S3234's file exists on disk; table rows S3170/S3198/S3234 match files. Held.
- FLAGS map: one copy (loader.sh), so run_cover.sh/reach.sh cannot diverge (held); per-letter deletion results in CHECKS-4.
- width_opt.c: 8 `ok` lines vs floor 8, an early exit/crash goes red; refusal at -1/ceil/ceil+1 and legal 0/1/ceil-1 checked through the library. Held.
- Verdict floor 49: rows now 49 verdict (41 - + 6 u + 1 R + 1 W); facts 19; the floor equals the count, so a deleted verdict row goes red. Held.
- run_b3_checks.sh / run_anchored_match.sh extra -D: the width -D is required by the new _Static_assert (width <= ceiling - 1) so without it the reference build fails to compile and the existing `bad` lines fire -- a deleted -D goes red loudly. Held.
