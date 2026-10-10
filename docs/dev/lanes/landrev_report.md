# Lane `landrev` — `[START-LANDING]` revision 2 (2026-10-09, opus)

**Brief:** apply the D6 panel `../reviews/2026-10-09-r-startlanding-panel.md` (24 ids,
binding dispositions) to `docs/design/start_landing.md`; DESIGN + twins only, nothing
under `src/`. Worktree `worktrees/landrev`, branch `lane/landrev`, from main
`efc58146` (abi 71). Box rules followed: compiles at `-j2`, no `make test`, no mech;
timing directional (median ± σ and the 2(σa+σb) test).

**Delivered (commits on `lane/landrev`):**
- `docs/design/start_landing.md` revision 2: a §R2 table (one row per id, with where),
  `[r2 <id>]` marks at every in-place edit, §11 candidates, §9 restated.
- `docs/design/locate_finish.md` L2.2: an `[r2-landing]` note (the RECOVER hand as
  masks, the (slot, route, hand) closure key, sequencing).
- `studies/start_landing/`: `mktwin.py` (three guard forms calling the seam's own
  decode), `mksubj.py` (the SL-E4 pool), `decode_eq.py`, `run_check.sh` (`GUARD`),
  `sumcheck.py` (totals + vacuity), `run_timing_guard.sh` + `summarize_guard.py`,
  `proto.patch` rev 2 (seam spelling, `[bmin, bmax]`, `LANDEMPTY`), `census.py`
  (empty arm, new columns), `edit_set.tsv`, `reader_tokens.tsv` + `readers.sh`,
  `witness_movers.py`, and `results/` (regenerated census + coverage, guard sweeps,
  timing, decode check, derived anchors/readers/movers, hand-extracted witnesses).
- `docs/design/start_table/sabotage_anchors.py`: `SL1`-`SL3` added to the commit
  order (byte-neutral for earlier labels).
- CLAUDE.md indexes: `docs/design/`, `docs/design/start_table/`, `studies/`,
  `studies/start_landing/`, `docs/dev/lanes/`.

## Results, by priority

**1. The guard (SL-G1 = SL-E1).**
- SL-G1's post-loop SKIP is the design's form: after the loop, if the character at the
  final landing `L` does not decode, start = the first position after `L` that does
  (bounded by `e`, never reached). Proof written out in full (§2.5.2: Claims A/B/C over
  four facts F1-F4, minimization addressed). SL-E1's Fix A rebuilt in this lane's twin
  and recorded (§2.5.3). Revision 1's restart withdrawn.
- Decode control: `decode_eq.py`, the seam's `u8_defs_decode` vs an independent Table
  3-7 spelling, all 2^32 four-byte windows × 4 ends: **17,179,869,184 cases, 0
  disagreements** (`results/decode_eq.txt`).
- Identity (assert mode, run 3 pool; `results/twins_guard_run3.txt.gz`): every utf8
  `landing` row — bench both configs 54, corpus default 220 — plus 5 constructed
  witnesses, with the SKIP and with Fix A: **SKIP total 279 rows, 98,321,644 cells,
  39,936,433 DFA-body calls compared, 0 differences; 50,989,794 libpcre2 cells, 0 NEW
  disagreements; 26,170,885 find-all calls, 0 differences. Fix A identical (0).**
- Controls: no-guard over the 27 bench default utf8 rows → 1,168,452 call differences
  on 22 rows (the 5 passing: 3 ASCII-only start sets where no guard is emitted, 2
  offset-set rows where the candidate test proves the character); `a\b` forced through
  `landing` → 64,200 call differences.
- Timing (`results/timing_guard_run{1,2}*.txt`; 7700X, load1 8-13, `taskset -c 5`):
  well-formed 1 MiB utf8: skip −30.9% / −26.9% (`.`), −39.1% / −42.2% (`\p{L}+`), all
  four clear 2(σa+σb); Fix A −22.4% / −15.4%, −28.3% / −35.1%, two of four clear. Skip
  faster than Fix A in all four; the gap itself does not clear the bar (727/940 µs and
  590/478 µs). Hostile 1 MiB (six lead-run subjects): both linear, 1.8-5.3 ms vs today
  1.27-2.09 ms; neither wins every cell. Restart on 64 KiB: **2.99 s / 4.67 s** vs today
  0.08 / 0.13 ms (≈13 min per MiB). No 60 s wall bound fired.
- **Pick: the skip** (consistent direction on the bench's regime, plus structure: no
  hot-path statement, no re-entry, no NEXT-emitter change). The hostile control is a
  standing cell (`run_start_landing.sh` §H, 10 s bound) with sabotage row 12.

**2. Checks and readers DERIVED (SL-C2 and the rest).**
- `edit_set.tsv` (23 entries) through `sabotage_anchors.py` at `efc58146`: **3 anchor
  re-aims (S221, S223, S693)**; 21 sites re-run at SL2, 5 at SL3, 92 after. Revision 1's
  "S218-S222 re-anchored" is withdrawn: no anchor text of S218/S219/S220/S222 moves.
- `readers.sh` (9 token classes, both trees): 250 (class, file) readers over 117 files,
  18 in pcrec-bench. Every gate the panel named is found by the census
  (run_search_pinned, run_nomatch_caps, run_scan_edge_census, cand_oracle_witnesses,
  m5_stage1_stamps, the registry checks, `selfcheck.py:5871`, the fixtures,
  `list_axes.tsv`).
- `witness_movers.py` over 636 files: 364 extracted witnesses, **112 move** (77
  sabotage-row files, 10 gate files); 34 files' run-time-built lists counted as
  unparsed, and the three named gates among them probed by hand
  (`results/hand_witnesses.tsv`: run_search_pinned `abc`/`$`/`(?!a)`; run_nomatch_caps
  three K78 witnesses + one empty; scan_edge_census four `r=1` rows + `[0-9]{3}\z`).
- Reach re-aims (SL-C4): S218, S220 (+ its 4-pattern manifest), S227, the scan-edge rows,
  all under `-fno-start-width`; S219 does not move.
- SL-C1: `recover_on_path`; census 63 corpus empties, 44 with `W ≥ 0`, 0 bench;
  witness `a\bb` (and run_nomatch_caps' empty K78 witness).
- SL-C3: one success-site emitter with the K78 fill; witnesses `(a){0}(b){0}c|d`,
  `(a){0}\w+` (twinned, 0 differences).
- SL-C5: the standing gate `run_start_landing.sh` designed; row 2 witnessed (`a\b`);
  row 3 dropped; row 4 per NEXT form (6 of 8 reached, `é(?:x$)?` constructed for
  `offset-set-bounded`; the two `first-*` forms declared unreached: seeded-only vs
  Λ ⇒ unseeded); row 9 restated as distinct from S222; rows 10-13 added.
- SL-C7: product arm floors (both-apply: 46 bench / 1,258 corpus); run_search_pinned
  §10 denies all three (25 corpus pinned rows with `W = 0`).
- SL-C8: the literal hand-witness `--emit-facts` table (12 rows; the probe agrees with
  every row); count corrected to 0 of 2,225 Λ-OK compiles seeded.
- SL-C9: census regenerated: corpus default 1,750 = 1,334 + 416; hybrid landing 71;
  reverse-pass 1,100; coverage 42.58 + 3.94 + 8.11 ms reproduces exactly.
- SL-C10/C11: bench readers into SL4; axes.def rows (mask derives since K92), pcrec.h
  bits, tuning.md headings, declared listing and trace files.

**3. Vocabulary.**
- SL-G2/E2: Λ over `start_cls`/`onebyte_max`, P0 self-synchronization; **K50: the gate
  is absent on Λ's (non-nullable) population, but its OMISSION CHECK
  (`cstart_check_omission`, `src/ir/nfa.c:1107`) fails the compile on any first byte
  outside `start_cls` — so Λ.1 implies Λ.2, checked on every compile**; Λ.2 becomes an
  assertion; `cont-in-start-set` population 0 / 9,858.
- SL-G3: `[bmin, bmax]` from the one union-frontier iterator; cross-check with rev 1's
  walk 0 disagreements / 9,858. Λ shares its closure step, not its union (a union
  frontier cannot isolate a path) — recorded as the one place the disposition was
  narrowed.
- SL-G4/C6: hand as EXISTS / WINDOW masks; (slot, route, hand) closure key; L2.2 note.
- SL-G5 grid, SL-G6 derivation (`ab` on "aab"), SL-G8 constants, SL-E3 signature.

**4. Candidates (§11):** U1 fixed-margin captures (note on `[CAP-EARLY-STOP]`/D142,
trigger D142's restricted to an all-fixed-margin census), U2 `bmax` for
`[OPT-ENDWIN-ENC]` (32 end-pinned multibyte declines, 4 bench), U3, U4 as filed.
**plan.md not edited** (the manager files them).

## Findings worth the manager's attention

- **F-LR1 (instrument defects, my own, fixed and recorded):** the first two SL-E4 pools
  were blind — run 1 lacked class-own truncations (the no-guard control passed on
  `(?i)s`, `[α-ω]+`), run 2 paired continuation classes with the first lead only (24
  of 274 rows' `ex` pools held no matching subject). `sumcheck.py` now prints vacuity;
  5 corpus rows' `ex` pools are still vacuous (rare `\p` categories), their other
  pools are not.
- **F-LR2:** on `offset-set` NEXT forms that verify the first character, the guard is
  dead code (observation; D77, not exploited).
- **F-LR3:** `run_search_pinned.sh`'s `START_VALUES` gate and `selfcheck.py:5871` go red
  by design at SL2; the bench one needs the bench's own change first (SL4 note).
- **F-LR4:** revision 1's twins carried the restart guard; their answers stand (identity
  holds), only the cost claim fell — the timing in rev 1 had only well-formed subjects.

## Validation

COMPLETE for a design lane: the guard identity sweeps, controls, decode check, census,
coverage, reader census, anchor derivation and witness movers all ran to completion
(logs in the lane's scratchpad, verdicts committed under `studies/start_landing/
results/`). Nothing is owed. No `make test`/mech was run (nothing under `src/`
changed; the brief forbade them).

## For a fresh agent resuming

The note's §R2 is the index. The build lane re-derives at its own pin: the census
(`census.py`), `edit_set.tsv` → `sabotage_anchors.py`, `readers.sh`,
`witness_movers.py`; re-runs the guard sweep on the BUILT rows against the triple-deny
build; and takes sabotage ids from the manager.
