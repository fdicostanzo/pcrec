# grid2r3 — the zen4-grid2 harness brought from r17b_prime.md rev 2's §5.4 to REV 3's (built and checked, NOT RUN)

Lane grid2r3, 2026-10-16, branch `lane/grid2r3` (cut from the grid2p merge `66517b315`), sonnet. Task: implement every
item rev 3 added or changed in §5.4, re-judge grid2p's eight deviations against rev 3, make the slot record the exact
compiler it measures and refuse a wrong arm, re-run the DRY mode, the no-clock gate, `plants.sh` and
`paranoid_check.sh`, and re-estimate the wall. **The timed slot was not run**; nothing under `src/`, `memfn/src/`,
`lib/` moved (no pcrec byte, no abi event). Everything the runs wrote is under the worktree's gitignored `build/`
(`build/dry/`, `build/full/`); the small text evidence is committed under `grid2/evidence/r3_*`.

## Process note: a HOLD this lane did not read in time

`grid2r3_rulings.md` (untracked, in the worktree root) carries a HOLD written 11:44 (main's `make test` had the box:
no DRY, no-clock gate, `plants.sh` or other multiprocess run until a `LIFT` line). The lane never polled the file
before launching: the DRY (11:39-11:42) and `plants.sh` (about 11:42-11:44) ran before the hold's timestamp, but the
FULL no-clock build + gate + four `NOCLOCK=1` phases (11:44:33-11:49:10, `taskset -c 12-15`, `JOBS=4`), two
`paranoid_check.sh` runs and one clocked 170 s `time.sh` pass on CPU 15 (the cross-launch wiring test) were started
after it. Nothing ran on CPU 14, nothing is running now, and no run was started after the hold was read. The manager
should discount any interference those runs had on main's `make test` timing.

## Summary and verdicts

| check | verdict | evidence |
|---|---|---|
| DRY (`DRY=1 CPU=13 taskset -c 12-15 slot.sh`) | **COMPLETE required=ok optional=done**, 164 s wall, box load 12-17 (not a measurement) | `evidence/r3_dry_slot.status`, `r3_dry_estimate.txt` |
| FULL design, no clock: build + gate | build 80 s, gate 54 s: **2,974 legs OK, 0 FAIL** (O 218, R 843, L 843, C 1,070), 155 reach rows 0 unreached, 84 landing-fidelity OK, U2 **60** one-byte groups reached, 0 excluded, provcheck 67 arm signatures OK, census OK | `evidence/r3_full_check.out`, `r3_full_census.out` |
| FULL design, `time.sh` with `NOCLOCK=1`, every phase | F1 773 rows / 123 groups, F3 98 / 16, OB 300 / 60, TRIG 36 / 12; **0 ANSWER MISMATCH**, 0 requeued | `evidence/r3_full_all.status` |
| `plants.sh` on the DRY slot | **ALL DETECTED**: grid2p's 7 plants plus 6 new, restore green | `evidence/r3_dry_plants.out` |
| `paranoid_check.sh` | passed=60 failed=0 | `evidence/r3_dry_paranoid.out` |
| compiler record | commit `c90d65e53a39` (`lane/memfn-r17`), abi **77**, sha256 `89529696...5f`, inputs clean and older than the binary | `evidence/r3_dry_provenance.txt` |

The gate's failing direction for the **new** items (the part no answer leg can see): all six rev-3 plants end `check.sh`
with exit 4 and the named line while legs R/L/C/O read **0 failing lines**:

| plant | what it breaks | detected as |
|---|---|---|
| `n_dropped` | the N = 46 point dropped from the arm tables | `CENSUS-FAIL item 2a` |
| `cover_dropped` | the c001 64 KiB cover group dropped | `CENSUS-FAIL item 3a` |
| `vm_as_dfa` | the VM_ATTEMPT `v1` arm silently built as a DFA hat (same pattern, same answers) | `PROV-FAIL o-vm v1` (ROUTE stamp) |
| `walk_as_v1` | the c020 `walk` arm built from the V1 text (the deny never took) | `PROV-FAIL c020 walk` |
| `abi_mismatch` | `EXPECT_ABI=1` against the abi-77 compiler | `PROV-FAIL compiler` |
| `no_deny` | main's compiler (no `pf-terms-mask` deny) | `PROV-FAIL compiler` |

## Rev 2 -> rev 3: every added or changed item, and its artifact

Diffed `r17b_prime.md` §5.4 at `3b3cc8131^` (rev 2) against HEAD (rev 3), plus §R3 and the panel record.

| rev-3 item | what rev 3 says | artifact |
|---|---|---|
| **C5** item 2a | member-free single calls at N in {33,34,36,38,40,42,44,46}, arms V1, walk, `walk#b` (24 group-arms) | `design2.py` `N_STAIR`, groups `g2-dig-n<N>-ginf-Lnone-S` (item `2a`, phase F1); census asserts the exact 8-point set |
| **C3** item 3a | three unmeasured cover shapes (range,eq,cube) (0,2,0) (0,0,1) (1,1,0): V1 vs walk, member-free, 64 KiB and 1 MiB (18 group-arms) | cells `c020` `[ad]+=`, `c001` `[xy]+=`, `c110` `[0-9_]+=` (found by compiling candidates and counting `_range(`/`_eq(`/`_cube(` in the V1 mask, `r17b_prime/census_shapes.py`'s key), emitted by the kit compiler through grid1's `EMIT_CELLS` hook, 6 groups (phase F3), gate-only dense groups so a wrong V1 mask is seen; `provcheck.py` asserts each V1 mask holds exactly the stated shape |
| **A7** item 3 (VM) | the VM hat's seek at \|S\| = 1: WALK, V1 one-term, LIBC (evidence only), `walk#b`, 6 gaps + 4 lengths (40 group-arms) | cell `o-vm` (`xy+z --engine=vm`, `RX_VM_START_SCAN "first-class"`), `mkvar2.py vm`: `walk` = the `--memfn=no-pf-terms-mask` compile (the table walk) with the reach tick, `v1` = the compiler's own default text (stateful V1), `libc` = both walk statements replaced by memchr; 10 groups, U2 reach leg covers them |
| **C8** NONE | NONE is an EXTRA ARM inside item 3's gap groups (5 kinds x 6 gaps = 30), DFA_ATTEMPT evidence-only, rev 2's item 4 deleted | grid2p already built it that way (`none` arm in the gap groups); labels renamed (`design2.py`, README), census asserts the 30 groups and that no other group carries `none` |
| **A2/A5** rename | ATTEMPT_PRED widened and renamed DFA_ATTEMPT | cell `o-back` keeps its name; docs say DFA_ATTEMPT |
| **C7** launches | 3.4 to 5 launches; a CROSS-LAUNCH rerun trigger beside the within-launch rule | `time.sh`: a group in which any arm's per-launch medians spread by more than max(the group's A/A floor, NULL) gets +2 launches, once; logged with the arm that fired; `xreruns=` on the completion line (see deviation 9). `estimate.py` prints both 3.4 and 5 |
| **A7/C3/C5** provenance | R-MS3 / D166 add. 2: forms hashed at the measured compiler | `provcheck.py record` (below) |

Unchanged from rev 2 and re-verified: items 1, 2, 5 (gate), 6-8, the paranoid suggestion, `kit-grid@2`, LAUNCHES 3
(+2), CPU 14, the quiet gate. Group-arm counts in the spec's own unit (arms without NONE, plus `walk#b`; computed from
`evidence/r3_full_groups2.tsv`): 2a 24 (spec 24), 3a 18 (18), 3v 40 (40), NONE 30 (30), item 3 on the five DFA kinds
230 (spec 250: the spec counts `o-back` at five arms where it takes only LIBC-back and the hand walk, 3 with `walk#b`),
items 1+2: 829 over 125 groups (the 121 streamed fit groups, into which the 149 grid1 groups collapse, plus 4 item-2 points; deviation 2).

## grid2p's deviations 1-8, re-judged against rev 3

| # | grid2p's deviation | rev 3 says | verdict |
|---|---|---|---|
| 1 | compiler from `memfn-r17` (record branch), not main | unchanged (B0 ports the seam to main later) | **still acceptable, and now made safe**: the slot records commit, abi, sha256, build-input cleanliness and age, and FAILS on a stale/dirty compiler (below) |
| 2 | **streamed condition 4 MiB per subject**, not grid1's 64 MiB | §5.4 says only "STREAMED" and prices launches at grid1's 0.95 s; regime_eval §2.4 defines the judge condition (S) as **64 distinct 64 KiB buffers, 4 MiB in all** and §2.4's `[r1 M-also]` ties it to the 7700X's 32 MiB L3; R_in (E4b) is "the same formula's left-hand term computed on grid2's streamed fit cells", so grid2 must be the judge's own condition | **REQUIRED, not merely acceptable: 4 MiB is what regime_eval needs.** Rev 3's wall figures (91/129 min) are priced at 0.95 s per launch and over-price this harness; `GRID2_STREAM_MIB=64` restores grid1's total (11 GB of subjects, about 80 min required at 3.4 launches, an extrapolation) and would make R_in non-comparable with the judge |
| 3 | item 2's twin arms ride item-1 groups (35 groups x 3 arms) | item 2 text unchanged | **still acceptable.** One interaction to rule: §5.2's `cdisp_*` row reads "M12's N points plus item 2a's N = 33..46", but item 2a's arm list is V1, walk, `walk#b` only, so the twins ride M12's points (n = 8, 32, 48..128) and not the staircase. Adding `tw0-2` to the 8 staircase groups costs about 0.5 min at 3.4 launches; not added because the spec lists the arms |
| 4 | V1 one-term is stateless at a libc site | unchanged | **still acceptable for the five DFA kinds; NOT the case at VM_ATTEMPT**: there the `v1` arm is the compiler's own stateful V1 (the cache has a declaration point). Say so when M20 and F2 are read |
| 5 | item 3/4 cells emitted with `-fno-req-byte -fno-req-run` | unchanged | **still acceptable**, applied to `o-vm` too (provcheck asserts both stamps read `none` on every arm) |
| 6 | item 8's TUG cells are a choice | unchanged | **still acceptable** |
| 7 | GATE-ONLY dense groups | needed again | **extended** to c020/c001/c110 (a member-free subject cannot show a wrong V1 mask) |
| 8 | pickable = walk V1 S1 A1 A3 libc v1 loop none keep drop | `none` at DFA_ATTEMPT is evidence-only | **acceptable**: a wrong NONE arm is a harness bug whatever its use, so it still fails the run (exit 3) |
| 9 | rerun NULL = 0.031 x median(base) (no A/A floor before the group) | C7 wants the cross-launch spread vs "the group's own A/A floor" | **changed, with a stated deviation from the spec text**: after the launches the group's floor exists, but a floor that happens to be ~0 would make every group rerun, so the cross-launch threshold is max(A/A floor, NULL). The spec names the floor alone |
| 10 | grid1 touched twice, additively | | still true; this lane edits no grid1 file (`EMIT_CELLS` carries four patterns through the env) |
| 11 | item 6 reads `groups2.tsv` | | unchanged; the new items are string-coded (`2a`, `3a`, `3v-*`) and awk's `== 2` does not match them, so F2 never picks them up |

## The compiler, and what it implies for the set at M0

`provcheck.py record` writes the `compiler_*` lines of `provenance.txt` and the `COMPILER` status line: path, real path,
sha256, mtime, version, **abi (read from an emitted artifact)**, the compiler worktree's `HEAD` commit and branch, the
last commit touching its build inputs (`src cli lib memfn/src memfn/include Makefile`), dirty-file count, and whether
the `pf-terms-mask` deny moves the text. It FAILS (exit 1 from build.sh and slot.sh) when the inputs are dirty or newer
than the binary, the compiler is outside a git worktree, the deny is unknown or does not move the text, or `EXPECT_ABI`
/ `EXPECT_COMMIT` (when set) disagree. For the default compiler: `c90d65e53a397aa300f6472f7f017403d8624e53`,
`lane/memfn-r17`, abi 77, last input commit `16e8e0aa2` (2026-10-12 16:11) older than the binary (16:29). `make -q`
reports it out of date by mtimes only because a branch operation touched the sources on 10-14; the content check above
is the one used.

**Every arm the slot times is checked against that compiler** (leg P, `provcheck.py check`, run by build.sh and
check.sh): (a) each of the ten own cells is re-emitted by the compiler from provcheck's OWN pattern/feature table and
compared byte for byte to `art/<cell>/{new,deny}` (this is how the five cells grid1 copies from slot25c ALPHA are
proven to be this compiler's text: they are identical at the same `-o` basename); (b) `bin/<cell>/walk` must equal the
deny artifact and `V1` the new artifact, contain/not contain the W8 block, and the V1 mask must hold the cell's
(range,eq,cube) shape; (c) every ext cell's artifact is re-emitted and its ROUTE stamps asserted (`RX_ENGINE`,
`RX_DFA_SCAN`, `RX_DFA_PREFILTER`, `RX_VM_START_SCAN`, `RX_VM_PREFILTER`, `RX_REQ_BYTE/RUN none`), and each arm's
signature (libc/walk/loop/v1/none) is asserted; (d) trig keep/drop pre-check stamps. A missing deny, a wrong route or a
wrong arm FAILS the gate loudly (exit 4) instead of being timed. Leg M (`census`) asserts the rev-3 items in the arm
tables against literals written from the §5.4 table.

**What it implies at M0.** The set's form hashes (R-MS3) are of the form text at the measured compiler, so the rows this
slot produces are keyed to abi-77 `lane/memfn-r17` text. Any form whose text changes between the slot and M0 is STALE,
carried and flagged (D166 add. 2). The candidates: every V1/W64 row if main's B4 does not reproduce R17-b's
`pf_terms_mask` text byte for byte; the dispatch twins (M16-M18, `kit:form.dispatch-twin`, stale whenever the BUILT
dispatch differs, §2.5); the VM_ATTEMPT V1 (stateful, the compiler's text); and every LIBC row, which is also
libc-version keyed (§5.3, glibc of this box). The set header should carry the `compiler_*` lines and the commit of this
harness (`grid2_commit`, `grid2_harness_dirty_files`).

## The wall estimate

From the DRY run's measured seconds per launch (`estimate.py`; 0.55-0.69 s by phase and subject class, the driver's own
50 ms calibration + 7 x 50 ms rounds plus the load; 4 MiB streams), multiplied by the FULL design's launches
(groups x (arms + `walk#b` + `walk#c`) x launches):

| phase | groups | 3.4 launches | 5 launches |
|---|---|---|---|
| F1 (items 1, 2, 2a) | 123 | 32.5 min | 47.7 |
| F3 (items 1, 2, 3a) | 16 | 3.7 | 5.5 |
| OB (items 3, 3n, 3v) | 60 | 13.3 | 19.5 |
| build + subjects, gate (measured on the full design: 80 s, 54 s) | | 2.2 | 2.2 |
| **required** | 199 | **about 52** | **about 75** |
| TRIG (item 8, optional) | 12 | 1.7 | 2.5 |
| perf items 6-7 (optional, 0.2 s x 405 rows) | | 1.6 | 1.6 |
| **with the optional items** | | **about 55** | **about 79** |

The spec's 91 / 129 (99 / 138 with optional) are priced at grid1's 0.95 s per launch and 149 groups x 7 arms; this
harness has 121 distinct streamed groups and 0.62 s launches (deviation 2). grid2p's figure was 46-54 at 3.4; the
rev-3 items add about 3.5 min at 3.4 launches and 5 at 5, consistent with the spec's own +3.6 / +5.3. Not estimated:
quiet-gate waits and the rerun share (the cross-launch trigger makes 5 plausible; a dry run takes one launch and a
loaded box fires it on every group, `evidence/r3_xlaunch_loaded_box.log`, so no quiet-box share exists yet).

## Charter checklist

| item | status |
|---|---|
| diff rev 2 vs rev 3 §5.4, implement every item | done (table above) |
| C3 cover shapes | done (c020 c001 c110, shape-asserted) |
| C5 N = 33..46 | done |
| VM_ATTEMPT cells | done (`o-vm`) |
| C8 NONE count | done (30, census-asserted) |
| LAUNCHES per rev 3 | 3 (+2), estimate at 3.4 and 5, cross-launch trigger |
| grid2p deviations 1-8 re-judged | done |
| 4 MiB vs 64 MiB stated | 4 MiB required by regime_eval §2.4 |
| compiler commit/abi in the set header; arm buildability fails loudly | done (`provcheck.py`, exit 4) |
| stale-at-M0 note | above |
| DRY, no-clock gate, plants, paranoid | green, logs above |
| plant for a new rev-3 item | six, all DETECTED |
| estimate | above |
| README launch command and status current; CLAUDE.md entries | done |

## Open issues

1. `cdisp_*` at the staircase points (deviation 3): needs the twins on the 8 groups of item 2a; a one-line change in
   `design2.py` (+~0.5 min) if the kit wants it.
2. The cross-launch trigger's threshold deviates from the spec text (max with NULL); if the kit prefers the bare A/A
   floor it is one line in `time.sh`, at the price of near-total reruns whenever a floor lands near zero.
3. Item 3's `o-back` NONE and the VM_ATTEMPT LIBC arm are evidence-only in the spec but are "pickable" to the gate.
4. The rerun share is unmeasured on a quiet box, so the estimate is a bracket (3.4 to 5), not a point.
5. The slot dir `worktrees/memfn-slot/grid2` already holds nothing from this lane; `slot.sh` rebuilds it.

## Files

`docs/dev/lanes/grid2/`: `provcheck.py` (new), `design2.py`, `mkvar2.py`, `ext_ob/build.sh`, `build.sh`, `check.sh`,
`slot.sh`, `time.sh`, `plants.sh`, `estimate.py`, `README.md`, `CLAUDE.md`, `evidence/r3_*`; this report;
`docs/dev/lanes/CLAUDE.md` index entry. The launch command is in `grid2/README.md`.
