# Lens 9 — public-surface tightness

**Lane** `lens9pub` (opus, read-only: nothing under `src/`, `cli/`, `lib/`,
`tests/`; no `make`, no build, no suite run).
**Charter** `docs/dev/reviews/code_review_criteria_draft.md` (RATIFIED
2026-09-17), lens 9.
**Branch point** `7d444f9e` (`main`).
**Binary/archive measured** `build/pcrec` and `build/libpcrec.a` as found in
the main worktree, built 2026-09-16 13:15 — **after** the last commit touching
`src/`/`cli/`/`lib/` (`cf0962e3`, 2026-09-17 10:23 is a *docs+src* merge;
`git log --since="2026-09-16 13:00" -- src/ cli/ lib/` lists the `[OPT-DIAL]`
train, so the archive predates `tune.c`). `ar t build/libpcrec.a` shows **47**
members and no `tune.o`. **Consequence stated up front**: the symbol census in
§2 is one object short. `tune.c` defines `pcrec_tune_*`-style symbols under the
`pcrec_` prefix (checked by grep, not by `nm`), so it cannot change §2's
headline — the finding is about *unprefixed* symbols in `arena.o`/`sb.o`/
`nfa.o`/`compile.o`, all of which are in this archive. The exact export **count**
(259) is therefore a floor, and I say so wherever I use it.

---

## 0. Summary of findings

| # | Finding | Severity | Effort | Blast radius |
|---|---|---|---|---|
| **P1** | `libpcrec.a` exports **12 symbols with no namespace prefix at all** (`arena_alloc`, `sb_puts`, `ctx_fail`, …). A consumer with its own `arena_alloc` or `sb_puts` **fails to link** — reproduced. | CORRECTNESS-RISK (consumer-side, loud) | CROSS-CUTTING | 1,652 source sites / 12 names; 26 test files incl. 8 sabotage rows |
| **P2** | `lib/pcrec.h:26` tells every reader `PCREC_ENC_UTF8` is "not yet implemented (arrives with milestone M5)". Measured: `-e utf8` compiles, exit 0. R29's exact class, in the same file R29 fixed. | CORRECTNESS-RISK (documentation) | MECHANICAL | 1 file, 0 checks |
| **P3** | `docs/spec/match_api.md` §8.2 quotes `pcrec_options` with **9 members**; the shipped struct has **19**. `docs/spec/tuning.md` §4 cites §8.2 as stating "the struct itself in full". | MAINTAINABILITY | MECHANICAL | 2 spec files, 0 checks |
| **P4** | The public header's contract names **11 limits constants a library consumer cannot read**, and the only way to learn a raise-only default is to trigger the refusal and parse its prose. `pcrec_limits_tsv` is exported and undeclared. | MAINTAINABILITY | LOCAL | 1 header + 1 spec hunk |
| **P5** | `PCREC_*` is one flat namespace holding **47 contract names and 113 internal-only names** with no lexical divider — and the internal half is what the public header's own prose cites. | MAINTAINABILITY | DESIGN-EVENT | tree-wide |
| **P6** | The rx_info-mask / axis catalogue has **three homes**, and `match_api.md` §8.2 delegates it *to the source comment* — a D80 inversion. | MAINTAINABILITY | LOCAL | 1 spec hunk |
| **P7** | 7 sites in the header spell an emitted constant at the **default prefix** (`RX_NCAPS` ×5, `RX_PUSH`, `RX_SET`) inside generic contract prose that uses `<PREFIX>_`/`<prefix>_` at 58 other sites. | POLISH | MECHANICAL | 1 file, 0 checks |
| **P8** | `lib/pcrec.h:883-885` says the warn default is "an order of magnitude under `PCREC_MAX_EMIT_BYTES`". It is 4×, and it was 4× at the commit that wrote the sentence. | POLISH | MECHANICAL | 1 file, 0 checks |

**Nothing here is an engine defect.** Every finding is in the boundary
between what pcrec *declares*, what it *exports*, and what its specs *say*
about both.

---

## 1. Symbol-level: what `lib/pcrec.h` actually declares (audit Q1)

### 1.1 The census

`lib/pcrec.h` is **1,072 lines**. Preprocessed (`gcc-16 -E -P`) and stripped
of the two system headers it includes, its entire declarative content is
**98 lines** — every enum on its own line, both structs fully expanded:

| kind | count | names |
|---|---|---|
| enum constants | 45 | 2 `PCREC_ENC_*`, 26 `flags` bits, 1 `PCREC_UNROLL_K_DEFAULT`, 5 `PCREC_VM_ENTRY_*`, 5 `PCREC_TUNE_*`, 1 `PCREC_ENGINE_AUTO`, 2 `PCREC_STEP_BUDGET_*`, 2 `PCREC_WORK_BUDGET_*`, 2 `PCREC_ERR_INPUT_*` (in a named enum) |
| `#define`s | 2 | `PCREC_ENGINE_DFA`, `PCREC_ENGINE_VM` (+ the `PCREC_H` guard) |
| types | 4 | `pcrec_options`, `pcrec_err_input`, `pcrec_error`, `pcrec_output` |
| functions | **3** | `pcrec_default_options`, `pcrec_compile`, `pcrec_output_free` |

**Roughly 900 of the header's 1,072 lines are comment** (the 98 declarative
lines re-formatted; the balance is comment plus blank). `tools/review/out/
churn_hotspots.tsv:12` prices the consequence: `lib/pcrec.h 1072 46 1165 94
1259 49312` — 46 touches, 1,165 lines added against 94 removed. The file is
**append-mostly**: each wave writes a new 30-to-60-line block and almost
nothing is ever taken out. That is the mechanism behind P2, P7 and P8, and it
is why P5 is a DESIGN-EVENT rather than a tidy-up.

### 1.2 Classification: contract vs. leaked internal

**Nothing in this header is a leaked internal type or helper.** I looked
for the usual shapes — an internal struct exposed to size a caller's buffer,
a helper declared "for testing", an opaque handle with its layout visible —
and found none. The four types are the four a caller passes or receives.
The three functions are the whole compile lifecycle. `src/` declares its
own surface in `src/core/internal.h`, which *includes* `pcrec.h`
(`internal.h:10`) rather than re-declaring anything from it, so the
duplication hazard audit Q4 asks about is closed **by construction**, not by
care. See §4.1.

The interesting classification question is not "what leaked in" but **"what
is this surface FOR"**, and the flag enum answers it in a way worth stating:

| flags bits | count | what a consumer does with them |
|---|---|---|
| `PCREC_CASELESS`, `PCREC_EMIT_MAIN`, `PCREC_NO_CAPTURES` | 3 | genuine user features |
| `PCREC_TRACE` | 1 | debugging axis (the header: *"never the default: a traced artifact writes to stderr"*) |
| `PCREC_NO_*` / `PCREC_FORCE_*` | **22** | strategy denial/force axes |

The header says of the first of the 22, in its own words
(`lib/pcrec.h:55-56`): *"A TESTING AND TUNING AXIS, not a user feature."*
**So 22 of the 26 bits in pcrec's public options word exist so the project's
own differentials can deny a strategy and compare.**

**I am not filing that as a finding, and A1 is why.** D46 rules
controllability an obligation of every optimization axis; D47.3 rules the
DENY spelling; `docs/spec/tuning.md` §2 is their ruled contract with a section
per axis. A finding of the form "these should be private" contradicts three
ruled rows and I have no argument that beats them: a strategy that cannot be
denied cannot be differentially tested, and a denial reachable only from a
private header is a denial the CLI cannot spell either. I record the
classification because it is the honest shape of the surface and because it
makes §1.3's real question askable.

### 1.3 What the library use case actually needs

Lens 6 answered the *link* half directly and I cite rather than re-run it
(`worktrees/lens6dep/docs/dev/reviews/lens_reports/lens6_dependency_rxt_cut.md`
§1.2, arm 1): a consumer written to `match_api.md` §8.0 — the three functions
and nothing else — links and emits 47,649 bytes of C. The declared surface is
sufficient and no part of it is dead weight at link time.

The **gap** is elsewhere, and it is P4: six of the 19 `pcrec_options` fields
are RAISE-ONLY caps whose contract is *"0 means the built-in default, and a
value below the built-in default is refused as a malformed option"*
(`lib/pcrec.h:811-819`, `:834-853`). A library consumer that wants to raise a
cap must first know what it is raising **from** — and this header declares no
constant for any of them. §5.1 measures what that costs.

---

## 2. Link-level: what `libpcrec.a` exports (audit Q2)

### 2.1 The count

```
$ nm -g build/libpcrec.a | awk '$2 ~ /^[TDBSC]$/ {print $3}' | sort -u | wc -l
259
```

**259 exported definitions against 3 declared in the public header** (a
floor — see the pin note, `tune.o` is absent from this archive). Lens 6
reached the same shape from the header side (*"the three functions
`lib/pcrec.h` actually exports … the header declares no others"*); this is
the archive side of it.

246 of the 259 carry the `pcrec_` prefix. One, `PCREC_DEFAULT_FEATURES`,
carries `PCREC_` — see §3.2. The remaining **12 carry no prefix at all**:

```
arena_alloc   arena_free
ctx_fail      ctx_nomem
nfa_has_asserts  nfa_has_bot  nfa_wrap_unanchored
sb_free  sb_printf  sb_putc  sb_puts  sb_take
```

### 2.2 P1 — the collision is real, and I measured it

These are not obscure names. `arena_alloc` and `sb_puts` are what a C program
that has an arena allocator and a string builder would independently call its
own. Every one of them lives in an archive member a matcher-only consumer
already selects (`arena.o`, `sb.o`, `nfa.o`, `compile.o` — lens 6 arm 1 finds
44 of 48 members pulled, and the four absentees are the `*_dump.o`). Lens 6's
archive has 48 members where mine has 47, which is exactly the `tune.o` my pin
note predicts and is an independent confirmation of that pin rather than a
disagreement.

**Transcript** (the `match_api.md` §8.0 consumer, plus two functions of its
own, named without any knowledge of pcrec's internals):

```c
#include <stdio.h>
#include "pcrec.h"
void *arena_alloc(void *a, unsigned long n) { (void)a; (void)n; return 0; }
int   sb_puts(void *sb, const char *s)      { (void)sb; (void)s; return 0; }
int main(void) {
    pcrec_options opt; pcrec_output out; pcrec_error err;
    pcrec_default_options(&opt);
    if (pcrec_compile("a(b|c)+d", &opt, &out, &err) != 0) return 1;
    printf("emitted %zu bytes\n", __builtin_strlen(out.c_src));
    pcrec_output_free(&out);
    return 0;
}
```

```
$ gcc-16 -O2 -I<repo>/lib -o collide collide.c <repo>/build/libpcrec.a
duplicate symbol '_arena_alloc' in:
    …/ccneKtAP.o
    <repo>/build/libpcrec.a[2](arena.o)
duplicate symbol '_sb_puts' in:
    …/ccneKtAP.o
    <repo>/build/libpcrec.a[5](sb.o)
ld: 2 duplicate symbols
collect2: error: ld returned 1 exit status          # exit 1
```

**A1 — the ruled record.** D38's addendum, resolved the same session, is
unambiguous: *"The native surface is uniformly `PCREC_*` for every flag …
One canonical namespace (PCREC_*), one compat aliasing surface (PCRE2_*)."*
That ruling is written about flag *constants*, so it does not literally
govern a linker symbol — but it is the project's stated namespace posture and
these 12 names are outside it in the most consequential way a name can be.
I found no D-row, design section or panel disposition that rules on the
LINKER namespace of a static archive, in either direction. So this is a gap
in the ruled record, not a contradiction of it, and it is the one finding in
this report I would put in front of Frank rather than fold into a wave.

**The failure is loud**, which is why the severity is CORRECTNESS-RISK rather
than a blocker: the consumer's build breaks at link time with an exact name.
Nothing silently miscompiles. But it breaks for a consumer who did nothing
wrong, and the workaround (rename *your* function) is the wrong party paying.

**Two candidate fixes, priced.**

*(a) Rename the 12.* Mechanical per site, cross-cutting by count:

| name | source sites | files |
|---|---|---|
| `sb_printf` | 569 | 12 |
| `sb_puts` | 396 | 12 |
| `ctx_fail` | 249 | 30 |
| `arena_alloc` | 195 | 26 |
| `sb_putc` | 133 | 8 |
| `nfa_wrap_unanchored` | 27 | 11 |
| `arena_free` | 26 | 9 |
| `sb_take` | 18 | 8 |
| `ctx_nomem` | 16 | 11 |
| `sb_free` | 13 | 4 |
| `nfa_has_bot` | 8 | 5 |
| `nfa_has_asserts` | 2 | 2 |
| **total** | **1,652** | |

A `#define`-shim would be the cheap version and is the *wrong* version — it
leaves the linker symbol unchanged, which is the entire problem.

*(b) Localize at archive-build time.* A Makefile post-step that localizes
every symbol except the three (`ld -r` + `-unexported_symbol` on darwin;
`objcopy --localize-symbol`/`--keep-global-symbol` on GNU) fixes all 256
non-public exports at once and costs zero source edits — but it is
per-platform build machinery in a project whose D2 ruling is *plain GNU make
on purpose*, and it would need its own check. It is the better *end state*
and the worse *next step*.

**Recommendation:** (a) restricted to the 12, as its own wave. `pcrec_`-
prefixed symbols are a real namespace-pollution issue too, but `pcrec_arena_
alloc` colliding with a consumer's symbol is a risk nobody has; `arena_alloc`
is a risk I just reproduced.

### 2.3 A3 — check-coupling for P1

`grep -rlw` over `tests/` for the 12 names:

- **`ctx_fail`: 26 test files**, of which **8 are sabotage rows** —
  `S64_prefilter_force_refusal.sh`, `S130_look_ignores_behind.sh`,
  `S160_revdet_reverses_call.sh`, `S165_prefilter_on_call.sh`,
  `S169_postresolve_pass_deleted.sh`, `S170_deferred_recheck_never_refuses.sh`,
  `S176_prefilter_for_a_linked_call.sh`, `S223_pinned_assert_routing_call_
  deleted.sh`. Each plants or greps text containing the identifier; a rename
  re-aims all eight, and per BOILERPLATE a re-anchor needs its intent
  re-verified, not just its string updated.
- `arena_alloc` 2, `sb_puts` 3, `nfa_has_bot` 1 test file each.
- Non-sabotage checks binding `ctx_fail` include
  `tests/reject/run_reject_tests.sh`, `tests/parse/run_parse_tests.sh`,
  `tests/cli/run_cli_tests.sh`, `tests/codegen/run_cpset_structure.sh`,
  `tests/codegen/run_search_pinned.sh`, `tests/harness/run.sh`,
  `tests/registry/registry_check.c`, `tests/thread/ts3_driver.c` and four
  `CLAUDE.md` file lists.

**A wave that renames `ctx_fail` carries eight sabotage re-aims and their
re-verification.** That is the single largest item in the price, and it is
why I would do the wave name by name rather than all twelve at once — the
three `nfa_*` names cost 37 sites and one test file between them and could
land first as the pattern.

---

## 3. Prefix discipline (audit Q3)

### 3.1 `PCRE2_*` — clean

Four occurrences in `lib/pcrec.h` (`:30`, `:583`, `:584`, `:598`), every one
a *reference to PCRE2's own name* inside prose (`PCRE2_CASELESS`,
`PCRE2_UTF`, `PCRE2_ERROR_BADUTFOFFSET`, `PCRE2_MATCH_INVALID_UTF`). **Zero
native declarations under the `PCRE2_` prefix, anywhere in the public
header.** D38's addendum is honoured exactly. Held, not a finding.

### 3.2 `PCREC_*` — P5, one namespace, two populations

| population | count |
|---|---|
| `PCREC_*` tokens appearing in `lib/pcrec.h` | 68 |
| … of which **declared** there | **47** (45 enum members + 2 `#define`s) |
| … referenced in its comments but declared elsewhere | 21 |
| `PCREC_*` names across `src/` + `cli/` | 175 |
| **internal-only** (`src/`/`cli/`, never in the public header) | **113** |

So `PCREC_` names **47 contract constants and 113 internal ones** with no
lexical distinction between them. The 113 include all 58 `limits.def` rows
(`PCREC_MAX_EMIT_BYTES`, `PCREC_MAX_SUBSET_ELEMS`, `PCREC_DEFAULT_UNROLL_K`,
…) plus `internal.h`'s own `PCREC_UNBUILT_MARKER`, `PCREC_RXT_WAVE_BUILT`,
`PCREC_W_UNBOUNDED`, `PCREC_MINW_MAX`.

**What makes this a finding rather than an observation** is that the two
populations are not merely adjacent — they are *cross-referenced*. The
public header's contract prose cites 11 of the internal names as if the
reader had them (§5.1). A reader cannot tell from a `PCREC_` name whether it
is something they can `#include "pcrec.h"` and use, or something that exists
only inside the compiler.

**A1**: `docs/spec/match_api.md` §8.2 states the naming rule and I quote it
because it is narrower than one might expect —

> `PCREC_*` names only pcrec's own enum/bit-valued constants — never a
> struct field name, never a bare CLI flag spelling — with the one stated
> exception §1 records: the per-artifact `PCREC_FEATURE_SET` /
> `PCREC_FEATURE_MODULES` stamps, which carry the `PCREC_*` spelling without
> living in `lib/pcrec.h`.

The sentence enumerates its exceptions **exhaustively** ("the one stated
exception"). Measured against the archive, there is a second one:

```
$ nm -g build/libpcrec.a | grep PCREC_DEFAULT_FEATURES
0000000000000950 S _PCREC_DEFAULT_FEATURES
```

`src/parse/enabled.c:112` — `const char *const PCREC_DEFAULT_FEATURES =
"std1";`, declared at `src/core/internal.h:4385`. It is a **`const char *`
data object with external linkage**, not an enum or bit-valued constant, and
not one of the two named stamps. §8.2's enumeration is short by one.

**Severity** MAINTAINABILITY, **effort** MECHANICAL for the spec sentence
(add the exception, or rename the object to `pcrec_default_features` and keep
the rule exhaustive — the latter is preferable and is one more name for P1's
wave), **blast** 1 spec file or 1 source file + 4 call sites.

*Rider, not a lens-9 finding, recorded because I met it:*
`cli/CLAUDE.md:125` describes `PCREC_DEFAULT_FEATURES` as *"(src/parse/
enabled.c, currently `"none"`)"*. The shipped value is `"std1"`. That is
lens 4's territory; I am naming it so it does not go unclaimed.

### 3.3 `RX_*` — P7, the emitted namespace leaking the default prefix

`RX_*` is the *emitted-artifact* namespace at the default `-p rx`, and a
generic contract statement must use `<PREFIX>_`. The header does, 58 times
(`<PREFIX>_` ×32, `<prefix>_` ×26) — and 7 times it does not:

| site | spelling |
|---|---|
| `lib/pcrec.h:39`, `:977`, `:1003`, `:1009`, `:1011` | `RX_NCAPS` (×5) |
| `lib/pcrec.h:797` | `RX_PUSH` |
| `lib/pcrec.h:798` | `RX_SET` |

The five `RX_NCAPS` sites are the sharpest, because four of them sit *inside
the generated-searcher contract block* — the same paragraphs that correctly
write `<PREFIX>_ERR_STEPS`, `<PREFIX>_RESUME_FRAMES`, `<PREFIX>_BUFFER_ALIGN`.
A caller building with `-p foo` reads at `:1009` that *"`RX_NCAPS` is 1 on any
DFA-compiled artifact"* and has no macro by that name; theirs is `FOO_NCAPS`.
`docs/spec/match_api.md` uses `RX_NCAPS` too, but it does so having declared
`rx` as the worked example's prefix; the header has not.

**Severity** POLISH, **effort** MECHANICAL, **blast** 1 file, 0 checks.
`grep -rl "RX_NCAPS" tests/` finds **69 files**, and every one is pinning the
*artifact's* macro on a default-prefix build — correct usage, unaffected by
editing a comment in `lib/pcrec.h`. The two populations share a spelling and
nothing else.

---

## 4. The `pcrec.h` / `internal.h` boundary, and prose vs. shipped (audit Q4)

### 4.1 Duplication: none, by construction

`src/core/internal.h:10` is `#include "pcrec.h"`. Every internal TU therefore
sees the public declarations through the public header and re-declares
nothing from it — I checked each of the four public types and the three
functions and found no second declaration anywhere in `src/` or `cli/`.
Lens 6's L5 measures `internal.h` as a god-header (5,522 lines, 225
declarations, 32 of them defined in `src/core/`, 52 of ~55 TUs including it);
that is a real problem and it is lens 6's, and it does **not** produce a
public-surface contradiction. **Held.**

One asymmetry is worth naming and is ruled, so I cite and hold rather than
file: `PCREC_ENGINE_AUTO` is an `enum` member while `PCREC_ENGINE_DFA`/`_VM`
are `#define`s. `lib/pcrec.h:666-684` gives the reason at length and D60's
addendum rules it — an artifact's own header `#define`s the same two names
byte-identically, and an `enum` member here would be textually rewritten into
`1 = 1,` when the artifact's header is included first (verified by that
lane against gcc). The asymmetry is the fix, not the bug.

### 4.2 P2 — the header denies a shipped encoding

`lib/pcrec.h:24-27`:

```c
enum {
    PCREC_ENC_BYTE = 0,   /* byte semantics, 8-bit clean; the default */
    PCREC_ENC_UTF8 = 1    /* not yet implemented (arrives with milestone M5) */
};
```

Measured against the shipped compiler:

```
$ build/pcrec -e utf8 -o u8.c 'a.b' ; echo "exit=$?"
exit=0
$ grep -m2 encoding u8.c
 * anchored entry points, rx_next_pos is caller-facing encoding
     * this artifact's encoding. A mid-character position is REFUSED
```

(and `-e utf8 --features all 'a\p{L}b'` gets past the encoding to an ordinary
large-artifact warning, i.e. the UTF-8 backend and `unicode-props` are both
live.)

`docs/spec/match_api.md` §8.2 says the opposite of the header, correctly:
**"Two encodings compile: `byte` (the default) and `utf8`"** ([M5.0] stage 2),
and the spec even records that *its own* earlier "byte is the only encoding
implemented today" lead was superseded. `[M5.0]` is in
`plan_completed.md`; `docs/dev/lanes/m5close_report.md` is its close-out.
**The milestone closed and the public header was not swept.**

This is **R29's precedent reproduced in the file R29 fixed**: the 2026-08-18
panel's blocker was that *both* shipped doc-comments "affirmatively deny the
give-up-code space §4 promises and the artifacts produce," one of them in
`lib/pcrec.h`. The wording R29 fixed is now correct; a *different* sentence
in the same header now denies a *different* shipped capability. The
generalisable form, and the reason I rank this CORRECTNESS-RISK rather than
POLISH: **a header comment is the only contract text a consumer reads without
being told to, so a false one in it is not a documentation defect with a
documentation blast radius — it is the surface behaving as if a feature does
not exist.**

Suggested replacement, matching §8.2's own wording:

```c
    PCREC_ENC_UTF8 = 1    /* UTF-8; a character is 1-4 bytes ([M5.0] stage 2).
                             docs/spec/match_api.md §8.2 is the contract. */
```

**Severity** CORRECTNESS-RISK, **effort** MECHANICAL, **blast** 1 file, 0
checks. `grep -rn "PCREC_ENC_UTF8" tests/` finds only uses of the *constant*
(`tests/utf8/startbnd_backend_check.c:72`, `tests/cli/run_cli_tests.sh:1635`
— the latter asserting the utf8 artifact stamps `.encoding = 1`, i.e. a
shipped check already contradicts the comment), never of this comment's text.

### 4.3 P3 — the spec's struct quotation is ten fields short (both directions checked)

The charter asks for a finding where the header and the spec disagree, "in
both directions". Here it is, and the direction is spec-is-stale.

`docs/spec/match_api.md:3319-3335` presents `pcrec_options` as a plain code
block with **no elision marker** and nine members:

```
prefix, encoding, flags, header_name, engine,
step_budget, work_budget, unroll_k, frame_capacity
```

The shipped struct (`lib/pcrec.h:710-944`, verified by preprocessing) has
**nineteen**. The ten missing:

`vm_entry_shape`, `max_emit_code_bytes`, `max_emit_bytes`, `max_nfa_states`,
`max_dfa_states_goto`, `max_subset_elems`, `max_auto_dfa_elems`,
`warn_emit_bytes`, `name`, `tune`.

Six of the ten are the `[LIM-2]` N1 / `[ART-SIZE]` raise-only caps; one is
`[OPT-4]`'s advisory warning; one is `[DD-13b.W1.2]`'s `name`; one is
`[CC-DIFF]` STEP 2's `vm_entry_shape`; one is `[OPT-DIAL]`'s `tune`.
`grep -n` over the whole of `match_api.md` for `warn_emit_bytes`,
`max_emit_bytes`, `max_nfa_states`, `vm_entry_shape`, `max_auto_dfa_elems`
and `options.tune` returns **zero rows** — the fields are not documented
elsewhere in that document either, so this is absence, not relocation.

**What makes it sharp rather than routine** is that a second spec document
cites this one as the authority. `docs/spec/tuning.md:2325-2327`:

> Which `pcrec_options` fields (`lib/pcrec.h`) correspond to which flags in
> §2. **`docs/spec/match_api.md` §8.2 states the struct itself in full;**
> this table only maps field to axis.

…and `tuning.md` §4's own last row is `| tune (PCREC_TUNE_MIN_SIZE …
_MAX_SPEED, -2..+2) | --tune=N | §5 |` — pointing a caller at a field the
document it just called authoritative does not contain. Two specs, each
correctly deferring to the other for the half it does not carry, and the
overlap is empty.

`docs/spec/CLAUDE.md` preserves the rule this breaks, in match_api.md's own
voice: *"an idealized quotation in a document whose authority is 'checked
against the shipped surface' is the failure mode the document exists to
prevent."* §8.2's block is one.

**Fix:** re-quote §8.2's struct from the shipped header (it will be ~19
commented lines), or mark the block explicitly partial and name where the
remainder lives. The former is right — the whole point of §8.2 is that
`tuning.md` §4 can say "in full" and mean it.

**Severity** MAINTAINABILITY, **effort** MECHANICAL, **blast** `docs/spec/
match_api.md` §8.2 (+ optionally a `tuning.md` §4 sentence), 0 checks — no
check in the tree compares the spec's struct against the header (see §7).

### 4.4 P6 — three homes for the mask catalogue, and the spec points at the code

`match_api.md` §8.2 says:

> **A caller that round-trips its own flags through `rx_info.flags` will find
> some bits missing, legitimately.** The masked ones are the testing/tuning
> axes that change no answer (§6.3); which bits those are, and why each is
> masked, **is documented per-flag in `lib/pcrec.h`'s own comments, which is
> the place to look** — this document does not duplicate that catalogue.

But `docs/spec/tuning.md` *does* carry it, per axis:
`grep -n "masked out of \`rx_info.flags\`\|strategy_denials"` returns 11 sites
(`:112`, `:155`, `:270`, `:343`, `:410`, `:453`, `:683`, `:763`, `:864`,
`:943`, …), each stating the mask verdict for its own axis, including the two
NOT-masked exceptions (`:410` `-fno-splice-calls`, `:453` `-fno-atomic-
discharge`) with their reasons.

So the mask catalogue lives in **`lib/pcrec.h`'s comments, `tuning.md` §2, and
`emit_dfa.c`'s `strategy_denials` array** — and the *spec* names the source
comment as "the place to look". Under D80 (`docs/spec/` is the contract, a
reviewer rejects a contract change without its spec hunk) that is inverted:
a caller is sent from the contract to a source file, and an author editing
`tuning.md` §2's mask sentence has no signal that `match_api.md` delegates
past it.

**A1 check.** I found no ruling that makes the header the mask authority.
D80 rules the opposite direction. `tuning.md`'s own charter entry in
`docs/spec/CLAUDE.md` describes it as stating per axis *"whether it is
ANSWER-IDENTITY-preserving or ENGINE-SELECTING"*, which is exactly the mask
predicate. So this is a stale sentence, not a contested design.

**Fix:** one sentence in `match_api.md` §8.2 — point at `tuning.md` §2 rather
than at `lib/pcrec.h`. The header's comments then become what they should be
(the design record beside the declaration), not a cited contract.

**Severity** MAINTAINABILITY, **effort** LOCAL, **blast** 1 spec hunk, 0
checks.

### 4.5 Spot-checks that HELD

I checked five other header prose claims against the shipped source rather
than assuming (these are §7's material, listed here because they are the
answer to "does the header's prose match shipped behavior"):

- `:249` names the splice/linkage stamps as `<PREFIX>_VM_CALL_SPLICED` /
  `_VM_CALL_LINKED`, "two counts, not one string" — matches `emit_vm.c`.
  This is the drift `docs/spec/CLAUDE.md` records as found by [SPEC-1.3] and
  fixed at `40d9f79`; it has stayed fixed.
- `:690` step budget **500,000,000** = `limits.def`'s
  `VM_DEFAULT_STEP_BUDGET, 500000000LL`. ✓
- `:706` work budget **1,000,000,000** = `VM_DEFAULT_WORK_BUDGET,
  1000000000LL`. ✓
- `:883` warn default **250,000** = `PCREC_DEFAULT_WARN_EMIT_BYTES, 250000`. ✓
- The 26 flag bits are `1u << 0` … `1u << 25`, all distinct, no gap, no
  reuse (verified from the preprocessed header, not by reading the enum).
  The two "Bit 17 is [ENG-ABS]'s" / "Bit 18 is [ART-SIZE]'s" disambiguation
  notes at `:385` and `:407` are correct.

### 4.6 P8 — the one arithmetic claim that fails

`lib/pcrec.h:883-885`:

> The default is `PCREC_DEFAULT_WARN_EMIT_BYTES` (250,000 total bytes),
> **chosen an order of magnitude under `PCREC_MAX_EMIT_BYTES`** so the line
> arrives while a pattern can still be changed rather than at the moment it
> is refused.

`PCREC_MAX_EMIT_BYTES` is **1,000,000** (`src/core/limits.def`). 250,000 is
**4×** under it, not an order of magnitude.

I checked whether this is drift — it is not. `git show 12dc1c64:src/core/
limits.h` (`12dc1c64` is `[OPT-4] --warn-emit-bytes`, the commit that wrote
the sentence) reads `#define PCREC_MAX_EMIT_BYTES 1000000` at `:672`, and its
own comment at `:664` makes the *qualitative* point without the number
("…on purpose: the point of a warning is to arrive while…"). **The claim was
never true**; the header borrowed the reasoning and added a magnitude the
source it borrowed from was careful not to state.

**Severity** POLISH, **effort** MECHANICAL, **blast** 1 file, 0 checks. Fix:
delete "an order of magnitude" (the sentence works without it) or write
"well under".

---

## 5. Stability: what a versioning story would have to freeze (audit Q5)

### 5.1 P4 — the library has no limits surface

`lib/pcrec.h`'s comments cite **21** `PCREC_*` names the header does not
declare. Discounting two historical spellings (`PCREC_ENC_ASCII`,
`PCREC_CASE_INSENSITIVE`), the include guard, two per-artifact constants that
correctly live in the emitted header (`PCREC_ERR_FRAMES`,
`PCREC_ERR_STARTPOS`), the `PCREC_RX_ABI_H` block name and three
abbreviated-in-prose stubs, **11 are limits constants a consumer is told to
reason about and cannot read**:

```
PCREC_DEFAULT_UNROLL_K            PCREC_MAX_NFA_STATES
PCREC_DEFAULT_WARN_EMIT_BYTES     PCREC_MAX_SUBSET_ELEMS
PCREC_MAX_AUTO_DFA_ELEMS          PCREC_MAX_VM_EMIT_CODE_BYTES
PCREC_MAX_DFA_STATES_GOTO         PCREC_PREFILTER_EXACT_NFA_STATES
PCREC_MAX_DFA_STATES_TABLE        PCREC_VM_INLINE_CHAIN_MAX_BYTES
PCREC_MAX_EMIT_BYTES
```

Six `pcrec_options` fields carry the contract *"0 means the built-in default;
a value below the built-in default is refused as a malformed option"*
(`:811-819`, `:834-853`). Measured, the refusal is real and the diagnostic
is the only place the number surfaces:

```
$ build/pcrec --max-emit-bytes=1000 -o r.c 'abc'; echo "exit=$?"
pcrec: --max-emit-bytes is RAISE-ONLY: 1000 is below the built-in limit of
1000000. These overrides exist to let a caller accept a larger artifact,
never to make a build refuse one it would have accepted
exit=1
```

**So a library consumer's only programmatic route to a raise-only default is
to deliberately trigger a refusal and parse English out of `err.msg[256]`.**
The CLI has `--list-limits`; the archive exports `pcrec_limits_tsv`
(confirmed in the `nm` census); `lib/pcrec.h` declares neither it nor any
constant. The data exists, is exported, and is undeclared.

**A1.** `limits.def` is the ruled central-config home (D90; the criteria doc
names it). This finding does **not** propose moving a number out of it — the
opposite: it proposes that the public header *derive* from it. `limits.def`
already carries an `override` column distinguishing `FLAG` rows (a caller can
move it per compile) from `BUILD_D` rows, so the row set that a public
surface should expose is already marked in the ruled table.

**Also relevant, cited not re-found: K9 is open.** `pcrec_compile(const char
*pattern, …)` takes no length, so an embedded NUL truncates and reports
success (`docs/dev/known_issues.md:961`). The public-surface observation
K9 does not make is that **the header says nothing about it**: the entire
doc comment on `pcrec_compile` is one line —

```c
/* Returns 0 on success (out filled), -1 on failure (err filled if non-NULL). */
```

— and `grep -ni nul lib/pcrec.h` returns 12 rows, every one about a NULL
*pointer* (`header_name`, `caps`, `h_src`, the buffers descriptor) and none
about NUL *termination*. K9's own entry offers two remedies and both begin
with documenting the rule; neither half has reached the header. That is a
one-sentence edit that does not pre-empt the API decision.

**Severity** MAINTAINABILITY, **effort** LOCAL, **blast** `lib/pcrec.h` +
`docs/spec/limits.md` hunk (D80). Two shapes, either acceptable:
(a) emit the `FLAG`-override rows as `#define`s into `pcrec.h` from
`limits.def` — generated, so it cannot drift; or (b) declare
`pcrec_limits_tsv` (it is already exported) and say so in `limits.md`.
(a) serves the raise-only contract directly; (b) is smaller and serves
introspection. I lean (a).

### 5.2 What a v1 freeze would have to pin

Stated as inventory rather than as a finding, because D40's pre-v1 posture
rules today's answer and A1 forbids arguing past it without cause:

| surface | frozen at v1? | note |
|---|---|---|
| 3 function signatures | yes | stable since [M4.4] |
| `pcrec_options` **layout** | yes | every addition since [M4.4] has been APPENDED (`name`, `tune`, the six caps) — the discipline is already being kept and is recorded per-field |
| 26 `flags` **bit values** | yes | `tests/registry/axes_registry_check.sh` already pins the bit of every `NO_`/`FORCE_` constant against `--list-axes` |
| `pcrec_error.msg[256]` | yes | a fixed-size buffer in a public struct is the least reversible thing in this header |
| the 22 denial bits' **meaning** | **no** | each is tied to a live optimization; `tuning.md` §2 is the contract and D46 makes denial an obligation, not a promise of permanence |
| 11 limits constants | not exposed | §5.1 — the freeze question cannot be asked until they are declared |

**Nothing exported is obsoleted by the `limits.def`/`tune` surfaces.** I
checked the two candidates and both are ruled live: `vm_entry_shape` vs.
`tune` is settled by `tuning.md` §5's *"explicit per-switch flags beat the
dial where a spelling exists"* (Frank, 2026-09-16), and `frame_capacity` vs.
`[DD-14.FB]`'s caller-provided buffers are different mechanisms — one sizes
the artifact's own default, the other replaces the storage.

One genuine gap, small: **`PCREC_TRACE` and `PCREC_VM_ENTRY_*` have no spec
row under their enum spellings.** `grep -c` over `docs/spec/tuning.md` and
`cli.md`: `PCREC_TRACE` 0/0, `PCREC_VM_ENTRY_AUTO` 0/0. Both have CLI
spellings that *are* documented (`--trace` at `cli.md:943`;
`--vm-entry-shape` at `tuning.md` §2.21, which even discusses `int
vm_entry_shape` at `:1778`) — so the axes are specified and only the
constants a library caller must actually type are not. `tuning.md` §4's
mirror table lists 14 of the 26 flag bits; seven tuning bits
(`NO_SIZE_TERM`, `NO_PREFILTER_COLLAPSE`, `FORCE_PREFILTER_COLLAPSE`,
`NO_SCAN_EDGE`, `NO_START_PINNED`, `NO_CLS_FOLD`, `NO_STARTPOS_GUARD`) have a
§2 section but no §4 row. Folded into P3's fix as one sweep of §8.2 + §4
rather than filed separately — it is the same append-without-sweep mechanism.

---

## 6. PROBED-AND-HELD

Negative results with the evidence behind them, so the same ground is not
re-covered.

1. **No leaked internal types or helpers in `lib/pcrec.h`.** All 4 types and
   3 functions are caller-facing. Method: preprocess the header, enumerate
   every declaration, classify each against `match_api.md` §8.0's calling
   sequence. 62 declarative lines, 0 internal.
2. **No duplication or contradiction between `pcrec.h` and `internal.h`.**
   `internal.h:10` includes `pcrec.h`; no public name is re-declared anywhere
   in `src/` or `cli/`. Checked per name for all 3 functions and all 4 types.
3. **No `PCRE2_*` native spelling anywhere in the public header.** 4
   occurrences, all prose references to PCRE2's own constants. D38's addendum
   honoured. (§3.1)
4. **No flag-bit collision, gap, or reuse.** Bits 0–25, all distinct,
   verified from the preprocessed enum rather than by reading the source.
   The two "bit N is X's" notes are correct. (§4.5)
5. **Four inline numeric constants in the header agree exactly with
   `limits.def`** — 500,000,000 / 1,000,000,000 / 250,000, plus the
   `PCREC_MAX_EMIT_BYTES` 1,000,000 that P8's ratio is measured against.
   This is worth recording because they are **unguarded**: `tests/registry/
   limits_check.sh:235` explicitly *excludes* `lib/pcrec.h`'s two budget
   sentinels from the limits-table check ("API SENTINELS (both 0) … not the
   limit value itself"), correctly, and nothing else reads the header's
   comment numbers. `grep -rn "500,000,000\|250,000\|1,000,000,000" tests/`
   finds only `run_cli_tests.sh`'s own 250,000 witness, which reads the
   *behaviour*, not the header. Four numbers currently right by care alone.
6. **The splice/linkage stamp names in the header are current**
   (`<PREFIX>_VM_CALL_SPLICED`/`_LINKED`) — the [SPEC-1.3] drift fixed at
   `40d9f79` has not recurred. (§4.5)
7. **The `PCREC_ENGINE_AUTO`-enum / `_DFA`-`_VM`-`#define` asymmetry is
   ruled and correct** (D60 addendum, `lib/pcrec.h:666-684`). Not a style
   defect; the `#define` spelling is what makes a consumer TU that includes
   both this header and an artifact's header compile at all.
8. **The declared surface is sufficient for the library use case.** Cited
   from lens 6 arm 1 rather than re-run: a consumer using only the three
   declared functions links and emits 47,649 bytes.
9. **The `-fno-*` denial bits are NOT a leaked-internal finding**, despite
   22 of 26 bits being testing/tuning axes by the header's own words. D46,
   D47.3 and `tuning.md` §2 rule them public and I have no argument that
   beats them (§1.2). Recorded so a later lens does not re-open it without
   new grounds.

---

## 7. Where this lens stopped (ADDENDUM 2)

Per the ratification addenda, the unreviewed remainder is named rather than
silently capped.

- **Covered in full**: every declaration in `lib/pcrec.h` (all 54, classified);
  every exported symbol in `build/libpcrec.a` (259, prefix-classified); the
  `PCREC_`/`PCRE2_`/`RX_` prefix populations across `src/`, `cli/`, `lib/`;
  the `pcrec.h`↔`internal.h` boundary; `match_api.md` §8/§8.1/§8.2 and
  `tuning.md` §4 against the shipped header, both directions.
- **Not covered**: (a) the **emitted** artifact's own public surface — the
  `rx_*` fixed-literal ABI types, `<prefix>_buffers`, the sizing macros and
  the `<PREFIX>_*` stamp catalogue. `match_api.md` §1/§2/§6/§10 is its
  contract and it is a second public surface of comparable size to this one.
  It deserves its own pass and I did not attempt it inside this lane's floor
  budget. (b) The other ~244 `pcrec_`-prefixed exports were classified by
  *prefix* but not individually audited for whether each needs external
  linkage at all; a `static`-ability census over them is the natural
  follow-on to P1's wave (option (b) in §2.2 makes it moot, which is an
  argument for option (b)).
- **Not attempted**: any measurement requiring a build. The archive pin is
  stated at the top and the one consequence (`tune.o` absent) is stated with
  it.

---

## 8. Recommended wave order

Ranked per A4 — MECHANICAL and safe first, DESIGN-EVENT last.

1. **P2** (utf8 comment) — one line, CORRECTNESS-RISK, 0 checks. Do it first.
2. **P8** (the ratio), **P7** (`RX_NCAPS` ×5 → `<PREFIX>_NCAPS`) — comment
   edits in the same file, 0 checks. Ride with P2 as one commit.
3. **P3 + the §5.2 rider** (re-quote `match_api.md` §8.2's struct from the
   shipped header; complete `tuning.md` §4's mirror; add `PCREC_TRACE` /
   `PCREC_VM_ENTRY_*` rows) and **P6** (§8.2's mask-catalogue pointer moves
   from `lib/pcrec.h` to `tuning.md` §2) — one spec wave, D80-shaped, 0
   checks staled.
4. **P4** (a generated `#define` block for `limits.def`'s `FLAG`-override
   rows, plus the one-sentence NUL-termination statement K9's own remedies
   both start from) — LOCAL, carries its `limits.md` hunk.
5. **P5's spec half** (`match_api.md` §8.2's exhaustive-exceptions sentence
   vs. `PCREC_DEFAULT_FEATURES`) — one sentence, or one rename that keeps the
   rule exhaustive; the rename belongs in P1's wave.
6. **P1** (the 12 unprefixed exports) — CROSS-CUTTING, 1,652 sites, 8
   sabotage re-aims. Land it name by name, `nfa_*` first (37 sites, 1 test
   file) as the pattern, `ctx_fail` last (249 sites, 8 sabotages). **The
   archive-localization alternative (§2.2b) is a Frank question, not a
   manager default** — it fixes all 256 at once and adds per-platform build
   machinery to a project whose D2 ruling is plain GNU make on purpose.
7. **P5's structural half** (separating the `PCREC_` contract namespace from
   the `PCREC_` internal namespace) — DESIGN-EVENT. Named, not proposed.
   Its measured trigger, per D77, would be a second collision or a v1
   declaration, whichever arrives first.
