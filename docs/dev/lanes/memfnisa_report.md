# Lane memfnisa: [MEMFN] R1b, ISA selection and checking

Lane memfnisa, opus, 2026-10-04, branch `lane/memfnisa` from main 3813fa00.
Docs and Mac probes only. Nothing under `src/`, `cli/`, `lib/` or `tests/`
changed, and no emitted byte moved.

## Delivered

- `docs/design/memfn/isa_selection.md`, the R1b addendum. It covers the
  options, a first-match decision table, the probes, the owed Linux run,
  RB-10..13 / N-12..14, rubric H-14..16, U-9..14 and Q4-Q6.
- `docs/design/memfn/requirements.md`: cross-references. Finding 5 is
  narrowed, RB-8 points to RB-13, N-4 notes the Darwin result and Q5, the
  rubric maximum is now 81, and §2.6 points to the script.
- Probes under `docs/design/memfn/probes/`, all built by `probes.mk`:
  `isacost.c` (the timing probe), `isanote.{c,sh}` (Linux loader probe),
  `fmvdarwin.{c,sh}` (Mac), `linux_run.sh` (the owed run), and their make
  rules.
- Transcripts: `probes/out/isacost.mac.{gcc,clang}.sel-{base,wide}.txt`
  and `probes/out/fmvdarwin.mac.txt`.
- Updated: the CLAUDE.md files (memfn, probes, out, docs/design, lanes) and
  plan.md's `[MEMFN]` row note.

## Validation (complete for the Mac; the Linux run is OWED)

- `isacost --check`: n 0..300, every hit position, alignments 0..31, spans
  ending at the allocation's end, under both `--sel=base` and
  `--sel=wide`. gcc-16 checked 26,179,776 cases, clang 31,997,504, and
  clang ASan+UBSan 31,997,504. All had 0 bad.
- `make compile-x86` compiled `isacost.c` clean at x86-64, -v3 and -v4,
  for ELF and Mach-O (clang `-target`), and `isanote.c` clean for ELF. The
  ELF object carries the ifunc, the `target_clones` resolver and both
  clones. `cpu_level` in the v3 ELF object has 0 VEX/EVEX instructions.
  `llvm-readelf` parses `isanote.c`'s source-embedded note as "x86 ISA
  needed: x86-64-baseline, x86-64-v2, x86-64-v3".
- `sh -n` passes on `linux_run.sh`, `isanote.sh` and `fmvdarwin.sh`.
  `linux_run.sh` itself has never run: there is no x86 Linux box here.
- Mac timings: unpinned, load average 4.8-7.5, directional only.

## Findings (detail in isa_selection.md §0)

1. Selection on a cached word costs about a direct call. An inline
   baseline arm behind a flag costs about the inline kernel. Querying the
   OS on every call (`sysctlbyname`) costs ~930 ns.
2. An artifact cannot cache the word itself. The cheap options left are
   libgcc's `__cpu_model`, the loader's GOT slot, or the caller's word.
   "Check at the first call" means "check at every call".
3. On Darwin, `__builtin_cpu_supports` answers 0 for every feature (Apple
   clang 21, LLVM clang 23). gcc-16 on darwin does not have it.
4. Apple clang lowers multiversioning on Mach-O to a dyld
   `__func_variants` table. LLVM clang lowers it to a lazily written
   `__DATA` pointer. R1's finding 5 is narrowed: no dispatch in emitted
   code by default, because the lowering depends on the toolchain.
5. A wide kernel cannot inline into baseline code. A per-call switch is
   B1b at best, and the remedy is to declare the level for the whole
   matcher.
6. `#if __AVX2__` does not change per `target_clones` clone, which is why
   RB-10 exists.

## Owed

On a quiet ubuntubudu, from a checkout at this branch (or at main after
merge), run:

    sh docs/design/memfn/probes/linux_run.sh

It writes `build/memfn_linux/<stamp>/`. The completion line is the last
line of `run.log`: `MEMFN-LINUX-RUN COMPLETE <dir> fails=<n>`. It takes
about 15 minutes, pins to CPU 2 (`CPU=` to change) and uses `gnutimeout`.
It answers U-1 and U-8 (R1) and U-9..U-12 (R1b). Archive the transcripts
into `docs/design/memfn/probes/out/` and fill isa_selection.md §1.1's
x86 column and §1.2.4's loader rows.

## Disclosure

At spawn I inherited the session-root CLAUDE.md and the manager's memory
index; I treated them as context. One scope slip: a `-dM -E` probe briefly
wrote `/tmp/x.c` (a 26-byte stub). I deleted it within the same minute;
nothing else was written outside the worktree and the session scratchpad.

## Resume point

The Q4-Q6 rulings and the Linux numbers are the next inputs. Nothing in
this lane is half-built.
