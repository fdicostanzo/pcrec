# D6 critic — ROWCON row_contracts.md rev 1 — lens: IS THE LOGIC SOUND?

Critic: soundness (read-only; no make, no compiles). Tree read:
`/Users/fdicostanzo/pcrec/worktrees/memfn` (branch lane/memfn-rowcon, 30a41a8a).
Cites are `memfn/src/<file>:line` unless a path is given. "RC §x" = row_contracts.md.

Counts: **3 BLOCKER, 6 MAJOR, 5 MINOR.**

The core idea is right: an allowlist (`honours`) fails safe where the current
`applies()` denylist fails open. But rev 1's gate treats every input as the
same kind of thing: a field that is either "at default" or not, and is
checked once. The real inputs come in at least four kinds and at two binding
times. Three consequences follow, and each is fatal as written:
- the define/use equality gate refuses every PRE and OFS site pcrec sends;
- Q-ROW-1's `miss` recommendation refuses pcrec's live PRE handoff sites;
- T3's "fix in text" is a byte move, and its "or drop from honours" is a
  compile break.

All three are repairable inside the design's own frame (§F below).

---

## BLOCKER

### B1. The define/use "same gate, equal masks" rule refuses every PRE and OFS site pcrec sends today

RC §1.2 bullet 3 and §3.4 say a use whose non-default mask differs from its
define's is refused. But pcrec hands the kit DIFFERENT hook sets at define and
at use, and the contract requires it to: integration.md §14.0 [rev4.1] item 2
says "`def` carries only what file-scope text needs (`fn_name`, `note`,
`note_tag`, …). `use` carries what the entry text needs (`indent`, `on_miss`,
`result_decl`, `result`, the subject and bound names)."

What pcrec actually sends:

| site | define hooks | use hooks |
|---|---|---|
| PRE | `fn_name`, `note_tag`, `comment_tier` (src/gen/emit_dfa.c:1490-1493) | `s`, `n`, `lo`, `indent`, `on_miss`, `result`, `result_decl`, `note`, `comment_tier` (emit_dfa.c:1552-1557) |
| OFS | `fn_name`, `table_name`, `comment_tier` (emit_dfa.c:6208-6211) | `s`, `n`, `lo`, `table_name` (emit_dfa.c:6229-6232) |

For either site, any `fields.def` that contains a single hook field gives two
different masks. That holds even for the minimal set the design needs to
cover S1/S5/S8, `{miss, floor, on_miss}`, because `on_miss` is use-only on
PRE. Every PRE (94 artifacts) and OFS (40) site is refused, which is a
`make test` compile break. That contradicts T2's "none".

The equality rule is also aimed at the wrong thing. S8 is a field that is
BOUND at define (generic's `has_floor` fixes the parameter list,
generic.c:79, :593) and differs at use (generic.c:602). Plain subset at use
would NOT catch S8, because generic honours ALL. Equality catches S8 only by
also refusing everything legitimate.

**Fix:** give each field a BINDING TIME in `fields.def`:
- **SITE**: the `mf_site` fields, fixed at define.
- **DEFINE-BOUND hook**: read at define and baked into define text, e.g.
  `floor` and `miss` on FUNC, which become parameters. The rule is
  value-equality between define and use, or "stated at define iff stated at
  use".
- **USE-ONLY hook**: `s`, `n`, `lo`, `on_miss`, `result`, `result_decl`,
  `indent`, `note`. The rule is a subset check against the CHOSEN row's
  `honours` at use, and a failure refuses.
- **DEFINE-ONLY hook**: `fn_name`, `note_tag`. Not checked at use.

Then state plainly the consequence in B1a.

### B1a. (Corollary, part of B1) For use-only fields the gate cannot "fail toward generic"; it can only refuse

The arm is chosen ONCE at `mf_define`, over the define hooks
(compose.c:275; integration.md §14.0 item 4). Every K96-class suspect on
PRE (S1 `miss`, S2-S4 `s`/`n`/`lo`, S5 `on_miss`) lives in a hook that pcrec
supplies only at use, so the define-time gate never sees it. RC §1.2 bullet 1
("forgetting fails toward the generic row") is therefore true only for SITE
and define-time fields. For PRE's whole failure surface, forgetting fails
toward a refusal, which is a pcrec compile break. That is still loud and
safe, but it is a different promise.

**Fix:** state it in §1.2 and §3.1. If falling back to generic is wanted for
those fields, the selection-relevant facts about them must be SITE facts
stated at define. For example, `on_miss_leaves` already is one: it is the
precedent for "a fact about a use-only hook, declared at define". That is an
abi event, which is the honest cost.

### B2. Q-ROW-1's `miss` recommendation refuses pcrec's live PRE ASSIGN (handoff) sites

RC §5 recommends "`miss` NULL ≡ the function's `n` for FUNC/RETURN and a
REFUSAL elsewhere". pcrec's PRE handoff site is STMT/ALL_PRESENT/ASSIGN
(emit_dfa.c:1481), and its use hooks carry `result` and `result_decl` but
NO `miss` (emit_dfa.c:1552-1557). precheck.c:206-209 relies on that: the
miss is the ofs function's `n`, tested by `>= n`. RC §1.2 puts the refusal
in `fields.def` as a CONTRACT refusal, so it applies to every row. The
handoff witnesses all stop compiling: `x{2,5}(?i:cat)`, `(?:a|bb)?catdog`
and `(?i)userpass[0-9]` (audit §5.1 A2 ASSIGN).

Related: generic already refuses ASSIGN without `miss` (generic.c:372). So
the T2 claim "generic honours ALL" is FALSE for a site pcrec sends today.
This is latent only because precheck applies first. Any T2 `honours`
omission on precheck turns the PRE handoff into a refusal, not a byte move
(see M3).

**Fix:** the default of `miss` is "unstated ≡ `n`" for EVERY valued handoff:
RETURN, ASSIGN, ON_CAND and the FUNC call. `n` is always outside
`[lo, n - end_back)`, which is what memfn.h requires of `miss`. Generic must
then render an unstated miss as `(n)`, so T0/T2 gains a generic text change.
It is zero-mover, because generic is unreached from pcrec and its ASSIGN
path refuses today. Also, "text-equal to `n`" must count as default, or C5's
`ofs-miss-n` pin (tests/memfn/arm_fixtures.c:357) moves to generic. That
makes `default_test` CROSS-FIELD (it reads `n`), so the "ONE predicate per
field" in RC §1.1 must take `(site, hooks)` and be allowed to read sibling
fields.

### B3. T3 cannot be zero-mover for S2-S7, and its stated alternative is a compile break

RC §4 T3 says: "fix S1-S8 in row text … OR drop the field from `honours`",
with pcrec bytes "none".
- **The text fix moves bytes.** Parenthesizing `s`/`n`/`lo` in precheck.c
  (:167-171, :187, :209, :214) and runcmp.c:345 rewrites, for example,
  `if (subject_length <= search_from ||` and `subject + scan_position` in
  every PRE artifact and every VM run compare (94 + 101 per m1bfix_report
  §4). Bracing `on_miss` (S5) rewrites every `return 0;` line.
- **"Drop from honours" breaks the compile.** `s`, `n`, `lo` and `on_miss`
  are ALWAYS stated at PRE/VMRUN use, so dropping them from `honours`
  refuses every such site (B1a).
- **The gate never sees this class.** RC §3.5 already admits that S2-S7 are
  a mis-honoured field, not an unhonoured one. So T3's "(cells unreachable
  from pcrec; gate)" is no proof here either.

**Fix:** settle S2-S7 and S5 by CONTRACT RULING, not row text. Options:
- (a) Rule that `s`/`n`/`lo` are primary expressions (identifier,
  parenthesized, or postfix) and `on_miss` is ONE statement. memfn.h already
  says "pcrec's STATEMENT", singular, and §14.0 gives `"return 0;"`,
  `"break;"`. pcrec complies today. G2's unparenthesized ternary style and
  its two-statement `on_miss` then become out-of-contract inputs. The kit
  either refuses them at the gate (`is_ident`-style shape test, compose.c:347
  has one) or wraps them conditionally.
- (b) Parenthesize or brace CONDITIONALLY: only when the text is not
  already a primary expression or a single statement. That moves no pcrec
  byte, but it needs a kit-side shape test of opaque text, which Q-G2-18
  avoided.

Recommend (a): it is a ruling plus a refusal, it moves zero bytes, and G2
gets one more hook-style axis that asserts the REFUSAL.

---

## MAJOR

### M1. "Non-default" is not one kind of thing; the mask needs field KINDS, and multi-valued fields need per-value bits

The subset gate is right for OBLIGATIONS: a non-default value demands
different behaviour (`reverse`, `end_back`, `empty` = NOP, `floor`, `miss`).
It is the wrong rule for three other kinds:

- **PERMISSIONS / FACTS.** The non-default value allows a cheaper form, and
  ignoring it is always correct: `guard_by_caller`, `on_miss_leaves`,
  `use` = DISCARD, `empty` = EXCLUDED, `need` = OPTIONAL, `span_*`, ppm
  hints, `consumer`, `policy` INLOOP.
  - Under rev 1's rule, a new permission that pcrec starts stating (e.g. a
    proven `span_hi`) makes EVERY specialized row decline. That is a mass
    byte move toward generic: safe, but an unplanned abi event.
  - For permissions the safe default is "honoured by every row unless the
    row EXPLOITS it". The exploiting row needs the opposite test, a positive
    requirement, which the subset gate cannot express.
- **REQUIREMENTS.** The row NEEDS a hook stated: generic needs `s`/`n`/`lo`
  (generic.c:339); precheck needs `indent` and `on_miss` (precheck.c:224);
  runcmp needs only `s`/`lo` (runcmp.c:341). The "default" here, unstated,
  is the case the row CANNOT do, which inverts the gate's assumption that
  the default is the easy case. Disagreements #5, #6 and #7 are this kind
  (see the table). A second mask `needs`, gated `needs ⊆ stated`, is
  required.
- **RENDERING / ADVISORY.** `note`, `note_tag`, `comment_tier`,
  `table_name`, `member` and `fn_name` change text, not answers. Generic
  ignores `note`, `note_tag` and `table_name` (generic.c:22-25). If they are
  in the mask, "generic honours ALL" is false. If they are excluded, say so.
- **Multi-valued fields.** `empty` has MISS (default), NOP (an obligation)
  and EXCLUDED (a permission). One "non-default" bit cannot say "honours
  EXCLUDED by testing anyway, but not NOP". Use per-value bits
  (`empty_nop`, `empty_excluded`), and the same for `use` and `policy`
  bits. The shape enums (`form`, `op`, `handoff`) have no meaningful
  default and belong to `applies()`, not the mask.
- **Fields inside `preds[]`/`term[]`** (term `offset` < 0, `mask`, `need`,
  `plan_hint`) need an aggregation rule ("any term non-default"). The
  decision record's "first failing field" should then name the pred/term
  index.

**Fix:** add `kind ∈ {OBLIGATION, PERMISSION, REQUIREMENT, RENDERING}` and
the B1 binding time to `MF_FIELD`. The gate becomes:
- `oblig_nondefault ⊆ honours`;
- `stated ⊇ needs`;
- permissions are implicitly honoured, and the exploiting row tests them in
  `applies`;
- rendering fields are ungated.

The soundness argument in RC §3.1 then holds per kind.

### M2. RC §3.3 "rows cannot disagree on unstated" is not by construction: rows read raw hooks

`fields.def` spells the default, but the rows keep reading raw fields:
- `ofs_fn_applies` declines any non-NULL `floor`, including `"0"`
  (ofsskip.c:99);
- `ofs_fn_call` refuses any non-NULL `floor` (ofsskip.c:282);
- `miss_is_n` has its own default (ofsskip.c:382-385);
- generic has `has_floor` (generic.c:79) and its own `need(miss)`
  (generic.c:372, :446, :646).

The gate admitting a `"0"` floor does not stop ofsskip refusing it at the
call. So disagreement #3 is not settled unless every raw read goes. Nothing
in the plan removes them or checks that they are gone.

**Fix (by construction):** CANONICALIZE in the composer before the gate and
before any row sees the site or hooks. Map `floor` `"0"` → NULL, and an
unstated or `n`-equal `miss` on a valued handoff → the canonical form B2
rules. Rows then read only canonical values. Then add a grep-based check
(the arch-blind check's shape) that no row file compares `->floor` against
`"0"` or tests `->miss` against `n`. Canonicalizing is zero-mover for pcrec
(pcrec states neither) and for C5 (`ofs-miss-n` stays ofsskip).

### M3. T2's zero-mover claim depends on an `honours` mapping the plan leaves unspecified, and pcrec states MANY non-default fields

RC §4 T2 says "pcrec states no non-default field these rows don't honour",
with honours "from the audit matrix". In the audit matrix most of these
cells are `i` (ignored, benign) or `I`, not `H`. What pcrec states today
(src/gen/memfn_sites.c:143-154; emit_dfa.c:1463-1493, :1552, :6199-6232;
emit_vm.c:4406-4436):
- `policy` = MF_P_PORTABLE_ONLY on EVERY site by default
  (memfn_stamps.c:218-221), plus INLOOP on loop-budget rows;
- `consumer` = ENGINE (enum 1) on all three sites;
- `use` = DISCARD on PRE ON_MISS and on VMRUN;
- `empty` = EXCLUDED and `guard_by_caller` = 1 on VMRUN;
- `on_miss_leaves` = 1 and `ret_pred` set on PRE; a predicate or term
  `need` = OPTIONAL on DFA-scan routes;
- `plan_hint`/`plan_pos` on OFS and PRE parts;
- `comment_tier` = 1;
- the hooks `fn_name`, `note_tag`, `table_name` and `note`;
- `n` on VMRUN (runcmp ignores it);
- `denies` = RUN_OVERLAP under `-fno-run-overlap`.

If T2 maps `i`/`I` to "not honoured", the result depends on the site:
- PRE ON_MISS and VMRUN fall to generic: a byte move;
- PRE ASSIGN falls to generic, which REFUSES (B2): a compile break.

The emit_sweep gate would catch it, but the plan's claim is unsupported as
written.

**Fix:** state the mapping. With M1's kinds, PERMISSION and RENDERING are
implicitly honoured and only OBLIGATION cells are declared. The specialized
rows then decline exactly `{reverse, end_back≠0, empty_nop, floor≠default
(OFS; PRE run parts), miss≠default (OFS, PRE)}` plus their shape tests.
List that set per row in the design, so the panel can check it against this
list.

### M4. `mf_row` (RC §1.5) has no slot for precheck's positive `miss_leaves` requirement; dropping it is a wrong answer

The composer's `arm.miss_leaves` column (kit.h:98; compose.c:131) admits
precheck ONLY where `on_miss_leaves` = 1. precheck's set rest carries no
empty test, and it tests each predicate only after the one before it
"missed and left" (precheck.c:244-245). This is a POSITIVE requirement on a
non-default value. The subset gate admits any row at the default (0), so if
T2 "moves the arm onto `mf_row`" without folding the column into
`precheck_applies`, precheck is chosen for `on_miss_leaves` = 0 sites. The
result is a wrong answer for a falling-through `on_miss`. pcrec always sets
1, so G2 is the only witness.

**Fix:** T2 must move the column into `precheck_applies`, name it in RC
§1.5, and add a C5 decline fixture (`pre-decline-leaves`) pinned to
generic.

### M5. `honours` is per row, but some honouring is per SHAPE

PRE ignores `floor` correctly for byte-only predicates: offset 0 ≥ `lo` ≥
`floor`, by Q-G2-6's precondition (audit §2.3 PRE×floor). It CANNOT honour
`floor` for run parts: `ofs_fn_call` refuses it (ofsskip.c:282). A static
mask has to pick one. Declaring "honours floor" lies for run-part sites.
Declaring "doesn't honour floor" gives a refusal at use (B1a) for a site
PRE renders correctly. The design's §3.1 decomposition into fields ×
predicate-shapes therefore only holds if `applies` keeps shape-conditional
field tests, which is the denylist the design set out to remove.

**Fix:** let a row declare `honours` as a function `honours(ctx)` returning
a mask, or split the row (PRE-bytes-only vs PRE-with-runs) in the T4
sub-tables. Either way the record names which part declined.

### M6. "Generic honours ALL (asserted)" is a control that shares its source with what it controls

A `_Static_assert` that generic's `honours == ALL` checks a constant someone
typed, not the text. The record already shows generic NOT honouring things
pcrec or the contract allow:
- `miss` unstated on ASSIGN/ON_CAND/RETURN/FUNC (generic.c:372, :446, :609,
  :646; see B2);
- `reverse` on ADVANCE (stmt_advance never reads it; Q-G2-5 is OPEN);
- an ALL_PRESENT FUNC reads `s->pred.fn_ref`, not `preds` (generic.c:568;
  contract unstated);
- `note`/`table_name` (rendering; M1).

This is exactly memory `pcrec-check-design-lessons` / learnings §3, a
control that shares a source.

**Fix:**
- Before T2, list generic's honest refusals explicitly as `refuse_test`
  rows. That covers ADVANCE `reverse` (until Q-G2-5 is ruled) and
  ALL_PRESENT FUNC.
- Make the independent half G2: one axis per OBLIGATION field × value,
  rendered through generic, checked against the scalar byte loop.
- Keep the assert only as a tripwire, labelled as such.

---

## MINOR

- **m1. Order.** The three specialized arms are pairwise DISJOINT on
  (form, op, handoff): FUNC/FIND/RETURN, STMT/ALL_PRESENT/{ON_MISS,ASSIGN},
  EXPR/VERIFY/BOOL (ofsskip.c:389-390, precheck.c:72-73, runcmp.c:325-326).
  So today's order is irrelevant, and first-match plus gate equals "any
  admissible applicable row". The gate is order-safe in general: it is a
  per-row conjunct, so first-match over (gate ∧ applies) is still
  first-match. Order matters inside RROWS (words before bytes, overlap
  before memcmp; runcmp.c:78-103). Those rows read a TERM, not a site, so
  the site `nondefault` mask is meaningless there.
  - Fix: RC §1.5 should say sub-tables pass their own field table or 0.
  - Fix: RC §3.6 should require the order rationale only where two rows'
    predicates can both hold. Today that is RROWS, and later any SIMD row
    stacked over its scalar twin.
- **m2. `denies` and `opts` are selection inputs, not site fields.**
  `denies` removes ROWS (`mf_row.deny`), and `opts` does too, by name. The
  design's example of a default, "`denies` iff 0" (RC §1.1), puts it in the
  field mask as well. Generic "honouring" a deny is a category error (it is
  the undeniable fallback). Keep them out of `fields.def`.
- **m3. `policy` PORTABLE_ONLY is the inverted case and works by luck.** It
  is non-default when the switch is OFF, and a future SIMD row must decline
  it. The subset gate does exactly that, because scalar rows "honour" it by
  ignoring it. Under M1 it is an OBLIGATION only for SIMD-layer rows. Write
  that down, because the audit flags it as the next K96 (audit §2.5 "Not
  counted").
- **m4. Several of the "13 disagreements" are not disagreements about a
  default.** #10 (member vs immediate/table probe) and #11 (`note` called or
  not) are rendering choices that the contract allows (rule 6 via §10.2's
  set truth; §14.2 text-only). #12 and #13 are agreements. RC §1.1/§3.3's
  "settles the 13 disagreements" overclaims. See the table.
- **m5. "8 more K96-class cells" mixes two classes.** K96 is a row IGNORING
  a field (S1, S8). S2-S7 are a row MIS-RENDERING a field it reads. The gate
  addresses only the first, as RC §3.5 concedes. The §0 headline should
  count them separately, 2 + 6, so nobody reads the gate as covering all 8.

---

## By-id resolution table

Legend:
- **R** = resolved by rev 1 as written;
- **P** = partially resolved, or resolved only with the fix named here;
- **N** = not resolved;
- **X** = rev 1's proposal breaks pcrec.

### The 8 suspect cells (audit §2.5)

| id | cell | rev 1's mechanism | verdict | why / fix |
|---|---|---|---|---|
| S1 | PRE × miss | the gate at use (miss is use-only) | P | Selection cannot see it (B1a). The use gate can refuse a stated `miss` ≠ `n`, which is loud, not a fallback. Q-ROW-1 as written refuses pcrec's NULL miss on ASSIGN (B2, X). Fix: B2 default plus a use-time refusal of `miss` ≠ canonical in PRE. |
| S2 | PRE × s paren | none (RC §3.5: tests only) | N / X | T3 text fix moves bytes; "drop from honours" breaks the compile (B3). Fix: contract ruling (a). |
| S3 | PRE × n paren | same | N / X | same |
| S4 | PRE × lo paren | same | N / X | same |
| S5 | PRE × on_miss braces | same | N / X | same; rule `on_miss` is ONE statement (memfn.h already says "STATEMENT") |
| S6 | RUNA × s paren | same | N / X | same (101 VM run compares would move) |
| S7 | RUNA × lo paren | same | N / X | same |
| S8 | GEN × floor define/use | define/use mask equality | P / X | Equality catches it but refuses every PRE/OFS site (B1). Fix: `floor` is DEFINE-BOUND on FUNC, with value-equality (or "stated at both or neither") between define and use. |

### The 13 disagreements (audit §3)

| # | field | rev 1's mechanism | verdict | why / fix |
|---|---|---|---|---|
| 1 | `miss` NULL | Q-ROW-1 default | X | The recommended "refusal outside FUNC/RETURN" refuses pcrec's PRE ASSIGN. Fix: B2, unstated ≡ `n` for every valued handoff; generic renders `(n)`. |
| 2 | `miss` ≠ `n` | gate (OFS and PRE don't honour) | P | OFS works at define only if `miss` is stated at define. pcrec states it nowhere, so this is enforced only at use, as a refusal (as K96 does today). Needs M2 canonicalization so ofsskip's own `miss_is_n` goes. |
| 3 | `floor` = "0" | default_test | P | The gate admits it, but `ofs_fn_applies`/`ofs_fn_call` still decline or refuse the raw `"0"` (M2). Fix: canonicalize. |
| 4 | `floor` define vs use | equality gate | X → P | B1. Fix: binding time. |
| 5 | `n` NULL | none | N | A REQUIREMENT, not a default (M1): generic needs it, runcmp does not. Fix: a `needs` mask per row; the decline/refusal reason is recorded. |
| 6 | `indent` NULL | none | N | Requirement: precheck needs it, generic uses "". Fix: `needs`; or canonicalize NULL → "" (then precheck's refusal goes; zero-mover since pcrec states it). |
| 7 | `on_miss` NULL on ASSIGN | none | N | Requirement: precheck needs it, generic treats it as optional. Fix: `needs`. |
| 8 | hook precedence | none (tests) | N / X | B3 (S2-S4, S6, S7). |
| 9 | `on_miss` statement shape | none (tests) | N / X | B3 (S5). |
| 10 | member vs immediate/table | n/a | not a defect | A rendering choice, legal by §10.2's set truth. Declare it a non-disagreement (m4). |
| 11 | `note` called or not | n/a | not a defect | Rendering (m4); kind RENDERING under M1. |
| 12 | `lo` > `n` | n/a | agree | nothing to settle |
| 13 | OPTIONAL need | n/a | agree | nothing to settle; kind PERMISSION under M1 |

Net: rev 1 RESOLVES **none** of the 8 suspects outright, partially resolves
2 (S1, S8), and its T3 options break pcrec on 6. Of the 13: 4 partial
(#2, #3, #4 with fix, #1 with fix), 3 unaddressed requirements (#5-#7),
2 unaddressed text-shape cells (#8-#9), 2 non-defects, 2 agreements.

---

## §F. The repaired design, in one paragraph

Give `MF_FIELD` two more attributes:
- **kind**: OBLIGATION / PERMISSION / REQUIREMENT / RENDERING, with
  per-value bits for multi-valued enums;
- **binding**: SITE / DEFINE-BOUND / USE-ONLY / DEFINE-ONLY.

The composer CANONICALIZES the site and hooks first: `floor` "0" → NULL; an
unstated or `n`-text `miss` on a valued handoff → canonical `n`;
`indent` NULL → "". Then:
- at define, the row is admitted iff (SITE ∪ DEFINE-BOUND) obligation
  non-defaults ⊆ `honours`, and the row's `needs` ⊆ stated, and `applies`
  holds;
- at use, the CHOSEN row must honour the USE-ONLY obligation non-defaults
  and find its `needs` stated, else a loud refusal;
- DEFINE-BOUND fields must be equal at define and use.

Text-shape obligations (S2-S7) become CONTRACT shape rules (primary
expressions, one statement), checked as refusals, not row text. Those three
changes make the RC §3 argument true as stated, and they keep T2/T3
zero-mover.

## Verdict

**NOT SOUND AS WRITTEN; SOUND WITH §F.** The allowlist direction is correct
and worth keeping. But rev 1's gate, applied literally:
- refuses every PRE/OFS site pcrec sends (B1);
- Q-ROW-1 as recommended refuses pcrec's handoff sites (B2);
- T3 cannot be zero-mover (B3).

A rev 2 should:
1. add field kind and binding time;
2. canonicalize before the gate;
3. move S2-S7 to contract rulings;
4. publish each row's declared OBLIGATION set, checked against M3's list of
   what pcrec states.

The panel should reread it before any T-step lands.
