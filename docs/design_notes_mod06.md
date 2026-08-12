# MOD-0.6 design note — module `unicode-props` — PHASE 1 (measurement + design, no code)

Written by the phase-1 implementation lane, against the git worktree at branch
`mod06`, HEAD `39f78f9` (MOD-0.4 close). Companion evidence:
`tests/probes/probe_uprops.c`, committed with this note.

**Disclosure** (per brief): the only context beyond this brief that entered
this work is the standard spawn-time injection — the session-root
`CLAUDE.md` (the repository-scope mandate, already restated in the brief)
and the memory index (`pcrec process preferences` / `pcrec project status` /
`pcrec check-design lessons` — none of their content was used beyond the
general working style they describe: journal/plan conventions, and "every
check this project has built has failed the same way — a control sharing a
source with what it controls," which shaped how §4/§5 below are written).
No other file, review, or conversation outside this brief and the repository
influenced this note.

---

## 0. The headline finding, stated up front because it reframes §1

**`\p`/`\P` have no DECLINE-shaped tail.** A full 256-byte sweep of the byte
immediately following the selector (`probe_uprops.c`, "(b) widened") lands
every one of the 256 bytes on exactly one of three PCRE2 outcomes —
COMPILES (14), ERR 146 "malformed \P or \p sequence" (204), ERR 147 "unknown
property after \P or \p" (38) — and never anything else. There is no byte
after `\p` that PCRE2 treats as "not an attempt at a property escape, carry
on as something else." This is unlike every other doorway this project has
built a recogniser for (`(?`, `(*`, `[[:...:]]`), all of which have a real
DECLINE case. The consequence, worked out fully in §1, is that the row's
current `recognise: NULL` / `tail: NULL` shape — "promise the module for
every tail" — which the plan flagged as *"the Q2 shape at a fourth
doorway"* and a likely tier-2 finding, is measured to be **correct** at this
doorway rather than a repeat of the Q2 bug. The Q2 bug was promising a
module for text PCRE2 does NOT dispatch on; `\p`/`\P` promise a module for
text PCRE2 DOES dispatch on, unconditionally, because there is no other kind
of text to receive.

---

## 1. The recogniser (syntax port) for `\p`/`\P`

### Function shape and location

`\p` and `\P` are each alone in their `(RK_ESC, sel)` bucket — no other row
shares selector byte `'p'` or `'P'` — so D32 §3's rule applies exactly:
*"rank only means anything between clashing recognisers... the [rows that
never clash] carry no meaningful rank."* There is nothing to arbitrate.

**The `recognise` field on both rows stays `NULL`** (default
`pcrec_recognise_tail_default` with `tail = NULL`, "always matches" —
D32 §2's honestly-answering fallback). This is not a placeholder pending
phase 2; it is the row's PERMANENT, CORRECT recogniser, because §0's sweep
establishes the doorway-level predicate is the constant function "true" —
there is no tail shape that should route away from these rows.

The **syntax port** — the body PARSER that phase 2 needs to actually read
`{...}` or a bare letter and produce a normalised name — lives in a new
`src/parse/mod_uprops.c`, following `mod_modifiers.c`'s template exactly:
the measured grammar (§3 below) and the code that implements it move
together in one file, because R8/C2-9's lesson (`(*LIMIT_*=digits`'s
description in `registry.c` drifting from its implementation in `ext.c`) is
the reason that template exists. Its signature, following the existing
`ExtPortFn` shape used by `pcrec_modport_optrun`:

    ExtResult pcrec_modport_uprops(Ctx *cx, const RegRow *rw, ExtWant want,
                                   size_t at, size_t from);

`at` is the offset to blame (the position right after `\p`/`\P`, i.e. where
`ext.c`'s `pcrec_ext_escape` already computes `at` for every escape row);
`from` is the byte position the body scan starts from (`cx->pos`, per every
other `ExtPortFn`'s convention). Not built this phase — no producer lands
(brief item 6) — but the signature is fixed now so phase 2 has no interface
decision left to make, matching how `pcrec_registry_option_run_recognise`
was specified as a marker before `pcrec_modport_optrun` existed.

### The D28 dispatch verdict per malformed-tail cell

D28's axis, restored to primary by D30 §3 ("did PCRE2 DISPATCH", not the
withdrawn CLAIM/REFUSE/DECLINE-from-one-example reading D29 tried first):

| cell | libpcre2 | D28 axis |
|---|---|---|
| `\pL`, `\p{L}` (well-formed, known name) | COMPILES | dispatched, SYN_OK |
| `\p{Foo}` (well-formed, unknown name) | ERR 147 | dispatched, dispatched-then-bad-NAME |
| `\p{^}`, `\p{^^L}` (caret shapes read as name) | ERR 147 | dispatched, dispatched-then-bad-NAME |
| `\pA`..`\pZ`/`\pa`..`\pz` minus the 14 known letters | ERR 147 | dispatched, dispatched-then-bad-NAME |
| `\p{}` (empty name) | ERR 147 | dispatched, dispatched-then-bad-NAME |
| `\p` at EOF, `\p!`, `\p9`, any non-letter/non-`{` single byte | ERR 146 | dispatched, SYN_MALFORMED (shape not even attemptable) |
| `\p{` at EOF, `\p{L` (unterminated, any content) | ERR 146 | dispatched, SYN_MALFORMED (unterminated) |
| `\p{Foo}` under `PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL` | COMPILES (as a 2-char literal) | **not dispatched under this mode** — see the bound-mode note below |

Both 146 and 147 are PCRE2-recognised-then-refused outcomes (D28's
`SYN_MALFORMED` sub-case survives inside CLAIM, exactly as D28 originally
said before D29 tried to make it the primary axis and R10 corrected that
back). **There is no `SYN_NOT` cell for `\p`/`\P` at options=0.** The
malformed-vs-unknown-name split (146 vs 147) is real and worth keeping in
pcrec's own future diagnostic text as two REFUSE messages sharing one
module, the same shape `\N`'s bare-vs-`{U+`-vs-`{name}` split already uses
— but it changes NOTHING about module attribution: every cell in the table
above names `unicode-props`.

### The CLAIM-vs-REFUSE rule, stated to cover both `\p{Foo}` and `[[:foo:]]`

> **A doorway CLAIMs (promises a module) for exactly the text shapes where
> libpcre2's behaviour is construct-specific — a compile, or an error that
> would not occur (or would occur for an unrelated reason) if the construct
> did not exist as PCRE2 syntax at all — measured over the COMPLETE tail
> byte space at the doorway's bound compile mode (R10 disposition 3).
> Everywhere else, REFUSE with no module, or (if the doorway can decline at
> all) DECLINE.**

Applied to both cases the brief names:

- **`\p{Foo}`**: measured over all 256 possible bytes after the selector,
  100% of the space is construct-specific (COMPILES/146/147, never a code
  PCRE2 would also produce for an unrelated escape). The doorway's answer is
  the constant "CLAIM", which is exactly what `recognise: NULL` already
  encodes — no change needed to reach the right answer, only the module's
  eventual implementation (out of scope, §6).
- **`[[:foo:]]`** (FIX-2's REFUSE, cited by the brief for contrast): the
  POSIX-name doorway requires seeing a *closed* `[:name:]` shape before
  PCRE2 treats the text as an attempt at a POSIX class at all —
  `[a[:b]` (no closing `:]`) is not a PCRE2 error, it is an ordinary class
  containing the literal members `a [ : b`, ie. DECLINE, not REFUSE. So
  unlike `\p`, this doorway's tail space genuinely splits into a
  non-construct-specific region (DECLINE) and a construct-specific one
  (CLAIM for a known name, REFUSE for
  `[[:foo:]]`'s bad name — both still inside the closed-bracket shape).
  **Same rule, different measured predicate**: `\p`'s predicate happens to
  be the constant function "true" (§0); `[[:...:]]`'s predicate is "does a
  closing `:]` exist before the enclosing `]`." Nothing in the rule itself
  is doorway-specific; only the measured answer is.

### `PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL`, bound out explicitly (R10 disposition 3)

`probe_uprops.c` establishes the bit **behaviourally** as `0x00000002`
(watching `\p{Foo}` flip from ERR 147 to COMPILES — no `pcre2.h` is
installed on this box to read it from, and D30 §4/R13's lesson is that a
bit taken from memory is itself an unverified claim about a moving target).
Under that mode `\p{Foo}` and every one of the malformed-tail cells above
COMPILE, because the `\` stops being a property-escape introducer and
becomes an ordinary bad-escape-as-literal fallback. **pcrec does not offer
this mode** (D30 §4's rule: pcrec writes down the mode it compiles for,
and `ALT_BSUX`/`ALT_BSUX`-family extras are not on that list). This is not
a hedge — it is the same shape as `\U`/`\u` being REFUSE "because pcrec
will not offer `ALT_BSUX`," a decision pcrec can defend, not a false claim
about PCRE2 (D30 §4). Stated once, here, rather than re-derived per cell:
**every REFUSE/CLAIM verdict in this note is at options = 0, unqualified,
and the `EXTRA_BAD_ESCAPE_IS_LITERAL` column is measured ONLY to bound it
out, never to change it.**

---

## 2. Row changes

### `\p` (registry.c:354) and `\P` (registry.c:355) — NO FIELD CHANGES THIS PHASE

```
ESC('p', "\\p{L}", unicode_props, ANY_ENGINE,
    "a character with the given Unicode property", QF_YES, "set 117"),
ESC('P', "\\P{L}", unicode_props, ANY_ENGINE,
    "a character without the given Unicode property", QF_YES, "set 139"),
```

Every field the `ESC` macro sets is already right, verified rather than
assumed:

- `tail = NULL`, `recognise = NULL` — §1's constant-true predicate, correct.
- `flags = 0` — no `RF_CLASS_INVALID`; correct, because `[\p{L}]`, `[\P{L}]`
  and `[\pL]`/`[\PL]` all COMPILE (measured, §5(e)) — this construct is
  never permanently invalid in a class, so the flag must stay absent.
- `class_expect = "set 117"` / `"set 139"` — unchanged; this phase does not
  re-run `probe_class_expect.c`'s census, and nothing measured here
  contradicts the existing values.
- `rank = 0`, `aport = NO_PORT`, `cport = NO_PORT` — correct for a
  producer-free phase; `aport`/`cport` become `{PORT_FN, false, 0, NULL,
  pcrec_modport_uprops}` only when a real producer lands (§6, out of scope).

**Nothing on these two rows needs to change for phase 1 or for the
recognition fix.** The plan's *"expect a live tier-2 finding"* did not
materialise for these two rows specifically — it materialised, as
predicted independently, at the `\N{U+` row below (K10), which the plan
had already flagged as this milestone's to fix.

### `\N{U+` (registry.c:328-335) — REMOVE `RF_CLASS_INVALID` (K10 fix)

Current row (longhand struct literal, not built through a macro — this is
the row R10/C5 found miscounted twice by macro-name grep, per D29's
inline correction):

```
{RK_ESC, 'N', "{U+", "\\N{U+0041}", M_unicode_props, FLAV_PCRE2, ANY_ENGINE,
 RS_MODULE, RD_MODULE, NULL, NULL, RF_CLASS_INVALID,
 "a Unicode code point by number — PCRE2 error 193 outside UTF mode, which is recognition, not rejection",
 ROADMAP_PLANNED, QF_NO, "err 193",
 70, NULL, NO_PORT, NO_PORT},
```

**The single field change: `RF_CLASS_INVALID` (the `flags` field, 13th of
`RegRow`'s 21 positional fields) becomes `0`.** Every other field, stated
explicitly because this
project has been burned by knowledge sitting in a field nothing reads:

| field | value | changes? | why |
|---|---|---|---|
| `kind`, `sel`, `tail` | `RK_ESC`, `'N'`, `"{U+"` | no | identity; unrelated to the flag |
| `syntax` | `"\\N{U+0041}"` | no | unrelated |
| `feature`/`module` | `M_unicode_props` | no | attribution was always right — K10 is a wrong FLAG on a correctly-selected, correctly-attributed row |
| `flavours`/`engines` | `FLAV_PCRE2`/`ANY_ENGINE` | no | unrelated |
| `status`/`diag` | `RS_MODULE`/`RD_MODULE` | no | still an implemented-eventually module construct |
| `msg` | `NULL` | no | `RD_MODULE` never reads `msg` |
| `open_msg` | `NULL` | no | this row cannot be a class's own bracket (`\N{U+` is never `[...`-opening syntax); unaffected either way |
| **`flags`** | `RF_CLASS_INVALID` **-> `0`** | **YES** | the K10 fix itself |
| `note` | *(unchanged text)* | no | the note already says "recognition, not rejection" — it was CORRECT and CONTRADICTED by the flag (R10/C1-7); removing the flag makes the row internally consistent, no text edit needed |
| `roadmap` | `ROADMAP_PLANNED` | no | unrelated |
| `quant` | `QF_NO` | no | unrelated — `\N{U+41}` has no quantifiable-atom question of its own beyond what the atom-position construct already has |
| `class_expect` | `"err 193"` | **NO** — stays `"err 193"` | removing `RF_CLASS_INVALID` changes which DIAGNOSTIC TEXT pcrec emits in a class (see below), not whether `[\N{U+41}]` compiles; it still doesn't, with no `cport` wired, so `class_expect` (a fact about libpcre2, not about pcrec's message) is unaffected |
| `rank` | `70` | no | arbitration among the `\N`/`\N{`/`\N{U+` trio is unaffected — `RF_CLASS_INVALID` was checked in `ext.c` AFTER row selection (D33 §4: "arbitrate exactly as today, then consult the winner's port"), never during arbitration |
| `recognise` | `NULL` | no | same reasoning |
| `aport`, `cport` | `NO_PORT`, `NO_PORT` | no this phase | a real `cport` (returning `EXT_SCALAR`, matching `\b`'s and the digit rows' base-scalar shape from D33 §3) is the NEXT step after the flag fix, and is explicitly deferred with the rest of the producer (§6) — the flag removal and the port wiring are two different commits with two different risk profiles, and D33 §9's migration obligations (below) are about the flag removal alone |

**The externally visible consequence of the one-field change**: `ext.c`'s
in-class dispatch (`pcrec_ext_escape`, the `RF_CLASS_INVALID` check
immediately followed by the generic module-refusal fallback) currently
takes the `RF_CLASS_INVALID` branch for this row and prints *"\N is not
valid inside a character class."* Removing the flag drops it through to the
generic `RD_MODULE` in-class branch, which prints *"\N in a class requires
module 'unicode-props'"* — using the SELECTOR byte (`N`), same as every
other generic in-class message, not the fuller `\N{U+0041}` syntax. This is
a tier-3 wording fact (D26): the row now correctly PROMISES a module where
it previously promised nothing, which is tier-2 and exact; the specific
sentence is free to read "\N" rather than "\N{U+...}" the way every other
row's generic fallback does. Flagged as an open question for the manager in
§7 in case that reads as under-specific.

### Both check-path implications of the flag removal (brief item 2, both required)

1. **`registry_check.c:797-807`'s text assertion** (the three-way branch in
   `check_class_ports`, keyed on `r->flags & RF_CLASS_INVALID`) is
   DATA-DRIVEN off the row's own flags — no check-file edit is needed for
   the assertion to change what it expects. But the EXPECTED STRING for
   this specific row changes as a pure side effect of the row edit, from
   the `RF_CLASS_INVALID` branch's `"\%c is not valid inside a character
   class"` to the generic branch's `"\%c in a class requires module
   '%s'"`. This is worth stating explicitly (as the brief asks) precisely
   because nothing in a diff of `registry_check.c` will show it — the same
   lines of check code silently start asserting a different string. A
   reviewer diffing only `registry_check.c` would see no change and could
   wrongly conclude the check's coverage of this row is unaffected.
2. **`registry_check.c:1013`'s in-class sweep `skip_flag` mechanism**
   (`sweep(RK_ESC, "[\\%c]", 2, ..., RF_CLASS_INVALID, false, true)`): today
   this sweep's probe template supplies exactly ONE byte of tail
   (`[\N]`), which arbitration resolves to the BARE `\N` row (not the
   `{U+` row — the `{U+` row's tail cannot fit in a one-byte probe at all,
   D33 §9.2's own diagnosis of the fourth blind net). So the `skip_flag`
   exemption is **currently irrelevant to the `{U+` row**, because that row
   is structurally unreachable by this sweep regardless of the flag — the
   exemption matters for the OTHER ten `RF_CLASS_INVALID` rows that genuinely
   are one byte (`\A \B \Z \z \G \K \R \X \C`, and the BARE `\N` row at
   registry.c:310 — correctly flagged, err 171 permanent, not to be
   touched), which are untouched by this change. Once §4's tail-sweep extension lands (this phase's other
   deliverable, still design-only), the sweep GAINS the ability to probe
   `[\N{U+41}]` directly, and AT THAT POINT the flag removal is what makes
   the row reachable-and-correctly-checked rather than reachable-and-
   wrongly-exempted: with the flag still set, the extended sweep would hit
   the `RF_CLASS_INVALID` branch's exemption and never notice the row
   contradicts its own `note` (K10's exact original failure mode, one level
   up); with the flag removed, the row is swept like any ordinary
   `RS_MODULE` row and the sweep's mismatch detection (`registry_check.c`
   ~1013's `bad(...)` call) becomes a live guard on it. **The flag removal
   and the sweep extension are a matched pair — landing one without the
   other leaves either a silently-exempted row (flag alone) or a sweep that
   cannot reach the row it was built to catch (extension alone, which is
   exactly K10's history for the last three checkpoints).**

---

## 3. The streaming normalisation algorithm

Measured (`probe_uprops.c`, sections (d)):

- **Insignificant bytes in a `{...}` body**: space (leading, trailing,
  internal), hyphen `-`, underscore `_`, tab, and ASCII case are ALL
  insignificant — every variant of `\p{L}`/`\p{Letter}` tested normalises to
  the identical property (verified semantically, not just by "compiles":
  each variant matches `'A'` and not `'1'`, same as the `\p{L}` baseline).
- **Streaming, not buffer-then-normalise**: a body of 1 significant
  character plus 100,000 insignificant spaces (100,001 total body bytes)
  COMPILES, consistent with the plan's cited 100,006-byte example (this
  probe's exact padding count differs; the claim being tested — total body
  length is unbounded when significant-character count is low — does not
  depend on matching the plan's number exactly, and it did not).
- **The cap is exactly 48 significant characters, and the evidence that it
  is counted while STREAMING rather than applied to a fixed buffer after
  the fact is the BLAME OFFSET, not just the pass/fail boundary**:
  - `n=48` significant `'A'`s -> ERR 147 "unknown property", blamed at the
    END of the pattern (offset == total pattern length).
  - `n=49` -> ERR 146 "malformed \\P or \\p sequence", blamed at the offset
    **immediately after the 49th significant character consumed** — not at
    the closing `}`, not at the end of the pattern.
  - Re-run with an insignificant space inserted after every significant
    character (so total body length roughly doubles): the `n=49` blame
    offset moves in lockstep with "one past the 49th significant
    character," NOT with total body length. (`probe_uprops.c`'s two
    48/49-boundary sections print this side by side.)
  - **The caret does not count toward the cap.** `\p{^` + 48 `A`s `}` is
    ERR 147 (unknown); `\p{^` + 49 `A`s `}` is ERR 146, blamed one past the
    49th `A` — the same 48-character budget applies to the NAME only, and a
    leading `^` is consumed and dropped before the budget starts (this
    resolves what would otherwise be an open question — see the brief's
    ask for "anything else the design note needs").

**The algorithm pcrec's syntax port must implement**, stated as pseudocode
against a fixed 48-byte buffer (never an arena — D29/the plan's own
citation, `arena_alloc` aborts under a memory limit, which is K7):

    negate = false
    if next byte is '^': negate = true; consume it (does NOT enter the count)
    sig_count = 0
    buf[48]                         # fixed, never resized
    loop:
        if no more input (avail exhausted): FAIL, SYN_MALFORMED (146-shaped)
        b = next byte
        if b == '}':
            consume it
            if sig_count == 0: FAIL, "unknown property" (147-shaped — an
                                empty name is a KNOWN-bad name, not a shape
                                error; \p{} and \p{^} both measure this way)
            break                    # body scan complete; sig_count in [1,48]
        if b is insignificant (SP, TAB, '-', '_'): consume it, do not count
        else:                        # significant: a name character
            if sig_count == 48:      # this WOULD be the 49th
                FAIL, SYN_MALFORMED (146-shaped), blame HERE (matches the
                measured offset exactly — pcrec's own convention, and it
                happens to already agree with libpcre2's, which the D26
                addendum says is a coincidence worth taking but never
                chasing if a future PCRE2 disagrees)
            buf[sig_count] = uppercase-fold(b)   # case-insensitive, measured
            sig_count += 1
            consume it
    # name is buf[0..sig_count), sig_count in [1,48]
    lookup buf against the known-name table; found -> SYN_OK/CLAIM with a
    normalised name; not found -> "unknown property" (147-shaped) REFUSE

The bare-letter form (`\pL`, no braces) is a SEPARATE one-byte case, not a
degenerate 1-character run of the loop above: it is checked directly
against the **14-entry short-name table** (`C L M N P S Z`, both cases,
case-insensitive — measured exhaustively over all 52 letters; the other 38
letters are ERR 147, "dispatched, unknown name," not ERR 146). Any
non-letter, non-`{` byte after `\p` (204 of the 256 possible, measured) is
ERR 146 with NO body scan attempted at all.

**The `48` constant belongs in `src/core/limits.h`'s PCRE2 INTERNALS
section** (R10 disposition 5's ruling, and this probe run does not
contradict 48 — the boundary is exactly 48/49 as predicted, so there is no
"the probe wins" correction to make here). It sits beside
`PCREC_VERB_NAME_MAX` (128) as the same kind of number: *"an artifact of
how libpcre2 10.46 is built, not a statement about what a regex means"* —
a future PCRE2 moving it is a journal note, never a chase. Proposed name,
matching the file's existing convention (`PCREC_VERB_NAME_MAX`):

    PCREC_UPROP_NAME_MAX = 48

---

## 4. In-class tail-sweep extension design (D33 §9.2)

**The gap.** `registry_check.c`'s in-class sweep template is `"[\\%c]"` —
exactly the selector byte, zero bytes of tail. It can probe `[\N]`,
`[\p...`-nothing (it can only ever form `[\p]`, `[\P]`), never
`[\N{U+41}]`, `[\p{L}]`, or any body-carrying construct in a class. This is
K10's fourth blind net (a control whose reach is scoped BY the same
narrowness the thing it's supposed to catch depends on) and the design must
close it in the same step that removes `RF_CLASS_INVALID` from the `{U+`
row (§2), per the brief's citation of D30 §8: *"the TEST is the work,"
not the flag.*

**The extension, sized to avoid the D33 §9.2 combinatorial worry.** Do NOT
generalise the sweep into a generated byte-space search over class bodies
— that is exactly the "counting a population by a generator that cannot
produce it" trap (R13's own closing lesson, cited by this repo's other
reviews). Instead, add ONE additional probe **per row that carries a `tail`
or whose `syntax` is not a bare `\X` two-character form** — i.e. exactly
the tailed/body-carrying population D30/R10 already counted (18 tailed
rows) plus `\p`/`\P` themselves (body-carrying but tail-less) — reusing
each row's own `syntax` field, the same data `check_table_to_parser`
(D32 §9.1's PRIMARY instrument) already uses as a per-row probe pattern:

    for each row r where r->tail != NULL
                       or (r->syntax is not exactly "\<one char>"):
        probe = "[" + r->syntax + "]"
        assert probe reaches THE SAME ROW r (same as the existing
               per-row `syntax` check already asserts at atom position —
               D32 §9.1's primary instrument, extended to class position)
        assert the in-class diagnostic matches check_class_ports's existing
               three-way branch (RF_CLASS_INVALID text / RD_FIXED text /
               generic "requires module" text) for whichever branch r's
               (possibly just-changed) flags select

This is **TOTAL and cheap** — 18 + 2 = 20 extra probes, not a generated
space, no oracle beyond the same `check_table_to_parser` machinery already
in the suite, and it directly reaches `[\N{U+41}]` (the `{U+` row's own
`syntax` field is literally `"\\N{U+0041}"`) and `[\p{L}]`/`[\P{L}]` (the
`\p`/`\P` rows' `syntax` fields are `"\\p{L}"`/`"\\P{L}"`).

**One implementation caution, already flagged by this project's own
comments for a different row and worth restating here rather than
rediscovering**: `registry_check.c`'s existing comment on the `\g{-1}` row
warns that wrapping a row's canonical `syntax` in `[...]` can CHANGE its
meaning if the syntax text itself contains a `]` or reads differently
inside a class (`[\g{-1}]` is a class of literal members `g { - 1 }`, not
the backreference). `\N{U+0041}` and `\p{L}`/`\P{L}` do not have this
problem — verified directly (`probe_uprops.c`'s section (e): `[\N{U+41}]`,
`[\p{L}]`, `[\P{L}]` all measure exactly as expected, no reinterpretation)
— but the extension's implementation must check this PER ROW when it is
built, not assume it holds for the population generally; a row whose
`syntax` reads differently inside `[...]` needs either a class-specific
probe string or an explicit skip with a reason, the same way the base
per-row check already special-cases nothing but could need to.

---

## 5. Test plan

### Reject-pin additions (offsets load-bearing — the S27 lesson)

All at pcrec's own future convention once phase 2 lands (own-offset, not
PCRE2's number, per the D26 addendum) — the measured PCRE2 offsets below are
the ORACLE for what pcrec's offsets should agree with where the two
conventions naturally coincide (they do, in every cell measured), not a
promise to chase PCRE2's number if a future version moves it:

| pattern | libpcre2 verdict | offset | pcrec pin (once phase 2 lands) |
|---|---|---|---|
| `\p` (at EOF) | ERR 146 | 2 | REFUSE, malformed, module `unicode-props` |
| `\p!` | ERR 146 | 3 | REFUSE, malformed |
| `\p9` | ERR 146 | 3 | REFUSE, malformed |
| `\p{` (at EOF) | ERR 146 | 3 | REFUSE, malformed (unterminated) |
| `\p{}` | ERR 147 | 4 | REFUSE, unknown name (empty) |
| `\p{L` (unterminated) | ERR 146 | 4 | REFUSE, malformed (unterminated) |
| `\p{Foo}` | ERR 147 | 7 | REFUSE, unknown name |
| `\pA` (not in C L M N P S Z) | ERR 147 | 3 | REFUSE, unknown name |
| the mirrored 8 cells for `\P` | (same shape) | (same, byte-identical) | REFUSE, module `unicode-props` |
| 48 significant chars | ERR 147 | end-of-pattern | REFUSE, unknown name |
| 49 significant chars | ERR 146 | one past the 49th sig. char | REFUSE, malformed (name too long) |
| `[\N{U+41}]` | ERR 193 (today: pcrec text changes, see §2) | 3 | REFUSE, module `unicode-props` (was: "not valid inside a class", no module) |
| `[0-\N{U+41}]` | ERR 193 | 5 | REFUSE, module `unicode-props`, SCALAR-shaped (endpoint rule does not override) |
| `[0-\p{L}]` | ERR 150 | 8 | REFUSE, PCRE2's own range error (endpoint rule DOES override — SET-certified) |
| `[0-\p{Foo}]` | ERR 147 | 10 | REFUSE, unknown name (uncertifiable — range check never runs) |

### PC-3 differential additions (Q1/Q2 precedent)

Design for phase 2 (this phase documents the generator, does not build it):
a generated space crossing

    prefix    in { "", "^" }
    name      in { the 14 known short names, a handful of known multi-
                    letter names (Alpha, Alphabetic, Any — all measured
                    COMPILING here), "Foo" (unknown) }
    noise     in { none, leading space, trailing space, internal
                    hyphen/underscore/space, mixed ASCII case }
    shape     in { bare "\pX" (single letter only), "{...}" }
    position  in { atom, class, class as low endpoint, class as high
                    endpoint, negated class }

against libpcre2 at options=0, comparing verdict AND (once the port
produces real output) the normalised name — the same shape as Q1/Q2's name
differentials, generated rather than curated, because the curated cells in
this note are deliberately the FAILURE-DIRECTION set (D27/R14's method: a
generator that reproduces only the examples that motivated the design would
under-cover the same way the digit-sweep probe's header warns against).

### Mech sabotages (S31+, table-driven like S27-S30)

Every check proposed above satisfies D33 §9.3's "false today" test
trivially and honestly, because there is no producer: a pin asserting
`[\N{U+41}]` reads "requires module 'unicode-props'" is FALSE against
current HEAD (which still prints "not valid inside a character class")
until §2's flag removal lands, and a pin asserting the 48/49 boundary text
is FALSE until phase 2's syntax port exists at all. Stated per D33 §9.3's
own phrasing ("was this already true yesterday?"):

- **S31 — flip the {U+ row's flags back to `RF_CLASS_INVALID`** after the
  fix lands: the extended in-class sweep (§4) must fail, and
  `registry_check.c:797-807`'s text assertion must fail on the wrong branch.
  Both were FALSE-then-TRUE by construction: before the fix, the row IS
  flagged, so this sabotage is a no-op (the check was already passing the
  "wrong" way) — the sabotage is meaningful only measured AFTER the fix
  lands, which is when this row joins the phase-2 commit.
- **S32 (planned, needs phase 2) — off-by-one the 48-char cap to 49** in
  `pcrec_modport_uprops`: the boundary reject-pins (n=48/n=49 in the table
  above) must both flip. Cannot be exercised until the port exists;
  recorded here so it lands in the SAME commit as the port, not discovered
  later.
- **S33 (planned, needs phase 2) — drop the `^`-before-count consume**
  (count the caret as a significant character): the caret-boundary pins
  (§3's measured `\p{^` + 48/49 `A`s`}` cells) must flip by exactly one.
- **S34 (planned, needs phase 2) — case-fold nothing** (compare names
  case-sensitively): the `\p{letter}`/`\p{LETTER}`/`\p{Letter}` pins (§3)
  must start disagreeing with each other.
- **S35 (planned, needs phase 2) — treat insignificant bytes as
  significant** (stop skipping space/hyphen/underscore/tab): the
  insignificant-byte-census pins (§3) must flip, and — sharper — the
  streaming pin (a valid 1-char name padded past 100,000 bytes) must start
  FAILING as "name too long," which is the exact bug the plan's "buffer is
  not fixed" warning exists to prevent (truncation turning `\p{____L}` from
  CLAIM into REFUSE — this sabotage is the truncation bug, reintroduced on
  purpose to prove the pin catches it).

### `tests/unicode-props/` directory

**Not created this phase.** No producer lands (brief item 6), so there is
nothing to assert beyond what `tests/reject/` and the extended
`registry_check.c` sweep already cover — the precedent is `tests/modifiers/`,
which this repository's own `tests/CLAUDE.md` records as landing WITH its
producers (MOD-0.5c/d), not at design time. If the manager wants the
directory scaffolded now anyway, its name should be `tests/unicode-props/`,
matching the module-name convention `tests/classes/`/`tests/modifiers/`
already use, with blocks carrying `features unicode-props`.

---

## 6. Out of scope, stated

- **No producer.** `pcrec_modport_uprops` is specified (§1, §3) but not
  written; `aport`/`cport` on all three affected rows stay `NO_PORT`.
- **No `aport`/`cport` wiring** on `\p`, `\P`, or `\N{U+` — the K10 fix in
  §2 is the FLAG only; the port that would let `[\N{U+41}]` actually
  COMPILE (an `EXT_SCALAR` cport, matching `\b`'s and the digit rows' base
  shape) is explicitly the next step, not this one.
- **No UTF mode.** Every measurement in this note and in `probe_uprops.c`
  is at options=0 (R10 disposition 3's bound mode). `PCRE2_UTF` is known
  (D30 §4/R13) to flip at least `\N{U+0041}`'s verdict outside a class; it
  is not swept here for `\p`/`\P` and is out of scope for this milestone.
- **Class-structure widening is RULED DEFERRED** to the first WIDE
  producer (Frank, 2026-08-12, amendment under D33 §7 — this worktree
  predates that amendment commit; taken from the brief, not independently
  re-derived). `\p{...}`'s eventual SET-shaped producer needs more than the
  current 256-bit `cls[32]`, and this phase does not touch `cls[32]`'s
  width, D33 §7's own text, or any codegen path.

---

## 7. Open questions for the manager

1. **The generic in-class message for the `{U+` row reads "\N in a class
   requires module 'unicode-props'"** after the flag removal — using only
   the selector byte, losing the `{U+...}` specificity, because it falls
   through to the same generic template every other `RD_MODULE` row's
   in-class fallback uses. D26 tier-3 says this is fine (wording, not
   attribution), and no other row gets special-cased text here today. Confirm
   this is acceptable, or say if the `{U+` row should get a bespoke
   in-class message the way `\g`/`\k`'s class ports do (those differ
   because they PRODUCE a literal, not because their wording is hand-tuned).
2. **The 14-member short-name table (`C L M N P S Z`, case-insensitive) is
   a measurement tied to libpcre2 10.46.** Recommend it be GENERATED from a
   live census the way `probe_cls_bits.c --emit` generates `cls_bits.inc`,
   rather than hand-typed into `mod_uprops.c`, so a future PCRE2 adding an
   eighth short-category letter is a re-generation (D26's addendum: "a
   version bump is a deliberate re-measurement event") rather than a stale
   table nobody notices. Flagging because `probe_cls_bits.c`'s emit-mode is
   the closest precedent and phase 2 should decide whether `unicode-props`
   gets the same treatment or a simpler hand-written 14-row table (it is a
   much smaller table than the class-bit censuses `probe_cls_bits.c` emits).
3. **`Script=Latin`/`sc=Latin` property-VALUE syntax compiles under
   libpcre2** (measured, §f) and therefore CLAIMS under this note's rule
   (§1) regardless of whether phase 2's first producer slice actually
   implements script-name lookups — recognition (tier 2, exact) and
   producer completeness (tier 3/roadmap) are different questions, and this
   note only answers the first. Confirm that reading is right, i.e. that a
   first producer slice implementing only general-category short/long names
   (not `Script=`) would still correctly promise `unicode-props` for
   `\p{Script=Latin}` today and simply not produce a working matcher for it
   until a later slice — the same "known-but-unimplemented, a complete and
   tested outcome" shape SR-1 already establishes for NULL handlers
   generally.
