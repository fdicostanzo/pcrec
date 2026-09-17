# F2 — the captures axis and the nullable-collapse rescue: MEASUREMENT ONLY

[O-31 finding 2] asked why the captures axis strips pcrec's own
"nullable-collapse rescue" on classic ReDoS shapes (`trim-nested-star`
×214,356, `winpath-near-miss` ×242,483) while `phone-list-nested-plus`'s
hybrid prefilter survives captures at ×135,700, and whether the decline
boundary can narrow to "declines only when a capture intersects the
collapsed region." Nothing under `src/`/`tests/` changes here — this is
read-only analysis plus constructed witnesses, run against a local
`make -j4 CC=gcc-16` build in `worktrees/f2rescue`.

**Headline: the premise needs correcting on three points before the
"boundary" question can be answered, and once corrected the boundary
cannot narrow by capture location — not as a small predicate change and
not at all, because capture placement never entered the predicate in the
first place.**

1. There are TWO decline mechanisms in this tree
   (`src/opt/select_engine.c:905-918`, `internal.h:1580-1651`), and the
   bench's own witness (`trim-nested-star`) fires the one that has
   **nothing to do with count-collapse**. The genuinely
   collapse-scoped decline (`ESEL_DECLINED_NULLABLE`, [OPT-4.1], what
   "nullable-collapse rescue" literally names) is **structurally
   unreachable whenever captures are present** (§2).
2. `winpath-near-miss` is not part of this mechanism at all — it has
   zero capturing groups, and `auto` selects the DFA identically with
   and without `--no-captures` (§4). Its ×242,483 gap is the unrelated
   `auto`-vs-forced-`--engine=vm` comparison.
3. Neither decline's predicate has ever tested capture *location*.
   Both are a single test of whole-pattern nullability
   (`pcrec_minw(root) == 0`, `select_engine.c:653`), and that is not an
   accident of implementation — it is the correct test for what a
   position-skipping prefilter needs, and a capture-location predicate
   would be actively wrong (§5, §6).

## 1. The predicate, by file:line, and why it has no captures term

`fit.lang_nullable = pcrec_minw(root) == 0` — `select_engine.c:653`.
`pcrec_minw` (`src/opt/mrl.c`) is the SAME whole-tree width analysis the
MRL prune uses, asked here of the erased/collapsed language; its
documented safe direction is under-estimation, so `minw==0` can claim
nullable when the true language merely might not be, never the reverse
(`src/opt/CLAUDE.md`'s "[OPT-4.1] the nullability predicate" section).

The decline that reads it:

```
select_engine.c:888-889
    bool lang_nullable_declinable =
        fit.lang_nullable && !has_bref && !has_call && !force_on;
```

**There is no capture conjunct anywhere in this expression**, and there
never has been one added or removed — `lang_nullable_declinable` is the
ONE local both decline fields derive from (`select_engine.c:905-910`):

```
905  fit.prefilter_declined_nullable =
906      cx->collapse_reason != CR_NONE && lang_nullable_declinable &&
907      fit.prefilter_has_collapsible_rep;
908  fit.prefilter_declined_nullable_default =
909      cx->collapse_reason == CR_NONE && !cx->dfa_disabled &&
910      lang_nullable_declinable && would_prefilter;
```

So the answer to the brief's framing ("is it structural because the
collapse erases capture groups, or conservative because it declines
whenever ANY capture exists") is **neither**. It is not about captures
at all, erased or otherwise. The reason a capture-bearing pattern
reaches this decline is a SEPARATE, unrelated mechanism —
`forces_captures` (`select_engine.c:99-135`) forces `ENGM_VM` in the
engine-selection fixpoint whenever `cx->want_caps && pcrec_has_live_capture(a)`
(`:131-134`), which runs BEFORE the prefilter fit is even computed and
has its own reason (a DFA artifact cannot promise capture offsets) with
zero reference to nullability. Once VM is chosen — by captures, by a
backreference forcing VM some other way, by `--engine=vm`, or by a DFA
state-cap overflow — the SAME nullability test applies uniformly. The
"captures axis strips the rescue" framing describes a real correlation
(captures often force VM, and VM is the only place this decline can
fire) but not a causal predicate: captures never appear as a term.

## 2. The rung-scoped decline (`ESEL_DECLINED_NULLABLE`, what "nullable-collapse rescue" names) is unreachable under captures

`src/opt/CLAUDE.md`'s own note on the count-collapse mechanism ([OPT-4]):
`X{m,n}` is rewritten `X{min(m,1),}` ONLY when the exact machine already
overflowed a DFA state cap on a `compile_driver` retry
(`cx->collapse_reason == CR_SEL1`, set only in that retry —
`src/core/CLAUDE.md`'s `compile.c` entry, "[SEL-1] `compile_driver` IS A
BOUNDED ONE-SHOT RETRY LOOP"). That retry exists to recover from a DFA
build that was ATTEMPTED and overflowed. But `pcrec_select_engine` runs
BEFORE any DFA is built, and when captures are present `forces_captures`
already forces `fit.chosen == ENGM_VM` at that point — so the pipeline
never attempts the exact DFA build the retry mechanism exists to catch
the overflow of. No overflow event, no retry, no `CR_SEL1`, no rung —
the whole [OPT-4.1] mechanism is inert.

Measured directly. `[a-z]{0,60000}` overflows the DFA state cap
regardless of captures (120,003-NFA-state exact machine — well past
`PCREC_MAX_AUTO_DFA_ELEMS`/state caps):

| construction | captures | reaches a DFA build? | `ENGINE_SEL` |
|---|---|---|---|
| `[a-z]{0,60000}` | none | yes — overflows, retries, CR_SEL1 rung offered | `declined-nullable` (the RUNG form, [OPT-4.1]) |
| `([a-z]{0,60000})` | capture spans the whole quantifier | **no** — `forces_captures` picks VM before any DFA is attempted | `declined-nullable-default` (the DEFAULT form, [OPT-4.2], no rung) |
| `(x)?[a-z]{0,60000}` | capture disjoint from the quantifier, pattern still whole-nullable | **no**, same reason | `declined-nullable-default` |
| `(x)[a-z]{0,60000}` | capture disjoint, pattern NOT whole-nullable (`x` required) | **no** (still VM by captures) — but `lang_nullable_declinable` is false, so nothing declines; the PREFILTER build for the ordinary hybrid then hits the SAME state-cap overflow independently and gets its own CR_SEL1 retry | `collapsed-prefilter` ([OPT-4] rung, survived — `RX_VM_PREFILTER_LANG_WHY "dfa overflow retry, exact nfa 120003"`) |

(Reproduced live: `./build/pcrec -p rx --emit-main -o out.c -- '<pattern>'`,
`grep ENGINE_SEL out.c`; artifacts kept under the session scratchpad,
not committed.)

Row 2 is the direct falsification of "the collapse erases capture
groups, so any capture in scope kills it": there is no collapse EVENT
here to erase anything from — the pattern never reaches a DFA build at
all once a capture is present, decline or not. Row 4 shows the ONE way
a captured, cap-overflowing pattern still reaches an [OPT-4] rung: not
through the main-match DFA (captures always route that to VM
immediately), but through the ordinary hybrid's OWN attempt to build an
exact prefilter DFA, which can independently overflow and retry. On
that path the decline still fires purely off whole-pattern nullability,
which this row is NOT nullable, so it correctly survives.

Corpus-independent confirmation: across the full shipped corpus census
(§4) and the bench's 58-pattern capability set, **zero** patterns
compile to `ESEL_DECLINED_NULLABLE` (rung form) at default flags; every
observed decline is `ESEL_DECLINED_NULLABLE_DEFAULT`. The rung form's
population is not merely rare — it requires a captures-FREE, cap-
overflowing, nullable pattern, a combination the ask's own witnesses
never produce because they all have captures.

## 3. `trim-nested-star` and `evil-alt-nested`: confirmed live, both DEFAULT-form, both have no collapsible repeat at all

```
$ ./build/pcrec -p rx --emit-main --no-captures -o t_nocaps.c -- '^(\s+)*$'
RX_ENGINE "dfa"            RX_ENGINE_SEL "selected"          RX_DFA_MATCH "search-filter"

$ ./build/pcrec -p rx --emit-main -o t_caps.c -- '^(\s+)*$'
RX_ENGINE "vm"             RX_ENGINE_SEL "declined-nullable-default"
RX_ENGINE_WHY "capture group at pattern offset 1"   RX_VM_PREFILTER "none"
```

matches the ledger exactly (`declined-nullable-default`,
`RX_ENGINE_WHY "capture group..."`). No `RX_VM_PREFILTER_LANG_WHY` field
is emitted at all for the caps arm — confirming `fit.prefilter_has_
collapsible_rep` is false (`(\s+)*` has no `{m,n}` for [OPT-4] to
collapse; `*` is already unbounded). **The term "nullable-collapse
rescue" does not literally apply to this witness**: no collapse rung
was ever offered or declined, because there was nothing to collapse.
What declined is the ordinary hybrid's exact prefilter, for the same
reason it would have declined on ANY VM-forcing route, capture or not.

The bench capability corpus census (§4) turned up a second live
instance with the identical shape: `evil-alt-nested`
(`^(([a-z]+)*)+$`, O-31 finding 3's own witness) also stamps
`declined-nullable-default` — the outer `+` requires one repetition,
but that repetition's own body (`([a-z]+)*`) can match empty, so
`pcrec_minw(root) == 0` and the ordinary hybrid declines its exact
prefilter the same way.

## 4. `winpath-near-miss` is not in this population

```
$ ./build/pcrec -p rx --emit-main -o w_caps.c   -- '^[A-Za-z]:\\(?:[^<>:"/\\|?*]+\\)*[^<>:"/\\|?*]+$'
$ ./build/pcrec -p rx --emit-main --no-captures -o w_nocaps.c -- '^[A-Za-z]:\\(?:[^<>:"/\\|?*]+\\)*[^<>:"/\\|?*]+$'
```
Both: `RX_ENGINE "dfa"`, `RX_ENGINE_SEL "selected"`. **Identical**,
caps or not — because the pattern's own `(?:...)` groups are all
non-capturing (`bench/capability/patterns.rxt:296`); there is nothing
for `forces_captures` to force VM over, so `auto` picks the DFA on both
arms and no decline of any kind is reached on either.

The ledger's own R-ARM-1 table (`bench/.../reports/2026-09-17-
capability-....md:423`) confirms this from the bench side: the
×242,483 row is `auto-caps` vs **`vm-caps`** — auto (fast, DFA) against
a testee config that FORCES `--engine=vm` (bare backtracking, no
prefilter attempt at all, by-passing `fit.prefilter`'s derivation
entirely) — not `auto-caps` vs `auto-nocaps`, the pairing that would
actually exercise this decline. `trim-nested-star`'s own ×214,356 row
two lines above it in the same table IS the `auto-caps` vs
`auto-nocaps` pairing. The ledger's §1.2 Finding D prose says so
explicitly ("here `auto`'s own selection logic... stays fast while the
bare forced-VM control does not") but the O-31 outbox summary's "mirrors
at ×242,483" compresses the two into one shape. **They are not one
mechanism**: `winpath-near-miss` never declines anything, on either
capture arm, and its ratio is evidence about the cost of the plain
backtracking VM relative to `auto`'s correct engine choice, not about
this decline's boundary.

## 5. Corpus census

Method: every `^pattern ` line in `tests/**/*.rxt` (raw grep, not the
`.rxt` decode path — a rough population count, not a correctness
check) and every `^pattern ` line in the bench's `bench/capability/
patterns.rxt` (fetched read-only over the tailnet, kept in the session
scratchpad, not committed), each compiled individually with
`--emit-main` at default flags (`-p rx`, no `--features`, so any
pattern needing an optional module — `atomic-groups`, `lookaround`,
etc. — refuses cleanly and is excluded rather than mis-measured) and
its `ENGINE_SEL` stamp read off the generated `.c`.

**Shipped corpus** (211 files, 3,938 `pattern` lines, 1,500 compile
under bare `-p rx`):

| `ENGINE_SEL` | count | % of compilable |
|---|---:|---:|
| `selected` | 1,443 | 96.2% |
| `declined-nullable-default` ([OPT-4.2]) | 56 | 3.7% |
| `collapsed-prefilter` (survived, [OPT-4] rung) | 1 | 0.07% |
| `declined-nullable` (declined, [OPT-4.1] rung) | **0** | 0% |

**Bench capability set** (58 patterns, 32 compile under bare `-p rx`;
26 refuse for missing modules — atomic groups, lookbehind — expected
and excluded):

| `ENGINE_SEL` | count |
|---|---:|
| `selected` | 30 |
| `declined-nullable-default` | 2 (`trim-nested-star`, `evil-alt-nested`) |
| `declined-nullable` | 0 |

Zero population for the rung-scoped decline in EITHER corpus, at
default flags, is consistent with — not proof of, on its own — §2's
structural finding that it cannot co-occur with captures; the
constructed witnesses in §2 are the causal evidence, this is the
corpus-scale confirmation that nothing in the shipped test suite or
the bench's own pattern set contradicts it.

## 6. Why `phone-list-nested-plus` survives and what that implies for the ask

```
$ ./build/pcrec -p rx --emit-main -o p_caps.c -- '^(\d+\s*)+$'
RX_ENGINE "vm"   RX_ENGINE_SEL "selected"
RX_VM_PREFILTER "hybrid"   RX_VM_PREFILTER_LANG "exact"
RX_VM_PREFILTER_LANG_WHY "no counted repeat"
RX_VM_PRUNE_CEILING "prefilter-window"
```

`^(\d+\s*)+$` requires at least one repetition of `(\d+\s*)`, and that
repetition itself requires at least one digit (`\d+`), so
`pcrec_minw(root) == 1`, not 0. `lang_nullable_declinable` is false —
not because a capture sits outside anything, but because the pattern
genuinely cannot match the empty string. The prefilter is built
(`RX_VM_PREFILTER_LANG_WHY "no counted repeat"` — same non-collapse
population as `trim-nested-star`, just on the surviving side of the
SAME predicate), and `RX_VM_PRUNE_CEILING "prefilter-window"` confirms
the brief's premise: the hybrid's DFA prefilter finds a candidate
window, and the VM (which alone can write captures) reruns only inside
that window — the erasure that makes a capture-bearing pattern
prefilter-compatible at all (`src/opt/select_engine.c`'s own
`[M6.5.2]`/backrefs section: a prefilter is built from the
capture-ERASED NFA, which is exactly why nullability of that erased
language, not the presence or position of the erased captures, is the
only thing that can defeat it).

So `phone-list-nested-plus` does not "escape the captures constraint"
through any special property of ITS capture — it was never subject to
a captures-shaped constraint in the first place. It escapes because its
whole-pattern language is not nullable, full stop, which is orthogonal
to where its one capturing group sits.

## 7. Answer to the ask: can the boundary narrow to "declines only when a capture intersects the collapsed region"?

**No — the premise does not hold and the proposed narrowing would be a
regression, not a small predicate change.**

1. For the bench's own witness (`trim-nested-star`) and the second
   corpus instance found here (`evil-alt-nested`), there is no
   "collapsed region" to intersect — no counted repeat is present, no
   [OPT-4] collapse rung ever runs (§3). A predicate keyed on
   intersecting a collapsed region is vacuously false for both, and
   the intended rescue would still not fire.
2. Where a genuine collapsed region DOES exist (§2's constructed
   family), it is only ever reached by a captures-FREE pattern — the
   moment a pattern has a live capture, `forces_captures` routes it to
   VM before any DFA is attempted, so the rung mechanism that would
   need narrowing is already unreachable. Narrowing a decline that
   never fires under the condition it is meant to be narrowed for is a
   no-op on the actual population.
3. Most fundamentally: `lang_nullable_declinable`/`fit.lang_nullable`
   test whether the WHOLE matched language can consume zero bytes
   (`pcrec_minw(root) == 0`), because that is exactly the property
   that makes a position-skipping DFA prefilter valueless — if the
   language can match empty anywhere, the filter can dismiss no
   position, and per `[OPT-4.1]`'s own measured need
   (`select_engine.c:816-821`, `O-10` item 3) building one anyway
   COSTS 1.2-9.9x versus no prefilter, because the artifact still pays
   the DFA scan for zero rejection power. That cost is a property of
   the WHOLE pattern's nullability, not of any one subexpression's
   location relative to a capture. The constructed `(x)?[a-z]{0,60000}`
   witness in §2 makes this concrete: the capture (`(x)?`) sits
   entirely OUTSIDE the large quantifier, yet the whole pattern is
   still nullable (via the capture's own optionality) and a prefilter
   built for it would be exactly as useless — "does the capture
   intersect the collapsed region" answers a question about SYNTAX
   that has no bearing on the semantic property (global emptiness-
   admission) the decline exists to detect. Narrowing on syntactic
   intersection would let this witness's prefilter build, and it
   would cost the measured 1.2-9.9x for zero benefit — reintroducing
   the defect [OPT-4.1]/[OPT-4.2] were built to close.

**What would actually help `trim-nested-star`-shaped patterns** is not
a narrower decline but a different mechanism entirely, and both
candidates are design events, not measured here:

- A prefilter construction that is not all-or-nothing on global
  nullability — one that can still dismiss SOME positions even though
  the whole language admits an empty match somewhere. This is
  materially new algorithmic work (a partial/local admission model),
  squarely a D77 build-under-measurement candidate with no measured
  need established yet beyond this one finding.
- The route [O-31] finding 3 already asks about for `evil-alt-nested`
  in the same report: a VM step budget / give-up analogous to PCRE2's
  match-limit. That is a general fix for pathological backtracking
  independent of whether a prefilter exists, and it would help exactly
  the population this finding is about (nullable, capture-forced,
  VM-only patterns) without touching engine selection at all — worth
  flagging as the more promising general direction, since it addresses
  the underlying vulnerability class rather than trying to make
  prefilter admission smarter for one shape family.

Neither is proposed for building here; both require their own
measurement before a design note, per D77.

## Reproduction

Witness `.c` artifacts and the census scripts/results live under the
session scratchpad
(`.../scratchpad/f2rescue/{census.sh,census_results.tsv,
bench_census.tsv,bench_patterns.rxt}`), not committed — per the
scope mandate, nothing in this lane's deliverable depends on scratchpad
persistence; every number above is reproducible with the two `pcrec`
invocations shown inline and the corpus grep in §5.
