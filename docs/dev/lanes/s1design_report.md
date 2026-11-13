# s1design: plan_frame 3.0b and span_runs_sheet K38-3, re-based on main after K38-2

Lane s1design (opus), branch `lane/memfn-s1design`, cut from main 35bee4da9. DESIGN ONLY: no code, no
make, no suites, no queue jobs. The changed text is marked `[s1d]` in `docs/design/memfn/plan_frame.md`
(§5 3.0b, plus one-line pointers in the header, §2.1, §3 and §4.2) and in
`docs/design/memfn/span_runs_sheet.md` (the K38-3 row and the §5 Order paragraph only).

## STATE AT HANDOFF

STATE: DONE. Branch lane/memfn-s1design, three commits on 35bee4da9 (plan_frame, span_runs_sheet, this report). No rulings file named.

OWED: none.

## Summary

- **ASK-2 is void.** K38-2 deleted `req_run_member`, the run window ask that ASK-2 framed, and its loud
  check. No pcrec ask states a run window any more.
- **ASK-6 is new.** K38-2 added a pcrec `mf_wdecide` caller: `req_run_at`, the cover row of the
  `<PREFIX>_REQ_RUN` `@` table. It reads only the decision group (`has_stop`, `stop`). Under 3.0b it asks
  with call NONE and `def` NULL, and no byte moves. 3.0b therefore has the same number of pcrec callers as
  before: ASK-1 and ASK-6.
- **The seam numbers.** `MF_SITE_ABI` is 27 at 35bee4da9, so 3.0b takes 28 if it lands next.
  `MF_CLASS_V` is 9 (K38-2 added `mf_class.run`), and 3.0b still does not move it. `mf_wreply`'s layout
  did not move, so the frame part is still appended after `path` and R27's `offsetof` comparator stands.
- **Sabotage ids.** S2994-S3012 are all taken. 3.0b has 19 rows: the 18 already listed plus (AF), which
  the kit manager ruled in at Q14 and which this revision now writes into §5. They are expected as
  S3078-S3096. The build re-takes them.
- **The `wf_part_site`/`wf_parts_prepare` overlap is gone.** It came from ASK-2's row alone. With
  ASK-2 void, 3.0b edits neither function.
- **K38-3.** K38-2 already delivered layouts L and A for every target pass. K38-3 now has two pieces:
  - the per-(level, layout) W-K4 cells, with the level list read from the kit's table;
  - the step-back card cell, kept UNMEASURED.
  It moves no byte: no abi event and no spec change.
- **Separability.** 3.0b and K38-3 are separable and touch disjoint files. K38-3 should go first, or the
  two can run in parallel.
- **The three standing questions** (`docs/design/CLAUDE.md`):
  - Measurement regime: relevant only to K38-3's card cell, and that cell is unmeasured here.
  - Independent control: relevant. The K38-3 level list is held to the kit's table, not to the
    script's own literal. 3.0b's controls are unchanged.
  - What moves on regeneration: nothing. No byte or abi moves in either unit.

## What K38-2 moved under 3.0b

I grepped every cite in 3.0b's text, and in the §3, §4.1 and §4.2 text that 3.0b reads, at a678d0a4e
(the note's tree) and again at 35bee4da9. The script that mapped them is
`/var/tmp/pcrec-pcrec/scratch/memfn/s1design/citemap.py`. It matches each cite's text; it does not
trust line numbers.

| item | moved by | at 35bee4da9 |
|---|---|---|
| ASK-2's subject: `req_run_member` (`emit_dfa.c`) and its loud check | K38-2 | deleted; ASK-2 VOID |
| new pcrec phase-1 caller `req_run_at` (cover row of the `@` table, commit 2c3b2097e) | K38-2 | `emit_dfa.c` :16077; becomes ASK-6 (NONE, `def` NULL) |
| new pcrec reader of ASK-1's reply: `req_run_at` reads `us.wr.run_stated`/`run_member` | K38-2 | :16089-16092; reads the decision group only, no edit |
| new kit-test caller `run_decide_check.c` (`wreply`) | K38-1 | :207; breaks at the signature change and is fixed in the same commit |
| `mf_wreply` run fields | K38-2's K7 (b) unified the run reply as `mf_run_reply` | `mf_wreply` UNCHANGED (`memfn.h` :1583-1598) |
| a decision input on the art: the `run-tie-left` lever | K38-2a | read in `decide` (`window.c` :938, :1563); `mf_wdecide` is pure per art |
| `MF_SITE_ABI` | U2 (25), review r5 X-1 (26), K38-2 (27) | 27 |
| `MF_CLASS_V` | K38-2 (`mf_class.run`) | 9 (`memfn.h` :1155) |
| `memfn/include/CLAUDE.md` :4 | none: left behind | STALE: it still says `MF_SITE_ABI` 25 and `MF_CLASS_V` 8 |
| G2's OFF-only window arts (`MF_P_PORTABLE_ONLY`) | U2 retired the bit | `g2_art_begin` states the portable target (`g2_win_gen.c` :111-118) |
| the derived run part (`derive_run_part`) | K38-2 | a FUNC part (nalt 0), not a window site; not in the agreement's population |
| `wf_parts_prepare` | K38-2 | calls `wf_prepare` once (`window.c` :2595); 3.0b keeps that call if F26's allocator stays on `wf_plan_site` |
| `fd_renderers`, the E-stmt pick map | 3.0a | gone into the search renderer table; `site_rec.fd_ren` and `select_arm`'s `*ren` already carry it |
| `MF_SITE_ABI` historical class | everyone | 354 lines in 79 files (304 in 71 at a678d0a4e, same grep) |
| line cites in 3.0b, §3, §4.1, §4.2 | many lanes | re-cited in place, or in §5 3.0b's re-base table |

The sabotage rows and ASK items are covered in the two sections below. K38-2's own witnesses (W-L1,
W-K1..W-K4b, EMIT-3) live in the G2 presence family, and no 3.0b row reads them. The 200 EMIT-3 in-run
sites under `run-tie-left` are window-family sites, so 3.0b's G2 agreement covers them if its generator
asks them framed. I added this point to the open questions below.

## 3.0b re-based

`plan_frame.md` §5 3.0b now opens with an `[s1d]` re-base block. It covers:

- ASK-2 void;
- ASK-6 new;
- the callers the signature change breaks, kit and pcrec;
- the unchanged `mf_wreply` layout;
- the lever as an art fact;
- `MF_SITE_ABI` 28 and `MF_CLASS_V` 9;
- the renumbered ids;
- what 3.0a's landing already provides (`fd_ren`, `wf_plan.strm`, `wf_plan_site`);
- the `wf_parts_prepare` contact;
- the Q15 (3) probe ruling, carried in (a successor probe under `docs/design/memfn/span_pick/`, not
  "left to break");
- a table of the §3/§4 cites that 3.0b reads, old cite against new.

Inline `[s1d]` re-cites:

- the rule-2 re-ask (now through `ask_sel`);
- the G2 `table_name` marker;
- R19's portable-target reason;
- the refusal text in (F);
- `fd_opt` (I);
- the gate comment (U);
- `wf_floor_uses` and `MF_MISS_N` (AD);
- the separability sentence (ASK-1/ASK-6);
- the concurrency paragraph (3.0b is the second lander; next number);
- the size (19 rows).

Row (AF) is written into §5, quoting Q14's ruling. §4.2 marks ASK-2 VOID and adds the ASK-6 row. §2.1's
run-window row is marked VOID. §3's number line points to the re-base block. The header points readers
to the block. Every prior ruling (r12, r13 R1-R28, Q13-Q15) stands, and nothing ruled was reworded.

## K38-3 re-based

The row in `span_runs_sheet.md` §5 records what K38-2 already delivered: layouts L and A on every target
pass, per-pass W-K4a floors, and per-pass SIMD census, with W-K4a and W-K4b GREEN and reaching. What is
left:

1. **Per-(level, layout) cells.** Today the negative-omin population and the SIMD-arm population are
   counted apart, so nothing shows that a w16 or w32 run part is ever called below its floor. The new
   cells are floored at the measured count, with no margin. The level list is read from `mf_levels()` and
   `mf_targets()`, not from the script's `TARGETS` literal. A level with no runnable target is a named
   failure, not a skip. If a cell measures 0, the generator is widened.
2. **The step-back card cell** (§5.2). It is a new append-only card row: the recommendation is a new
   quantity at ver 3 keyed `kind;entry;back`, so the planner's one METHOD_VER holds. The planner gets a
   line for the `back` dimension. The cell stays UNMEASURED; measuring it is a timing run in an
   owner-cleared window.

Plants:

- per level, a load UNALIGNED at `floor - 1`: W-K4a faults in layout L on that level's targets only;
- per level, a load ALIGNED DOWN from the floor: W-K4b, an ASan report in layout A;
- a coverage plant: drop x86-64-v3 from the pass list, and the coverage check goes red;
- a planner plant: remove the planner's `back` line, and the dry run refuses.

**Byte moves: none.** No `MF_SITE_ABI` move, no pcrec abi event, no `docs/spec/` hunk. I also corrected
the row's run-record cite: it is span_cards.md §3.5, not §4 (§4 is the noise channel).

**Separability and order.** 3.0b and K38-3 are separable. They touch disjoint files:

- K38-3: the G2 presence family, `memfn/data/cards/`, and the S2c planner;
- 3.0b: `window.c`, `compose.c`, `kit.h`, `memfn.h`, `emit_dfa.c`, the window-family G2, and the purity
  harness.

Neither moves a number the other reads. Recommended order: K38-3 first (size S, zero-mover, and it closes
R-38), or the two in parallel lanes.

## Sabotage fates and numbers

- **3.0b's planned ids S2994-S3012 are all taken on main:**
  - S2994-S3004: the target seam (U2, u2fix, u2c4, xarch);
  - S3005-S3006: K38-1;
  - S3007-S3012: K38-2a.
- **Which ids the K38-2 lanes took.** The brief names S2994-S3011, but K38-2 itself took S3040-S3042 and
  S3060-S3064, from its reserved range S3040-S3069; the earlier numbers belong to the lanes above.
- **Highest id on any local branch:** S3077 (lane/rpfix, S3074-S3077, unmerged). S3070-S3073 is s1fix's
  reservation in the manager's ledger.
- **3.0b's 19 rows** are expected as S3078-S3096, in the order E, E2, F, G, H, I, J, S, T, U, V, X, Y, Z,
  AA, AB, AC, AD, AF. They are re-taken at build time, ledger first.
- **Existing sabotages 3.0b moves:**
  - S686: its anchors still match `ofsskip.c`'s `fn_rows` BODY lines (:414-415). The re-aim moves with the
    pick column, as R9 ruled.
  - S2903 and S1089: their anchor texts are unchanged (S2903's is at `compose.c` :898).
  - K38-2's retired rows (S1543-S1548, S449) are none of 3.0b's.
- **K38-3:** its ids are not reserved yet. It takes its ids from the free range at build time; it has no
  existing sabotages to move.

## MF_SITE_ABI

27 at 35bee4da9: 25 from U2, 26 from review r5 X-1, 27 from K38-2. 3.0b takes the next number at landing,
which is 28 if nothing lands first. The readers were re-grepped:

- **Symbolic readers:** listed in the re-base table. Three files are new since a678d0a4e:
  `g2_pres_gen.c`, `tests/memfn/policy_check.c` and `tests/memfn/run_decide_check.c`. They need a
  recompile only.
- **Historical class:** 354 lines in 79 files.
- **Literal pins:** still none.
- **Prose:** `memfn/include/CLAUDE.md` :4 is already stale; it still says 25 and `MF_CLASS_V` 8. 3.0b's
  ledger line must write the new number and 9. The kit may want to fix the line before then.

`MF_CLASS_V` stays at 9 through 3.0b. K38-3 moves no number.

## Open questions

1. **Lever arm in `reach_equal.py` (kit manager).** Should `--harness=run-tie-left` join `reach_equal.py`'s
   `--arms` for 3.0b's corpus agreement? The decision now reads the lever, so that arm is where
   lever-moved decisions get compared. Recommendation: yes. It costs one more arm in an existing
   boxqueue job.
2. **Stale CLAUDE.md line (kit manager).** Fix `memfn/include/CLAUDE.md` :4 (stale since U2's fixes and
   K38-2) now, or leave it for 3.0b's ledger line? Recommendation: now, as one doc line, so the line 3.0b
   edits starts correct.
3. **Card row shape (kit manager).** K38-3's card cell: a new quantity at ver 3, or `enter` at a new
   version? Recommendation: a new quantity, which keeps the planner's single METHOD_VER.
4. **ASK-6's place in R-35 (main).** ASK-6 is a pcrec hunk that R-35's (a) package did not name. Main
   files it as part of 3.0b's pcrec asks, or rules otherwise. Recommendation: file it with ASK-1/ASK-3-5.
   It is the same kind of edit ASK-2 was.

Outside this lane's scope, left as found: `plan_frame.md` §6 still cites "ASK-2's existing loud check",
and §7 Q1 still asks about `req_run_member`. Both now have no subject, as the re-base block says.

## Charter-vs-committed checklist

| brief item | done | where |
|---|---|---|
| read BOILERPLATE.md and memfn/CLAUDE.md first | yes | (process) |
| 1. list what K38-2 moved under 3.0b, grep every cite, check S2994-S3011 against tests/mech/sabotages | yes | "What K38-2 moved under 3.0b", "Sabotage fates and numbers" |
| 2. revise §5 3.0b in place: ASK-2 void (why), next MF_SITE_ABI, sabotage rows renumbered, K38-2's readers, prior rulings kept, `[s1d]` marks | yes | `plan_frame.md` §5 3.0b re-base block and inline `[s1d]`; pointers in header, §2.1, §3, §4.2 |
| 3. K38-3 re-based: card cell (run record), W-K4a/W-K4b over every admitted level, its plant, byte move | yes | `span_runs_sheet.md` §5 K38-3 row; "K38-3 re-based" |
| 4. separable? order | yes | span_runs_sheet §5 Order `[s1d]`; "K38-3 re-based" |
| span_runs_sheet: only the K38-3 row and the Order paragraph | yes | the diff touches those two places only |
| did not touch part_d.md; no code under memfn/src or src/; no suites, no queue jobs, no monread | yes | (process) |
| report sections per deliver file; `OWED:` line; cites by section/[TAG] | yes | this file |
