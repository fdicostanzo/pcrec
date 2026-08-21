# Registry built-status field — decision memo

PROPOSED, unbuilt. Written by the REGSTATUS lane (2026-08-21) per the
[M6.2] repair slice's refutation (docs/dev/dev_journal.md, 2026-08-19 part 6,
"ITEM 3 REFUTED"; the same finding is archived at docs/dev/plan_completed.md's
`## 2026-08-21` [M6.2] row). Read the "How to read the generated index below"
section of docs/pcre2_compliance.md (added by the repair slice, line 592)
before this memo — it is the interim measure this memo is meant to retire or
shrink.

## The problem, in three sentences

The generated index at the bottom of docs/pcre2_compliance.md renders each
registry row's `status`/`roadmap` fields (`RegStatus`/`Roadmap`,
src/core/internal.h:791-827), and those two fields answer "is this base
grammar, and if not, who owns it" — a fact about PCRE2 and about pcrec's base
grammar, not about what pcrec has built. Because of that, 34 rows belonging to
four SHIPPED modules (`classes` 12, `modifiers` 12, `assertions` 7,
`named-groups` 3 — measured 2026-08-19 by `pcrec --list-syntax`, docs
line 602) read `REJECTED | planned` identically to a module with zero
producers. The [M6.2] wave E lane misread that as staleness specific to module
`assertions` and proposed flipping its eight rows to `RS_BASE`; the repair
slice refuted the flip on measurement, not on taste — 34 rows read the same
way, so flipping eight would make the index *inconsistent* (`\d` and `\b`
would then disagree with each other on the same fact), it would break the
`RS_BASE => ROADMAP_NONE` pairing `registry_check.c` enforces (§ "the MOD-0.1
item... legal pairings", internal.h:818-822), and it would delete the module
name from the gate-CLOSED "requires module 'X'" diagnostic that tests/reject/
pins. The refutation named the real fix as "a registry BUILT-STATUS field...
a whole-registry design question" — this memo.

## What "built" already means at runtime, and where it already lives

There is no declared "built" field anywhere in the registry today, but there
IS an existing, already-measured, per-construct signal the compiler computes
on every compile: a `RegRow` carries two producing ports, `aport` (atom
position) and `cport` (class position), each an `ExtPort{PortKind kind, ...}`
(internal.h:1152-1173). `PortKind` is `PORT_NONE` (no producer — "the row
refuses with its own diagnostic") or `PORT_SCALAR`/`PORT_SET`/`PORT_FN` (a
real producer). ext.c's `UNBUILT` macro (ext.c:171-173, doc comment
ext.c:144-170) already renders this distinction as a *diagnostic*: when a
row's module is enabled (its `FEAT_*` bit set, checked by `pcrec_ext_gate`)
and `WANT_RESULT` is asked, but the row's port is `PORT_NONE`, the refusal is
"module 'X' is enabled but Y is not implemented yet" — never "requires module
'X'" (that wording is reserved for a CLOSED gate, and would be a lie once the
module is on). This mechanism's own header is explicit that it deliberately
reads off ONE source rather than a second column: "The condition is read off
ONE source, and deliberately not off a second `built` column somebody would
have to keep in sync with the ports... reaching this point at WANT_RESULT
means the gate was OPEN and the port block above declined" (ext.c:152-158).

This is not a narrow or rare code path. tests/reject/run_reject_tests.sh:711
records that its population is "EVERY registry row whose module is enabled
and whose port is unwired, and that set is large and live today", pinning
four rows from three ENTIRELY-unbuilt modules as the control since module
`assertions` (the mechanism's original motivating case) closed at wave E and
left it with zero rows of its own to pin (run_reject_tests.sh:711-751):

```
reject_gated backrefs      '\k'    "module 'backrefs' is enabled but \k is not implemented yet"
reject_gated lookaround    '(?=a)' "module 'lookaround' is enabled but (?=...) is not implemented yet"
reject_gated atomic-groups '(?>a)' "module 'atomic-groups' is enabled but (?>...) is not implemented yet"
reject_gated quoting       '[\Q]'  "module 'quoting' is enabled but \Q in a class is not implemented yet"
```

So the runtime ALREADY answers "is this construct built" correctly, per
construct, for every row whose port is the row's sole producer — which is
every `RK_ESC` and `RK_CLASSBRACKET` row, and every `RK_GROUP` row wired
through the [M6.3] GENERAL producer-invocation path (`group_answer`'s
`aport.kind == PORT_FN` branch, src/parse/CLAUDE.md's ext.c entry). The
question this memo answers is not "does pcrec know whether a construct is
built" — it does, and proves it on every `make test` run through the
`reject_gated` pins above — the question is how to SURFACE that fact in the
generated index without inventing a second, driftable source.

**One granularity mismatch is worth flagging up front.** `aport.kind !=
PORT_NONE` is a per-ROW fact, and it is accurate wherever one row is one
construct (true of every esc/class-bracket row and of named-groups/classes).
It is NOT reliable at ROW granularity for a producer SHARED by several rows
that dispatches on the row's own `sel` internally: module `modifiers`' twelve
`GROUP_OPT` rows (registry.c:728-743) all share one `aport` PORT_FN,
`pcrec_modport_optrun` (wired at MOD-0.5c), and that one function's `switch`
decides each letter's real-vs-refused status internally
(src/parse/mod_modifiers.c:276-373) — so `aport.kind` reads "wired" for all
twelve letters even during the interval (documented at
mod_modifiers.c:285-322) when only `i`/`s`/`U`/`n`/`x`/`r`/`a` were real and
`m` still refused "requires module 'assertions'" (pre-[M6.2] wave C). This is
exactly the shape the refutation is about, one level down: a shared-dispatch
family can be built for SOME of the names/letters it recognises and not
others, and the row-level port field cannot see the difference — only a LIVE
PROBE of that specific row's own `syntax` can. (`module `verbs``'s single
`verb_rows[0]` is the same shape at the extreme — up to 50 names dispatched
by NAME through mod_verbs.c's own tables, "a direct call, not a port"
src/parse/CLAUDE.md — but is a degenerate case for THIS memo: it has zero
producers today, so a whole-row "unbuilt" is exact.)

## Field semantics options

**Option 1 — per-module** (built | unbuilt, one value per `FEAT_*` bit).
REJECTED for the same reason the wave-E flip was refuted: module
`assertions` spent five real, merged, tested waves between 2026-08-19 (part
1) and 2026-08-19 (part 4) at 3/8, 5/8, 6/8 (+ the cross-module `m` letter),
7/8 and 8/8 constructs built (docs/dev/dev_journal.md, the four wave entries
at lines 10583, 10683, 10765, 10807) — at every one of those points except
the last, a per-module field would have had to read either "unbuilt" (false
for the constructs already shipped and pinned live in
tests/assertions/run_assertions_tests.sh) or "built" (false for the
constructs still refusing via `UNBUILT`, pinned live in tests/reject/'s
gate-closed rows). There is no module-level answer that is not a lie during
a real, weeks-long, tested, merged interval — the identical shape the
refutation used to reject flipping assertions' rows wholesale.

**Option 2 — per-construct** (RECOMMENDED). One value per registry row (or,
for the two shared-dispatch families noted above, per row where the row IS
the construct — which is every row except `verbs`' single catch-all and
possibly `modifiers`' GROUP_OPT family, addressed as an open question below).
This is what the runtime already computes and what `reject_gated`'s pins
already assert row-by-row.

**Value vocabulary**: three-valued, not two. `RS_BASE` and `RS_REJECTED`
rows have no module and no port to ask about — the built/unbuilt question
does not apply to them, and rendering it as false would misleadingly suggest
`\d` is "unbuilt" alongside genuinely-unimplemented module rows. Recommend
`built` / `unbuilt` / `—` (n/a, for `RS_BASE`/`RS_REJECTED` rows), mirroring
how the existing generated table already renders `roadmap` as `—` for
`RS_BASE` rows (compliance_section.py:100).

## Population options

**Option A — declared column** (a new hand-authored `built` field on
`RegRow`, flipped in the same commit as a producer lands). REJECTED: this is
precisely the "second `built` column somebody would have to keep in sync
with the ports" that ext.c's own UNBUILT-macro comment already declined to
build (ext.c:152-155), and it is the general shape this project's
check-design lessons name explicitly — a control (a check asserting the
column is right) sharing a source with the thing it controls (a human typing
the column) catches nothing an author who is already wrong would not also
get wrong in the check. It also reproduces the D24 "two-homes" failure mode
the whole registry exists to prevent (`\v`'s decoding bug, cited in
src/parse/CLAUDE.md's opening paragraph, is the project's own example of
what two homes cost).

**Option B — derived, registry-check-only** (a new assertion in
tests/registry/registry_check.c or tests/registry/pcre2_check.c that drives
each row's own `syntax` through the gate-open `WANT_RESULT` path — the same
call shape `doorway_call`/`pcrec_probe_ask` already use,
src/parse/syntax_dump.c:386-448 — and classifies the outcome, asserted but
never surfaced in the generated doc). COST: closes the "is the claim
checked" question but not the actual problem this memo exists to fix, which
is that a human reading docs/pcre2_compliance.md cannot currently tell
shipped from unbuilt without reading the "How to read" prose section first.

**Option C — derived at dump time** (RECOMMENDED). Extend
`pcrec --list-syntax` (src/parse/syntax_dump.c) with a new column computed
the same way `--probe-ask` already computes `answered_at`
(syntax_dump.c:418-448's own doc comment): for each `RS_MODULE` row, force
its own `FEAT_*` bit on in an isolated `Ctx` (the same isolation
`doorway_call`'s callers already use — "BOTH QUERY SURFACES `setjmp` THEIR
OWN Ctx", src/parse/CLAUDE.md's syntax_dump.c entry), call the row's own
doorway with the row's own canonical `syntax` at `WANT_RESULT`, and classify
the `ExtResult`: a produced answer (`EXT_NODE`/`EXT_MEMBERS`/`EXT_SCALAR`) is
`built`; a refusal whose text matches the `UNBUILT` shape ("module '%s' is
enabled but ... not implemented yet") is `unbuilt`; any OTHER refusal for a
row's own well-formed `syntax` (SR-1's own rule already requires every row's
`syntax` to "really reach that doorway") is a registry defect, not a status,
and should fail a `registry_check.c` assertion loudly rather than render
silently. `RS_BASE`/`RS_REJECTED` rows are `—` without a call.

This is the same "cannot drift from the compiler because it is printed by
it" property SR-4 already gives the rest of the generated index
(compliance_section.py's own docstring, quoted at
docs/pcre2_compliance.md:637): the column is not a claim about the code, it
IS a measurement of the code, taken the same way `--probe-ask`/`--explain`
already take one for a different axis (election/promise/attribution,
design_notes_mod07.md §5.2). It costs one new TSV column
(`compliance_section.py`'s `COLS` list, tests/registry/compliance_section.py:42,
plus the `dump()` row-count assertion which stays unchanged since no rows
are added) and one new helper in syntax_dump.c reusing existing plumbing —
no new source of truth, no second home.

## Consumer changes

- **`pcrec --list-syntax`** (syntax_dump.c): gains one new column,
  `built` — the derivation in Option C. Every other column is unchanged;
  SR-4's "columns are APPENDED, never reordered" rule (src/parse/CLAUDE.md's
  syntax_dump.c entry) is honored by appending it last.
- **`compliance_section.py` / the generated index**: gains a `built` column
  in the rendered table, alongside the existing `status`/`roadmap`/`module`
  columns. The 34 shipped-module rows now read correctly without the reader
  needing the "How to read" prose to explain why they don't.
- **`registry_check.c`**: gains one new assertion, the Option-C classifier's
  own defect check (any row whose own `syntax` fails to classify cleanly as
  built or unbuilt is a registry defect, reported by name) — NOT a
  hand-maintained population count by itself, though a floor/count guard in
  the SR-1 style ("N rows currently read `built`") is worth adding so a
  producer that silently regresses is visible in the diff, the same
  reasoning tests/reject/'s and registry_check's other exact-count
  tripwires already use (with their own documented limit: an exact count
  makes a change VISIBLE, it does not make a WRONG one FAIL —
  tests/registry/CLAUDE.md, "R8/C4-10 measured").
- **PC-3 (`pcre2_check.c`)**: UNCHANGED. It measures RECOGNITION against
  libpcre2 (does PCRE2 have this construct, and does pcrec's `RS_MODULE`
  row's claim survive an external oracle) — a different question from "did
  pcrec build it", and D26's tiering (compatibility is measured against
  PCRE2, wording is not) does not move: this memo is entirely about the
  index telling the truth about pcrec's OWN state, never about matching
  PCRE2 further.
- **tests/reject/**: UNCHANGED. The `reject_gated` pins stay the hand-written
  control (tests/registry/CLAUDE.md's own standing rule: "the control for a
  wrong module name is the hand-written table in tests/reject/, never
  [compliance_section.py]" applies here too — a derived `built` column is a
  drift detector, not proof the row is RIGHT to be built).
- **`RegStatus`/`Roadmap` and their `RS_BASE => ROADMAP_NONE` pairing**:
  UNCHANGED. This memo adds an orthogonal THIRD axis (is it built) beside
  the existing two (is it base grammar; will a module ever implement it) —
  it does not touch `internal.h`'s enums, `registry_check.c`'s pairing
  rule, or any row's `status`/`roadmap` value. The `(?J)` row is a clean
  worked example of why the three axes must stay separate: `RS_MODULE` +
  `ROADMAP_PLANNED` (D38: PCRE2_DUPNAMES is real, planned-later capture
  machinery) + `built = unbuilt`, permanently and unconditionally (its
  refusal at mod_modifiers.c:352-357 does not even consult the gate) — a
  cell no two-axis scheme can represent honestly.
- **Gate-CLOSED diagnostics** ("requires module 'X'"): UNCHANGED. The
  `built` column is read at an ARTIFICIALLY forced-open gate for
  measurement purposes only; it does not change what a real compile with
  the module actually disabled reports, and does not touch ext.c's
  `REFUSE`/`UNBUILT` text.
- **The "How to read the generated index" section**
  (docs/pcre2_compliance.md:592-626): SHRINKS, not deletes. Once `built` is
  a real column, the paragraph explaining "the shipped status lives in the
  PROSE rows above, not here" (line 607) is answered by the table itself and
  can go; the RS_BASE-is-a-PCRE2/base-grammar-fact explanation (lines
  594-600) is still worth a short paragraph for a first-time reader, and the
  wave-E history (lines 614-626) is worth keeping as a citation of why the
  column exists, shortened to a sentence pointing at this memo instead of
  re-deriving the argument in place.

## Risks and the check-design question

The standing project lesson (this memo's own brief quotes it: "controls
sharing a source with what they control") is why Option A (a declared
column) is rejected above, and it is worth restating why Option C does not
reproduce the same failure. A declared column's check would have to
independently re-derive the expected value to compare against — and the only
independent way to know whether a construct is built IS to drive the
compiler, which means the "independent" check and the declared column would
converge on asking the same question through two different code paths that
could each be wrong the same way (the tests/registry/CLAUDE.md "R4/R5/R6"
history: "a row that is plausibly WRONG in the single home is invisible,
because the wrongness is what both sides read" — measured three separate
times in this project already). A derived column has no second path to
converge with: the SAME call that decides what the CLI's `--list-syntax`
output says is the same call a real compile with the module enabled would
make (`pcrec_ext_gate` + the row's own `aport`/`cport`), so a bug in the
derivation is a bug in the dump binary, visible the moment anyone diffs
`--list-syntax` against a real compile's behavior — which is exactly SR-4's
existing "cannot drift from the compiler" guarantee, extended to a new
column rather than invented for it.

The one honest residual risk: the classifier's OWN text-matching of the
`UNBUILT` refusal shape (Option C, "a refusal whose text matches...") is a
STRING comparison against ext.c's own format string, so a reworded `UNBUILT`
macro that is not also updated in the classifier would misclassify unbuilt
rows as "other-refusal" (registry_check's defect-check catching a change
that did not need catching) rather than silently mislabeling anything as
`built` — a fail-loud direction, not a fail-silent one, but worth a same-TU
guard (share the fixed prefix string as a `#define` both sites include)
rather than two copies of the sentence.

## Open questions for Frank

1. **Field semantics: per-construct vs per-module.** Recommend
   per-construct (Option 2) — per-module repeats the exact mistake the
   repair slice refuted, one level coarser, and module `assertions`' own
   five-wave history is the measured proof a module-level value would have
   lied at four of five checkpoints.
2. **Population: declared vs derived-at-dump-time vs derived-in-test-only.**
   Recommend derived-at-dump-time (Option C), extending `--list-syntax` with
   a `built` column computed by driving each row's own doorway at a
   gate-forced-open `WANT_RESULT` — no second source of truth, reuses
   `doorway_call`/`pcrec_probe_ask`'s existing isolated-`Ctx` machinery.
3. **Value vocabulary: two-valued vs three-valued vs a fourth defect
   bucket.** Recommend three-valued (`built` / `unbuilt` / `—` for
   `RS_BASE`+`RS_REJECTED`) rendered in the doc, plus a registry_check
   assertion (not a rendered value) for the "well-formed syntax produced
   neither a clean answer nor the UNBUILT shape" defect case.
4. **Fate of the "How to read the generated index" section.** Recommend
   shrink-not-delete: keep the RS_BASE/RS_MODULE explanation, retire the
   now-redundant "the shipped status lives in the prose, not here" caveat,
   and compress the wave-E history to a citation of this memo.
5. **Row-granularity mismatch for `verbs` and `modifiers`.** `verbs`' single
   catch-all row (Q1/D25's separate `VerbName`/`VerbTable` schema, not
   `RegRow` at all) has zero producers today, so a whole-row `unbuilt` is
   exact and needs no finer resolution yet — mirrors [M4.7a]'s own SR-8
   deferral at "zero producers, zero customers". `modifiers`' twelve
   `GROUP_OPT` rows share one port function whose internal `switch` can (and
   historically did, pre-wave-C) diverge per letter from what the row-level
   `aport.kind` shows; Option C's live-probe derivation resolves this
   correctly today because it exercises each row's OWN `syntax` text (e.g.
   `(?m)` for the `m` row) rather than reading the shared function pointer,
   so no schema change is needed for `modifiers` specifically — flagged here
   only so the choice is deliberate, not accidental, the next time a module
   ships a many-names-one-row family (a plausible shape for a future
   `unicode-props` producer, whose `\p`/`\P` doorway already dispatches by
   NAME inside one recogniser). Recommend: ship the per-row column now: it
   is correct for every row that exists today, including all twelve
   `modifiers` rows, by construction of Option C's own probe.

## Verification status

Every citation above is to a file:line or a command this lane ran
read-only in its worktree (`pcrec --list-syntax` counts, `grep -n` over
registry.c/internal.h/ext.c/syntax_dump.c/mod_modifiers.c, and the journal
entries at the line numbers given). Nothing in this memo is UNVERIFIED.
