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
default):** <FILL IN FROM full_run.log>

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
dirty baseline gives a false NOW-DETECTED"): <FILL IN — checks passed/failed
count from full_run.log>

**Solo mech runs of S229 and S-U8 against that green baseline:**
<FILL IN>

## Validation summary

| deliverable | instrument shown to fail | commit |
|---|---|---|
| DD12a(i) rebuilt | scratch plant in emit_vm.c, `git archive` tree, never landed | <FILL> |
| cwmax floor (i) | S230, solo mech run, DETECTED | <FILL> |
| cwmax floor (ii) | S231, solo mech run, DETECTED | <FILL> |
| `encoding` mech arm | S229/S-U8 solo mech runs against a green post-rewrite baseline | <FILL> |

## Targeted validation run (delivery)

- `PCREC=... CC=gcc-16 ENC_MAX_BLOCKS=250 bash tests/codegen/run_encoding_checks.sh`: <FILL>
- `bash tests/mech/run_sabotage_matrix.sh S230` / `S231` / `S229` / `S-U8`: DETECTED (see above)
- `make test-codegen`: <FILL — owed if touched further>

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
