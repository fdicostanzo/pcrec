# wcrev — window_contract.md revision 2 (2026-10-12, docs only)

Branch `lane/wcrev` from main `76067df80`. Deliverable:
`docs/design/memfn/window_contract.md` REVISION 2 (PROPOSED), applying the
light D6 panel r4 (`docs/dev/reviews/2026-10-12-r4-window-contract.md`) and
D161 addenda 7-8. Nothing under `src/`, `cli/`, `lib/`, `memfn/` or `tests/`
changed and nothing was run, so no `make`. Kit tips read with `git show`:
`lane/memfn-r17` `f1cf102c5`, `lane/r17b` `174f3e320`.

## What changed (the note's §R2 table has every row)
- **Reply** (D161 add. 7): a STREAM of exact span-0 starts. COMPLETE,
  ASCENDING with no repeats, each candidate span 0's start, plus REQUIRED
  spans bind. The ORIGIN moves to span 0's start; a bounded head before it
  (`h_max`) is pcrec's. `[L, U]`, resume-at-`U+1` and Q3 are deleted (E7
  dissolves). E1: context predicates are not spans; pcrec tries the edge and
  "miss = NOMATCH" covers only COVERED candidates.
- **Producer** (E2): hull spans only, a MEMBER of the position-pin fact family
  (§5.6). `start_set`/k-set stay their own facts. Offset-pinned union spans
  are unlock (b). Prefix-sum obligation (E6), C-SP1/2 floors, C-SP3 min (E8).
- **Presence** (E3): its own table T-PRES beside T-CUT; both have a deny
  column (R10).
- **Proven facts** (R2 REJECTED, D161 add. 8): kept; layer-invariant by
  contract, checked by a new C-PROOF; Frank's `foobar` example; T-PROOF keeps
  E4's conjuncts and gains `report` and `verify-rest` rows.
- **S1 is a pcrec abi event** (R1). The stamp means OFFERED, with one entry per
  kind; spec hunks in `findings.md` §5 and `match_api.md`; mover census owed.
- UNSTATED sentinels and the payload invariant (R4). The shadow lives to S4
  (R5). S3's full grep-derived file list includes a blinded lane for G2 (R6).
  The W1/W2 refusal is a kit code change (R7). Naming (R8). Event rows (R9).
  Activation and evidence-strength facts are filed (R10).

## Findings
1. The position-pin unification is filed in `match_split_pinonly.md` §4.3 /
   §9 U3, not in `compound.md`; `compound.md`'s U3 is [EMIT-ENTRIES]. The note
   carries it (§5.6).
2. With the stream, the K82 handoff's `c - K` does NOT retire. K is the
   bounded head before span 0, so it is pcrec's. Revision 1 said it retired.
3. After S1, every regeneration of the prior moves every artifact's
   `<PREFIX>_FINDINGS` digest (§10.3).
4. `mf_need`'s `MF_REQUIRED = 0` is a silent binding default once REQUIRED
   binds the stream, so the enum is re-numbered (an `MF_SITE_ABI` event).

## Open / validation
Q1 (inner-segment choice) open for Frank; Q2 stays a leaning. §14 lists the
re-check's targets. Docs only; citations read at `76067df80`. Nothing owed.
