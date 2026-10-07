# D6 critic r2 — ROWCON row_contracts.md rev 2.1 — lens: IS IT NOW SOUND?

Critic: soundness, r2 (read-only; no make, no compiles). Tree:
`/Users/fdicostanzo/pcrec/worktrees/memfn` (lane/memfn-rowcon, a165e69d).
"RC §x" = row_contracts.md rev 2.1. Code cites are relative to that worktree.
Frank's two Q-ROW-1 rulings are treated as binding; the findings test whether
rev 2.1 IMPLEMENTS them soundly, not whether they are right.

Counts: **3 BLOCKER, 7 MAJOR, 6 MINOR.**

Summary: rev 2.1 fixes r1's structural defects (binding times, kinds, requires,
row splits). Three new holes come from the rulings' implementation:
- "no silent defaults" is specified only for `const char *` hooks. Most of
  `mf_site` (zero-valued enums and numerics) has no "unstated" representation
  (B1).
- "snapshot at the top of each site" has no placement for EXPR sites. It is
  wrong for ADVANCE. As specified it breaks `-Werror` generated-code compiles
  (B2).
- The engine itself keeps three zero-means-everything defaults. One of them
  contradicts pcrec's own meaning of `routes == 0` (B3).

---

## BLOCKER

### B1. No silent defaults cannot be implemented for non-pointer fields as designed

RC §4.1/§4.2 define "stated" as "NULL means not stated". That works only for
pointer hooks. Every enum in `memfn/include/memfn.h` has a REAL member at 0:
- `MF_FORM_EXPR`, `MF_OP_FIND`, `MF_H_RETURN`;
- `MF_EMPTY_MISS`, `MF_REQUIRED`, `MF_T_SET`;
- `MF_C_RESULT`, `MF_USE_POSITION`.

Every numeric field reads 0 as a value:
- `end_back`, `reverse`, `guard_by_caller`, `on_miss_leaves`;
- `span_lo`, `cand_ppm_lo`;
- `plan_hint`, where 0 = "scan term 0";
- `fn_ref`/`table_ref`, where 0 = "none";
- `comment_tier`, `count_start`, `on_cand_reach`.

pcrec's builders lean on zero-initialization for exactly these:
- `pcrec_memfn_site` (src/gen/memfn_sites.c:143-155) sets only `abi`,
  `ret_pred`, `span_hi`, `cand_ppm_hi`, `pred.plan_hint`, `policy`, `denies`
  and `opts`.
- PRE's byte predicates come from `pcrec_memfn_preds` (memfn_sites.c:157) and
  never set `plan_hint`. precheck's `run_part` then tests `p->plan_hint == 0`
  (precheck.c:64).
- `pf_ofs_call` (emit_dfa.c:6227-6233) never sets `comment_tier`.
- OFS and VMRUN never set `empty`'s neighbours `end_back`/`reverse`.

A forgotten `empty` IS `MF_EMPTY_MISS`. A forgotten `need` IS `MF_REQUIRED`.
That is a silent default in the strict sense of Frank's words, and
`mf_check_stated` cannot see it.

**Fix:** pick one, and state it in §4.1:
- (a) a `stated` bitmask in `mf_site`/`mf_hooks`/`mf_pred`/`mf_term`, written
  only by builder macros (`MF_SET(site, end_back, 0)`), which
  `mf_check_stated` reads. This is part of the `MF_SITE_ABI` 4→5 bump already
  in §4.5.
- (b) renumber every enum from 1, with 0 = `MF_UNSTATED`, and give numerics
  sentinels. This is uglier and still leaves `0`-valued numerics.
- (c) take it back to Frank as a scope question: does the ruling cover text
  hooks only?

Recommend (a). Without one of these, rev 2.1 meets the ruling only for about
a third of the fields rows read.

### B2. The snapshot's placement is undefined or wrong for 3 of the 4 site shapes, and as written it breaks the generated-code compile

RC §4.4 says "at the top of each site … `const size_t mf_lo = (lo);` … and
likewise for `s`, `n` and the rest". Checked per shape:

1. **EXPR has no statement position.** VMRUN is spliced inside a condition:
   `if (scan_position + %d <= subject_length && <EXPR>) …` (emit_vm.c:4538,
   :8681). A declaration cannot go there. The only sound form is a GNU
   statement expression, `({ const size_t <lo> = (scan_position); <compare>; })`.
   Generic already does exactly this (generic.c:286-310, `expr_text`). The
   design must name it; "at the top of each site" is not implementable for
   EXPR.
2. **FUNC needs no locals.** The define has no caller values. Its body reads
   kit-owned parameters (`subject, n, pos`; ofsskip.c, generic.c:563-610). The
   call `fn(s, n, lo[, floor, miss])` already evaluates each argument exactly
   once: C's argument passing IS the snapshot. Say so, and keep FUNC out of the
   `no-snapshot` deny's byte set, or the T3b mover census over-counts.
3. **STMT ASSIGN with `result_decl` cannot be braced.** PRE writes
   `size_t handoff_position = …;` (precheck.c `run_line`), which pcrec's text
   reads AFTER the site (`emit_req_handoff_rest`, emit_dfa.c:1563). The
   snapshot locals therefore sit in the CALLER's scope, for the rest of the
   function:
   - Two STMT uses in one block collide. "`mf_lo`" is a fixed spelling.
     Generic's `<prefix>_mf<handle>_lo` (generic.c:72-77) is unique per
     HANDLE, not per USE, and one handle can be used more than once (the PRE
     handle is used by both engines' entries, emit_dfa.c:8655/8948,
     emit_vm.c:13231).
   - The names must be unique per USE: a use counter on the art.
4. **ADVANCE must NOT snapshot `more` and `peek`.** They are re-evaluated per
   iteration by definition (generic.c:539-547:
   `while ((more) && … ((unsigned char)(peek)) …) step`). Snapshotting them
   gives an infinite or zero-trip loop. "And the rest" must be an enumerated
   set (see M2 for what that does to "calls are ALLOWED").
5. **Unused snapshots fail `-Werror`.** Generated code is compiled with
   `-O1 -std=gnu11 -Wall -Wextra -Werror`, for example:
   - tests/axes/run_ksweep.sh:55;
   - tests/lib/run_gen_timeout_tests.sh:366;
   - and `-Wall -Wextra` under every sanitizer GENCFLAGS (Makefile:1560,
     :1607, :1667).

   pcrec STATES `n` at VMRUN (emit_vm.c:4432), but runcmp reads only `s` and
   `lo` (runcmp.c:341). A `const size_t <n> = (subject_length);` there is an
   `-Wunused-variable` error at every VM literal run.

**Fix:** a placement table in §4.4, one row per shape:

| form | snapshot |
|---|---|
| EXPR | `({ … })` |
| STMT | locals before the first statement, per-USE-unique names; braced only when no `result_decl` escapes |
| FUNC | the call's argument list; nothing in the define |
| ADVANCE | `more`/`peek` are NOT snapshot (they are per-iteration expressions; parenthesized only) |

The snapshot SET is "the value hooks the CHOSEN ROW READS", never "every value
hook stated". That needs the per-row reads declaration of M6, so T3b depends
on it.

### B3. The engine keeps zero-means-everything defaults, and one contradicts pcrec's meaning

These are ruling (1) violations inside Layer 1 itself (RC §2.1):
- **`routes = 0` = "all routes".** pcrec's `cand_routed` (emit_dfa.c:5068-5078)
  reads mask 0, and an unrouted list (`CAND_UNROUTED`: `DFA_SELECT`'s
  `dfa_reprs`, `req_admits`, …), as **DFA-ONLY**. customers.md:159 says the
  same. Appendix/§3 row 2 maps dfa_pfs' optional routes onto
  "`routes = 0` (= all)", and calls the outcome identical. It is not:
  - hosted under the engine, every mask-0 dfa_pfs row and every row of an
    unrouted list becomes eligible on the VM and ATTEMPT routes;
  - a DFA-only row would be chosen for a route it cannot serve.

  T0's fixture would not catch this, because it is cand_rows-shaped and every
  cand row carries an explicit mask.
- **`honours`/`requires` 0/0 = "no profile", per ROW.** In a profiled kit
  table, a row whose author forgets `honours` is admitted for every subject.
  That is the fail-open denylist the design exists to remove, reintroduced by
  zero-initialization.
- **`scope 0` = "one".** `CAND_SLOT_WINDOW` is 0 (customers.md:23). If the
  walk ever reads 0 as a wildcard, as `routes` does, WINDOW rows answer every
  slot.

**Fix:**
- Make profile presence a TABLE property (`mf_table.profile`). In a profiled
  table a row must carry a stated `honours`, through a macro that sets a
  stated bit; T0's table validation refuses an unstated one.
- Make `routes` a named `MF_ROUTES_ALL` token, refuse 0, and give the mapping
  of pcrec's "0 = DFA-only" explicitly (`CAND_ON(CAND_ROUTE_DFA)`).
- Make `scope` plain equality, with no wildcard value.
- Add one unrouted-list row to the T0 fixture.

---

## MAJOR

### M1. The reserved `mf_` namespace collides with a legal user prefix

`valid_prefix` (src/core/compile.c:253) accepts `-p mf`, and `mf_art_begin`'s
own fallback prefix is `"mf"` (compose.c, `art->prefix = prefix ? prefix :
"mf"`). Under `-p mf`, pcrec's own hook text names `mf_…` identifiers:
- `fn_name` → `mf_ofsskip`-style names;
- `table_name` → the prefix's tables;
- the subject names are not affected, but every prefix-derived hook is.

RC §4.4's "a hook text that names an identifier in it is refused" therefore
refuses a legal compile. Separately, existing kit locals are outside the
proposed namespace: `rq_set` and `rq_i` (precheck.c `set_rest`).

**Fix:** reserve `<prefix>_mf<k>_` (generic's existing scheme, extended with
the per-use counter of B2.3), refuse hook identifiers that match THAT pattern,
and rename `rq_*` in T3b, the same abi event.

### M2. "Calls are therefore ALLOWED" relaxes rule 1, and three places still depend on it

memfn.h:`mf_hooks` says "side-effect-free C expressions (rule 1)". RC §4.4
drops it ("calls are ALLOWED: they run once"). That is false or unsound in
three places:
- **`more` and `peek`** run once per iteration (B2.4).
- **The FUNC call's arguments** run in UNSPECIFIED order, so two side-effecting
  hooks in one call have no defined order. The STMT snapshot order is
  defined, so the two forms would disagree.
- **`--memfn=no-snapshot`** is a deny. test-axes requires every deny to be
  answer-identical to default over the corpus. With calls allowed, the deny
  arm gives a DIFFERENT answer for in-contract input, because it evaluates
  the hook several times. A deny that changes answers for legal input is not
  a deny. pcrec's hooks are side-effect-free, so the corpus will not show it,
  but G2 would, if G2 tested calls.

**Fix:** keep rule 1 (side-effect-free) in the contract. The snapshot is
defence in depth for hazards 1, 7 and 8, not a licence. The D80 hunk must not
advertise calls.

### M3. `break`/`continue` in `on_miss` (or in on_cand's verify) is captured by a kit loop

RC §4.4 admits `on_miss` as "ONE jump statement (`goto`, `return`, `break`,
`continue`) or a braced block". But kit forms place `on_miss` INSIDE their
own loops:
- precheck's set rest:
  `for (size_t rq_i …) if (!memchr(…)) <on_miss>` (precheck.c `set_rest`).
  A `break;` there exits the KIT's loop and FALLS THROUGH as a hit. That is a
  wrong answer, and `on_miss_leaves = 1` makes it worse, because precheck
  then believes the miss left.
- generic ON_CAND splices pcrec's verify text inside the kit's
  `for (… _c …)` (generic.c:497-508). A `break`/`continue` there binds to the
  kit's loop.

This hazard is not among RC §4.4's eight. pcrec sends `return 0;` today
(REQ_ON_MISS), so it is not live. memfn.h §14.0's own example on_miss is
`"break;"`.

**Fix:** pick one per row:
- refuse a top-level `break`/`continue` in `on_miss` where the chosen row
  nests it in a loop or switch (a row attribute `nests_on_miss`, gated like
  `requires`);
- or have such rows hoist the hook behind a kit label after the loop (moves
  bytes, so it belongs in T3b).

Add the hazard as #9.

### M4. The gate is undefined once the default column is gone

Rev 2.1 deletes `default_test` (§4.1: "There is NO default column"), but the
rest of the document still runs on "non-default":
- §4.3's rule is `nondefault ⊆ honours`;
- §2.2 has `subject_mask /* profile: the non-default fields */`;
- §5 says "reached only at defaults".

Under R-6 pcrec STATES `floor = "0"` everywhere. If the gate tests "stated",
`floor` is stated at every OFS/PRE site:
- ofsskip declines OFS at define (`ofs_fn_applies`: `def->floor` non-NULL →
  0, ofsskip.c:99), so it falls to generic, a BYTE MOVE;
- PRE's run-part call refuses (`ofs_fn_call`: "states a floor its definition
  did not", ofsskip.c:282).

T3a's "none (gate)" depends on an unspecified rule.

**Fix:** gate on VALUE CLASS (the `classes` column, which already exists for
reach): `honours` is a set of (field, class) bits, and `floor`'s classes are
{zero, other}. Spell the zero as a named token (`MF_FLOOR_0`) rather than the
text `"0"`. Then "zero" is recognised by token identity, not by `strcmp`, and
`"0u"`/`"(size_t)0"` cannot silently fall into "other".

### M5. T3a's ordering breaks `make test` between steps, and R-6's inventory is incomplete

1. **Refusals go live before callers state.** T3a's `mf_check_stated`
   refusals switch on while pcrec's builders (src/gen, R-6) and G2's quick
   tier (a `make test` section, `test-memfn-g2`) still send NULL. §4.5 puts
   the G2 update with a BLINDED author "after lane g2x", so T3a cannot merge
   green.
2. **R-6 depends on the kit.** pcrec cannot state `MF_MISS_N` before the kit
   defines it. The boundary rule (memfn/CLAUDE.md, "a split commit is a
   delivery failure") forbids landing them apart while the build is red.
3. **R-6's inventory**, from the builders:
   - PRE use (emit_dfa.c:1552-1557): `miss`; `floor` if PRE is declared to
     read it;
   - OFS define (:6208) AND use (:6229): `miss` and `floor`, both
     DEFINE_BOUND on FUNC, so stated at both;
   - OFS use: `comment_tier` (an int, so B1);
   - VMRUN: nothing beyond `n`'s question in B2.5.
4. **Rows that must change in the same step:**
   - `miss_is_n` (ofsskip.c:382-385, which compares text against `n` and so
     REFUSES the `MF_MISS_N` token at ofsskip_use);
   - `ofs_fn_call`'s floor refusal (ofsskip.c:282);
   - `ofs_fn_applies` (ofsskip.c:99);
   - generic's `need(…"miss"…)` (generic.c:372, :446, :646), which must
     render the token.

**Fix:** split T3a into three green steps:
- T3a-1: tokens defined and ACCEPTED, all four rows taught them, no refusal;
- then R-6 together with the blinded G2 update;
- T3a-2: the refusal switched on.

Or land all of it as one commit that includes the src/gen hunk.

### M6. `mf_check_stated` needs a per-row READS declaration, and its control shares a source

§4.2's "refuses … whenever the chosen row reads an unstated field" needs to
know what a row reads. `mf_row` carries `honours` and `requires`, not
`reads`. Either way the declaration is TYPED BY THE ROW'S AUTHOR. A row that
reads a field it did not declare escapes the check, and that is K96 exactly
(ofsskip read neither `miss` nor `floor`, and nobody declared that it
mattered). B2's snapshot set needs the same declaration.

**Fix:**
- Make `reads = honours ∪ requires`, per (field, class), explicitly.
- Add an INDEPENDENT control that shares no source with it, a POISON
  DIFFERENTIAL in G2: for every reached cell, render once with each
  UNDECLARED hook set to a poison text (`MF_POISON_<field>`, or a distinct
  identifier), and require byte-identical output, or a byte loop agreement
  where the field is semantically inert.
- A row whose text moves under poison reads a field it never declared.

### M7. The token inventory is open-ended, and the contract has NULL-as-value cases rev 2.1 does not rule on

§4.2 lists `MF_MISS_N`, `"0"` and `""` and ends with "…". memfn.h itself gives
NULL a meaning in:
- `result_decl` ("or NULL": no declaration);
- `count` ("or NULL");
- `cursor` (NULL accepted, Q-G2-14);
- `mf_term.mask` (NULL = exact);
- `opts` (NULL = none);
- `indent` (generic: NULL → "", generic.c:451);
- every callback (`note`, `member`, `table_name`, `fn_name`, `on_cand`;
  "a NULL op is 'not offered'").

Each needs either a token or an explicit exemption. "An absent OFFER is not a
value" is a defensible exemption for callbacks, but it must be written.

**Fix:** enumerate every field in `fields.def`'s stated column now, as part of
T3a's design and not its implementation, and list them in §4.2.

---

## MINOR

- **m1. Walk-order claim.** §2.1 says the first four steps are "cand_rows'
  own order". cand_rows is slot, deny, route (customers §1.2), and
  `dfa_select` is deny, route (emit_dfa.c:5095-5097). The outcome is the same
  (filters commute). The RECORD differs: a denied, off-route row is counted
  as filtered instead of DENIED. Correct the sentence; nothing in C1's SET
  diff reads it.
- **m2. Snapshot hooks, never compounds.** A snapshot of `s + lo` ahead of
  the empty test is `NULL + 0`. That is UB that `make ubsan` reports on the
  legal NULL empty subject (match_api §3.1; the `<=` arm's own comment,
  emit_dfa.c:1525-1531). Write "each HOOK, never an expression over hooks"
  into §4.4.
- **m3. Declaration after a label.** A STMT snapshot declaration placed
  immediately after a pcrec label is not valid C before C23
  (`-std=gnu11`: an error on older gcc, a pedwarn on newer). The placement
  rule (B2) should guarantee a statement precedes it, or use `({ })`.
- **m4. Lexical refusals are per hook class.** Different hooks need
  different checks:
  - `note_tag` is pasted INSIDE a comment (precheck.c `run_comment`), so its
    rule is "no `*/`";
  - `note` writes straight to the sink and cannot be checked at all, so say
    so;
  - `member`'s and `table_name`'s RETURNED text must be checked too;
  - the one-statement check must reject `return 0; f();` and `{ … };`. The
    trailing `;` after a brace breaks any later `else`.
- **m5. Snapshot types.** Generic snapshots `s` with an explicit CAST,
  `(const unsigned char *)(s)` (generic.c:304, :487). A cast silences an
  incompatible-pointer or integer-to-pointer mistake that an implicit
  initialization would diagnose under `-Wall`. Prefer
  `const unsigned char *<s> = (s);` with no cast. For pcrec's real hooks
  (`const unsigned char *subject`, `size_t subject_length/search_from/
  scan_position`; emit_dfa.c:541, :1654) neither form changes behaviour, and
  the `size_t` conversion of `n`/`lo` is the identity.
- **m6. M4(r1)'s fixture.** `requires on_miss_leaves` is in §4.3, but the C5
  decline fixture `pre-decline-leaves` (pinned to generic) that r1 asked for
  is not in T2's or T4's content.

### (b) Evaluation order and timing: no finding for pcrec's real hooks

pcrec's value hooks are bare identifiers (`subject`, `subject_length`,
`search_from`, `scan_position`). Snapshotting them at the site's top, or inside
`({ })` at the EXPR's own position after pcrec's guard, reads the same values
at the same sequence point. The change is observable only for side-effecting
or volatile hooks, which rule 1 excludes (M2). One aliasing case improves: a
`result` naming the same variable as `lo` (an in-place ASSIGN) now reads the
pre-write `lo`.

### (d) Engine gate: beyond B3, no remaining wrong-row path in the kit's three arms

- The specialised arms are pairwise disjoint on (form, op, handoff) (r1 m1),
  so order cannot pick a wrong arm.
- The define-time gate sees SITE and DEFINE_BOUND fields.
- USE_ONLY fields can only refuse, which is loud.
- Generic is total or refuses through `MF_NONE_NULL` → `kit_fail`.

The remaining risks are the zero-defaults in B3, the class-blind gate in M4
and undeclared reads in M6.

---

## By-id table: r1 soundness critic's blockers and majors

| id | r1 finding | rev 2.1 | why |
|---|---|---|---|
| B1 | define/use mask equality refuses every PRE/OFS site | **RESOLVED** | §4.1 binding times (SITE / DEFINE_BOUND / USE_ONLY / DEFINE_ONLY); equality withdrawn |
| B1a | use-only fields can only refuse | **RESOLVED** | §4.1 "USE_ONLY (subset-checked at use, can only refuse)" |
| B2 | `miss` default refuses PRE ASSIGN | **PARTLY** | Superseded by the ruling: pcrec states `MF_MISS_N` (R-6), precheck honours it. But `miss_is_n` (ofsskip.c:382) refuses the token, generic's `need(miss)` must render it, C5's text-equal `ofs-miss-n` pin needs a class, and the step order is red (M5) |
| B3 | T3 not zero-mover; S2-S7 text shape | **PARTLY** | Honestly re-cast as ONE abi event (T3b), and the snapshot closes S2-S4/S6/S7 by parenthesization, S5 by the statement-shape rule. But the snapshot's placement is undefined for EXPR/FUNC/ADVANCE and breaks `-Werror` (B2), and `break`/`continue` reopen S5's class (M3) |
| M1 | field kinds, per-value bits | **PARTLY** | §4.1 adds `kind` and `classes`; §4.3's gate is still stated as one `nondefault ⊆ honours` rule, with no per-kind rule and no default to be "non-" against (M4) |
| M2 | rows read raw hooks | **PARTLY** | "Unset means nothing" closes the NULL disagreements, but the raw reads remain (`strcmp(floor,"0")` generic.c:79; `def->floor` ofsskip.c:99, :282; `miss_is_n`). No step removes them, and no grep or poison control checks they are gone (M6) |
| M3 | honours mapping unspecified | **NOT** | T2 still says "from the audit matrix"; no per-row OBLIGATION set is published to check against what pcrec states (memfn_sites.c:143-155 and the builders) |
| M4 | precheck's positive `miss_leaves` need | **RESOLVED** | §4.3 `requires` names `on_miss_leaves` (the decline fixture is m6) |
| M5 | honouring per shape | **RESOLVED** | §4.3 splits rows with disjoint predicates. Note: ofsskip/precheck reject every negative offset (ofsskip.c:106), so their floor honouring is trivially per-class, not per-shape, today |
| M6 | "generic honours ALL" asserted against itself | **RESOLVED** | §4.3: generic's limits are contract refusals in `fields.def`, checked by G2 per-field cells, not by an assert |

## Verdict

**NOT YET SOUND; SOUND WITH B1-B3 AND M3-M6 FIXED.** The r1 structure is
repaired: 6 of 10 r1 ids are resolved or nearly so. Frank's two rulings are
the right direction, but rev 2.1 under-specifies both:
- **No silent defaults** reaches only pointer hooks (B1, M7).
- **The snapshot** has no form for EXPR, is wrong for ADVANCE, and as written
  fails the `-Werror` artifact compile (B2). It also needs the per-row reads
  declaration (M6), which the design does not have.

The engine reintroduces zero-means-all in `routes`/`honours`, one of which
silently inverts pcrec's DFA-only meaning (B3).

None of the fixes needs a new ruling, except B1's scope if Frank wants option
(c). Rev 2.2 should add:
- the stated-bit mechanism;
- the per-shape snapshot placement table and the read-set rule;
- explicit engine tokens;
- class-based honours;
- the poison differential;
- the three-step T3a.
