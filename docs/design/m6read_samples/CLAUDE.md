# docs/design/m6read_samples/ — the [M6-READ] style exemplar

**APPROVED by Frank 2026-08-21** ("look fantastic"), with one cosmetic ruling
applied — `/* */` for structural comments, `// ` for line-level intent — and
all five of README §2's judgment calls ratified as embodied here. This
directory is now the STYLE OF RECORD for the emitter conversion.

The one sample commented artifact the [M6-READ] plan row owes Frank before
the emitter conversion, plus the proposal it exists to justify. **Design
artifacts only: nothing here is built or tested by pcrec's make, and nothing
in `src/` was touched to produce it.** The `*_after.c` files are HAND-EDITED
emitted C — they show what the emitter should produce, they are not produced
by it, and they will go stale the moment the emitter changes. That is fine;
their job ends when Frank approves or redirects the style.

## Files

- `README.md` — **read this first.** The proposal: the naming scheme for
  emitted local identifiers, five judgment calls flagged for Frank's ruling
  (headed by where "ABI" stops for parameter names), the style rationale with
  measured comment density, the object-code-neutrality result and its one
  real finding, and the implementation plan for the emitter conversion with
  the measured pin budget.
- `dfa_before.c` / `dfa_before.h` — emitted verbatim by `build/pcrec` for
  `ERROR-[0-9]{3,5}: [a-z]+`. Prefilter + forward scan + reverse pass.
- `dfa_after.c` / `dfa_after.h` — the same artifact hand-edited into the
  proposed style. **The primary deliverable**; read it top to bottom.
- `vm_before.c` / `vm_before.h` — emitted verbatim for
  `(\w+)@(\w+)\.(com|org)`. Captures, so the VM engine: the DFA pair becomes
  a prefilter subroutine and the compiled program sits above it.
- `vm_after.c` / `vm_after.h` — the same, hand-edited.
- `check_neutrality.sh` — the object-code comparison gate. Runs in seconds,
  needs only gcc/objdump/nm. Its header comment states the definition of
  "neutral" the sample stage had to pin down: executed bytes and exported
  symbols must be identical, while internal symbol NAMES necessarily change
  and a disassembly-text diff will false-alarm on them.

## Two things a later reader should not have to rediscover

1. **The `rx_L<N>` labels are deliberately NOT renamed.** They are shared
   vocabulary with `pcrec --emit-ir` and are held in correspondence by
   `tests/codegen/run_ir_listing.sh`. README §2 decision 2.
2. **`tests/codegen/run_ir_listing.sh:132` is the conversion's real hazard**,
   not any of the ~94 mechanical pins: it greps the IR listing's own prose
   for `stv[N]`, so renaming the emitter and the listing consistently makes
   both sides empty and the check passes vacuously. README §5.

Maintenance: this directory is frozen once [M6-READ]'s style is ruled. If the
samples are regenerated against a newer compiler, regenerate BOTH sides of
each pair and re-run `check_neutrality.sh` — a stale `*_before.c` against a
fresh `*_after.c` compares nothing.
