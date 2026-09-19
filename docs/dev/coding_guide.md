# CODING GUIDE — read before writing C in this tree

Distilled from the 2026-09-17 code review (`docs/dev/reviews/2026-09-17-code-review.md`;
per-lens evidence in `reviews/lens_reports/`). Rules only, each with WHY in one
sentence and its source, so a doubter can follow the evidence.

**Scope:** you are about to edit `src/`, `cli/`, `lib/` or add a check under
`tests/`. Read this once at lane start. It does not replace
`docs/dev/learnings.md` (process + check-design lessons, cited below, never
restated) or the root `CLAUDE.md` situation index (the triggers).

**Marked `[wave N]`** = the rule changes when that refactor wave lands. Until
then the rule as written is the tree's truth. Never instruct a reader to use a
primitive that does not exist yet.

---

## 1. House disciplines — verified by the review, do not break

The review checked these tree-wide and found them holding. Each has exactly one
known hole, named. Breaking one of these is a regression, not a style choice.

**1.1 Every allocation failure routes through `ctx_nomem`.** pcrec is a library;
an `abort()` on OOM kills the caller's process (K7's worst item). `arena_alloc`
already routes through the arena's `.cx`; allocation is architecturally confined
(`emit_vm.c`, `parse.c`, every `mod_*.c` and most of `opt/` have ZERO raw
allocations — L8-H8), so a raw `malloc`/`calloc`/`realloc` you add is a finding
against you unless it routes.

**1.2 The Job-buffer attachment rule, stated as a RULE:** *every `StrBuf` the
`Job` owns gets `.cx = &cx` as soon as the `Job` exists* — `src/core/compile.c:756-762`.
Not "the four buffers": the comment said four, there were six, and the two
unattached ones (`scr_test`/`scr_desc`) were a live caller-`abort()` reachable
from ordinary VM-route patterns (L8-F1, fix-now #1). If you add a buffer to
`Job`, you attach it in the same edit.

**1.3 No `default:` arm on an `AKind`/node-kind switch.** The exhaustive switch
IS the alarm that fires when a kind is added — `-Wswitch`, promoted by
`make strict`. The rule's home is `src/opt/mrl.c:18-24`; `src/opt/atomic.c`'s
header states it for its own seven switches and says why: "can this construct
contain a cut" is a question only the author of the new kind can answer, and
inheriting the wrong answer is silent in every case.

**1.4 Anything crossing a `setjmp`/`longjmp` boundary is `volatile`.**
`compile_driver` (`src/core/compile.c:595-691`) is the pattern — every scalar
that survives the retry loop, the loop counter included. `-Wclobbered` under
`make strict` is the backstop and the discipline is complete today (L8-H2), with
one caveat: `-Wclobbered` is vacuous at `-O0`, so the compiler will not catch you
in a debug build. These declarations are NOT noise and do not get "cleaned up"
(L11 §5.1 item 4).

**1.5 Zero function-local statics; file-scope mutable state is write-once.**
Library re-entry depends on it — verified clean tree-wide, the three file-scope
mutables being write-once at spec-parse time (L8-H7). A `static int cache` inside
a function is a re-entrancy bug in a library, not an optimization.

**1.6 Never `free()` an arena-backed pointer.** All 76 free sites were classified
and all are correct (L8-H3); arena storage dies with the compile's arena. The
hand-freed heap tables in `minimize.c` (five) and `scanedge.c` (nine/ten) are the
named exceptions and are correct on every exit (L8-H5/H6) — match their shape if
you add one, and say why the arena was wrong for it.

**1.7 Single-letter locals in the emitters ARE the house convention.** `c` the C
string buffer, `d` the `Dfa`, `p` the prefix, `b` a `StrBuf`, `v` the `Vm`, `st` a
state, `r` a row — applied identically across `emit_dfa.c`, `emit_vm.c` and
`rxt_source.c` (L4-P1). Do not "fix" them; renaming buys nothing a reader of two
files does not have and is exactly the violence §4's rubric warns about.

**1.8 `src/core/limits.def` is the one home for a numeric limit (D90)** — and the
boundary matters in both directions. A `limits.def` row is *a value a pattern can
be measured against*. A scratch-buffer size is NOT one and does not get a row
(L3-F6 declines to propose 94 of them; L10 §2.4 confirms). A tuning constant that
is neither (`C_MEMCHR`, `SIZE_TERM_BAR_DEFAULT`) is today invisible to
`limits_check.sh`'s name-keyed detector — that is L3-F1, a check defect, not your
licence to open-code a new one.

---

## 2. Taught primitives — reach for these, in their state TODAY

**2.1 `sb.c` is the text mechanism: `sb_putc` / `sb_puts` / `sb_printf` /
`sb_take` / `sb_free`** (`src/core/internal.h:62-67`). The emitters' 771 `sb_*`
call sites ARE the norm — lens 2's own seed hypothesis ("the emitters use neither
sb nor stdio") was REFUTED by measurement. There is deliberately no `emit_line()`
wrapper and there will not be one (L10 §2.3): it buys nothing `sb_printf` does not.

**2.2 Formatted fragments: size from `PCREC_MAX_EMIT_NAME_LEN`, never by hand.**
Any buffer holding an emitted identifier or sub-expression built from the `-p`
prefix is sized `PCREC_MAX_EMIT_NAME_LEN` (`limits.def:134` =
`PCREC_MAX_PREFIX_LEN + 96`). K38 is the recorded miscompile of exactly its
absence. **`sb_fragf` (landed 2026-09-18, wave 2 stage 3) is now the answer,
and a new fixed scratch buffer in either emitter is a finding against you.**

```c
const char *sb_fragf(Arena *a, const char *fmt, …);   /* core/internal.h */
```

Arena-owned text sized exactly to the result: truncation is impossible by
construction rather than by a per-site size argument. The result lives for the
whole compile, which is what makes it safe to hand to an `sb_printf` `%s` far
below the site that built it — the thing a stack buffer could not do.
Allocation failure routes through `ctx_nomem` via the arena's own `.cx`
(§1.1). It takes an `Arena *` and nothing else on purpose: D108's data-in /
text-out rule, so a back-end fed from a deserialized IR calls it unchanged.

**Three things it is NOT for.** A buffer whose EMPTY value is load-bearing
(the conditionally-filled `char tr[N] = ""` trace inserts, whose emptiness is
a byte-identity contract) becomes `const char *tr = "";` plus a conditional
assignment — same shape, but the `""` default is the point. A buffer read back
and mutated in place after it is written is not a fragment. And a buffer whose
VALUE IS STREAMED into the destination by a callback rather than held by the
caller is not one either — `emit_dfa.c`'s `<PREFIX>_DFA_PREFILTER_OFFSETS` is
the tree's one instance and says so at its site.

**What is left, and it is a closed list.** Six fixed scratch declarators
remain across both emitters and all six are the ENCODING-SEAM GUARD/ADVANCE
family — the `enc.h` seam entries' `buf`+`cap`+`trunc` output contract, which
belongs to the encoding module (DD-12), and the destinations of
`pcrec_startpos_guard_text`. Their text carries the caller's indent and the
backend's expression and NEVER the `-p` prefix, which is what puts them
outside the K38 class (`limits.def:360` says exactly that). A seventh, `Vm.up`,
retired in wave 2 — see §2.6. `tools/review/fragment_census.py` is the count.

**Its no-truncation promise is enforced by the `vsnprintf` SIZE argument, not
by the allocation.** Measured: an allocation one byte short is invisible to
`tests/core/sb_fragf_check.c` AND to AddressSanitizer, because `arena_alloc`
rounds to 16 and zeroes, and ASan sees only the arena's own block `malloc`,
never the intra-block slice. Know which half is checked.

**2.3 Use the file's own declared helper instead of re-deriving it.**
`vm_slot_expr` (`src/gen/emit_vm.c:940`) exists precisely so that "every site that
names a slot inside an emitted expression spells it the same way `vm_set` does —
the alternative is each site re-deriving `<PREFIX>_` + `vm_slot_name`, which is
three spellings of one convention." Its own header names hand-derivation as the
defect, and four sites do it anyway (EP2-E1). Before you hand-roll an expression,
grep the file for the helper that already builds it.

**2.4 Walking the AST: copy the spine discipline, do not invent one.**
`A_CAT`/`A_ALT` spines are LEFT-NESTED and as long as the pattern, so a walk
descends a spine ITERATIVELY and recurses only into items hanging off it (a
20,000-character pattern segfaulted pcrec once for want of this — K20, D10/DD-10).
A whole-tree walk must NOT follow `Ast.u.call.body`, the AST's first back edge,
and each `A_CALL` arm says why declining it is exact. `src/opt/atomic.c:22-36` is
the canonical statement — cite it, copy it. `pcrec_ast_visit` (`core/internal.h`,
landed FIX-NOW #10/L1-X2, 2026-09-17) is the ONE home for the generic
pre-order whole-tree visit with no rewrite and no thread — use it rather
than writing a new copy. **[wave 2 / L1-X1]** the other 75 hand-written walk
sites (each with its OWN edge policy — a rewrite, a threaded accumulator, a
reversal) stay separate walks by design; only a walk that is genuinely this
same generic shape merges into `pcrec_ast_visit`, and until L1-X1's staged
sweep reaches a given site you are still copying the two rules above
verbatim there.

**2.5 Ownership.** The compile's `Ctx` owns the arena; the arena owns everything
allocated from it; the caller owns nothing you did not hand back through the
documented API. A helper that can fail takes `Ctx*` so it can diagnose — the three
arena `strndup` helpers in `mod_backrefs.c`/`mod_named_groups.c`/`mod_recursion.c`
are the correct shape, and `rxt_source.c`'s bare-`Arena` pair is the counterexample
that aborts instead (L8-F4).

---

**2.6 Emitting an artifact stamp: `sb_stampf` / `sb_stampwf` / `sb_stamp_str`**
(`core/internal.h`, landed [REVW.2] wave 2, 2026-09-18). One
`#define <UPPER>_<NAME> <value>` line. All 73 former hand-written stamp sites
across `emit_vm.c` (52) and `emit_dfa.c` (21) are on them, and a new
hand-written `sb_printf(c, "#define %s_...")` is a finding against you.

```c
sb_stamp_str(c, up, "VM_PREFILTER", "hybrid");   /* owns the quoting */
sb_stampf   (c, up, "VM_RUNGS", "0x%xu", rungs); /* the value is a FORMAT */
sb_stampwf  (c, up, "R_STEPS", 9, "%s", "((ptrdiff_t)PCREC_ERR_STEPS)");
```

**The value is a format, not a type, and that is the rule not an accident.** A
stamp's value is emitted C: `0x%xu`, `%lluULL`, `%lldLL` and a raw
`((ptrdiff_t)…)` are four C tokens with four meanings to the artifact's own
compiler. Do not "clean up" a site onto a typed integer helper — lens 1
proposed one and it is deliberately not built, because it covers 9 of
`emit_vm.c`'s 37 value stamps and silently moves the emitted bytes of the
rest. `namew` left-pads the NAME field for the two families that align their
value column; that alignment is emitted bytes and §3.1 governs it.

**They are for a VALUE stamp and not for a function-like macro.** The 15
`#define %s_` lines still in `emit_vm.c` are seven multi-line macro BODIES
with backslash continuations (`_CHARGE_WORK`, `_TRAIL`/`_SET`/`_PUSH`/`_CUT`,
`_CALL`, `_TIER_NOTE`, the `_PRUNE_*` pair) whose emitted text is a program,
not a value. They stay `sb_printf`, and four sabotage rows sit on them.

**The uppercased prefix is ONE derivation**: `sb_upper(Arena *, const char *)`.
`GenNames.upper` and `Vm.up` are both `const char *` pointing at its one arena
result; neither is storage any more. Do not re-derive an uppercase at a call
site and do not add a third field.

## 3. Emitted text — the rules with teeth

**3.1 Any change to an emitted byte IS an `abi` event.** Comments, declarations,
layout, whitespace — all of it (D76/D94). The change carries the bump, the
identity-gate re-pin and the spec hunk in ONE commit; `abi` is **26** today
(`src/gen/emit_dfa.c:1965`). Find readers **by grep**, never by memory — a
hand-enumerated "four sites" list missed a fifth in `match_api.md` (D94). And grep
for the digit is not sufficient on its own: a manifest whose rows never cite an
abi number can still hold byte COUNTS that move (lane `battriage`, 2026-09-17), so
recompile the witnesses a manifest pins. Run `make test-codegen` before delivering.

**3.2 Escape every pattern-derived byte you put in an emitted comment.**
`emit_comment_safe_byte` (`src/gen/emit_dfa.c:80`) is the shared primitive: it
hex-escapes anything that would complete `*/` **or** `/*` with the previous byte
(threaded via `*prevp` across calls), plus whatever the caller's `extra_escape`
predicate asks for. Both hazards are real — gcc's `-Wcomment` fires on an unclosed
`/*` and the harness's own `GENCFLAGS` is `-Wall -Wextra -Werror`
(`tests/harness/run.sh:213`). Lane `cmtfix` / O-31 F1 is the incident.

**3.3 Know what the identity gates do NOT see.** The four byte-identity gates
compare the `.c` artifact. `vm_render_listing` writes `&job->irsb` — the
`--emit-ir` listing — and NO identity gate reads it; its only comparator is
`tests/codegen/run_ir_listing.sh` (EP2 §1). Touch a listing-writing buffer and you
owe that arm explicitly, or your "byte-identical" claim is about a different stream.

**3.4 Near a sabotage anchor, KEEP COLUMNS.** `tests/mech/lib/replace.py` matches
`SAB_BEFORE` as a whole-file, line-agnostic substring, so a verbatim relocation
costs zero re-aims and a RE-INDENTATION breaks the anchor (92 of 94 `emit_vm.c`
anchors carry leading whitespace — EP2 §3.5). Price a move by "does the moved text
keep its column," not by lines moved.

**3.5 Find anchor populations by grep, and treat the count as a FLOOR.**
`grep -rl <identifier> tests/mech/sabotages/` on YOUR tree. Rows quote CALLERS, so
the identifier you are moving may be anchored from a file you did not expect, and
~24 rows' `SAB_DESC` text has already drifted from what they plant. Never cite a
count from a report as a site list without re-running it (L10 §2.4; L11/EP2).

**3.6 Anything a caller can observe carries its `docs/spec/` hunk in the same
change** (D80) — an entry, a flag, a stamp, a limit, a diagnostic tier, a module's
behaviour. A reviewer rejects a contract change without its spec hunk.

---

## 4. Function composition — the altitude rubric

Frank's rule, verbatim from the ratified criteria (lens 11): a C function targets
a code-line limit — "fits on a screen" — stated with its own warning: *"this is
the kind of rule that can be perverted into doing violence against good design.
It's a tool that can be used for good and evil."*

So **length is a TRIGGER, never a verdict.** A function over a screen gets reviewed
against five questions:

1. Is all the code at the RIGHT LEVEL — not too detailed (extract it) and not too
   general? A function's body should sit at roughly ONE semantic level.
2. Is it all part of the same simple semantic purpose — and is that purpose clear
   from the NAME?
3. Is it appropriately code-driven vs DATA-driven for what it does (a switch ladder
   that should be a table, or a table that should be code)?
4. Are variations LOOPED rather than inlined N times?
5. Are optimizations weighed — never taken at the expense of clarity and simplicity
   unless the cost is clearly understood, and *"if the code can't explain itself the
   comments should."*

**A long function that passes all five STAYS LONG, and you say so.** Thirteen
functions in this tree passed and are listed in collation §5 — do not re-open them.
The editing principle governs the whole rubric: *"Editing is equally as important as
writing. Cut away everything that is not the elephant."*

**4.1 Common extracts FIRST (ratification ADDENDUM 1).** The remedy for a too-long
function is first the shared idiom/missing-library extraction, not an ad-hoc split:
the two loop — an extraction re-scores the length population, and an over-N function
is examined for extract candidates before any function-specific restructuring is
proposed. `emit_predicate_axes` (178 lines, not one `if` or loop) is the pure case:
the axes-table centralization IS the whole remedy and no split is proposed at all.

**4.2 Comments carry invariants and why-not-the-alternative; HISTORY goes to docs
with a pointer.** A function header, sized to the function, answers (a) what it
produces, (b) what it reads that is not a parameter, (c) the one invariant a caller
must not break (L4-C1). Most of that text already exists inside the body and can be
hoisted rather than composed. Wave narratives, panel citations and change logs
belong in `docs/` — the `abi` change log lives in three drifting homes today and two
transitions are recorded nowhere (L4-A1), which is what that costs.

---

## 5. Writing a check

**Read `docs/dev/learnings.md` §3 first** (and memory `pcrec-check-design-lessons`)
— the full catalogue lives there and is not restated here. The 2026-09-17 review
added five fresh instances of the same shapes, found by five different lenses on
five different surfaces, which is the argument that the shape is systemic:

1. **A control must not share a source with what it controls.** The include-graph
   instrument cannot see 31 of 39 call-level back-edges because `core/internal.h`
   declares them all — metric and architecture route through the same header (L6-L2).
2. **Count the population, and fail on an empty one (K35).** L10's stage-3
   acceptance criterion would have passed with a whole third sizing category
   untouched — the K35 shape appearing INSIDE a criterion written days earlier to
   retire an instance of it (EP2 (a)).
3. **A witness must REACH its site ([MECH-REACH]).** The cautionary tale: the tree's
   only long-prefix control compiles the pattern `a`, reaching essentially none of
   the 48+ buffers it exists to guard (L10 §2.2). Measure the reach; do not assume it.
4. **Name-keyed filters are the recurring blind spot.** `limits_check.sh` filters on
   ceiling vocabulary in the constant's NAME; the repair after its first miss widened
   the vocabulary instead of changing the filter's KIND, and the miss recurred
   (L3-F1). If your filter is a name list, say what it cannot see.
5. **A check needs a failing-direction story before it is written.** Run it against
   the unrepaired defect and record the red. L8-F6 is what the absence looks like:
   the ctx_nomem discipline's only positive control is Darwin-skipped, so it has not
   run on the dev box since the two-machine split — and the F1 hole shipped in
   exactly that window.

Also standing: a check's FAILURE MESSAGE is a second, undeclared claim about the
space of causes, and it goes stale with the check (`w23impl_report.md`,
`dialimpl_report.md` — two arms went red blaming the witness while the table was wrong).

---

## 6. Do NOT — the probed-and-held list most likely to tempt you

Each was examined with evidence and held. Re-opening one needs new grounds, in
writing. The full record is collation §5.

- **Do not merge the nine `atomic.c` predicate walks.** Every one differs in at
  least one per-kind arm with a measured justification; a naive merge deletes two
  sabotage plant sites and the `-Wswitch` alarm in one commit. Only the TRAVERSAL
  is extractable, never the verdicts (L1 §5 + L11 §5.1 item 3, found independently).
- **Do not table-drive the rung emitters.** The table would have to carry the
  emitted control-flow graph itself — differing label counts, slot families, frame
  discipline, fail-label semantics (EP2 §6 item 1). This is question 3 answering
  "correctly code-driven."
- **Do not rename the emitters' short locals** (§1.7).
- **Do not add `limits.def` rows for scratch-buffer sizes** (§1.8).
- **Do not write unit tests of an emitted shape.** A unit test of a rung's emitted
  shape duplicates oracle coverage and is explicitly the thing lens 5 must not
  recommend (L5 §7).
- **Do not touch the four `syntax_dump.c` enum→string mappers** (D82 bound 3 + the
  D75 addendum), **the template layer** (closed by measurement, population 1 — not
  deferred), **the 22 public denial bits** (D46/D47.3), or the 56% comment ratio
  (not a finding).

---

*Maintenance: this guide states rules, not findings. When a wave lands, delete the
`[wave N]` marker and restate the rule in its new form. When a rule is re-learned
the hard way, add a line with its incident — never a paragraph.*
