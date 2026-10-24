# 2026-10-24 r1 — memfn-s3-final (code): D172 S3, REPORT routed by default, PAIR widened

DRAFT by the coordinator, with PROPOSED dispositions. The manager rules them.

## Subject

- SUBJECT `cc4f54eb296f035e0e5d9863c680a69721a64875` (lane/memfn-s3pair), BASE `0d3765c87ae412f9a99dc0df1ea56250d6943a55`
  (git merge-base with main; main tip 1030ef437 has the same product source).
- What it does: the `cover` LOCATE row admits on the default build (`RX_DFA_SCAN "cover"`), and the kit's window family
  renders the REPORT search: E-find, Table B through `fd_find` (PAIR widened to any two-byte stop), B's renderers,
  Table D with D-hors. abi 84 -> 85. Design: window_site.md rev 3.3 DRAFT (rev 3.2 is the design of record).
- Compilers: SUBJECT = a byte copy of the lane worktree's clean build at SUBJECT (sha256 5574edea..., newer than every
  source). The review tree's own build was queued under `scripts/boxlock run` but never got the lock (job 620 held
  the box the whole time) and was cancelled unrun. BASE = a copy of main's build (product source identical to BASE,
  emits abi 84).
- Critics read the review tree `worktrees/crit-memfn-s3-final` (removed at the end). Nobody ran make or a suite.

## Lenses as run

| lens | model | its one question | why chosen |
|---|---|---|---|
| emitted vs replaced | opus | C + asm of the cover path vs BASE and the OFF arm; every pre-existing entry diffed; what is worse? | the subject changes emitted C on the default build |
| contract | opus | does the code do what the spec hunks say for every admitted input; do names describe behaviour? | new stamp value, two new denies, four spec hunks |
| slot tracing + ruling check + goals + previous findings + the two standing questions | opus | every slot traced to its table; rulings and their consequences; ranked goals served in order; r1/r2 findings fixed? | Tables B/D/E and the FIND slot changed; rev 3.3 DRAFT rulings; two earlier rounds |
| check adequacy + trade audit (folded) | sonnet | per new/changed/deleted check: what makes it fail, does a witness reach; per moved pin: what was given up, who judged | about 60 test files, 7 sabotages deleted, many re-pins |
| house rules | sonnet | coding.md / style.md / addenda/kit.md at function level | window.c +1185 lines |

Trade audit was folded into check adequacy to stay at 5 critics. One verifier (sonnet) re-ran every CONFIRMED finding
that would change code or a design (`review/verify.md`).

## Which lens caught what

- Every speed finding came from **emitted vs replaced** (EMIT-1..4); slot tracing found EMIT-4 independently from the
  design side (SLOT-1). Contract and slot together found every doc/contract finding. House and slot overlapped on
  renderer duplication and row actions. Check adequacy found the one check that misreads the new default form (CHECK-1).
- **Answers: no finding.** About 5M differential cases against libpcre2-8 (emit about 2.0M, contract about 4.0M incl.
  find-all, utf8, SIMD block edges, ASan exact-size subjects, every `search_from`; slot 93k), 0 differences on DFA
  artifacts and no out-of-bounds read.

## Findings and PROPOSED dispositions

### Speed

| id | finding | verified | proposed | reason |
|---|---|---|---|---|
| **EMIT-1** | PAIR's two `memchr` streams restart on every `rx_search` call. When one byte is absent or far away, each call scans to `n`, so find-all is O(n x matches). `(?i)xq`: BASE 7.8, SUBJECT 3175 instr/byte at 4 MiB (BASE and OFF linear). `x[Q%]y`: 3.1 vs 3124. BASE already had this on the `(?i)` literal fn-pair arm (`(?i)hello` 3032 instr/byte); S3 makes it the default for every PAIR stop. | HOLDS (verify.md) | **FIX-NOW** | an unbounded Goal-2 loss on the default build, in the shared renderer `ofs_pair_text`. One fix serves the pre-existing case too, e.g. search the second stream only up to the first stream's hit. If no bounded form is ready, narrow PAIR back to the pre-widening scope until there is one. SIMD-on escapes it. |
| **EMIT-4 = SLOT-1** | A-mass picks the rarest core position whatever it costs to find. A 3+-member set stop takes the byte walk where BASE ran `memchr` on a one-byte position. Real text (dev_journal, find-all): `[<>&]x` 0.62 -> 11.3 instr/byte (18x), `[xqz]ab` 0.91 -> 12.3 (13.6x), `[.,;]\d` 6.9 -> 11.4, `[QXZ]{2}` 6.3 -> 11.3. | HOLDS | **FIX-NOW (needs a ruling)** | Goal 2 outranks the Non-goal "Table A ranks by mass alone" ([MEMFN-PAIRSTOP]). The bar's sample does not contain a set-led window, so the bar cannot see this. Smallest repair: E-find declines (cover falls back to composite, the BASE text) when B's pick is the walk and some core position is one byte. The priced stop x method choice stays [MEMFN-PAIRSTOP]. This conflicts with the design's Non-goal, so the manager rules. |
| EMIT-3 | A stop below the candidate re-clamps `c` and re-tests `c >= 1` on every iteration; gcc keeps both. Hoisting saves 17% instr on `(?<=x)foo` candidate-dense text. | HOLDS | FIX-NOW if EMIT-1/4 reopen the bytes, else PLAN | S effort. It moves bytes inside abi 85, which has not landed, so re-pins only and no new bump. |
| EMIT-2 | After a failed verify, D-hors shifts by 1. Adversarial `[0-9a-f]{8}` over `aaaaaa-`: 12.1 -> 20.0 instr/byte (1.66x). On real text it is a 4x win. The `_sh` table is constant on uniform-class windows. | HOLDS (adversarial only) | PLAN | worst case only; a right-to-left verify skip is the repair. |
| SLOT-4 | Common two-byte stops on PAIR were suspected slow. | REFUTED on instruction counts (`[st][hr]` 17.4M -> 10.2M, all four cells fewer) | NOTED, plus PLAN: one common-pair cell in the bar's sample | instructions under-count libc call cost; one timed cell would settle it. |

### Contract and doc (D80: the spec is the contract, so it must be right before landing)

| id | finding | verified | proposed |
|---|---|---|---|
| CONTRACT-1 | `_DFA_PREFILTER` / `rx_info.prefilter` read `"none"` on every cover artifact. §6.3.4¶3 defines `"none"` as "every position is a candidate", which is false here. | HOLDS | FIX-NOW (a ¶3 cover clause, like ¶8's) |
| CONTRACT-2 = EMIT-5 | `REQ_WHY "dominated"` now comes from cover. The spec lists only `rev-end`/`empty` (match_api ~2370, tuning §2.29¶5), and the text claims a memchr that a walk-stop artifact does not have. `_REQ_RUN @idx` names a member no memchr scans. | HOLDS | FIX-NOW (spec text) |
| CONTRACT-3 | tuning §2.47¶2 and match_api §3.1¶21 (the hunk's own paragraph) give `abcd`, `a|b`, `[a-z]` as end-minus-width witnesses; all three are cover now. | HOLDS | FIX-NOW |
| CONTRACT-4 | tuning §3's `_DFA_SCAN` value list omits `"cover"`. | read | FIX-NOW |
| CONTRACT-5 | tuning §2.46¶4 says "the denied build reads unanchored"; a `\z`-ended window reads `"cover"` under `-fno-rev-end`. | HOLDS | FIX-NOW |
| CONTRACT-6 | `--list-axes` `.desc` for `attempt-start` and `dominated` omits cover (product strings, not emitted, no abi). registry §6¶3a does not list cover as a second row with no pcrec deny. | read | FIX-NOW |
| CONTRACT-7 = SLOT-9 | D174, in force since 2026-10-22: the new prose names `S3`, `C8`, `cover_conj` and a kit source file; the new names `wf-find`, `wf-hors` and the stamp value `"cover"` are family letters, mechanism or proof terms. | read | prose FIX-NOW. Names are the manager's call; leaning: rename `wf-*` before landing (nothing has shipped), and file `"cover"` under [IFACE-PUSH] |
| SLOT-5 | kit_proof.md (the design of record for `cover`) still says B1 lands `-fno-kit-proof` and a `kit-proof` listing; S3 built neither and revised nothing. Consequence: the cover row has no pcrec-side identity, and C13's `refused` cannot tell a deny from a decline. | read | DOC (revise kit_proof.md in the landing) |
| SLOT-6, HOUSE-9 | Stale text: PAIR is still a "cube stop" with a "stretch" (memfn/src/CLAUDE.md:15, finder.c:33, :314); `kind_cl`'s KD_ALL comment is wrong; `wf_plan_brow`'s header contradicts kit.h:833; `window_reply_ask` says "previews"; index lines cite rev 3.2. | read | DOC (FIX-NOW, comments only) |
| SLOT-7 | The Goals' strict ranking is contradicted by the subject's own ruled trades: the hex8 cap lets Goal 4 win over Goal 2, and the mass-only non-goal lets Goal 3 win over Goal 2. | read | DOC (at rev 3.3 acceptance: say which wins qualify for a cap, and list the populations outside Goal 2's sample) |

**Ruling precondition (slot Q2 a):** the code and the spec hunks implement rev 3.3, which is marked "NOT YET ACCEPTED".
Accepting rev 3.3 is a precondition of the merge, not a follow-up.

### Maintenance (structure)

| id | finding | verified | proposed |
|---|---|---|---|
| SLOT-2 (+HOUSE-12) | "Rows carry their own actions" holds for Table D only. E and B renderer row ids are tested outside the walk at 8 lines (window.c 1771, 1839, 1843, 1848, 1850, 2611, 2619, 2644). `wf_b_text` and `wf_d_text` are parallel arrays. | HOLDS | PLAN (D's row-struct form for E and B; trigger: the next E or B row) |
| SLOT-3 (+HOUSE-10, HOUSE-13's `two()`/`shape()`) | One-stream memchr has 3 renderers (pffind, ofsskip fn-memchr, B-memchr) and the set walk has 2: the third member of a family. | read | PLAN (an `ofs_stream` primitive; trigger: the next edit of any copy, or the SIMD thread picking up R2-3) |
| SLOT-8 | On B-fn sites the FIND slot picks PAIR and then fn_rows' BODY slot decides again. They agree by construction, and nothing checks it. | HOLDS (reading) | PLAN, plus a cheap self-check (BODY pick == FIND pick) FIX-NOW |
| HOUSE-1 | `pcrec_fact_span` has no caller left. | HOLDS | FIX-NOW (delete) |
| HOUSE-6 | The "is a window site" test is spelled 3 ways; the new gate.c:476 one omits `wfloor`. | HOLDS (spelling; defect not shown) | FIX-NOW (one helper, S) |
| HOUSE-7 | `d_hors_head` voids its `bound` and prints `C + chi >= N`. | HOLDS | bundle with EMIT-3 (byte move), else PLAN |
| HOUSE-2 (= r1 C16) | The kit-proof lever is inert and is pointed at by a lane report. | read | DOC (point at a plan row, not a lane report); retirement stays filed |
| HOUSE-3 | `fd_find` duplicates `fd_route`'s setup and decide. | read | PLAN |
| HOUSE-4, HOUSE-14 (r1 C14 remainder) | `b_fn_holds` and `e_legacy_holds` write state; `wf_find_decide` runs twice per define. | read | PLAN (compute before the walk, as Table D does) |
| HOUSE-5 (= r1 C5) | REPORT is keyed in predicates instead of contract columns. | read | NOTED (filed as C5) |
| HOUSE-8 | Comments narrate history and cite review ids a reader cannot follow. | read | DOC (FIX-NOW, comments only) |
| HOUSE-11 | `ofs_pair` carries layout strings. | judgment | NOTED |

### Checks and trades

| id | finding | verified | proposed |
|---|---|---|---|
| **CHECK-1** | `cover_pick` (run_encoding_checks.sh DD12a) reads 0 clauses on the B-fn shape, the default for caseless runs: `(?i)foobar` byte and utf8 both give `[]`, and their stamps differ. Any corpus pair of that shape is either RED ("carries 0 search clause(s)") or a silent gap. | HOLDS (extracted reader); suite effect NOT VERIFIED | FIX-NOW (teach the reader the helper's body). **Manager: check job 620's DD12a section for this red.** |
| CHECK-2 | D-hors's `whi >= 0` condition has no plant and no census cell for the intersection (hors with the window below the candidate). | SUSPECTED | FIX-NOW (one plant, S; a miss would be an over-read) |
| CHECK-5 | PAIR's widening has no direct witness: rows.tsv witnesses a cube, and row_floors has `fd PAIR PLACEHOLDER`. g2's reach counters are substring heuristics. | read | FIX-NOW (a non-cube witness such as `x[Q%]y`, and real floors) |
| CHECK-3 | The `wf-find`/`wf-hors` axis classes carry no floors ("owed"). | read | PLAN (a plan row, owner) |
| CHECK-4 | About 50 re-aimed checks rest on "the OFF arm IS the build before S3", and nothing pins that equality (held by three critics' sweeps: 36, 54+6 and 15 compiles, 0 differences). `run_cand_oracle`'s shipped-declines check now has population 0. | partly | PLAN (a pinned OFF-arm manifest) |
| CHECK-6 | proof_check.c lost the REPORT `proven[] == REQUIRED` equality. G2 holds soundness only, so under-proving is unobserved. | SUSPECTED | PLAN |
| CHECK-7 | Trade audit. Every moved pin has a recorded reason, but several are judged by the LANE only: the SIMD-on re-pins ("a JUDGED trade"), the DIFFER pins 513->328 etc., FLOOR_EMW 1124->510, S283 flipped to UNDETECTED. | read | NOTED; the manager ratifies these trades by name in the ruling |
| CHECK-8 | S1251-S1256, S922, ZK6/ZK7 were deleted with their mechanisms. "No row decides before its step" has no successor (no held rows exist today). | read | NOTED |

## Previous findings (slot lens, full tables in review/critic_slot.md Q4)

- r1: FIXED C1, C3, C7, C9, C13; PARTLY C2, C10, C14, C15, C17; DRAFT-only C4; OPEN as filed C5, C6, C8 (now SLOT-1 =
  EMIT-4), C12, C16; C11 not verifiable (its code sits under the denied s3_evidence).
- r2: FIXED R2-4, R2-5 (prose), R2-6, R2-7 (Table D only), R2-9, R2-10 (DRAFT); R2-1 fixed for two bytes; OPEN as
  planned R2-2, R2-3 (`\b(?i:foobar)\b -fmemfn-simd` SUBJECT `"none"` vs BASE `vrun@w32+w16`), R2-8, R2-12. The r2 slot
  critic's F4, F5, F10, F11, F12 are all still open.

## PROBED-AND-HELD (consolidated)

- Answers: about 5M (subject, search_from) cases vs libpcre2-8 across byte, utf8, -fmemfn-simd (SSE2, AVX2), every deny,
  tune, no-captures, find-all, `rx_search_in`, NUL bytes, ASan exact-size subjects: 0 differences, 0 OOB.
- OFF arm (`--memfn=no-wf-find[,no-wf-hors]`) == BASE but for abi digits and file name: emit 83, slot 60, contract 15,
  checks 36 artifacts: 0 differences. Non-cover artifacts: 0 byte moves (175 sampled corpus patterns: only the 30
  cover artifacts move). `no-wf-hors` moves exactly the `_sh` artifacts. SIMD-on = SIMD-off plus guarded rungs.
- Pre-existing entries (rx_match*, the iterator, rx_next_pos, rx_valid_upto, rx_info's other fields) byte-identical on
  21 cover artifacts. Size: text+rodata smaller on all 21. Real text: SUBJECT <= BASE on 31 of 38 cover patterns (hex8
  9.9 -> 2.2 instr/byte, `(?i)xq` 6.2 -> 0.3); the losses are EMIT-4's walk sites.
- Stamps on cover artifacts: SCAN, START, TABLE, UNIFORM_FOLDS <= 2, SCAN_EDGE, MEMFN_LIBC as specified, except
  CONTRACT-1/2. Declines held: a 2+-byte stop below the start is `"unanchored"`. Listing: locate rows 1/2/3, memfn floor 14.
- House: abi bump in the same diff; no stale references to retired symbols; new Table D predicates are pure; no float.

## D27

Not recommended for this subject. The contract (a fixed-width window, leftmost, `[c, c+k)`) was exercised by about 5M
differential cases written from the spec, not the code, and found nothing. The gap is speed, which a D27 author does
not test.

## Lessons for the guide (proposed)

1. **A default-route change gets a find-all, real-text instruction sweep per new renderer** in the emitted-vs-replaced
   lens. Both large speed losses (EMIT-1, EMIT-4) were invisible to the stated bar: its sample held no set-led window
   and, as far as the critics could see, no find-all over a subject missing one pair byte. That is a population nobody
   counts (K35) at the bar. Proposed for critics.md: "for a change that alters the DEFAULT search, the emitted lens
   runs find-all over one real text and one adversarial text per new find form, BASE vs SUBJECT, by instruction count."
2. **A new stamp VALUE is a D94-style reader hunt.** CONTRACT-2..6 are closed enumerations and witness lists that the
   hunks did not touch. Proposed for coding.md / the abi row: "adding a value to a stamp or a row to a selection: grep
   every enumeration of that stamp's values and every witness sentence of the rows it now pre-empts."

## Rulings (the kit manager, 2026-10-24, with Frank's rulings quoted)

The coordinator's PROPOSED dispositions stand except where listed here.
- **EMIT-4 = SLOT-1: PLAN, no stopgap.** Frank: "no. Leave the wart. Its fix is the test for pricing." The witnesses are D176's acceptance cells (stop_ranking_study.md §5.1, lane/memfn-stopstudy fc6735cdf). Rev 3.3 lists them as a known gap under Goal 2.
- **The bar (SLOT-7, the hex8/foobar caps): FIX-NOW (doc).** Frank: no per-pattern passes. Goal 2 is "no slower than DEF beyond the relative floor or a MEASURED per-call layout allowance (ns per call)". Job 588 measures it from layout variants of the DEF arm, and every named cap is deleted. Dense-hex SKIP (hex8 throughput/dense 1.543x) becomes a known gap and a D176 witness (Frank: "Add hex case to the pricing tests").
- **CONTRACT-7 = SLOT-9: FIX-NOW, rename.** Frank: "rename". The deny rows `wf-find`/`wf-hors` take behaviour names (D174). The stamp value `"cover"` is filed under [IFACE-PUSH]. The prose is cleaned as proposed.
- **EMIT-1: FIX-NOW.** The kit's call: bound each PAIR stream's look-ahead per call, so find-all stays linear. One renderer serves fn-pair too.
- **EMIT-3 and HOUSE-7: FIX-NOW.** EMIT-1 reopens the bytes inside abi 85 (not yet landed: re-pins only, no new bump).
- **CHECK-7: ratified by name.** The SIMD-on re-pins, DIFFER pins, FLOOR_EMW and S283 to UNDETECTED were each judged with a recorded cause. The manager accepts them as trades.
- **SLOT-5: FIX-NOW (doc)** in the fix lane: revise kit_proof.md where S3 superseded it.
- **Rev 3.3: accepted** once the fix lane's edits land (Goal 2 reworded, known gaps listed, ranking exceptions none).
- **Process changes:** both accepted. Launch critics UNNAMED (a teammate coordinator cannot name its spawns, and the final replies were lost). In code mode, use a clean-build copy of the subject commit FIRST when the box is held: the boxlock build waited 27 minutes and never ran.

Completeness: EMIT-1..5, CONTRACT-1..7, SLOT-1..9, HOUSE-1..14 and CHECK-1..8 each carry a disposition, the coordinator's or the ruling above.
