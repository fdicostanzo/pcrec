# cmpentry — every exported entry as a compound controller; the dial deciding what is inline (report)

Lane `cmpentry`, 2026-10-14, opus, from main `d6e7fa993` (abi 78). Assessment and
design note only: nothing under `src/`, `cli/`, `lib/` or `tests/`; compile-only probes
plus clockless callgrind instruction counts; no timing.

## Deliverables

- `docs/design/compound_entries.md` — the note (§0 answers first).
- `docs/design/compound_entries/` — four probes, the driver, four result tables, own
  CLAUDE.md.
- `docs/design/CLAUDE.md` — index entry.

## Summary (what a resuming agent needs)

1. **The entry map holds.** Every matcher entry is already a small combinator over a
   body (`locate-then-finish`, `finish-at-position`, `forward`); the residuals are leaf
   parts. Gaps: the STATE part (`rx_iter`, not built), the kit's stream state (needs
   the STATE part), captures-on-demand (`select-by-arg`, filed). Give-up codes,
   vars/callouts and utf-check are already the call-site table, the vars channel and the
   controller prologue.
2. **Today nobody in pcrec decides the layout; gcc does**, and its decision flips with
   `-fPIC` (exported siblings stop inlining into each other: the function bytes fall
   1.5-20% on eight of nine witnesses and rise 6.7% on the vars one). Three emitters
   write their own entries; `entries.c` restates the call edges by hand.
3. **Hard constraints (gcc errors, measured)**: a static label table cannot be copied
   (DFA attempt route, which includes split's F part, so split leaves the dial nothing
   to decide); a computed goto cannot be inlined (framed VM `match_anchored`). Soft: a
   single-caller part must never be shared (+112 B, no gain).
4. **Costs (callgrind Ir, Zen 4, gcc 15.2 -O2)**: a shared static part 5-29 Ir per
   call over inlined; an exported-sibling call through the PLT about 4.8 Ir per call
   more than the same call bound locally; sharing a multi-caller part saves 0-160 B
   (0-5%); inlining every copyable part costs +4.4% to +21.2% `.text` for −2% to −13%
   Ir. On a small VM artifact the one-body `plain` rung is BOTH larger and slower than
   `inline` (per-entry frames and canaries), so "shared" is not automatically the size
   end.
5. **The dial row**: one `part-layout` row generalizing `--vm-entry-shape` over an
   eight-member sibling family. `0` = as emitted (byte-identical; D103's no-op cell);
   `−2`/`−1` = `shared`, `+1` = `hot-inline`, `+2` = `inline`, every non-zero cell `†`
   until the D166 set carries the static-part call cost and part bytes. Constraint rows
   H1-H7; H6 brackets the attribute text out of every length decision (RQ-3's
   precedent), so no position moves the refusal set.
6. **Convergence**: one declared `entry_rows[]` (EMIT-ENTRIES' table with the
   controller a column; edges derived, not hand-written). The iterator's NOTEMPTY retry
   is `first-nonzero(R@q, SEARCH@next_pos(q))`, split's own combinator; `next` is a new
   `iterate` combinator over the STATE part. I1 stays one abi event if the zero-mover
   table (E0a-c) lands first.
7. **Recommendation**: E0 (zero-mover entry table) before I1; the layout row's
   mechanism at all-`†` cells (E1, zero-mover); cells only by ruled diff with a
   measurement. The layout row alone is low-impact; the entry table is the value.

## Findings

- F-1: B4's compound controller calls exported `<p>_next_pos` (`emit_compound.c:129`)
  and, under `-futf-check`, P's prologue calls exported `<p>_valid_upto`: PLT calls in a
  shared object. Not an answer defect; the iterator's static twin `__adv` is the fix's
  shape (fold into I1).
- F-2: gcc's entry layout flips with `-fPIC`; the bench builds `.so`s, the in-tree
  drivers do not.
- F-3: gcc partially inlines `_valid_upto` into a `.part.0` clone (K24's shape on a
  residual without `noclone`); harmless as measured.
- F-4: on split, H1 leaves the dial nothing to decide.
- F-5: "shared" is not automatically the size end (§2.4).
- F-6: the NOTEMPTY retry is split's combinator.
- Instrument note: the entry probe's first version took objdump's printed call target
  for a global call, which in a `.o` is the relocation placeholder's address and can
  name the next function; it reported two false VM edges. Fixed to read the relocation;
  sizes were unaffected (commit b3153da98).

## Questions for Frank (in the note, §5.4)

Q1 pinned dial cell (D103) or measured selection (D166) for "what is inline" (leaning:
pinned policy per position, the one threshold from the set); Q2 keep `balanced` as
emitted (leaning yes); Q3 the iterator parity gate binds `0..+2` only (leaning yes); Q4
E0 before I1 (leaning yes); Q5 never call an exported sibling (leaning: adopt as H5,
applied where an event already moves the bytes).

## Validation

No build of pcrec was changed; `make -j16` on the base tree was used to run the probes.
No suite run is owed: the lane delivers documents and probes only. The probes are
re-runnable with the commands in `docs/design/compound_entries/CLAUDE.md`.
