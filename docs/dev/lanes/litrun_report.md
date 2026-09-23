# litrun — VM literal-run fusion measurement (2026-09-23)

Lane `litrun`, sonnet, branch `lane/litrun` from `main`. Measurement only
(D77): nothing under `src/`. Frank's question: the VM emits a literal run
(`xyzabcdefgh`) as N per-byte if/goto tests; should it fuse them into a
word compare / `memcmp`?

**Deliverable**: `docs/dev/optloop/litrun_census.md` (its own CLAUDE.md
entry added), this report, and `lanes/CLAUDE.md`'s entry below.

## What was done

1. **What gcc already does.** Compiled `xyzabcdefgh` / `(?i)xyzabcdefgh` /
   `[0-9]+abcdefgh` with `--engine=vm`, read the emitted C (confirmed the
   brief's cited per-byte if/goto shape at `emit_vm.c`'s `A_CLASS` arm —
   pcrec has no `A_LIT` kind, every literal byte is a one-byte class node)
   and disassembled at `gcc-16 -O2`/`-O3` on this Mac (arm64). Then
   hand-rewrote the run as one `&&`-chain expression and, separately, as an
   explicit `memcmp()` call, and disassembled both. Repeated the `&&`-chain
   and `memcmp()` pair on x86_64 via a light probe over the tailnet
   (`ssh duxevents@100.69.121.107`, gcc 15.2.0 — two small compiles, no
   suite, scratch dir removed after).
   **Finding**: gcc never fuses the `&&`-chain shape (11 separate
   `ldrb`+`cmp`/`cmpb`+branch, arm64 and x86_64, -O2 and -O3). Only
   `memcmp()` against a compile-time constant gets gcc's own builtin
   fusion (11→3 loads arm64, 11→2 x86_64). This is the load-bearing fact:
   pcrec cannot rely on the compiler finding this on its own; it has to
   emit the `memcmp` form directly.
2. **The population.** Parsed literal runs out of all 64
   `pcrec-bench/bench/capability/patterns/*.rx` texts with a rough
   tokenizer, joined against `docs/dev/optloop/b2ledger/stampdiff.json`'s
   per-pattern `RX_ENGINE`, and cross-referenced the 60 losing match-regime
   cells from `cycle1_caps_view.md` + `cycle1_nocaps_view.md` (AFTER pin).
   Hand-verified every raw hit against its `.rx` file, which caught the
   parser's real limitation (it misreads `(?<name>`/`(?&name)` DEFINE/
   subroutine-call syntax as literal bytes — 2 of 7 raw VM-route hits were
   this false positive on `bracket-array-define`). **5 genuine VM-route
   losing cells carry a real literal run ≥4**, all three `wild-secrets-*`
   patterns, all on `auto-caps`; `auto-nocaps` has zero. Checked
   `RX_VM_PREFILTER` for the three before speculating about cause: already
   `"hybrid"` on all of them, so the 55.16x/29.65x ratios are not an
   absent-prefilter artifact — whatever's left is per-attempt match cost,
   which a fused compare would actually touch.
3. **The general-mechanism note.** `src/opt/reqbyte.c` already derives the
   necessary-run fact (`RX_REQ_RUN`) but only for the prefilter; a fused
   VM compare would be a second PATFACTS reader for `github-pat`'s
   single-branch case, but most of the real population has no
   whole-pattern `REQ_RUN` (alternation, per-branch literals) so the
   fusion has to key directly off `emit_vm.c`'s own `A_CAT`/`A_CLASS`
   shape. Stated the caseless complication (masked-word path vs `memcmp`)
   without building either.

## Verdict

**NOT MET.** Named the one more measurement: hand-patch `github-pat`'s
generated matcher to the `memcmp` form, rebuild just that `.c`, and
re-time its `thr`/`srch` bench cells against the current 2.66x/1.01x
ratios — if the ratio closes substantially the trigger is met on this
5-cell population, if not the gap is elsewhere.

## Validation

No `src/` changes to validate. Own build: `make -j4 CC=gcc-16` in the
worktree, clean. Every number in the census names its exact command
(`gcc-16 -O2 -S`/`-c` + `objdump -d`, the ssh probe commands, the Python
join script). Nothing owed.
