# Review 2026-11-06 r7 — span_cards rev 1.2, readiness (one critic, diff only)

**Subject.** docs/design/memfn/span_cards.md rev 1.2 at 040309e7b (lane/memfn-s2rev12), the diff against rev 1.1 (e52cd716a) only, as ruled in r6. One opus readiness critic, fix-induced focus, launched directly by the kit manager (no coordinator; one lens). Its file: `2026-11-06-r7-memfn-span-cards-ready/readiness.md`.

**Critic verdict.** S2c, S2d and S2e are each READY WITH TEXT FIXES; nothing blocks. Rev 1.2 changes nothing S2a builds. The loader accepted every new shape (7 fixture cases), all 7 drills reproduced their quoted figures, and the 10 cites checked hold.

**Findings.** READY-1 (embed_text.sh takes the set name from the path: the strip copies keep `<id>/<rev>/set.tsv`, and the `gen-%` rule needs a per-store row); READY-2 (the run record is written at the window's end, but J2p reads J1's verdict mid-window; the `jobs` writer after a failed job is unnamed); READY-3/4 (S2c still lists the withdrawn §2.2¶3 hunk; contradictory separability sentences); READY-5 (three copies without a compare: cell-id fields vs columns, the header `run` sha, base vs family); READY-6 (the 0-cells assertion has no mechanism); READY-7 (the cost-row PARTIAL path is unreachable today); READY-8 (the S2c dry-run run id is unstated); READY-9 (arm_fixtures/check_hash changes missing from S2c's package).

## Rulings (kit manager, 2026-11-06)

**Verdict: READY with text fixes.** Every finding is ACCEPTED as a text fix. The S2c build lane applies READY-1..9 to span_cards.md as rev 1.3 in its FIRST commit, marked `[rev1.3 <id>]` with an §R1.3 table, then builds S2c against that text. No further design round. READY-7 is NOTED: the unreachable PARTIAL path is stated as such, not removed. The S2d/S2e lanes read rev 1.3.
