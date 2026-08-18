# The match API — generated-artifact and library contract

This is the **spec**, not the design record: what pcrec's compiled library
(`lib/pcrec.h`) and every generated matcher actually promise, as shipped.
Per `docs/spec/CLAUDE.md`'s charter, this document states the contract; it
is actively maintained and carries no build history. Where it references
`docs/design/match_api_m4.md` or `docs/design/engine_m4.md`, that is
informational — the reasoning and panel record behind a rule, never a
second source of authority. On any disagreement between this document and
those, THIS document is what pcrec promises.

Every rule below was checked against the shipped surface at commit
`c113890` (the point this document was authored from): `lib/pcrec.h`
itself, artifacts actually emitted by `build/pcrec` for representative
patterns (a `--no-captures` DFA build, a captures-default VM build, a
custom `--prefix`), and the test cases cited inline. Two places where the
shipped surface does not match `match_api_m4.md`'s design text are called
out explicitly (§3.5, §7) rather than silently reconciled.

---

## 1. Two namespaces plus one closed, fixed-literal family

Every symbol a pattern compile can produce falls into exactly one of three
groups:

1. **Per-artifact symbols**, scoped by the caller's `pcrec_options.prefix`
   (default `"rx"`): `<prefix>_search`, `<prefix>_match`,
   `<prefix>_match_caps`, `<prefix>_info`, and the `<PREFIX>_*` macro
   family (`RX_NCAPS`, `RX_UNSET`, `RX_ERR_*`, the D46 observability
   macros in §6.3). A pattern compiled with `-p foo` gets
   `foo_search`, `FOO_NCAPS`, etc. — verified by compiling the same
   pattern under `-p foo` and reading the emitted header. (The CLI spells
   this option `-p` and only `-p`; there is no `--prefix` long form —
   `pcrec --prefix foo ...` is an unknown-option error.)
2. **pcrec's own fixed library surface**: the `PCREC_*` enum/bit
   constants and the `pcrec_options`/`pcrec_output`/`pcrec_error`/
   `pcrec_err_input` types declared in `lib/pcrec.h`. Never scoped by a
   generated pattern's prefix.

   **The `PCREC_*` spelling is not by itself a promise that a name lives
   in `lib/pcrec.h`**: two macros break that reading, and a consumer
   grepping for the namespace will find them. Every emitted artifact
   carries `PCREC_FEATURE_SET` and `PCREC_FEATURE_MODULES` (the D37
   artifact stamp — e.g. `#define PCREC_FEATURE_SET "std1"`,
   `#define PCREC_FEATURE_MODULES "classes,modifiers"`), which are
   `PCREC_*`-named, PER-ARTIFACT, and declared nowhere in `lib/pcrec.h`.
   They are the one exception to §8's own naming rule, and they are
   deliberate: an artifact must not be ambiguous about what it was built
   with. Everything else `PCREC_*` follows the rule as stated.
3. **Fixed-literal ABI types**, scoped by *neither* of the above, in the
   order the artifact declares them: `rx_ctx`, `rx_matchfn`,
   `rx_callout_ref`, `rx_renderfn`, `rx_group_entry`,
   `struct rx_info`. These are always spelled `rx_*`
   regardless of `--prefix`, on purpose: they are what let two
   differently-prefixed generated matchers compose in one translation
   unit (a compiled matcher links directly as another's callout, with no
   adapter) — verified in the emitted header: the six types live inside
   their own `#ifndef PCREC_RX_ABI_H` guard, separate from the
   per-prefix `PCREC_GEN_<PREFIX>_H` guard wrapping the rest of the file,
   so two artifacts compiled with different prefixes and `#include`d into
   one TU declare these types identically and do not collide (confirmed:
   `-p rx` and `-p foo` builds of the same pattern emit byte-identical
   `#ifndef PCREC_RX_ABI_H` blocks).

A generated artifact is either self-contained (`options.header_name ==
NULL`, everything below in the `.c`) or split into a paired `.h`/`.c`
(`options.header_name` set) — both forms carry the identical declarations
below. Two things beyond the file split differ, and a consumer writing
against the header namespace should know both: the self-contained form
omits the `PCREC_GEN_<PREFIX>_H` include guard entirely (measured with
`header_name == NULL`: zero occurrences, against three in the split
form's `.h`), since there is no header to guard; and the D46
observability macros of §6.3 are emitted into the `.c` only, never into
the `.h` (§6.3 states this where it matters).

---

## 2. Fixed ABI types

```c
typedef struct rx_ctx {
    const unsigned char *subject;   /* whole subject, not a slice */
    size_t                len;      /* subject length */
    size_t                pos;      /* where to match, anchored */
    size_t                ncap;     /* capture slots known so far (watermark
                                        mid-match; ncaps on completion) */
    const ptrdiff_t     (*caps)[2]; /* [start,end); {-1,-1} = unset */
    void                 *user;     /* per-binding user data */
} rx_ctx;

/* returns matched length >= 0 (anchored at ctx->pos), -1 (fail), or a
 * typed give-up code in [<PREFIX>_ERR_FLOOR, -2] -- one per way the
 * engine can give up (<PREFIX>_ERR_STEPS/_FRAMES/_WORK), where
 * <PREFIX> is this artifact's own uppercased --prefix. D49: those
 * codes PROPAGATE, they are not collapsed to -1, and a caller doing
 * an exact `== -1` test sees them as distinct values. Values
 * strictly BELOW <PREFIX>_ERR_FLOOR stay RESERVED for a future abort
 * semantic; no pcrec-emitted matcher produces one today, and a
 * generated call site that invokes an rx_matchfn traps on one.
 * Self-contained: must accept ctx->ncap == 0, ctx->caps == NULL. */
typedef ptrdiff_t rx_matchfn(const rx_ctx *ctx);

typedef struct rx_callout_ref {
    rx_matchfn *fn;
    void       *user;
} rx_callout_ref;

/* Emitted ONLY when a substitution template names it. Renders one
 * template segment from the same rx_ctx a callout receives. Writes at
 * most outcap bytes to out; returns the number of bytes produced, or
 * -1 to fail. Called with out == NULL and outcap == 0, it returns the
 * length it WOULD produce, writing nothing. */
typedef ptrdiff_t rx_renderfn(const rx_ctx *ctx,
                              unsigned char *out, size_t outcap);

typedef struct {
    const char *name;
    int         number;
    int         slot;   /* caps[] index this entry delivers, or -1 if
                           this build delivers no slot for it */
    const char *ref;    /* NULL/empty for the primary's own groups */
} rx_group_entry;

struct rx_info {
    /* ... elided here; §6 quotes the full field list ... */
};

extern const struct rx_info <prefix>_info;   /* not inside the ABI block */
```

The block above is the emitted text verbatim (re-quoted from a freshly
emitted artifact for this revision), with two marked exceptions: the
`struct rx_info` body is elided to §6, and `extern const struct rx_info
<prefix>_info;` is per-prefix and so lives *outside* the
`PCREC_RX_ABI_H` guard, not in this block. Three things the comments
state that a reader should not have to infer:

- **`rx_renderfn` carries a sizing protocol**, and it is shipped ABI
  text, not a design intention: called with `out == NULL` and
  `outcap == 0` it writes nothing and returns the length it *would*
  produce. That is how a caller sizes a buffer before rendering.
- **`rx_group_entry.ref`** is documented in the artifact only as
  "NULL/empty for the primary's own groups". Its non-empty form is a
  labeled insertion path that nothing in pcrec can produce today.
- **`<PREFIX>` in these comments is a placeholder, not a literal.** The
  block is byte-identical across every `--prefix` on purpose (§1), so it
  cannot name any one artifact's macros; substitute your own uppercased
  prefix when reading it.

**`rx_info` is a struct TAG, not a typedef, and every reference to it
spells `struct rx_info`** — verified directly (`grep`-visible in every
emitted header: `struct rx_info { ... };` and
`extern const struct rx_info <prefix>_info;`, no bare `rx_info` typedef
anywhere). This is an as-built departure from `match_api_m4.md` §5's
sketch, which showed a bare `typedef struct { ... } rx_info;`. The reason
is forced, not stylistic: under the default prefix `"rx"`, the per-artifact
instance `<prefix>_info` *is* the literal identifier `rx_info` — byte-
identical to the type's own name — and a typedef name and a variable name
cannot coexist in one C scope. Struct tags live in a separate C namespace
from ordinary identifiers, so `struct rx_info` (the type) and `rx_info`
(the default-prefix instance) coexist without conflict. **This is the
contract as shipped: an embedder writing code against a generated header
declares `const struct rx_info *`, never a bare `rx_info`.**

**This spelling is RULED, not provisional (D57, 2026-08-18).** The
question of renaming the per-artifact instance to buy a bare typedef
back is closed: the struct-tag form is blessed as the contract, and the
design sketch's typedef form is dead. A consumer that wants a typedef'd
name ships `typedef struct rx_info rx_info_t;` in its own header, which
touches nothing pcrec emits.

---

## 3. Entry points

Every generated artifact exports, unconditionally, four `<prefix>`-scoped
symbols.

### 3.1 `<prefix>_search` — the search-loop entry

```c
int <prefix>_search(const unsigned char *s, size_t n, size_t startpos,
                     ptrdiff_t (*caps)[2]);
```

Searches `s[startpos..n)` for the leftmost match and returns:

| return | meaning |
|---|---|
| `1` | match found; if `caps != NULL`, `<PREFIX>_NCAPS` pairs are written, `caps[0]` the whole-match span (no second name for it) |
| `0` | no match; `caps` (if non-NULL) is left **untouched** — the `int` return alone communicates match/no-match |
| `<PREFIX>_ERR_STEPS` / `_FRAMES` / `_WORK` | engine gave up (§4) |

`caps` may be `NULL` (existence-only search — every caller before M4.5
did exactly this, and the signature costs them nothing new).
`startpos > n` returns `0`. `^` anchors to absolute offset `0` regardless
of `startpos`. `s` may be `NULL` only when `n == 0`. One-shot: this finds
the *first* match from `startpos`; a caller wanting every match restarts
at the previous match's end (D41.5) — there is no batch find-all
primitive and none is planned for v1.

Verified against the shipped emitter (`src/gen/emit_dfa.c`): the DFA
matcher writes `caps[0][0]`/`caps[0][1]` only under `if (caps)`, guarded
exactly as documented, both in the unanchored search body and the
`--emit-main` `main()`.

### 3.2 `<prefix>_match` — the unconditional, anchored match-here entry

```c
ptrdiff_t rx_matchfn(const rx_ctx *ctx);   /* the shared type, §2 */
ptrdiff_t <prefix>_match(const rx_ctx *ctx);
```

Matches at exactly `ctx->pos`, no search loop. Returns the matched
length (`>= 0`), `-1` on no match, or a typed give-up code (§4). Delivers
**no captures** — `ctx->caps` is an *input* (§5), not an output channel,
and there is no parameter for `<prefix>_match` to write group offsets
into. Self-contained per its type's contract: a top-level caller passes
`ctx->ncap = 0, ctx->caps = NULL`.

### 3.3 `<prefix>_match_caps` — the anchored, capture-delivering entry

```c
ptrdiff_t <prefix>_match_caps(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2]);
```

Same anchoring as `<prefix>_match` (no search loop), plus a
capture-delivering output. On success, `caps_out[0..<PREFIX>_NCAPS-1]` are
all written (the same completed-match discipline as `<prefix>_search`),
`caps_out[0]` is `[ctx->pos, ctx->pos + length)`. On failure, `caps_out`
is untouched. `ctx->caps`/`ctx->ncap` are read as ordinary `rx_ctx` input
(unrelated to `caps_out`) — a top-level call passes `ncap=0, caps=NULL`
exactly like `<prefix>_match`.

Which entry a caller reaches for: no start position known and/or no
captures wanted → `<prefix>_search`; start position known, captures
wanted, no search loop wanted → `<prefix>_match_caps`; neither offsets
nor a loop wanted → `<prefix>_match`.

### 3.4 `<prefix>_info` — the reflection structure

```c
extern const struct rx_info <prefix>_info;
```

One instance per artifact, `.rodata`, zero runtime cost. Full field list:
§6.

### 3.5 A design-vs-shipped note: give-up codes are uniform, not collapsed

`match_api_m4.md` §3 as originally written required `<prefix>_match` to
**collapse** every give-up code to a bare `-1` (D42.3's reservation on
the `rx_matchfn` type). **That collapse does not exist in the shipped
artifact.** Verified directly: the emitted `<prefix>_match` body is

```c
ptrdiff_t rx_match(const rx_ctx *ctx)
{
    ptrdiff_t caps[RX_NCAPS][2];
    int found = rx_search(ctx->subject, ctx->len, ctx->pos, caps);
    if (found < 0) return (ptrdiff_t)found;   /* propagates, does not collapse */
    ...
}
```

with a comment stating the reasoning explicitly ("the give-up codes
PROPAGATE rather than collapsing to -1 ... the contract of `rx_matchfn`
is one contract"). This is the shipped, correct state: `docs/dev/
decisions.md` D49 supersedes D42.3 and rules the uniform-codes contract
this artifact implements — `match_api_m4.md`'s own §3 carries the D49
amendment in place. Stated here because a spec reader who only checked
the type comment (`rx_matchfn`'s doc comment inside the ABI-type block
still reads "matched length >= 0 ... or -1 (fail)" without spelling out
the give-up-code space in the same sentence) could reasonably expect the
collapse; the actual, checkable behavior is uniform propagation. A caller
that only tests `r < 0` for "did it match" is unaffected either way; a
caller doing an exact `== -1` comparison sees give-up codes as distinct
values, not folded into `-1`.

---

## 4. The give-up code space (D49)

`<prefix>_search`, `rx_matchfn` (hence `<prefix>_match` and any callout),
and `<prefix>_match_caps` all report engine give-up the same way: a
negative return strictly below `-1`.

```c
#define <PREFIX>_ERR_STEPS  (-2)   /* step budget exhausted (backtrack resumptions) */
#define <PREFIX>_ERR_FRAMES (-3)   /* backtrack-frame/trail capacity exhausted */
#define <PREFIX>_ERR_WORK   (-4)   /* forward-work budget exhausted (frames
                                       discarded at a cut; frameless-scan
                                       iterations — work the fail label
                                       never sees, counted separately from
                                       steps) */
#define <PREFIX>_ERR_FLOOR  (-4)   /* codes in [FLOOR, -2] are typed give-ups
                                       a caller may read and propagate;
                                       anything strictly below the floor is
                                       RESERVED for a future abort semantic */
```

Verified against both a DFA-only artifact (`--no-captures`, no counter
exists, these codes are reserved-but-unreachable) and a captures-default
VM artifact (`RX_STEP_BUDGET`/`RX_WORK_BUDGET`/`RX_BT_FRAMES`/
`RX_TRAIL_FRAMES` macros present, the counters live). A DFA-compiled
artifact never emits or reaches these codes — it has no counter to
exhaust — but the constants are still reserved and named from the first
build of any artifact, so a caller's `switch` written today does not need
revisiting when a later compile of the same pattern selects the VM.

**Composed call sites must trap below the floor.** Every generated call
site that invokes an `rx_matchfn` (a callout, a composed submatcher) must
enforce `if (ret < <PREFIX>_ERR_FLOOR) __builtin_trap();` — this binds
call sites that call *into* another `rx_matchfn`, not an exported entry's
own internal `return`. No such call sites are emitted by pcrec today
(callout code generation has no producer yet); the obligation is recorded
here for whichever future work (callouts, composition) first emits one.

**Today's `1`/`0` contract for `<prefix>_search` is unchanged** — this
reservation adds give-up outcomes, it does not renumber match/no-match.

---

## 5. Capture-slot semantics

```c
const ptrdiff_t (*caps)[2];         /* rx_ctx field; half-open [start, end) pairs */
#define <PREFIX>_NCAPS <n>          /* per-artifact, compile-time constant */
#define <PREFIX>_UNSET ((ptrdiff_t)-1)
```

- **Unset representation:** `{-1, -1}` in **both** slots of a pair.
  `caps[k][0] < 0` is a sufficient unset test.
- **Index 0 is always the whole match.** `<PREFIX>_NCAPS >= 1` always.
- **`<PREFIX>_NCAPS` is a property of the compiled ARTIFACT, not of the
  pattern text.** A DFA-compiled artifact — capture-bearing pattern or
  not — always emits `<PREFIX>_NCAPS 1`; `<PREFIX>_NCAPS > 1` implies the
  VM engine was selected. Verified: `'a(b|c)+d'` compiled `--no-captures`
  emits `RX_NCAPS 1` with `rx_info.ngroups == 1` (the pattern *has* a
  group; the artifact delivers no slot for it); the same pattern compiled
  with captures on (the default since M4.5) emits `RX_NCAPS 2`.
  `rx_info.ncaps == <PREFIX>_NCAPS` always (a structural invariant of the
  build).
- **Every pair `0..<PREFIX>_NCAPS-1` is written on a completed match** —
  no watermark needed at read time once a match succeeds.
- **On a failed match, the caller's array is left untouched.** No
  attempt is made to write `{-1,-1}` into it; the `int`/`ptrdiff_t`
  return value alone communicates failure.
- **Caller-owned, fixed-size, compile-time-sized**: a caller declares
  `ptrdiff_t caps[<PREFIX>_NCAPS][2];` on the stack. Nothing in the
  generated contract allocates.
- **`ctx->caps`, handed to a callout mid-match, is valid for the
  duration of that one call only.** The engine rewrites the same storage
  afterward (trail-based undo); a callout that retains the pointer past
  its own call and reads it later is the embedder's bug, not a pcrec
  contract violation.
- **A completed match's `caps` are stable until the next match call
  reusing the same buffer** — the matcher may overwrite the buffer
  between separate calls, but never mid-splice.

### 5.1 What a written slot's value actually means (the R22 rules)

C6 above says every slot `0..ncaps-1` is written on a completed match; it
does not by itself say *which* value a group inside a repeated construct
ends up holding when that group did not run in every iteration. Two rules
govern this, measured three-way unanimous (python `re`, libpcre2, and
pcrec agree) and now part of the shipped contract, not an addendum to it:

1. **Cross-iteration retention.** A group inside a quantifier whose
   subexpression did not run in the *final* iteration retains its value
   from the last iteration in which it *did* run. `((a)|(b))*` matched
   against `"ab"` reports group 2 as `[0,1)` — not unset — because group
   2 ran on the first iteration even though the second iteration took the
   other alternative. Unset means "never participated in the whole
   match", not "didn't participate in the match's last iteration".
2. **An empty final iteration still overwrites.** `(a*)*` and `(a?)*`
   matched against `"aaa"` both report group 1 as `[3,3)` — an empty
   iteration's write is a write, even though it contributes no bytes.

A caller reading `caps[k]` after a successful match therefore never needs
to reason about *which* iteration produced the value; both rules above
are already applied by the time the match completes, and the slot either
holds the group's last-executed span or is genuinely unset (the group
never ran at all, in any iteration, anywhere in the match).

### 5.2 Explicit non-requirements

The following are deliberately **not** part of this contract:

- No ovector sizing negotiation — the group count is a compile-time fact.
- No match-data object, no allocation, no lifecycle to manage.
- No run-time "does group N exist" query (a compile-time check, if
  needed, is the caller's own business).
- No run-time name lookup for template resolution (a future substitution
  compiler resolves `${name}` at pcrec-compile time).
- No partial-match or streaming window state.
- No callout/callback context beyond what `rx_ctx` itself carries — a
  callout binding's `user` data lives entirely in the `rx_callout_ref`
  the binding declares; nothing about *which* callout is firing is
  visible to `rx_matchfn`'s own signature.

---

## 6. `rx_info` — the reflection structure

```c
struct rx_info {
    unsigned      abi;             /* layout version; bump-on-change */
    uint64_t      flags;           /* PCREC_* option bits, exactly as compiled */
    int           encoding;        /* PCREC_ENC_* */
    int           ncaps;           /* == <PREFIX>_NCAPS: this artifact's
                                       caps[] slot count, all-in */
    int           ngroups;         /* capturing groups in the PATTERN
                                       TEXT — a lexical fact, independent
                                       of --no-captures and of engine
                                       selection */
    int           nnames;          /* entries in groups[]: NAMED groups
                                       only. 0 until module 'named-groups'
                                       lands (still true as of this
                                       writing — verified: '(?<g>a)' still
                                       refuses "requires module
                                       'named-groups'") */
    unsigned      engine;          /* ENGM_DFA (1) / ENGM_VM (2) */
    int64_t       step_budget;     /* -1 = none */
    int64_t       work_budget;     /* -1 = none; the THIRD bound (D47
                                       SECOND ADDENDUM): forward work the
                                       fail label never sees, counted
                                       separately from step_budget */
    int64_t       frame_capacity;  /* -1 = unbounded */
    int64_t       subject_ceiling; /* 0 = unset/not applicable; else the
                                       stamped honest ceiling for a
                                       residually-unbounded capture body */
    const char           *pattern;      /* source pattern text, as given
                                            to pcrec_compile() */
    size_t                pattern_len;  /* companion length — see §7 */
    const rx_group_entry *groups;       /* sorted, bsearch-able; NULL
                                            until named-groups */
    const char           *engine_why;   /* forcing construct/reason, or
                                            NULL; also carries a prefilter
                                            note on hybrid-eligible
                                            artifacts */
};
```

`ngroups`, `ncaps`, and `nnames` are three genuinely different counts and
do not, in general, coincide: `ngroups` is a fact about the pattern's own
text; `ncaps` is a fact about what *this build* delivers (pinned to `1`
on any DFA-compiled or `--no-captures` build regardless of how many
groups the text has); `nnames` is the length of the (currently always
empty) named-group index. Verified: the `--no-captures 'a(b|c)+d'` build
above has `ngroups=1, ncaps=1`; the captures-default build of the same
pattern has `ngroups=1, ncaps=2`.

`pattern` is embedded unconditionally as an escaped C string literal
(`"`, `\`, and control bytes are escaped — an unescaped pattern
containing `"` would otherwise emit a syntactically broken `.c` file;
verified the emitter carries a dedicated string-literal escaper distinct
from the `/* ... */`-comment escaper used elsewhere in the file).

`groups`/`nnames` stay `NULL`/`0` for every pattern until module
`named-groups` lands — verified live on this build (`'(?<g>a)'` still
refuses with `requires module 'named-groups'`).

### 6.1 `rx_info` is `.rodata`-only, link-time, not runtime, data

It is **not** part of `rx_ctx` or any callback parameter — a caller
reads `<prefix>_info` by symbol, once, at whatever point it wants the
artifact's own facts about itself (option flags, which engine, the
budgets it was built with, its own source pattern text).

### 6.2 Second-count example, worked

`'a(b|c)+d'` compiled `--no-captures`: `ncaps=1, ngroups=1` — the pattern
*has* a group, the artifact delivers no slot for it, and a reader who
only checked `ncaps` would wrongly conclude the pattern has no groups at
all. The two facts coincide only when `ncaps - 1 == ngroups`, i.e. a
VM-compiled, captures-on artifact — the common case since M4.5, not a
rule `rx_info` restates for every build.

### 6.3 The compile-time mirror: observability macros

Everything `rx_info` states as runtime/link-time data is *also* available
as a compile-time macro on a VM-compiled artifact, for a caller that wants
to `#if` on it rather than read a struct field — D46's "every strategy
selection point must be observable" requirement, discharged as a
same-shaped pair for each axis. Verified present on a captures-default
build of `'a(b|c)+d'`:

```c
#define RX_ENGINE          "vm"                    /* mirrors rx_info.engine */
#define RX_ENGINE_WHY       "capture group at pattern offset 1"
#define RX_VM_PREFILTER      "hybrid"               /* or "none" */
#define RX_VM_RUNGS           0x1u   /* bitmask: which per-quantifier rungs
                                         this artifact actually uses —
                                         CURSOR/FRAMES_BOUNDED/
                                         FRAMES_UNBOUNDED/REVDET/COUNTER */
#define RX_VM_STRATS           0x1u  /* bitmask: POSSESSIVE/BACKTRACKING */
#define RX_VM_PRUNES            0x1u /* bitmask: CLAMPED/UNCLAMPED (MRL) */
#define RX_VM_PRUNE_CEILING      "prefilter-window"
```

These are scalar/bitmask macros for a per-artifact-wide verdict
(`RX_ENGINE`, `RX_VM_PREFILTER`) or a bitmask when the axis is decided
per-quantifier and a single scalar would misreport a mixed pattern
(`RX_VM_RUNGS`, `RX_VM_STRATS`, `RX_VM_PRUNES`). Testing/tuning axes that
change no answer (possessification, reverse-determinism, the counter
rung, length pruning, the prefilter, alternation-class normalization) are
deliberately masked *out* of `rx_info.flags` and out of these macros'
underlying selection where the axis itself is a denial knob rather than a
selected strategy — two artifacts that behave identically must not differ
in their reflection surface over a knob with no observable effect. The
full `PCREC_NO_*`/`PCREC_FORCE_*` flag catalogue and its per-flag
reasoning live in `lib/pcrec.h`'s own comments (`lib/CLAUDE.md` indexes
them); this document does not duplicate that catalogue.

---

## 7. The compile-entry contract: patterns are NUL-terminated

`pcrec_compile()` takes a NUL-terminated `const char *pattern` and no
length parameter:

```c
int pcrec_compile(const char *pattern, const pcrec_options *opt,
                   pcrec_output *out, pcrec_error *err);
```

**A raw `0x00` byte inside the intended pattern silently truncates the
compile.** A 3-byte pattern `"a\0b"` compiles as the 1-byte pattern `"a"`
and `pcrec_compile()` reports **success** — for a different, shorter
pattern than the one the caller passed. This is not a defect pcrec
intends to fix in this API shape; it is the documented, checkable
behavior of a NUL-terminated entry point, and it is symmetric with a
comparison engine measured independently for this document:

**PCRE2's own `PCRE2_ZERO_TERMINATED` compile mode truncates
identically.** Measured directly against libpcre2 10.46 on this box
(dlopen'd via `tests/fuzz/pcre2_abi.h`, the project's existing
no-dev-package ABI shim — not read from documentation): compiling the
3-byte buffer `{'a', 0, 'b'}` with `PCRE2_ZERO_TERMINATED` produces a
pattern that matches only `"a"` (a 1-byte match at the start of the
3-byte subject `"a\0b"`), while compiling the same buffer with an
explicit `length=3` produces the real 3-byte pattern, matching the full
subject with span `[0,3)`. Both engines have exactly one honest way to
avoid this: the caller must pass the pattern's true length, which
PCRE2's API accepts and pcrec's `pcrec_compile()` today does not. This is
therefore an **API-surface gap relative to PCRE2's own length-taking
mode**, not a semantics divergence between the two engines' NUL handling
— PCRE2's sentinel mode has the identical failure mode pcrec's only mode
has.

**`rx_info.pattern_len` is the detectability instrument for this gap.**
It reports the *actual* byte count `pcrec_compile()` saw and compiled —
the truncated count, not the caller's intended count. A caller who
independently knows the pattern's true length can compare it against the
compiled artifact's `pattern_len` and catch exactly this silent
truncation after the fact. Verified: compiling the byte-built 3-byte
`"a\0b"` buffer through the real `pcrec_compile()` (not the CLI, which
cannot carry a NUL through `argv` at all) produces `out.c_src` containing
`.pattern_len = 1,` — the artifact honestly reports what it actually
compiled. This exact probe is pinned as `tests/cli/run_cli_tests.sh`
case16, and the general "`pattern_len` is the source byte count, not the
matched-byte count" property (distinguishing `pattern_len` from a count
of bytes the matcher actually walks — e.g. `'a\nb'`, 4 source bytes,
`pattern_len = 4`) is pinned structurally in
`tests/codegen/run_codegen_tests.sh`.

**Full length-taking compile support — a `(pattern, length)` overload or
equivalent that lets `pcrec_compile()` refuse a pattern whose declared
extent it cannot verify, rather than silently truncating and succeeding —
is not part of this contract.** It is scheduled with `DD-3` (generated-API
versioning/compatibility policy), tracked as `docs/dev/known_issues.md`
K9, and is the natural trigger for customer `V-A`'s `(pattern, length)`
compatibility shim. Until then, a caller with an untrusted or
NUL-containing pattern source must check `pattern_len` itself; nothing in
`pcrec_compile()`'s signature enforces that.

---

## 8. `pcrec_options`, `pcrec_error`, and the `PCREC_*` namespace

```c
typedef struct {
    const char *prefix;      /* C identifier prefix; default "rx" */
    int         encoding;    /* PCREC_ENC_* */
    uint64_t    flags;       /* PCREC_CASELESS | PCREC_EMIT_MAIN |
                                 PCREC_NO_CAPTURES | ... (see lib/pcrec.h
                                 for the full, growing bit catalogue) */
    const char *header_name; /* NULL = self-contained .c */
    int         engine;      /* PCREC_ENGINE_AUTO / _DFA / _VM */
    int64_t     step_budget; /* PCREC_STEP_BUDGET_DEFAULT / _NONE, or a count */
    int64_t     work_budget; /* PCREC_WORK_BUDGET_DEFAULT / _NONE, or a count */
    int         unroll_k;    /* PCREC_UNROLL_K_DEFAULT (0) = built-in default */
    int         frame_capacity; /* 0 = let the compiler size it */
} pcrec_options;
```

Every boolean option (`PCREC_CASELESS`, `PCREC_EMIT_MAIN`,
`PCREC_NO_CAPTURES`, and the strategy-denial/force flags in `lib/
pcrec.h`) is one representation end-to-end: the same bit set by a CLI
flag, carried in `pcrec_options.flags`, and reflected verbatim (where not
deliberately masked, §6.3) in the compiled artifact's `rx_info.flags`.
`PCREC_NO_CAPTURES` recovers the pre-captures-default pure-DFA artifact
(`<PREFIX>_NCAPS 1`); captures are on by default since M4.5.

`pcrec_error` carries which input a diagnostic's `pos` indexes into:

```c
typedef enum {
    PCREC_ERR_INPUT_PATTERN  = 0,
    PCREC_ERR_INPUT_TEMPLATE = 1
} pcrec_err_input;

typedef struct {
    char            msg[256];
    size_t          pos;
    pcrec_err_input input;
} pcrec_error;
```

`pcrec_compile()` always sets `input = PCREC_ERR_INPUT_PATTERN` today (it
has no other input yet — a future substitution-template compiler is the
first producer of `PCREC_ERR_INPUT_TEMPLATE`). `pcrec_compile()` returns
`0` on success (`out` filled) or `-1` on failure (`err` filled if
non-NULL) — verified directly: an unterminated group `"a(b"` returns
`-1` with `err.pos == 1, err.input == PCREC_ERR_INPUT_PATTERN`.

`PCREC_*` names only pcrec's own enum/bit-valued constants — never a
struct field name, never a bare CLI flag spelling. `PCRE2_*` spellings
are reserved for a future PCRE2-compatibility layer and are never native.

---

## 9. Provenance and status

This document graduates `docs/design/match_api_m4.md` (the M4 match-API
freeze design record) and `docs/design/engine_m4.md` into a spec per
`docs/dev/decisions.md` D40's addendum: design records what pcrec wants
to build and the process that got there; this spec records what shipped
and is pcrec's contract with an embedder, going forward. Consult those
documents for *why* a rule is what it is (ruling citations, panel
findings, refuted alternatives); consult this document for *what the
rule is*.

**Pre-v1 posture (D40):** this contract carries no backwards-compatibility
weight yet. Breaking changes are unconstrained in substance and governed
only in form — one announced-boundary commit per break, populations
conserved and accounted, never silent drift. At a future v1 declaration,
this document (or its direct successor) becomes the compatibility-bound
enumeration; until then, "frozen" here means "the M4 working baseline",
not "permanent".
