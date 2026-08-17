# K24 fix: the measurement behind the lever

Companion to `k24_bisect_note.md`, which found the mechanism but deliberately
landed no fix. This note is the fix lane's evidence: the head-to-head that
chose the lever, the VM-artifact audit, and the acceptance run. The ruling
itself, with the reasoning, lives in `docs/dev/known_issues.md`'s **K24
CLOSED** block — this file is the numbers it cites.

Lane: `worktrees/k24fix` (branch `lane/k24fix`, off `main` at `caca837`).

## The fix, in one line

`__attribute__((noclone))` on `<prefix>_search`, emitted by
`emit_search_head()` in `src/gen/emit_dfa.c` — the one emission site that
serves BOTH the DFA artifact's exported entry AND the VM hybrid's `static`
prefilter.

It has to be in the emitted artifact rather than in pcrec's own build:
`-fno-partial-inlining` recovers everything, but that is a flag only whoever
compiles the artifact can pass, and pcrec cannot dictate its users' CFLAGS.

## Measurement protocol (identical to the bisect's, deliberately)

- Build line is `compare.sh`'s own, verbatim:
  `gcc -O2 -std=gnu11 -Wall -Wextra -Werror -I<dir> -o eng_pcrec eng_pcrec.c gen.c`.
  This matters more than it looks: the split's cost is a code-PLACEMENT cost,
  so a number is only commensurable with `floors.tsv` if it comes from
  `floors.tsv`'s own link. The bisect note's closing caution is exactly this
  point, and it is why this lane did not reuse `probe.sh`'s hand-built driver
  for the acceptance numbers.
- `taskset -c 2` on every timed invocation (`compare.sh`'s R2-B1/B3 pin), 10
  trials, medians reported, iteration count calibrated to ≥0.3 s wall.
- Quiet box, load checked before measuring and recorded per row: 1-min
  0.08-0.27, 5-min 0.19-0.26 against the probe's own 2.0 refusal threshold.
- Subject is `compare.sh`'s case-(c) subject regenerated bit-for-bit; verified
  with `cmp` against `gen_subject.py`'s independent replay.
- Correctness is asserted before every timing run: case (c) must report
  nomatch, case (j) must report match. A timing number from a matcher that
  stopped agreeing is not a timing number.

Instruments here: `mk_levers.py` (builds each variant by inserting one
candidate attribute at the site the emitter would insert it, so the
head-to-head measures exactly what landing it would produce),
`lever_probe.sh` (the pinned timing harness), `sweep_clones.sh` (the
`nm` clone audit across a pattern set). Raw output: `h2h_case_c.tsv`,
`h2h_case_j.tsv`, `clones_before.tsv`, `clones_after.tsv`.

## Head-to-head, case (c) — `(alpha|beta|gamma|delta|epsilon)`, 8 MB nomatch

| lever | median MB/s | min-max | `.part` clone in `nm`? |
|---|---|---|---|
| none (the K24 state) | 293.500 | 285.6-375.1 | SPLIT |
| `-fno-partial-inlining` (bisect's control) | 391.646 | 390.2-392.8 | mono |
| `noipa` on the two cold wrappers | 292.721 | 287.6-338.2 | SPLIT |
| `noinline` on the two cold wrappers | 295.315 | 288.2-344.0 | SPLIT |
| `cold` on the two wrappers | 397.076 | 394.5-400.0 | SPLIT |
| `hot` on search + `cold` on wrappers | 288.745 | 288.1-308.6 | SPLIT |
| `hot` on `<prefix>_search` | 397.589 | 396.6-401.7 | SPLIT |
| **`noclone` on `<prefix>_search`** | **391.061** | **389.4-392.8** | **mono** |
| `optimize("no-partial-inlining")` on search | 390.873 | 389.7-392.5 | mono |
| `noipa` on `<prefix>_search` | 390.786 | 379.5-391.9 | mono |

Read the min-max column alongside the median: every SPLIT row is also a WIDE
row (285-375 on the baseline) even fully pinned, and every mono row is tight
(<1%). The spread is part of the symptom, not measurement slop — which is the
bisect note's own finding, reproduced here on a different harness.

### The three things this table settles beyond the choice

1. **Attributes on the WRAPPERS do nothing.** `noipa`/`noinline` on
   `<prefix>_match`/`<prefix>_match_caps` leave both the clone and the ~293
   number in place. gcc's `pass_split_functions` runs on the CALLEE and does
   not consult callers' attributes, so severing IPA at the call site cannot
   un-split the callee. The wrappers' arrival at `1dbb6ce` is still what dated
   the regression — the bisect stands — but "the wrappers trigger the split"
   is the wrong causal reading for choosing a fix, and it was the leading
   candidate going in.
2. **Layout steering recovers the number without fixing anything.** `hot` on
   the entry (397.6) and `cold` on the wrappers (397.1) both beat the floor
   with the clone still present. Combining them measures **288.745 — worse
   than doing nothing.** That is the mechanism declining to be steered: the
   cost is placement within one particular link, and a stranger's link is not
   this one. A future reader who finds `noclone` odd-looking and reaches for a
   `hot`/`cold` pair instead should read that row before doing it.
3. **`noclone`'s emitted assembly is BYTE-IDENTICAL to the same source built
   `-O2 -fno-partial-inlining`** (`diff` of `gcc -S` output: no differences).
   That is the strongest available statement that the lever reproduces the
   bisect's causal control and perturbs nothing else — and it is the check
   the brief asked for only in the `optimize(...)` branch, done here for the
   branch actually taken.

### Why `noclone` over the two other working levers

Both alternatives work; `noclone` is the smallest denial that is about the
mechanism rather than about this box.

- `optimize("no-partial-inlining")` replaces the function's entire
  optimization environment to switch off one pass — a documented footgun, and
  a wide instrument for a narrow job.
- `noipa` forbids all interprocedural optimization involving the function.
  That is strictly more than needed, and on the VM hybrid path it would
  forbid a real inline gcc performs today: the `static` prefilter is fully
  inlined into the VM's `<prefix>_search` (verified — no
  `<prefix>_prefilter` symbol appears in a VM artifact's `nm` output, before
  or after this fix). `noclone` forbids duplication only, and leaves that
  inline standing.

Portability, separating what was measured from what was read:

- MEASURED — gcc 15.2.0 (the box's compiler) accepts `noclone` under
  `-Wattributes -Werror` with no ignored-attribute diagnostic. This is worth
  checking rather than assuming: an attribute gcc merely IGNORED would make
  this fix a no-op that still looked landed, and the `nm` result would be the
  only thing that noticed.
- READ, not measured — GCC's manual has documented `noclone` since 4.5. Inside
  the gcc-dialect mandate the emitter already lives under (computed goto,
  `__builtin_expect`).
- UNMEASURED — there is no clang on this box, so clang's treatment of the
  attribute is unknown, and is recorded as unknown rather than assumed in
  either direction.

## The VM-artifact audit

The charter asked whether the VM's search entry is also being split, and said
to record WHY either way. **It is not, and the premise for expecting it to be
is wrong.**

The brief's premise was that "every VM artifact has the same wrapper shape
(match/match_caps → search)". It does not. In `emit_vm.c`, `<prefix>_match`
and `<prefix>_match_caps` call the `static` `<prefix>_match_impl` DIRECTLY,
and `<prefix>_search` calls it too. So in a VM artifact `<prefix>_search` has
zero in-TU callers and is not a wrapper target at all; the three entries are
siblings over one implementation, not a chain.

Clone sweep over 25 patterns (14 DFA, 11 VM), compiled with the bench build
line, `nm`-audited for every `.part`/`.constprop`/`.isra` clone
(`clones_before.tsv` vs `clones_after.tsv`):

| | DFA artifacts with a clone | VM artifacts with a clone |
|---|---|---|
| before the fix | **13 of 14** | **0 of 11** |
| after the fix | 0 of 14 | 0 of 11 |

Two findings fall out:

- **The split was never specific to case (c)'s pattern — only its measured
  COST was.** Essentially every unanchored DFA artifact pcrec emitted since
  `1dbb6ce` carried `rx_search.part.0`. Case (c) is where the placement
  penalty happened to land hard enough to break a floor; the other DFA cases
  matched or beat their floors while split. Anyone tempted to read K24 as "a
  trie-shape problem" should read that row: the artifact defect was
  near-universal and the *visibility* was pattern-specific.
- **The one DFA artifact that was never split is `^abc`, and its reason is
  the same one that protected the VM.** That is the ENG_ATTEMPT engine — 5
  `goto *` sites. gcc cannot outline a function whose labels are
  address-taken (they bind to one function), so a computed-goto matcher is
  unsplittable by construction. The VM's hot loop is exactly that shape
  (engine_m4.md §2.7: one function per pattern, one indirect jump at the fail
  label), which is why the VM was never at risk. It is a property of the VM's
  design rather than luck — but it is also a property nothing checks, so it is
  written down here instead of relied on silently.

The attribute nonetheless rides the VM's `static` prefilter, because that is
the same `emit_search_head` output and the same split-eligible table-driven
shape. Measured neutral on the capture-bearing hybrid, case (j)
`([01]*)1([01]{8})` over 8 MB (`h2h_case_j.tsv`, floor 150.369):

| variant | median MB/s | clone? |
|---|---|---|
| VM artifact as-is | 150.237 | none |
| `noclone` on the static prefilter (what landed) | 150.433 | none |
| `noclone` on prefilter AND on the VM's own `search` | 150.393 | none |

All three within 0.2% of each other and of the floor, spreads ≤1.01x. The
third variant is recorded because it was tried: the VM's own `search` entry
does NOT get the attribute, since it never splits (no in-TU callers, and its
hot work is the unsplittable `match_impl`), and adding it buys nothing
measurable. If a future VM artifact shape ever does split its `search`, the
lever to copy is one line and this row is its precedent.

## Acceptance

`floors.tsv` was NOT touched — case (c) stays at 388.615/0.900, and the gate
goes green because the number came back, which is the only way this project
lets a red floor turn green (`gate.sh`'s own header rule).

Full 10-case `gate.sh` run, quiet box: case (c) measures **391.063 MB/s at
spread 1.02x** — above its floor, and back to this case's historical
1.02x-1.06x tightness rather than the 1.13x-1.16x the split produced. The
recovered spread is worth as much as the recovered median: it is the
independent signature of the clone being gone.

## Reproducing this

```sh
# 1. subject + baseline artifact (K24_SCRATCH defaults to the session dir)
python3 docs/design/k24bisect_impl/gen_subject.py "$SCRATCH"
build/pcrec -p rx --no-captures -o "$SCRATCH/base/gen.c" -- '(alpha|beta|gamma|delta|epsilon)'
# 2. build every lever variant from that one baseline
python3 docs/design/k24bisect_impl/mk_levers.py "$SCRATCH"
# 3. time them, pinned (check `uptime` first -- an unpinned or loaded run of
#    this measurement is worthless, see the bisect note's methodology section)
K24_SCRATCH="$SCRATCH" bash docs/design/k24bisect_impl/lever_probe.sh "$SCRATCH"/v_*
# 4. the clone audit, before/after
K24_SCRATCH="$SCRATCH" bash docs/design/k24bisect_impl/sweep_clones.sh
```
