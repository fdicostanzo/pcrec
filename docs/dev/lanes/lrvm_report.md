# lane lrvm — [LOSS-REVIEW] phase 1, the VM-route share (2026-10-11, opus)

Deliverable: `docs/dev/optloop/lossreview/vm.md`, with instruments and data
in `docs/dev/optloop/lossreview/vm/`. Branch `lane/lrvm`, from main
`f2fcffb4`. Docs and scripts only: nothing under `src/`, `tests/` or
`docs/spec/`, and nothing written in pcrec-bench.

## What was done

No timing was taken (the box was busy). The evidence is:

- **Stamps** at main, compiled with the bench's flags.
- **gcov line counts.** The bench's find-all loop ran over the subjects,
  regenerated read-only from a `git archive` of pcrec-bench `d359564f` with
  its own generators; all 31 throughput and 278 short subjects
  sha256-matched.
- **walk_survey loads** as a cross-check.
- **gcc -S / objdump reads** of artifacts built the bench's way
  (`-O2 -fPIC -shared`).
- **20 hand twins**, all answer-identical to today's artifact over
  throughput, short and discriminating extra subjects.

## Results

37 VM-route cells were attributed. **34,603,784 ns** was lost vs jit in
total. The top three causes by that total:

1. **C1 BACKREF-ATTEMPT, 27,194,692 ns (79%).** Fix-existing:
   - (a) emit the encoding seam's hot entries (`<prefix>_span_match`,
     `<prefix>_back_step`) with internal linkage. Under `-O2 -fPIC` every
     call is `call ...@PLT`, because gcc may not inline an exported
     function;
   - (b) [ART-TRAIL-ELIDE]'s FRAMELESS sub-case. It needs no dominance
     fact: replace the trail with a static reset of the written slots.
     bak-2 undoes 6.5 trail entries per failed attempt;
   - (c) START-SET's VM-hat MASS admission (Q-R5 / [START-DENSE]).
2. **C2 VM-HAT TABLE FORM, 2,583,534 ns.** The VM hat walks a 256-entry
   table even for a 1- or 2-member sparse set (quoted-delim: 4.64M
   iterations over 4.68 MB). Fix-existing: a form row (memchr / two-stream
   leapfrog) selected by `|S|` and rate. It is one table with C1(c).
3. **C3 ONE-BYTE MEMCHR RESTART, 1,990,832 ns.** lka-*, lkb-* and slack
   pay one memchr restart per pinned-byte hit, where JIT runs a SIMD char
   pair. Fix-existing: memfn R4d, the scalar SWAR pair filter (trigger MET,
   unbuilt). R-13's SIMD rows are the SIMD form.

The answers to the brief's specific questions:

- **bak-2 grew** +17.5% because START-SET stage 2's VM hat seeks on the
  dense `\w` set. It is the only program diff between `c4c70f2c` and main.
- **ANCH-ATTEMPT** = the `t-trim` / `t-evil` hazard subjects. G2 declines
  the necessary-byte pre-check, whose byte is absent behind an unbounded
  leading run.
- **BACKTRACK**: pcre2-interp is 6-8x slower than pcrec on every cell, so
  those cells are not algorithmic. Only moment-iso8601 is (interp beats
  pcrec there).

The brief's expected asr-*, stack-frame, mod-i/mod-r and email-owasp cells
are DFA-route at main and belong to lrdfa. An FYI went to lrdfa: the M2.1
stay-threshold cause (C5) reaches their `\b` cells.

## Owed

- **Twin timing (20 twins) in a quiet slot.** The commands are in `vm.md`
  §5 and `vm/twins/twins.tsv`.
- **No suite runs**, because nothing under `src/` or `tests/` changed.
