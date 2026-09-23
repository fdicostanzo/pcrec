# Pattern variables — a runtime byte span at a fixed program point

**Status: PROPOSED.** Design only; nothing under `src/`, `cli/`, `lib/` or
`tests/` was touched. This is the pattern-side half of the variable design.
`variables_common.md` owns the expansion grammar (§1), the value model
(UNSET/EMPTY, §2) and the call interface's type and array rule (§3) — this
note depends on all three and does not restate them. `replace_design.md` is
the sibling consumer. `variables_roadmap.md` phases all three.

The feature: `^${prefix}-[0-9]+$` compiles **once**, and the caller supplies
`prefix`'s bytes per call, so one artifact matches a family of patterns.

## Inherited charter

**[RATIFIED]** plan row `[FEAT-VAR]` (`docs/dev/plan.md:1413`, filed by Frank
2026-09-02, `STATE:not-started`) is this note's charter and it records four
design questions "to record now, not answer." Three are answered here and one
is deliberately deferred by the 2026-09-23 charter:

- **(a) the determinization placement rule** — "a variable edge is an OPAQUE
  symbol... the placement rule is the whole design." **Deferred**: Frank's
  2026-09-23 charter says "Ignore the tricky DFA engine... If we do try it,
  that's a different effort." §6 records what the deferral costs and what
  re-opens it.
- **(b) "the edge must be a memcmp against raw bytes, never a class walk"** —
  **confirmed, and sharpened**: §1 finds the mechanism is not a `memcmp`
  either, because a caseless comparison under `utf8` cannot be one.
- **(c) "the backref module is the nearest existing runtime string compare"** —
  **confirmed by reading the code**, and it is nearer than "nearest": §1 argues
  a pattern variable *is* a backreference with a different span source.
- **(d) "the API surface is a D80 spec change... and a caller-observable
  stamp"** — **confirmed**; §4 gives the shape.

---

## 1. The mechanism — a backreference whose span comes from outside

### 1.1 What a literal is today, and why it is the wrong starting point

**[MEASURED]** by reading `src/gen/emit_vm.c`. The charter's framing —
"a VM instruction that compares against a caller-supplied byte span" as a
variant of the literal instruction — starts from a literal machinery that
does not exist in the shape it assumes:

- A literal byte is a **singleton `A_CLASS`** node; the parser normalizes
  every literal to one (`src/core/internal.h:328`).
- A literal *run* like `abc` is an `A_CAT` spine of three such nodes, emitted
  as three independent per-byte `if`/`goto` blocks (`emit_vm.c:8298-8319`).
  The shape is chosen by `vm_cls_shape`/`vm_cls_test` (`:1607-1659`):
  `byte == N`, or `(unsigned)(b-lo) <= hi-lo`, or `(b|0x20) == lower` for a
  compile-time ASCII fold pair, or a 32-byte bitmap read.
- **There is no compile-time-literal span compare in the VM's instruction
  stream.** The one `memcmp` in `emit_vm.c` (`:1566`) deduplicates class
  bitmaps in a pool, at COMPILE time, not in the emitted matcher.
  `src/gen/emit_dfa.c`'s `emit_req_run_check` (`:671-772`, landed at `[OPT-
  REQPOS]` tier 2b, abi 30) is the near miss that proves the distinction
  rather than the exception to it: it DOES emit a constant-length
  `memcmp(%s + rp_c, "…", L)` against a compile-time literal (`:710`, `:716`),
  for both engines — but it is a whole-window PRE-CHECK computed once before
  the scan begins, not an instruction in the per-position match loop, and it
  takes a compile-time literal it can never take a runtime operand for
  without becoming exactly the mechanism §1.3 below builds.

So "the literal instruction, with a runtime operand" names nothing. A literal
is not a span compare; it is a chain of byte tests the compiler unrolled
because it knew the bytes.

### 1.2 What a backreference is, and why it is the right starting point

`vm_bref` (`emit_vm.c:8103-8245`) is the VM's one runtime span compare, and
every property a pattern variable needs is already in it:

- **It reads a `(start, end)` pair discovered at match time**, out of the VM's
  own `slot_values[]`, chained over `a->u.bref.refs[]` for PCRE2's dupnames
  "first member that is SET" rule (`:8203-8213`).
- **It calls through the encoding seam, never inline**: `vm_rolef(v,
  "%s_bref_match%s", v->p, caseless ? "_caseless" : "")`, guarded by
  `pcrec_enc_entry_engine_callable` (`:8189-8194`), with `v->enc_mask` OR'd so
  the residual function appears only in artifacts that use it.
- **It returns a LENGTH, not a boolean**, and the reason is exactly the
  charter's caseless question: `src/enc/enc_byte.c:118-127` states that under
  an encoding whose fold is not length-preserving the bytes consumed need not
  equal the bytes compared, "which is why this entry returns a length rather
  than a bool."
- **It meters work on failure too**: a negative return encodes how many bytes
  *did* compare equal (`-(result)-1`), charged via
  `vm_work_at(v, ..., "took >= 0 ? took : -took - 1", ...)` (`:8234-8236`), so
  a `(a*)\1`-shaped pattern cannot do unbounded uncharged work.

**[PROPOSED]** therefore, and this is the note's central claim:

> A pattern variable is a backreference whose span is supplied by the caller
> instead of being read out of `slot_values[]`. Everything downstream of "here
> is a start and a length" is already built.

### 1.3 The minimal new operand form

What genuinely differs is one thing: a backreference's span is an offset pair
*into the subject*, so `bref_match(s, n, ref_start, ref_end, at)` needs one
buffer. A variable's bytes live in a **different buffer**. So the new seam
entry takes a pointer and a length rather than two offsets:

```c
/* src/enc/ — a new PcrecEncEntry row, engine_callable, per encoding. */
ptrdiff_t $_var_match(const unsigned char *s, size_t n,
                      const unsigned char *v, size_t vlen, size_t at);
ptrdiff_t $_var_match_caseless(const unsigned char *s, size_t n,
                               const unsigned char *v, size_t vlen, size_t at);
```

Same return protocol as `bref_match`, byte for byte: `>= 0` is subject bytes
consumed at `at`; `< 0` is no match with `-(r)-1` the bytes that did compare,
for the work charge. Under `byte` the body is `enc_byte.c:143-154` with `s[ref_start + i]`
replaced by `v[i]` and `need` replaced by `vlen` — a mechanical substitution.
Under `utf8` it is `enc_utf8.c`'s decode-and-fold loop with the same
substitution, **once the value is known well-formed** — see below.

**Where `variables_common.md` §2.1's UTF-8 well-formedness refusal lives, and
why it cannot live in the seam entry.** `enc_utf8.c`'s decoder returns 0 for a
truncated or ill-formed sequence, and its compare turns that into
`return -(ptrdiff_t)(j - at) - 1` (`:226-231`) — a silent NOMATCH, which is the
documented and correct rule for a *subject*, since the reference span there
came out of the automaton and is well-formed by construction
(`enc_utf8.c:274-278`: "ill-formed input matches nothing, never an error").
For a caller-supplied value that rule is the opposite of what §2.1 promises,
and the seam entry's return space is two-valued by sign — there is no third
value for "refuse the call" without breaking §1.3's "byte for byte" protocol.
So the well-formedness check does **not** move into `$_var_match[_caseless]`.
**[PROPOSED]** it runs once, in the calling wrapper, before the match begins —
an `O(vlen)` pass over the value, paid once per call per variable rather than
once per position, which is the general place a per-call precondition
belongs (the wrapper already owns `PCREC_ERR_UNSET_VAR`'s check, §5). Once a
value has passed it, both the caseless and the `exact` `utf8` compares can
keep assuming well-formed input exactly as the subject-side code already
does — `enc_utf8.c`'s `u8_defs_bref` (the exact `utf8` compare) is a byte loop
identical to `byte`'s and never decodes at all, so a value that reached the
compare well-formed is the only case either compare needs to handle, and
`${v}` and `(?i)${v}` agree.

**[PROPOSED]** the emitted VM block is `vm_bref`'s, with the span source
swapped:

```c
    took = rx_var_match(subject, subject_length,
                        vars[RX_VAR_PREFIX].p, vars[RX_VAR_PREFIX].len,
                        scan_position);
    if (took < 0) goto rx_fail;
    scan_position += (size_t)took;
```

That is the whole instruction. No new opcode family, no new dispatch, no new
`VEKind` beyond a listing event for `--emit-ir` (§4.4).

### 1.4 The AST kind

**[PROPOSED]** one new `AKind`, `A_VAR`, with its own `union u.var` member per
D70's rule (a new kind gets a new member, and every whole-tree walker with no
`default:` becomes a forced audit site — §2). It carries the variable's
compile-assigned index, a caseless bit, and the reference's expansion program
(`variables_common.md` §5's expansion half, resolved to a small template the
wrapper evaluates before the match).

`A_VAR` is `A_BREF`'s structural twin and `internal.h`'s own comment on
`A_BREF` (`:480-511`) is already the right comment for both: it "consumes a
VARIABLE number of bytes decided at MATCH time, which no `A_CLASS` can
express." The one difference to state in the new kind's header, because it is
the one that matters to every analysis: `A_BREF`'s span is a slice of the
*subject*, so its bytes are at least *in* the text being matched; `A_VAR`'s
bytes are not in the subject at all and have no relationship to it.

---

## 2. What the optimization passes see

**[PROPOSED]** `A_VAR` is an opaque span of unknown bytes and unknown length —
`0 <= len` with no upper bound. Every analysis must decline across it.

The tree makes this safe by construction rather than by diligence: **each of
these files has an exhaustive `switch` over `AKind` with no `default:`**, a
house rule `src/opt/mrl.c:39-45` states as "a node kind added after this file
is written must be a COMPILE ERROR here" — **under `-Wswitch`, which `make
strict` promotes to an error** (`Makefile:1229-1233`; the default `make` build
is `CFLAGS ?= -O2 -g` with no `-Werror`, deliberately, per the root
`CLAUDE.md`). So adding `A_VAR` does not risk a silently-wrong analysis under
`make strict`, which CI runs on every PR and push (`.github/workflows/
ci.yml`); a contributor's plain `make` sees the missing case as a warning, not
a build failure, and what an unhandled kind does at that point differs by
site — some spin forever in a bare `for (;;)`, some silently fall to a
`return;` — so the alarm is real in CI but the sentence should not promise
more than a plain `make` delivers.

Each arm below is the same answer `A_BREF` already takes, which is what makes
this a widening of an existing decline rather than a new decline:

| analysis | file / function | today's `A_BREF` arm | `A_VAR` arm |
|---|---|---|---|
| necessary byte + necessary run ([OPT-REQBYTE], [OPT-REQPOS] 2b) | `src/opt/reqbyte.c`, `rb_walk` (`:380`, switch `:387`) | `case A_BREF: case A_CALL: acc.runs = rr_cat(rr_none(), acc.runs); return acc;` (`:487-494`) — the empty set, "always sound" | **join the same case label.** The empty set for both the byte set and the run |
| start anchor ([OPT-ANCHOR-VM]) | `src/opt/startanch.c`, `sa_walk` (`:70-134`) | `case A_BREF: case A_CALL: return acc;` (`:129-131`) | same case label; contribute nothing |
| end window ([OPT-ENDWIN]) | `src/opt/endwin.c`, `ew_walk` (`:81-141`) | `case A_BREF: case A_CALL: return EW_NONE;` (`:136-138`) | same case label; `EW_NONE` |
| min/max width | `src/opt/mrl.c`, `pcrec_minw`/`pcrec_cwmin`/`pcrec_cwmax` | `A_BREF` contributes `0` to `minw` and to `pcrec_cwmin`; `pcrec_cwmax`'s `A_BREF` arm already returns `PCREC_W_UNBOUNDED` | `minw = 0` and `pcrec_cwmin = 0` (a variable may be EMPTY); `pcrec_cwmax` joins `A_BREF`'s existing unbounded arm |
| first-byte set / prefix, frequency prior | `src/opt/prefix_k.c`, `wclose` (`:172-221`) | no `N_BREF` kind exists — the analysis runs over the lowered `Nfa`, and backref-bearing patterns are VM-only with no prefilter, so they never reach it | **structurally unreachable, identically.** §3's `has_var` PREFILTER predicate is what declines the prefilter build before this pass runs — engine selection alone (the registry row) makes the pattern VM-only but does not, by itself, stop a prefilter from being built; it is the third whole-tree predicate in `prefilter_decision` that does that |

Two consequences worth stating rather than leaving to be discovered.

**`pcrec_cwmax`'s `A_BREF` arm is already unbounded, and `A_VAR` joining it is
free.** There is no `pcrec_maxw` — that function was retired at [M5.0] stage
2 and `pcrec_cwmax` (BYTES) took its role; `src/core/internal.h:5864` records
the rename. `pcrec_cwmax`'s `A_BREF` arm already returns `PCREC_W_UNBOUNDED`
(`mrl.c:339-341`, "this is the one arm where minw's 'and it is EXACT' argument
does not carry over to maxw"), for the header's own stated reason
(`:295-303`): a backreference's width is a match-time quantity, not derivable
at compile time — exactly the property `A_VAR`'s value has too. So the arm
`A_VAR` needs is the one `A_BREF` already has, and every consumer is already
written for it: `src/opt/endwin.c:171-172` tests `w >= PCREC_W_UNBOUNDED` and
bails; `src/opt/startanch.c:84` tests `pcrec_cwmax(a->l) == 0`, which an
unbounded value fails; and `src/parse/mod_lookaround.c:307/318`'s
fixed-width rule (`pcrec_cwmin(branch) == pcrec_cwmax(branch)`, both finite)
already refuses a lookbehind containing a backreference for the same
reason (`mrl.c:300-303`) — **so a lookbehind containing a variable,
`(?<=${v})x`, is refused for free too, by the identical mechanism**, provided
`A_VAR` joins `A_BREF`'s arm in both `pcrec_cwmin` and `pcrec_cwmax`. No
function in the tree computes a byte-unit upper bound for a backreference or
a variable, and none is needed: `pcrec_cwmin = 0` is exact and safe for the
byte-width consumers that read it (`emit_vm.c`'s `Vm.fmin` accumulator, the
MRL clamp).

**The forced-audit surface is larger than the five-row table above, and the
honest number matters to sizing.** A brace-matched census of every `switch` in
`src/`, `cli/`, `lib/` whose body contains a `case A_…` label (comments and
string literals stripped) finds **44 `AKind` switches with no `default:`**,
across **17 distinct files** — `src/core/internal.h`, `src/gen/emit_vm.c`
(8 sites), `src/ir/nfa.c`, `src/opt/{altcls,atomic (10 sites),endwin,lower_enc
(3),mrl (3),possessify (3),reqbyte,revdet (4),select_engine,startanch}.c`,
`src/parse/{definitions,mod_backrefs,mod_lookaround,parse (2),rxt_compose
(2)}.c` — against 5 switches that carry a `default:`. **Most of the 44 are not
declines.** The five-row table above is the ANALYSIS-DECLINE population; the
rest are sites that must do real work, not join an existing empty-set case
label: `src/ir/nfa.c:586` must LOWER the kind (there is no NFA representation
for `A_VAR`, so this arm routes it to the same loud internal error `A_BREF`
takes at `:908` — the only sound arm, since neither ε-erasure nor Σ*-erasure
is safe here, the same reasoning `select_engine.c` already applies to
`A_BREF`/linked `A_CALL`; this is a declared unreachability, not a decline);
`src/gen/emit_vm.c:8303` must EMIT it (§1.3's instruction); `src/opt/
lower_enc.c:476/517/592` must decide whether the variable's stored expansion
template (`variables_common.md` §5, `${…:-word}`'s literal fallback text)
lowers under the artifact's encoding; `src/parse/definitions.c:149`
(`pcrec_ast_is_core`) must rule the kind core or reducible — its own header is
explicit that this function is EXHAUSTIVE, NO DEFAULT, "a new `AKind` is a
compile error here until this function states which side of the reduction it
falls on"; and `src/parse/rxt_compose.c:288/442` must place it in the
composer's leaf lists. (The five `AKind` switches that carry a `default:` arm
instead — `internal.h:877`'s own census names four; `known_issues.md` K63
records that there are actually five, `vm_isl_words` postdating the census —
are all safe for `A_VAR` without a code change, per `[VAR]`'s D6 panel; this
is a tree-audit fact recorded there, not a design decision this note makes.)
**This is `[PATFACTS]`'s first outside customer**, and
D120 (`docs/dev/decisions.md:8171-8200`, plan row `docs/dev/plan.md:560`,
`STATE:not-started`) — one per-pattern analysis record computed once after
`pcrec_lower_enc` and read by every pass, on Frank's own observation that "we
are doing a bunch of analysis in various places... it's ad hoc" — absorbs the
five one-line ANALYSIS declines specifically; it does not and cannot absorb
`nfa.c`'s lowering or `emit_vm.c`'s emission, which are real per-kind work no
shared record removes. **[PROPOSED]** the sequencing note, not a dependency:
if `[PATFACTS]` lands first the five analysis declines are one field each; if
it does not, they land as written and migrate under `[PATFACTS]`'s own
implement-then-replace clause, which D120 explicitly sanctions ("new
analyses... may land in today's shape and migrate"). Neither order blocks the
other, and neither order touches the sites that are not declines.

---

## 3. The DFA declines, and the ENGINE decline is free — the PREFILTER decline is not

**[PROPOSED]** a pattern containing a variable compiles to the VM engine only.

**Engine selection needs no code in `src/opt/select_engine.c`.** Engine
selection is a mask ANDed across a small table of analyses (`:393-417`), of
which `forces_registry` (`:318-343`) is the generic one: it walks the tree for
the first node whose registry row's `engines` mask excludes `ENGM_DFA`
(`:237`), and uses that row's own `syntax` string as the diagnostic's reason
(`:341`). This is SR-8's whole point — "a fifth VM_ONLY module needs no line
here."

**But the PREFILTER decline is a separate decision in the same file, and it is
not registry-driven — this design owes it a line.** `prefilter_decision`
(`select_engine.c:549`) carries hand-written, construct-named predicates:
`has_bref = pcrec_has_bref(root)` (`:606`) and `has_call =
pcrec_has_linked_call(root)` (`:648`, `[DD-14]`'s own precedent for exactly
this shape — module `recursion`'s subroutine calls, `internal.h:4398`), each
feeding a `-fprefilter` refusal that names the construct in its own text
(`:653-657`). A VM-only pattern normally still gets a hybrid DFA prefilter
(`engine_m4.md` §6.1, `[OPT-4]`), so "VM-only" and "no prefilter" are two
facts with two mechanisms, and `A_VAR` needs the second one stated: `src/ir/
nfa.c`'s `compile_ast` (`:583`, switch `:586`) sends `A_BREF` and a linked
`A_CALL` to a loud internal error at `:908` — "a backreference and a linked
call are loud internal errors (nothing may build a machine for either)" — and
a var-bearing pattern reaches that same state by the identical route. So the
design adds a **third** whole-tree predicate, `has_var = pcrec_has_var(root)`,
following the mechanism that already exists (the same shape `has_bref` and
`has_call` take), plus the third named noun in the `-fprefilter` refusal's
text. `[PATFACTS]` (D120) is named, as it is in §2 below, as the eventual
general home for all three predicates via its implement-then-replace clause —
the interim hand-written predicate is not a permanent parallel mechanism, it
is the acceptable shape while D120 has not landed.

So the decline is: **one `RegRow` for the `${` doorway with `engines =
ENGM_VM` and `syntax = "${…}"`** for engine selection, **plus the third
prefilter predicate** above for the prefilter decline, and the module's
producer stamping every `A_VAR` it builds with the registry row
(`pcrec_ast_stamp`, D67). Everything else follows:

- `--engine=dfa` refuses with the existing sentence, `select_engine.c:1022-1039`:
  `"${…} requires the VM engine, which --engine=dfa excludes"`.
- `--features` with module `vars` off gives the ordinary
  `"requires module 'vars'"` refusal, which D26 tier 3 says discharges the
  diagnostic obligation **in full** — no PCRE2 wording is reproduced anywhere.
- `rx_info.engine_why` carries the reason for a caller to read, with no new
  field.

**[PROPOSED]** how the new row resolves against the shipped bare `$` row.
`src/parse/registry.c:1542` carries `{RK_BARE, '$', NULL, "$", 0, …}` — a bare
row on the byte `$` with a NULL tail, which SR-9's `byte + tail` design
(`pcrec_recognise_tail_default`, `registry.c:1753-1764`) already resolves
correctly: a tailed row (this design's `${` row) always outranks the
tail-less fallback, so `${` parses as the new doorway and a lone `$` not
followed by `{` still falls through to the existing bare row and parses as
`A_EOL`, exactly as `variables_common.md` §0.2's "matches nothing" proof
requires when module `vars` is off. No new mechanism — the existing
tail-arbitration rule is the whole answer, and it is worth stating rather
than leaving a reader of the parser half to re-derive it.

**Why the DFA route is deferred rather than refused.** `[FEAT-VAR]` (a) is
right that the hard part is *placement*: determinization cannot see the
variable's bytes, so a variable edge is sound only where the automaton's
decision at that point does not depend on them. Frank's own example,
`(${v}|ab)c`, cannot be determinized without the bytes. That is a real design
with a real prize (a variable in a DFA-shaped pattern keeps the DFA's
throughput), and the 2026-09-23 charter defers it as "a different effort."
`variables_roadmap.md` phase 5 carries it with the one thing that would open
it: a measured pattern family where the VM route's throughput is the
bottleneck and the placement rule's precondition holds.

---

## 4. The call interface

> **[OPEN-FRANK]** §4.1's proposal below makes `<prefix>_match` and
> `<prefix>_match_caps` gain a `const rx_var *vars` parameter — but
> `<prefix>_match` **is** `rx_matchfn`, a fixed-literal ABI type shared by
> every artifact (`docs/spec/match_api.md:915-918` declares
> `ptrdiff_t rx_matchfn(const rx_ctx *ctx); ptrdiff_t <prefix>_match(const
> rx_ctx *ctx);`, emitted unconditionally at `src/gen/emit_dfa.c:1013`, and
> `match_api.md:1238`/`lib/pcrec.h:1326` bind the unprefixed spelling to
> composability — installing `<prefix>_match` as a callout (`rx_callout_ref.
> fn`) or invoking it as a composed submatcher across differently-prefixed
> generated matchers). §4.1 makes a var-bearing artifact's `<prefix>_match`
> **no longer an `rx_matchfn`** — a narrower version of the exact harm D38
> rejected in the sentence §4.2 itself quotes approvingly ("it changes
> `rx_matchfn`'s signature for every caller"), scoped to var-bearing
> artifacts rather than all of them, and the note does not currently mark
> the tension. §4.1 and §4.2 as written contradict each other.
>
> **The manager's recommended option, for Frank to rule on:** a var-bearing
> artifact's match entry gets its own fixed-literal typedef,
> `rx_varmatchfn` (`rx_matchfn`'s shape plus the trailing `vars` parameter),
> declared alongside `rx_matchfn` and named in `rx_info`/the artifact's
> stamp; a var-bearing artifact is **not** a composable submatcher or
> callout target in the MVP — declined, with a named re-open condition: a
> measured need to compose a var-bearing artifact as a callout or
> submatcher. Alternatives, one line each: **(a)** vars ride `rx_ctx`
> instead — rejected by this note's own §4.2 per-binding argument (a
> variable environment is per-*call* input, not per-*binding* state); **(b)**
> a separate `<prefix>_match_vars` entry beside an unmodified,
> `rx_matchfn`-shaped `<prefix>_match` that simply refuses on a var-bearing
> pattern — two entries per var-bearing artifact, D18's cost for keeping one
> code path per axis.

### 4.1 The shape

**[PROPOSED]**, and the argument is `variables_common.md` §3.3's, which is not
repeated: **the artifact's existing entry points gain a `const rx_var *vars`
parameter. No new entries, no `rx_bind`, no bound state.**

```c
#define RX_NVARS       1
#define RX_VAR_PREFIX  0

int       rx_search    (const unsigned char *s, size_t n, size_t startpos,
                        ptrdiff_t (*caps)[2], const rx_var *vars);
ptrdiff_t rx_match     (const rx_ctx *ctx, const rx_var *vars);
ptrdiff_t rx_match_caps(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2],
                        const rx_var *vars);
```

and identically for the three `_in` siblings, so the caller-buffer feature
([DD-14.FB]) composes rather than conflicting. `vars` is last so the `_in`
descriptor's position is unchanged in the sources of anyone reading both.

**Why a bound state is refused, in one line each:** `docs/spec/match_api.md`
§5.3 is a *binding contract on future emitters* that a generated matcher holds
no mutable state; §10.5 already refused the identical convenience for frame
buffers ("no way to set a buffer once per artifact or per thread") because it
would be mutable state or thread-local, and thread-local fails reentrancy. A
`rx_bind(vars)` handle is that refusal's exact shape one noun over.

**Thread safety** therefore needs no new rule, only one more noun in §5.3's
existing one: concurrent calls are fine provided each has its own `caps` array
**and its own `vars` array**. The artifact still holds nothing.

**[PROPOSED]** the descriptor's memory-safety precondition, stated explicitly
because it is caller data rather than structural. `bref_match`'s precondition
is *structural*: `ref_start <= ref_end <= n` holds because the caller passes a
PUBLISHED capture pair, and a published pair is ordered by construction
(`enc_byte.c:113-116`). `$_var_match(s, n, v, vlen, at)`'s `v`/`vlen` have no
such construction — they are caller fields, and `variables_common.md` §2.2's
`p == NULL` vs `len == 0` spelling leaves the pair `p == NULL && len > 0`
unspecified. The contract: **`p == NULL` implies `len` is ignored** (UNSET is
determined by `p` alone), so a caller-supplied `len` on a NULL `p` is never
read and never a null-deref hazard — the artifact checks `p` first, at the
entry wrapper, before any use of `len`, the same refusal shape
`PCREC_ERR_UNSET_VAR` already gives a bare `${name}`. `${name:-}` admitting an
UNSET value into the match path (§5) still resolves to a concrete, non-NULL
zero-length span by the time it reaches `$_var_match`, since the expansion
half (`variables_common.md` §5) runs before the seam entry is called.

### 4.2 The callout-ABI precedent, and where it does *not* reach

`design_callout_abi.md` §1.1 is worth citing precisely, because it is the
nearest thing in the tree to "caller-supplied data reaching the engine," and
it is **not** the right precedent here:

- `rx_ctx` carries `void *user`, filled from a `rx_callout_ref` binding unit,
  and the D38 ruling explicitly **rejected** both alternatives a variable
  design might reach for: a process-global `user` pointer ("defeats the point
  of per-binding state") and a per-call `user` parameter threaded through
  every call site (Frank: "ouch — over-callback-friendly, and it changes
  `rx_matchfn`'s signature for every caller to serve the minority that needs
  it").
- That second rejection is the one to read carefully, because §4.1 does
  something adjacent: it changes an entry's signature. The difference is that
  `rx_matchfn` is a **fixed-literal ABI type shared by every artifact** —
  changing it taxes every caller. A `<prefix>_search` signature is
  **per-artifact** and already varies (`<PREFIX>_NCAPS`, the `_in` family, the
  DFA/VM split), so the parameter appears only on artifacts whose pattern has
  variables, and a var-free artifact's entry SIGNATURE is unchanged. (§5's
  own byte-identity claim for the shared ABI block, once `PCREC_ERR_UNSET_VAR`
  lands, is narrower than "byte-identical" and is stated precisely there: a
  var-free artifact is unchanged except for the `abi` digit every artifact
  carries.)

So the precedent constrains the design without supplying it: variables do not
ride `ctx->user`, because `user` is per-*binding* state for a callout and a
variable environment is per-*call* input to the match.

### 4.3 Stamps and the abi event

**[PROPOSED]** this is caller-observable, so the D76/D94 ritual applies in
full: an `abi` bump, the identity-gate re-pin, a `docs/spec/match_api.md` hunk
in the same change (D80), and the site list found **by grep over the current
abi number**, never hand-enumerated — D94's own lesson, and the
`battriage`/`evtriage3` addendum that a reader whose text cites a *byte count*
and no abi digit still moves with it.

The stamps: `<PREFIX>_NVARS` and one `<PREFIX>_VAR_<NAME>` index macro per
variable; `rx_info.nvars` **appended at the end** of the struct per §6's
standing rule so no existing member's offset moves; and a `vars` names table
on the `rx_info.groups` model — **in the MVP, not conditional** (§9 Q2), since
it is the only route a name-indexed consumer (the `.rxt` test harness's
driver, §5 of the common note) has from a `.rxt` case's variable name to the
compiled artifact's `RX_VAR_<NAME>` slot, and deferring it would be a second
`abi` event for a table that costs `.rodata` only.

**One named site the `abi`-grep ritual does not reach on its own, because it
asserts a POPULATION from the test rather than from the artifact:**
`tests/codegen/run_codegen_tests.sh`'s `[M5-SEAM]` fixture table
(`:1349-1359`) is one row per pattern with per-entry call counts
(`next_pos:0,bref_match:1`, …), fails if an artifact's declared entry set
differs from its fixture's (`:1287`, "asserted from the TEST and not read off
the artifact"), and carries EXACT population pins for its existing residual
families (`:1373` five, `:1395` seven). Adding `var_match`/
`var_match_caseless` as engine-callable entries moves the entry-set assertion
on every new fixture and needs its own per-site count rows and its own exact
population pin, or the pair ships with no detector — the implementer owes
this the same treatment `bref` and `back_step` each already have. (The two
new `PCREC_ENCE_*` bits take the next free values, `1u << 4` and `1u << 5`,
after `enc.h`'s current top bit `PCREC_ENCE_BACK_STEP` at `1u << 3`;
`Job.enc_mask` is `unsigned` at `internal.h:2295`, so there is room, and
`src/enc/CLAUDE.md` gets the update its own third-encoding-recipe section
implies.)

### 4.4 `--emit-ir`

D108 and `dd8_report.md` made the listing a machine-first TSV of named
`#section` blocks. **[PROPOSED]** one `VE_VAR` listing event carrying the
variable's index and its caseless bit. **Not** a row in the `slots` family:
the `slots` section reports `slot_values[]` slots specifically —
`VE_SET`'s own comment is "a: `slot_values` slot" (`emit_vm.c:263`), and
[DD-8] gave the section a FAMILY column exactly to classify entries like this
one. `A_VAR` occupies no slot — its span is external, which is this note's
own central claim (§1.4) — so putting the row in `slots` would make the
`irsb` baseline assert a falsehood. `VE_VAR` gets its own section, or joins
`program`; reserving the enumerator with no producer yet has precedent
(`VE_ISLAND`, `VE_CALLOUT` at `:269-270`). The `irsb` byte-identity arm
(`w1stage0.md` (2)) is the gate that would catch a drift, and a var-free
artifact's listing is unchanged.

---

## 5. UNSET in a pattern — the opinion the charter asks for

**[PROPOSED]** an UNSET variable reaching a *bare* `${name}` at match time is
a **refused call**, not a compile-time error and not an empty match.

The three candidates and why two lose:

- **A compile-time error is not available.** The value arrives at match time.
  The compiler knows the name is *mentioned*; it cannot know whether the
  caller will fill the slot. There is nothing to diagnose at build time.
- **Rendering it as empty is the dangerous one.** `^${prefix}-[0-9]+$` with
  `prefix` unset silently becomes `^-[0-9]+$` and matches inputs the caller
  never authorized. The failure is invisible, it widens the language, and it
  sits on the same boundary `variables_common.md` §4.2's literal rule exists
  to defend. It must be loud.
- **A refused call is loud, cheap and already has a home.** `docs/spec/
  match_api.md` §4 defines a class *below* `PCREC_ERR_FLOOR` for "not a
  give-up": `PCREC_ERR_INTERNAL` (-6) and `PCREC_ERR_STARTPOS` (-7).
  `PCREC_ERR_STARTPOS` is precisely this shape — a **caller refusal**, where
  "nothing was attempted and `caps` is untouched." **[PROPOSED]**
  `PCREC_ERR_UNSET_VAR` is its second instance and needs no new vocabulary,
  only the next value.

  **This value lands in the shared ABI block, which `src/gen/emit_dfa.c`
  emits UNCONDITIONALLY into every artifact** (`:1034`, `:1051`, `:1073` are
  straight `puts` of the three existing `#define` lines with no gate) — the
  same block `docs/spec/match_api.md:178-179` records moving abi 24→25 for
  the last such addition ("`[K50]` ... **every artifact** gains `#define
  PCREC_ERR_STARTPOS (-7)` in the shared ABI block"). So the VALUE
  `PCREC_ERR_UNSET_VAR (-8)` is fixed once, in the spec, for every artifact —
  but its **emission** is gated on whether the artifact is var-bearing, the
  same `enc_mask`/residual pattern the encoding seam already uses to keep a
  var-free artifact's *entries* unchanged. Under that gate, a var-free
  artifact stays byte-identical across this module's landing **except for the
  `abi` digit itself** — the one line every artifact carries regardless — and
  that is the precise claim, not an unqualified "byte-identical," since §4.3's
  identity gates re-pin against the new `abi` number in the same change as
  every prior such event.

And the caller's opt-in to permissiveness is explicit and already in the
grammar: `${name:-}` for "empty is fine, use nothing", `${name:-dev}` for a
real default, `${name:?}` for "refuse, and this is the message." The default
is the safe one; the permissive ones are written down where a reviewer sees
them.

**The asymmetry with the replacement side is deliberate** and
`variables_common.md` §2.4 carries the reason: an unset group rendering empty
in a template produces wrong *output* (visible, recoverable); an unset
variable rendering empty in a pattern produces a wider *language* (silent,
security-relevant). D38 Q3 already ruled the template side's default empty via
a generation axis, and that ruling stands untouched. Two consumers, one model,
two defaults, each matched to its own blast radius.

---

## 6. Caseless — viable now, and the charter's own proposal is the one to decline

The charter asks whether caseless is viable, and leans toward preprocessing
the value ("if we can preprocess the variable, it might be viable"). The
answer is that caseless is viable *without* preprocessing, and preprocessing
is wrong.

### 6.1 It is already built

`<prefix>_bref_match_caseless` ships today. **[MEASURED]** from the source:

- Under `byte`, `enc_byte.c:165-190` spells the ASCII fold arithmetically
  **inline in the residual text** (`if (x >= 'A' && x <= 'Z') x += 32`), never
  as a run-time flag on top of the case-sensitive entry — D23's rule, whose
  own measurement was that a run-time fold indirection cost **26%** on a
  pattern containing no letters.
- Under `utf8`, `enc_utf8.c` decodes one character per side and folds through
  a generated 1,484-pair map (`utf8_fold_pairs.inc`).
- **The length-changing case is already handled end to end.** `src/enc/
  CLAUDE.md`: "`^(k)\1$` on `k` + U+212A is a match of length 4, one byte
  captured and three consumed." `tests/utf8/axis06_caseless_fold.rxt`
  (`:25-37`) pins it directly — pattern `k`, `flags i`, `encoding utf8`,
  `m "\xe2\x84\xaa" 0 3`: a one-byte pattern literal matching a three-byte
  KELVIN SIGN.
- And `tests/utf8/axis07_caseless_1ton.rxt` pins the negative control: pcrec's
  fold is **simple (1:1)**, like PCRE2's — `ß` does not match `SS`, `ﬁ` does
  not match `fi`. Eleven blocks, twenty-two cases.

So a caseless pattern variable is the *same work* as a caseless
backreference, which shipped. It is `$_var_match_caseless`, the mechanical
substitution of §1.3.

### 6.2 Why preprocessing the value is wrong

Folding the value once at the top of the call looks cheaper and is incorrect
for a reason that is structural rather than a matter of care:

- **A fold is a relation between two sides, not a normalization of one.** The
  subject side has not been folded. Comparing a pre-folded value against raw
  subject bytes fails on every subject that carries the other case.
- **Folding both sides is not available**, because the subject is the caller's
  and the matcher does not own a buffer to fold it into — and folding it per
  position would cost far more than the per-character fold already does.
- **Under `utf8` there is no canonical byte string to fold to.** The fold can
  change byte length (§6.1's KELVIN case, 1 ↔ 3), so a pre-folded value's
  length no longer corresponds to the subject bytes it should consume — which
  is exactly why `bref_match` returns a length rather than a boolean in the
  first place. A pre-folded `memcmp` cannot express the answer.

The `byte` encoding is the one case where pre-folding *would* work, since the
ASCII fold is length-preserving and 1:1. **[PROPOSED]** decline it anyway:
it would be a per-encoding special case of a general mechanism that already
covers both encodings, at zero measured gain (the general form is one
arithmetic fold per byte, which is what the pre-folding would also cost), and
it is the shape memory `pcrec-general-mechanisms-not-special-cases` names.

### 6.3 What *is* deferred

Not caseless matching, but **caseless expansion operators**: `${name^^}`
uppercases the value's *text*, which is a transform in the expansion half
(`variables_common.md` §5) and is a different thing from matching the value
caselessly. Under `utf8` an uppercase transform has the 1:n problem
`axis07` pins — `ß` uppercases to `SS`, two characters — and pcrec's fold
tables are 1:1 by design. **[PROPOSED]** `^`/`^^`/`,`/`,,` ship ASCII-only in
their phase and refuse by name under `utf8` until a 1:n case-mapping table is
vendored, which is a `third_party/` question of its own and not this
feature's.

---

## 7. Declines and refusals, collected

Every refusal this feature introduces, with its class, so a reviewer can check
the list against the code rather than reconstructing it.

| situation | when | class | shape |
|---|---|---|---|
| module `vars` not enabled, pattern contains `${` | compile | module gate | `"requires module 'vars'"` (D26 tier 3, discharged in full) |
| `--engine=dfa` on a var-bearing pattern | compile | engine selection | `"${…} requires the VM engine, which --engine=dfa excludes"` — the existing sentence, free (§3) |
| nesting deeper than the `limits.def` bound | compile | limit | the ordinary limit refusal, visible to `--list-limits` |
| a variable named in the pattern but the artifact built `--no-captures` | — | **not a refusal** | variables are independent of captures; the two features do not interact |
| UNSET value at a bare `${name}` | run | caller refusal | `PCREC_ERR_UNSET_VAR`, below `PCREC_ERR_FLOOR`, `caps` untouched (§5) |
| value is not well-formed UTF-8, artifact is `-e utf8` | run | caller refusal | same class, `variables_common.md` §2.1 |
| `${name^^}` under `-e utf8` (phase) | compile | deferred capability | refuse by name; §6.3 |
| a value that is pattern syntax | — | **never** | matched literally, always; `variables_common.md` §4.2. Not an unbuilt opt-in — re-homed to `[LIB]`/definitions |

---

## 8. The four lenses

| lens | verdict |
|---|---|
| **specific vs general** | **GENERAL**, and more so than the charter anticipated. The feature adds one AST kind, one registry row and one encoding-seam entry pair, and every one of those is an existing *kind* of thing with existing siblings. The instruction is `vm_bref`'s with one operand changed. The decline arms join `A_BREF`'s own case labels rather than adding new ones. The one genuinely new surface is the entry parameter, and it is per-artifact. |
| **core vs derived** | **DERIVED.** No automaton changes: determinization, minimization, the DFA emitter and every optimization pass are untouched. The DFA engine route declines rather than adapting, and the VM hybrid's prefilter route declines too, via its own third whole-tree predicate (§3) rather than by adaptation. The VM gains one emit arm. The five analysis arms are declines, not new derivations. |
| **applicable vs assumption-changing** | **APPLICABLE**, with the one assumption that *would* change named and refused: a value is never pattern syntax (§7's last row). A build with module `vars` disabled is unchanged in EMITTED CODE for every var-free artifact — recognition is live and production is gated (D34 ruling 5), and `variables_common.md` §0.2 proves the gated spelling matches nothing — except for the shared ABI block's `abi` digit, which every artifact carries regardless of whether it uses variables (§5's precise statement); the gate protects a population of patterns that could never have worked. |
| **fits-arch vs refactor** | **FITS**, with one debt named rather than hidden. Everything lands in an existing mechanism: `AKind` + `union u.*` (D70), a registry row (SR-8), `PcrecEncEntry[]` (`src/enc/enc.h`), `axes.def` for the deny flag, `limits.def` for the nesting bound, the `rx_info` append rule, the D76/D94 abi ritual. The debt is the five analysis sites that must stay in step — which is D120's `[PATFACTS]` charter arriving with a new instance rather than a refactor this feature has to perform (§2). |

---

## 9. Open questions

Numbered; recommendations are this note's, not rulings. `variables_common.md`
§7 carries the questions that are common to both consumers and are not
repeated here.

1. **Does a use site declare a bound?** §2 gives `A_VAR` `minw = 0`, `maxw`
   unbounded, which declines every width-dependent optimization across it. A
   declaration — a non-empty assertion, or a byte range — would restore some.
   *Recommend: not in the MVP.* D77: the prize is a set of optimizations
   nobody has measured on a pattern nobody has written yet. The re-open
   condition is a measured artifact where the decline is the bottleneck.
   Spelling, if it is ever built, should be a pattern-text declaration rather
   than an `rx_var` flag (`variables_common.md` §7 Q1's reasoning).

2. **~~Does `rx_info` carry a variable NAMES table?~~ PROMOTED INTO THE MVP**
   (was an open question here; `variables_roadmap.md` M7 now ships it, per
   `[VAR]`'s D6 panel, TEST-F1). §4.3 proposes index macros, which is what a
   *compiled* caller needs; a *reflective* caller (V-A's `pcre2_pattern_info`
   analogue, a debugger, and — the concrete customer — the `.rxt` test
   harness's driver, which has no OTHER way to resolve a `.rxt` case's named
   variable binding to a compiled artifact's `RX_VAR_<NAME>` index, since
   `driver.c` is one static file never templated per pattern) needs names.
   `rx_info.groups` is the precedent and it costs `.rodata` only. This note's
   own words for what deferring it would cost are the reason it is not
   deferred: "adding it later is a second `abi` event for a `.rodata`-only
   table." It ships on the `rx_info.groups` model, in the same `abi` event as
   the rest of §4.3.

3. **May a variable appear inside a quantifier or an alternation?**
   `${v}{2,4}` and `(${a}|${b})` are both expressible and both sound on the VM
   (the span compare is an ordinary consuming instruction). *Recommend: yes,
   no restriction* — but it is worth a named test axis, because a variable
   under a quantifier is the shape whose work charge matters most, and §1.2's
   `(a*)\1` precedent says the metering is already there.

4. **The same name in two places.** `${v}-${v}` is two references to one
   value, which is well-defined (both compare the same span). It is also
   *nearly* a backreference and a reader may expect it to mean "whatever the
   first one matched." It does not — it means "the value, twice." *Recommend:
   permit it, and say so in the guide*; a diagnostic would be noise.

5. **Does an empty value match at all?** With `minw = 0`, `${v}` bound to an
   empty span matches the empty string, so `^${v}$` matches only the empty
   subject. That is correct and also surprising. It interacts with §5's
   refusal rule: EMPTY is not UNSET, so a bare `${name}` with an empty-but-set
   value does *not* refuse. *Recommend as stated* — the distinction is
   `variables_common.md` §2.2's and it is bash's; `${name:?}` is how a caller
   asks for both to be refused.

6. **Interaction with `\G` and the find-all loop.** A caller driving
   `docs/spec/match_api.md` §3.1's loop passes `vars` on every iteration.
   Nothing requires the values to be *the same* on each. *Recommend: permit,
   document as the caller's business, and do not attempt to detect it* — the
   matcher holds no state between calls by §5.3, so there is nothing that
   could notice, and a caller varying the value per position is doing
   something deliberate.
