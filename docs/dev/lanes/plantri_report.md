# plantri report: stale plants embedded in test runners (TRIAGE, no fix)

Lane plantri (sonnet), 2026-11-24, branch lane/plantri off lane/memfn-arch @ 1ec619bdf. Nothing under
src/, cli/, lib/, memfn/, tests/ or scripts/ was edited. Static decode only: no runner's `--plants`
mode was run. Evidence (a decoder and its output, not a check): `docs/dev/lanes/plantri_evidence/`.

## Summary

- Premise confirmed: `memfn/tests/run_g2_win.sh` exists (635 non-empty lines) and S1423's FROM text
  matches 0 times in `memfn/src/window.c`.
- FOUR plants are STALE, not two: S1423 and S3092 (run_g2_win.sh), S1224 (run_proof.sh) and S3064
  edit 1 of 2 (run_g2_pres.sh). Of 81 plants in the four runners that carry an `--plants` mode, 77
  apply (OK), 4 are STALE, 0 AMBIGUOUS, 0 MISSING FILE. The census is 4 runners (win, pres, proof,
  wreply); run_finder.sh and run_d3floor.sh do not carry a PLANTS list (see Population).
- Nothing runs `--plants` automatically: no Makefile target, script or test invokes it (grep below).
  So a stale plant is invisible until a person runs it, and then dies in `fail_setup` before the
  planted kit is even built.
- The anchor tripwire (`scripts/m6read_check_sab_anchors.py`) reads only `tests/mech/sabotages`. It
  runs in `make test-codegen` as [SABANCHOR] (`tests/codegen/run_codegen_tests.sh:3687`) and in
  BOILERPLATE's pre-delivery line, so extending it to the runners' plants puts them in the per-PR
  tier and in every lane's delivery run.
- Cause: commits d4b25d950 (S1423) and 4d00fccfe (S3092, S1224, S3064) moved the anchors. Two of
  the four (S1224, S3064) have a mech twin row that the SAME lane re-anchored (ad5a89b26); the
  runner's copy of the same plant was left behind.
- Fix shape (class level): one decoder shared by the runners' appliers and the checker, wired into
  [SABANCHOR]. Detail under Fix shape.

## Population

Confirmed by grep (`grep -rnE '^\s*PLANTS=|PLANTS\+?=|PLANTS=\(|--plants|plant_apply|apply_plant'`
over tests/ and memfn/tests/): a `PLANTS` id list exists in FOUR of the six named runners, not six.

| runner | plants | apply rule (the runner's own code) | target |
|---|---|---|---|
| `memfn/tests/run_g2_win.sh` | 38 | split `FILE@@FROM@@TO` at :361; heredoc python :364-370: `\n` -> newline, `\&` -> `&`, `count != 1` refuses (:368) | `memfn/src/FILE` |
| `memfn/tests/run_g2_pres.sh` | 35 (41 edits; one spec per output line, applied in order to one copy) | split :670; `un()` :675-676 (`\\n` kept as the two-character C escape, `\n` newline, `\&` `&`); `count != 1` refuses (:679) | `memfn/src/FILE`, or `@c0/X` = `docs/design/memfn/span_pick/X` (:671) |
| `tests/memfn/run_proof.sh` | 6 | same text as run_g2_win.sh: split :116, heredoc :119-125, count :123 | `memfn/src/FILE` |
| `tests/memfn/run_wreply.sh` | 2 (S1413, S1414) | `apply()` :92-109: `spec.split("@@")` into exactly 3 (a 4th `@@` raises), `\n` only, `count != 1` refuses (:103); S1413 applies the two PERTS first (:75-78, :196 `build_copy ... "${PERTS[@]}" "$spec"`), S1414 alone (:193) | `ROOT/FILE` (`src/gen/emit_dfa.c`) |

Cross-check: the ids in each `plant_spec` case equal the ids in `PLANTS` (both directions, all four
runners: 38/38, 35/35, 6/6, 2/2; no orphan case, no unlisted plant).

The other two named runners, and the other spellings found by grep:

- `tests/memfn/run_finder.sh`: no PLANTS list. Two purity plants (`purity_plant`, :196-231, calls at
  :228 and :230) match a WHOLE LINE of window.c with awk `$0 == o` and demand exactly one changed
  line (:202-209). Both lines occur once (`grep -Fxc`: 1 and 1). OK. Runs in the default gate, and a
  non-applying one is a `FAIL` line there, so it is self-reporting.
- `tests/memfn/run_d3floor.sh`: no PLANTS list in the runner; `d3_floor.py` `PLANTS = 15` (:42) are
  derived from the MEASURED sweep (records removed, repin refusals), carrying no source FROM text.
  Not countable, not applicable.
- `tests/memfn/run_purity_reach.sh` (rows in `tests/memfn/purity_rows.tsv`): 49 substring rows plus 4
  `-` rows (no text, declared UNREACHED). The applier is awk `index($0, o)`, one hit per line, `hit
  == 1` (:70-73). All 49 occur on exactly one line of window.c. OK. Default-gate, self-reporting
  ("its text does not occur exactly once").
- `tests/memfn/decider_census.py` plants (:361-384 and the section D loop): anchor-and-append,
  a missing anchor returns the error "anchor ... is not in ..." into a `bad()`. Default run unless
  `--no-plants`. Self-reporting; not counted.
- `memfn/tests/run_g2_mfind.py`, `run_g2_any.py`, `run_g2_simd.py`: UNDECODED statically, by design
  of this lane: they edit the RENDERED kit text at run time (`plant_text`), so their FROM is not
  a source-file substring. They are default-run and self-reporting (`run_g2_any.py:374`,
  `run_g2_mfind.py:488` call `bad()` on "the edit does not apply").
- `tests/mech/run_sabotage_matrix.sh`, `run_deleg_sites.sh`, `run_arm_pins.sh`, `g2_parts_selftest.sh`:
  plants are inline sed/awk beside their own assertion that the plant changed something; no list.

So the SILENT class is exactly the four shell runners with `--plants`: runners whose plants run only
when invoked by hand. Every other spelling reports its own non-application in the default run.

Method (decoder: `plantri_evidence/plant_census.py`, 0.4 s): for each runner, extract that runner's own
`plant_spec` function text verbatim, evaluate it with bash for each id in `PLANTS`, split and decode
by the rule named above, apply in order to an in-memory copy of the target, count FROM occurrences.
Positive control: the same decoder pointed at a tree whose compose.c and window.c are the parent of
4d00fccfe (`git show 4d00fccfe^:...`) reads S1224, S3092, S3064 (both edits) and S1423 as OK, count 1;
at HEAD the same four read STALE, count 0. So the decoder is not what makes them stale.

## Class

ANCHOR DRIFT IN A HAND-COPIED TEST-SIDE LITERAL THAT NO GATE EVER RE-READS. The plant's FROM text is
a second copy of a source fragment, held in a runner's shell function; the source moved and the copy
did not. The class has two parts: (a) the population (runner plants) lies outside the one tripwire's
population (mech rows), (b) the runners that own the plants are manual-only, so nothing fails.
Consequence: a G2 family's "it can fail" proof (the plant must go red) quietly certifies nothing.
Not a bug in the runners' code: each applier does exactly what it says (and `fail_setup`s loudly
when run).

Per-plant triage (git history by `git log -S` on the target file; `-S` lists the commit that CHANGED
the count of the anchor text, newest first, so the first line is the one that moved it away):

| plant | runner | target | commit that moved the anchor | what it guards, and where to re-aim |
|---|---|---|---|---|
| S1423 | run_g2_win.sh | window.c | d4b25d950 (2026-11-21, bsu2 WIP R-47 U2: "B-hors stores its probed index once (SLOT-2)"; its message re-aims mech S689/S730/S3280 and not this plant). Earlier: 0963bd61a, bc675b020 | D-hors's bound one short (`c + K > n` as `c + K - 1 > n`): the probe and verify read s[n]; G2's window family (read-limit layouts, ASan) must go red. Re-aim at `d_hors_head` (`memfn/src/window.c:4213-4221`): the line is now `int ih = w->hix;` and the bound is the `bound` parameter its callers pass. `find_head` (:4244) holds the identical `kb_printf(... "if (!(%s)) break; " ...)`, so FROM must keep the `int ih` line to stay unique. The fix lane must also re-derive TO: with the bound now a parameter, check the inline compare still differs from what the callers render |
| S3092 | run_g2_win.sh | window.c | 4d00fccfe (2026-11-16, span4kfix SEAM-1: `reply_of`/`reply_frame` write in statements); its comment says it was already re-anchored once that day by span4k (56bf1508e) | `frame_row` swapped E-find <-> E-generic on REPORT sites; G2's form class must go red. The answered branch is now `reply_of(d, out, rows); reply_frame(fp, out, rows); rc = 0;` inside `if (ok && !art->err[0] && rows_hold(...)) {` (`window.c:3090-3093`); the swap rides after `reply_frame` there. No mech twin |
| S1224 | run_proof.sh | compose.c | 4d00fccfe (same SEAM-1 commit; the ask's tail is now `kit_class(row, s, out, stp) \|\| fd_pres(...)` on one line, `compose.c:1229`). Earlier 56bf1508e | a proof bit set only by a SIMD layer (clear `proof[0][0]` bit 0 where the target admits a level): C-PROOF (proof identical across every kit target) must go red. HAS a mech twin `S1224_proof_bit_simd_only.sh`, re-anchored by ad5a89b26 (2026-11-16, span4kfix CHECK-2/3/4) onto the line-1229 shape; the runner copy still holds the pre-fix two-line shape. Re-aim = take the twin's SAB_BEFORE/AFTER |
| S3064 edit 1 of 2 | run_g2_pres.sh | compose.c | 4d00fccfe (earlier fe20a7dc4) | C2's DECISION plant: the reply (`mf_ask`'s `mf_class.run`) says `ver_len + 1` while the renderer renders the old extent; the EXTENT classifier (`plant_expect` `: EXTENT: `) must go red. Edit 1 targeted `return fd_pres(art, art->nsites + 1, s, FD_PRES_QUIET, out, &why) ? -1 : 0;` which is now the `if (fd_pres(...)) { memset(out, 0, sizeof *out); return -1; } return 0;` of the ALL_PRESENT branch (`compose.c:1198-1201`); edit 2 (the `mf_define` side) still applies. HAS a mech twin `S3064_reply_claims_one_more_position.sh`, re-anchored by ad5a89b26 (span4kfix, r27 MEM-2 (c)), which the runner did not follow |

The mech twin rows (S1224, S3064) claim in their headers to be "the same text" / "one source of the
text" as the runner's plant. They are two copies that diverged. Whether the other 38 twins' texts still
agree with their runner copies is NOT measured here (the lane counted twins by id only: win 1/38,
pres 35/35, proof 4/6, wreply 0/2 have a `tests/mech/sabotages/<id>_*.sh` row).

## Sibling count

Commands (run from the worktree root `/Users/claude/pcrec/worktrees/plantri`, absolute paths in the evidence):

    grep -rnE '^\s*PLANTS=|PLANTS\+?=|PLANTS=\(|--plants|plant_apply|apply_plant' tests memfn/tests
    python3 -I docs/dev/lanes/plantri_evidence/plant_census.py "$PWD" | cut -f1,4 | sort | uniq -c
    grep -rnE -- 'run_(g2_win|g2_pres|proof|wreply)\.sh +--plant' Makefile tests scripts memfn   # callers: none
    python3 -I scripts/m6read_check_sab_anchors.py   # "sabotages checked: 1404 (1463 anchor sites) all anchors resolve"

Plants per runner (counted by the decoder on this tree; pres counted in edits and plants):

| runner | plants total | OK | STALE | AMBIGUOUS | MISSING FILE |
|---|---|---|---|---|---|
| run_g2_win.sh | 38 | 36 | 2 (S1423, S3092) | 0 | 0 |
| run_g2_pres.sh | 35 (41 edits) | 34 (40 edits) | 1 (S3064, edit 1) | 0 | 0 |
| run_proof.sh | 6 | 5 | 1 (S1224) | 0 | 0 |
| run_wreply.sh | 2 (4 edit rows: 2 shared PERTS + S1413 + S1414) | 2 | 0 | 0 | 0 |
| run_finder.sh (purity, awk whole-line) | 2 | 2 | 0 | 0 | 0 |
| run_purity_reach.sh / purity_rows.tsv | 49 | 49 | 0 | 0 | 0 |
| run_d3floor.sh | 15 sweep-derived, no FROM text | n/a | n/a | n/a | n/a |
| run_g2_mfind/any/simd.py | UNDECODED (rendered text, run-time edit) | n/a | n/a | n/a | n/a |
| **the four `--plants` runners** | **81** | **77** | **4** | **0** | **0** |

Callers of `--plants`: none automated (the third command prints nothing; the only mentions are
comments and SAB_DOC_FIGURE text in mech rows recording a past manual run).

Twin coverage (mech row of the same id exists): win 1/38, pres 35/35, proof 4/6, wreply 0/2: 40 of
81. The tripwire therefore sees a runner plant only through a twin, and a twin's text is a separate
copy, so even twin coverage does not cover the runner's text (S1224 and S3064 show it).

## Fix shape

Class-level, to be checked against what it relies on. Candidate (accepted by main): extend the
anchor check to the runners' plants so BOILERPLATE's pre-delivery run covers them.

1. WHERE IT RUNS (checked): `scripts/m6read_check_sab_anchors.py` is invoked (a) by BOILERPLATE's
   "Any change under src/, cli/, lib/ or memfn/" line (a manual command a lane must remember), and
   (b) by `make test-codegen` as [SABANCHOR] (`tests/codegen/run_codegen_tests.sh:3687`, with a
   row-count floor at :3691), which is in `make test` and CI's per-PR tier. Adding the runner pass
   INSIDE that script (new mode or second pass, same exit code) covers both with no new BOILERPLATE
   sentence, and [SABANCHOR] must gain its own plant-population floor (81 across the four runners,
   plus the id cross-check: every `plant_spec` case id is in `PLANTS` and the reverse), otherwise an
   extraction that finds 0 plants reads clean (the script's own "unreadable is not healthy" lesson).
2. WHAT IT CAN READ (checked): the four runners keep plants as a bash `plant_spec` case function, so
   a Python check must call bash on the function text. `m6read` already shells out to bash for the
   same reason, and the evidence decoder does it in 0.4 s for all 81. Formats are NOT uniform: three
   decoders exist today (win == proof; pres with the `\\n` dialect, multi-edit, `@c0/` paths; wreply
   with PERTS prefix and an exactly-three-fields split) and the apply order matters (pres edits and
   wreply PERTS are cumulative).
3. ONE DECODER, SHARED, VERSUS SIX: recommend ONE, and it must be the runners' own applier, not a
   checker twin. The check's question is "will the runner's applier apply this?"; a re-implemented
   decoder answers a neighbouring question and drifts silently (the dialect differences above are
   already a live example: `\\n` means two different things in pres and in win/proof). Concretely:
   move the four heredoc appliers into one module under `tests/lib/` (dialect and path-root as
   arguments; the three semantics kept bit-for-bit first, unification a separate decision), have
   each runner call it, and have the checker call the same entry in count-only mode. Cost: four
   heredocs replaced, evidence for the equivalence is the existing 81 OK/4 STALE census reproduced
   through the module. Without the runners calling it, the check would be a fifth decoder.
4. NOT COVERED by that fix, state it plainly: an applying plant is not a reaching plant (it can apply
   and no longer go red: [MECH-REACH]), and `plant_expect`/`plant_want` detector text can go stale.
   The check proves only "the plant still applies exactly once", the property whose loss was
   found here.
5. Alternative, larger: derive each runner plant from its mech twin (one source). Only 40 of 81
   have twins and the runners add detector expectations the rows do not carry; not recommended
   until the check above shows how many drift (D77, build under measurement).
6. Re-aim of the four stale plants is a separate fix lane and each re-aim is a design edit to a gate
   (TO may need re-deriving); the table above gives each one's site.

House rule or mechanism broken: no rule names runner plants. The nearest are BOILERPLATE.md's
"a moved anchor makes its sabotage row certify nothing" (names only the mech-row tripwire),
`docs/dev/learnings.md` §3 "populations nobody counts (K35)", and `memfn/tests/CLAUDE.md`'s entries
for run_g2_win.sh / run_g2_pres.sh, which promise that `--plants` "must each go red" but name no
check that the plants still apply. The sibling mech rows' headers ("one source of the text") are the
claim the copies falsify.

## STATE AT HANDOFF

- Branch lane/plantri, committed; report here, evidence in `docs/dev/lanes/plantri_evidence/`
  (`plant_census.py` header says evidence, not a check; `census.tsv` its output at 1ec619bdf).
- Rulings file `docs/dev/lanes/plantri_rulings.md`: read by name before the commit and before the
  report; empty (0 bytes), so no R-n applied.
OWED: none
- No heavy run. Tracked-file edits: this report, the evidence dir, and one line in
  `docs/dev/history/claude_md/docs__dev__lanes.md`.
- Not measured: whether the other 38 twin rows' texts still equal their runner copies; whether the
  semantics of the 77 OK plants still go red (needs `--plants`, run by a box job).
