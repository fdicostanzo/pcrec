# lane `clstudy` — [CLS-TREE] THE STUDY — delivery report

Branch `lane/clstudy`, worktree `worktrees/clstudy`, branched from `main` at
`13b56a12`. Opus tier. **Study only**: nothing under `src/`, `tests/` or
`docs/spec/` is touched on this branch — `git diff --stat main...lane/clstudy`
shows only `docs/dev/cls_tree_study.md`, `docs/dev/lanes/clstudy_report.md`,
`studies/cls_tree_study/**`, and the two index entries the brief required
(`docs/dev/CLAUDE.md`, `studies/CLAUDE.md`).

## Deliverables

| brief item | where | status |
|---|---|---|
| study memo, house style | `docs/dev/cls_tree_study.md` | committed |
| reproduction harness + own CLAUDE.md/README.md | `studies/cls_tree_study/` | committed |
| `docs/dev/CLAUDE.md` index entry | same change | committed |
| `studies/CLAUDE.md` index entry | same change | committed |
| (1) representation per set-structure class | memo §4 | answered — and the answer is that the question has no per-class form |
| (2) sectioning rule as measured output | memo §5 | answered |
| (3) discovery compile-time + explicit D77 verdict | memo §6 | answered — **cache NOT triggered** |
| (4) property-testing exploit of provenance-blindness | memo §7 | answered |

## The four answers, in one line each

1. **No single representation wins any real code-point set.** `\p{L}` at the
   middle policy is 27 sections of four different forms. The KIT is the
   answer; a per-class dial setting would choose among matchers the search
   never proposes. [CLS-TREE]'s own seed (`BSEARCH`) is chosen 12 times in 72
   cells and never at the speed end.
2. **The rule is a DP** minimizing `rodata + text + λ·ops` over contiguous
   partitions. λ IS [OPT-DIAL]'s dial, reached from the algorithm rather than
   fitted to it. What it picks is described in §5.3 rather than prescribed.
3. **Mean 4.19 ms / max 26.4 ms** over the 60 largest property sets, in C,
   single-threaded —
   under a fifth of the 144 ms `build/pcrec` already spends on that one
   pattern. **CONSTITUTIONAL CONSTRAINT 2's pre-analysis cache is NOT
   triggered.**
4. **438 cells × 1,114,112 code points, 0 mismatches**, checking
   `kit(A∘B) ≡ kit(A) ∘ kit(B)` on arbitrary unreachable sets — a check only
   a provenance-BLIND design can write.

## Headline numbers

* **All 312 property sets: 3,977,754 object bytes today → 85,613 as kit
  matchers, 46.5×.** `\p{L}` alone 227,409 → 4,359 (52×); `\p{Xwd}`
  294,153 → 5,326 (55×).
* Today's cost is **entirely tables**: `obj_text` is a constant 788 or 672
  bytes across all 312 baseline rows.
* The 41 corpus byte classes compile to **1,584 bytes of `.text` and ZERO
  `.rodata`**, against 319 32-byte table sites today.
* Exhaustive verification: **every** matcher built, checked against an
  independently constructed reference on **all 1,114,112 code points**.

## Two findings worth the manager's attention beyond the brief

**The general form covers twice the population the shipped special case
does.** Eight of the 41 corpus byte classes take a one-cube test; only FOUR
are case-fold pairs. `{a,c}` (xor 0x02), `{g,k}` (xor 0x04) and `{A,B,a,b}`
(two free bits) are emitted as 32-byte bitmap tables today, and
[FORM-CHAR]'s shipped `(lo^hi)==0x20`-and-both-letters classifier is
*structurally* blind to them. The kit reaches all eight through one O(k)
routine that was never told what caselessness is. This is the
general-mechanisms rule (memory `pcrec-general-mechanisms-not-special-cases`)
stated as a count.

**The algebraically impressive half of the analysis was the half that did not
pay.** The exact Quine–McCluskey two-level minimizer — the textbook answer to
Constraint 1's own "byte class = boolean fn over 8 bits → exact minimization
feasible" — costs 4.9× the discovery time to change 10 of 126 sectionings for
0.36% fewer probe ops. Dropped, and `discover.c` never implemented it. The
cheap O(k) tier is the one that finds the fold.

## Three bugs the study's own instruments caught (memo §8)

Each is recorded because the instrument is reusable, not because the bug was
interesting:

1. **A cost model that prices a form without building it is only safe if
   something independently builds and checks.** `PAGE64` is priced in O(k)
   without materializing its tables (that is what makes the D77 verdict
   possible); the first version double-counted a 64-wide page shared by two
   consecutive intervals, suppressed the all-empty leaf, and under-priced the
   form by 8 bytes on one section of `\p{L}`.
2. **Two implementations of one algorithm find what one cannot.**
   `crosscheck.py` caught an integer floor `log2` in the C against
   `math.log2` in the Python, then a duplicated fixed term in the Python's
   `RANGES` text cost that left the two disagreeing on **12 of 36 cells,
   every one at the pure-size policy** where `RANGES` is the contended form.
   Both implementations were self-consistent throughout.
3. **A Pareto point dominated on BOTH axes is a modelling error, not a
   result.** The first cost model priced only `.rodata`; the first full sweep
   returned `\p{L}` at 9,672 bytes / 1,302 ops against the middle policy's
   4,311 / 111 — smaller and faster at once. `.text` was then measured two
   independent ways and fed back.

## Validation

**COMPLETE for every number the memo cites**, with one scoped exception named
below.

| arm | population | result |
|---|---|---|
| exhaustive verification | K53 12 sets × 6 policies | 72/72 PASS, 0 mismatches |
| exhaustive verification | 41 byte classes × 6 policies | 246/246 PASS, 0 mismatches |
| exhaustive verification | 312 uprops sets × 3 policies | **936/936 PASS, 0 mismatches** |
| composition property test | 40 generated pairs × 4 ops × 3 policies | 438 PASS / 0 FAIL |
| C-vs-Python DP cross-check | K53 12×3 policies + 60 largest uprops | **96/96 AGREE, 0 DIFFER** |
| `.text` calibration (OLS) | 72 sweep rows | R² = 0.9996, worst residual 211 B |

Every verification cell compares all 1,114,112 code points against a reference
built by a different construction.

## Owed

Nothing that changes a conclusion. Two items, both named in memo §9/§10:

* **ns/char (memo §10).** The bench harness is written and committed
  (`bench.py`, house protocol: interleaved arms, `load1 < 0.5` gate that
  REFUSES rather than caveats, per-round answer checksums). It is the last
  thing this lane launches, per DO-THEN-FINISH. **No conclusion in the memo
  rests on a timing number** — §4, §5 and §6 are size, form-choice and
  compile-time results, and §9 states explicitly that nothing here licenses
  an end-to-end throughput claim.
Nothing else. The uprops arm completed (936/936) after this table's first
draft and its numbers are in the memo.

## Scope and disclosure

Scope mandate honoured: only `/Users/fdicostanzo/pcrec`, and inside it only
this worktree. `pcrec-bench` was neither read nor written. No `make test`,
`mech`, `san` or battery was run. Session-temporary files stayed in the
session scratchpad.

Disclosure: the session-root CLAUDE.md and the manager's memory index were
injected at spawn and treated as context. The brief's two constitutional
constraints were supplied verbatim and are answered as written. **The brief's
allowance that a provenance tag "may be a search HINT — accelerates, never
decides" was not needed and not used**: `cube_of` is O(k), no search needed
accelerating, so the kit takes no hint argument at all and §7's
provenance-blindness is total rather than nearly total.
