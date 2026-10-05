# memfnsetup — the in-tree pcrec-memory-functions subtree, and integration.md rev 4.2

Lane memfnsetup, 2026-10-05, opus, writer (docs + skeleton, no code),
branch `lane/memfnsetup` from main 06ec65c8. Inputs: D146, D147 (with
Frank's Q35/Q36 rulings), integration.md rev 4.1, analyze/ as the
in-tree-subtree precedent.

## Delivered

1. **`memfn/` skeleton.** It contains:
   - `CLAUDE.md`: purpose, the D146 boundary, the D147 layer rules, the
     same-commit abi rule, symbols/licence, process, the three standing
     design questions, and the layout;
   - `README.md`: the stand-alone "bespoke high-speed memory functions"
     pitch, the 0BSD licence, and "status: no code yet";
   - `LICENSE` (0BSD);
   - `docs/`: `requests.md` (written only by the manager),
     `responses.md` (written only by the kit), `journal.md`, a `wake.md`
     TEMPLATE for the dedicated kit session, and its own `CLAUDE.md`;
   - `src/`, `include/`, `tests/`: CLAUDE.md stubs that state the
     planned contents (K1, K2, the scalar arms as the live scalar layer,
     native arms; `memfn.h`; G2).

   There is no Makefile wiring and no code. The first code lands with
   R4a (D77).
2. **Root CLAUDE.md** gains a `memfn/` entry under "Where things are"
   and a situation-index row for "change search/scan emission or a kit
   kernel".
3. **integration.md rev 4.2.** A new §L, read first, applies D147:
   - **L.1** defines the layers. The scalar layer is everything the kit
     renders without `memfn-native` (SWAR and libc included). The SIMD
     layer is the native arms.
   - **L.2** makes the baseline a per-step comparator only; `arms.tsv`
     becomes a change detector.
   - **L.3** withdraws `memfn-off`, `-fno-memfn-scan/-loop`, `off.tsv`
     and `pcrec[memfn-off]`. Each kit change's own `--memfn-deny=` is
     its OFF arm, and a per-change comparator checks that deny against
     the parent commit.
   - **L.4** makes G1 read both layers. Scalar changes are accepted on
     SIMD-off; native changes are accepted against the current scalar;
     native arms are re-read after every scalar change.
   - **L.5** has the stamp report the SIMD layer: its reference compile
     is `-fno-memfn-native`.
   - **L.6** is a conflict table.

   33 in-place `[rev4.2]` annotations cover §8.5, §8.6, §9.2, §9.5,
   §10.1, §10.5, §10.6, §11.1, §12, Q27, §14.6, §14.9, §16, §17.2,
   §17.4, §17.6, §18, §20.1 (the file names as built), §20.2, §21.1,
   §21.2, §21.3 and §22. In §23, Q35 and Q36 are recorded RULED, Q38 is
   revised, Q39 is re-derived as Q52, and Q50-Q52 are new.
   option_sets.md, docs/design/CLAUDE.md and docs/design/memfn/CLAUDE.md
   carry cross-notes.
4. **R-1 filed** in `memfn/docs/requests.md`: the R4b measurement (the
   T-B twin on Linux on the post-handoff build). It has four variants:
   `emit` copied from the CURRENT artifact, a new SWAR fused form,
   `ffl` SSE2/AVX2, and the byte loop. It covers the K82 cells plus
   K85's `cls-n-uc` in both regimes, and reports SIMD-off (`swar` vs
   `emit`, R4c's trigger) and SIMD-on (`ffl` vs `swar`).
5. **plan.md [MEMFN]** gets a short note.

## Judgement calls for the manager

- **File names.** The brief named `requests.md`/`responses.md`, while
  rev 4 §20.1 had `inbox_from_pcrec.md`/`outbox_to_pcrec.md`. I followed
  the brief and recorded the rename in §20.1's annotation. The commit
  prefixes are `[requests]`/`[responses]`.
- **Withdrawing `memfn-off` (Q51)** is my reading of D147, not a
  ruling. A frozen kit-off arm has no acceptance role once SIMD is
  measured against the current scalar and scalar changes are measured
  against their parent. It is put to Frank as Q51.
- **The stamp's new reference (Q52).** It keeps M1 zero-mover. The cost
  is that scalar-layer forms are not bucketed by the stamp. Rev 4.2 is
  unpaneled; a light panel before R4a′ would be prudent.
- **The libc line (Q50).** glibc's `memchr` is vectorized internally,
  and it sits in the scalar layer under the "no ISA text" line.
  Frank should confirm that this is the line D147 means.
- **R-1's trigger.** `lane/k82hbuild` is merged (f116cff5). Before the
  R4b lane is briefed, the manager should confirm that the handoff was
  alpha-accepted.

## Validation

`make strict` on the lane branch: see the handback (no source changed).
