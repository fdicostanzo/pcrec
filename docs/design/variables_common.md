# The common variable design — one expansion grammar, two consumers

**Status: PROPOSED.** Design only; nothing under `src/`, `cli/`, `lib/` or
`tests/` was touched. This note is the shared half of a three-note set
chartered by Frank on 2026-09-23 (the charter is quoted verbatim at the top
of `variables_roadmap.md`). Its two consumers have their own notes:
`variables_pattern.md` (a variable inside a *pattern*) and
`replace_design.md` (a variable inside a *replacement template*). Read this
one first: both others depend on §2's value model and §3's call interface,
and neither restates them.

Frank's instruction is that the two consumers share a syntax. §1 surveys the
shell's expansion vocabulary to find out how much of it can be shared; §0
records the three findings that decided where the seam actually falls.

## How claims in this note are marked

House style, as `subst_template_design.md` and `utf8_design.md` use it.

| mark | meaning |
|---|---|
| **[RATIFIED]** | restates a ruled decision or plan row. Not open. |
| **[MEASURED]** | a fact established by running something on this box, with the command or cell cited. Not read from documentation. |
| **[PROPOSED]** | this note's design. Awaiting review and Frank's ruling. |
| **[OPEN]** | a question this note deliberately does not answer. Collected in §7. |

---

## 0. Three findings, before any design

These three reshape the charter enough that a reader who skips them will
mis-read every section below.

### 0.1 The replacement side's `${name}` is already taken, and it is ruled

**[RATIFIED]** `docs/design/subst_template_design.md` §3.1, ruled wholesale by
**D38** (2026-08-14, all fourteen of its §9 questions): in a *replacement
template*, `$0`/`${0}` is the whole match, `$n`/`${n}` is capture group *n*,
`${name}` is the *named capture group*, and `$$` is a literal `$`. D38 Q2
additionally ruled the brace-less `$name` form supported, greedy, PCRE2-exact.

So on the replacement side the brace namespace is fully occupied by the
match's own groups. A caller-supplied variable cannot spell itself `${name}`
there without either colliding with a ruled production or silently changing
what a valid PCRE2 template means — the one outcome D26 tier 1 cannot
survive.

**The consequence for the charter:** a design in which the two consumers'
syntax is *character-for-character* identical in every form is not available.
What *is* available, and what this note builds, is one grammar, one parser and
one evaluator, differing in exactly one place: which namespace a bare selector
resolves in. §1.3 makes that precise and §1.4 gives the one spelling that
means the same thing in both.

### 0.2 In a *pattern*, `${...}` is a spelling PCRE2 accepts and that can never match

**[MEASURED]** on this box, 2026-09-23, against the shipped compiler at
`build/pcrec` and against python `re` as an independent oracle:

- `build/pcrec -p rx --pattern '${name}'` **compiles** (exit 0). So does
  `a${v}b` and `$name`. (`${1}` refuses — "quantifier does not follow a
  repeatable item" — because `{1}` is a well-formed quantifier with nothing to
  quantify. The digit forms are therefore *already* unavailable in a pattern,
  which is a second reason the pattern side never wants them.)
- The compiled `${name}` artifact answers `nomatch` on every subject tried
  (`{name}`, `x{name}`, `name`), and so does `a${v}b` on `a{v}b` and `ab`.
- python `re` agrees on all six of `${name}`, `(?m)${name}`, `${name}?`,
  `a${v}b`, `${name}$`, `(?s)${name}` over eight subjects: **no match, in
  every cell**.
- Exhaustively, for `${n}` over every subject of length 0..7 drawn from the
  alphabet `{}name\nax` (which contains every byte the pattern or a newline
  could need): **zero matches**.

The mechanism is structural, not a sample: `$` asserts a position whose next
byte is a newline or which has no next byte at all, in every mode — checked
explicitly under three named variations rather than left to "every mode" to
imply coverage: the active newline convention (CR/LF/CRLF/ANYCRLF/ANY, a
fixed small set of control bytes, none of them `0x7B` `{`), `(?m)` (which only
widens *which* newlines count, never what counts as one), and
`PCRE2_DOLLAR_ENDONLY` (which only narrows where `$` can match). No PCRE2
option ever widens "newline" to include `{`. `{` is not a newline under any of
the three. So a `$` immediately followed by a literal `{` is an assertion
followed by a byte that assertion has just forbidden.

**[MEASURED]** the corpus population of the colliding spelling is **zero of
3,954 shipped `pattern` lines** (`find tests -name "*.rxt" | xargs grep -cE
'^pattern ' | awk -F: '{s+=$2} END{print s}'`, 2026-09-23, independently
re-run and reproduced). The structural unsatisfiability proof above is the
primary evidence; this corpus count is corroboration, reproducible by the
command cited, not the argument itself.

**Why this matters more than the zero.** `docs/design/reqbyte_freq_pick.md`'s
own lesson — restated in `c2design_report.md` — is that *a population of zero
is the state in which a hazard ships unobserved*, so a zero count is normally
a reason for suspicion rather than comfort. Here it is not the evidence: the
unsatisfiability proof is, and the zero merely confirms it. A spelling that no
subject can match is a spelling whose reinterpretation breaks no working
pattern. That is strictly stronger than the module-gating the collision rule
would otherwise demand (§4.1), and it is very nearly the *stronger* property
D38 Q5 adopted for the template side ("every pcrec-only template form must be
a spelling PCRE2 rejects").

### 0.3 The runtime string compare already exists, and it is not a literal

**[MEASURED]** by reading `src/gen/emit_vm.c`. A compile-time literal's
INSTRUCTION shape in the VM is **not** a `memcmp` — literals are normalized to
singleton `A_CLASS` nodes (`src/core/internal.h:328`) and emitted as a chain
of per-byte `if` tests (`emit_vm.c:8298-8319`), one `goto` per byte. (The
claim is narrowly about the emitted per-position instruction stream, not about
`memcmp`'s absence from the emitters generally — `src/gen/emit_dfa.c`'s
`emit_req_run_check`, landed at `[OPT-REQPOS]` tier 2b after this note's own
survey, emits a constant-length `memcmp` against a compile-time literal as a
whole-window pre-check, `variables_pattern.md` §1.1 has the detail; the
argument here does not depend on its absence.) The single `memcmp` in
`emit_vm.c` (`:1566`) is class-bitmap pool deduplication.

What *does* compare against a runtime pointer and length is the
**backreference**, `vm_bref` (`emit_vm.c:8103-8245`): it reads a `(start,
end)` pair out of the VM's own `slot_values[]` at match time and calls
`<prefix>_bref_match[_caseless]` through the encoding seam, which returns a
**length** rather than a boolean — deliberately, because under a
length-changing caseless fold the bytes consumed need not equal the bytes
compared (`src/enc/enc_byte.c:118-127`).

This is the mechanism a pattern variable wants, one span-source over.
`variables_pattern.md` §1 is the whole argument; it is flagged here because it
decides §5's architecture question: the *insertion* is not a preprocessing
layer at all.

---

## 1. The survey — shell expansion, form by form

Bash and zsh between them define about twenty expansion forms. The question
for each is not "is it nice" but three narrower ones: does it apply here at
all; in which consumer; and what does it mean when the value comes from a
**match** (a capture group) versus from the **caller** (an environment of
name → bytes).

### 1.1 The table

Consumers are **P** (a variable inside a pattern) and **R** (a variable
inside a replacement template). "value from match" is the column that matters
for R, where a selector may name a capture group; in P there is no match yet
when a variable is expanded, so that column is structurally empty and the
table says so rather than leaving it blank.

| form | bash meaning | applies? | P | R | from a MATCH | from the CALLER |
|---|---|---|---|---|---|---|
| `$name` | expansion, bare | yes | no (§1.5) | **ruled core** (D38 Q2) | the named group, greedy | n/a in R; not offered in P |
| `${name}` | expansion, braced | yes | **the variable** | **the named group** (D38) | the group's span | the caller's bytes |
| `${!name}` | indirect expansion | **re-purposed** | the variable | the variable | — | the caller's bytes, in both consumers (§1.4) |
| `${name:-word}` | default if unset **or empty** | yes | yes | yes (`subst-extended`) | group unset or empty → `word` | var unset or empty → `word` |
| `${name-word}` | default if **unset only** | yes | yes | yes | group did not participate → `word` | `p == NULL` → `word` |
| `${name:+word}` | alternate if set **and non-empty** | yes | yes | yes (`subst-extended`) | group participated non-empty | var set non-empty |
| `${name+word}` | alternate if **set** | yes | yes | yes | group participated | `p != NULL` |
| `${name:?word}` | error if unset/empty | yes | **yes, and it is the P default** (§2.4) | yes | — | refuse the call, naming the variable |
| `${name:=word}` | **assign** default | **no** | — | — | — | §1.2 |
| `${name#pat}` / `##` | strip shortest/longest prefix | yes | phase | phase | strip from the group's text | strip from the value |
| `${name%pat}` / `%%` | strip shortest/longest suffix | yes | phase | phase | same | same |
| `${name/pat/repl}` / `//` | substitute within the value | **no** | — | — | — | §1.2 |
| `${name^}` / `^^` / `,` / `,,` | case transform (bash) | yes | phase | phase | transform the group's text | transform the value |
| `${(U)name}` / `${(L)name}` (zsh) | case transform (zsh flags) | **no** | — | — | — | §1.2 |
| `${name:u}` / `:l` (zsh) | case transform (zsh modifiers) | **no** | — | — | — | §1.2 |
| `\U` `\L` `\E` `\u` `\l` | case forcing (PCRE2/perl) | yes | **no** | **ruled** `subst-extended` | on the OUTPUT stream | same |
| `${name:off:len}` | substring | yes | phase | phase | a sub-span of the group | a sub-span of the value |
| `${#name}` | length in characters | yes | **no** (§1.6) | phase | the group's length | the value's length |
| `${name@Q}` etc. | bash transform operators | **no** | — | — | — | §1.2 |
| `${name[i]}`, `${name[@]}` | arrays | **no** | — | — | — | §1.2 |
| nested `${a:-${b}}` | nested expansion | yes | phase | phase | — | one recursion bound (§1.7) |

### 1.2 What is declined, and why each is declined for its own reason

These are not one rejection wearing five hats. Each has a different cause,
and recording the cause is what lets a later reader re-open exactly one.

- **`${name:=word}` (assign).** Assignment mutates the environment. pcrec's
  environment is a caller-owned array the matcher reads and never writes
  (§3); writing to it would give a generated matcher mutable state, which
  `docs/spec/match_api.md` §5.3 forbids as a **binding contract on future
  emitters** ("A generated matcher holds no mutable state of its own"), not
  as an observation. The operator is not merely unneeded — it is unavailable.
  `${name:-word}` covers every non-mutating use.
- **`${name/pat/repl}` (substitute within a value).** This is a *regex
  substitution inside a variable expansion*, i.e. the whole of
  `replace_design.md` reached recursively, with a pattern that is not known
  until run time. pcrec is an ahead-of-time compiler; a run-time pattern
  would require running the compiler at match time, which is the one thing
  the architecture is built to avoid (`APPROACH.md` §1). Declined
  architecturally, not on effort.
- **zsh's `${(U)name}` / `${name:u}`.** These are *alternate spellings* of
  `${name^^}`, which the table already takes. Adopting both would be a
  parallel mechanism for one fact — memory `pcrec-general-mechanisms-not-
  special-cases`, and the reason D118 retired `--source` when the operand
  already meant it. One spelling per operation; bash's is the one with the
  wider audience.
- **`${name@Q}` and the transform family.** Every member is either shell-
  specific (`@Q` quotes *for the shell*, which has no meaning here) or a
  rename of something already in the table. Nothing in the family survives
  translation to bytes.
- **Arrays `${name[i]}` / `${name[@]}`.** An array is a second value model.
  §2's model is one name → one byte span, which is exactly what both
  consumers can use. A caller with a list flattens it themselves, or passes
  *n* names. Re-open condition, stated so it is checkable: a measured case
  where the flattening has to happen inside the matcher because the
  separator depends on the match. Nothing in the corpus or the bench has one.
- **`${#name}` in a *pattern*.** It renders a *number* — decimal text — and
  inserting decimal text into a pattern is inserting a literal whose bytes
  are a length, which is never what a pattern author means. It is genuinely
  useful in a *replacement*, where it is output, and the table keeps it
  there.

### 1.3 The one place the two consumers differ, stated exactly

Everything above is one grammar. The production is:

```
    ${ [scope] selector [operator word] }
```

One parser, one evaluator, both consumers. The single difference is the
default `scope` when none is written:

- **In a replacement, a bare selector resolves in the GROUP scope.** This is
  D38's ruling and it is PCRE2 fidelity; it is not this note's to change.
- **In a pattern, a bare selector resolves in the VAR scope.** Not by
  preference but by construction: a pattern variable is expanded *before* the
  match runs, so there is no match, no capture, and nothing for a group
  selector to name. A group scope in a pattern has no referent at the moment
  of expansion.

So the rule is not an arbitrary per-consumer convention. It is "resolve in
the only scope that exists here," and in the replacement both exist, which is
why the replacement is the one that needs the explicit form.

### 1.4 `${!name}` — the spelling that means the same thing in both

**[RATIFIED]** D38 Q5 ruled `${!...}` reserved as pcrec's template-extension
prefix, on the §7.1 rule that every pcrec-only template form must be a
spelling PCRE2 rejects — **[MEASURED]** there against libpcre2 10.46 in both
dialects (`-35` in each). That measurement was run against the
*replacement/substitution-template* dialect (`subst_template_design.md`), a
different grammar from a PCRE2 *pattern*; §1.4 spends the reservation in
BOTH consumers, so the pattern side owes its own derivation rather than
borrowing the template side's, which is worked out here explicitly: `{!name}`
is not quantifier-shaped (its body is not digits), so `$` followed by
`{!name}}`-as-literal-text is exactly §0.2's `${name}` unsatisfiability
argument again — `$` asserts a next byte that is a newline, and `{` is not
one. The template-side measurement and the pattern-side structural argument
are two different safety properties for two different grammars; both hold,
independently.

**[PROPOSED]** that reservation is spent here, once, on the thing it is most
useful for: **`${!name}` is the caller's environment, explicitly, in both
consumers.** A user who wants one spelling that means one thing everywhere
writes `${!name}` and it reads identically in a pattern and in a replacement.
`${name}` stays the short form whose scope is the consumer's default.

This is a re-purposing of bash's *indirect expansion* and the note should say
so plainly rather than pretend the borrowing is exact: in bash `${!name}`
means "the variable whose *name* is the value of `name`". That form is
declined here for the same reason `${name/pat/repl}` is — it resolves a name
at run time, where pcrec resolves every name at compile time (§3.2). The
sigil is free because the meaning it carries in bash is one pcrec cannot
have, and it is already reserved on this side of the fence.

### 1.5 Why the bare `$name` form is offered in R and not in P

In a template, D38 Q2 ruled it in, on the argument that pcrec's compile-time
check defuses the greedy-name footgun that makes it dangerous in PCRE2. That
argument holds and this note does not re-open it.

In a pattern it does not hold, because `$` is a live assertion there. `$name`
is a currently-valid pattern with a currently-valid meaning — end-of-line,
then the literal `name` — and **[MEASURED]** it compiles today. Unlike
`${name}` (§0.2) it is satisfiable: it matches `name` at the end of a line
under `(?m)`. So the bare form in a pattern collides with a *working* pattern
and would have to be module-gated on the weaker rule, for a convenience the
braced form already provides. **[PROPOSED]** decline it in P; the brace is
mandatory there.

That asymmetry is worth one sentence in the guide, and it is not arbitrary:
in a template `$` is an ordinary byte, and in a pattern it is an operator.

### 1.6 Operators whose result is a number

`${#name}` is the only one. It renders decimal ASCII. §1.2 declines it in P
and keeps it in R as a phase item. Nothing else in the table changes a value's
*type*; every other operator is bytes → bytes, which is what keeps the
evaluator a single function over one value model.

### 1.7 Nesting

`${a:-${b}}` is the useful case and the only one with a real customer (a
fallback chain). **[PROPOSED]** nesting is permitted in the `word` position
only, with a **compile-time** depth bound — the expansion grammar is parsed
when the artifact is built, so an over-deep template is a compile error, not
a run-time recursion. The bound is a `src/core/limits.def` row like every
other bound in the tree, which makes it visible to `--list-limits` and
raisable by the documented mechanism. No run-time recursion is introduced in
either consumer. **A new `limits.def` row is caller-observable, so it carries
its own `docs/spec/limits.md` hunk in the same change (D80/D90) —
`docs/spec/limits.md` is D90's own spec, "the ONE TABLE that `--list-limits`
dumps and the spec derives from," and this is the one D80 obligation this
round of notes must not miss.**

---

## 2. The value model

### 2.1 A value is BYTES, under the artifact's encoding

**[RATIFIED]** `APPROACH.md` §4 and D58: encoding is a per-compile-call
scalar, and a backend supplies residual *text* an artifact embeds — "no
encoding conditional anywhere in the compiler, the emitter or the artifact"
(DD-12 (7)). The lowering pass `pcrec_lower_enc` runs once, after parse, and
splices in place.

**[PROPOSED]** a variable's value is a byte span, interpreted under the
artifact's own encoding, and the artifact's encoding is fixed at compile
time. Under `byte` every span is valid by definition. Under `utf8` a value
that is not well-formed UTF-8 is a **refused call**, not a silent
mis-match — the same class as `PCREC_ERR_STARTPOS`, which
`docs/spec/match_api.md` §4 already defines as "refused, nothing attempted,
`caps` untouched" for a start position that is not a character boundary. A
variable is the second producer of that class and needs no new vocabulary,
only a new code.

Validation cost is paid once per call per variable, over the value's own
length, and only under `utf8`. **[OPEN]** whether it is paid unconditionally
or only for variables whose use site can be reached is §7 Q3; the safe answer
is unconditional and it is what the MVP takes.

### 2.2 UNSET vs EMPTY — two states, and the tree already spells both

The charter asks whether there are three states or two. There are **two**,
and pcrec has been distinguishing them since the match API froze.

**[RATIFIED]** `docs/spec/match_api.md` §5: `PCREC_UNSET ((ptrdiff_t)-1)`
written into *both* slots means a capture group that never participated;
`caps[k][0] == caps[k][1] >= 0` means a group that participated and matched
the empty string. R22's two measured rules (three-way unanimous across python
`re`, libpcre2 and pcrec) turn on exactly this distinction.

So the model is:

| state | from a MATCH | from the CALLER | `:` operators | bare operators |
|---|---|---|---|---|
| **UNSET** | `caps[k] == {-1,-1}` | `rx_var.p == NULL` | fire | fire |
| **EMPTY** | `caps[k][0] == caps[k][1] >= 0` | `p != NULL, len == 0` | fire | do not fire |
| **SET** | a non-empty span | `p != NULL, len > 0` | do not fire | do not fire |

That is bash's rule unchanged: the `:` in `:-`, `:+`, `:?` is what folds EMPTY
in with UNSET. pcrec gets it for free because its two states are already the
two shell has, under different names. There is no third state to invent, and
"NULL" in the charter's phrasing is UNSET — the C spelling `p == NULL` and
the capture spelling `{-1,-1}` are one state seen from two sides.

### 2.3 Where pcrec agrees with `pcre2_substitute`, and where it departs

D26 makes PCRE2 the semantic reference where it has one. It has one here, and
the honest accounting is that pcrec agrees on semantics and departs on *when
the answer is computed*.

| PCRE2 | pcrec | tier | verdict |
|---|---|---|---|
| `${n:-word}`, `${n:+word}` under `SUBSTITUTE_EXTENDED` | same spellings, same semantics, gated on module `subst-extended` | 1 | **agrees**; the option becomes a D18 compile-time tier, ruled at D38 §3.0 |
| `\U` `\L` `\E` `\u` `\l` | same, and **[MEASURED]** at `subst_template_design.md` §3.3 as a pending operator on the *output byte stream*, not on the next template item | 1 | **agrees**, including the three corners a naive design gets wrong |
| `SUBSTITUTE_UNSET_EMPTY` (a run-time bit) | a **generation axis**, default empty | 3 | **departs in shape, agrees in reachable behaviour** — D38 Q3, already ruled |
| `SUBSTITUTE_UNKNOWN_UNSET` (an unknown group name is treated as unset) | **no analogue**: an unknown name is a *compile-time* error | 3 | **departs deliberately.** `subst_template_design.md` §4 resolves every reference at build time against the pattern's own group count; there is no run time at which a name can be unknown. This is the AOT win the `[M4-SUBST]` row names, and D26 does not protect error *timing* |
| `SUBSTITUTE_LITERAL` (a run-time bit) | not an option: a template with no `$` is the degenerate template compiler | 3 | **departs in shape.** D18; ruled at §3.3 |
| the unset default is a run-time error (`-55`) | in a **pattern**, an unset variable is a refused call (`variables_pattern.md` §5); in a **replacement**, empty by the ruled axis | 3 | **the two consumers differ on purpose** — see §2.4 |

### 2.4 The deliberate asymmetry in the unset default

This is the one place the two consumers take different defaults from the same
model, and it is worth stating why rather than leaving a reader to find it.

- In a **replacement**, an unset group rendering as empty produces *wrong
  output*. The failure is visible, local, and recoverable: the caller sees the
  bytes.
- In a **pattern**, an unset variable rendering as empty produces a *wider
  language*. `^${prefix}-[0-9]+$` with `prefix` unset silently becomes
  `^-[0-9]+$` and matches inputs the caller never authorized. The failure is
  invisible and it sits on a security boundary — the same shape as the
  injection hazard §4.2 exists to close.

Different blast radius, different default. So: **empty in a replacement (the
ruled axis), refused in a pattern**, with `${name:-word}` as the caller's
explicit opt-in to permissiveness on either side. The general principle is
that the silent-and-widening failure gets the loud default.

---

## 3. The call interface — how a caller supplies variables

### 3.1 The type

**[RATIFIED — Frank 2026-09-23]**, one fixed-literal ABI type, never
`--prefix`-scoped, joining the family of fixed-literal ABI types: `rx_ctx`,
`rx_matchfn`, `rx_callout_ref` (fixed at D41 ruling 1, cited as D41.1) and
`rx_info`, `rx_group_entry` (fixed later, at D43 and D44 respectively — see
`match_api_m4.md`'s own changelog):

```c
typedef struct {
    const char          *name; /* NUL-terminated; the pattern's own spelling
                                   of the name */
    const unsigned char *p;    /* NULL == UNSET; see §2.2 */
    size_t               len;  /* bytes; 0 with p != NULL == EMPTY */
} rx_var;
```

Three members, no flags word. **This is Frank's 2026-09-23 ruling, and it
overturns §3.2's own original premise** ("the array, and there is nothing to
resolve"): variables are passed BY NAME. The compile-time index macros this
note originally proposed as the caller's ABI (`RX_VAR_PREFIX` and its
siblings) cannot serve that role, because indices cannot be aligned across
SEPARATELY COMPILED artifacts — a caller filling `vars[RX_VAR_PREFIX]` for
one artifact has no way to know that the same index means the same name in
a second, independently compiled artifact composed alongside it (§3.3's own
composition case; an artifact invoked as a callout exists precisely for
composing pieces the outer artifact was compiled with no knowledge of, or
for a bind-time choice of the inner artifact — in every such case the inner
artifact's layout is unknown to the outer at compile time). A name is the
only key both sides can agree on without coordinating a shared compile-time
fact; an enum is an index in disguise. §3.2 below carries the ruling's
argument in full and rewrites the array-vs-resolver answer accordingly; the
index macros SURVIVE, but only as the artifact's own INTERNAL indices into
its resolved table (§4.3's stamps in `variables_pattern.md`), never as
something a caller writes.

The charter asks about a `flags` field; **[OPEN]**
§7 Q1 records what one would be for, and the MVP does not have it, because
every candidate use (declare-non-empty, declare-a-pattern, declare-prefolded)
is a *compile-time* property of the use site, not a per-call property of the
value — and a compile-time property belongs in the pattern text where the
reader can see it, not in a caller's array where they cannot.

### 3.2 Array or resolver? The array, resolved BY NAME, once per call

**[RATIFIED — Frank 2026-09-23]**, overturning this section's own original
premise. The charter asks the question as array-versus-callback and notes
the array is a resolver; the first draft answered "the array, and there is
nothing to resolve," on the argument that the emitter assigns every
mentioned name a compile-time index and the caller writes
`vars[RX_VAR_PREFIX]` with no string comparison anywhere at match time.
**That argument is false, and the reason is a coordination problem, not a
performance one: the artifact knows its own names, but not the caller's
layout.** An index is meaningful only inside the artifact that assigned it.
Two separately compiled artifacts — the ordinary case, since composition
exists precisely for pieces compiled with no knowledge of each other's
layout (§4.2's re-homing argument for a pattern-valued variable makes the
same point from the opposite direction) — cannot agree that index 0 names
the same variable, and a caller juggling two different artifacts' index
tables by hand would be re-deriving the compiler's own bookkeeping outside
the compiler.

So the design is **the array, resolved BY NAME** — still an array, not a
callback, and the charter's array-versus-resolver framing was never really
about names versus indices. A caller still fills a flat `rx_var[]` with no
indirect call anywhere:

```c
rx_var vars[] = {
    { "prefix", buf,  n  },
    { "suffix", buf2, n2 },
};
```

What changes from the withdrawn draft is what each entry carries and when
the artifact reads it:

- **Compile time, unchanged.** The emitter still knows every name the
  pattern or template mentions (typically 1-3) and still emits a small
  static table of them (`#define RX_NVARS 2` and the like) — this part of
  the original argument survives.
- **Once per entry call, before the match loop — new.** The artifact scans
  the caller-supplied array for each of ITS OWN mentioned names — length
  check then `memcmp`, FIRST MATCH WINS on a duplicate name in the caller's
  array (§3.4) — resolving each into a small stack array of `(p, len)`
  pairs. The match loop itself is unchanged: it still reads a
  compile-time-indexed local (`RX_VAR_PREFIX` now names that internal
  slot, not anything the caller writes). Only the boundary between "the
  caller's array" and "the artifact's own index" moved — from a
  compile-time-shared index (unsound across separately compiled artifacts)
  to a run-time name resolution the artifact performs once on entry and
  never again per position.
- **The hot path is unaffected.** §1's span compare already reads from a
  small resolved local, not from the caller's array directly — the
  resolution above happens once, upstream of the scan the mechanism
  performs at every position it is reached. D23's measured **26%**
  run-time-fold-indirection cost is a PER-POSITION indirection; this is a
  PER-CALL one over a handful of short names, and the precedent that
  justified declining a resolver callback in the withdrawn draft does not
  transfer to this cost the way that draft implied.

**[RATIFIED — Frank 2026-09-23]** LINEAR SCAN ONLY. A sorted search or a
hash table waits on a measured need (D77): the set size is 1-3 names in
every case this design has looked at, and a length-check-then-`memcmp` scan
of a few short strings is not a mechanism to optimize ahead of a
measurement.

A resolver CALLBACK — the charter's other named alternative — stays
declined, and for the sharper reason above rather than the withdrawn
draft's "the compiler already answered this": a callback would put an
INDIRECT CALL on the same per-call boundary the by-name array already
resolves inline with a few comparisons, buying nothing a caller could not
get by filling the array themselves. **[PROPOSED]** the resolver form
stays declined with the same named re-open condition as before: a measured
case where the *set* of names is not known until run time. Such a case is
not expressible in this design at all (a name the compiler never saw has no
compile-time table entry to resolve against), so re-opening it re-opens
§4.2's literal-only rule too. They are one question.

### 3.3 Where the array is passed

**[RATIFIED — Frank 2026-09-23]**, overturning this section's own original
answer. `variables_pattern.md` §4 and `replace_design.md` §3 settle this per
consumer; the shared rule stated once here changed with the ruling.

**The array rides `rx_ctx`: TWO FIELDS APPENDED AT THE END —
`const rx_var *vars; size_t nvars;`. `rx_matchfn` is UNTOUCHED, and a
composed call passes the ctx through unchanged.** This is what resolves
MECH-B2, the D6 panel's blocker (`docs/dev/reviews/2026-09-23-r1-var-design.md`,
boxed at the top of `variables_pattern.md` §4): `<prefix>_match` **is**
`rx_matchfn`, a fixed-literal ABI type shared by every artifact, and the
withdrawn draft's `const rx_var *vars` entry PARAMETER would have made a
var-bearing artifact's `<prefix>_match` no longer an `rx_matchfn` — the
identical harm D38 rejected for a per-call `user` parameter, narrowed to
var-bearing artifacts rather than every one. Appending to `rx_ctx` instead
means `rx_matchfn`'s signature — and every already-compiled caller of it —
is untouched by construction, and a matcher composed as a callout or a
submatcher receives the outer's `vars`/`nvars` simply because it already
receives the outer's `ctx`.

**This does not reopen the objection the withdrawn entry-parameter draft
raised against riding `rx_ctx` (retained below as reasons 1-3).** Those
reasons argue against a BOUND STATE — a handle set once and read implicitly
on every later call — which is a real hazard `rx_ctx.user`'s per-*binding*
semantics also has to respect. A `vars`/`nvars` pair appended to `rx_ctx` is
not that: it is an ordinary per-*call* field, filled fresh on every call
exactly as `ctx->caps`/`ctx->subject` already are, so it is not reached by
the argument that refused a bound handle or by D38's refusal of a second,
inconsistent way for per-call data to reach the engine alongside `user`'s
per-binding one.

**Top-level entries (the `<prefix>_search` family) of a var-bearing
artifact take the same pair by the caller-buffer-siblings precedent** —
`docs/spec/match_api.md`'s own `<prefix>_search_in` = the un-suffixed twin
plus a final caller-buffer descriptor is the existing precedent for a
per-artifact entry gaining a trailing parameter present exactly when
meaningful (D18). **[PROPOSED]** the manager's default: the var-bearing
artifact's un-suffixed entries gain a trailing
`const rx_var *vars, size_t nvars` pair (present exactly when meaningful).
**The exact spelling is [PROPOSED], not ruled** — an `_in`-style descriptor
folding the pair in instead of a bare trailing pair is a live alternative,
named here in one line rather than chosen.

**The three reasons below explain why a BOUND state is refused; they are
unchanged by the ruling** (riding `rx_ctx` as an ordinary per-call field is
not a bound state):

1. **A bound state would be mutable state.** `docs/spec/match_api.md` §5.3 is
   a binding contract, not an observation: a generated matcher holds none.
   §10.5 already refused the analogous convenience for frame buffers — "no way
   to set a buffer once per artifact or per thread" — because it would be
   either mutable state or thread-local, and thread-local fails reentrancy.
   A `rx_bind(vars)` returning a handle walks into the identical wall.
2. **No combinatorial growth.** A pattern with no variables cannot be handed
   any, and a pattern with variables cannot be matched without them, so the
   parameter is present exactly when it is meaningful. This is D18's rule
   applied unchanged — a fixed choice is compiled away, never a run-time
   dispatch — and it is how `<PREFIX>_NCAPS` already varies per artifact.
3. **Thread safety falls out** and needs no new sentence: each call has its
   own array, the artifact holds nothing, and §5.3's existing rule ("provided
   each call has its own buffer") extends by one noun.

It is caller-observable, so it is an `abi` event with a `docs/spec/` hunk in
the same change (D80), a stamp (`<PREFIX>_NVARS` on the artifact's own
internal-index table, and `rx_info.nvars` appended at the end of the struct
per §6's rule), and the D94 grep ritual over every reader of the number —
now widened, since this lands as a struct-layout event on `rx_ctx` itself
rather than a per-artifact signature change, so every site that reads
`rx_ctx`'s layout is in scope.

### 3.4 What a missing variable does

Two different times, two different answers, and conflating them is the trap:

- **Compile time.** A name is *mentioned* by the pattern or template. The
  emitter knows every mentioned name, so a name is never "missing" at compile
  time — it is *declared* by being mentioned. There is no compile-time missing
  case to define. What *is* a compile-time error is the reverse: a
  replacement's `${name}` naming a capture group the pattern does not have
  (`subst_template_design.md` §4, already ruled).
- **Run time.** A slot the caller left UNSET. §2.4 gives the per-consumer
  default; §2.2 gives the operator that overrides it.

**[PROPOSED]** one compile-time diagnostic that exists only because pcrec is
AOT, and that closes §1.3's one real footgun: if a *replacement*'s `${name}`
names no capture group, and the artifact's variable set does contain `name`,
say so —

```
    pcrec: ${name} names capture group 'name', which this pattern does not
    have; the caller variable of that name is spelled ${!name}
```

PCRE2 cannot produce this message because it has no compile-time template.
The generic "unknown group" refusal stands when the variable set does not
contain the name either; this is the *pointed* arm of it, and D26 tier 3
leaves the wording ours.

### 3.5 The `.rxt` binding directive — one line, shared by both consumers

**[PROPOSED]**, added here rather than in either consumer's own note because
the underlying array is shared (§3.2-§3.3) and a test author reading either
consumer's note needs one pointer, not two independent proposals that could
drift: a `.rxt` case binds a variable with

```
    var <name> "<value>"        block-scoped, repeatable; sets a variable
    var-unset <name>            block-scoped; declares the slot UNSET
```

**One line per variable per case, and the same line serves BOTH consumers**:
a case with a bare `m`/`ms`/`n`/`ns` block (pattern matching, no `repl`) and a
case with a `repl` block (replacement) read `var`/`var-unset` identically —
there is no substitution-only reading of this directive. Both UNSET and
EMPTY are spellable and distinguishable: `var-unset name` is UNSET
(`p == NULL`, §2.2); `var name ""` is EMPTY (`p != NULL, len == 0`) — a
format that could not tell the two apart could not test the operator
(`:-` vs `-`) that exists to distinguish them. A value's bytes are read
under the artifact's own encoding and reuse the existing quoted-subject
escape set (`docs/spec/rxt_format.md`'s five-escape TSV-framing subset) —
no second escape vocabulary.

**[RATIFIED — Frank 2026-09-23]** Name resolution is by NAME, and it now
happens INSIDE THE ARTIFACT, not in the driver — the ruling in §3.1-§3.2
above simplifies this directive's implementation rather than complicating
it. The driver builds an `rx_var[]` array directly from a case's
`var name "value"` / `var-unset name` lines — one entry per line, `name`
copied verbatim into the entry's `rx_var.name` field — and passes it
through unconditionally (`rx_ctx.vars`/`rx_ctx.nvars`, §3.3). It performs NO
lookup of its own against any compiled index: `docs/spec/rxt_format.md`'s
`driver.c` is one static file, compiled fresh per test case but never
templated per pattern, so it never needed to (and, under the WITHDRAWN
index-based draft, could not have) referenced a compile-assigned macro name
it does not know at its own compile time. The artifact resolves its own
mentioned names against whatever the driver supplied, the same way it
resolves any other caller's array.

**`rx_info`'s variable-names table (§3.3's stamps, promoted into the MVP by
`[VAR]`'s D6 panel) now does DOUBLE DUTY as a validation aid rather than a
load-bearing lookup route.** A driver — or any caller — MAY consult it to
catch a typo in a `.rxt` case's `var name` line before the call (the
`rx_info.groups` precedent for capture-group names), but nothing in the
match path depends on that check running: the artifact's own entry-time
resolution (§3.2) is authoritative regardless. This is a SMALLER obligation
on `driver.c` than the withdrawn index-based design placed on it — no
per-case NAME→INDEX resolution machinery is needed there at all.

**The SPELLING above is the manager's call, not this note's** (memory
`pcrec-dd13b-syntax-is-managers`): the two production names, the block-scoped
repeatable shape, and where this directive sits relative to `repl`/`s`/`sg`/
`serr` are all open to the manager's ruling at `[DD-13b]`'s own pace. What is
fixed here is the SEMANTICS above, which do not depend on the spelling.

### 3.6 The pattern-side oracle — what verifies a compiled `${name}` artifact's match answers

> **[RATIFIED — Frank, 2026-09-23 ~13:2x] The splice is WRAPPED: `(?:` +
> quotemeta(value) + `)`, never the bare escaped bytes.** A variable
> reference is ONE node (`A_VAR`, `A_BREF`'s twin), so a quantifier,
> alternation or lookaround written against `${name}` applies to the WHOLE
> value: `${x}+` with `x = "ab"` means `(?:ab)+`, and a bare splice would
> read `ab+`, quantifying only the last byte and making the oracle disagree
> with the artifact on a correct artifact. The same wrap makes `${x}{2}`,
> `a|${x}`, `(?=${x})` and `${x}?` splice correctly; EMPTY splices to
> `(?:)`, which PCRE2 accepts. `(?:…)` and `(?>…)` are equivalent here — a
> literal byte sequence matches in exactly one way at a position (the fold
> compare returns ONE consumed length), so there is nothing to backtrack
> into; the artifact's span compare is atomic by construction and the
> oracle's group need not be. The implementing lane's oracle helper wraps
> unconditionally; a test that relies on the bare splice is wrong.

**[PROPOSED]**, and it is the one piece of MVP measurability the design owed
and did not previously name: nothing in `variables_pattern.md` proposes an
oracle for the built feature's MATCH semantics, only for the `${...}`
spelling's compile-time unsatisfiability (§0.2, a proof about SYNTAX, not
about what a landed `A_VAR` recognizes). Two techniques, covering different
axes, neither a substitute for the other:

1. **QUOTEMETA-SPLICE, the primary technique.** Interpolate the variable's
   value, quotemeta-escaped, into the pattern text as a literal, and run
   libpcre2/python on the composed pattern. §4.2's own D87 citation
   (`docs/design/…`: "textual append silently breaks absolute backrefs and
   name collisions") does **not** foreclose this: D87's hazard is about
   splicing a CAPTURING sub-pattern's own text into a composed whole, which
   shifts group numbers — the `[LIB]`/definitions use case §4.2 re-homes AWAY
   from itself. A quotemeta'd VALUE carries no capturing groups; inserting it
   as plain literal text perturbs no numbering. This covers caseless folding
   and ordinary SET values, external to and independent of pcrec's own
   mechanism.
2. **BACKREF-EQUIVALENCE, a second-order WIRING check.** `A_VAR`'s emitted
   code and its caseless fold call are the same encoding-seam mechanism
   (`bref_match[_caseless]`-shaped, §1 of `variables_pattern.md`) the already
   oracle-verified backreference module uses. A same-compiler A==B
   differential — `${v}`-pattern vs. the semantically matched `(literal)\1`
   pattern on one subject — catches VAR-SPECIFIC wiring bugs (wrong index,
   UNSET mishandling, wrong caseless bit threaded through). **Labeled
   explicitly, per `docs/dev/learnings.md` §3's opening rule ("a control must
   not share a source with what it controls"): a bug in the shared fold code
   would pass BOTH sides of this differential**, since the var path and the
   backref path call the SAME per-encoding fold function — its real value is
   wiring correctness, not an independent check on the fold itself, which is
   covered transitively by CITING `tests/utf8/axis06_caseless_fold.rxt`'s and
   `axis07_caseless_1ton.rxt`'s existing KELVIN-SIGN pins as already
   discharging that population, not by re-deriving it.

**Neither technique reaches the UNSET/EMPTY population or the UTF-8-validity
refusal**: there is no PCRE2 spelling for "this literal is absent" to splice,
so those cells are oracle-less by construction and are tested as refusal-
table rows instead (`variables_pattern.md` §7's table). Stated per
`docs/dev/learnings.md` §3's rule to "name the set the claim is measured
over, and ask what is outside it." This oracle section is a delivery-bar
item for `variables_roadmap.md`'s MVP (M10).

---

## 4. Escaping, quoting, and the literal rule

### 4.1 Writing a literal `$`

Nothing new is needed in either consumer.

- **In a pattern**, `\$` is already an escaped literal `$` — today's PCRE2
  meaning, unchanged. And `${` only becomes a doorway when module `vars` is
  enabled, so with the module off today's parse stands in full. That is
  `design_callout_abi.md` §3's **collision rule** ("a spelling that
  reinterprets a currently-valid pattern must be module-gated") satisfied by
  the ordinary mechanism — and §0.2 shows the gate is protecting a population
  of patterns that could never match, which is why enabling the module by
  default later is a cheaper conversation than the rule normally makes it.
- **In a replacement**, `$$` is a literal `$` in the core tier and `\$` is one
  under `subst-extended` — both **[RATIFIED]** at D38, both measured against
  PCRE2. The `$$` spelling is the one that works in every tier.

### 4.2 A value is inserted LITERALLY. Always.

**[PROPOSED]**, and this is the load-bearing rule of the whole design:

> The bytes of a variable's value are matched as themselves. They are never
> parsed as pattern syntax, in any consumer, under any flag.

Three independent reasons, and the design is safe if any one of them holds:

1. **It is the injection boundary.** A caller who interpolates user input into
   `^${prefix}-[0-9]+$` must be able to rely on the user not being able to
   write `.*` and widen the language. Quotemeta-by-default is the only
   defensible default, and an opt-out would be a footgun with a flag on it.
2. **It is what makes the mechanism cheap.** §0.3's runtime compare is a
   span-versus-span byte comparison. A value that could be *pattern* would
   have to be compiled, at match time, which is not a feature this
   architecture can have (§1.2).
3. **A caller-supplied, match-time pattern is declined architecturally, for
   the identical reason §1.2 declines `${name/pat/repl}`.** D85's
   predicate-scanned definitions table, D87's AST-level composition, D89's
   numbering rules and the `[LIB]` row's user-facing form are every one of
   them a COMPILE-TIME mechanism: entered through `pcrec_compile()`/
   `--source`/`--lib-path`/the `.rxt` `lib`/`name` grammar, resolved by the
   pcrec compiler before or during one compile call. None of them has any
   path from an `rx_var.p` pointer supplied at MATCH time into anything the
   DFA/VM tables can use — that would mean running the compiler again after
   the artifact is already generated, the one thing AOT-ness forbids, and it
   is exactly the shape §1.2 already declines for `${name/pat/repl}`: "a
   run-time pattern would require running the compiler at match time, which
   is the one thing the architecture is built to avoid."

So the charter's "explicit opt-in for a value that IS a pattern" has two
readings, and they get different answers. Read as a pattern AUTHOR composing
a known library subpattern at COMPILE time, `[LIB]`/D85/D87/D89 answer it in
full and this feature has nothing to add — that is a genuine re-homing.
Read as a CALLER-supplied value used as pattern syntax at MATCH time — which
is what "a value the caller supplies" naturally means in a document about
`rx_var` — it is **declined, permanently, with no re-open condition**, for
the same architectural reason `${name/pat/repl}` is declined. `[LIB]` will
never let a caller hand pcrec a pattern at match time; a reader must not come
away believing otherwise.

### 4.3 What the caller still owes

Three obligations pcrec cannot discharge, stated so they are in the contract
rather than discovered — the third new with the by-name ruling above:

- **Lifetime.** `rx_var.p` must stay valid for the duration of the call. This
  is F9's rule for `rx_ctx.caps` (`design_callout_abi.md` §5) pointed the
  other way, and like F9 it is the embedder's bug when violated, with nothing
  in the generated code detecting it.
- **`rx_var.name`'s lifetime is the same rule, one field over.** It, too,
  must stay valid for the duration of the call — the resolution scan (§3.2)
  reads it during entry, not only at array-construction time. A caller who
  passes a `name` pointer that is freed between filling the array and
  calling the artifact has the identical bug class as an `rx_var.p` freed
  early, and the same absence of detection in generated code.
- **NUL.** A value may contain `0x00`; pcrec is 8-bit clean and the length is
  the contract, exactly as D38 Q4 ruled for substitution output. The caller
  passing a `strlen`-derived length over data that contains a NUL is the
  caller's truncation, not pcrec's — and it is the same hazard K9 records for
  the *pattern* string, where `pcrec_compile` takes no length at all.

---

## 5. Where this sits in the architecture

The charter asks: a preprocessing layer over a compiled artifact, or
something the emitter knows? **[PROPOSED]** both, and the seam between them is
not a compromise — it is forced, because the two halves have disjoint inputs.

| half | input | output | where it lives | shared? |
|---|---|---|---|---|
| **EXPANSION** — apply `:-`, `:+`, `^^`, `:off:len` … | the environment, and the group spans in R | one fixed byte span per reference | a wrapper at the top of the call; no subject, no automaton | **yes**, one implementation, both consumers |
| **INSERTION** — match those bytes | that span, and the subject | a match | the emitter (`vm_bref`'s span, one source over) in P; the splice loop in R | no, the consumers genuinely differ |

The expansion half is Frank's "a bit of code at the beginning, or in a
wrapper, that converts it to a fixed string," and it is exactly that: a pure
function of (template, environment) that touches no subject and knows nothing
about matching. It is where every shell operator lives, which is why the
operator suite can be identical in both consumers even though the insertion
halves are unrelated.

The insertion half is *not* preprocessing and the charter's framing would
mislead an implementer here. §0.3: the VM's runtime span compare already
exists, in the emitter, through the encoding seam. Trying to do the insertion
in a wrapper would mean rewriting the pattern text and recompiling per call,
which is the interpreter this project exists not to be.

**One consequence worth stating for the roadmap.** The expansion half is
shippable and testable *with no matcher at all*, exactly as
`subst_template_design.md` §1 argues for the template compiler and for the
same reason. That is what makes the MVP's phasing honest rather than
optimistic.

---

## 6. The four lenses

| lens | verdict |
|---|---|
| **specific vs general** | **GENERAL.** One grammar, one parser, one evaluator, one value model, serving two consumers that already exist in the plan as separate rows (`[FEAT-VAR]`, `[M4-SUBST]`). The alternative — a bespoke substitution syntax for templates and a different bespoke one for patterns — is the parallel-mechanism shape memory `pcrec-general-mechanisms-not-special-cases` names. The one per-consumer difference (§1.3) is a *scope* resolution, not a second grammar, and it is forced by what exists at each expansion point rather than chosen. |
| **core vs derived** | **DERIVED on the expansion half, CORE on one narrow line of the insertion half.** The expansion is a new pass over new input that touches no automaton, no table and no existing analysis. The insertion adds one AST kind and one encoding-seam entry; determinization, minimization, both emitters' existing paths and every optimization pass are untouched except for the forced-audit arms (`variables_pattern.md` §2), each of which takes the neutral element that `A_BREF` already takes. |
| **applicable vs assumption-changing** | **APPLICABLE**, with one assumption named and closed. A build with module `vars` disabled is unchanged in emitted code for every var-free artifact, because recognition is live but production is gated (`extension_design.md` §12, D34 ruling 5) and §0.2 proves the gated spelling matches nothing — except for the shared ABI block's `abi` digit, which every artifact carries once `PCREC_ERR_UNSET_VAR` lands in it, gated to EMISSION not existence (`variables_pattern.md` §5's precise statement). The one assumption that *would* change is "a value may be pattern syntax" — §4.2 refuses it, permanently and with its reason, precisely so the assumption stays where it is. |
| **fits-arch vs refactor** | **FITS.** Every piece has a home that predates it: the module gate (D37/`--features`), the registry row carrying `ENGM_VM` (SR-8, so engine selection needs no line in `select_engine.c` — though the PREFILTER decline does need one, a third construct-named predicate joining `has_bref`/`has_call`'s existing shape, `variables_pattern.md` §3), the encoding seam's entry table (`src/enc/enc.h`'s `PcrecEncEntry[]`), the fixed-literal ABI type family (D41.1 for `rx_ctx`/`rx_matchfn`/`rx_callout_ref`, D43/D44 for `rx_info`/`rx_group_entry`), the per-artifact stamp and `rx_info` append rule, the `limits.def` row for the nesting bound, and `axes.def` for the deny flag. Nothing here asks for a new *kind* of thing. The one structural debt it adds — six analysis/predicate sites to keep in step, five analysis declines plus the new prefilter predicate — is exactly what `[PATFACTS]` (D120) is chartered to absorb, and `variables_pattern.md` §2 names it as that row's first outside customer. |

---

## 7. Open questions

Numbered for reference; recommendations are this note's, not rulings.

1. **Does `rx_var` carry a `flags` word?** §3.1 ships three members
   (`name`, `p`, `len`). Every candidate flag is a compile-time property of
   the *use site*, which belongs in the pattern text where a reader can see
   it. *Recommend: no flags; a per-use-site declaration syntax if a phase
   ever needs one.*

2. **Is `${!name}` spent here?** §1.4 spends D38's reserved extension prefix
   on "the caller's environment," which is one use of a namespace ruled for
   pcrec extensions generally. *Recommend: yes — it is the extension with the
   widest reach, and the remaining namespace is still open (`${!upper:1}`-style
   forms all remain spellable).*

3. **UTF-8 validation of a value: unconditional, or only where reachable?**
   §2.1. *Recommend: unconditional in the MVP, and re-open under measurement
   only if a profile shows it.* The reachability analysis costs more to get
   right than the validation costs to run.

4. **Is `${name}` in a pattern the variable, or must a pattern also write
   `${!name}`?** §1.3 says the variable, on the "only scope that exists"
   argument. The counter-argument is one spelling, one meaning, everywhere.
   *Recommend as written, with §3.4's diagnostic as the mitigation* — but this
   is a taste call about a caller-facing surface and Frank's to make.

5. **Which phase's operators are worth building at all?** §1.1's table marks
   seven forms "phase" without ranking them. `variables_roadmap.md` §3 ranks
   them; the ranking is D77-shaped (each needs a stated want or a measured
   need) and none has a measurement today.

6. **Module name.** This note writes `vars` for the pattern-side module
   throughout. The replacement side rides D38's already-named `subst` /
   `subst-extended` / `subst-pcrec`, and by D38 Q5's own rule a `${!name}` in
   a template is `subst-pcrec`. *Recommend: `vars`; it is the noun the charter
   uses.* Naming is Frank's.
