# Lane r45b report — R-45 reply rev 2 (applies design review r20 as ruled)

Lane r45b (opus, design only), on branch `lane/memfn-r45` in `worktrees/r45`, from tip 280082b45
(lane r45's rev 1), 2026-11-16. The deliverable is `docs/design/memfn/r45_reply.md` rev 2; its §8
is a block ready for `responses.md`, for the kit manager to post.

What this lane did and did not do:
- No code changed. Nothing was timed, no box job ran, and `make` was not run.
- One `sizeof` probe was compiled with plain gcc in lane scratch:
  `/var/tmp/pcrec-pcrec/scratch/memfn/r45b/sz2.c`.
- The review (`review.md` and its `review/` directory) was filed unchanged as
  `docs/dev/reviews/2026-11-16-r20-memfn-r45.md` (+ dir) and indexed in
  `docs/dev/reviews/CLAUDE.md`. `grep -nE 'plan\.md:[0-9]'` over both finds nothing.

## Summary

- **Every r20 finding is answered in the text.** F1-F18 are fixed, F19-F20 are doc fixes, and
  F14's PLAN row is stated in §3 for main to file. The reply opens with a "Changes from rev 1"
  table by finding id.
- **The proof range (F1, F2).**
  - It is `[MF_PROOF_LO, end)` with `end = max(last stated + 2, last tested + 1)`, clipped at
    `MF_MAX_FWD`, so it always reaches offset `k`, whether or not the after side is stated.
  - A tested offset outside the range is a kit REFUSAL, never clipped. An over-read at the
    first offset past the statement lands in B5's view.
- **Where the rows live (F3).** CALLER-SUPPLIED storage, chosen over an arena parameter, which
  is a callback and fails seam principle 9:
  - a new `mf_rows` parameter on `mf_ask` and `mf_wdecide`;
  - a pure `mf_rows_need(site)` that sizes it from the statement.
  The asks stay pure. The define side keeps using the art's existing arena. All of this is
  inside `MF_SITE_ABI` 29 -> 30.
- **Readers (F4-F6), found by grep at main.**
  - One deep-compare rule.
  - 17 compare sites. Five were not in r20's list: `g2_win_gen.c:1358`, `arm_fixtures.c:432`,
    `d27_frame.c:1028/1050/1052/1105`.
  - The count-bounded loops, every `proven[]` reader, five plants, the `mf_wspan` host-storage
    rule (const members, so writers fail to compile), and 14 silent `(uint8_t)` casts.
- **The default form (F11-F13).**
  - A COMBINING rule: the default is H(h\*); h\* is the grid value with the smallest worst-cell
    slowdown, ties going to the smaller head; the grid includes 0 (L) and `>= k` (I).
  - Cells where I wins are dial evidence.
  - h is a kit constant, independent of pcrec's width default. The cards run first on the same
    frozen binary, and then the width cells (ruling R1, settled with main).
  - Plans A and B go to the owner in plain words; the kit recommends A.
  - "Zero movers at 32" becomes a stability trade offered to the owner.
  - The interim UNMEASURED h = 32 is withdrawn: no outcome ships an unmeasured h.
- **Forms over the existing segmenter (F14).** C-run's `find_groups` gains segment kinds, so
  `lit-l40` stays one run compare in every form.
- **The near-miss skip (F15)** follows D77 strictly: it is D-hors generalised to every offset,
  triggered by C1's near-miss column.
- **Witnesses (F7-F10).**
  - S526 stays on `MF_MAX_TERM`, DETECTED by C14's stride clause.
  - B2's control is cover_cap.md §11.6.3's reference compile.
  - Two rows for the proof-range defence.
  - G2's twins are asserted, with the long cases as their own rows.
  - The PAIR row's readers are named: registry floor 13 -> 14, `memfn_arm.py`, and a force cell.

## Fixes by id

| id | disposition | fix in rev 2 | section |
|---|---|---|---|
| F1 | FIX-NOW | `end >= last_s + 2`: one past the statement, always reaching `k`; no REPORT clause; pcrec need not state an empty after span | §1 |
| F2 | FIX-NOW | range sized from stated AND tested offsets; tested outside `[MF_PROOF_LO, MF_MAX_FWD)` or past the caller's caps is a refusal; "by construction" restated as a kit promise B5 checks | §1 |
| F3 | FIX-NOW | caller-supplied `mf_rows` + pure `mf_rows_need`; arena parameter rejected (principle 9: a callback), art allocation rejected (breaks PURE); every caller listed with `file:line`; S3045/S3064/S3097 re-anchored; abi inside 29 -> 30 | §5 "Where the rows live" |
| F4 | FIX-NOW | deep-compare rule; 17 compare sites and the count-bounded loops by `file:line`; a NONE ask leaves `plan_test` NULL | §5 (a), (b) |
| F5 | FIX-NOW | every `proven[]` reader (kit, pcrec, tests) and the plants S1224 (+ `run_proof.sh:45`), S1083, S1407, S1221's REACH, S526, S1131 | §5 (c), (d) |
| F6 | FIX-NOW | host-storage rule (writer owns storage, `pcrec_memfn_wspan` gains the `Ctx`, const members make every writer a compile error); 14 silent casts listed; `window.c:3017` truncates today | §5 (e), (f) |
| F7 | FIX-NOW | S526 back to its pre-k382mech shape, with a new REACH; B2 via §11.6.3; any 4094 plant a NEW row after B2; `emit_dfa.c:1446`'s lost witness named | §2 |
| F8 | FIX-NOW | (a) kit row: refusal by its message; (b) pcrec mech row: plant + `SAB_FILE2` bypass, B5's text | §1, §6 |
| F9 | FIX-NOW | `G2W_MAXPOS` 64 / `G2W_REACH` 128 / `G2P_MAXRUN` 64 (CHOSEN), each `_Static_assert`ed against the kit name; 500/4095 as own rows; readers listed; runtime priced (UNMEASURED estimate, plus a record and a split rule) | §3 "Answers" |
| F10 | FIX-NOW | registry.md §6¶8a sentence, §6¶8b floor 13 -> 14, `memfn_arm.py:346-349` class entry, `:452-460` plus a force cell; force spelling = L | §3 "The option" |
| F11 | FIX-NOW (ruled) | combining table R0-R3; tie-break declared; grid includes 0 and `>= k`; the four r20 drills re-run in the text; stability trade in plain words | §3, Goals 3-4 |
| F12 | FIX-NOW (ruled) | h independent of the width default; order SETTLED with main per ruling R1: form cards first on the same frozen binary with h's rule committed before the run, h frozen, then the width cells (one night if both fit, else two) | §3, §7 "Answered" |
| F13 | FIX-NOW (ruled) | plans A and B in plain words; kit recommends A, with reasons; B's lower cost stated; A falls back to B's shape, never to an unmeasured h | §3 "Scope", §7 |
| F14 | FIX-NOW + PLAN | L/H over `find_groups` with segment kinds; PLAN row "SHARED SEGMENTER ... TRIGGER: the first build of L" stated for main to file; the other unlocks with triggers | §3 "The forms" |
| F15 | FIX-NOW | no skip in the first build; trigger = C1's near-miss column / §11.4 row 5; the fix = generalised D-hors, one answer to §11.2's EMITTED-2 order; spec hunk names the slow regime | §4, §7 |
| F16 | FIX-NOW | grid labelled UNMEASURED; `WF_LEGACY_POS` 32 DERIVED; `MF_WMAX_SPAN` = derived 25 + UNMEASURED slack 7; 36 DERIVED (census); G2 lengths CHOSEN; "about 32" withdrawn from the owner's words | throughout |
| F17 | FIX-NOW (ruled) | build starts from main; cites carry symbols; old Q4 answered (retire now); mfind caveat (g) and doc readers (h) listed | header, §1, §5 |
| F18 | FIX-NOW | fallback withdrawn: the kit branch merges only onto A1 | header, §1 |
| F19 | DOC | about 12 `mf_wreply` holders (`UnanchStart` sites + `rus = us` + 2 locals), each -396 B; arena per compile, summed over attempts | §5 "Stack and arena" |
| F20 | DOC | 528 tests per 32 bytes, 16.5 per byte, the failing test counted; ~2,048 per byte at 4095 | §4 |

Sizes restated in rev 2, re-probed (`sz2.c`): class 2,932 -> 1,640 B; result 3,000 -> 1,712 B;
`mf_wspan` 1,164 -> 32 B; `mf_wreply` 532 -> 136 B; `mf_run_reply` 4 -> 8 B (all four `uint16_t`); 8
classes 23,456 -> 13,120 B.

Proof rows by `k` (from `proof_n` of 33-34, 41-42, 509-510 and 4104):

| `k` | rows |
|---|---|
| 24 | 1,056-1,088 B |
| 32 | 1,312-1,344 B |
| 500 | 16,288-16,320 B |
| 4095 | 131,328 B |

Plan lists take 7 B per entry, 28,728 B at 4095.

## Open questions

Each is for main unless it says the owner; each carries a recommendation in the reply's §7 and §8.
- **pcrec's other window sites.** Should they stay at 32 positions by pcrec's own assertions?
  Recommend yes.
- **For the owner: plan A or plan B.** A: forms built, measured before the landing, and shipped
  as his stated default. B: long spans all-inline now, forms next, cheaper. Recommend A.
  Inside A: keep spans of 32 or fewer unchanged as a stability trade? Recommend no.
- **The order of the timings** is no longer open: it was settled with main by ruling R1 and
  stated in the reply as settled (§3, §7 "Answered").
- **For the owner: the dense near-miss fix.** Should the first build carry it? Recommend no
  (D77) until a timed card shows the loss.
- **Caller storage.** May the asks take caller-supplied storage for their lists (one new
  parameter, plus a pure sizing function)? Recommend yes.
- **Memory.** Is about 160 KB of rows per ask of a 4095 cover, kept per compile, acceptable
  until the compile-cost record? Recommend yes.

## STATE AT HANDOFF

- STATE: done. Design only. Branch `lane/memfn-r45`, all work committed.
- Rulings file `docs/dev/lanes/r45b_rulings.md`: R1 arrived before the report's final check
  (F12's night order, settled with main). It is applied in §3, §7 and §8. Last entry applied:
  R1.
- Next step: the short re-check round r20 recommends (premise + owner criteria) on rev 2,
  then the kit manager posts §8.
- Not checked by this lane: whether pcrec's B5 (on `lane/covs2afix` or later) already
  implements cover_cap.md's rule. Rev 2's range rule satisfies B5 as written in cover_cap.md
  §11.1.
- OWED: none.
