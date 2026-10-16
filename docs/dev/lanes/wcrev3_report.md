# wcrev3 — window_contract.md revision 3 (the design E-1 implements)

Lane `wcrev3`, 2026-10-16, from main `063b4a4b4` (abi 78). Design only: nothing
under `src/`, `cli/`, `lib/`, `memfn/` or `tests/` changed. One compile-only
census was run (`docs/design/memfn/window_contract_rev3/`). Deliverable:
`docs/design/memfn/window_contract.md` revision 3 (read its §R3 first, then
§3.7).

## Summary (for a resuming agent)

- **E-1 (§3.7).** pcrec builds `mf_analysis` per attempt through ONE kinds
  table, `find_kinds[]`, keyed by the [FINDINGS] query vocabulary. Each row has
  an `arrives` column: `byte-rate` is ALWAYS, other kinds MEASURED-ONLY.
  T-KIND's rows decide the state, and provenance goes by the answering LINK's
  identity, not by name. The object is handed ONCE on `mf_art_begin`, filling
  the kit's B1 slot with no kit edit.
- **Why the slot is per art (§3.7.2).** D162 says one object per compile. It
  makes revision 2's same-pointer check structural. `mf_measures` rides
  `mf_art_begin` already, the memo lives in `mf_art`, and the art already
  carries compile-wide facts.
- **The sibling check against [KNOW-SRC] (§3.7.3) finds a CONFLICT.** Revision
  2 made `_FINDINGS` mean OFFERED. `measure_sets.md` §3.5 makes `_MEASURES` mean
  CONSULTED, and [KNOW-SRC] builds ONE stamp grammar for both. The design of
  record is CONSULTED: the offer does not set `byte_rate_asked`. So E-1 is
  ZERO-MOVER in every arm: no abi event and no D80 hunk. The kit's per-kind
  `consulted` (layer-invariant) joins the stamp at B3b, which carries the
  findings.md §5 / match_api hunks (§3.7.9).
- **Rev 2's open question 5, MEASURED (§3.7.4).** 0 of 5,336 / 5,364 / 5,337
  default corpus artifacts (byte / utf8 / `--engine=vm`) stamp `""` today:
  every default compile asks. `""` exists only on deny arms: 1,973 under
  `-fno-req-byte`, and all 5,337 under `--engine=vm -fno-req-byte -fno-req-run`.
  So the OFFERED alternative's movers are deny-arm only. A zero-mover gate on
  the default arms alone is vacuous, so G1-E1 includes deny arms (K35).
- **The OFFERED alternative is stated exactly (§3.7.5).** It covers the event,
  the movers, the +68/+28 cap hazard on deny-arm artifacts, the census, the
  re-aims (findings §4 "nothing asked", §6 #22, S314) and the sibling reopen.
- **The C-items.** winreq C-1..C-16 are applied: the PRESENCE span class, the
  span-class enum, ONE stream reply (ALL_PRESENT → VERDICT deleted) with
  obligations 5-7, T-WITHHOLD replacing T-PRES, `consumer` replaced by
  `site_kind` at S3. C-7 is done in §11, and the R-18 ledger amendment text is
  in Appendix A for main to apply (`requests.md` single writer). C-8: unlock
  (c) is struck.
- **D161 add. 10.** A `byte_form` (EXACT/SUPERSET) per span gates verify and
  proofs.
- **Checks (§3.7.7):** G1-E1, C-E1-1..4, C-CONS (B3b), ASan.
- **Sabotage (§3.7.8):** proposed S991-S998, the manager allocates. S991-S996
  belong to E-1, S997-S998 to B3b.
- **Findings.**
  - F-2: `req_rate_why` writes `rate:builtin-prior` for any answering bundle,
    contradicting facts_listing.md 4.1.3¶4 (read from code).
  - F-3: the query vocabulary is spelled four times.
  - F-4: `measure_sets.md`'s `consulted` lacks the layer-invariance obligation.

## Open questions (discussion form, each with a leaning; §12)

- **Q3 (Frank's): what the `_FINDINGS` stamp means once the kit receives the
  analysis, CONSULTED or OFFERED.** Leaning CONSULTED for both [KNOW-SRC]
  siblings. At default flags the two readings give identical stamps on every
  corpus artifact; they differ on deny arms and on kit reads from B3b on.
- **Q4 (manager's): when the `rate:builtin-prior` mislabel (F-2) is fixed.**
  Leaning: in B3b's commit, spelled `rate:<provenance>`; correct the spec
  sentence to what the code does until then.

## Validation

- Design lane: no build gate applies. `make -j16` was run only to compile the
  census binary (rc 0).
- Census:
  `python3 -I docs/design/memfn/window_contract_rev3/stampcount.py TREE build/pcrec`
  and `stampcount_deny.py`. Outputs are committed beside them.
- Not run: the bench patterns and emit_sweep's composition stream. Both are
  owed by E-1's G1-E1.
