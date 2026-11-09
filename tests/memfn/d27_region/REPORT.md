I ran 8,154 checks: 8,141 passed and 13 failed. That covers what match_api.md §6.3.10, §10.7¶4 and §6.3.12, tuning.md §2.43, limits.md §8.3 and cli.md §1.24/§2.16/§1.10 promise a caller, tested against the cell's prebuilt `build/pcrec` (0.2.0-beta, abi 98). The harness blocked writing `d27/REPORT.md` as a report file, so its content is below for you to place. `run.sh` and the case files are in the cell under `d27/`.

## Summary

`d27/run.sh` exits 0 only if every check passes and prints `checks passed: 8141` / `checks failed: 13`. It takes about 2 minutes at 4 jobs under nice. Every compile and run goes through `gnutimeout` (the bare `timeout` here is uutils), and build products go under `$D27_OUT`. The targets come from `--list-cpu-targets`: `generic`, `x86-64` and `x86-64-v3` for this family, plus `armv8-a` for the refusal cases.

- **Self-checked control:** with `D27_CONTROL=1` the deliberately wrong expectation (the default artifact's `TARGETS` == `amd64:x86-64-v3`) is added as an ordinary check, and the run reports 14 failures, the new one observing `"none:generic"`. Two checks run every time to show the stamp check and the answer comparator catch a wrong expectation.
- **Everything else held**, including the blind spots you named. A consumer file includes the artifact and then uses its own:
  - SSE2 intrinsics;
  - AVX2 intrinsics (directly where its flags allow, else in its own `target("avx2")` function);
  - fortified `memcpy`/`strlen`/`memchr` under `-D_FORTIFY_SOURCE=2 -O2`.
- **Combinations covered:**
  - a second artifact for another target, in both orders;
  - the consumer's own headers before and after the artifacts;
  - gcc and clang at -O0, -O2, -O3, -Os, with -fPIC and with -flto;
  - consumers built with `-march=x86-64`, `-v2`, `-v3` and `native`;
  - consumers built with `-mno-sse2` and `-mgeneral-regs-only`.
- **No target macro leaked out of a region:** `__AVX2__`, `__SSE4_2__` and `__BMI2__` after the include match the consumer's own flags.
- **The guard refuses** gcc/clang `-m32`, gcc `-mx32` and `clang --target=aarch64`, with the guard as the first error. It also refuses the `armv8-a` artifact on the host compilers.
- **Answers** equal python3 `re` at every start position of my own subjects.

## Cases by paragraph

Counts are checks; failures in parentheses.

- **§6.3.10¶1, ¶8, ¶12** (448, 0): the six count stamps each appear once, in order. GUARDED comes directly after LIBC and MEASURES directly after FINDINGS.
- **¶4** (about 940, 0):
  - MEMFN_FORMS is `"none"` at the default.
  - It is `"none"` exactly when the artifact (`.c` and `.h`) equals its `-fno-memfn-simd` compile apart from the target's text.
  - x86-64 never shows the 32-byte level.
  - `(?i)needle` reads `vrun@w16` at x86-64 and `vrun@w32+w16` at v3, the spec's own spellings.
- **¶5, ¶7** (280, 0): MEMFN_LIBC is in the right format and equals the undefined functions of the `gcc -O0 -fno-builtin` object, for plain and `--emit-main` artifacts.
- **¶8, ¶9, limits §8.3¶1, ¶3** (about 520, 0):
  - The count is 16 hex digits with `ULL`.
  - It is 0 at the portable target and nonzero at every family target.
  - It stays within the stated bounds.
  - Where FORMS is `"none"` it equals the bytes of the added lines exactly: 469 at x86-64, 615 at v3, 165 at armv8-a. Compounds add 20 for the part's `<string.h>`.
  - Neither `-fno-comments` nor `-p` changes it.
- **¶14** (448, 0): `_TARGETS` appears once, after `_COMPOUND`, with the right value; no part carries one.
- **¶15** (about 4,950, 12 failures):
  - Text checks:
    - The guard comes before every `#include`, and its `#error` names its condition.
    - x86-64 and v3 have a region; `armv8-a` has the guard alone; generic has neither.
    - The region opens before the first function and closes after `rx_info`, with only `main()` after it.
    - There is no CPU `#if` outside the guard.
    - There is no `#include` inside the region: this is where F1 fails.
  - Consumer builds:
    - 1,680 checks with one artifact per consumer (included, consumer headers first, or a separate file with the object linked);
    - 594 checks with two artifacts in one file, for every ordered pair of targets;
    - 2,100 checks under the special consumer flags;
    - 504 checks of the `--emit-main` exit codes 0/1/2.
- **§10.7¶4** (360, 0): with `-mno-sse2` and `-mgeneral-regs-only`, the x86-64, v3 and default artifacts compile and answer correctly under both compilers.
- **Guard refusal, ¶4/¶15** (84, 1): the refusals in the Summary all hold. `armv8-a` passes its own guard under `clang --target=aarch64`. The default artifacts compile under `-m32` and aarch64, except the VM one under `-m32` (F2). These probes use stub headers.
- **tuning §2.43¶1, ¶3e through the library** (8, 0):
  - A CPU list is refused without the force bit, with the deny bit, and with deny plus force.
  - Force with no list gives `amd64:x86-64`; force with a list gives exactly that list; `"generic"` gives `none:generic`.
- **§2.43¶3b** (92, 0):
  - A SIMD row's deny at the default does nothing.
  - At v3, `no-vrun-w32` and `no-vrun-w16` drop their own level.
  - All five per-form denies keep the answers.
- **§2.43¶4** (14, 0): `-fno-memfn-simd` and `=generic` both give the default artifact byte for byte.
- **cli §1.24** (about 470, 0):
  - `-fmemfn-simd`, `=x86-64`, `=amd64` and `=x86-64,x86-64` give the same artifact.
  - Tokens match without regard to case.
  - The later spelling wins.
  - Each refusal exits 1 with a `pcrec: ` message and writes no artifact.
- **cli §2.16** (11, 0): the listing's columns, families listed first, one host row (amd64, default x86-64), and refusal of a pattern or `-o`.
- **§6.3.12¶1, §3.7¶2** (112, 0): the compound cases really are compounds.

## Failures found

**F1: in a compound artifact, the region contains `#include` lines** (§6.3.10¶15: "The region holds no `#include`"). 12 failures: c1, c2, c3 × x86-64, x86-64-v3 × plain and `--emit-main`.
```
build/pcrec -p cq -fmemfn-simd=x86-64-v3 -o cq.c --pattern '^abc|xyz$'
```
- **Observed:**
  - `#include <string.h>` at line 23, before the region opens (lines 24–29).
  - A second `#include <string.h>` at line 226, inside the region (it closes at lines 525–529).
  - Under `--emit-main` the region also holds `#include <stdio.h>` and `<string.h>` at lines 97–98 and 261–263.
- **Impact today: none.** Each header was already included before the region, so the second include does nothing, and every consumer build containing a compound compiled and answered correctly.
- **Risk:** the next part that includes a header the prologue doesn't, or one without an include guard such as `<assert.h>`, would be read inside the region. That is exactly the break ¶15 warns about.

**F2: a default VM artifact does not compile for a 32-bit target** (¶4: "`none:generic` runs on any machine"; §2.43¶2: "the artifact runs on any target").
```
build/pcrec -p v1_generic --engine=vm -o v1_generic.c --pattern '(?i)needle[0-9]{3}'
gcc -m32 -ffreestanding -nostdinc -isystem $(gcc -print-file-name=include) -isystem d27/cases/stubinc -fsyntax-only v1_generic.c
```
- **Observed:** `static assertion failed: "V1_GENERIC_RESUME_FRAME_SIZE disagrees with sizeof(v1_generic_frame) ... recompile the pattern with a pcrec built for this target."`, and the same for `_TRAIL_FRAME_SIZE`.
- **Comparison:** the DFA default artifacts pass the same probe. The VM one passes under aarch64, which is also 64-bit.
- **Assessment:** the refusal is clean and explains itself, so the spec most likely overstates the promise.
- **Probe limit:** this box has no 32-bit sysroot, so it is a syntax-only check with stub headers; nothing was linked or run 32-bit.

## Spec findings

- **S1 (with F2):** "runs on any machine/target" doesn't say that a VM artifact is tied to the pointer width of the machine pcrec ran on, through its frame-size asserts. §10.4 publishes those sizes but never ties them to the target.
- **S2:** ¶15 says a target whose features are its family's baseline has no region, only the guard (`armv8-a`). But `x86-64` is the amd64 baseline and has a region (`target("sse2")`), and §10.7¶4 relies on that region. The two sentences disagree on what "baseline" means; the current behaviour is the useful one.
- **S3:** ¶9 says the count "is the artifact's size beyond its SIMD-off compile". The whole file actually grows by 1 more byte at armv8-a and 3 more at v3, because the `_TARGETS` value is longer than `none:generic`. The stamp itself equals the added lines exactly. §2.43¶4 already says "the stamp aside"; ¶9 should too.
- **S4:** limits §8.3¶3 bounds each `vrun` row separately, but ¶4 says form ids must never be parsed. A caller can't apply a per-row bound without parsing `vrun@w32+w16`. The suite gives each token both rows' bounds.
- **S5:** `-fmemfn-simd=generic,x86-64` is refused as "mixes families", although the portable target has no family (cli §2.16¶1). That is reasonable, but the spec doesn't say it; I recorded it without judging.
- **S6:** "beside the `rx_info` definition" (¶1) can't be tested, so I checked only the order.
- **S7:** §2.43¶3e's "SIMD off with a list is refused" can't be reached from the command line (§1.24¶4: the later spelling wins), only through the library, where it holds.
- **S8:** two artifacts for different targets in one file work at the same abi. The header's abi `#error` covers different abi numbers; ¶15 could point to it.

## Disclosure

- **Injected at spawn, not asked for:**
  - `~/.claude/CLAUDE.md` (security rules), which does not touch the subject.
  - The project root `CLAUDE.md`, which mentions the memfn kit and D146/D147 but states no fact of this contract.
  - The memory index, which touches the subject lightly ("`-fmemfn-simd` OFF", and a note that the dev box CPU has AVX2 and AVX-512). I took CPU features from `/proc/cpuinfo` instead, and no expectation comes from the index.
  - The list of agent names in the session (names only).
- **Hooks:** a hook blocked my first two commands, which tried to `cd` into the cell; I used absolute paths after that.
- **Beyond the named paragraphs, inside the allowlist:**
  - `lib/pcrec.h` comments and tuning.md §2.43¶3e name `src/gen/memfn_targets.c` and `src/gen/emit_dfa.c`; I did not open them.
  - I read `lib/pcrec.h` only for `memfn_simd`, the flag bits and `pcrec_compile`.
- **The cell is not git-free:** it contains a `.git` directory, though the brief describes it as non-git. I did not list, read or query it.
- **Generated output:** I read pcrec's output to fit my text recognizers to its spelling (where the pragma push/pop and the guard `#error` sit). That is the compiler's output, not its source, and each such check is phrased in the spec's terms.
- **Not read:** `src/`, `tests/`, `memfn/`, `scripts/`, other worktrees, git history, or the main tree.
- **Writes:** only under the cell's `d27/` and `/var/tmp/pcrec-pcrec/scratch/d27region/`.

The one-check-per-row result table is `/var/tmp/pcrec-pcrec/scratch/d27region/run/results.tsv`.

Files are in /home/pcrec/projects/pcrec/worktrees/d27region-cell/d27:
- run.sh
- lib/d27.py
- cases/patterns.tsv
- cases/consumer.c
- cases/lib_options.c
- cases/stubinc/string.h