# r2 — [UTF-VALID] design note, contract lens (read-only critic)

Reviewed: `docs/design/utf_valid_design.md`, `docs/dev/lanes/k73utf_report.md`
(branch `lane/k73utf`, worktree at `bd1be543`), plan.md `[UTF-VALID]`.
Probes: `pr4.c` (the lane's own probe, PCRE2_UTF, checking ON) rebuilt in
`build/scratch/r2utf/` against libpcre2 **10.48 locally** (Homebrew) and, for
every case that decides a finding, re-run on **10.46** (ubuntubudu, one light
`mktemp -d` compile, removed). Where both were run they agree. No `make`, no
tracked file edited.

Bottom line: the measured PCRE2 rows in section 1 reproduce and I found no
error in them. But the *derived* contract (what `from` is, how it is
computed, what the caller does with the error) has four defects, one of
which (F1) makes the offset entry unable to report the error it was
introduced for. The `scan` rejection holds for the *fused DFA mechanism* but
not for the *contract*; one costed alternative is missing (F5).

## Findings

### F1 (HIGH) `utf_invalid_at(s, n, from)` cannot report a lookbehind-window error

Note section 4.2: "A caller that received `PCREC_ERR_UTF` calls it with the
same `from`". The artifact's checked range starts at `startpos - LB` (LB =
max lookbehind in characters), which the caller cannot know. Passing
`from = startpos` starts inside the valid tail and returns `n`, i.e. "no
invalid byte".

Evidence (10.46 and 10.48): `(?<=..)b` on `\xffab` from 2 -> -23, startchar
0. The bad byte is at 0, BEFORE `startpos`. The caller's second call
`utf_invalid_at(s, 4, 2)` returns 4. The caller holds `PCREC_ERR_UTF` and a
"the subject is fine" offset. Same for `\bb` on `a\xffb` from 2 (F2).

Disposition: the entry must take `startpos` and apply the artifact's own
step-back inside it (so it is byte-for-byte what the wrapper checks), or the
artifact must export `<PREFIX>_MAX_LOOKBEHIND` and the caller-visible rule
must be written in the spec. The validate-once use (`from = 0`) is
unaffected. This also removes the "same `from`" trap from the spec hunk.

### F2 (HIGH) The lookbehind fact is not only `vm_look_behind`'s widths: `\b` and `\B` widen the range

Note section 2.1 sources the step-back from "the lookbehind width table
`vm_look_behind` already reads", and section 7 prices "a `max_lookbehind_chars`
fact". PCRE2's `max_lookbehind` also counts `\b` and `\B` as 1 (they read the
previous character).

Evidence (10.46 and 10.48): `\bb` and `\Bb` on `a\xffb` from 2 -> -23 at
offset 1; `(*UCP)\bb` same; `(?m)^b` on `a\xffb` from 2 -> plain no match
(`^` does NOT widen); `\X`, `\R`, `\G` from 2 do not widen (they matched or
no-matched without error). Nested and conditional lookbehinds do propagate:
`(?(?<=a)b|c)`, `(?<=(a))b`, `(?i)(?<=A)b`, `(?<=aaa)b` (LB 3, error at 1
from 3), `(?<=a(?<=..))b` (max = 2).

Consequence: a `whole` build fed only by lookbehind widths is a silent
divergence from "PCRE2's contract" for every pattern with a word boundary,
which is a very common pattern class. The A_CTX context nodes (U2) are the
likely carrier for the boundary fact; the note should name the derivation as
"every construct that reads the previous character": lookbehind widths
(max over branches and nesting), `\b`, `\B`, and say `(?m)^` is NOT one.
Add these rows to the 10.46-pinned differential in section 7.

### F3 (MEDIUM-HIGH) The step-back is PCRE2's raw continuation skip, not pcrec's `back_step`

Note section 2.1: the walk "uses the backend's existing `back_step` rule".
`enc_utf8.c`'s `back_step` VALIDATES each stepped-over run and returns
`BACK_STEP_NONE` on a malformed one, and stops at 3 continuation bytes
(`end - pos < 4`). On exactly the inputs where this check matters (ill-formed
subjects) it returns NONE, and the note does not say what NONE means for
`from`.

PCRE2's rule, measured: skip back over ALL continuation bytes to the first
non-continuation byte, per character, unvalidated, unbounded, clamped at 0.
Evidence: `(?<=a)b` on `\x80\x80\x80b` from 3 -> -22, startchar 0 (a 1-byte
step-back would start at 2 and report 2). `(?<=a)b` on `a\x80\x80b` from 3
-> -22 at 1.

If NONE is mapped to "from = 0" the outcome is refuse-vs-refuse but with a
different offset in some cases (an earlier bad sequence than PCRE2's `from`
is reported). Measured: bytes `ff c3 a9 a9 62` with `(?<=a)b` from 4 -> PCRE2
starts at 1 (the lead `c3`) and reports -22 at offset 3; NONE -> 0 would
report offset 0. Offset-only, so D26-tolerable, but the note calls the
contract "PCRE2's".

Disposition: state the walk as a dedicated raw skip (it needs no validator
and is 4 lines), do not reuse `back_step`, and say which offsets are pinned.

### F4 (MEDIUM-HIGH) Q10 is answerable now, and the recommended order is the opposite of PCRE2's

Q10 says the order "was not probed" and recommends UTF-error-first. Probed
(10.46 and 10.48): a mid-character start beats a bad subject.
- `a` on `\xc3\xa9\xffa` from 1 -> **-36 BADUTFOFFSET** (bad byte at 2 is
  never reported).
- `a` on `\x80\xa9a` from 1 -> -36 (a stray continuation at start, no valid
  lead before it, is still -36, not -22).
- `(?<=a)b` on `\xc3\xa9\xffb` from 1 -> -36.
- With the start on a non-continuation, the UTF error wins as expected:
  `a` on `\xa9a\xff` from 1 -> -23 at 2.

So PCRE2 tests "is `subject[startoffset]` a continuation byte" BEFORE
validating. The note's recommendation (UTF first, "even when startpos is also
mid-character") is a stated divergence, which is allowed, but it is then
not "PCRE2's contract", and section 2.1's reasoning that "a continuation
byte at startpos is by definition inside a character" on a validated range
is only half the story: PCRE2 applies -36 without validating. Recommend
matching PCRE2 (K50 guard first, then the check): cheaper (the guard is O(1)
and can refuse before the O(n) pass) and it removes a divergence from the
spec hunk. Change Q10's text to the measured fact.

### F5 (HIGH, on Frank's explicit ask) `scan` is rejected as a mechanism, not as a contract

Refutation attempt on the `scan` rejection. The optimizer-dependent read set
R is decisive against the FUSED DFA form, and the note under-sells why: it is
not only "the same subject may be accepted by one version and refused by the
next", it also breaks `make test-axes` by construction. Every deny/force axis
is asserted answer-identical over the whole corpus (K50's axis is the one
documented exception, axes.def "the one axis that is NOT answer-identical"),
so a fused check whose accept/refuse depends on which prefilter ran fails the
sweep unless it denies them all. Say so; it is the stronger, repo-native
argument.

But the rejection of the CONTRACT is not airtight. Frank's words are "check
as you move forward". The note defines scan as "bytes R the scan happened to
read" and derives all the badness from that definition. A read-set-free
definition exists:

> **`extent`**: `PCREC_ERR_UTF` iff an ill-formed sequence begins in
> `[startpos - LB, e)`, where `e` is the end of the reported match, or `n`
> when there is no match.

`e` is a function of the ANSWER, which is already axis-identical, so this
contract is optimizer-independent, works for the VM and the hybrid (post-hoc
in the entry wrapper, no product automaton, no state-count/refusal-set
hazard, K53/K59 does not apply), and keeps find-all linear (each call
validates its own [from, e) not [from, n)). Its costs, which the note should
weigh:
- no-match calls validate all of `[from, n)` (same as `whole`, and the scan
  had to read all of it anyway);
- lookahead and `\K`-free reads beyond `e` are not covered, so `a(?!.)` on
  `a\xff` answers a match where PCRE2 refuses (as `scan` already does);
- **`caps` must not be written on -9** (section 3.1's rule for every negative
  return), so a post-hoc check needs the engine to write a scratch caps
  buffer or the contract must relax to "caps unspecified on -9". That is the
  real price, and it is a stack copy of `NCAPS` pairs per matching call, not
  a per-byte cost.

I am not asserting `extent` should be built; I am saying the note's
"Do NOT build scan" is proved only for "fused" and that Q6 (quadratic
find-all, currently answered by "validate once and compile a second,
non-checking artifact", which doubles emitted code for a caller who wants
both) has a cheaper candidate answer that the note does not cost. Disposition:
add `extent` as a costed row or reject it explicitly with the caps argument.

### F6 (MEDIUM) The "one first-match table" is not one table over one contract

Recommended build: rows 1, 2, 4. That is `if (byte) inert; else if (!flag)
off; else precheck`: a boolean, not a selection table, and rows 1 and 2
select "nothing". Fine and harmless, but the prose ("one option, two
contracts, one table") describes a structure that is only present if row 3
exists.

With row 3 the table is not sound:
- **Row 4 is a strictly stronger contract than row 3**, so the mechanism
  choice changes observable answers: `a` on `a\xff` is refused by row 4 and
  accepted by row 3. A first-match table of mechanisms for one contract
  must be answer-identical across rows (the `dfa_pfs[]`/`DFA_SELECT` idiom
  is). The note's "a `scan` artifact that cannot take row 3 is never refused"
  is exactly what makes `scan` = "may refuse more than R", i.e. no contract.
- **Row 3's predicate reads other tables' results** ("route is a DFA scan
  with no byte-skipping mechanism selected", "product fits the caps"), and
  the product changes the state count that the route/prefilter tables
  consume: a circular dependency unless row 3 is evaluated before them AND
  denies them. Both are reasons the doc is right to leave it unbuilt.

Disposition: state that `scan-fused` is not a row of a mechanism table but a
different contract, so the "Frank's two shapes are rows of one table" framing
in section 0 and plan.md should be dropped for this design, or the table
should hold `precheck` and `extent`, which really are two mechanisms of
"validate a function-of-the-answer range".

### F7 (MEDIUM) Caller surface against match_api.md conventions

1. **"Default-off identity: every artifact moves by exactly the stamp line"
   (section 7) contradicts section 6 item 3.** Every `-e utf8` artifact
   gains an exported function, a prototype and a doc comment (and `[VAR]`'s
   `var_valid` is rewritten), on the default-off path. `artifact_size_log.tsv`
   tracks this. The cost is real, arguably worth it (it is what enables the
   validate-once workaround), but the identity claim, and "default-off
   costs nothing", are wrong. Consider emitting the entry only when the axis
   is on or the caller asks, and say which.
2. **Name.** The spec's residual entries are encoding-neutral (`_next_pos`;
   `byte`'s body is `pos + 1`). A `<prefix>_utf_invalid_at` that exists in
   `byte` artifacts returning `n` is `utf`-named in an encoding it does not
   apply to. Prefer `<prefix>_invalid_at` or `_valid_upto`.
3. **"The six public entries return it."** Section 1 of match_api.md lists
   five per-artifact symbols; only `_search`, `_match`, `_match_caps` take a
   subject (`_info` and `_next_pos` cannot). Also `_match_caps` PROPAGATES
   codes (match_api.md near the `PCREC_ERR_INTERNAL` paragraph), so it needs
   no check of its own if it calls `_match`; the spec hunk should say which.
4. **The below-the-floor trap rule** ("Composed call sites must trap below
   the floor", match_api.md, [K50] paragraph): -9 is caller-data-dependent
   (unlike -6/-7, where a composed callee seeing it means the engine broke a
   rule). The check lives in the entry wrapper so no composed callee can see
   it today, but the spec paragraph that lists what trapping means should
   record -9's status now; the note's silence is the [K50] consequences-list
   pattern the spec already models.
5. **Contract axis vs the axis sweep.** `-futf-check` is the SECOND axis that
   is not answer-identical (axes.def documents K50's as the only one, masked
   out of `rx_info.flags`). It needs the same treatment there, and
   `make test-axes` (which sweeps the whole corpus, ill-formed subjects
   included) must run it only over well-formed cells or expect the refusal.
   Section 7's check list omits this and omits the harness/oracle work that
   [VAR]'s -8 needed (`tests/harness/driver.c`, `run.sh`, `verify_rxt.py`,
   `rxt_format.md`, `run_codegen_tests.sh`, `run_encoding_checks.sh`,
   `run_resource_tests.sh` all name `PCREC_ERR_UNSET_VAR`). F2 of the k73utf
   report already found the harness mislabelling -7 as "VM budget
   exhausted"; -9 will do the same unless taught.
6. `-9` is unused in `lib/`, the spec, and all lane worktrees I grepped
   (`git grep "(-9)"`, `worktrees/*/lib/pcrec.h`). No collision today.

### F8 (LOW-MEDIUM) Cost numbers: method

Method is honest (best of 7, two runs, sanity-checked to libpcre2's offsets,
the bench's validators are labelled "not the emitted one", darwin marked
directional), but the headline ratios overreach:
- **The denominators are not comparable.** `zq[0-9]x` at 0.0023 ns/byte is
  ~435 GB/s: that call does not read the subject; it answers from a
  prefilter. "17x a call a prefilter answers" is a ratio against a call that
  is sublinear in n. The honest statement is qualitative: the precheck turns
  a sublinear call into an O(n) one. `jumpz` (0.335) is a pure-literal
  pattern, the cheapest real scan; a realistic pattern is slower per byte,
  so "12% of a scan" is an upper bound, and "3x-7x a full DFA scan" divides a
  non-ASCII validator rate by an ASCII scan rate.
- **The subject mix.** ASCII (best case) and two non-ASCII shapes, of which
  "cyrillic-1/3" is a RANDOM mix (branch-predictor worst case, named as such).
  Missing the common case: mostly-ASCII text with sparse multi-byte
  characters, where the 8-byte fast path is neither a 16x win nor a
  regression. The fast path is slower than plain bytewise on the mixed
  subject (2.53 vs 2.21) and the note reports only the 16x.
- **Harness.** Standalone gcc-16 -O2 on darwin at load 7-10, not the
  artifact's compile flags or Linux (the project's perf box; house rule says
  darwin is directional only, which the note respects). The DFA-validator
  row (1.95) is a separate walk, which section 5 itself says row 3 must not
  be, so it prices something never proposed.
- Fine to keep, but not as decision inputs: the recommendation (`whole`
  only, default off, ASCII fast path) does not depend on them. The one number
  that does matter and is missing is the per-call fixed cost on small
  subjects (lookbehind step, function call) since find-all calls are many
  and small.

## What I tried to break and could not

- Every row of section 1's table: `a`/`a\xff`, `xa\xffz`, `b`/`\xffab`@2,
  `(?<=a)b` vs `(?<=..)b`, `(?<=a|bc)d` (max, not min: `\xffbcd`@2 errors at 0,
  @3 matches), truncated 2/3/4-byte tails, isolated 0x80, and -36 on a valid
  subject. All reproduce on 10.46 and 10.48.
- Edge cases: empty subject and empty pattern (match), `\xff`@0 -> -23 at 0
  but @1 (= n) -> match (1,1), truncated tail after `startpos`
  (`xa\xc3`@1 -> -3 at 2), `\K`/lookahead reads (`a\xff` refused regardless of
  what the match read, so the "not only what the match read" line holds),
  nested lookbehind = the max, conditional lookbehind, backreference
  lookbehind, case-insensitive lookbehind. The offset is always the first
  byte of the first ill-formed sequence. No further divergence found.
- startpos > n is BADOFFSET (-33), not covered by the note. That is
  existing K50/startpos territory, not new, but worth one sentence.

## Verdict on the recommendation

`whole` as the first build is right and Frank's "precheck whole subject"
maps to it. Before a build lane is chartered: fix the contract text for F1
through F4 (they change the spec hunk and the entry's signature, i.e. an abi
decision), and answer F5 (is `extent` worth a row?) since Frank named the
incremental shape and the note's rejection currently covers only the fused
mechanism.
