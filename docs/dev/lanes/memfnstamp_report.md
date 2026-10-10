# memfnstamp — [MEMFN] R-3 part 2, R4a′: the kit's two stamps (PRE-BUMP)

Lane `memfnstamp` (kit session, opus), 2026-10-05. Branch
`lane/memfnstamp`, from `lane/memfn-r4a2` `090020a2`. Request:
`memfn/docs/requests.md` R-3 part 2. Design: integration.md rev 4.7
§R4.3.3, §18, §10.5, §17.6, §22; D147 addendum 10 (Q53, Q55); D81; D80.

**Status: everything except the abi bump is built and validated on the Mac
(directional).** The bump (abi 62 → 63 once START-SET stage 2 has merged; the
number current at landing + 1) and its grep-found re-pins are a separate,
LATER commit on this branch, after the kit session merges main. §8 is the
exact procedure.

## 1. What landed

- **Kit** (`memfn/`): `mf_art_note_libc(art, name)` (the libc record's
  writer: a sorted, distinct name list on the art; a non-identifier is
  refused loudly) and `mf_stamps(art, sink)` (two `sink->stamp` calls,
  `MEMFN_FORMS "none"` then `MEMFN_LIBC "<names>"|"none"`). Declared in
  `memfn.h` with their contract; `kit.h` gains the list.
- **pcrec** (`src/gen/memfn_stamps.c`, new): `pcrec_emit_memfn_mark` (both
  engines, one line right after `<PREFIX>_RUN_WORDS`) and
  `pcrec_memfn_stamps_render` (the driver's finishing pass, called in
  `compile_driver` once per attempt after the engine emitter and the comment
  balance check, BEFORE the size measurement).
- **C11**, `make test-memfn-stamps` (in TEST_SECTIONS):
  `tests/memfn/run_libc_census.sh` + `libc_census.py`.
- **Mech arm `memfnstamps`** and rows **S513-S517**.
- **Spec**: `docs/spec/match_api.md` §6.3, the two stamps (D80).
- **The mover census instrument**: `tests/memfn/stamp_mover_census.py`.
- **Re-pins for the two lines** (§7): `m5_stage1_stamps.tsv`, the resource
  pin, the recursion-identity FILEPIN.
- CLAUDE.md: `src/gen/`, `tests/memfn/`, `tests/mech/`, `memfn/src/`,
  `memfn/include/`; `docs/testing.md` (runtime); this report's index row.

## 2. The mechanism: (b), a finishing pass over the whole artifact

**Choice.** The emitters write a MARK (`"\x01M\n"`) where the stamps go;
after the whole artifact exists, `pcrec_memfn_stamps_render` scans the
finished `csb` (and `hsb`, the header, which carries no calls today) for
libc calls, notes each via `mf_art_note_libc`, has `mf_stamps` render the
two lines through an `mf_sink` whose `stamp` op is `pcrec_sb_stamp_str`, and
splices them over the mark.

**Why (b).** Q53 makes the record a WHOLE-ARTIFACT inventory: the search
code, the variable resolver's `strlen`/`memcmp`, `--emit-main`'s
`printf`/`fprintf`/`strlen`, `--trace`'s `fprintf`. Under (a) every emitter
that spells a libc call (about 30 string sites across `emit_dfa.c`,
`emit_vm.c` and `runcmp.c`, multi-line formats included) would carry a second
spelling of the same fact, and a new site that forgets its note is silently
missing from the record. (b) reads what was actually written. It is the
prefix render's shape ([K79], core/internal.h): a placeholder in the text,
rendered on the finished buffer. The design's `mf_art_note_libc` stays the
WRITER (§R4.3.3 "Coverage"); only its caller changed, from one call per
pending site to one finishing pass. When delegated sites exist the kit
records its own calls on the same art, and the set union is idempotent.

**Placement and timing.** The lines sit right after `<PREFIX>_RUN_WORDS`
(both engines; FINDINGS/RUN_WORDS precedent: written after the engine body).
The pass runs on every attempt BEFORE `emit_size_measure`, so the size term
measures the artifact it ships, and the ST_FINAL re-emission identity
control compares the stamped text.

**Failure modes, stated.**
1. **A libc function missing from `libc_names`** (C17 `<string.h>`,
   `<stdio.h>`, `<stdlib.h>`, `<ctype.h>`, plus the POSIX/GNU string
   functions) is not recorded. C11 reports it the first time a corpus
   artifact calls it, because C11's names come from the object.
2. **A length spelled other than as a literal** (`sizeof w`, a macro) on a
   1-8 byte `memcpy` is recorded as a call by the pass, while the compile
   folds it: C11 fires, and the pass is taught the spelling.
3. **A call inside an uninvoked macro body** would be recorded but not
   compiled. None exists today: the `--trace` stream (every trace macro)
   reads equal.
4. **ctype under glibc**: `isalpha` is a macro over `__ctype_b_loc`; an
   artifact that used it would read `isalpha` here and `__ctype_b_loc` in
   the object. No artifact uses ctype; C11 would fire if one did.
5. **A missing or doubled mark** is an internal error (`pcrec_ctx_fail`); a
   mark left unreplaced cannot reach a caller, because `\x01M` fails the
   prefix render as a stray lead byte.

The mf_art is created inside the pass (one per attempt, in `cx->arena`),
since no emitter calls the kit yet. R4c, whose delegated sites call
`mf_emit` during emission, moves its birth to the attempt's start.

## 3. The stamp grammar

```c
#define <UPPER>_MEMFN_FORMS "none"
#define <UPPER>_MEMFN_LIBC "none"            /* or "memchr,memcmp" */
```

- One line each, on EVERY artifact of both engines (D81), in that order,
  directly after `<UPPER>_RUN_WORDS`. Written through `pcrec_sb_stamp_str`.
- FORMS: `none` (constant until R4f, Q55); its grammar for later ids is the
  spec's (`ID@LEVEL+LEVEL`, opaque).
- LIBC: `none`, or names sorted in byte order (`strcmp`), distinct,
  comma-joined with no space. Source-level inventory; one exclusion
  (`memcpy` of a literal 1-8 bytes); stdio data objects are not functions.
- No kit version, no `MF_VOCAB`.

Values observed on the corpus: `none`, `memchr`, `memchr,memcmp`,
`memcmp,strlen`, `memchr,memcmp,strlen`; with `--emit-main`
`fprintf,memchr,memcmp,printf,strlen`; with `--trace` `fprintf,memchr`.

## 4. C11 — design, independence, population, runtime

**What it asserts, per artifact:** exactly one FORMS and one LIBC line
(presence, counted per family); FORMS is `none`; the LIBC value obeys the
grammar; and the LIBC set EQUALS the control set.

**The control.** The artifact is compiled `gcc -O0 -fno-builtin
-fno-stack-protector -U_FORTIFY_SOURCE -std=gnu11 -c` with a prelude
(`-include`) that redefines `memcpy` so that a call whose length the
COMPILER folds to a constant 1-8 goes to `c11_idiom_memcpy` instead; `nm -u`
of the object gives the undefined names; the platform decoration is learned
from a probe object (darwin `_`, glibc none); the control set is those names
minus `c11_idiom_memcpy` and minus the stdio data objects (`stdin`,
`stdout`, `stderr`, `__stdinp`, `__stdoutp`, `__stderrp`). Any other
undefined name counts as a call.

**Independence.** No list is shared with the producer: the producer's is
`libc_names` in `memfn_stamps.c`, which C11 never reads; C11's only lists are
the data objects (which the producer has no notion of) and the floors. The
idiom rule is applied by the compiler's constant folding, the producer's by
a text test of the literal, so the two implement Q53's rule independently;
S515 shows a divergence in the producer fires.

**Population.** Deterministic: the `--list-source` corpus (3,523 distinct
patterns, via `scripts/emit_sweep.py`'s enumeration), each pattern kept iff
`sha1(stream \0 pattern) mod N == 0`, so a new corpus pattern never
reshuffles the rest. Streams: default engine (1 in 6), `--engine=vm`
(1 in 12), `--emit-main` (1 in 60), `--trace --engine=vm` (1 in 60), and
EVERY `.rxt`/`.rxtin` composition file with `-o DIR` (its artifacts carry a
separate header, which the pass also scans). Prefix `-p cxi`, so the lines
follow the prefix render.

Measured (Mac, gcc-16, tip of this lane):

| count | full | `--quick` (default stream only) |
|---|---|---|
| artifacts | 918 (51 composition) | 533 |
| families | dfa 353, vm 565 | dfa 293, vm 240 |
| LIBC `none` | 344 | 224 |
| idiom-`memcpy` artifacts | 95 | 42 |
| calls | memchr 529, memcmp 48, strlen 47, printf 44, fprintf 96 | memchr 305, memcmp 26, strlen 2 |
| refused patterns (not artifacts) | 107 | 72 |

K35 floors (literals in `run_libc_census.sh`, ~10 % under): full
artifacts 820, dfa 310, vm 500, composition 45, none 300, idiom 80,
memchr 470, memcmp 40, strlen 40, printf 38, fprintf 85; quick artifacts
480, dfa 260, vm 215, idiom 37, memchr 275, memcmp 23.

**UNREACHED, printed as such:** the FORMS half's "none implies identical to
the `-fno-memfn-simd` compile" (no `-fmemfn-simd` switch exists until the
first SIMD-on form, Q55/R4e′). A non-constant `memcpy` sabotage is
UNREACHED (no corpus artifact calls one; the calls line shows no `memcpy`),
so §17.6's third `[rev4.6]` row is not built.

**Runtime.** ~40 s wall full (8 jobs), ~15 s `--quick`.

## 5. Sabotage rows (arm `memfnstamps`), each run SOLO through mech

`CC=gcc-16 bash tests/mech/run_sabotage_matrix.sh S51N` at `ef94e86d`
(S516 re-run with KEEP=1 at `fdefbfa9` to read the arm log):

| id | plant | results | verdict |
|---|---|---|---|
| S513 | `memchr` dropped from `libc_names` | reach:ok(1/1), memfnstamps:44fail/3pass | DETECTED |
| S514 | every artifact notes `strlen` | reach:ok(1/1), memfnstamps:44fail/3pass | DETECTED |
| S515 | idiom exclusion narrowed to 1-2 bytes (`v <= 2`) | reach:ok(2/2), memfnstamps:8fail/5pass | DETECTED |
| S516 | VM emitter writes no mark + the no-mark internal error disabled (two sites) | reach:ok(2/2), memfnstamps:44fail/3pass | DETECTED |
| S517 | `memcmp` dropped from `libc_names` | reach:ok(1/1), memfnstamps:27fail/5pass | DETECTED |

Each `mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0,
unreached: 0, anomalies: 0, oracle-skipped: 0)`. S516's arm log shows the
presence check itself firing on VM artifacts (`presence: 0 FORMS, 0 LIBC
lines`), with families `dfa 293, vm 240` (the VM artifacts still compile).
Brief mapping: (a) S513 (also §17.6's "forced to `none` on a memchr
artifact": a memchr-only artifact reads `none`), (b) S514, (c) S515,
(d) S516, plus S517 (§17.6's `memcmp` row).

## 6. The census (pre-bump)

`python3 tests/memfn/stamp_mover_census.py --ref 090020a2` (base =
lane/memfn-r4a2's tip; working = this lane's build). It drives
`scripts/emit_sweep.py`'s own machinery (reference build from `git archive`,
corpus enumeration, the argv/IR/composition streams) and replaces its
identical-or-mover verdict with a classifier (header of the script): a `.c`
must be the old text plus EXACTLY two adjacent lines, FORMS then LIBC,
directly after `RUN_WORDS`; listings and headers must not move.

First run (106 s), 4,512 pattern rows and 360 composition files:

| stream | identical | stamps | OTHER | both-refuse |
|---|---|---|---|---|
| c-default | 0 | 4065 | 0 | 447 |
| c-vm | 0 | 4066 | 0 | 446 |
| comp-c | 0 | 50 | **1** | 0 |
| comp-h | 51 | 0 | 0 | 0 |
| emit-ir-vm | 4066 | 0 | 0 | 446 |

**The one OTHER, reviewed:** `tests/uprops/size_ladder_prefilter_drop.rxt`'s
`rx.c` also moves `#define RX_VM_PREFILTER_WHY "size cap retry, hybrid
1028494 > 1000000"` to `1028553`: that stamp QUOTES the measured size of the
DISCARDED hybrid attempt, and that attempt now carries its own two lines
(+59, LIBC `none`). This follows from rendering the stamps before the size
measurement (§2), which is the intended order: the size term measures what it
would ship. No test pins the number; no artifact crossed a cap (every other
artifact is exactly `stamps`). The classifier now names this class,
`stamps+size` (a `_PREFILTER_WHY` size quote whose N grew by 59-120, nothing
else), so the bump step's re-run reads clean rather than re-reviewing it.
Second run, with the classifier extended (CLEAN, exit 0):

| stream | identical | stamps | stamps+size | OTHER | both-refuse |
|---|---|---|---|---|---|
| c-default | 0 | 4065 | 0 | 0 | 447 |
| c-vm | 0 | 4066 | 0 | 0 | 446 |
| comp-c | 0 | 50 | 1 | 0 | 0 |
| comp-h | 51 | 0 | 0 | 0 | 0 |
| emit-ir-vm | 4066 | 0 | 0 | 0 | 446 |

Every `.c` artifact moved by exactly the two lines (one also moves its
discarded-attempt size quote, above). Headers and listings are unmoved.

## 7. Pins

**Re-pinned now, for the two lines** (one commit):
- `tests/codegen/manifests/m5_stage1_stamps.tsv`: all 12 `EMITTED_BYTES`
  rows, +59 (`none`) / +61 (`memchr`) / +68 (`memchr,memcmp`): 30 bytes of
  FORMS line plus the LIBC line. Comment in `run_cpset_structure.sh`.
- `tests/resource/run_resource_tests.sh`: `a{5,25000}` 762604 → 762665
  (+30 +31).
- `tests/codegen/run_recursion_identity.sh`: FILEPIN → this lane's last
  `src/`/`memfn/` code commit (self-pin convention).

**Not re-pinned, with reason:** `docs/dev/artifact_size_log.tsv` is a
measurement log that `make test`'s full `test-corpus` run rewrites itself
(`tests/size/run_size_log.sh`); its only check is the tripwire's 1,400,000
byte max (corpus max 811,724, +≤ 70 bytes). It has not been refreshed at
any abi event since 2026-09-28 (abi 58-61 all moved it); the Linux
`make test` at landing produces the new file for the manager to commit.

**Suites that read bytes and did NOT move** (run green, Mac): test-codegen
(save the pre-existing darwin red `run_inline_capability.sh`'s
`nm could not read arm_a.o`, reported pre-existing by R4a's response),
test-registry, test-rxtsource, test-cli.

**Will move AGAIN with the abi digit** (the bump step):
- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI`;
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT`;
- `tests/codegen/run_recursion_identity.sh` FILEPIN (again: the bump is a
  `src/` change; the `ABI_SUBJ`/`ABI_PIN` tripwire fires until it moves);
- `docs/spec/match_api.md`: the K80 `#error` text (`(abi N)`), the abi paragraph's (match_api.md §6¶17; entry in docs/dev/history/abi_changelog.md)
  "`rx_info.abi` is `N`" paragraph and its change-log entry for R4a′, and
  the new §6.3 entry's heading "(the stamps' own `abi` event)", which gains
  the number;
- NOT the byte counts: the digit keeps its width (62 → 63), so
  `m5_stage1_stamps.tsv`, the resource pin and the size log do not move
  again (verify, §8 step 4).

## 8. The bump procedure (the later step)

At the bump commit, with `N` = main's abi after the merge (62 expected) and
`M = N + 1`:

1. Find every reader of the number (D76/D94; the list below is a floor):

        git grep -nE 'PCREC_ARTIFACT_ABI [0-9]|ABI_EXPECT=|\(abi N\)|abi N\b|PCREC_RX_ABI_H[^0-9]*N\b|\.abi = N|ABI_SUBJ|FILEPIN=' \
            -- src cli lib tests docs/spec Makefile memfn
        git grep -nE '`abi` N\b|is `N`' -- docs/spec
        git grep -nE 'EMITTED_BYTES|762665' -- tests docs/spec lib src Makefile
        git grep -nlE 'emit_sweep|norm\(' -- tests docs/dev/optloop

   (substitute the digit for `N`). Provenance comments "(abi N)" in
   CLAUDE.md files and design docs do not move.
2. Edit: `PCREC_ARTIFACT_ABI M`; `ABI_EXPECT=M` with the bump's cause in
   its message (copied FROM §6); `match_api.md §6¶17` paragraph ("is `M` …
   [MEMFN] R4a′ added the two kit stamps") and change log, the K80 `#error`
   example, and §6.3's R4a′ heading gains "`abi` M".
3. Commit the src change, then re-pin `run_recursion_identity.sh` FILEPIN to
   that commit (self-pin convention) in a follow-up commit on the same
   branch, or as one commit whose FILEPIN names the parent if the manager
   prefers.
4. Re-run the census WITH the digit: `python3
   tests/memfn/stamp_mover_census.py --ref <main-at-merge> --abi N:M`;
   expect every `.c` artifact in class `stamps+abi`, and every IR listing
   and composition header `identical` or `abi` (digit-only). The run fails
   on any `OTHER`, on a `.c` without the two lines, and on a listing or
   header that moved by more than the digit.
5. The suites that count (D94 addendum): `make test-codegen
   test-registry test-rxtsource test-cli test-cpset-structure
   test-resource test-recursion-identity test-memfn-stamps`, then the Linux
   `make test` through the executor; commit the size log it rewrites.
6. The bench inbox note (§22 R4a′): the two stamps, the source-level
   inventory sentence, the build-recipe attribution sentence.

## 9. Charter vs committed

| brief item | status |
|---|---|
| 1 kit side (`mf_stamps`, `mf_art_note_libc`) | DONE |
| 2 pcrec side, every family, mechanism chosen + failure mode | DONE (b), §2 |
| 3 C11 LIBC half in `make test`, independent, floored, darwin `_`, FORMS UNREACHED | DONE, §4 |
| 4 sabotage rows (a)-(d), mech solos DETECTED + reach ok | DONE, S513-S517, §5 |
| 5 spec hunk | DONE, match_api.md §6.3 |
| 6 census, classifier, counts | DONE, §6 (1 reviewed size-quote mover) |
| 7 re-pins now + list moving with the digit | DONE, §7 |
| 8 CLAUDE.md + report index | DONE |
| validation: make, make strict | DONE (strict clean) |
| validation: test-codegen, registry, rxtsource, cli | DONE (§7) |
| validation: C11, memfn link/manifest/g2 | DONE, §10 |
| NOT done by design: abi bump, abi-number readers | the later step, §8 |

## 10. Validation log (Mac, directional)

All runs used `CC=gcc-16`. The logs are in the worktree's `build/scratch/` (gitignored).

| run | result |
|---|---|
| `make`, `make strict` | clean (strict: "whole tree compiles clean with -Werror -Wshadow") |
| test-codegen | 201 s; every group 0 failed except `run_inline_capability.sh`'s `nm could not read arm_a.o`, a darwin-only red that predates this lane (R4a's response, `memfn/docs/responses.md`) |
| test-registry | rc 0, 234 s |
| test-rxtsource | rc 0, 81 s |
| test-cli | rc 0, 20 s |
| test-cpset-structure | red before the re-pin (12 EMITTED_BYTES rows), then rc 0, 41 s |
| test-resource | red before the re-pin (762665), then rc 0, 271 s |
| test-recursion-identity | red before the re-pin ((B) whole-file against b55d5554), then rc 0, 1910 s, against FILEPIN 07ccd3cc |
| test-memfn-link | rc 0 |
| test-memfn-manifest | rc 0 (22 passed, 0 failed) |
| test-memfn-g2 | rc 0, 51 s |
| test-memfn-stamps (C11) | rc 0, 32 s, 918 artifacts |
| mech S513-S517, solo | 5/5 DETECTED, reach ok |
| mover census | CLEAN (§6) |

The full `make test` was NOT run. That is per the brief: the verdict is the Linux run after the bump.

**Open items.**
- The abi bump step (§8).
- The bench inbox note, which the brief assigns to the bump event.
- R4c moves the `mf_art`'s birth to the attempt start, once emitters call the kit (§2).
- C11 cannot yet check a non-constant `memcpy`, because no corpus artifact calls one.
- The FORMS half is UNREACHED until R4e′.
