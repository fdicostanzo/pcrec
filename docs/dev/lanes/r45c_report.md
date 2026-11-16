# Lane r45c report: R-45 reply rev 3 (applies re-check review r22 as ruled)

Lane r45c (opus), 2026-11-16, DESIGN ONLY: no code, no timing, no box jobs, no build.
Worktree `worktrees/r45`, branch `lane/memfn-r45` (started at 501937519).

## Summary

- Filed the ruled review r22 verbatim as `docs/dev/reviews/2026-11-16-r22-memfn-r45b.md` (+ its
  `review/` dir: `fixind.md`, `owner.md`, `fixind_vm_probe.c`) and indexed it in
  `docs/dev/reviews/CLAUDE.md`. r22 is free on main for 2026-11-16 (main has only r19 that day;
  r20 is this branch's, r21 is on `lane/memfn-d3wire`).
- Revised `docs/design/memfn/r45_reply.md` to rev 3. New "Changes in rev 3" table, by r22
  finding id (F1-F18 plus the FREEZE NOTE). FIX-NOW F1-F15 and F16(a) are applied; F16(b)(c),
  F17 and F18 are applied as DOC.
- Rewritten whole: §1 "The proof range", §3 (forms, head and rule, drills, scope, cards, head
  lever, G2, option, night order), §6, §7 and §8. §5 got additions (define side, internal
  producers, the list family, callers, compare count, holders, arena price).
- Re-counted at origin/main 56c315567 (fetched; its code is byte-identical to the reply's tree
  ea83fbc01): the d27 whole-reply compares (4 added, 22 total), `probe.c:101`, the G2 REPORT
  draw (`g2_win_gen.c:433`), `G2W_NOFF` and its holders, `kit_opt_denied`'s callers,
  `formhash.c`'s `fh_work`, `g2_win_gen.c:1145/:1290`, `cover_window` at `known.c:583`, and the
  lever plumbing (`memfn.h:1596-1617`, `internal.h`, `memfn_sites.c:210-226`).
- One correction to r22's text: `g2_win_gen.c:1145` copies into G2's OWN `g2w_reply` (fixed
  `G2W_NOFF` arrays), not through a const `mf_wreply` member. Rev 3 lists it as a holder sized
  by `G2W_NOFF` that the long rows outgrow.
- One correction to rev 2 that r22 did not name: rev 2 set `G2W_MAXPOS` to 64 and called that
  "twice the grid's largest finite h", but the grid's largest finite h is 64. Rev 3 uses 128.
  This matters more now that ties go to the largest h.
- §8 is 33 lines. Its open questions are in plain words, each with a slug and a leaning. It
  states that plan B alone is ready now with text fixes.

## Fixes by id

| id | fix | where |
|---|---|---|
| F1 | Three kit refusals declared: R-out, R-cap and R-short. R-short is the range self-check, shares its source with `end`, and runs on both paths. Row (a) reads its message through `mf_define`. Row (b) runs on an after-unstated cover (`[0-9a-f]{40}`), and its REACH asserts that no after span is stated | §1 |
| F2 | RULED (i): the cover ask passes storage up to `MF_MAX_FWD` (4,104 rows), stated as the kit's proposal for main to confirm. The "lands inside the range" sentence is corrected to depend on the storage | §1, §5, §7 |
| F3 | Rows only for PROVING classes (window plan classes, old-field FIND). Every other class has `proof_n` 0, so the 5000-byte VM run renders as today. The `MF_MAX_FWD` derivation is scoped. Old-field FIND keeps today's conservative clip (no behaviour change). R-out applies to window plan classes | §1 table, §1 |
| F4 | The define allocates exactly `proof_n` rows and refuses by R-out and R-short. Ask and define agree whenever the ask's storage holds `proof_n`. Five internal producers listed. Define rows added to the arena price (about 291 KB per attempt at 4095, about 133 KB at 32) | §5 |
| F5 | `formhash.c` `fh_work` listed as a kit-internal writer. `last_s` is the largest stated POSITION (a RUN term counts as `offset + run_len - 1`). `proof_n` 0 with NULL is the all-ones class for PRESENCE, NONE, non-FIND and the zeroed refusal | §1, §5 (c), (e) |
| F6 | `d27_frame.c:1075, :1084, :1124, :1178` added. Count is 22. G2 holders listed. Test rows come from the test's own storage (`d27_frame.c:1094`) | §5 (a), (e), §8 |
| F7 | `probe.c:101` listed (run_link_checks `-Werror`). S3097 is re-anchored; S3045 and S3064 get a REACH re-read only | §5 |
| F8 | The DRAWS are the movers: REPORT `:433` first, a repeated-class shape straddling every finite h, and the other families at today's stated reach. A counted per-h line fails at zero. `G2W_MAXPOS` 128 / `G2W_REACH` 256. `G2W_NOFF` holders listed. Runtime re-priced | §3 "Answers", §6 |
| F9 | RULED: default candidates are FINITE h only. I is timed as the reference and as the dial arm (R2) | §3, Goal 3 |
| F10 | RULED: the largest h in E wins. Drills (i)-(viii) re-run against the written rule; (i) and (iv) give h\* = 64 | §3 drills |
| F11 | `E = { h : W(h) <= (1+f) min W }`, never chained. `W` is against I, from raw medians. `f` is the cards' A/A ratio floor, reduced as §11.4 reduces B's. R1 reads C1-C2 only; C3 feeds R2 and R5. §4's trigger becomes R4 | §3 |
| F12 | RULED: the test-only lever `mf_lever(art, "span-head=N")`, reached through `--harness=span-head=N` on `build/pcrec-harness`; readers listed. Identity check: the lever at h\* is byte-equal to the shipped build at h\* | §3 "The head lever" |
| F13 | cover_cap.md edits for main (§11.4, §11.6.1, §11.6.4), plan A only. `[0-9a-f]{64}` joins C2. The cards run on the kit's harness in the same window | §3, §7 |
| F14 | RULED: plan A's fallback, costs and decider (main, with the owner told) are in the plan A question, cross-referencing §11.6.1 | §3 "Scope", §7, §8 |
| F15 | A three-state kit option read; the deny wins (tuning.md §2.43¶1). Readers listed: registry §6¶7 and ¶8a's table, the CI shard tables, `cloud_units_plan.py:64` (checked at build), `formhash.c:425`. Spec homes: registry §6¶8a for the row, tuning.md §2.43¶3d for caller behaviour | §3 "The option", §4 |
| F16 | (a) Literal stretches render as one compare in every form and are never split by h; `lit-l31` is dropped from the movers and the movers are re-derived. (b) Bold plain-word slugs on every question. (c) A/B framed as the same end state, with a different interim default and cost | §3, §7 |
| F17 | DOC: the caller-owned output-list family (three shapes), its general form and four unlocks, each with a trigger | §5 |
| F18 | DOC: `cover_window` is `known.c:583`; `pcrec_cover_site` is `:613-628` | §1 |
| FREEZE NOTE | The night order is recorded in §3 and §8, along with its agreement with main on 2026-11-16 and that it applies to plan A only | §3, §7, §8 |

## Open questions

These are the questions in §7 and §8. Each has a plain-word slug and the kit's leaning.

- **other-sites-at-32** (main): should pcrec keep its other window sites at 32 positions by its own asserts? Leaning: yes.
- **cover-ask-storage** (main): should the cover ask get ceiling storage, about 131 KB per attempt at every width? Leaning: yes.
- **caller-storage** (main): should the asks take caller-supplied storage? Leaning: yes.
- **row-memory** (main): is about 291 KB per attempt at 4095 (about 133 KB at 32) acceptable until the compile-cost record exists? Leaning: yes.
- **night-order-edits** (main, plan A only): take the three cover_cap edits? Leaning: yes.
- **forms-now-or-next** (owner): plan A or plan B, with A's fallback and costs stated. Leaning: forms now.
- **keep-short-spans** (owner): keep spans of 32 or fewer all-inline even on a measured win? Leaning: no.
- **near-miss-fix-later** (owner): fix near misses in the first build? Leaning: no (D77).

Design choices the follow-up critic should look at, made by this lane where r22 left them open:
- The old-field FIND clip is kept as conservative rather than turned into a refusal (F3). This
  avoids an unlisted behaviour change.
- The cover ask's ceiling storage costs about 130 KB more per attempt even at short widths. This
  is stated openly in the row-memory and cover-ask-storage questions.
- The lever is the first VALUED `mf_lever` name.

## STATE AT HANDOFF

STATE: done. Rev 3 is committed on `lane/memfn-r45`. The review is filed and indexed, and the
design and lane-history indexes are updated. No code, no timing, no box jobs and no make runs
(no build was needed: every recount was a `git grep` at origin/main).
Rulings file `docs/dev/lanes/r45c_rulings.md`: empty at every checkpoint. Last entry applied:
none.
Next per the r22 ruling: ONE critic (fix-induced, on F1-F16 only), then post.
OWED: none
