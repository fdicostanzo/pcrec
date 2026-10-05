# pcrec-memory-functions — journal

Append-only, dated, newest last. One entry per significant work session
or delivery: what was done, what was measured (both layers, D147, with
box and regime), issues, next steps. Never edit an entry away; correct
it with a later one. pcrec's `docs/dev/dev_journal.md` gets a one-line
pointer when a kit change merges to main.

---

### 2026-10-05 — subtree set up (lane memfnsetup)

- Frank's rulings: D146 (delegation), D147 (layers: the scalar layer is
  live and improvable forever, SIMD is a layer that must beat the
  CURRENT scalar, both layers reported), Q35 (integration.md §8+§14 is
  the design of record), Q36 (in-tree `memfn/`, `pcrec_mf_*` symbols,
  0BSD, extraction on a measured trigger: a stable API over several
  migration steps AND a real second consumer).
- Set up: CLAUDE.md, README.md, LICENSE (0BSD), the ledger pair
  (`requests.md`, `responses.md`), this journal, the session wake
  template, `src/`/`include/`/`tests/` with planned-contents stubs. No
  code and no Makefile wiring: the first code lands with R4a (D77).
- integration.md revised to 4.2 for D147 (the frozen baseline becomes a
  per-step comparator only; the SIMD-off profile is the current scalar
  layer; G1 reads each change against its own deny, in both layers).
- First request filed: R-1, the R4b measurement (T-B twin re-run on
  Linux on the post-handoff build, with a SWAR fused variant).

## 2026-10-05 — integration.md revision 4.3: Frank's rulings folded (lane memfnr43)

- D147 addenda 1-7 folded into integration.md (§R4.3, read first):
  - Q35-Q42 and Q50 ruled; Q51/Q52 rejected.
  - ONE SIMD switch, `-fno-memfn-simd` / `-fmemfn-simd` (axis
    `memfn-simd`), OFF by default until the SIMD hold lifts:
    - OFF = portable C (plain C, SWAR, libc);
    - ON = optimized for a specific CPU, no portability promise;
    - the contents of ON are this kit's per-site choice, cascades
      included (K-6).
  - EVERY search site migrates (Q42 reversed), under a checked site
    manifest (C17, born at R4a, every row `pending`). The memchr
    ratchet ends at 0 outside the kit.
  - The planner moves live at M5; M5′ is the ruled adoption event.
  - Stamps: `MEMFN_FORMS` (Q39 as ruled) plus a `MEMFN_LIBC` record
    (spelling asked as Q53).
- New questions: Q53 (the libc line), Q54 (N7 under completeness), Q55
  (the plan's stamp visibility at SIMD-off).
- R-1's "R4c's trigger" now reads "R4d's trigger": M1 (R4c) is triggered
  by completeness. `requests.md` is the manager's to amend.
