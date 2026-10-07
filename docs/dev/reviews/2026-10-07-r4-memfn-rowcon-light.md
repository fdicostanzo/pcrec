# ROWCON rev 4: light D6 re-check (read-only)

Subject: `worktrees/memfn/docs/design/memfn/row_contracts.md` rev 4
("RC:N"). Code read in the same worktree. Nothing built or run.

## 1. S1-S8 against the §2 gate

| cell | blocked by the gate? | what else it needs |
|---|---|---|
| S1 PRE x miss | **Only if the gate runs at USE.** PRE's `miss` is a use-time hook (PRE define carries only `fn_name`/`note_tag`/`comment_tier`, hook_census), and `select_arm` sees only define hooks (compose.c:128-135, :275). | The use-phase gate (B1). Then precheck declares `miss` either {MISS_N} or `ANY` (r3 m1: `on_miss_leaves` makes `result` dead on a miss). If it declares `ANY`, only a semantic check can confirm that (M1). |
| S2-S4 PRE x s, n, lo (unparenthesised text) | No. §2 gives no class set for expression hooks. | Either a `fields.def` class {IDENT, OTHER} for s/n/lo, with PRE and RUNA serving {IDENT} (zero-mover: every pcrec site passes bare identifiers, per hook_census), or parenthesising in the row (a byte mover, so an abi event). The class route also needs the use-phase gate. |
| S5 PRE x on_miss shape | No. | A contract sentence: `on_miss` is ONE statement (memfn.h already says "STATEMENT"). Or PRE braces it (a mover). It is not a class question. |
| S6-S7 RUNA x s, lo | No (same as S2-S4). | Same as S2-S4. RUNA is EXPR via `mf_emit`, so define and use hooks are one struct, and a define-time class check would reach it. |
| S8 GEN floor, define vs use | No. The gate selects once, at define. | A define/use agreement refusal in generic's `func_call`, the way ofsskip.c:282-283 does it. That is a one-line fix, not mechanism. |

Net: the gate as written closes K96 itself (both halves are define-time
on OFS) and S1 only with B1. S2-S8 need the small items above. Rev 4 §0
says the defect class covers "8 more cells". It should say which ones §2
closes and which are closed by other means, so N4's floors don't claim
coverage they lack.

## 2. Findings

**B1 (BLOCKER). The gate has no use phase.** §2 puts the gate "in the
existing `select_arm` walk". Selection happens once, at `mf_define`, over
the DEFINE hooks. `mf_use`/`mf_call` dispatch to the stored arm without
re-checking (compose.c:298-311).

- Every use-time hook escapes R1/R2: `miss`, `s`/`n`/`lo`, `on_miss`,
  `result`, and `floor` at the call.
- N3 says "ofsskip's ad hoc K96 checks are replaced by the gate". Those
  checks are partly USE-time: `ofsskip_use` refuses `miss != n`
  (ofsskip.c:420), and `ofs_fn_call` refuses a call-only floor (:282).
  Replacing them with a define-only gate REMOVES K96's call-time half.
- **Fix (a §2 paragraph, before N1):** at use, re-apply rules 1-2 for the
  CHOSEN row over the use hooks. A failure is a loud refusal naming the
  fields, since the row cannot be re-selected after its define text exists.
  WARN mode records it like a define decline, so N2 counts both phases.
  N3 replaces ofsskip's checks only once both phases enforce.

**M1 (MAJOR). The poison differential does not catch K96's shape (RC:99-103).**

- Poison catches a row that READS an undeclared or `ANY` field: the render
  changes.
- K96 was the opposite: a row that IGNORED a stated field that changes the
  answer. That row renders identically under any poison, so it passes.
- The live risk under §2 is a dishonest `ANY` (or a too-wide serves set).
  The gate cannot see it, and poison cannot either.
- **Fix:** add the semantic half to G2u. For each field a row declares
  `ANY`, vary it across its classes on sites that reach the row, and require
  byte-loop agreement under the reference semantics of each value. Keep
  poison too (it guards `uses` honesty). Correct the "K96's exact shape"
  sentence.

**M2 (MAJOR). N2 → N3 entry condition.** "Zero would-decline" catches
every gate-caused row change: the gate only adds declines, so the chosen
row moves only if it would-decline. It needs three things:

- (a) N2 re-run AFTER R-6 (stating values removes rule-1 declines and can
  add rule-2 ones), and again on N3's own build;
- (b) both phases (B1);
- (c) WARN and ENFORCE verdicts computed by ONE function, with only the
  action switched.

It does NOT catch N3's other content:

- "a shape-dependent row is split";
- "precheck serves a stated miss", if that changes precheck's text.

Only the identity gate (156/156) covers those. Name it in N3's row next to
"N2 = 0". Coverage also needs every (pcrec builder, chosen row) pair
reached in the census, not just corpus × axes. Add that as a census line.

**M3 (MAJOR, Frank's test). The `UNSTATED` enum forms and tri-state
booleans (RC:66-71, in N1) solve no scenario.** None of S1-S8 and nothing
in K96 involves `comment_tier`, `reverse`, `guard_by_caller` or
`on_miss_leaves`. pcrec states each of them at every site that reaches a
row that uses it. The work costs an `MF_SITE_ABI` bump and enum surgery.
**Cut:** use r3 M7's exemption list in its place ("0 is a contract value"
for `reverse`/`end_back`/`comment_tier` at define; "0 is the conservative
value" for `on_miss_leaves`/`guard_by_caller`/`fn_ref`/`table_ref`). File
`UNSTATED` with a trigger: the first row that must tell "unstated" from 0.

**m1 (MINOR, Frank's test).** Two N4 items duplicate other witnesses:

- "a text signature per row, checked in its witness's artifact" duplicates
  the trace's CHOSEN record and the C5 arm pins. Cut it.
- Per-(row, field, class) counters: keep only if N4 floors the specialised
  class (e.g. `miss` = MISS_N reached). Otherwise per-row CHOSEN is enough.

**m2 (MINOR).** `miss` ∈ {MISS_N, OTHER} is undefined.

- It could be text equality with the `n` hook (today's `miss_is_n`), or a
  new enum (R-6 says "`MF_MISS_N`").
- Under text equality, the class needs `n` stated in the SAME phase. PRE
  and OFS define do not carry `n`.
- Say which, in `fields.def`'s first row.

**m3 (MINOR).** G2u lands before N3. Its "refusal expectations" must hold
against the WARN-mode kit, or that part lands with N3.

**m4 (MINOR).** §6 H2's trigger census already exists
(`probes/rowcon/hook_census.md`: every hook is a bare identifier or a
single `return 0;`, no risky text). Record the outcome ("filed, not yet")
rather than "decides it". H1 and H3 triggers are concrete.

## 3. Verdict

**FIX FIRST**, and the fix is small and on paper only:

- B1: a use-phase paragraph in §2, and N3's ofsskip sentence conditioned
  on it;
- M1: the semantic `ANY` check in G2u;
- M2: N3's entry line;
- M3: cut `UNSTATED` from N1.

After those edits, BUILD N1 needs no further panel.
