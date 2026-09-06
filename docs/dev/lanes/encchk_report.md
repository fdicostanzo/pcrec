# lane encchk — [ENCCHK-DD12A] report

Charter: docs/dev/plan.md's `[ENCCHK-DD12A]` row, chartered at K52's filing
(docs/dev/known_issues.md). Three deliverables: rebuild DD12a(i)'s instrument
(K52), give the cwmax floors a mech row, and give
`run_encoding_checks.sh` a mech suite token so S229 (and S-U8) score on their
real detector rather than on `harness`/`codegen` alone.

Branch: `lane/encchk`, worktree `worktrees/encchk`. Not merged to main.

## 1. DD12a(i) rebuilt (K52)

**The old instrument.** Compiled both artifacts to `.o` and diffed
`.text`+`.rodata` bytes with `objdump -s -j .text -j .rodata`. VACUOUS on
darwin (`-j .text` matches nothing on Mach-O — `.o` sections there are
`__TEXT,__text` — so every historical green was empty-vs-empty) and
MIS-SCOPED on Linux (the four encoding residual entries and, since K49, the
retry advance are legitimate per-encoding text the whole-object scope cannot
admit — a real run there reports every artifact "differing", restating the
seam's own design as a failure).

**The repair operates on emitted SOURCE TEXT, never on an object.** Both
artifacts are re-emitted with the SAME prefix (`rx`) into per-encoding
subdirectories sharing the SAME basename (`rx.c`) — this project's own
documented trap (`run_trie_identity.sh`'s `gen_a`/`gen_b` note: a differing
`#include "<name>.h"` line dominates an otherwise-identical diff) avoided by
construction rather than by a post-hoc filter. An empirical same-prefix diff
of a real lookbehind+capture pattern (`(?<=(a)(b))c(d|e)*`) showed the
*entire* legitimate difference is three things: the K49 retry-advance splice,
the two residual entry bodies present on that witness (`next_pos`,
`back_step`), and the `.encoding` scalar in the `rx_info` initializer — 59
diff lines, fully accounted for, nothing left over.

**Three named regions are excised from both texts before comparing**, each
anchored on text that is confirmed identical on both backends (never on
per-encoding prose):

1. Each of the four residual entries (`next_pos`, `back_step`, `bref_match`,
   `bref_match_caseless`) — found by its function SIGNATURE line (identical
   across backends, D58 P-1), with its own immediately-preceding descriptive
   comment swallowed too (that comment differs in prose per encoding — "byte
   encoding: one byte is one character..." vs "utf8 encoding: skip
   forward..." — and would otherwise show up as a spurious difference).
2. The [K49] retry advance splice, anchored on the SAME guard line the
   existing K49 advance-agreement check already uses
   (`if (attempt_position >= subject_length) return 0;`) through the
   enclosing block's own closing `    }`. Both anchor lines are kept,
   unchanged, on both sides; only the span between them is excised — which is
   why this works even though only the `utf8` artifact carries a comment
   there (the `byte` side's span is a bare `attempt_position++;` with no
   comment at all).
3. The `.encoding = N,` scalar — normalized (value replaced by a canonical
   placeholder) rather than deleted, since the line always exists and only
   the value differs.

**Why per-symbol object exclusion was rejected instead** (K52's own finding,
restated as the reason this design avoids it): under `always_inline` the
K49 advance's inlined body SMEARS across the VM entry chain at the object
level, so a symbol-table exclusion list can no longer name "the one function
this text lives in." Source-text excision, applied before any compiler sees
the file, has no inliner to smear across — the K49 splice is one physical
span in one physical function in the `.c` text regardless of what `-O2`
later does to it.

**(a) Non-empty by construction.** `next_pos` is unconditional on every
artifact (DD-12's own promise), so it is required to be found EXACTLY ONCE
per side on every compiled pair — zero is a hard FAIL. The other three
residuals and the retry advance are pattern-dependent, so three explicit
witnesses are added to the swept population (never trusted to the corpus's
luck): `a*` (unanchored, VM — forces the retry advance, reusing the K49
check's own witness), `(?i)(?<=a)(b)\1x` (DD12a(ii)'s own witness — forces
`back_step` + `bref_match_caseless`) and its case-sensitive twin
`(?<=a)(b)\1x` (forces `back_step` + `bref_match`). An aggregate floor
requires every one of the six counters (four residuals, the advance, the
`.encoding` field) to be reached at least once across the whole run.

**(b) The normalization count is pinned and printed**, per pattern: a
pattern whose byte and utf8 sides disagree on how many of a given region
each contains is reported by NAME (an "asymmetric" finding) even if the
final texts happen to agree elsewhere — this is not folded into the
aggregate pass/fail.

**(c) Darwin.** The whole instrument reads and writes only `.c` text — no
compiler, no object file, no `objdump`, on either platform. This is not a
loud SKIP naming a limitation; it is the SAME check on both boxes. Run on
this Mac (darwin/gcc-16) below; a Linux confirmation is owed to whoever runs
the merge battery.

**(d) Validation — the failing direction, demonstrated.** A throwaway
`git archive HEAD` tree (never the live worktree) had one line planted in
`src/gen/emit_vm.c`, immediately before the `_accept:` label — OUTSIDE every
named region above:

```
    if (v.cx->opt->encoding == PCREC_ENC_UTF8)
        sb_printf(c, "    /* SCRATCH-VALIDATION-PLANT: utf8-only text in the shared hot loop, outside DD12a(i)'s named regions */\n");
```

Rebuilt (`make -j4 CC=gcc-16`, clean), then run against a small mixed
pattern set (`abc`, `(a|b)+`, `a{2,5}b`, `(?<=(a)(b))c(d|e)*`, `^abc$`, `x*`,
`(a)\1`, plus the three explicit witnesses):

```
pairs compiled: 10, byte-only (utf8 refused): 0
excised totals: {'next_pos': 20, 'back_step': 6, 'bref_match': 4,
                 'bref_match_caseless': 2, 'advance': 10, 'encoding': 20}
diverging pairs (after normalization): 5
  FINDING pat=[(a|b)+] : TEXT DIFFERS after excision:
    ...
    +    /* SCRATCH-VALIDATION-PLANT: utf8-only text in the shared hot loop, outside DD12a(i)'s named regions */
  FINDING pat=[(?<=(a)(b))c(d|e)*] : TEXT DIFFERS after excision: ...
  FINDING pat=[(a)\1] : TEXT DIFFERS after excision: ...
  FINDING pat=[(?i)(?<=a)(b)\1x] : TEXT DIFFERS after excision: ...
  FINDING pat=[(?<=a)(b)\1x] : TEXT DIFFERS after excision: ...
exit: 1
```

The plant landed only on VM-selected patterns (5 of the 10), and the check
caught every one of them, naming the pattern and the exact leaked line — the
failing direction the old instrument was never shown at all. The plant was
never applied to the real worktree; it lived and died in
`/private/tmp/.../scratchpad/encchk/plant_tree`.

**Clean-tree run, this worktree, `ENC_MAX_BLOCKS=250` (the light local run
default), full log at
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/473e6e37-7956-4ed9-ba50-50a475f1a231/scratchpad/encchk/full_run2.log`:**

```
§8.5 ran 250 ASCII blocks (0 cc-skipped), 0 divergences
PASS: §8.5 byte and utf8 artifacts agree on every ASCII subject (250 blocks)
CHK3 ASCII stamp differences: 0
PASS: CHK3 every ASCII pattern's utf8 stamps equal its byte stamps
DD12a(i) pairs compared: 253 (byte-only: 0) — strict-identity bucket: 243, widens-under-utf8 bucket: 10
EXCISED next_pos=506  back_step=4  bref_match=2  bref_match_caseless=2  advance=182  encoding=506
PASS: DD12a(i) the engine minus its named encoding-owned regions is byte-identical
      between byte and utf8 artifacts on 243 strict-identity pairs
      (10 widens-under-utf8 pairs correctly exempted, source-text comparison,
      darwin and linux alike)
DD12a(i) widens-under-utf8 pairs differing (expected): 10 of 10
PASS: DD12a(ii) the seam's residual entries appear under identical signatures (3 entries)
PASS: K49 the emitted -e byte retry advance agrees with next_pos on all 10738 cells
PASS: K49 non-vacuity control: every -e byte advance IS pos + 1 (10738 cells)
PASS: K49 the emitted -e utf8 retry advance agrees with next_pos on all 10738 cells
PASS: K49 non-vacuity control: -e utf8 differs from pos+1 on 2268 of 10738 cells
PASS: S-U8 the utf8 MRL clamp stride is the encoded length
checks passed: 11
checks failed: 0
```

**A genuine finding surfaced mid-repair and had to be resolved before this
was trustworthy**, not merely a bug in the new instrument: the FIRST version
(no `widens_under_utf8` exemption) reported `checks failed: 1` with 10
diverging pairs, ALL ten patterns using `.` or a negated class (`.*\z`,
`[^c]{1,3}\z` and five siblings, `\G.`). Direct same-prefix diffs of
`[^c]{1,3}\z` and `\G.` (both saved in the scratchpad's `investigate/`
directory during the session, not committed) showed the class table growing
from 2 classes to 14 and the whole state machine growing with it (7 states
→ 28 on one witness) — a real, correct structural difference in the
compiled automaton, not a hot-loop conditional, because a negated class or
`.` means "any code point [not in the set]" and lowers to a class spanning
the whole encoded space under utf8, even when the SUBJECT stays ASCII. The
`widens_under_utf8` pattern-text classifier (independent of anything pcrec
computes, `lookaround_classify.py`'s own precedent) exempts exactly that
population from the strict claim while counting and flooring it — `WIDENS`
must be nonzero (never dead code) and `STRICT` must clear a floor of 150 (so
the exemption cannot swallow the whole population). §8.5's own answer
differential already covers correctness for the widens bucket; DD12a(i) now
states its scope honestly rather than asserting something false about it.

## 2. The cwmax floors' mech row (S230, S231)

`tests/mrl/CLAUDE.md`'s account of the 2026-09-05 K49-adjacent repair to
`cwmax_check.c` (the character-vs-byte unit mismatch, run_mrl_tests.sh §8)
named two population floors validated by hand at the repair and never
encoded as permanent mech rows: (i) the utf8 block population is nonzero,
(ii) at least one compared span's byte width exceeds its character width.

- **S230** (`tests/mech/sabotages/S230_cwmax_encoding_reader_dropped.sh`) —
  `cwmax_check.c`'s `encoding` directive reader resolves the name but never
  assigns it to the block (`b.encoding = e->id;` dropped), so every block is
  swept as `byte`. Trips floor (i) AND floor (ii) (there is no utf8
  population left to have a multi-byte span at all), and reproduces 40 real
  CHECK 2 violations on the whole corpus as a side effect (byte-parsed
  cwmax compared against character-tier oracle spans on the exact shapes
  `axis01_encoded_length.rxt` carries).
- **S231** (`tests/mech/sabotages/S231_cwmax_char_width_reverts_to_bytes.sh`)
  — `char_width`'s independent non-continuation-byte scan reverts to
  `return end - start;`, the literal pre-repair spelling. Trips floor (ii)
  ONLY (floor (i)'s population stays intact — this row's symptom is
  disjoint from S230's, which is why they are two rows) and reproduces
  EXACTLY 84 CHECK 2 violations on the whole corpus, matching the CLAUDE.md
  account's own historical figure to the digit.

Both carry `SAB_REACH` (build+run the real `cwmax_check.c` on the clean tree
against `tests/utf8/axis01_encoded_length.rxt`, requiring the real printed
counters) and `SAB_REACH_POP` (the `encoding utf8` directive count in that
same file, floored at 50 against a measured 64) — [MECH-REACH] from birth,
per the charter.

**Solo mech runs, tree `5991a6b2e60c57a4809ec921580cec9d4103623f`:**

```
S230  pop:tests/utf8/axis01_encoded_length.rxt:/^encoding utf8/=64(want>=50),
      reach:ok(1/1), mrl:1fail/26pass                              DETECTED
S231  pop:tests/utf8/axis01_encoded_length.rxt:/^encoding utf8/=64(want>=50),
      reach:ok(1/1), mrl:1fail/26pass                              DETECTED
```

Both `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0,
unreached: 0, anomalies: 0, oracle-skipped: 0)`.

## 3. `run_encoding_checks.sh`'s missing mech suite token

There was no `encoding` word in `run_sabotage_matrix.sh`'s closed suite
vocabulary — S229's own header already said so, naming
`run_encoding_checks.sh`'s advance-agreement section as its real second
detector and recording that the suite "is not wired into this matrix's
dispatch today." S-U8 carries the identical unfulfilled claim about the
clamp-stride probe.

Registered `encoding` (runs `tests/codegen/run_encoding_checks.sh` at its
own `ENC_MAX_BLOCKS` default), before the two rows that name it, per the
R31 C11 convention this file's own header states. Added the arm to both
S229 and S-U8's `SAB_SUITES`.

**Green baseline established BEFORE any solo sabotage run** (this lane's
own DD12a(i) rewrite changes the check count, so the pre-rewrite baseline
was stale and re-measured after landing — journal 2026-09-05 lesson 3, "a
dirty baseline gives a false NOW-DETECTED"): the post-rewrite, post-K37-fix
clean tree (commit `4081a775`) reads `checks passed: 11, checks failed: 0`
on `run_encoding_checks.sh` at `ENC_MAX_BLOCKS=250` (log above).

**Solo mech runs of S229 and S-U8 against that baseline**, tree
`f6f8a51b95b319a475c0980fb16caddb56df872e` (the commit at the time these
ran, one commit before the K37 fix — the K37 finding is a `run_codegen_tests.sh`
scoring artifact unrelated to `run_encoding_checks.sh`'s own checks passed/
failed count, which was already 11/0 at that commit too), full log at
`/private/tmp/claude-501/-Users-fdicostanzo-pcrec/473e6e37-7956-4ed9-ba50-50a475f1a231/scratchpad/encchk/mech_solo.log`:

```
S229  harness encoding  corpus:1fail/71pass,encoding:1fail/9pass          DETECTED
S-U8  codegen encoding  pop:tests/codegen/run_encoding_checks.sh:/RX_PRUNE_CLAMP_SPAN/=3(want>=1),
                        reach:ok(1/1),codegen:6fail/102pass,encoding:1fail/10pass   DETECTED
```

Both new arms fire (`encoding:1fail`) alongside their pre-existing detector
(`corpus`/`codegen`), confirming the previously-unfulfilled claim in each
row's own header — S229's advance-agreement section and S-U8's clamp-stride
probe are now SCORED, not merely named. Both
`== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0, unreached: 0,
anomalies: 0, oracle-skipped: 0)`.

## Validation summary

| deliverable | instrument shown to fail | commit |
|---|---|---|
| DD12a(i) rebuilt | scratch plant in emit_vm.c, `git archive` tree, never landed (transcript §1 above) | `f6f8a51b` (DD12a(i) itself); `4081a775` (K37 fix, no functional change) |
| cwmax floor (i) | S230, solo mech run, DETECTED | `5991a6b2` |
| cwmax floor (ii) | S231, solo mech run, DETECTED | `5991a6b2` |
| `encoding` mech arm | S229/S-U8 solo mech runs, DETECTED, against the real detector for the first time | `f6f8a51b` |

## Targeted validation run (delivery)

- `PCREC="$PWD/build/pcrec" CC=gcc-16 ENC_MAX_BLOCKS=250 bash tests/codegen/run_encoding_checks.sh`
  at commit `4081a775`: **checks passed: 11, checks failed: 0** (§1 log above).
- `bash tests/mech/run_sabotage_matrix.sh S230` / `S231` / `S229` / `S-U8`
  at commit `f6f8a51b`/`5991a6b2`: **all four DETECTED** (§2/§3 transcripts above,
  full log `mech_solo.log`).
- `bash tests/codegen/run_codegen_tests.sh` alone (fast re-run to confirm the
  K37 fix, not the full `test-codegen` group a second time): **104 passed / 4
  failed**, log `codegen_only.log`. The 4 failures are PRE-EXISTING and
  unrelated to this lane's changes — none of them touch `tests/codegen/
  run_encoding_checks.sh`, `tests/mech/run_sabotage_matrix.sh`, or either
  `cwmax_check.c` sabotage row:
  - `FAIL: OS-0b: two-engine file failed to compile` / `FAIL: OS-0b [M4.4]:
    duplicating the guarded ABI-types block broke the build` / `FAIL: OS-0b:
    could not extract both engine bodies` — three lines of ONE OS-0b
    multi-engine-fixture compile failure on this darwin/gcc-16 box.
  - `FAIL: [K24]: the de-sugaring left 4 accessor call(s) in the CONTROL's
    rx_search body` — the noclone control's sed-based de-sugaring, outrun by
    an emitter change unrelated to this lane.
- `make test-codegen` (the full run_group, before the K37 fix, log
  `test_codegen.log`): `run_codegen_tests.sh` 103/5 (the 4 above + the K37
  finding this lane's own code caused and then fixed in commit `4081a775`,
  confirmed above); `run_dfa_stamps.sh` 31/0; `run_offset_skip.sh` 22/0;
  `run_size_term.sh` 31/0; `run_inline_capability.sh` — **FAIL: nm could not
  read arm_a.o (no rx_search symbol)** on this box, a PRE-EXISTING
  darwin/gcc-16 nm-reading issue in a script this lane never touched (no
  `checks passed`/`failed` line — the script's own non-vacuity guard refuses
  to render a verdict rather than reading a broken symbol table as a
  pass/fail); `run_trie_identity.sh` 7/0; `run_scan_edge_census.sh` 14/0;
  `run_n1_budget.sh` 13/0. Per the manager's own note, these are the
  known darwin-only reds — not chased further, and not caused by anything in
  this diff.

## Open questions for the manager

- The two new mech rows (S230/S231) and the rewired S229/S-U8 numbering may
  collide with `k50bnd`'s concurrent lane per `tests/mech/sabotages/CLAUDE.md`'s
  own numbering caveat (a worktree's id space is as of its own branch point).
  Renumber at merge if needed; nothing else in the tree references S230/S231
  by number.
- DD12a(i)'s rebuild was validated on darwin only (this box). A Linux
  confirmation (that the same source-text comparison reads identically
  there, and that the full `ENC_MAX_BLOCKS=0` sweep stays green) is owed to
  whoever runs the merge-time battery on the Linux slot.
- The `.encoding` field's assertion (`cb['encoding'] != 1`) will need a
  second look if a future artifact shape legitimately emits `rx_info` more
  than once per file (not true today, per `[M4.4/D44/A-2]`'s single-guard
  ABI block, but worth naming since it is a closed assumption).
