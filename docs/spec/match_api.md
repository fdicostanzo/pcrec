# The match API — generated-artifact and library contract

This is the **spec**, not the design record: what pcrec's compiled library
(`lib/pcrec.h`) and every generated matcher actually promise, as shipped.
Per `docs/spec/CLAUDE.md`'s charter, this document states the contract; it
is actively maintained and carries no build history. Where it references
`docs/design/match_api_m4.md` or `docs/design/engine_m4.md`, that is
informational — the reasoning and panel record behind a rule, never a
second source of authority. On any disagreement between this document and
those, THIS document is what pcrec promises.

Every rule below was checked against the shipped surface: `lib/pcrec.h`
itself, artifacts actually emitted by `build/pcrec` for representative
patterns (a `--no-captures` DFA build, a captures-default VM build, a
custom `-p` prefix, budget-limited builds), and the test cases cited
inline. Two places where the shipped surface does not match
`match_api_m4.md`'s design text are called out explicitly (§3.5, §7)
rather than silently reconciled.

**Verification ledger.** The document was authored at commit `c113890`
and re-verified end to end after the R29 adversarial panel
(2026-08-18, `[M4.7g]`). Every claim was re-checked against artifacts
emitted freshly for that pass, and this revision adds these measurements:
the find-all protocol of §3.1 run against `python3 re.finditer` on twelve
(pattern, subject) pairs plus three that expose its documented lossiness;
the §8.0 example compiled `-Wall -Wextra -Werror`, run, and its output
compiled in turn; the subject-side contract of §3.1 measured under
AddressSanitizer on exact-size heap buffers with a firing positive
control; §5.3's concurrency promise checked against the shipped,
sabotage-validated TS-1/TS-2/TS-3 guards rather than a one-off probe;
§3.4/§6.1's section placement measured with `readelf`; §6.3's macro
inventory measured by listing every `#define` in a build of each engine;
§8.1's D56 guarantees measured at the refusal boundary. Two errors the
panel found in the previous revision are recorded where they happened
rather than quietly repaired: §3.5 (a contradiction described as an
omission, and §2 quoting a corrected comment as if it were shipped) and
§6.3 (a mirror claimed to be total that is partial). The corresponding
shipped comments — the emitted `rx_matchfn` ABI block and
`lib/pcrec.h`'s generated-searcher comment — were fixed in the same
pass, so §2's quotation is now the real text.

**[M5-SEAM] revision (2026-08-18, D58 — the encoding seam prelude).** The
document gains §3.1.1, the `<prefix>_next_pos` encoding residual, and §3.1's
find-all loop now advances through it. What this pass re-measured, all
against artifacts emitted by the build at this commit: §3.1's loop compiled
against real artifacts and run on 26 (pattern, subject) pairs x 2 engine
arms = 52 runs against `python3 re.finditer`, with the lossy class checked
as a strict SUBSET in both directions (the measurement is now
`tests/encseam/`, a suite in `make test`, rather than a one-off transcript);
§3.1.1's two code blocks quoted verbatim from a fresh `-p rx` build of
`'a(b|c)+d'`, no elisions; §8.0's example recompiled `-Wall -Wextra -Werror`
against `lib/pcrec.h` and `libpcrec.a`, run, and its `matcher.c` compiled in
turn, plus every field of a `pcrec_default_options()` struct printed to
re-check item 1's claim; §8.1's D56 refusal re-measured at the `a{9795}` /
`a{9796}` boundary (its wording changed — the old text promised a milestone
that had already shipped) together with the escape it now names; §8.2's
encoding paragraphs measured at the refusal boundary for `utf8` and for an
out-of-range value. Two SURFACE changes ride this revision and are recorded
where they happen rather than folded in silently: `PCREC_ENC_ASCII` is
renamed `PCREC_ENC_BYTE` (§8.2), and §3.1's byte-vs-character caveat is
RESOLVED rather than deleted — §3.1.1 keeps the old caveat's text and says
what discharged it. A same-day manager follow-up (from a live
consumer-question thread) adds two ADVISORY clarifications: the §3
entry-picker's discriminator sentence and §3.2's failing-match cost note —
prose only, no emitted text quoted, nothing re-measured.

---

## 1. Two namespaces plus one closed, fixed-literal family

Every symbol a pattern compile can produce falls into one of three
groups, with one stated boundary case (the two artifact-stamp macros
noted under group 2, which are `PCREC_*`-named yet per-artifact):

1. **Per-artifact symbols**, scoped by the caller's `pcrec_options.prefix`
   (default `"rx"`): `<prefix>_search`, `<prefix>_match`,
   `<prefix>_match_caps`, `<prefix>_info`, `<prefix>_next_pos` (§3.1.1),
   and the `<PREFIX>_*` macro
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

Every generated artifact exports, unconditionally, five `<prefix>`-scoped
symbols: the four below, plus the encoding residual `<prefix>_next_pos`
that §3.1.1 specifies (a fifth entry since [M5-SEAM], and the one place an
artifact's byte-vs-character distinction lives).

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
| `<PREFIX>_ERR_STEPS` / `_FRAMES` / `_WORK` | engine gave up (§4); `caps` also left **untouched** |

Note that `0` here means **no match**, not a zero-length match. A
zero-length match is a success: it returns `1` with
`caps[0][0] == caps[0][1]`. (The anchored entries of §3.2/§3.3 use the
other convention, because their return value carries a length: there `0`
IS a zero-length match, and no-match is `-1`.)

`caps` may be `NULL` (existence-only search — every caller before M4.5
did exactly this, and the signature costs them nothing new).
`startpos > n` returns `0`. `^` anchors to absolute offset `0` regardless
of `startpos`. `s` may be `NULL` only when `n == 0`.

**Every offset written to `caps` is an ABSOLUTE offset into `s`, never
relative to `startpos`** — measured, and the property a find-all loop
depends on: searching `"xabcabcx"` for `abc` from `startpos = 0` reports
`[1,4)`, and the next search from `4` reports `[4,7)`, not `[0,3)`.

**The subject side of the contract.** `s` is `n` bytes and nothing more:
a `0x00` byte inside `s` is an ORDINARY byte with no special meaning (it
is only the *pattern* side, §7, that is NUL-terminated), and **the
matcher never reads `s[n]`** — there is no sentinel, so `s` need not be
NUL-terminated and need not have a readable byte after its end.
Measured on both engines with the subject in an exact-size heap
allocation under AddressSanitizer: `a.b` and `a(.)b` both match the
3 bytes `{'a', 0x00, 'b'}` (span `[0,3)`, group 1 `[1,2)`), and matching,
non-matching and `n == 0` searches over exact-size buffers are all clean.
The check is non-vacuous: the same probe compiled to read one byte past
the end (`n` overstated by one) fires a heap-buffer-overflow at the
matcher's own `memchr` prefilter.

#### Finding every match

This entry is ONE-SHOT: it finds the *first* match at or after
`startpos`. There is no batch find-all primitive and none is planned for
v1, so a caller wanting every match writes the loop — and the loop is
not simply "restart at the previous match's end", which spins forever
the first time a pattern matches empty (`a*` on `"bbb"` returns `[0,0)`
from `startpos = 0` for ever). The rule that terminates and is correct:

```c
size_t p = 0;
while (p <= n) {
    int r = <prefix>_search(s, n, p, caps);
    if (r != 1) break;                       /* 0 = done; < 0 = gave up (§4) */
    report(caps[0][0], caps[0][1]);
    p = (caps[0][1] > caps[0][0])            /* non-empty: resume at its end */
          ? (size_t)caps[0][1]
          : <prefix>_next_pos(s, n, (size_t)caps[0][0]);   /* EMPTY: next char */
}
```

**The empty-match advance rule**: a zero-length match is reported like
any other, and then the next search starts at the next CHARACTER boundary
past its start. Note that the advance is off the match's own START
(`caps[0][0]`), not off the loop variable — an empty match can be found at
a position later than the one searched from. The loop terminates because
`p` moves strictly forward every iteration (§3.1.1's contract makes
`<prefix>_next_pos` return a position strictly greater than the one it was
given) and `p > n` ends it.

That loop, coded exactly as written above, was compiled against real
artifacts and run against `python3 re.finditer` on twenty-six
(pattern, subject) pairs, on BOTH engines — each pattern compiled twice,
captures-on and `--no-captures`, for 52 runs. Twenty-two agree with
`re.finditer` span for span, including the three that motivate the rule:
`a*` over `"bbb"` → `(0,0) (1,1) (2,2) (3,3)`; `x?y` over `"yy"` →
`(0,1) (1,2)`; and alternations mixing empty and non-empty branches —
`a|` over `"bab"` → `(0,0) (1,2) (2,2) (3,3)` and `a|b*` over `"cbbac"` →
`(0,0) (1,3) (3,4) (4,4) (5,5)`. It also agrees on `a*`/`"aaa"`,
`a?`/`"aba"`, `b*`/`"abbbab"`, `(a|)`/`"xax"`, `a(b|)c`/`"acabc"`,
`(ab)*`/`"ababx"`, `a{0,2}`/`"aaaa"`, `[a-c]*`/`"xabcx"`, and on the ten
pairs added with this revision: `[0-9]+`/`"a12b345"`, `a{2,}`/`"aaaa"`,
`(?:ab|a)`/`"aab"`, `(a*)*`/`"aab"`, `.`/`"abc"`, `ab$`/`"xabab"`,
`^a`/`"aa"`, `c*` and `x` over the EMPTY subject, and `a`/`"a"`. The whole
set is `tests/encseam/findall_cases.txt` and it runs in `make test`, so
this measurement is a check now rather than a transcript.

**Where this loop is LOSSY, stated honestly.** It reports fewer matches
than PCRE2 and python `re` do for a pattern that *prefers* the empty
match at a position where a non-empty match also starts. Those engines,
on finding an empty match at `p`, RETRY at `p` with an
"empty match not permitted here" constraint (PCRE2 spells it
`PCRE2_NOTEMPTY_ATSTART`) and report the non-empty match too, before
moving on. **pcrec's entry points cannot express that retry** — there is
no "must not match empty here" mode on any of them — so the advance rule
above is the whole of what a pcrec consumer can do. Measured
divergences, all of this one class, and all of them OMISSIONS — the
protocol's spans are always a strict SUBSET of `re.finditer`'s, which the
suite checks rather than accepting any difference at all: `|a` over
`"aaa"` — this loop reports 4 spans `(0,0) (1,1) (2,2) (3,3)` where
`re.finditer` reports 7, adding `(0,1) (1,2) (2,3)`; likewise `a*?` over
`"aaa"` (4 vs 7), `a??` over `"aba"` (4 vs 6) and `b*?` over `"abba"`
(5 vs 7). Where the pattern's own preference picks a non-empty match
wherever one starts — all twenty-two agreeing cases above, including
every greedy quantifier among them — there is no divergence.

Verified against the shipped emitter (`src/gen/emit_dfa.c`) and a fresh
artifact: the DFA matcher writes `caps[0][0]`/`caps[0][1]` only under
`if (caps)`, guarded exactly as documented, in the unanchored search
body. The `--emit-main` `main()` carries no such guard and needs none —
it passes a real array, never `NULL`.

#### 3.1.1 `<prefix>_next_pos` — the encoding residual

The loop's advance is not `+ 1`. It goes through a fifth exported entry,
which every artifact carries:

```c
size_t <prefix>_next_pos(const unsigned char *s, size_t n, size_t pos);
```

**This entry is the one place an artifact's byte-vs-character distinction
lives** ([M5-SEAM], `docs/dev/decisions.md` D58; the architecture is
`docs/dev/plan.md`'s `[DD-12]` row). An artifact embeds exactly one
encoding's residual block, chosen per compile call by
`pcrec_options.encoding` (§8.2) — never process- or file-globally, so two
differently-prefixed artifacts compiled for different encodings compose in
one translation unit exactly as §1 says they do.

The contract, quoted verbatim from a freshly emitted artifact (the
declaration and its own comment in a `-p rx` build of `'a(b|c)+d'`, no
elisions):

```c
/* rx_next_pos -- the ENCODING RESIDUAL entry (pcrec DD-12/D58).
 *
 * Returns the smallest position STRICTLY GREATER than pos that is a
 * CHARACTER BOUNDARY of this artifact's encoding, counting every position
 * >= n as a boundary. So the result is in (pos, n] whenever pos < n, and is
 * pos + 1 whenever pos >= n -- which is what lets a find-all loop advance
 * past a zero-length match and still terminate (see pcrec's
 * docs/spec/match_api.md S3.1, which writes that loop out).
 *
 * This entry is the ONE place an artifact's byte-vs-character distinction
 * lives. It reads s only at offsets in [pos, n), so the (s == NULL, n == 0)
 * subject rx_search accepts is legal here too, and it is never called from
 * this artifact's own engine: it is caller-facing residue, not hot-path
 * code.
 *
 * THIS artifact was compiled for the `byte` encoding, where one byte is one
 * character. An artifact compiled for another encoding exports this same
 * entry with that encoding's body and no caller loop changes. */
size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);
```

Four consequences a caller can rely on:

- **It is an ordinary extern function**, declared in the emitted header
  (or, in a self-contained artifact, in the `.c` beside the other four
  entries' declarations) and defined in the `.c`. Not a macro, not
  `static inline`: it is a caller-facing entry point, and it is declared
  where the other entry points are declared.
- **It never reads outside `[pos, n)`**, so the `(s == NULL, n == 0)`
  subject §3.1 already admits is legal here too. Under the byte encoding
  it does not read `s` at all.
- **`pos > n` is not an error** — the result is simply `pos + 1`. That is
  what lets the loop above terminate with no special case.
- **The result is always strictly greater than `pos`.**

**Under the byte encoding — the only one implemented today — the body IS
`pos + 1`**, and this is measurement, not intention. The whole definition,
verbatim from the same artifact:

```c
/* byte encoding: one byte is one character, so the next boundary after pos
 * is pos + 1 and the subject is never read. */
size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos)
{
    (void)s; (void)n;
    return pos + 1;
}
```

**This resolves a caveat this section carried until [M5-SEAM], and the
history is worth keeping rather than deleting.** The loop's advance used
to be a literal `+ 1`, and this section warned that "`+ 1` advances one
BYTE … when module `utf8` lands at M5 this becomes the wrong advance for a
multi-byte character, and M5 owns sharpening it; a consumer writing
UTF-8-aware find-all today must advance to the next character boundary
itself." That obligation is discharged, and discharged in the direction
that costs the caller nothing: **the loop above is already final.** M5's
UTF-8 backend supplies a boundary-aware body for this same entry under
this same signature, and no caller's find-all loop changes a character —
which is the entire point of the residual seam. What a consumer must NOT
do is inline the `+ 1` back: that is the one edit that would make a
byte-compiled caller wrong against a UTF-8-compiled artifact. (The
caveat's other half — "the ASCII encoding, `PCREC_ENC_ASCII`" — is also
gone by rename: the constant is `PCREC_ENC_BYTE` and the CLI value is
`byte`, since the semantics were always "every byte is a character",
which is not what ASCII says. §8.2 records the rename.)

The complementary half of the seam is a NEGATIVE promise, and it is
enforced rather than asserted: **a residual entry is never called from the
artifact's own engine.** DD-12 (7) forbids the hot path depending on the
encoding; `tests/codegen/run_codegen_tests.sh` reads every emitted engine
body for a residual reference across six emission shapes in both artifact
forms; and the check is sabotage-validated
(`tests/mech/sabotages/S68_residual_in_hot_loop.sh` makes the emitted
bitmap prefilter's skip loop advance through `<prefix>_next_pos` — the
whole `.rxt` corpus stays green, because under this backend the two are
the same value, and only the structural check sees it).

### 3.2 `<prefix>_match` — the unconditional, anchored match-here entry

```c
ptrdiff_t rx_matchfn(const rx_ctx *ctx);   /* the shared type, §2 */
ptrdiff_t <prefix>_match(const rx_ctx *ctx);
```

**Matches at exactly `ctx->pos`: a match starting anywhere else is not
reported.** That is the semantic promise, and it is what a caller can
rely on; it is deliberately not a claim about how the artifact is built.
The two engines implement it differently — the VM emitter genuinely has
no search loop here, while the DFA emitter reaches the same answer by
running its ordinary search and rejecting any match whose start is not
`ctx->pos`. Both were measured to give the same answers; only the
promise above is contractual. One COST consequence of the DFA shape is
worth a caller's attention: on a FAILING match-here, the underlying
unanchored search does not know the question is anchored — it may skim
the remainder of the subject hunting a later match the filter will then
discard (the state-0 `memchr` skip keeps this a skim rather than a
per-byte walk), where the VM's anchored body fails at the first
divergent byte. A caller issuing many expected-to-fail `<prefix>_match`
probes against long subjects on a DFA artifact is in this entry's worst
case; the filed improvement (an emitted anchored automaton,
docs/dev/plan.md [ENG-ABS]) is evidence-gated and not scheduled.

Returns the matched
length (`>= 0`), `0` for a zero-length match at `ctx->pos`, `-1` on no
match, or a typed give-up code (§4). Delivers
**no captures** — `ctx->caps` is an *input* (§5), not an output channel,
and there is no parameter for `<prefix>_match` to write group offsets
into. Self-contained per its type's contract: a top-level caller passes
`ctx->ncap = 0, ctx->caps = NULL`.

### 3.3 `<prefix>_match_caps` — the anchored, capture-delivering entry

```c
ptrdiff_t <prefix>_match_caps(const rx_ctx *ctx, ptrdiff_t (*caps_out)[2]);
```

Same anchoring promise as `<prefix>_match`, plus a
capture-delivering output. On success, `caps_out[0..<PREFIX>_NCAPS-1]` are
all written (the same completed-match discipline as `<prefix>_search`),
`caps_out[0]` is `[ctx->pos, ctx->pos + length)`, and **`caps_out[k]` is
capturing group `k`** for `k >= 1`, in the pattern's own left-to-right
numbering, on any captures-on build. (`rx_group_entry.slot` exists for a
future in which a build delivers a *different* slot for a group; on
today's builds no such indirection is in play and the identity above is
what the examples in §5.1 rely on.)

**On failure, `caps_out` is untouched — and a give-up is a failure for
this rule.** Every negative return leaves the caller's array exactly as
it was; the generated source says so outright ("caps_out is UNTOUCHED on
every negative return, give-up included"). The same holds for
`<prefix>_search`'s `caps`.

`ctx->caps`/`ctx->ncap` are read as ordinary `rx_ctx` input
(unrelated to `caps_out`) — a top-level call passes `ncap=0, caps=NULL`
exactly like `<prefix>_match`.

Which entry a caller reaches for: no start position known and/or no
captures wanted → `<prefix>_search`; start position known, captures
wanted, no search loop wanted → `<prefix>_match_caps`; neither offsets
nor a loop wanted → `<prefix>_match`. The discriminator is whether the
start position is KNOWN, never whether captures are wanted:
`<prefix>_search` delivers full captures too when handed a `caps`
buffer (§3.1's table), so "first match plus its groups" is one
`<prefix>_search` call — `<prefix>_match_caps` is only for the anchored
case, and reaching for it because "captures" appears in its name is the
misreading this sentence exists to prevent.

**One caveat on that ergonomic framing**, because it invites reading the
three entries as interchangeable views of one answer: they are not, on
the give-up axis. §4's uniformity is about the CODE SPACE — which values
mean what — not about which entry gives up on a given input. Whether a
budget is exhausted is a property of the entry point, because the
entries do different amounts of work — and it goes BOTH ways. Measured,
`(a|aa)+b` built `--step-budget=3`: over `"aaaaaaaaaaaaaaaaaaaaX"`,
`<prefix>_search`
returns `0` (its DFA prefilter resolves the question definitively
without ever entering the VM) while `<prefix>_match` and
`<prefix>_match_caps` both return `-2`. And on the same artifact family
built `--backtrack-frames=1`, the reverse: over `"xxaaaaab"`,
`<prefix>_search` returns `-3` while both anchored entries return a
clean `-1`, because anchoring at position 0 fails immediately and never
spends a frame. A caller must therefore handle give-ups on whichever
entry it actually calls, and must not infer from one entry's clean
answer that another would give one.

### 3.4 `<prefix>_info` — the reflection structure

```c
extern const struct rx_info <prefix>_info;
```

One instance per artifact, link-time constant, no runtime cost to build
it. Full field list: §6.

**It is not, strictly, `.rodata`, and the difference is the one an
embedder targeting ROM or flash cares about.** `struct rx_info` holds
two pointers — `pattern` and `engine_why` — so the object needs
load-time relocation and the toolchain places it accordingly. Measured
with `readelf` on a default build of `'a(b|c)+d'`: `rx_info` is a
104-byte object in section `.data.rel.ro.local` (writable-then-read-only,
not `.rodata`), and that section carries exactly two `R_X86_64_64`
relocations, one per embedded string pointer. The strings themselves are
in `.rodata`. There is no run-time initializer and no constructor; the
cost is two relocations at load, not zero.

### 3.5 A design-vs-shipped note: give-up codes are uniform, not collapsed

`match_api_m4.md` §3 as originally written required `<prefix>_match` to
**collapse** every give-up code to a bare `-1` (D42.3's reservation on
the `rx_matchfn` type). **That collapse does not exist in the shipped
artifact**, on either engine. Both bodies, quoted from freshly emitted
artifacts:

```c
/* DFA artifact (--no-captures 'a(b|c)+d'), with its full comment: */
/* D49: the give-up codes PROPAGATE rather than collapsing to -1.
 * Unreachable on this engine — a DFA artifact has no counter to
 * exhaust — but written uniformly on purpose: the contract of
 * rx_matchfn is one contract, and a wrapper that discards codes it
 * merely happens never to see is the shape that goes wrong when a
 * later engine shares this emitter. */
ptrdiff_t rx_match(const rx_ctx *ctx)
{
    ptrdiff_t caps[RX_NCAPS][2];
    int found = rx_search(ctx->subject, ctx->len, ctx->pos, caps);
    if (found < 0) return (ptrdiff_t)found;
    if (found != 1 || (size_t)caps[0][0] != ctx->pos) return -1;
    return caps[0][1] - caps[0][0];
}
```

```c
/* VM artifact ('a(b|c)+d' under -p r22a), where the codes are LIVE: */
ptrdiff_t r22a_match(const rx_ctx *ctx)
{
    r22a_work w;
    ptrdiff_t r;
    if (ctx->pos > ctx->len) return -1;
    r22a_work_init(&w);
    r = r22a_match_impl(ctx, &w, ctx->len);
    /* No translation and no clamp: the impl's return space IS this
     * contract's -- >= 0, -1, or one of the three R_ sentinels, which
     * are the ERR_ codes. A defensive floor test here would be dead
     * code pretending to be a safeguard. */
    return r;
}
```

**Both quotations matter, and quoting only the first would be a broken
check.** The DFA body's own comment says the propagation branch is
*unreachable on that engine* — a DFA artifact has no counter to exhaust
— so it is evidence that the emitter WRITES the propagation, not that
propagation ever happens. The live evidence is the VM: measured,
`(a|aa)+b` built `--step-budget=3` returns `-2` from `<prefix>_match`
and `<prefix>_match_caps`, and the same pattern built
`--backtrack-frames=1` returns `-3` from all three entries — including
`<prefix>_search` — on the subject `"ab"`. (The DFA body's second line,
`if (found != 1 || caps[0][0] != ctx->pos) return -1;`, is also the only
thing making that engine honor §3.2's anchoring promise — worth seeing
rather than eliding.)

This is the shipped, correct state: `docs/dev/decisions.md` D49
supersedes D42.3 and rules the uniform-codes contract these artifacts
implement — `match_api_m4.md`'s own §3 carries the D49 amendment in
place. A caller that only tests `r < 0` for "did it match" is unaffected
either way; a caller doing an exact `== -1` comparison sees give-up
codes as distinct values, not folded into `-1`.

**An artifact generated before 2026-08-18 carries a comment that
contradicts all of the above, and a reader holding one needs to know
that.** Until that date, the emitted `rx_matchfn` ABI comment read
"Return values < -1 are RESERVED for a future abort semantic; no
pcrec-emitted matcher produces one today" — an affirmative false
statement about the artifact it sits in, which the measurements above
refute. **Where an old artifact's comment and this document disagree,
this document is the contract; the artifact's behavior always matched
this document, not its own comment.** This section as first written
(`[M4.7f]`) described that comment as merely *omitting* the give-up
codes, which was too generous by a wide margin, and §2 of this document
quoted a *corrected* version of that comment as though it were the
shipped text. Both were found by the R29 panel and fixed in the same
pass (`[M4.7g]`, 2026-08-18): the emitted comment now states the give-up
space (§2 quotes it verbatim), and `lib/pcrec.h`'s generated-searcher
comment, which had the same defect in its own words, now names the
negative return space too.

---

## 4. The give-up code space (D49)

`<prefix>_search`, `rx_matchfn` (hence `<prefix>_match` and any callout),
and `<prefix>_match_caps` all report engine give-up in the same CODE
SPACE: a negative return strictly below `-1`, with the same value
meaning the same thing at every entry. That uniformity is about the
codes, not about when a give-up happens — which entry gives up on a
given input is a property of that entry (§3.3's caveat, measured in both
directions).

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
artifact never RETURNS one of these codes — it has no counter to
exhaust — but it does EMIT them: the constants are defined in every
artifact, and a DFA artifact built `--emit-main` even emits the full
three-way handler text for them (measured: `if (rc == RX_ERR_STEPS)`,
`_FRAMES`, `_WORK` all present in a `--no-captures --emit-main` build).
That is deliberate, and it is what lets a caller's `switch` written
today survive a later compile of the same pattern selecting the VM.

**Composed call sites must trap below the floor.** Every generated call
site that invokes an `rx_matchfn` (a callout, a composed submatcher) must
enforce `if (ret < <PREFIX>_ERR_FLOOR) __builtin_trap();` — this binds
call sites that call *into* another `rx_matchfn`, not an exported entry's
own internal `return`. No such call sites are emitted by pcrec today
(callout code generation has no producer yet); the obligation is recorded
here for whichever future work (callouts, composition) first emits one.

**Today's `1`/`0` contract for `<prefix>_search` is unchanged** — this
reservation adds give-up outcomes, it does not renumber match/no-match.
It does mean the return is not two-valued, so `if (<prefix>_search(...))`
reads a give-up as a match: test `== 1` for "matched" (§3.1).

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
- **On a failed match, the caller's array is left untouched — and an
  engine GIVE-UP is a failure for this rule.** Every negative return
  from an anchored entry, and a `0` or a give-up code from
  `<prefix>_search`, leaves the array exactly as the caller left it. No
  attempt is made to write `{-1,-1}` into it; the `int`/`ptrdiff_t`
  return value alone communicates failure. The generated source states
  the give-up half outright ("caps_out is UNTOUCHED on every negative
  return, give-up included").
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

The following are deliberately **not** part of this contract. Every item
here is scoped to the MATCH path — the generated matcher and its
caps buffers. The pcrec LIBRARY's own compile path does allocate and
does have a lifecycle to manage; that is §8's `pcrec_output` /
`pcrec_output_free`, and nothing here excuses skipping it.

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

### 5.3 Concurrency: a generated matcher is reentrant and thread-safe

**A generated matcher holds no mutable state of its own.** Every entry
point's working state lives in its own stack frame and in the caller's
`caps` buffer; the tables, bitmaps and the `rx_info` instance are
`const`. Therefore:

- Any number of threads may call the same artifact's entry points
  concurrently, **provided each call has its own `caps`/`caps_out`
  buffer** (which the caller owns and declares, per the rule above).
  Sharing one buffer between concurrent calls is a data race in the
  CALLER's code, not something the matcher serializes for it.
- The same holds for one thread re-entering a matcher (from a callout,
  say), subject to the same distinct-buffer rule.
- `<prefix>_info` is read-only and may be read from anywhere at any time.

**This is a CONTRACT, binding on future emitters, not merely an
observation about today's output.** It is what makes a generated matcher
usable from a thread pool at all, and an engine that wanted a mutable
scratch buffer would have to change this document first.

It is also GUARDED rather than asserted, by two shipped checks that run
in `make test`:

- **TS-1** (D19) is static: it scans every emitted file across nine
  emission shapes and fails on any non-const static object, or any
  reference to a non-reentrant or allocating libc symbol.
- **TS-2** is dynamic and runs under ThreadSanitizer: eight threads
  share ONE compiled matcher and search DIFFERENT subjects
  concurrently, across five patterns chosen to hit five differently
  *shaped* emitted engines, and every threaded result must equal a
  single-threaded baseline recorded before any thread was spawned.
  **Its sabotage arm proves the detector is watching** — a planted race
  in a scratch copy of the driver must be caught, or the check fails
  itself.

The library side has the same treatment: **TS-3** runs eight threads
each compiling its own pattern through `pcrec_compile()` concurrently,
byte-matching a single-threaded baseline, also TSan-instrumented and
also sabotage-validated. So `pcrec_compile()` is safe to call
concurrently too, which §8 assumes and this is the evidence for.

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
    unsigned      engine;          /* 1 = DFA, 2 = VM. The artifact
                                       spells these ENGM_DFA/ENGM_VM in
                                       a COMMENT only — no such constant
                                       is #defined anywhere, so compare
                                       against the numbers */
    int64_t       step_budget;     /* -1 = none */
    int64_t       work_budget;     /* -1 = none; the THIRD bound (D47
                                       SECOND ADDENDUM): forward work the
                                       fail label never sees, counted
                                       separately from step_budget */
    int64_t       frame_capacity;  /* -1 = unbounded. NOTE the sentinel
                                       is NOT the one the same-named
                                       pcrec_options field uses — see
                                       the asymmetry note below */
    int64_t       subject_ceiling; /* 0 = unset/not applicable; else the
                                       stamped honest ceiling for a
                                       residually-unbounded capture body */
    const char           *pattern;      /* source pattern text, as given
                                            to pcrec_compile() */
    size_t                pattern_len;  /* companion length — see §7 */
    const rx_group_entry *groups;       /* NULL until named-groups; the
                                            sort key is not yet fixed —
                                            see below */
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
refuses with `requires module 'named-groups'`). **The `groups` array is
described as sorted and `bsearch`-able, but no document states the sort
KEY**, and there is no producer to measure: a consumer must not assume
an ordering today. Module `named-groups` fixes the key when it ships,
and this section states it then.

**Two more reflection facts are weaker than they look**, and the
difference from a shipped guarantee matters to anyone writing code
against them:

- **`rx_ctx.ncap`'s "watermark mid-match" reading has no producer.**
  (It is an `rx_ctx` field rather than an `rx_info` one, but it belongs
  with these.) Every call site in every emitted artifact sets
  `ctx.ncap = 0`; nothing ever advances it, so no caller can observe a
  watermark. It is reserved for a future mid-match view, exactly as
  `nnames`/`groups` are reserved for `named-groups`.
- **`rx_info.abi` is `2` on every artifact today, and is not yet a
  compatibility promise.** Being pre-v1 (§9), it is a layout version and
  nothing more: do not build version negotiation on it until v1 declares
  what a bump means.

**`frame_capacity`'s sentinel asymmetry.** The field name appears on
both sides of the API with different sentinels, and neither side is
wrong — they answer different questions. On the INPUT side,
`pcrec_options.frame_capacity == 0` means "let the compiler size it"
(and a positive value is a request). On the OUTPUT side,
`rx_info.frame_capacity == -1` means "no bound at all" — which is what a
DFA artifact stamps, having no resume stack to bound (measured:
`.frame_capacity = -1` alongside `.step_budget = -1` and
`.work_budget = -1` on a `--no-captures` build). `0` is not a legal
output value and `-1` is not a legal input value. §8 restates this at
the options side.

### 6.1 `rx_info` is link-time, not runtime, data

It is **not** part of `rx_ctx` or any callback parameter — a caller
reads `<prefix>_info` by symbol, once, at whatever point it wants the
artifact's own facts about itself (option flags, which engine, the
budgets it was built with, its own source pattern text). Its section
placement is `.data.rel.ro.local` rather than `.rodata`, for the reason
§3.4 measures.

### 6.2 Second-count example, worked

`'a(b|c)+d'` compiled `--no-captures`: `ncaps=1, ngroups=1` — the pattern
*has* a group, the artifact delivers no slot for it, and a reader who
only checked `ncaps` would wrongly conclude the pattern has no groups at
all. The two facts coincide only when `ncaps - 1 == ngroups`, i.e. a
VM-compiled, captures-on artifact — the common case since M4.5, not a
rule `rx_info` restates for every build.

### 6.3 The compile-time mirror: observability macros

An artifact also carries compile-time macros, for a caller that wants to
`#if` on a fact rather than read a struct field at run time — D46's
"every strategy selection point must be observable" requirement. Two
scoping facts first, because both are easy to get wrong and neither is
guessable:

**The mirror is PARTIAL — on a VM artifact six of `rx_info`'s fifteen
fields have a macro, and nine do not.** The six that mirror are `ncaps`
(`<PREFIX>_NCAPS`), `engine` (`<PREFIX>_ENGINE`, as the string `"vm"`),
`engine_why` (`<PREFIX>_ENGINE_WHY`), `step_budget`
(`<PREFIX>_STEP_BUDGET`), `work_budget` (`<PREFIX>_WORK_BUDGET`) and
`frame_capacity` (`<PREFIX>_BT_FRAMES`). The nine with no macro at all
are `abi`, `flags`, `encoding`, `ngroups`, `nnames`, `subject_ceiling`,
`pattern`, `pattern_len` and `groups` — including `ngroups`, which is
exactly the count §6.2 works hardest to distinguish from `ncaps`, and
which is therefore reachable only by reading `<prefix>_info` at run
time.

**On a DFA artifact the mirror is thinner still: `ncaps` alone.** A
`--no-captures` build defines exactly `<PREFIX>_NCAPS`,
`<PREFIX>_UNSET`, the four `<PREFIX>_ERR_*` codes, and the two
`<PREFIX>_ALTCLS_*` stamps below — no `<PREFIX>_ENGINE`, no budgets, no
`_VM_*` axis at all. A consumer that `#if`s on `<PREFIX>_ENGINE` is
writing code that does not compile against half the artifacts pcrec
produces. (Both counts measured by listing every `#define` in a fresh
build of each kind.)

**The macros live in the `.c`, not the `.h`.** In the split form the CLI
produces by default, a consumer `#include`s the `.h` — which carries
only `<PREFIX>_NCAPS`, `<PREFIX>_UNSET` and the four `<PREFIX>_ERR_*`
codes (plus its two include guards). Every macro named below is emitted
into the `.c` only (measured on one build: eight `#define`s in the `.h`,
thirty-five in the `.c`), so **the `#if` use case above is unreachable
from a consumer translation unit unless the artifact was built
self-contained** (`header_name == NULL`) or the consumer is the
generated `.c` itself. Whether these should also be emitted into the
header is an open design question, not settled here.

With that scoping, the observability macros on a captures-default build
of `'a(b|c)+d'` (the `#define` lines are the artifact's; the `/* ... */`
annotations below are this document's, not emitted text):

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

These are scalar macros for a per-artifact-wide verdict
(`RX_ENGINE`, `RX_VM_PREFILTER`, `RX_VM_PRUNE_CEILING`) or a bitmask
when the axis is decided per-quantifier and a single scalar would
misreport a mixed pattern (`RX_VM_RUNGS`, `RX_VM_STRATS`,
`RX_VM_PRUNES`). Everything above is VM-artifacts-only. Two more D46
stamps are NOT, and a DFA-only artifact carries them too:

```c
#define RX_ALTCLS_MERGES   1   /* alternation runs merged into one class */
#define RX_ALTCLS_FACTORED 0   /* alternation runs prefix-factored */
```

They are emitted before either engine is built, so they appear on a
capture-free pattern's DFA artifact as well (measured on a
`--no-captures` build).

**`rx_info.flags` and these macros answer different questions, and the
masking rule applies to only one of them.** `flags` records the REQUEST
— the `PCREC_*` option bits exactly as compiled — with the
testing/tuning denials masked OUT, because an axis that changes no
answer must not make two identically-behaving artifacts differ in their
reflection surface. The macros record what the emitter DID, and they
visibly move when a denial is exercised: measured on
`'(x)(?:a|bc)+d'`, building `-fno-possessify` moves `RX_VM_STRATS` from
`0x1u` (POSSESSIVE) to `0x2u` (BACKTRACKING) while the emitted
`rx_info.flags` value is unchanged — the whole `rx_info` initializer is
identical between the two builds except `frame_capacity`, which moves
because denying possessification really does cost a frame. So: to see
what was ASKED FOR, you cannot use `flags` for a masked axis at all; to
see what HAPPENED, read the macro.

The set of bits that get masked, and the per-flag reasoning, live in
`lib/pcrec.h`'s own comments (`lib/CLAUDE.md` indexes them) — that is
where to look, from here and from §8, to see which bits legitimately
vanish from `rx_info.flags` on a round trip. This document does not
duplicate that catalogue.

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

**`rx_info.pattern_len` is the detectability instrument for this gap,
and reaching it costs more than reading a field.** It reports the
*actual* byte count `pcrec_compile()` saw and compiled — the truncated
count, not the caller's intended count. But `rx_info` lives in the
GENERATED ARTIFACT, and `pcrec_compile()` hands its caller C source
text, not a struct: at compile time the only way to read `pattern_len`
is to string-search `out.c_src` for the emitted `.pattern_len = N,`
line, and the only way to read it as a value is to compile and link the
artifact first. Neither is a check a caller will write by accident.

**The one-line pre-flight is cheaper and is what a caller should
actually do.** If you know the pattern's true length independently —
and a caller handling untrusted or NUL-bearing pattern text does — test
it before compiling:

```c
if (strlen(pattern) != known_length) { /* the pattern contains a NUL:
                                          refuse it yourself */ }
```

That catches the truncation before it happens, using only the standard
library. `pattern_len` remains the after-the-fact instrument for an
artifact you already have. Verified: compiling the byte-built 3-byte
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
NUL-containing pattern source must run the `strlen` pre-flight above
itself; nothing in `pcrec_compile()`'s signature enforces that.

---

## 8. The library entry: `pcrec_options`, `pcrec_output`, `pcrec_error`

### 8.0 A complete compile, start to finish

This is the whole calling sequence, and it compiles and runs exactly as
written (verified: built with `gcc -Wall -Wextra -Werror` against
`lib/pcrec.h` and `libpcrec.a`, run, and its `matcher.c`/`matcher.h`
output compiled in turn):

```c
#include <stdio.h>
#include "pcrec.h"

int main(void)
{
    pcrec_options opt;
    pcrec_output  out;
    pcrec_error   err;

    /* MANDATORY first step: a zero-initialized pcrec_options has
       prefix == NULL and every compile fails with "invalid symbol prefix". */
    pcrec_default_options(&opt);
    opt.header_name = "matcher.h";   /* NULL (the default) = self-contained .c */

    if (pcrec_compile("a(b|c)+d", &opt, &out, &err) != 0) {
        fprintf(stderr, "pcrec: %s (at byte %zu of the %s)\n", err.msg, err.pos,
                err.input == PCREC_ERR_INPUT_PATTERN ? "pattern" : "template");
        return 1;
    }

    /* out.c_src and out.h_src are malloc'd, NUL-terminated C source and are
       the CALLER's to free from here on. h_src is non-NULL exactly when
       opt.header_name was set. */
    FILE *c = fopen("matcher.c", "w");
    if (c) { fputs(out.c_src, c); fclose(c); }
    if (out.h_src) {
        FILE *h = fopen("matcher.h", "w");
        if (h) { fputs(out.h_src, h); fclose(h); }
    }

    pcrec_output_free(&out);   /* frees both buffers, NULLs both fields */
    return 0;
}
```

Four things in it are contract, not style:

1. **`pcrec_default_options()` is mandatory, and skipping it fails every
   compile.** It is not a convenience that fills in tasteful defaults
   over a working zero state: a zeroed `pcrec_options` has
   `prefix == NULL`, and pcrec refuses a NULL prefix. Measured — a
   `memset`-zeroed options struct returns `-1` with
   `err.msg == "invalid symbol prefix (must be a C identifier, <= 60
   chars)"` for a pattern that compiles fine after
   `pcrec_default_options()`. It sets `prefix = "rx"`,
   `encoding = PCREC_ENC_BYTE` and `header_name = NULL`, and zeroes
   everything else; override fields after calling it, never instead.
   (Re-measured for this revision by printing every field of a
   default-initialized struct: `prefix=rx`, `encoding=0` — which is
   `PCREC_ENC_BYTE` — `header_name=NULL`, `flags=0`, `engine=0`.)
2. **`pcrec_output` owns two heap buffers and the caller frees them.**

   ```c
   typedef struct {
       char *c_src;   /* malloc'd; free with pcrec_output_free */
       char *h_src;   /* malloc'd, or NULL when options.header_name == NULL */
   } pcrec_output;
   ```

   `pcrec_output_free()` frees both and NULLs both fields (measured
   before and after), so it is safe to call twice and safe on a struct
   whose `h_src` was never produced. There is no other way to release
   them. §5.2's "no allocation, no lifecycle to manage" is a statement
   about the MATCH path only; the compile path allocates and this is its
   lifecycle.
3. **`h_src` is non-NULL exactly when `header_name` was set** (measured
   both ways). Do not test `header_name` and assume; test `h_src`.
4. **Check the return value, not the error struct.** `pcrec_compile()`
   returns `0` on success and `-1` on failure, and fills `err` only on
   failure.

### 8.1 What `pcrec_compile()` guarantees its caller (D56)

pcrec is a library, and two of its promises exist because a library
cannot behave like a program:

- **It never `abort()`s the caller on the compile path.** Every
  allocation site routes failure through the internal `ctx_nomem()` and
  comes back as a normal `-1`-with-diagnostic return, so a caller that
  sets a memory limit precisely in order to survive a hostile pattern
  does survive it. Two `abort()`s remain in the code deliberately and
  neither is an allocation failure: a "cannot happen" DFA structural
  invariant, and the syntax-dump path's detached string buffers, which
  run outside a compile and have no `pcrec_error` to report through.
- **A pattern can be REFUSED for compile-side RESOURCE reasons, and
  that is a distinct failure class from a syntax error.** It arrives
  through the same `-1` and the same `pcrec_error`, so a caller
  distinguishes them by reading `err.msg`, not by the return value.
  Measured at the D56 boundary (re-measured for this revision): `a{9795}`
  compiles, `a{9796}` returns `-1` with `err.msg == "pattern too complex
  for the DFA engine (subset construction exceeds 48000000 state-set
  elements; try --engine=vm)"`. The pattern is perfectly legal PCRE; what
  failed is that compiling it would cost more than pcrec is willing to
  spend. A caller that reports every `-1` as "bad regex syntax" to its
  user will be wrong here. **The escape the diagnostic names is real and
  was measured, not assumed**: the same `a{9796}` compiles cleanly under
  `--engine=vm`, because that mode never builds the DFA whose cap this
  is. (Until [M5-SEAM] this message ended "VM engine arrives in M4" — a
  promise about a milestone that had already shipped, which sent a reader
  looking for a future release instead of at a flag they already have.)

### 8.2 The option and error structures

```c
typedef struct {
    const char *prefix;      /* C identifier prefix; default "rx" */
    int         encoding;    /* PCREC_ENC_* ; PER-COMPILE-CALL, see below */
    uint64_t    flags;       /* PCREC_CASELESS | PCREC_EMIT_MAIN |
                                 PCREC_NO_CAPTURES | ... (see lib/pcrec.h
                                 for the full, growing bit catalogue) */
    const char *header_name; /* NULL = self-contained .c */
    int         engine;      /* PCREC_ENGINE_AUTO / _DFA / _VM */
    int64_t     step_budget; /* PCREC_STEP_BUDGET_DEFAULT / _NONE, or a count */
    int64_t     work_budget; /* PCREC_WORK_BUDGET_DEFAULT / _NONE, or a count */
    int         unroll_k;    /* PCREC_UNROLL_K_DEFAULT (0) = built-in default */
    int         frame_capacity; /* 0 = let the compiler size it. NOT the
                                    same sentinel as rx_info's field of the
                                    same name, which uses -1 for unbounded */
} pcrec_options;
```

**`encoding` is a PER-COMPILE-CALL scalar** ([M5-SEAM], D58): one encoding
per `pcrec_compile()` call, carried in this field and nowhere else. There is
no process-global, no file-global and no environment variable, so mixing
encodings inside one compilation unit or one binary is supported by
construction — each artifact is self-contained, carries its own prefix, and
embeds exactly one encoding's residual block (§3.1.1). The CLI spells it
`-e NAME` or `--encoding=NAME`.

`PCREC_ENC_BYTE` (0, the default) is the only encoding implemented; the
value is what `rx_info.encoding` reports (§6). `PCREC_ENC_UTF8` (1) is a
recognised NAME with no backend: `pcrec_compile()` refuses it with
`err.msg == "encoding 'utf8' arrives with milestone M5 (an engine axis, not
a module: no --features name enables it)"`, and any other value is refused
with `"unknown encoding (want byte, utf8)"`. Both refusals are ordinary
`-1`-with-diagnostic returns and write no C.

**`PCREC_ENC_BYTE` was spelled `PCREC_ENC_ASCII` before [M5-SEAM]**, and
`-e ascii` was the CLI value. It is a RENAME, not an alias — `-e ascii` is
now an unknown encoding — taken under §9's pre-v1 posture as one announced
boundary. The reason is that the old name asserted something false about
the semantics: this encoding treats every byte as a character, `0x80`-and-up
included, with no case and no meaning attached, which is precisely what
"ASCII" does not say. D58's own ruling text names the encoding `byte`.

Every boolean option (`PCREC_CASELESS`, `PCREC_EMIT_MAIN`,
`PCREC_NO_CAPTURES`, and the strategy-denial/force flags in `lib/
pcrec.h`) is one representation end-to-end: the same bit set by a CLI
flag, carried in `pcrec_options.flags`, and reflected verbatim (where not
deliberately masked, §6.3) in the compiled artifact's `rx_info.flags`.
`PCREC_NO_CAPTURES` recovers the pre-captures-default pure-DFA artifact
(`<PREFIX>_NCAPS 1`); captures are on by default since M4.5.

**A caller that round-trips its own flags through `rx_info.flags` will
find some bits missing, legitimately.** The masked ones are the
testing/tuning axes that change no answer (§6.3); which bits those are,
and why each is masked, is documented per-flag in `lib/pcrec.h`'s own
comments, which is the place to look — this document does not duplicate
that catalogue.

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
struct field name, never a bare CLI flag spelling — with the one stated
exception §1 records: the per-artifact `PCREC_FEATURE_SET` /
`PCREC_FEATURE_MODULES` stamps, which carry the `PCREC_*` spelling
without living in `lib/pcrec.h`. `PCRE2_*` spellings
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
