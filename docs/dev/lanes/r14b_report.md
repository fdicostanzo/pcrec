# r14b — [MEMFN] R-14, the BUILD: vrun verifies only what its filter did not prove

Lane r14b (opus), 2026-10-11. Branch `lane/r14b`, cut from the kit branch
`lane/memfn-r14` 9fefd983 (main 76428e05 + the R-14 ack). Charter:
`memfn/docs/requests.md` R-14 (build part only; the re-timing slot is not
this lane's), D147 addendum 15, `memfn/docs/ideas.md` 2026-10-11.

## 1. Summary (resume from here)

- **What changed.** Before this lane, each set lane of a vrun helper's
  candidate mask was verified by the BODY's whole run compare. Now the
  verify compares only the run positions the mask did NOT test. KA is
  always dropped, and KB is dropped too when the mask reads it (`vrun-kb`
  not denied). A run the mask covers whole has no verify at all: the
  helper returns the lowest set lane (`if (m) return i + ctz(m);`).
- **How.** runcmp.c gains `run_cmp_render_trim` and `run_cmp_trim_none`.
  - It is ONE renderer with the full compare: `rc_render` takes an
    optional proven-position list.
  - The row is the whole run's walk choice, so the `denies` class still
    reaches it.
  - In the words form, the word width is the whole run's, the one helper
    `run_cmp_prepare` already declared outside any guard (see §3).
  - A proven position, or one an earlier window already compared (the
    overlapping last word), becomes a don't-care byte of its window, and a
    window left with no compared byte is not loaded.
  - The bytes form drops the proven positions.
  - A trimmed exact run (the `memcmp` row) is compared byte by byte. No
    vrun site reaches that today, because KA is always a masked cube.
- **The deny.** `--memfn=no-vrun-trim` (options.def, DENY, scan, simd)
  renders the whole-run verify. Against the base it is byte-identical
  (§5.3), so it is the OFF arm R-14's re-timing measures the trim against.
- **SIMD-off is untouched.** There are 0 movers on c-default, c-vm and
  emit-ir in the light sample (§5.3), so this is not a pcrec abi event.
- **SIMD-on.** Only the vrun helpers' verify lines and the
  `SIMD_GUARDED_BYTES` stamp move (§5.3).
- **The scalar `__body` is unchanged.** Its memchr stream proves KA's two
  members only.
- **G2's SIMD family** gains three things:
  - a `deny-trim` class;
  - a VERIFY CHECK: each rendered helper's verify is parsed from its text
    into the set of positions it compares. That set must equal the rule's
    set, derived in the runner from the GENERATED masks and filter. The
    expectations come from G2's generated data and its scalar byte-loop
    answers, never from the kit's output;
  - floors per verify shape: none, gap (non-contiguous), whole, bytes and
    words.

  `--quick`: 1,599 passed / 0 failed (§5.2).
- **Bounds did not move.** The trimmed verify's worst case is smaller
  (2,583 / 2,643 / 5,214, against 2,661 / 2,721 / 5,370 for the whole run).
  The bound must hold for whichever arm a caller picks, so it stays at the
  whole-run arm's 2,700 / 2,800. G2's ALONE measurement is now the larger
  of the two arms.

## 2. Commits

| commit | content |
|---|---|
| 845e17fa | runcmp.c `rc_render` / `run_cmp_render_trim` / `run_cmp_trim_none` (and `rc_emit_words`/`rc_emit_bytes` take the proven list); vrun.c `vrun_proven` + the trimmed / no-verify render; kit.h; options.def `vrun-trim`; G2 generator (`deny-trim` class, `mask` meta column, alone over both arms) and runner (verify check, instrument/plant updates); S719 re-anchored |
| a3ef3ff9 | G2 verify-shape floors (measured); spec hunks: tuning.md §2.43¶3b, registry.md §6¶8a row + §6¶8b floor 3 -> 4; `simd_accept.tsv` 4 CANDIDATE lines; cli cases; S793-S796; CLAUDE.md files; integration.md §R4.9.5 table row |
| 74e6ceb7 | the trimmed bound measurement in vrun.c / simd_bounds.tsv comments |
| (tip) | this report, lanes/CLAUDE.md line, final G2 run numbers |

## 3. Design decisions

**Deny row: YES, `vrun-trim`.** The house rule (memfn/CLAUDE.md, "Every kit
change that moves bytes carries its own deny", D144 item 4) is
unconditional. The trim moves SIMD-on bytes, so it needs a row that is its
OFF arm. It is also the only way R-14's re-timing can measure trim against
full in one binary: the KB question was DEFAULT vs `no-vrun-kb`, and this
one is DEFAULT vs `no-vrun-trim`. It is an option of both vrun rows, like
`vrun-kb`, not a row of a table, so it carries no MEMFN_FORMS token
(`vrun@w32+w16` is unchanged).

**Word width: the whole run's.** The narrower word a short trimmed range
could use would need a word-load helper declaration (`<p>_w2`) that only
the SIMD rendering reads. A declaration inside the `#if` guard would mark
the helper emitted (`wemitted`), and a later scalar use would then find it
compiled out. A declaration outside the guard would be text the SIMD-off
artifact lacks, which breaks the floor rule (simdfloor). The whole run's
width was already declared by `run_cmp_prepare` ahead of the FUNC, outside
any guard, for the BODY's own compare, so the trim reuses it. The cost is
that a 1-byte remainder in a long run still loads a word, for example
(?i)eqeeez's second word, which compares only E@4.

**Dedup across the overlapping last word.** Words form only: a position an
earlier window compared is a don't-care of a later window, so no byte is
compared twice. The full compare keeps its overlap: it is byte-identical,
because the dedup applies only when a proven list is given.

**No verify where nothing is left.** This is `run_cmp_trim_none`: every
position is proven or has mask 0x00. The loop's `while (m) { cand...
verify... }` becomes `if (m) return i + ctz(m);`. G2's runner text edits
(`instrument`, the `no-verify` plant) were taught the second shape. The
`no-verify` plant skips helpers that have no verify, and is red if it
edits none.

## 4. Before / after (the w16 helper's verify line; the w32 helper's is
identical in every case, checked; the filter lines are unchanged by this
lane)

`(?i)cat` (KA = C@0, KB = A@1):

| arm | before (9fefd983) | after |
|---|---|---|
| KB on | `if ((rx_w2(subject + cand) & rx_w2("\337\337")) == rx_w2("CA") && (rx_w2(subject + cand + 1) & rx_w2("\337\337")) == rx_w2("AT")) return cand;` | `if ((rx_w2(subject + cand + 1) & rx_w2("\000\337")) == rx_w2("\000T")) return cand;` |
| KB off (`no-vrun-kb`) | same as above | `if ((rx_w2(subject + cand) & rx_w2("\000\337")) == rx_w2("\000A") && (rx_w2(subject + cand + 1) & rx_w2("\000\337")) == rx_w2("\000T")) return cand;` |

`(?i)eqeeez` (KA = Z@5, KB = Q@1: uncovered 0, 2, 3, 4, non-contiguous):

| arm | before | after |
|---|---|---|
| KB on | `if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("EQEE") && (rx_w4(subject + cand + 2) & rx_w4("\337\337\337\337")) == rx_w4("EEEZ")) return cand;` | `if ((rx_w4(subject + cand) & rx_w4("\337\000\337\337")) == rx_w4("E\000EE") && (rx_w4(subject + cand + 2) & rx_w4("\000\000\337\000")) == rx_w4("\000\000E\000")) return cand;` |
| KB off | same as above | `if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("EQEE") && (rx_w4(subject + cand + 2) & rx_w4("\000\000\337\000")) == rx_w4("\000\000E\000")) return cand;` |

`(?i)union` (KA = U@0, KB = N@4):

| arm | before | after |
|---|---|---|
| KB on | `if ((rx_w4(subject + cand) & rx_w4("\337\337\337\337")) == rx_w4("UNIO") && (rx_w4(subject + cand + 1) & rx_w4("\337\337\337\337")) == rx_w4("NION")) return cand;` | `if ((rx_w4(subject + cand) & rx_w4("\000\337\337\337")) == rx_w4("\000NIO")) return cand;` (the second word holds only N@4, proven: not loaded) |
| KB off | same as above | `if ((rx_w4(subject + cand) & rx_w4("\000\337\337\337")) == rx_w4("\000NIO") && (rx_w4(subject + cand + 1) & rx_w4("\000\000\000\337")) == rx_w4("\000\000\000N")) return cand;` |

**A 2-byte run.** pcrec emits no vrun FUNC for a 2-byte run: `(?i)ab`,
`(?i)qz` and nine other shapes tried all read `MEMFN_FORMS "none"`. The
cases below are therefore G2 SIMD family sites, seed 20261009, rendered by
the same generator against the base library and the tree library:

- Site 44: run `JT` at offset 2, masks DF DF, KA@1 + KB@0 (KB on). Both
  levels:
  - before: `if ((g2v_p44_w2(subject + cand + 2) & g2v_p44_w2("\337\337")) == g2v_p44_w2("JT")) return cand;`
    inside the `while (m)` loop;
  - after: `if (m) return i + (size_t)__builtin_ctz(m);`, with no verify
    and no loop.
- Site 85: a 2-byte run with no ranking, so KA alone, which is the KB-off
  shape. It also runs under MF_D_RUN_OVERLAP, so the bytes form. Both
  levels:
  - before: `if (((subject + cand)[0] & 223) == 76 && ((subject + cand)[1] & 223) == 85) return cand;`
  - after: `if (((subject + cand)[0] & 223) == 76) return cand;`

**Deny arm.** Every `deny-trim` helper G2 rendered (34 of them) is
byte-identical to the base library's rendering. Every `__body` helper (400
of 400) is unchanged. At the pcrec level, the deny arm against the base at
`-fmemfn-simd` has 0 movers (§5.3).

## 5. Validation (light only; pinned `taskset -c 12-15`, `-j4`, gcc 15.2, the dev box)

Logs: `/home/pcrec/.claude/jobs/e99da2a5/tmp/r14b/` (`light/`, `g2s*.log`,
`sweep_*.log`, `sab_*.log`).

### 5.1 Suites (tree a3ef3ff9, with 74e6ceb7's comment-only edits landing mid-chain; times are 2026-10-11 EDT)

| check | start-end | verdict |
|---|---|---|
| `make -j4` | 01:31:23 | rc 0 |
| `make strict` | 01:31:23-01:31:34 | rc 0 |
| `make test-codegen` | 01:31:34-01:34:52 | rc 0, 16/16 scripts, [SABANCHOR] resolves the re-anchored S719 and S793-S796 |
| `make test-registry` | 01:34:52-01:35:42 | rc 0; `[memfn floor] 4 row(s), floor 4`; axes coverage pin 226 unchanged (the floor arm is one check whatever the row count) |
| `make test-spec-history` | 01:35:42-01:35:45 | rc 0, 145/0 |
| `make test-memfn-simdfloor` | 01:35:45-01:36:11 | rc 0, 51/0 (44 movers, 44 SIMD FUNCs) |
| `make test-memfn-rank` | 01:36:11-01:36:23 | rc 0, 11/0 |
| `make test-memfn-arch` | 01:36:23-01:36:31 | rc 0, 15/0 |
| `make test-memfn-stamps` | 01:36:31-01:36:50 | rc 0, 25/0 |
| `make test-memfn-guarded` | 01:36:50-01:37:55 | rc 0, 10/0 (3,976 cells, neutrality and bound) |
| `make test-memfn-rows` | 01:37:55-01:37:56 | rc 0, 151/0 (check F: the 4 `vrun-trim` lines) |
| `make test-cli` | 01:37:56-01:38:09 | rc 0, 284 passed / 0 failed (the two `no-vrun-trim` cases PASS) |
| `make test-memfn-arms` | 01:38:23-01:38:24 | rc 0, 338/0 (the scalar arm pins: the full run compare's text unchanged) |
| `make test-memfn-deleg` | 01:38:24 | rc 0, 5/0 |

### 5.2 G2 SIMD family, `--quick` (`memfn/tests/run_g2_simd.py`)

`g2s1.log`, 01:28:43-01:30:52, on 845e17fa's content with the
verify-shape floors still at 0 (measuring them):

- **1,599 passed / 0 failed.**
- Every build: 19,250,552 answer checks, 0 fails, 0 faults: x86-64,
  x86-64-v3, x86-64-v4, gpr-only and asan-x86-64-v3.
- Every plant red where its level is live and green where it is compiled
  out.
- Classes: pos 230, `deny-trim` 17, and every other class 17.
- The verify check is green on every rendered helper.
- Verify shapes: none 24, gap 344, whole 34, bytes 67, words 437. The
  floors are set at about 80%: 19 / 275 / 27 / 53 / 349.
- Guarded bytes: the ALONE maxima are 2,661 / 2,721 (the whole-run arm's);
  `vrun@w32+w16` max 5,214 against bound 5,500.

FINAL RUN on the tip: see §5.5.

### 5.3 Identity, light tier (a 1-in-8 corpus sample, NOT the full gate)

The population was every 8th distinct corpus pattern (emit_sweep's own
enumeration and sampling rule, 567 patterns) plus 8 vrun witnesses, 575 in
all, 537 reached. The command was `scripts/emit_sweep.py --ref-bin <base
9fefd983 build> --no-corpus --patterns-file ...`.

| arm | streams | result |
|---|---|---|
| SIMD-off (default) | c-default, c-vm, emit-ir-vm, dumps | **0 artifact movers** on all three artifact streams. The only dump that moves is `--list-axes`, by exactly the `vrun-trim` row. Self-check passed (`sweep_off.log`, 01:38:34-36) |
| `--extra=-fmemfn-simd` | c-default, c-vm | c-default 10 movers, c-vm 9 (`sweep_on.log`, 01:38:36-40). `movers.py`: every mover is a vrun artifact, every vrun artifact moved (10 / 10), and every changed line is a helper's `return cand;` verify line or the `SIMD_GUARDED_BYTES` stamp (0 bad) |
| tree `--memfn=no-vrun-trim` (a wrapper `--bin`, because the base has no such row) vs base, both `-fmemfn-simd` | c-default, c-vm | **0 movers** on both (`sweep_deny.log`, 01:38:40-44): the deny arm IS the pre-R-14 rendering |

### 5.4 Sabotage S793-S799 (allocated to R-14; S797-S799 unused, free)

Each row was run SOLO with `PROCS=1 bash tests/mech/run_sabotage_matrix.sh SNNN`
on a fresh `git archive HEAD` tree.

| id | edit | arms | solo verdict |
|---|---|---|---|
| S793 | (a) the trimmed words compare also skips the first position after each earlier window (`done = at + w + 1`): an uncovered position is never compared | g2simd | DETECTED, g2simd 269 fail / 1,330 pass (01:39:09-01:41:23, at 74e6ceb7) |
| S794 | (b) the trim takes the first ranked non-KA position as proven even under `--memfn=no-vrun-kb` | g2simd | DETECTED, g2simd 31 / 1,568 (01:41:23-01:43:36) |
| S795 | (c) KA's run index off by one in the proven list (`x->k - off + 1`) | g2simd | DETECTED, g2simd 541 / 1,058 (01:43:36-01:45:49) |
| S796 | the `no-vrun-trim` deny ignored | cli g2simd | DETECTED, cli 1 fail / 284 pass and g2simd 35 / 1,564 (01:45:49-01:48:16) |
| S719 | (re-anchored, r13's row) the verify replaced by `1` on every rendering, trimmed or whole | g2simd | DETECTED, g2simd 551 / 1,048 (01:48:16-01:50:28) |

### 5.5 Final G2 SIMD family run on the tip

`g2s2.log`, 01:50:38-01:52:49, on 74e6ceb7 (the tip's code; the tip adds only this report): **1,599 passed / 0 failed**, with the verify-shape floors live (24/344/34/67/437 against 19/275/27/53/349), every build at 19,250,552 checks with 0 fails and 0 faults, and the guarded maxima unchanged (2,661 / 2,721 alone; 5,214 both).

## 6. OWED (heavy; the kit manager's slot)

1. **Identity, the full gate, on every arm, both layers**, against
   lane/memfn-r14 9fefd983:
   - `python3 scripts/emit_sweep.py --tree . --ref 9fefd983 --jobs 12`,
     then the same with `--arms start` and with `--variant all`. Expected:
     0 artifact movers; only the `--list-axes` dump moves, by the
     `vrun-trim` row.
   - `--extra=-fmemfn-simd`: the movers are exactly the vrun FUNC
     artifacts (test-memfn-simdfloor's 44), and only their verify lines and
     the `SIMD_GUARDED_BYTES` stamp move.
   - `-fmemfn-simd` with `--memfn=no-vrun-trim` on the tree side (the
     wrapper-bin method, §5.3): 0 movers.
2. **G2 full:** `make test-memfn-g2-full`. G2 quick (`make test-memfn-g2`,
   all families) is also OWED. BOILERPLATE names no allowed light list, so
   this lane ran only the SIMD family section standalone (§5.2, §5.5).
3. **make test:** `scripts/perfrun --label r14b -- <log>`. Read it with
   `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`.
4. **The mech rows:** none are owed for this lane's rows (§5.4). A full
   battery would re-run the rows anchored in `vrun.c` / `runcmp.c`: S716-S723,
   S750-S754, S267, S285, S443-S445 and S573. S443/S444/S445/S573 anchor on
   `rc_emit_words` lines that this lane kept verbatim but whose
   surroundings changed. Their intent (the full compare's word offsets,
   sense and count) is unchanged.
5. **R-14's re-timing** (the charter's second deliverable, a heavy slot:
   ask main for the GO). Use slot20's harness RQ4 cells: dense-hit, the
   spacing ladder, pc16/short75. Run them at both levels and both layers,
   with arms DEFAULT, `--memfn=no-vrun-trim`, `--memfn=no-vrun-kb`, the two
   denies together, and OFF. The question is whether the 179 losing
   KB-vs-no-KB comparisons persist when both arms trim. Note that the trim
   also helps the KB-deny arm (KA is dropped there too), so the KB
   comparison to re-time is DEFAULT vs `no-vrun-kb` with trim on in both.
   `no-vrun-trim` isolates the trim's own effect.

## 7. Charter vs delivered

| charter item | state |
|---|---|
| trimmed verify: only positions not covered by the filter (KA always, KB when rendered) | DONE (`vrun_proven`, `run_cmp_render_trim`) |
| word-load idiom kept (rx_w2/rx_w4 via memcpy, masked compares) | DONE (the whole run's width; don't-care bytes masked 0x00) |
| every shape: empty remainder (no verify), non-contiguous, masked and exact positions, w16 and w32 | DONE: the no-verify shape (`if (m) return ...`); a gap ((?i)eqeeez, G2 gap 344); exact positions in masked words; both arms (identical verify text) |
| scalar `__body` unchanged | DONE (400/400 G2 `__body` helpers byte-identical; arms pins 338/0) |
| SIMD-off byte identity, no abi event, light identity proof | DONE light (§5.3: 0 movers on the sample; simdfloor/stamps/guarded green); full gate OWED (§6 item 1) |
| deny row if a distinct form, with floor + coverage pin | DONE: `vrun-trim`; floor 3 -> 4; coverage pin 226 did not move (verified, §5.1) |
| SIMD_GUARDED_BYTES bounds | measured: the trim lowers the worst case (2,583 / 2,643); the bound stays 2,700 / 2,800, the whole-run arm's, which a caller can still select; comments updated, no number moved |
| G2 green; new cases from the scalar byte loop | DONE: `deny-trim` class, the verify check from GENERATED masks, shape floors (none/gap/whole/bytes/words); answers are the driver's byte loop |
| simdfloor / stamps / guarded / rank / arch green | DONE (§5.1) |
| sabotage S793-S799: (a), (b), (c) + deny, solo DETECTED | S793-S796 (§5.4); S797-S799 unused |
| spec hunks (D80) | DONE: tuning.md §2.43¶3b, registry.md §6¶8a row + §6¶8b floor. MEMFN_FORMS tokens did not change (an option, not a form) |
| report with before/after for (?i)cat, (?i)eqeeez, a 2-byte run, (?i)union; both arms; KB on/off | DONE (§4) |
| OWED heavy list | §6 |
