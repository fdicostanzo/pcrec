# docs/design/k18_measurements/capdiff/ — the K18 capture-offset differential

Discharges `../k18_memo_design.md` §4.6's open item: every measurement in
that note (and in the K18 rewrite lane that built `src/ir/dfa.c`'s A2
closure from it) is spans-only. This directory is the dedicated
capture-bearing differential the note flagged as owed, now that [M4.5]'s VM
emitter has landed and a capture-bearing pattern's correctness genuinely
depends on the DFA closure (as its prefilter) rather than being masked by
`--no-captures`.

**Nothing here proposes a patch.** Every run is read-only against a built
`build/pcrec` (or, for the positive control, a scratch binary built from an
old commit in a temp directory outside the repo) — this directory holds the
generator, the sweep driver, the batch oracle and the resulting transcripts,
never a modification to `src/`.

## The finding that shapes this lane

`src/gen/emit_vm.c`'s `<prefix>_search` (the hybrid entry) calls the DFA
prefilter ONCE and reads only `win[0][0]` — the computed match **START** —
discarding `win[0][1]` (the computed END) entirely; the VM re-derives the
end (and every capture) itself via backtracking (`~emit_vm.c:1994-2004`).
K18's own defect lives in the FORWARD machine's thread-priority ordering
(`prune=1`, over-consumption at the match END) — so for the family of
patterns the original K18 corpus and `gen_shapes.py`'s dense sweep are built
from (fully nullable, matching trivially at offset 0), a K18-class DFA
defect **cannot reach a capture at all**: the prefilter's `win[0][0]` is `0`
either way, and the VM never consults the corrupted `win[0][1]`. Verified
directly: a scratch binary built from `9d39b97` (the commit immediately
before the K18 fix landed) reproduces the known span bug under
`--no-captures` (`((?:a|b*?)?)*` on `"ab"`: pre-fix `[0,2)`, oracle `[0,1)`)
but produces IDENTICAL output to the fixed binary once captures are on
(`x((?:a|b*?)?)*`, same subject family, both `[0,2)`, matching the oracle).

This means the only route by which the K18-shaped defect could ever corrupt
a capture is through the **REVERSE machine's** (`prune=0`) computed START —
exactly the axis `k18_memo_design.md` §4.6's R23 addendum flags as where the
stack-entry corruption actually lived (a MANDATORY LEADING ATOM forcing a
non-trivial reverse-machine computation; R23 S11 measured 1,980/81,840
diverging cells on the unfixed prototype, 0 on A2, spans-only). This
directory's corpus is built to hit that axis specifically, with captures
placed after the leading atom so a wrong reverse-computed start would show
up as a wrong (or missing) capture slot, not just a wrong overall span.

## Files

- `gen_capshapes.py` — the pattern generator. Ingredients: the nullable-loop
  K18 family (both arm orders, greedy/lazy/explicit-empty-alternative arms,
  four capture placements per arm-pair — whole alternation, both arms,
  nullable-arm-only, atom-arm-only), the `{0,2}` SPLIT family (§2b — the
  sub-case B's cheap alternative got wrong), §1.5's four named witnesses
  with captures added structurally, modest deep nesting (captures at
  multiple levels), and a MANDATORY-LEADING-ATOM cross (`x`, `xy`, `(x)`,
  `(x)(y)`) applied to a bounded subset of the above. `--full` widens the
  leading-atom cross to every base pattern and adds the deep-nesting family
  to it too; default output (526 patterns) is what `outputs/capshapes.tsv`
  freezes. Every pattern is checked valid python `re` syntax before use
  (capdiff.py's `py_oracle` silently skips anything that isn't, so an
  invalid pattern would read as "0 cells checked" rather than a loud error —
  worth knowing if a future edit to this generator needs to be re-verified).
- `pcre2_batch_oracle.c` — one-process libpcre2 8-bit oracle over
  `tests/fuzz/pcre2_abi.h` (the project's one hand-declared ABI slice —
  this file does not re-declare it, see PC-3's own rationale). Reads
  `PATTERN\tSTARTPOS\tSUBJECT_HEX` lines from stdin, prints
  `match S0 E0 S1 E1 ... S19 E19` (20 pairs, UNSET `-1 -1` padded — far more
  than any shape here needs groups for) / `nomatch` / `cerr N` / `mlimit N`
  per line, in order. Compiles at PCRE2 `options=0` only (D26's standing
  exclusion). Reads only `ov[0 .. 2*rc)` — the slice PCRE2's own contract
  says `pcre2_match_8` actually wrote — never uninitialised ovector memory
  past `rc`, which is the K21 lesson one layer up (a printf reading memory
  a call never promised to have written). Exists as a SEPARATE program from
  `tests/fuzz/pcre2_oracle.c` because that one is one-process-per-cell
  (fine at the fuzzer's few hundred patterns, prohibitive at this lane's
  tens of thousands) and prints only the whole-match pair, not every group.
- `capdiff.py` — the sweep driver. Per pattern: builds AUTO (default —
  every capture-bearing pattern is VM-forced with the DFA prefilter ON,
  `src/opt/select_engine.c`) and VMONLY (`--engine=vm`, prefilter off, D44/
  R21 E-6) artifacts via the SHARED `tests/vm/vm_driver.c` (never a
  reimplementation of its three-valued-return discipline — K21's lesson).
  Generates a subject sweep from the pattern's own alphabet (bounded by
  alphabet size: maxlen 5/4/3/2 for 1/2/3/4-letter alphabets, keeping cell
  counts sane once leading-atom patterns add `x`/`y` to the mix). Four
  comparisons per cell: AUTO vs python `re`, AUTO vs libpcre2 (batched
  through `pcre2_batch_oracle`, one process for the whole run), AUTO vs
  VMONLY (isolates a prefilter-fed defect — if these agree and AUTO is
  still wrong, the defect is not in the DFA/prefilter at all), and python
  vs libpcre2 (oracle/oracle sanity — a disagreement here excludes the cell
  from the first two rather than blaming pcrec, matching D26/
  `../../dev/upstream_issues.md`'s standing discipline; none has occurred
  in this lane's own runs). `PCREC=/path/to/pcrec` selects the binary under
  test — this is how the positive control below points the identical
  driver at a scratch build without touching the script.
- `outputs/` — stable-named transcripts with a source-info header (date,
  repo commit, python/gcc/libpcre2 versions, exact command line) plus the
  exact `.tsv`/pattern files each transcript was run against (committed
  verbatim rather than re-derived from the generator's current state, so a
  future generator edit cannot silently invalidate what an old transcript
  claims to have covered — see `../../k18_memo_design.md` §7, "A note on
  this lane's own instrumentation": three prior defects in THIS lane's own
  tooling each produced numbers that would otherwise have entered the note
  as findings, and R23 found a fourth in the prototype itself). See its own
  listing below for what each file is.

## Positive control (why a zero here is a measured zero)

A generated-sweep "0 divergences" is not evidence unless the corpus could
have produced a divergence in the first place. Because a synthetic control
built from the CURRENT `pcrec` under test would share its source with the
thing it's supposed to control (the project's own standing lesson —
`docs/dev/known_issues.md`'s repeated instrumentation defects), the control
here is a REAL HISTORICAL BUILD: a scratch `pcrec` compiled from git commit
`9d39b97` (the last commit before `8f1f8c5` — "K18 fix: path-sensitive
epsilon closure" — landed; `9d39b97` itself is design-prose-only, so its
`src/ir/dfa.c` is byte-identical to the pre-fix shipped compiler). Built
outside the repository (a `git archive` of the worktree's `HEAD` into a
scratch directory with `dfa.c` swapped for the pre-fix version, then
`make`), never committed, per the scope mandate.

That control confirmed the instrument works on two levels:

1. **Spans, `--no-captures`**: reproduces the textbook K18 divergence
   directly (`((?:a|b*?)?)*` on `"ab"`: pre-fix `[0,2)` against the oracle's
   `[0,1)`), and the leading-atom sweep below finds the reverse-machine
   sub-class of it (§4.6's own open finding) on a real, non-source-shared
   binary.
2. **Captures, AUTO (default)**: `capdiff.py` pointed at the SAME scratch
   binary via `PCREC=`, over this lane's own capture corpus — see
   `outputs/capdiff_prefix_control.txt` for the exact counts.

See `outputs/` for the actual numbers; this file states the METHOD, the
transcripts are the evidence.

## Maintenance

Update this file when files are added/removed or their roles change.
