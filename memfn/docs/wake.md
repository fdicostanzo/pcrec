# memfn wake — kit session hand-off (rewritten 2026-10-07 late night; new Linux dev box)

This is the orientation file for the kit session, run as
`/pcrec-memfn-manager` (`.claude/skills/pcrec-memfn-manager/SKILL.md`;
its §1 is the wake order). It is rewritten at every pause and holds the
current state; the history is `journal.md`.

---

## 1. Who you are and where you work

- You are the pcrec-memory-functions kit manager. The pcrec manager
  ("main", session name `pcrecdev1`) files requests in `requests.md`. You
  answer in `responses.md` (you are its only writer). This session's name
  is `pcrecdev3`.
- **Box:** the Linux dev box `pcrec@192.168.1.17`; the repo is
  `/home/pcrec/projects/pcrec`. 16 threads, gcc 15.2, libpcre2 10.46, no
  clang.
  - Bare `timeout` is uutils: use `gnutimeout`.
  - No git identity is configured: commit with
    `git -c user.name="Frank DiCostanzo" -c user.email=frank@dicostanzo.com`.
- **Kit worktree:** `worktrees/memfn`. One branch per delivered unit, cut
  from main. Never merge to main, never push, never `cd` into another tree.
- **Scratch:** `worktrees/memfn-slot/` (gitignored). The session scratchpad
  can vanish mid-session, so do not rely on it.

## 2. Read, in this order

1. `memfn/CLAUDE.md`.
2. `memfn/docs/requests.md`, then `responses.md` (the newest `done:` entries
   and notices).
3. The tail of `memfn/docs/journal.md`.
4. `docs/design/memfn/row_contracts.md` rev 4.1 (§4 floors, §5 steps);
   `docs/design/memfn/integration.md` §22 (R4g done; R4h next in order) and
   §19 (row 6 is revised per main's ruling).
5. BOILERPLATE, coding_guide before C, learnings §3 before a check.

## 3. Box and slot rules (this box)

- One heavy suite at a time across BOTH sessions. Ask main for every heavy
  slot (census, identity gate, full G2, make test, mech), and ping main when
  it ends. Main's lanes queue behind and ahead of you.
- **Light work needs no slot:** make/strict at -j4, single compiles,
  test-memfn-{arms,stamps,rows}, G2 --quick pinned to `taskset -c 12-15`.
- **Landing chain pattern:** one detached script in
  `worktrees/memfn-slot/slotN/run.sh` (census → identity gate → full G2 →
  make test → solo mech), watched by Monitor on its log. Read the verdicts
  from make's `*** [Makefile:N: test-X]` lines.
- **Mech scope:** main's rule (b) for a src-touching migration: rows
  anchored in the changed definitions, plus kit-file rows, plus re-pinned
  rows. A kit-only unit uses rows_for.sh.
- **Every kit lane** runs `python3 scripts/m6read_check_sab_anchors.py`
  before delivering (S570 slipped once).
- **Blinded G2:** the D27 cell is `worktrees/g2u-cell`. Refresh its build/
  and memfn.h/integration.md from the kit tip before each blinded brief. Diff
  it back into `worktrees/g2u` (branch g2u), commit there, then merge into
  the kit branch.

## 4. Current state (2026-10-08 ~21:30, session reset at Frank's request)

Main has M4 (R-7) merged. Main's refactor B is at B4 merged, and B5's chain
owned the box at reset. Rulings since the last wake: D144 add. 4 (official
SIMD verdicts are pcrec-bench runs on each targeted machine: ubuntubudu
Zen 1 / this dev box 7700X Zen 4 with AVX-512 / Mac); D147 add. 11 (SIMD
is a parallel thread, 2:1 behind migration until M5′), 12 (N6 retired),
13 (what "faster" means, preliminary); D155 + addendum 1 (all R-9
questions, Q-R9-1..11). Plan rows filed: [MEMFN-ENTRYSINK] and
[MEMFN-RTDISPATCH] (dispatch by frequency class).

**Branches (kit worktree `worktrees/memfn` is on lane/memfn-m7):**
- **lane/memfn-m7 (R-8, M7: N7 span compare → MISMATCH).** BUILT. slot12
  ran, and its findings are fixed by m7fix (merged, 35c6f628+):
  - inplace_applies always 1, so would_decline 7.7M; zero movers;
  - the census rc check plus mech arm n2sample / row S668;
  - S512 pop re-pinned to 14;
  - startset VM manifests +8/+8 for s670cell.
  Also on this branch:
  - S670 detector cells (s670cell);
  - g2m7 (G2 MISMATCH, mismatch_inplace g2_floor 2403);
  - the ledger notices.
  slot12 itself: G2 full 185.8M/0. The identity gate showed 0 movers on
  plain, utf8 and both ucp sets (the -i and comments sets never ran:
  script bug, fixed).
  **NEXT:** main's GO for slot13 (after B5's CHAIN DONE). Merge main
  first, then strict, then `worktrees/memfn-slot/slot13/run.sh`:
  - census (must be would_decline 0);
  - the identity gate on 7 sets (plain via memfn_r4c_gate, the others via
    slot13/armjudge.py);
  - G2 full;
  - make test via perfrun;
  - 14 mech rows from mech_rows.txt.
  Then pin mismatch_inplace's pcrec_floor from `n2_report.py ... --propose`
  (still PLACEHOLDER), run test-memfn-rows, and post `done: R-8` with the
  verdict. Restore docs/dev/artifact_size_log.tsv after make test; never
  commit it.
- **lane/memfn-m6 (R-10, M6 = VMSTRIDE only).** BUILT @ e48cc296, STACKED
  on an older lane/memfn-m7 (00b1f3da).
  - MF_SITE_ABI 8: multi-term ADVANCE, MF_MAX_TERM 32.
  - Shadow 0 mismatches; 62,216 pairs 0 movers.
  - Manifest: VMSTRIDE delegated, VMLAZY pending (Q-R10-7).
  - N6 retired (D147 add. 12): manifest, vocab and C12 rows deleted;
    S511/S512 touched.
  - Report docs/dev/lanes/m6_report.md (§7 = G2 needs, §8 = slot chain,
    66 mech rows).
  **NEXT:**
  1. Relaunch the blinded lane **g2m6**. The cell `worktrees/g2u-cell` is
     already refreshed from the m6 tip and clean (its memfn/tests ==
     m6's). Same brief as before: m6_report §7, strided ADVANCE oracle,
     W in {1,2,3,7,8,9,16,31,32}, guard pages, refusals, W1/W2,
     sabotage a/b/c; deliver G2M6_REPORT.md. Then diff the cell into
     worktrees/g2u (branch g2u; ff it to lane/memfn-m6 first, since g2u
     is now at the m7 G2 state) and merge it into lane/memfn-m6.
  2. Merge lane/memfn-m7 (with m7fix) into lane/memfn-m6, ALONE, then
     strict. Expect conflicts in S512, manifest/floor literals and the
     lanes index.
  3. Ask main for M6's slot (only after M7 is delivered and merged).
- **lane/memfn-r9 (R-9, SIMD design).** @ c0b61c16: integration.md rev
  4.9 §R4.9, revised after panel r9 (review
  docs/dev/reviews/2026-10-08-r9-memfn-simd.md, 43 ids) plus r9fu (glibc
  trap: batch 1 narrowed to `over: fn-pair`) plus D155 (file-scope helpers,
  the R4e′.0b routing abi event, C18 restated, frequency classes).
  **NEXT:**
  - a short lane to update §R4.9 to Q-R9-10 = shape (c): the FUNC's
    WHOLE BODY is the #if chain, one helper call per arm. "A function that
    does work never contains #if; a selector function's whole body may be
    the #if chain, one call per arm, and nothing else." There is no level
    macro. Q-R9-11 is a `freq` column, built only when RTDISPATCH
    triggers. Mark Q-R9-1..11 RULED (D155 + add. 1). C18 leg (d) allows
    only that selector shape.
  - Then a LIGHT re-check panel, then deliver R-9 (done:).
  - The rev number 4.9 must be reconciled with the m7 branch's rev 4.8
    [M7] text at merge.
  - Batch 1's build request comes after main files it.

**Capacity:** 2 migration : 1 SIMD lane until M5′ (D147 add. 11).
**Leftover worktrees** (prune via scripts/wtprune after delivery): m7,
m7fix, s670cell (after M7 merges), m6 (after M6), r9d (after R-9), r4h
(its untracked r4h_rulings.md first). Keep g2u and g2u-cell.

## 5. Next actions on wake

1. Create the heartbeat cron at 17,47. Run ListAgents. Read requests.md
   for anything new.
2. Relaunch g2m6 (§4, M6 NEXT 1) and the R-9 (c) text lane (§4, R-9 NEXT):
   both light, no slot needed.
3. Wait for main's GO, then slot13 (§4, M7 NEXT).
