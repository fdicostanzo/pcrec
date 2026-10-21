# b4prep report: B4's pre-brief OWED items (r17b_prime §3.1a, rev 4.1)

Lane b4prep, 2026-10-21, worktree `worktrees/b4prep`, branch `lane/memfn-b4prep` (cut from `lane/memfn-r26` @ 5d1afca69).
Measurement and record only; no kit code changed. Artifacts are under `docs/design/memfn/r17b_prime/b4prep/` (own CLAUDE.md).
RULINGS FILE `b4prep_rulings.md`: re-read before the report, "None yet" (no entry applied).

**FINDINGS UP FRONT.** (1) No sign change to report: the F3 re-time (item 1) has NOT run, so its values stay PROVISIONAL.
(2) Item 2 refutes grid2read §9's attribution: the V1 text, the walk text, their object code and the driver are
byte-identical in grid1 and grid2 on all six shared cells, so a V1-text difference cannot explain M9 not reproducing.
(3) Item 5 found a gap between §9.2a's rule and its own known-cells list: dfa-hat L = 32 at g >= 16 (unpredictable
landings) loses 8.5-13.3% and dig L = 32 g = 16 loses 2.6%, and the rule lists neither (main's ruling owed).

## Item 1: the quiet F3 re-time. OWED (queued, not yet run)

- Job: `520-kit-b4prep-f3rr` (kit band, cap 900, expect `groups=4 last=^time.sh: COMPLETE rows=[0-9]+ groups=`), script copy
  `docs/design/memfn/r17b_prime/b4prep/jobs/520-kit-b4prep-f3rr`. It runs grid2read §8 item 1's command verbatim
  (`OUT=<slot> PHASE=F3 CELLS_RE='^f3-(word-eq|quad)$' RAW_TAG=F3rr PASS_STATUS=<slot>/time_F3rr.status CPU=14 LAUNCHES=3`)
  with `time.sh` from `lane/grid2r3`'s worktree (read, not edited) in slot `worktrees/memfn-slot/grid2`. `--estimate` says 4
  groups, about 1.4 min plus quiet-gate waits.
- Queue state at hand-off (10:2x): ENQUEUED and `ready`, behind another lane's direct box lock (`x0oracle-*`) and
  `200-reachonly-reach`; it had not started. Status file when it runs: `worktrees/memfn-slot/grid2/time_F3rr.status`; raw rows:
  `worktrees/memfn-slot/grid2/time/raw_F3rr.tsv`; log: the queue run dir (`scripts/boxqueue status`, `scripts/verdict`).
- To close it (a fresh agent): (a) `scripts/boxqueue state kit-b4prep-f3rr` green; (b) copy `time/raw_F3rr.tsv` to
  `r17b_prime/b4prep/raw_F3rr.tsv`; (c) write `r17b_prime/b4prep/f3rr.md` with the re-timed word-eq (2,0,1) and quad (3,1,0) values
  beside grid2read's, each marked MEASURED if the cells are no longer LOAD-SUSPECT and the group's A/A holds, else
  PROVISIONAL; expected per grid2read §8: word-eq A1 beta ~0.019-0.021, quad V1/S1/A1 unchanged; (d) a sign change (V1 vs walk:
  word-eq -13%, quad -41%) is a FINDING, stated at the top; (e) mark item 1 CLOSED in §3.1a.
- Nothing about item 1's values is known; they remain PROVISIONAL (keys.tsv unedited, SHA256SUMS untouched).

## Item 2: the V1 attribution. CLOSED (`b4prep/v1attr.md`, `v1attr.sh`, `v1attr.tsv`)

- grid1's V1 arm and grid2's are `bin/<cell>/V1/art.c` in the two slots. On dig, bounded, dfa-hat, hex-run, word-eq and quad
  (the six shared cells): V1 and walk `art.c` byte-identical (12 of 12 files), `art/{new,deny}` byte-identical (12 of 12),
  disassembly of `V1/art.o`, `V1/gdrv.o`, `walk/art.o`, `walk/gdrv.o` identical (24 of 24), `lib/gdrv.c` identical.
- So the compiler's V1 text does not differ from grid1's V1 arm on grid2's member-free cells (dig carries them). grid2read §9's
  sentence is not supported. At the N both slots share, the sign agrees (n = 48: -4.56 vs -4.98 ns; 64: -5.75 vs -7.25; 128:
  -14.16 vs -13.54). grid1's dig first-mode cells exist only at n >= 48; the 36 B crossover and M12's +2.3/+0.6 ns at N = 8/32
  are not in grid1's time files, so they are an interpolation or a model, not a V1 text effect (INTERPRETATION, mine: the
  27 ns bracket of rev 3 C5 plus the harness change, A14).

## Item 3: main's walk against the slot's walk. CLOSED (`b4prep/walkcmp.md`, `walkcmp.sh`, `walkcmp.tsv`)

- Tree: this worktree's `build/pcrec` (`make -j4`, main plus kit docs, abi 81); ten compiler-emitted grid2 cells.
- Result: the slot's `walk` arm is byte-identical to the deny artifact on 10 of 10; against main's default emission the only
  differences, on every cell, are `.abi = 81` vs `77` (and its comment) and one added line `#define RX_COMPOUND "none"`, a stamp
  macro nothing in the file reads. The table walk and every executable line are the same bytes. `art.h` differs only in the
  abi value. B4's G1 can read the slot's walk as main's. Not compared: the `o-*` cells' mkvar2-built walks (not B4's baseline).

## Item 4: B4's predicted-mover manifest, regenerated. OWED (path built and proven; the sweep is queued)

- Path (said as asked): a TEST-BUILD LEVER SET, not the converter (E14 does not exist). `mk_lever_set.py` builds
  `b4prep/b4prep-v1max2.tsv` through the writer of `memfn/data/sets/generate.py` (imported, not edited), from grid2read's
  `keys.tsv` (read only). It spells rev 4.1's rule as data for B1's unchanged finder shadow: a `kit.saving.V1.WALK.<shape>` row
  above the floor for every shape of at most 2 terms (range + eq + cube; values from keys.tsv where timed, else 0.5, labelled
  PLACEHOLDER for r0e0c2, r0e1c0, r1e0c1, only the sign against eps is read), no row for any shape of 3 or more terms (R7 does not
  hold, R7w decides: the walk), no `r2` row (R0 does not hold: retired), `kit.eps.streamed.slope` from keys.tsv. No kit code change
  was needed; the set's header metadata (run/box/code_commit) is generate.py's scratch boilerplate and describes nothing.
- Proven on samples: the traced harness (`fdb1/mk_trace_harness.sh`, built in this worktree) under the lever set picks `[0-9]+x`
  (1,0,0) V1, `[a-f0-9]+` (2,0,0) V1, `[ad]+=` (0,2,0) V1, and WALK for `[A-Za-z_]+=` (2,0,1), `[0-9A-Fa-f_]+=` (3,1,0), `\w+=` (3,0,1);
  a one-member `x[a-z]+y` gets D1 LIBC as before.
- Job: `521-kit-b4prep-manifest` (cap 1800, expect none; about 9.2k compiles at `--jobs 4`, heavy by the SWEEP CAP so it was queued
  rather than run). It writes `b4prep/predicted_movers_B4_rev41.tsv`; `fdb2/predicted_movers_B4.tsv` (860 movers) is untouched. Queue
  state at hand-off: ready, behind the same holders as item 1.
- To close it: when the job is green, `python3 -I b4prep/summarize_manifest.py b4prep/predicted_movers_B4_rev41.tsv
  fdb2/predicted_movers_B4.tsv grid2read/keys.tsv > b4prep/manifest_summary.txt`. It prints movers by (arm, shape, row, pick), the
  new-vs-old movers by ID, a rule check (any site whose pick disagrees with "V1 iff terms <= 2" must be zero), and the split of the
  sites on shapes with no keys.tsv key between V1 and WALK by arm and term count. The old manifest gives a baseline for the same
  script (412 unkeyed-shape sites over both arms; the "54" of §3.5 are byte-arm sites among 620 candidate movers, a different
  denominator, so the summary reports both). If the rule check is not zero, that is a finding.
- Not known yet: the new mover count by group and the V1/walk split of the 54 no-key sites.

## Item 5: §9.2a's expected-loss list. CLOSED as far as the kit can (`b4prep/expected_losses.md`)

- Pre-registered (committed before any B4 timing): EL1-EL10 (B4): dig g = 2 at L = 32/1k/64k (+21.8/+15.3/+14.9%), dig g = 8 `reg`
  L = 1k (+34.9%), dfa-hat g = 2 at L = 32/1k/64k (+41.3/+44.8/+45.7%), bounded g = 2 at L = 32/1k/64k (+21.4/+17.9/+17.8%); EL11 (B5):
  VM hat |S| = 1, g = 2, +38.3%. Each carries its 2x line (the FINDING threshold).
- Relay question to pcrec-bench: drafted in section 4 of that file; main sends it, the lane wrote nothing to pcrec-bench.
- FINDING for main: §9.2a's rule (regular, gap <= 8) does not select the cells its own known-cells list names (dfa-hat L = 32; bounded's
  ~64 B crossing). Measured unlisted losses already in grid2: dfa-hat L = 32 at g = 2 and g >= 16 (+8.5..+13.3% at g >= 16, unpredictable
  landings), dig L = 32 g = 16 +2.6%. Under §9.4 they would refute B4 unless main widens the rule or accepts them; the kit did not edit the rule.
- Owed: the bench's cells (relay, owner main), counter readings on B4's G1 cells (owner B4's acceptance lane), main's ruling on that gap.

## Charter vs committed

| item | artifact | state |
|---|---|---|
| 1 F3 re-time | job `520-kit-b4prep-f3rr`; status `memfn-slot/grid2/time_F3rr.status`; closing recipe above | OWED; owner: the next lane / main; trigger: job green |
| 2 V1 attribution | `b4prep/v1attr.md`, `.sh`, `.tsv` | CLOSED |
| 3 walk compare | `b4prep/walkcmp.md`, `.sh`, `.tsv` | CLOSED |
| 4 mover manifest | `b4prep/mk_lever_set.py`, `b4prep-v1max2.tsv`, `summarize_manifest.py`; job `521-kit-b4prep-manifest` | path proven; sweep OWED; owner: next lane; trigger: job green |
| 5 expected losses | `b4prep/expected_losses.md` | CLOSED except the bench's cells (main's relay) and the 3b ruling (main) |
| §3.1a edit | `[b4prep]` tags on items 1-5 only | done; items 1 and 4 say OWED/QUEUED, 2, 3, 5 CLOSED |

Resource use: `make -j4` once (about 10 s), a few dozen compiles; no make test, no sanitizer, no timed run; only the two queued
jobs are heavy. Scratch under this worktree's `build/` (gitignored); nothing written outside the worktree except by the queue's own run dirs.

## Closing (lane b4close)

2026-10-21. Rulings file `b4prep_rulings.md`: all three entries applied (the short-subject class, the I-156 note, the POSCOST count).

**Item 1: CLOSED, no sign changed.** `b4prep/f3rr.md`, `raw_F3rr.tsv`. Re-timed V1 vs walk: word-eq (2,0,1) -13.71% (was -13.27%),
quad (3,1,0) -41.26% (was -41.26%); S1/A1 betas within 1.7% of grid2read's (quad S1 0.2816 vs 0.2864 ratio). All values MEASURED (no
LOAD-SUSPECT cell, A/A held in all 4 groups). word-eq A1 beta now exists: 0.019163 ns/B. keys.tsv and SHA256SUMS untouched.

**Item 4: CLOSED. The 9 s wall is real, not a short sweep (K35 check).** The job's header says population 4636 distinct patterns x 2 arms
= 9272 compiles (the ~9.2k sizing) and 2374 set sites. Checked from the output: 2374 data rows = 2374 sites; every one of fdb2's 2369
old sites is present with identical members and shape (0 lost, 5 new; the corpus grew 4624 -> 4636 patterns); 1457 distinct patterns carry
a site in both. Compiles are ~1 ms each (the harness compiles to stdout; 4 jobs), so 9 s is consistent. A residual gap: `shadow_census.py manifest`
ignores a compile's return code (`rc` is returned but unread), so a failed compile would silently drop a pattern; the old-site cross-check above
is the evidence none did.
- Movers: 1766 (arm, pattern) = byte 658 + byte-vm 1108 (fdb2: 860 = 320 + 540). By the ID (arm, pattern): all 860 old movers are movers
  again (only-OLD 0); 906 are new (byte 338, byte-vm 568). By group, the new V1 sites per shape: r1e0c0 780 (unchanged), r0e2c0 330, r0e0c1 259,
  r0e1c0 159, r1e1c0 124, r2e0c0 43, r0e1c1 40, r1e0c1 19, r0e0c2 15 (counts are sites, all arms; full table in `manifest_summary.txt`).
- Of those, the shapes with no saving key in keys.tsv that now route to V1 are r0e1c0 (159 sites), r1e0c1 (19), r0e0c2 (15): 193 sites over both arms.
- The "54 no-key sites": the summary cannot reproduce the 54 (it was a byte-arm count among R17-b's 620 candidate movers, a different
  denominator, and the keys.tsv-keyed set has changed since). On the regenerated manifest, sites on shapes with no keys.tsv key: byte
  arm 172 sites = 71 V1 (57 at 1 term, 14 at 2) + 101 WALK (41 shape "-", 45 at 3 terms, 15 at 4); byte-vm 240 = 122 V1 + 118 WALK.
  So of the byte-arm no-key sites with a term count (131), 71 route V1 and 60 walk.
- Rule check ("V1 iff terms <= 2") finds 2 sites that disagree, both byte arm, both WALK at 2 terms: `(?:\Gx|\b)(?:ab|cd)\b` (kind DFA_HAT,
  r0e0c1) and `(?i)(?:^|;|\|)\s*(?:cat|ls|id|whoami)\b` (kind DFA_SCAN, r0e2c0). Re-running the harness shows both are row R7w with
  basis UNMEASURED-DEFAULT and 2 members: the cause is NOT established; the two kinds (DFA_HAT, DFA_SCAN) differ from the ones the lever set was proven on,
  and a missing per-kind row in the lever set is the likeliest reading (unverified). FINDING (small): the term-count rule as spelled by rev 4.1 and the lever set disagree on 2 of 2374
  sites; B4's census must say which wins.

**Short-subject ruling: applied.** `expected_losses.md` section 3e and r17b_prime §9.2a register SS1 (dfa-hat L = 32 g = 2, same cell as EL5),
SS2a-e (dfa-hat L = 32 at g = 16/32/64/256/inf) and SS3 (dig L = 32 g = 16) under a new L <= 64 B class, tagged `[b4prep-close]`; 3b is ruled.

**POSCOST count (rulings entry 3): OWED, with cause.** The manifest (and the finder shadow trace behind it) carries one shape per site, the
SCANNED position's cover; it has no per-position covers, so "has a <= 2-term position anywhere within its span" and "has a <= 2-term superset
filter" cannot be counted from it. What it does give: the walk-routed set-FIND sites with >= 3 terms at the scanned position number 517
(byte 241, byte-vm 276; 179/201 of them are r3e0c1, the `\w`-like class). `--emit-facts` has `kset_walk` (per-position set SIZES, e.g.
`[3],[3],[4],[10],[3],120`) and `RX_DFA_PREFILTER_OFFSETS`, which are neither covers nor a span. Exact fix (a build, not done here): extend the harness's FD
trace line with `poscov=<terms per position over the span>` (it already holds each position's byte set), rerun `521`'s command (~9 s,
`shadow_census.py manifest --bin build/pcrec-mftrace-harness --ls-bin build/pcrec --set b4prep/b4prep-v1max2.tsv --jobs 4`), then count the 517 sites
by min(terms over positions) <= 2, and for the superset filter state the hull merge (merge cover terms by hull while the merged filter stays
<= 2 terms and adds <= k extra members; k to be stated). Needs a build go for the harness edit.

## State at handoff (lane b4close)
Items 1 and 4 CLOSED; POSCOST OWED (needs a harness build go); short-subject class registered; §3.1a items 1 and 4 marked `[b4prep-close]`.
Rulings: last entry applied is the POSCOST entry (2026-10-21, Frank via kit manager).
