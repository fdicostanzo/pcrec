# R12 — 2026-08-11 — a COMPARATIVE design panel: D30's rank vs an ordered list of parser functions

**Nothing was built.** Four lenses, one primary question each — the narrow-brief
format R11 measured as delivering far better than five-part briefs. All four
delivered. **Five of the author's claims were refuted, one design was killed,
and a third shape emerged that neither author proposed.**

Read alongside D30 (with its R11 marks), R11 and its three addenda.

## The two designs

**A — D30 as it stands.** A row names a PURE recogniser (no `Ctx`, no
allocation, no failure path); the selector byte is a bucket key; every
recogniser runs; the highest-ranked ANSWERING row wins; a separate SEMANTIC port
takes `Ctx *` and builds.

**B — Frank's, 2026-08-11.** A row names ONE parser function that both decides
and parses. The doorway walks an ORDERED LIST; `sel` demotes from key to cheap
pre-test; first function to claim wins; three outcomes (NOT_MINE / PARSED /
UNIMPLEMENTED); functions called with a COPY of `Ctx` and a `trial` flag that
trips `arena_alloc`/`ctx_fail`, so a speculative call can be abandoned.

---

## P2 — DESIGN B'S PRECEDENCE RULE IS REFUTED ON THE SHIPPED TABLE

**B's loop, run against `registry.c` as it stands, gets its own canonical
example wrong twice over.** No edit required — this is the file today:

    registry.c:242   \N          tail-less FALLBACK — declared FIRST
    registry.c:254   \N{name}    tail "{"    — short, second
    registry.c:257   \N{U+0041}  tail "{U+"  — long, LAST

1. First-match hands `\N{U+0041}` to the fallback (no tail = always matches) →
   module `classes` instead of `unicode-props`. **16 of 17 boundary probes.**
2. Pin the fallback last and it is still wrong: `"{"` precedes `"{U+"`, so the
   short prefix claims it — the REJECTED row instead of `unicode-props`.
   **7 of 17**, including the canonical example.

**The irony is exact.** `src/parse/CLAUDE.md:166` records that the `\N` rows are
written SHORTEST first *deliberately*, so `check_tail_precedence` would have a
real prefix-pair to observe. **The hardening that made the old check meaningful
is precisely the configuration that breaks the new rule.**

**Census:** 70 pairwise reorderings across the four multi-row buckets — 18
load-bearing, 52 silent, every load-bearing pair involving the bucket's
tail-less fallback. Wider: moving `RK_GROUP`'s `REG_SEL_ANY` catch-all to
position 0 **breaks 54 of the other 55 GROUP rows**, none of which were touched.

**The structural finding:** order has a failure mode rank cannot have —
**global positional coupling.** One untouched row's position silently changes
what fifty-four others mean. A rank is local to its row.

**And B's own repair cannot cover B's own reason for existing.** A static
position check is buildable (~40 lines, mirroring `check_tail_precedence`) and
would catch all of the above — but it can only reason about `tail` STRINGS,
while B demotes `tail` to a hint and lets functions claim beyond it. **The check
covers exactly the rows that do not need design B.**

## P1 — TRIAL MODE IS SELF-DEFEATING, BUILT AND TESTED

§2.2 calls `row.parse` once and commits only after it RETURNS. So any construct
with a body to build must allocate INSIDE the trial-covered call. Under a
literal trip, **that aborts every CORRECT implementation**, not just buggy ones.

So a real handler must clear the flag first. P1 built exactly that — `cx->trial
= false;` as line one, then allocated freely. **The trip did not fire.** `trial`
is ordinary mutable state on the struct the checked function holds a pointer to;
nothing distinguishes "committed, now building" from "buggy, allocating early".

**Design A's boundary — a pure recogniser has no `Ctx *` at all — cannot be
defeated this way. B's can, by construction.** The claim that the dynamic check
is "strictly stronger than design A's type-level guarantee" is FALSE.

**And it degrades with growth:** every construct beyond a bodyless keyword needs
that escape hatch, so coverage converges toward vacuous. Invisible today because
**zero shipped rows ever return `PARSED`** — every row is
`RS_MODULE`/`RS_REJECTED`, so the trip has never been exercised on its one real
job. R11/C4-1's shape again.

**Trial mode also buys nothing for its own motivating customer.**
`pcrec_ext_class_pair_opens` is safe to call speculatively only because it is
ALREADY pure — so it is equally safe under design A.

**Arena leak, quantified:** with the necessary bypass, ~76-80 bytes leaked per
byte scanned — 0.1 MB at N=100, **76.4 MB at N=1,000,000** — unreachable from
the real `Ctx`, so `arena_free` frees NONE of it, with no pattern-length cap.
The author's "waste, not corruption" was wrong by orders of magnitude.

**Good news for the successor shape:** all three hard "does deciding require
committing" candidates — class_bracket's three-rule scan, `LIMIT_MATCH`'s
magnitude accumulator, the option-run grammar — are **genuinely pure**.

## P3 — THREE OUTCOMES HOLDS AT ONE DOORWAY OF FOUR

- **It would resurrect a bug FIX-2 removed.** The class `:` row has FOUR live
  terminal shapes — `[[:alpha:]]` (module), `[:alpha:]` (open_msg, no module),
  `[[:foo:]]` (bad name), `[x[:<:]]` (wrong position). Mechanically rendering
  "UNIMPLEMENTED → requires module 'classes'" is the exact over-promise FIX-2
  removed, for **three of its four shapes**.
- **Module-shaped outcomes are a minority even at ESC** — only ~18 of 41 rows.
- **`NOT_MINE` is structurally unreachable at VERB**: one row, one unconditional
  call site, nothing to hand back to. And `(*)` fits none of the three outcomes.
- **"Falling off the end" is three different behaviours**, and two of the four
  epilogues do not exist as code — unreachable only by a convention nothing
  enforces (M4's R11 finding, re-verified in source).

## P4 — THE SABOTAGE MATRIX

| sabotage | A | B |
|---|---|---|
| `module` swapped (tier 2, EXACT) | no | no |
| row deleted | no | no |
| row added for a construct PCRE2 lacks | yes | yes |
| two rows REORDERED | n/a | **no check proposed** |
| a rank changed | almost never (20/22) | n/a |
| function claims across bytes | no | yes (`sel`-redundancy) |
| `sel` disagrees with its function | n/a | yes |

Also: the author's `sel`-redundancy check is **vulnerable to R11/C4-1 as
worded** — "does not return PARSED" passes vacuously for all 100 stub rows
before any discrimination exists. And the claim that the per-row `syntax` check
"gets stronger" under B is true but **irrelevant to the module-swap blindness it
was cited to fix**: `registry_check.c` builds its expected message from
`r->module` and the real output comes from the same field.

## THE THIRD SHAPE — one function per BUCKET, and a pure predicate only where one is needed

Both A and B are mechanisms for arbitrating BETWEEN ROWS IN A BUCKET. Two of
pcrec's four doorways already have no such mechanism, because one function
handles the whole bucket: `pcrec_ext_class_bracket` (all three class rows, K3/K4's
scan as control flow) and `pcrec_ext_verb` (D25's four answers and both name
tables as control flow).

So: **one function per bucket.** Precedence becomes `if`/`else` inside a single
function — local, greppable, visible in a diff, testable in isolation. It cannot
couple across rows, cannot be perturbed by table position, and needs no integer.
**It deletes both precedence mechanisms and every check either needed.**

It also dissolves P2's declared-vs-actual gap rather than mitigating it: that gap
exists because B keeps metadata making a claim about a function's behaviour while
the function may disagree. Under one-function-per-bucket there is no competing
claim — the function's control flow IS the precedence.

And P1's finding that a decide/build boundary must be STRUCTURAL is honoured
proportionately: the boundary is only needed where something asks
speculatively, and there is exactly **one such customer in the parser** —
`pcrec_ext_class_pair_opens`, already pure, at one doorway. Three doorways need
no split; one does and already has it.

## Dispositions

1. **Design B's order-as-precedence is REJECTED** (P2).
2. **Trial mode is REJECTED** (P1) — self-defeating, and it buys nothing over
   calling an already-pure function.
3. **The three-outcome protocol is REJECTED as uniform**; the terminal outcome
   must be selected by the row's existing vocabulary, i.e. what `ext.c` does now.
4. **Design A's rank survives R12 but not R11** — still 20 of 22 values
   unconstrained, still two coincident checks.
5. **One function per bucket is the candidate to take forward**, with a pure
   predicate only at the class doorway. NOT yet panelled; it emerged from this
   panel and has not been attacked.
6. **Two doorway epilogues (GROUP, VERB) do not exist as code** and should be
   written regardless of which design wins.

## Reflection

The narrow-brief format worked: 4 of 4 delivered against R11's 2 of 4. Every
substantive finding was a correction to the author, and the two most valuable —
P1's and P2's — were produced by BUILDING the proposal rather than reasoning
about it. P2's repro needed no hypothetical edit at all; it ran design B against
the shipped table and watched it fail.

The pattern worth keeping: **a design that cannot be run should be simulated
against the real data before it is adopted.** D30's rank was measured that way
and survived; design B was not, and did not.
