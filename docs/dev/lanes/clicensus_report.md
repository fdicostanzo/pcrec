# Lane clicensus — CLI call-site census for D118 (the gcc-shaped CLI)

Read-only census. No source touched; this report is the only new file.
Methodology: `grep`/`awk`/`python3` over text in the main tree
(`/Users/fdicostanzo/pcrec`, 5db0d20d), no `make`. Counts below are exact
where a single `grep -c` is cited; where a population was filtered through
several heuristics (comment-stripping, `--` detection) that is stated, and
the residual uncertainty is named rather than hidden.

D118 read first: `docs/dev/decisions.md` tail entry (this file's git log
head at census time). Summary for reference: positional operands become
INPUT FILES; the literal pattern moves to `--pattern 'X'` (long form only);
`-I` becomes `--lib-path`'s short form; `--source FILE` is retired (the
operand *is* the source-file mechanism now).

## 1. The wrapper — `tests/lib/gen_timeout.sh` `pcrec_run` (line 200)

Verbatim argument-handling core (lines 200–216):

```sh
pcrec_run() {
    local hostile=0
    if [ "${1:-}" = "--hostile" ]; then hostile=1; shift; fi
    local what
    what="$(basename -- "${BASH_SOURCE[1]:-${0:-pcrec_run}}"):${BASH_LINENO[0]:-0}"
    if [ "$hostile" -eq 0 ] && [ "$#" -gt 0 ]; then
        local pat="${@: -1}"
        case "$pat" in
            *'(?R'*|*'(?&'*|*'(?P>'*|*'\g<'*|*"\\g'"*| \
            *'(?'[0-9]*|*'(?+'[0-9]*|*'(?-'[0-9]*)
                hostile=1 ;;
        esac
    fi
    local _secs; _secs="$(pcrec_timeout_secs)"
    if [ "$hostile" -eq 1 ]; then
        "$GEN_LIB_ROOT/scripts/watchdog" -l "$what" -S "${WATCHDOG_SECTION:-pcrec_run}" \
            -s "$((_secs * 3))" -c "$_secs" -m "${PCRECRUNMEM:-512m}" \
            -L "${WATCHDOG_LOG:-$GEN_LIB_ROOT/build/watchdog.log}" -- "$@"
    else
        "$TIMEOUT_BIN" "$((_secs * 3))" "$@"
    fi
}
```

**How it identifies "the pattern":** `local pat="${@: -1}"` — bash's
last-positional-parameter slice, taken unconditionally over the *entire*
`pcrec_run` argv (which includes `"$PCREC"` itself as `$1` unless it has
already been shifted off by nothing — callers always pass `"$PCREC"` as
part of `"$@"`, e.g. `pcrec_run "$PCREC" -p rx ... -- "$pat"`). This last
argument is inspected ONLY for the call-bearing-construct substring match
(`(?R`, `(?&`, `(?P>`, `\g<`, `\g'`, `(?N`, `(?+N`, `(?-N`) that decides
plain-`$TIMEOUT_BIN` vs. `scripts/watchdog` routing. **The wrapper does
nothing else with the pattern** — it does not insert a flag, does not
special-case `--`, `--pattern-esc`, or any query mode; the rest of `"$@"`
(including `"$PCREC"`, all flags, and any `--`) is forwarded verbatim to
whichever underlying runner is chosen.

**Does every caller pass the pattern last?** Not universally — see the
mode breakdown below. For a plain compile (`-o file -- 'pat'`),
`--count-groups -- 'pat'`, and `--probe-ask WANT -- 'construct'`, the last
argument genuinely is the CLI's ONE positional operand (`cli_operand`,
`cli/main.c:689`). For `--explain SYNTAX`, `--list-source FILE`, and
`--probe-ask WANT` alone (without a trailing `--`/construct — not
observed in this corpus but legal per the parser), the flag's OWN value is
consumed via `argv[++i]` (`cli/main.c` e.g. lines 936–941, 929–935), not
through `cli_operand` — that value can still land as `pcrec_run`'s last
argument, but it is not the shared "pattern operand" D118 item 2 moves to
`--pattern`. This is a real ambiguity for the flip's mechanical wrapper
edit — flagged again in §5/§6.

**Callers passing `--`, `--pattern-esc`, or a query mode through the
wrapper** (grep across the 510 real call sites, tests/ only — see §2 for
the count derivation):
- `' -- '` (double-dash operand terminator) present: 344 of 510 calls.
- Query-mode flags present in the call: 89 calls carry one of
  `--list-syntax`(12) `--list-verbs`(4) `--list-families`(4) `--list-axes`(1)
  `--list-limits`(1) `--explain`(31) `--count-groups`(10) `--probe-ask`(28)
  `--list-source`(2) — counts overlap where one call composes two flags
  (e.g. `--list-syntax --explain`), so the per-flag sum exceeds 89.
  `--emit-ir` appears in 23 further calls (a compile-mode flag, not a
  query, but it also changes what the trailing operand means to the
  reader).
- `--pattern-esc`: 0 occurrences inside any `pcrec_run` call in this
  corpus (`tests/cli/run_cli_tests.sh` exercises it via a direct
  `"$PCREC"` call instead — see §2).
- `--source`: 0 occurrences inside any `pcrec_run` call (every `--source`
  caller in the corpus bypasses the wrapper — see §3; consistent with
  `pcrec_run`'s own doc comment, which frames it as "the COMPILER
  invocation itself").

**Call-site count:** `grep -rn "pcrec_run" tests scripts tools studies`
returns 551 lines; 41 of those are the `. .../gen_timeout.sh  # pcrec_run`
sourcing-comment lines (every file that uses the helper sources it once,
noted in a trailing comment), leaving **510 real invocations across 78
distinct files**, all under `tests/`. `scripts/`, `tools/`, and `studies/`
have zero `pcrec_run` call sites — those trees call the binary directly
(§2) or not at all.

## 2. Direct invocations bypassing the wrapper

Search: every `build/pcrec`, `"$PCREC"`, `$PCREC`, `${PCREC}` (word- and
brace-bounded, trailing-space required to exclude assignments/prose) across
`tests/`, `scripts/`, `tools/`, `studies/`, `Makefile`, `.claude/skills/`,
excluding lines that are themselves `pcrec_run` calls. Raw hit count: 371
lines. `tools/` has ZERO — every apparent hit there was the bare word
"pcrec" in prose, not a `$PCREC`/`build/pcrec` invocation.

| class | lines | method |
|---|---:|---|
| `--source`/`--target`/`--lib-path` present | 23 | grep -cE |
| query-mode flag present (`--list-*`, `--explain`, `--count-groups`, `--probe-ask`, `--list-source`) | 75 | grep -cE |
| `PCREC=...` bare assignment (no invocation) | 3 | grep -cE |
| `[ -x/-f "$PCREC" ]` existence check (no invocation) | 19 | grep -cE |
| `--help`/`--version`/`-h` only | 7 | grep -cE |
| comment/docstring/prose mention (first non-blank char `#`/`"""`/`*`) | 44 | python3 strip-and-classify |
| **real code-form invocation, remaining** | **200** | residual |

Of the 200 residual code-form lines, 96 carry an explicit `' -- '`
operand terminator on the same physical line (unambiguous positional
pattern); the other 104 are either continuation lines (the `--`/pattern
lands on a later physical line — the majority of this bucket: e.g.
`tests/recursion/run_recursion_diff.sh:148/191/295/303/309`,
`tests/uprops/run_uprops_tests.sh:113/182/228/241`,
`tests/vm/run_vm_tests.sh:542/551`, `tests/definitions/run_definitions_tests.sh:118/143`,
`tests/resource/run_resource_tests.sh:945`), bare positional patterns with
NO `--` at all (`studies/form_char_twins/gen_base.sh:28,31,34,37,40,51` —
7 calls, e.g. `"$PCREC" -p rxA -i --engine=vm --emit-main -o "$OUT/A_abcdef.c" 'abcdef'`),
or indirect (the `$PCREC` value is exported/passed to a subshell, a
`python3 - "$PCREC" ... <<'PY'` heredoc, or another script that builds its
own argv — `tests/axes/run_ksweep.sh`, `tests/axes/run_axes.sh`,
`tests/codegen/run_longprefix_sweep.sh:69` (hands `$PCREC` to
`docs/dev/w1stage0_evidence/longprefix_sweep.py`), `tests/codegen/run_dfa_uniform_fold.sh`,
`tests/registry/run_registry_tests.sh` (hands it to `compliance_section.py`)).

**A population the shell-level grep misses entirely: Python scripts that
receive `PCREC` and build their own `subprocess` argv.** Cross-referencing
every `.py` file mentioning `PCREC`/`pcrec` against one calling
`subprocess.run/Popen/check_output/call` finds **25 files** with both:
`tests/backrefs/d27/oracle.py`, `tests/lookaround/d27/checker.py`,
`tests/recursion/run_lookbehind_call_sweep.py`, `tests/recursion/d27/sr_perl.py`,
`tests/recursion/d27/sr_features.py`, `tests/recursion/gen_corpus.py`,
`tests/oracle/local_adapter.py`, `tests/assertions/verify_pcre2.py`,
`tests/harness/verify_rxt.py`, `tests/vm/vm_oracle.py`,
`tests/quoting/d27/gen_corpus.py`, `tests/registry/compliance_section.py`,
`tests/fuzz/fuzz.py`, `scripts/emit_sweep.py`,
`studies/tt4_batching/proto/collect_patterns.py`,
`studies/cls_tree_study/{extract_byteclasses,baseline,proptest}.py`,
`studies/tt4m_batchrun/{batchrun,collect_patterns}.py`, plus 5 more under
`docs/dev/*_evidence/` (out of the brief's tests/scripts/tools/studies
scope, named here because they DO invoke the compiler positionally and
WILL break — `docs/dev/w1stage0_evidence/longprefix_sweep.py`,
`docs/dev/w1stage0_evidence/listing_reach_census.py`,
`docs/dev/dialtrain_byteid_evidence/byteid_sweep.py`,
`docs/dev/optvmfl_step0_evidence/census.py`,
`docs/dev/artifact_size_census/census.py`). Sample confirmed shape,
`tests/vm/vm_oracle.py:302`: `subprocess.run([PCREC, "-p", "rx"] + extra +
["-o", cfile, "--", pat], ...)` — a genuine positional-pattern call in
argv-list form, invisible to a `"$PCREC" ` text grep. **This 25-file
population is NOT individually line-verified below the sample; it needs
its own per-file read during the actual flip**, not just the shell census.

**`tests/mech/sabotages/` — a large, easy-to-miss sub-population.** Of 270
sabotage `.sh` files, 75 define a `SAB_REACH=` string (a shell string
later `eval`'d by `tests/mech/run_sabotage_matrix.sh`) that itself
contains a `"$PCREC" ...` invocation. `grep -oE '"\$PCREC"[^;'"'"']*'
tests/mech/sabotages/*.sh` finds **73 such embedded invocations** (a few
files carry two, e.g. `S70_unbuilt_refusal_removed.sh` line 109 runs the
compiler twice in one `SAB_REACH` string); 12 of those 73 use a query mode
(`--list-*`/`--explain`/`--probe-ask`/`--source`), leaving **~61 embedded
positional-pattern calls**. Example: `SAB_REACH='"$PCREC" --features all
-p rx -o - -- "^(?:(?<h>cd)){0}..."'`
(`tests/mech/sabotages/S70_unbuilt_refusal_removed.sh:109`). These are
real call sites for the flip and are easy to miss because each sabotage
file shows as only 1 grep hit in a per-file directory listing.

**Real, non-`.py`, non-sabotage direct callers worth naming individually**
(genuine `-- 'pattern'` or bare-positional compiles, not existence
checks): `tests/bench/compare/compare.sh:746`, `tests/bench/run_bench.sh:404,490,516,570,773`,
`tests/lookaround/run_expansion_diff.sh:192,285,571,575`,
`tests/rxtsource/run_rxtsource_tests.sh:3198`,
`tests/recursion/run_specimen_identity.sh:175,258,366`,
`tests/recursion/run_recursion_diff.sh:148,191,295,303,309`,
`tests/uprops/run_uprops_tests.sh:113,182,228,241`,
`tests/vm/run_vm_tests.sh:542,551`,
`tests/definitions/run_definitions_tests.sh:118,143`,
`tests/resource/run_resource_tests.sh:945`,
`studies/form_char_twins/gen_base.sh:28,31,34,37,40,45,51` (7 calls, 6 of
them bare-positional with no `--` at all — the riskiest shape in the
corpus, see §5),
`studies/scan_edge_ladder/run_floor.sh:116-117`,
`studies/scan_edge_ladder/Makefile:56`.

**Grand total, direct (non-wrapper) invocations:** 200 shell-level
code-form lines (§2 table) + ~61 sabotage-embedded + an unquantified
residual inside the 25 Python files (sampled, not fully counted) ≈
**270+ confirmed, with a known-incomplete Python tail**.

**Files that would need editing for the flip** (positional-pattern class
+ `--source` class, deduplicated across §2 and §3, INCLUDING the wrapper
itself and the 25 Python files): **123 files** by this census's file-level
union (list retained in the lane's scratch output; available on request —
not reproduced here to keep this report a census, not a diff plan).

## 3. `--source`/`--target`/`--lib-path` callers

| file | `--source` | `--target` | `--lib-path` |
|---|---:|---:|---:|
| `tests/rxtsource/run_rxtsource_tests.sh` | 47 | 18 | 4 |
| `tests/harness/run.sh` | 6 | 6 | 0 |
| `tests/definitions/run_definitions_tests.sh` | 4 | 1 | 0 |
| `tests/codegen/run_codegen_tests.sh` | 1 | 0 | 0 |
| `tests/codegen/run_recursion_identity.sh` | 1 | 0 | 0 |
| `scripts/emit_sweep.py` | 9 | 0 | 0 |
| `tests/core/alloc_check.c` | 1 | 0 | 0 |
| **total** | **69** | **25** | **4** |

(`tools/review/out/literal_*.tsv` also match `--source`/`--target`/
`--lib-path` as text — those are the review tool's OWN generated literal-
frequency census artifacts, not call sites, and are excluded above.)
`tests/rxtsource/run_rxtsource_tests.sh` is overwhelmingly the
concentration point (47 + 18 + 4 = 69 of the 98 total occurrences) — it IS
the `.rxt`-source compile-mode test suite, so this is expected, not a
surprise. The C3 registry-store builder and oracle adapters (`tests/oracle/`)
were checked and carry NO `--source`/`--target`/`--lib-path` use — they
call the compiler in plain pattern mode (`tests/oracle/local_adapter.py`,
confirmed no `--source` hit).

## 4. Spec/doc sentences naming the CLI shape

| file:line | what it states |
|---|---|
| `docs/spec/cli.md:18` | usage line: `pcrec [options] -o OUT.c [--] 'PATTERN'` |
| `docs/spec/cli.md:26,154,168-193,505-516,559,667-674,828,860,921,993,1033` | the pattern-operand rule, `--pattern-esc`, `--source`'s own section (§, ~508-674) and its precedence/refusal relations, the "positional argument … belongs to the PATTERN" note at 828 |
| `docs/spec/rxt_format.md:9,58,125,375,406` | driver-protocol: "`pcrec` itself (`--source`/`--list-source`...)"; the `pcrec --source FILE -o OUT` sentence at 125; the operand-form note at 406 |
| `README.md:9` | example invocation: `build/pcrec -p rx --emit-main -o matcher.c 'a(b|c)+d'` |
| `CLAUDE.md:24,37` | the `make` comment line and the try-it line `build/pcrec -p rx --emit-main -o out.c 'a(b|c)+d'` (this is the session-root CLAUDE.md shown above — same file) |
| `docs/testing.md:2128,3206,3724,3737,3788,4211,4419,4440,4494` | example invocations with a positional pattern (3724, 3737), the "positional arguments" refusal-message quote (3788), and four `--source` composition-rule sentences (4211, 4419, 4440, 4494) |
| `docs/dev/coding_guide.md` | NO hits — the coding guide does not state the CLI usage shape |
| `cli/CLAUDE.md:184,240-269,345-351` | usage line inside the main.c description (184: `-o OUT.c 'PATTERN'`); the whole `[DD-13b.W1.2]` `--source`/`--target`/`--lib-path` section (240-269); the "ONE DECODER, THREE CALLERS" `--pattern-esc` note (345-351), which names `--source` as one of the three |

## 5. Risks visible from the parser

- **Filename vs. pattern confusion today:** there is none — today's
  parser never treats an operand as a file; every mode's positional slot
  (`cli_operand`, `cli/main.c:689-693`) is unconditionally "the pattern."
  Under D118 the SAME function's meaning flips to "the file", and nothing
  in the parser distinguishes the two by content — a caller passing a
  literal pattern positionally post-flip gets "not an existing file" per
  D118 item 1's stated behaviour (no fallback), which is the safe failure
  mode, but every one of the ~270+ call sites in §2 that still does this
  will hard-fail until migrated. Zero silent-miscompile risk; all-loud-
  failure risk, concentrated at the flip's landing commit.
- **What `--` means today:** `cli/main.c:723-726` — `--` sets
  `no_more_opts = 1` for the REST of that `argv` (not just the next
  token); every subsequent argument, however many, routes straight to
  `cli_operand`, which still only accepts ONE (a second one is "exactly
  one pattern expected"). So `-- a b` is already a refusal today, not a
  multi-operand acceptance — D118's "several input files" (item 1) is a
  behaviour change to `cli_operand` itself (accept N operands), not
  merely a renaming.
- **`cli_operand` is ONE function serving THREE modes, not one.** Besides
  the plain compile, `--count-groups` (help text: `--count-groups [--]
  PATTERN`) and `--probe-ask WANT [--] CONSTRUCT`'s trailing CONSTRUCT
  BOTH set `st->pattern` through the identical `cli_operand` call
  (`cli/main.c:1003`, reached from the same fall-through as the compile
  path). D118 item 2 says "the literal pattern is `--pattern 'X'`" and
  item 1 says "positional operands are INPUT FILES" — but it does not say
  which of these two rules `--count-groups`/`--probe-ask`'s operand
  follows post-flip: it is not a file, so item 1 does not fit it
  verbatim, and item 2's `--pattern` flag is framed around "the literal
  pattern" (the compile case) without naming these two query modes. This
  is a real decision gap the manager needs to close before the flip
  lands, not just an implementation detail — it determines whether
  `--count-groups`/`--probe-ask` change AT ALL, and it is exactly the kind
  of thing `pcrec_run`'s "insert `--pattern` before the last argument"
  mechanical fix (§1) would get WRONG if applied uniformly: doing so
  would also be wrong for `--explain SYNTAX` and `--list-source FILE`,
  whose values are consumed as the FLAG's own argument (`argv[++i]`,
  never through `cli_operand`) and are not "the pattern operand" at all.
- **`studies/form_char_twins/gen_base.sh`'s 6 bare-positional calls**
  (`lines 28,31,34,37,40,51`, e.g. `"$PCREC" -p rxA -i --engine=vm
  --emit-main -o "$OUT/A_abcdef.c" 'abcdef'`) have NO `--` at all. These
  are the sharpest concrete example of what breaks hardest: post-flip,
  `'abcdef'` is read as a file operand and refused as "not an existing
  file" with no diagnostic pointing at `--pattern`. `studies/` is
  reference material never built/tested by `make` (its own CLAUDE.md), so
  this will not show up in `make test` — it will only be discovered by
  someone running the study by hand.
- **The `.rxt` `config` block's `pcrec <raw flags>` line IS a second
  caller of the parser** (`cli/main.c:711`'s `where` parameter literally
  distinguishes "command line" from a config block — confirmed in code),
  per `docs/spec/rxt_format.md:66,328`. Grepped the full corpus: **zero**
  of the 213 `.rxt` files under `tests/` use this line
  (`grep -rlE '^\s+pcrec\s' tests --include='*.rxt'` → no matches). The
  mechanism is exercised only in `tests/rxtsource/fixtures/*.rxtin` (5
  raw-flags lines across 3 fixtures: `head_basic.rxtin:25`,
  `three_configs.rxtin:34,37,39`, `config_pcrec_escape.rxtin:17`) — every
  one of those 5 lines is flags-only (`--warn-emit-bytes=`,
  `--no-captures`, `--engine=dfa`, `--max-emit-bytes=`, `-p notmyprefix`),
  none carries a positional pattern. So this second caller is CURRENTLY
  SAFE against the flip by construction of the existing corpus, but the
  mechanism itself is real and any future fixture or `.rxt` file adding a
  raw positional pattern there would need the same `--pattern` treatment.

## 6. What the flip touches — summary

At minimum **123 files** carry a direct or wrapper-mediated CLI call that
the flip's grammar change reaches (78 wrapper-only files are UNAFFECTED
if the wrapper alone absorbs the change per D118's own plan — see below;
the 123 is the set needing SOME edit: the wrapper file itself, every
direct-invocation file from §2, every `--source` caller from §3, and the
25 Python files with their own `subprocess` argv). Call-site count:
**510 wrapper calls** (most self-heal once `pcrec_run` is fixed, per
D118's own plan — "the wrapper inserts the flag") + **270+ confirmed
direct calls** (200 shell-level + ~61 sabotage-embedded, with the 25
Python files' own internal count not fully enumerated) + **98
`--source`/`--target`/`--lib-path` occurrences** across 7 files.

The three riskiest edits, in order:
1. **`pcrec_run` itself** cannot safely do a uniform "insert `--pattern`
   before the last argument" rewrite (§1, §5) — its last-argument
   heuristic conflates the true pattern operand (compile, `--count-groups`,
   `--probe-ask`'s CONSTRUCT) with flag-owned values (`--explain`'s
   SYNTAX, `--list-source`'s FILE) that must NOT gain a `--pattern`
   prefix. Whoever writes the wrapper fix needs the mode-aware branch this
   census's §1 table implies, not a blind last-arg rule.
2. **`tests/mech/sabotages/`'s 61 embedded `SAB_REACH` calls** are the
   easiest population to under-count (each file shows as 1 grep hit in a
   directory listing, easy to treat as noise) and the costliest to get
   wrong silently — a `SAB_REACH` string that stops reaching the compiler
   after the flip is a sabotage the matrix would then fail to catch for
   the wrong reason, which is exactly the "[MECH-REACH]" failure mode
   `docs/dev/learnings.md` §3 already warns about for checks in general.
3. **The 25 Python `subprocess` callers** (§2) are invisible to a plain
   `"$PCREC" ` text grep and were found only by cross-referencing two
   separate greps; this census's classification of them is a file list,
   not a verified line-by-line count — treat that count as a lower bound
   and read each file before editing.
