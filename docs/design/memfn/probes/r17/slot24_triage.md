# slot24 triage (R17-a, kit tip c6a3bfea, ref a080c69a)

Read-only triage. Nothing was built or run except the one allowed light check
(item 4: `run_spec_history.sh`, 2.8 s, pinned to cpus 12-15, `gnutimeout 120`,
`ROOT_DIR` = the r17 worktree, `PYTHONDONTWRITEBYTECODE=1`).

Classes: (a) pre-existing on the ref/main, (b) caused by R17-a, (c) harness/environment.

| # | item | class | owner of the fix | slot re-run needed |
|---|---|---|---|---|
| 1 | SWEEP variants rc=1 (24 lines) | (a) pre-existing; instrument pins stale on main | main (`scripts/emit_sweep.py`) | no (variants sweep only, optional, after main re-pins) |
| 2 | SWEEP utf8 rc=1 (4 lines + a 5th the judge did not count) | (a) pre-existing; same stale pins plus an `--extra`-arm floor that is plain-arm-only | main (`scripts/emit_sweep.py`) | no (utf8 sweep only, optional) |
| 3 | N2 rc=4 (floor_fail=1, floor_placeholder=1) | floor_fail is (b), a selection-count move by design, 0 byte movers; the placeholder is (a) | kit (`tests/memfn/row_floors.tsv`) | no N2 re-run; re-read the report against the amended file |
| 4 | `test-spec-history` Error 1 | (a) pre-existing on main | main (one review doc) | no (that one section, 3 s) |
| 5 | mech `undetected: 1` | (a) a declared-UNDETECTED row, `unexpected: 0`; not an R17-a row | none (judge wording) | no |

## 1. SWEEP variants, rc=1, 24 floor/manifest lines

Every line comes in an a/b pair (side a = ref a080c69a, side b = tree) with
identical text and counts, so there are 12 distinct findings, none of them a side
difference. Every stream of every cell reads `movers=0 asymmetric=0`
(`sweep_variants.log`: 90 `movers=0 asymmetric=0` lines, 0 nonzero lines).
The self-checks PASSED. Final line: `VARIANTS: FAILED`, from the instrument's
pins, not identity.

Evidence lines (`sweep_variants.log`, cell | stream):

- MANIFEST, 16 lines = 8 pairs, the same 8 pairs slot23 printed (`worktrees/memfn-slot/slot23/sweep_variants.log:219-220,232-233,254-255,271-272,380-381,393-394,473-474,486-487`):
  - `plain/utf8` and `lowthr/utf8`, `emit-ir-auto` and `emit-ir-auto[-fno-prefilter-collapse]`: `b'(\\p{Xwd})' does not carry no-size-cap` (lines 219-220, 232-233, 477-478, 490-491)
  - `lowsize/byte` `emit-ir-auto`: `b'((a)+)+' does not carry no-size-cap`; `lowsize/byte` `stderr`: `... does not carry stderr-default` (254-255, 271-272)
  - `lowboth/byte` `emit-ir-auto` and `-fno-prefilter-collapse`: `b'((a)+)+' does not carry no-size-cap` (382-383, 395-396)
- TAG FLOOR, 8 lines = 4 pairs, NEW since slot23, still identical on both sides:
  - `lowsize/utf8` `emit-ir-auto` no-size-cap 289 < 290 (285-286); `stderr` stderr-default 356 < 357 (302-303)
  - `lowboth/utf8` `emit-ir-auto` no-size-cap 266 < 267 (413-414); `stderr` stderr-default 415 < 416 (430-431)

Classification (a).

- The 16 MANIFEST lines are a recorded, owed item of main. The comment above
  `VARIANT_PINS` in `scripts/emit_sweep.py` says: "MANIFESTS NOT re-measured:
  `(\p{Xwd})` and `((a)+)+` no longer carry their thin tags in slot22 and need a
  tree-measured --emit-pins run (OWED, see rlhbuild_report.md)". The report says the
  same (`docs/dev/lanes/rlhbuild_report.md` ~529-533). slot23 (R-16, green by
  its own judge) printed the same 16.
- The 8 TAG FLOOR lines are one count lower than the pins, on both sides. The
  floors (290/357, 267/416) are rlhbuild's 2026-10-11 re-pin to slot22's values, and
  slot23 (ref fdc2f2af) held them. The ref moved after that: main commits
  `fdc2f2af..a080c69a` that touch `src/` are `337f9a6ed`/`b553fb608` (seambuild,
  abi 75 -> 76: the seam helpers become `static inline`, so the emitted code
  shrinks slightly under the lowered caps) and `eed189975`/`eb2aad0dd`
  (CAND-PATH-READS, trace-build only). Seambuild is the likely cause: the
  lowered-cap tags (`no-size-cap`, `stderr-default`) are the size-sensitive ones
  and fall by exactly one. This attribution is an inference from commit content
  and the unchanged slot23 reading; it has not been bisected.
  `--variant lowsize --bases utf8` at `337f9a6ed^` vs `337f9a6ed` is the
  discriminator (about 150 s a rev, per the pin comment).
- R17-a (kit) is not in this: the kit's diff vs ref moves 0 artifacts on every
  stream, and the a-side (ref) counts equal the b-side.

Fix, owner main: one tree-measured pin refresh in `scripts/emit_sweep.py`, with a
single command:
`python3 scripts/emit_sweep.py --ref HEAD --tree-rev HEAD --variant all --no-variant-floor --no-self-check --trace --trace-order fallback=ordered --emit-pins pins.py`
(the header comment's own command) at the main tip. This re-measures the
manifests (the tallies already show the new thin-tag witness, e.g. `((ab)+c)+` for
lowsize/lowboth byte, in `build-emitsweep/slot24-variants/variant_tallies.tsv`) and the four tag floors.

Slot re-run: not needed for R17-a's verdict. Re-run `SWEEP variants` alone (441 s)
only if the judge wants a mechanically green line after the kit merges main's re-pin.

## 2. SWEEP utf8, rc=1, 4 floor/manifest lines

Zero movers on all streams (22 `movers=0 asymmetric=0`, 0 nonzero).

Evidence (`sweep_utf8.log`):

- 4 MANIFEST lines (75-76, 88-89): `b'(\\p{Xwd})' does not carry no-size-cap`, in `emit-ir-auto` and
  `emit-ir-auto[-fno-prefilter-collapse]`, a and b alike. Same stale thin-tag manifest as item 1
  (`plain/utf8` cell pins).
- A fifth failing line the judge's grep (`MANIFEST|FLOOR side`) does not count: line 98,
  `COMPOSITION PRODUCING FLOOR VIOLATION: 36 < 37`. Not a side difference: the
  ref-vs-ref self-check already reads `composition producing=36` (line 59), while the
  plain/start/simd/trace sweeps' self-checks read 37. `--extra '-e utf8'`
  composition produces one fewer artifact than the plain arm, on both sides.

Classification (a). The first four are item 1's stale manifest. The fifth is an
instrument property: `composition_producing_floor` (37, set at SL2,
`242aba6b7`, main) is the plain arm's number and is applied to every
full-population run, including `--extra` arms. slot12 and slot13 show the same
shape (utf8 reads 37 against a plain floor of 38, `slot12/sweep_utf8.log:94`,
`slot13/sweep_utf8.log:94`), so it recurs after each plain re-pin and has been
read as noise. It is not R17-a: the ref side prints the same 36.

Fix, owner main (`scripts/emit_sweep.py` near the `composition_producing_floor` check
at ~2755): either skip the composition floors when `run_extra` is non-empty, or key
the floor by base like `VARIANT_PINS` (utf8 = 36). Plus the item-1 manifest refresh.
Slot re-run: not needed; `SWEEP utf8` alone can be repeated after the re-pin.

## 3. N2 rc=4: floor_fail=1, floor_placeholder=1

`n2.log` / `n2_c6a3bfea/n2_results.md` section 7: would_decline=0, noend=0,
reason_stale=0, reach_dropped=0. The two floor items:

1. `arms | pf_walk | pcrec | chosen 478404 | floor 608765 | BELOW FLOOR`
2. `arms | precheck_assign_byte | pcrec | chosen 22320 | floor PLACEHOLDER`

`n2_census.sh:96` accepts `floor_fail=0,*reason_stale=0,reach_dropped=0`, so the
placeholder alone is tolerated (any `floor_placeholder=N`). The rc=4 comes from the pf_walk floor only.

### pf_walk (class b, by design, no byte moved)

What moved is the count of define-phase selections, not the sites. `ends` for the
null arm, slot22 (kit r15 `62261bc3`, before L1 and R17-a) vs slot24:

| | slot22 | slot24 |
|---|---|---|
| `arms define pf_walk` | 6986 | 3784 |
| `arms use pf_walk` | 6986 | 6988 |

Decomposition, exact on the data: 580 non-hat sites at define:use = 1:1, plus 3204 VM-hat
sites each defined once and used twice: `580 + 3204 = 3784` defines and
`580 + 2 x 3204 = 6988` uses. Cross-checks:

- `-fno-start-set` arm (no hat): define = use = 580 (the 580).
- `--engine=vm` arm: define 5986, use 11972 = exactly 2.000 x.
- `n2_census.sh`'s other rows keep their 1:1 define:use pairing; the pcrec-side
  `precheck_assign` / `precheck_assign_byte` exceed it (164/212, 176/245) from L1's
  second pre-check use, which is unrelated to pf_walk and does not trip a floor.

Cause: R17-a's `f2b16c801` ("define-then-use PF set sites and VM hat"). In `src/gen/emit_dfa.c` the
VM hat is defined once (`find_define`, stored in `job->mf_vmhat`) and used at both the entry and the
retry seek (`src/core/internal.h:6254`: "(`mf_vmhat`) for both seeks"), where it used to be two
`mf_emit` calls each doing a define. The emitted text is the same (a walk row's define writes no
text of its own), which is why every sweep reads 0 movers. The floor counts "selections (define +
run phases)" (`row_floors.tsv` header), so one define where there were two lowers
it by the hat count. `r17a_report.md` section 8 item 5 listed this census as OWED ("REACH lines can
gain cells"). The floor itself (608765) is 0.9 x slot7/8's 676406, older than every slot since.
What cannot be told from artifacts alone: whether L1 (`rlhbuild`, abi 75) also shifts the
pf_walk total, because no N2 census exists between slot22 and slot24 (slot23 ran none). It
cannot change the diagnosis (the 2:1 decomposition is R17-a's), and the amount is now
measured.

Fix, owner kit (`tests/memfn/row_floors.tsv` on lane/memfn-r17, same commit as the cause):
set `arms pf_walk` pcrec_floor to `430563` (the report's floor(0.9 x 478404)), naming this
decomposition in the commit message. The report's `floor_fail` line is then re-read with
`python3 docs/design/memfn/probes/rowcon/n2_report.py worktrees/memfn-slot/slot24/n2_c6a3bfea --floors tests/memfn/row_floors.tsv`
against the existing slot24 output (seconds). No N2 re-run is needed.

### precheck_assign_byte placeholder (class a)

Pre-existing and legal: R-15's row became `reach pcrec` with L1 (rlhbuild, abi 75); its
floor was left PLACEHOLDER "until the full N2 census reads it" (row_floors.tsv header,
`rlhbuild_report.md:527`). slot24 is the first census that reads it: 22320 chosen, so
floor(0.9 x) = `20088`. Fill it in the same kit commit (the report column "floor(0.9 x chosen)").

Slot re-run: none.

## 4. `*** [Makefile:1515: test-spec-history] Error 1`

The only `*** [... test-` line in `make_test.log` (6988); `perfrun`: `section-errors=1 class=RED-REAL red
sections: test-spec-history`. Makefile `test-spec-history:` (line 1513) runs
`bash tests/spec_history/run_spec_history.sh` -> `tests/spec_history/spec_history.py`
(+ `spec_cites.py`). It reads text only.

Failing line (log 6842; reproduced by the light re-run, 144 passed / 1 failed, rc=1):

    FAIL: [cites] match_api: line-number citation(s) -- cite the section number (match_api.md §N¶K), never a line: docs/dev/reviews/2026-10-12-r1-match-split-pinonly.md:78

Line 78 of that file reads "... RX_DFA_START reverse-pass understates (sentence in ¶11, xref
match_api.md (line 1770)) ...". The file came in with main `d8fbbb540` (2026-10-12, "review: D6 panel r1 on
the [MATCH-SPLIT] 4a note"), which is inside the ref a080c69a (`git show a080c69a:<file>` line 78 carries
`xref match_api.md (line 1770)`) and unchanged at the main tip (`3a5b3e269`, same text). R17-a's
diff vs the ref touches nothing under `docs/dev/reviews/` or `docs/spec/`. Class (a): the check is
red on main as of that merge, and nothing in the review chain ran it.

Main's green at 35c0b923 (from team-lead): `35c0b9231` IS an ancestor of the ref
a080c69a, but it does not contradict this. It is dated 2026-10-12 06:47 and its tree does
not contain the review file (`git ls-tree -r 35c0b9231` has no `r1-match-split-pinonly`);
`d8fbbb540` added the file at 09:36, about three hours later, and is also an ancestor of
a080c69a (`merge-base --is-ancestor d8fbbb540 35c0b9231` is false). So main was green
before the offending line existed, and the red appears on main at `d8fbbb540` with no R17-a
or merge-of-main involvement. Not verified by a run at `d8fbbb540` itself; the evidence is
the file's presence and text at the ref and at main's tip. Main's tip and its docs-only
commits (6b2dbd3e+) still carry the line unless main has since reworded it.

Fix, owner main: reword `docs/dev/reviews/2026-10-12-r1-match-split-pinonly.md:78` to cite the section
number ("match_api.md §N¶K" of the sentence in question) instead of `match_api.md (line 1770)`; this is
the failure mode `specnum_report.md` / `spectri_report.md` already fixed once for a report quoting a
citation form. Slot re-run: none; `make test-spec-history` (3 s) after the kit merges main's fix.

## 5. mech: 67 rows COMPLETE, undetected: 1

`mech.log:215`: `== mech run COMPLETE: 67 rows (unexpected: 0, undetected: 1, unreached: 0, anomalies: 0,
oracle-skipped: 0)`. The one row (log 86 / 156):

    S284-run-rows-reseeds-false   src/gen/emit_dfa.c   ...   UNDETECTED (EXPECTED -- see this row's SAB_DOC_FIGURE for what would close it)

`tests/mech/sabotages/S284_run_rows_reseeds_false.sh` declares `SAB_EXPECT=UNDETECTED` (line 34) and
carries its measured figure (s1build, 2026-09-25: the plant moves 0 artifacts over 151 corpus + 94 bench
run-row artifact-configs and 21 constructed witnesses; "WHY IT SHIPS UNDETECTED (EXPECTED), on S219's
precedent"). Its last edits were stc3 (`ba1ca7582`) and ssbuild01 (`12b43eb22`), long before R17-a. It is in
`mech_rows.txt` only because the lane's derived row list includes every row anchored in
`src/gen/emit_dfa.c`.

It is not an R17-a row and nothing about R17-a should have made it detectable. R17-a's own rows all
read DETECTED: S846 (`memfnarms:2fail/381pass`), S847, S848, S849 (1 fail each), plus S478 and the kit
rows S526 S619 S681 S682 S722 S803. The brief's judge says "none undetected"; the right reading is
`unexpected: 0` and `unreached: 0`, which hold. Fix: none for the code; the judge wording (in `run.sh`
comments / future slot scripts) should say "none UNEXPECTED". Slot re-run: none.

## Other judges, for the record

- Identity sweeps: plain, start, simd, trace, utf8 and all variant cells: 0 movers, 0 asymmetric at full reach.
- G2 quick and full: 0 failed (52,987,686 and 199,850,927 checks passed).
- `make`, `make strict`, SABANCHOR: rc 0.
- `make test`: one red section (item 4); the other sections are green.

## Bottom line

R17-a is still a zero-mover: every artifact sweep, at every variant, base and extra arm, reads 0 movers and
0 asymmetric at full reach, G2 reads 0 failed, and R17-a's own sabotage rows are DETECTED. All five reds
are explained without a byte move. Three are main's: stale pins in `scripts/emit_sweep.py`
(the 16 owed thin-tag manifests, four tag floors one count low since seambuild's abi 76, and a
plain-arm composition floor applied to the utf8 arm) and one review file that cites a line number
(`test-spec-history`). One is a declared-UNDETECTED row (S284) that predates the lane. One is the kit's:
the N2 `pf_walk` floor, which fell because the VM hat is now defined once and used twice, a
selection-count change the lane's own report listed as owed, and the unfilled `precheck_assign_byte`
placeholder; both are settled by amending `tests/memfn/row_floors.tsv` (430563 and 20088) and re-reading
the existing N2 output. No stage of slot24 needs a re-run for R17-a's verdict; the variants and utf8
sweeps and `test-spec-history` can be repeated alone after main's fixes are merged into the kit branch if a
mechanically green slot line is wanted.
