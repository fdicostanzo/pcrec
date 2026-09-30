# [UTF-VALID] — an opt-in subject UTF-8 validity check (DESIGN NOTE, PROPOSED)

Lane `k73utf`, 2026-09-29. This is a design note only. Nothing is built.
Charter: `docs/dev/plan.md` [UTF-VALID]. Frank, 2026-09-29: *"a
default-off check for valid subject utf. either precheck whole subject or
check as you move forward (dfa?)"*. Evidence is in `utf_valid_evidence/`,
which has its own CLAUDE.md.

## 0. Summary and recommendation

- **Today** every `-e utf8` artifact is invalid-tolerant. An ill-formed
  sequence matches nothing, and nothing reports it (ASK 1). K73 (fixed on
  the same branch) makes the start of the search follow
  PCRE2_MATCH_INVALID_UTF too. PCRE2's own default is the opposite: it
  validates the subject and refuses an invalid one with an error code and
  an offset.
- **The design is ONE option with two contracts**, `whole` and `scan`.
  One first-match table (§3) picks which mechanism implements the contract
  an artifact was compiled for. Frank's two shapes are rows of that table,
  not two features.
- **Recommend building only the `whole` contract**, implemented by a
  PRECHECK. The check is an encoding-residual entry called once per call by
  the entry wrapper, the same shape `[VAR]`'s `$_var_valid` already ships.
  Its contract is PCRE2's, measured on 10.46 (§1). The caller gets one new
  refusal code and an exported entry that reports the offset.
- **Record the incremental (`scan`) row but do NOT build it.** Its contract
  is weaker (§2.2) and depends on the engine's own optimizations. It needs
  a product automaton, and it is incompatible with every byte-skipping
  prefilter. No measured need triggers it (D77).
- **It is an abi event** when built, even for default-off artifacts (§6).
- **Cost** (darwin, directional, §5). A strict check with an 8-byte ASCII
  fast path costs 0.04 ns/byte on ASCII text and 1.0-2.5 ns/byte on
  non-ASCII text. That is 1.6x-17x the cost of a whole pcrec call that a
  pre-check answers, about 12% of a full DFA scan on ASCII, and 3x-7x a
  full DFA scan on non-ASCII text. It is not free, which is why it must
  stay default-off.

## 1. PCRE2's contract, measured

Probe: `utf_valid_evidence/pr4.c` under PCRE2_UTF (checking ON), on
libpcre2 10.46. Transcript: `utfcheck_10.46.txt`.

| case | 10.46 |
|---|---|
| `a` on `a\xff` from 0 | **error** -23, offset 1. There is a match at (0,1) BEFORE the bad byte, and the call still refuses: the check is not "only what the match read". |
| `a` on `xa\xffz` | error, offset 2 |
| `b` on `\xffab` from 2 | match (2,3): bytes BEFORE `startoffset` are not checked |
| `(?<=a)b` on `\xffab` from 2 | match: the check starts at `startoffset - 1` (the max lookbehind is 1 char), and the bad byte is at 0 |
| `(?<=..)b` on `\xffab` from 2 | **error**, offset 0: a lookbehind of 2 reaches the bad byte |
| `(?<=a\|bc)d` on `\xffbcd` from 3 | match: the max lookbehind is 2, so the check starts at 1 |
| truncated / overlong / surrogate / > U+10FFFF / isolated 0x80 | errors -3 / -17 / -16 / -15 / -22, each at the offset of the sequence's first byte |
| `a` on `\xc3\xa9a` from 1 | -36 BADUTFOFFSET (checking ON: a mid-character start is an error) |

**PCRE2's contract is therefore: the range `[startoffset − maxlookbehind
(in characters), n)` is well-formed, or the call returns a UTF error whose
offset is the first ill-formed sequence's first byte.** No match attempt
is made first. D26 applies: pcrec owes the refusal and the offset, not
PCRE2's twenty error codes.

## 2. The two shapes, as contracts

### 2.1 `whole`: the precheck

Before any attempt, the entry validates `[from, n)`, where `from` is
`startpos` stepped back by the pattern's maximum lookbehind in characters.
If the range is ill-formed, the call returns `PCREC_ERR_UTF` and leaves
`caps` untouched (§3.1's rule for every negative return). Otherwise the
call proceeds exactly as today.

This is PCRE2's contract, with one choice to make (**Q1**) about the
lookbehind step-back:

- Stepping back needs a new fact, the pattern's max lookbehind in
  characters. The lookbehind width table `vm_look_behind` already reads is
  its source. A lookbehind-free pattern has 0, so the step is free there.
- The step-back walks characters over input that may be ill-formed. It
  uses the backend's existing `back_step` rule, so "a character" means what
  the engine means by it.
- The simpler alternative is to check from `startpos`. It differs from
  PCRE2 only when a lookbehind reaches back over an ill-formed byte, and
  then pcrec's lookbehind already fails to match there (ASK 1).

**What it promises**: an answer (match or nomatch) is given only for a
subject whose checked range is well-formed UTF-8. So every answer is also
the PCRE2_UTF answer, not the MATCH_INVALID_UTF one.

**Interaction with K50/K73.** The check runs FIRST. On a validated range,
a continuation byte at `startpos` is by definition inside a character, so
the K50 refusal (PCREC_ERR_STARTPOS) is then exactly PCRE2's BADUTFOFFSET.
The K73 offset-0 rule becomes unobservable: a subject that begins with a
continuation byte is refused at offset 0 before any search.

### 2.2 `scan`: the incremental check riding the engine

Under `-e utf8` the DFA's byte classes already separate continuation bytes
from leads (`UPC_NOSTART`). A validity automaton has 9 states: accept,
need-1/2/3, the four constrained second bytes, and reject. Its product
with the pattern's forward machine, with REJECT routed to an error sink,
detects ill-formedness in the same table step the scan already pays. Most
pattern states imply the validity state, because they sit mid-character
in a match. The start state's skip loop is what splits, into up to 8
copies.

**What it can promise, precisely**: *let R be the bytes the artifact's
forward scan actually read. If R contains the first byte of an ill-formed
sequence, the call returns `PCREC_ERR_UTF` at the first such offset in
scan order. Otherwise the answer is the unchecked artifact's answer.* What
it CANNOT promise:

- **Not PCRE2's contract.** `a` on `a\xff` succeeds, because the scan stops
  at the match's end; 10.46 refuses it (§1).
- **R is an implementation fact.** Every byte-skipping mechanism removes
  bytes from R: the memchr/offset-set prefilters, the whole-window
  pre-checks (`REQ_BYTE`/`REQ_RUN`), the scan edge's run loop, the pinned
  search, and the end-window clamp. So the SAME subject can be accepted by
  one pcrec version and refused by the next. Either the contract moves
  with the optimizer, or the row must deny all of those mechanisms and
  give up most of the DFA's speed.
- **No VM coverage.** The VM has no per-byte table. Its class tests fail
  on an ill-formed sequence without distinguishing it from a non-match. A
  hybrid's DFA prefilter could carry the sink, but only over the bytes the
  prefilter reads, which are again optimization-dependent.
- **Cost moves into state count, not time.** It is up to 9x states in the
  worst case, and in practice the start family grows by about 8 states. It
  counts against `PCREC_MAX_DFA_STATES_*` and the emitted-size caps, so it
  can MOVE THE REFUSAL SET, the K53/K59 hazard class.

The row's one real advantage is that each call checks only what it reads.
So a find-all loop stays linear, where the precheck is quadratic (§4.3).

## 3. One selection table, not two mechanisms

The option names a CONTRACT. The table picks the MECHANISM, first passing
row wins (memory `pcrec-decisions-as-first-match-tables`; `dfa_pfs[]`'s
idiom):

| # | row | predicate | mechanism |
|---|---|---|---|
| 1 | `inert` | the encoding restricts nothing (`byte`; no `start_guard`) | nothing: every byte string is valid |
| 2 | `off` | contract = off (the default) | nothing |
| 3 | `scan-fused` | contract = scan, AND the artifact's route is a DFA scan with no byte-skipping mechanism selected, AND the product fits the caps | the REJECT sink in the forward machine (NOT BUILT, §2.2) |
| 4 | `precheck` | contract ∈ {whole, scan} | the precheck residual call |

Row 4 is the total fallback, and it is legal for `scan` because the
precheck's promise implies the incremental one (every read byte is inside
a checked range). So a `scan` artifact that cannot take row 3 is never
refused. It pays the precheck instead, and a stamp says which row ran.
**If Frank rules only `whole` (the recommendation), row 3 is recorded here
and not built.** The table then has three live rows, and `scan` as a
spelling is not accepted until row 3 has a measured reason to exist.

## 4. The caller surface

### 4.1 The switch: a compile-time axis (recommended)

D18 compiles options away, and this tree never uses a runtime flag where
an emitted choice can be made. So the switch is an axis in `axes.def`: a
default-off FORCE-style bit, spelled `-futf-check` (or
`-futf-check=whole`, for **Q2**), with a `pcrec_options` field and a
config directive. A runtime switch would need a new `rx_ctx` field (an
`rx_ctx` layout change) and a new parameter on `<prefix>_search`. PCRE2
has one (NO_UTF_CHECK) mainly to escape the quadratic find-all (§4.3),
and §4.3's exported entry gives the caller that escape without it.

Under `byte` the axis is **inert** (row 1), not refused. That matches
`-fno-startpos-guard`'s inert-under-byte precedent (tuning.md §2.23).

### 4.2 The result code and the offset

- **One code, `PCREC_ERR_UTF` (-9)**, below `PCREC_ERR_FLOOR`. It is not a
  give-up, and it sits in the same family as `_STARTPOS` (-7) and
  `_UNSET_VAR` (-8). It goes in the shared `PCREC_RX_ABI_H` block. The
  six public entries return it, and `caps` stays untouched.
- **The offset comes from an exported encoding-residual entry,
  `<prefix>_utf_invalid_at(s, n, from)`.** It returns the first byte of
  the first ill-formed sequence in `[from, n)`, or `n`. Every `-e utf8`
  artifact carries it, whatever the flag. `next_pos` is the precedent for
  caller-facing residue, and the byte backend's body is `return n;`. A
  caller that received `PCREC_ERR_UTF` calls it with the same `from`, and
  pays for a second pass only on the error path. Writing the offset into
  `caps[0][0]` was considered and rejected: it would break §3.1's
  "untouched on every negative return" for one code.
- **One validator, three callers.** The precheck calls
  `<prefix>_utf_invalid_at`, the caller calls it for the offset, and
  `[VAR]`'s `$_var_valid(v, len)` becomes `$_utf_invalid_at(v, len, 0) ==
  len`, so the tree has one spelling of "well-formed UTF-8" rather than
  two (**Q7**). Like `var_valid`, it is NOT engine-callable: the ENTRY
  WRAPPER calls it once per call (DD-12 (7)'s terms, `var_valid`'s status
  in `entries_utf8[]`).

### 4.3 The find-all loop is quadratic under `whole`, as it is in PCRE2

§3.1's loop calls `<prefix>_search` once per match. Each call validates
`[startpos − L, n)`, so a subject with `m` matches costs O(n·m) validation
bytes. PCRE2 has the same property and documents NO_UTF_CHECK for every
call after the first. pcrec's answer without a runtime flag is for the
caller to validate once with `<prefix>_utf_invalid_at(s, n, 0)` and use a
non-checking artifact. The spec hunk must say so. **Q6** is whether that
is acceptable. The alternative is a stateful "already validated up to"
cursor, which the reentrancy contract (§5.3) forbids inside the artifact.

## 5. Cost, measured (darwin, directional)

Instrument: `utf_valid_evidence/utfcheck_bench.c`. It runs three strict
validators, every one checked to stop at libpcre2's own offsets on 8 cases,
over 64 MiB subjects, best of 7, taken twice (`bench_run1.txt`,
`bench_run2.txt`), at load average 7-10. The pcrec reference rates come
from `scanbench.c`, `-e utf8` artifacts, recorded in `scan_ref.txt`.

| ns/byte | ASCII text | ~1/3 two-byte (random mix) | CJK 8/9 three-byte |
|---|---|---|---|
| bytewise strict | 0.64 | 2.21 | 0.88 |
| 8-byte ASCII fast path + bytewise | **0.04** | 2.53 | 1.01 |
| byte-class DFA (one dependent table load/byte) | 1.97 | 1.98 | 1.92 |
| memchr pass (reference) | 0.025 | 0.024 | 0.025 |

| pcrec `-e utf8` call on the 64 MiB ASCII subject | ns/byte |
|---|---|
| `zq[0-9]x`: no match, answered by the offset-set prefilter | 0.0023 |
| `[a-z]+@[a-z]+`: no match, answered by the required-byte pre-check | 0.025 |
| `jumpz`: no match, a scanning call | 0.335 |

What the numbers say:

- **On ASCII text** the fast-path precheck costs 0.04 ns/byte. That is
  **17x** a call a prefilter answers, **1.6x** a call a pre-check answers,
  and **12%** of a scanning call.
- **On non-ASCII text** it costs 1.0-2.5 ns/byte, **3x-7x a full DFA
  scan**. The random-mix subject is the branch-predictor's worst case.
- The DFA-shaped validator's flat ~1.95 ns/byte is the per-byte price the
  fused row pays inside the scan loop's own dependency chain. In
  `[OPT-3]`'s terms, it is one more dependent load if the product is not
  merged into the pattern's table. This is why row 3 has to be a PRODUCT
  automaton and never a second walk.
- A SIMD validator (the simdutf family) is the known lever for the
  non-ASCII rows, and it is out of scope here: SIMD is LAST in this
  project's order (memory `pcrec-post-spine-direction`). The ASCII fast
  path is portable C, and it is a 16x win on ASCII, so the emitted
  validator should carry it (**Q8**). Today's `var_valid` does not.

## 6. Is it an abi event? Yes, once, when built

These move every artifact, default-off ones included:

1. `PCREC_ERR_UTF` joins the shared `PCREC_RX_ABI_H` block.
2. A `<PREFIX>_UTF_CHECK` selection stamp, `"inert" | "off" | "precheck"`,
   unconditional per the §6.3 family-(a) rule.
3. On utf8 artifacts, the new exported residual entry, and `var_valid`'s
   re-spelling on `[VAR]` artifacts.

It needs the full D76/D94 ritual. `rx_info` could mirror the stamp; D77
says not until a runtime reader exists.

## 7. What building `whole` would touch

This is a sketch, for pricing only.

- `src/enc/enc_utf8.c`: the `utf_invalid_at` entry with the ASCII fast
  path, and `var_valid` rebased on it.
- `src/enc/enc_byte.c`: the trivial body.
- `axes.def`, `lib/pcrec.h`, the `cli` flag, and the config directive.
- A `max_lookbehind_chars` fact, if Q1 rules the PCRE2 range.
- One emitter primitive (`pcrec_emit_utf_check`, the K50 guard's sibling),
  called at the same caller-facing sites K73's `pcrec_emit_start_zero`
  uses. Those are exactly the caller-facing bodies that need the check.
- The stamp and the spec hunks: match_api §3.1/§4/§6, tuning.md, and the
  cli spec.
- Checks: a 10.46-pinned differential over §1's cases plus a generated
  ill-formed family, a byte-inert identity arm, the default-off identity
  (every artifact moves by exactly the stamp line), a failing-direction
  plant for each of the three validator callers, and sabotage rows.

## 8. Questions for Frank

1. **The checked range.** PCRE2's `[startpos − maxlookbehind, n)` (needs a
   new fact plus a back-step walk), or the simpler `[startpos, n)`, a
   stated divergence only where a lookbehind reaches back over bad bytes?
   *Recommend PCRE2's.*
2. **Build `whole` only, and record `scan` (row 3) unbuilt until a
   measured need?** *Recommend yes.* If `scan` is wanted, it has to accept
   either an optimizer-dependent contract or denying every byte-skipping
   mechanism (§2.2).
3. **A compile-time axis** (`-futf-check`, default off), not a runtime
   `rx_ctx`/`search` flag? *Recommend compile-time (D18).*
4. **The offset** through the exported `<prefix>_utf_invalid_at` entry,
   rather than through `caps`? *Recommend the entry.*
5. **One code**, `PCREC_ERR_UTF` (-9), rather than PCRE2's per-kind codes?
   *Recommend one (D26).*
6. **The quadratic find-all** under `whole`: document it and point callers
   at validate-once plus a non-checking artifact, as PCRE2 documents
   NO_UTF_CHECK? *Recommend yes.*
7. **One validator** for the precheck, the offset entry and `[VAR]`'s
   `var_valid`, in the same abi event? *Recommend yes.*
8. **The ASCII fast path** in the emitted validator (16x on ASCII,
   measured)? *Recommend yes.* SIMD stays out.
9. **Under `byte`**, is the flag inert (stamp `"inert"`) or refused?
   *Recommend inert, `-fno-startpos-guard`'s precedent.*
10. **Order against K50**: the check runs before the startpos guard, so a
    mid-character `startpos` on a valid subject is still
    `PCREC_ERR_STARTPOS`, and an invalid subject reports `PCREC_ERR_UTF`
    even when `startpos` is also mid-character? *Recommend yes.* 10.46
    answers BADUTFOFFSET for a mid-character offset into a VALID subject
    (§1); its order on an invalid subject with a mid-character offset was
    not probed, and a build lane should probe it before pinning the order.
