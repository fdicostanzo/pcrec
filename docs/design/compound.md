# [COMPOUND] — the compound artifact as a general tool; first client [MATCH-SPLIT] (DESIGN NOTE, REVISION 2.1)

**Revision 2**: lane `mscomp2`, 2026-10-12, from main `21641979` (abi 76). It applies the D6
panel r1 on revision 1 (`../dev/reviews/2026-10-12-r2-composite.md`; read its dispositions
table, which is this revision's work list) and D163 addendum 2 (the name, always on,
pin-only first, B3 first, captures on demand). §R2 maps every accepted finding to the place
it is addressed. **Design only**: nothing under `src/` changes. The evidence is the
revision-2 twin (`compound/twin/twin2.py`, `cost2.py`, `ctrl2.c.in`): UNCHANGED `build/pcrec`
compiles plus a hand-written controller, an every-startpos and find-all differential against
today's artifact and libpcre2 10.46 on the SHIPPED configuration (derived DFA Q, every option
arm), counted subject loads (no clock), and three failing-direction plants.

**Revision 1** (lane `mscomp`, the same day, as `composite.md`) is superseded. The file and
its evidence directory were renamed by D163 addendum 2 item 1; revision 1's twin
(`twin/twin.py`, `cost.py`, `ctrl.c.in`, `results/split_*.tsv`) is kept as history.

**The name.** "Compound" is the artifact kind everywhere: this note, the plan row [COMPOUND],
the stamp `<PREFIX>_COMPOUND`, the route value `"compound"`, the table `compound_rows[]`, the
code identifiers. **One exception, stated once:** `cand_rows[]`'s existing LOCATE row named
`"composite"` (`src/gen/emit_dfa.c:8892`, the inlined-prefilter locator) keeps its name. It is
a row inside one machine's start table and has nothing to do with this artifact kind. The
historical review files keep the old word.

Rulings read: D163 with addenda 1 and 2, D88 addendum 1, D156 (and `locate_finish.md` rev 2.1,
its typed vocabulary), D158, D135, D76/D94, D80, D104, D144 addendum 4, D155 addenda 4/4.1.
Plan rows: [COMPOUND], [MATCH-SPLIT], [EMIT-ENTRIES], [FINDALL-NEXT], [OPT-ATTEMPT-SPLIT],
[OPT-REVEND] (B3 = the match-end mark, D164), [ADAPTIVE-ARM], [V-E], [IFACE-PUSH].

Read §0 first. §A is the tool, §B the first client, §C the cross-call hook, §D the clients
(captures on demand first), §E the checks, §F the build plan, §G the open questions, §H the
unlocks, §I the standing questions, §J the findings.

## §R2.1. Revision 2.1 (lane `cpfix`, 2026-10-12): the light re-check's five findings

Text only; no `src/`. Revision 2's design is unchanged.

| id | where | what changed |
|---|---|---|
| MUST-FIX-1 | §A.11, §E.3 G7, §E.4 CMP-17, §F B4 | The lever fence's host was wrong: `tests/spec_mod0/check01_isolation.sh` is the enabled-set isolation check and its named-exception count is pinned at exactly 1. Verified by grep that no export-surface allowlist check exists (`tests/memfn/run_link_checks.sh` C15 checks the `pcrec_` prefix only). NEW check `tests/compound/run_symbol_allowlist.sh`: every global of `build/libpcrec.a` outside `lib/pcrec.h`'s declarations is on `symbol_allowlist.tsv` with a reason (measured: 566 globals, 6 public); the lever's internal entry is one allowlisted name. Added at B4 with the lever. |
| MUST-FIX-2 | §A.11 | `visibility("hidden")` does NOT fence the shipped static archive (measured with a probe: `nm -g` lists the symbol, an executable linking the `.a` calls it). The fences are the unadvertised name, the allowlist check, and `run_lever_fence.sh` with its grep scope widened to `tests/`, `scripts/`, `cli/` (allowlisting the harness's own uses). |
| SHOULD-1 | §E.5 | The abi greps read the current number from `PCREC_ARTIFACT_ABI` (`src/gen/emit_dfa.c`) instead of hard-coding 76. |
| SHOULD-2 | §A.11, §A.7, §E.3, CMP-15 | The lever stamps `"forced-off"` ONLY when the default build would have shipped a row name (the lever runs the complete admission, caps and `drop-compound` included, and replaces only "ship the compound"). A `pre_admits` pass alone could mark an artifact the lever changed nothing about. "The lever moves nothing else" is now an exact two-directional property. |
| SHOULD-3 | §A.6 | One sentence: the DFA reach of the `qf = next_pos(aligned f)` correction is CMP-13's `\Ga$|b$` under `-fstartpos-guard=align`. Checked by grep: that witness is in the twin's case list for `byte` only (`hand:g1`; `tests/assertions/rev_end.rxt:338`), so its utf8 × align arm was ABSENT. OWED item added as `docs/design/compound/twin/results/cases2_owed.tsv` (kept apart from `cases2.tsv` so revision 2's recorded 177 case-arms / 2,170,123 cells stay true of the file that produced them; folded in when the differential is next re-run). Cheap, so run once (4 cores, GNU timeout, 0.8 s): 6 arms, 13,523 cells each, 0 differences (`results/cases2_owed_run.tsv`). The twin has no plant that hands F the raw `from`, noted in §A.6. |

## §R2. What revision 2 changed, by panel id

| id | where addressed | what changed |
|---|---|---|
| chk B1 | §B.4 (A6), §B.7, §F B4/B5 | The first build is PIN-ONLY: Q is end-pinned (route `rev-end`) or never. A pin-only subject has a floor match plus at most the end matches, so there is no many-match term. S+F (concat-sqli) waits for its trigger, a bench reading of concat-sqli on its own subjects; the derived match-density cost conjunct is sketched in §B.7 and designed at that trigger. Counted on matching pin-only subjects (§B.5). |
| chk B2 | §B.5, §F B3 | B3 is a consequence of D164's MATCH-END MARK (internal END_MARK; `X$` lowers to `X END_MARK \n? \z`, so the reverse DFA walks once from n with no seeds, tags or tie special case); its design lane follows this note. (Revision 2 originally named lane revb3's tagged two-seed walk here; that design was rejected by Frank and the lane stopped before delivering.) This note does not design it. §B.5 states the dependency: the final-newline shape costs 3.00× today; after B3 its factor is whatever `revend_onepass.md` measures, and G3's bound for that shape is that factor. |
| sem MF1/MF2/MF4, arch M5 | §A.6 | ONE controller prologue computed from P: range, boundary guard (refuse / align / none, P's option), `-futf-check` with P's lookbehind reach. Parts are compiled guards-off. The floor is the ALIGNED `from`; `qf = next_pos(f)`. Twin: all six utf8 option arms, 0 differences; plants 2 and 3 fire. |
| sem MF3 | §B.1 | F is a BOUND on P's own attempt (`start_max = search_from`, a part option), not a tree wrap. `(?R)`/`(?0)` keep P's root. Twin: F built that way; `^x|a(?R)?b` 0 differences. |
| sem S1 | §B.1 | The prune keeps called groups' bodies, referenced groups, and groups named by a condition. In the DFA-only first build any such pattern declines (calls and backreferences route VM anyway); the DEFINE-style keep is designed for B6. |
| sem S3, notes | §B.8, §C, §A.9 | `\K` declines the cache (or keys on the attempt start). Verbs and callouts decline through a registry-keyed predicate. D158: the give-up surface is not a subset in either direction, so "answer for answer" is dropped; a part's give-up is returned at once. §C states the caller contract for the cache. |
| arch M1 | header, everywhere | Renamed to "compound" (D163 add. 2 item 1); `cand_rows[]`'s LOCATE row "composite" keeps its name. |
| arch M2 | §A.2 | Controllers are COMBINATORS over `locate_finish.md`'s typed results: `first-nonzero`, `min-start-then-finish`, `locate-then-finish`, `select-by-arg`, `dispatch`. A row is a combinator expression; it writes no emitter. The rule for in-Job LOCATE row versus compound part is stated. |
| arch M3 | §A.1 | `CompPart` carries its OPTIONS: `flags_set`, `flags_clear`, `engine`, `bound`, `derive`. Every field is stated by every part; no field has a default. |
| arch M4 | §A.8 | No second ladder: `fit_rungs[]` gains the row `drop-compound`, and the `compound_rows[]` choice is attempt-level state that T1 can retry. |
| arch M6 | §A.4 | Keep is CONTROLLER EDGES into [EMIT-ENTRIES]' closure. The hybrid's `pcrec_emit_dfa_engine(cx, fn, "static ")` (`emit_vm.c:12761`) is subsumed by `pcrec_entry_linkage` in B0, as its first zero-mover customer. |
| arch S2 (and Q1 of rev 1) | §A.11 | Superseded by D163 add. 2 item 2: ALWAYS ON, no family bit, bit 55 stays free. One harness-only force-decline lever instead (§A.11). |
| arch S1 | §A.7 | Every stamp classified pattern-level or machine-level; each machine-level stamp has a defined compound value, never inferred from absence. |
| arch S3 | §A.10 | Table kit: C1 trace site key, `TABLE_ROOTS` root, row-reach witnesses, the trace build's declared-read check. No `--list-axes` projection (Frank: no axis row). |
| arch S4 | §A.5 | Parts inherit `emit_search_head`'s `noclone` (K24). Whether part entries also get `noinline` is decided by the short-call scratch cell at B4 (§E.3). |
| arch S5 | §A.3 | The admission reads the plain compile's selections through a declared projection (`compound_rows[].reads`), checked in the trace build like `CandNode.reads`. |
| arch S6 | §H U6 | Shared tables between parts: deferred (D77), trigger named. |
| arch S7 | §A.1, §C | `CompRow.state_words` reserved now (0 for split); the caller-struct access is §C's. |
| arch N1 | §A.5, §G Q2 | `__` is reserved for parts; a user prefix containing `__` is refused (population 0 in the tree). |
| arch N2 | §A.12 | Compile CPU: F's NFA/DFA build hits `dfamemo` (`src/opt/dfamemo.c`); Q is one new build. A D45-margin row at B4. |
| arch N3 | §A.13, §H U1 | The hybrid's re-expression trigger is "a client needs a part interface wider than entries". |
| arch N4 | §E.2 | Twin arms: align and `-futf-check` (six utf8 arms). |
| arch §H | §E.3 G4 | G4's expected symbol set comes from the PLAIN artifact's own `nm -g`, not from B0's closure. |
| chk M3 | §E.2 | The differential runs the SHIPPED config: derived DFA Q (never node + prune, not `(?!)`), every option arm, per-ID `q=dfa` and `matches > 0` recorded. Twin2: 177 case-arms, 2,170,123 cells, 574,769 matches, 0 differences. |
| chk M4 | §E.2 | Subject alphabet built from the pattern's own non-ASCII bytes and `\x{...}` code points plus `\xc3\xa9`, `\x80`, lone `\xc3`, `\xff`; asserted present per case. The panel's witness subjects are added verbatim. |
| chk M5 | §E.4 | Each decline control records its reason and asserts it. CMP-1 and its siblings declared UNREACHED in the DFA-only build where their witnesses are VM. The A2 check is an independent walk of Q's tree. |
| chk M6 | §E.5 | The D94 recipe greps by macro and field NAME. |
| chk M7 | §E.3 G3 | G3's attempt clause is DROPPED; loads only (the wrapper's n+3 attempt entries show as loads). |
| chk S8 | §E.3 G3 | G3's constants derived: excess ≤ calls (one seed byte per Q call); growth by the 4k/k ratio test; the k set justified. |
| chk S9 | §F B0-B2 | B0-B2's validation is not "zero movers" alone: each has a positive control (a unit drive that must produce the new text). |
| chk S10 | §E.3 G6 | The landing bar is every bench artifact (bench reach is 0), with the 16 single-class floor rows and the 2 concat-sqli rows named; "byte-identical" is defined. |
| chk S11 | §E.2, twin CLAUDE.md | `sizes.tsv`/`one_tu_probe.txt` get their reproduction commands; revision 2's own results all have generators. |
| chk S12 | §B.4 A4 | Q's cap: Q compiles under P's caps, and the admission declines if Q's own ladder degraded it. |
| D163 add. 2 item 2 | §A.11 | ALWAYS ON, the one harness-only lever, its home and its fence. |
| D163 add. 2 item 3 | §D.1 | Captures on demand as a named client. |

## 0. Answers first

1. **A compound is one artifact** (one pattern, one prefix, one `.c` + `.h`, ONE exported call
   interface, one `rx_info`; D88 add. 1) whose `.c` holds several PARTS. Each part is the
   unchanged pipeline run on a DERIVED input: an AST rewrite at the composer hook and/or
   per-part OPTIONS. A CONTROLLER, a combinator expression over typed part results (§A.2),
   implements the default entry set. A client is one row of the first-match table
   `compound_rows[]`.
2. **Always on, no deny axis** (D163 add. 2 item 2). There is no flags bit, no `-f` spelling,
   no `--list-axes` row and no `tuning.md` section. The plain artifact is compiled anyway (it
   is the fallback and the admission's input), so ONE harness-only lever can force-decline the
   whole family. It lives in an internal options struct reached only by a harness build of the
   CLI (`build/pcrec-harness`), outside `pcrec_options` and outside the caller contract
   (§A.11). An artifact built with it stamps `<PREFIX>_COMPOUND "forced-off"`, so it can
   never pass for a shipped one.
3. **Linkage is [EMIT-ENTRIES]' three categories** (EXPORTED / KEPT STATIC / OMITTED),
   landed first as an internal, zero-mover, non-abi step. Keep is the controller's EDGES
   into the closure (§A.4).
4. **The controller owns ONE prologue computed from P** (range, guard, `-futf-check` with P's
   lookbehind reach); parts are compiled guards-off (§A.6). The floor is the ALIGNED `from`.
   Twin: six utf8 option arms, 0 differences; the "Q's reach" and "no prologue" plants fire.
5. **[MATCH-SPLIT]'s parts.** F is a BOUND on P's own attempt (`start_max = search_from`): one
   attempt, no tree wrap, so `(?R)` keeps P's root (§B.1). Q is P with every `\G` killed (required)
   and `^`/`\A` killed (route only), then never-pruned; called and referenced groups are kept
   (§B.1). The controller is `first-nonzero(F at f, Q from next_pos(f))` (§B.2).
6. **Why F is a bound and not `_match`.** On an attempt route `_match` is `"search-filter"`: it
   runs the whole attempt loop and then filters. As F it is answer-right and cost-wrong:
   measured, K106's internal run stays at 128,040,004 loads and a trailing-run match costs
   2.00× today. With the bound F the same cells read 3 loads and 1.0001× (§B.5, finding J-2).
7. **The first build is PIN-ONLY** (chk B1, D163 add. 2): Q's route must be `rev-end`, or Q is
   never (the floor-only compound). Counted on the twin's case list: 43 case-arms of that
   shape; mssurvey's population gives about 30 patterns (20 S+E DFA, 1 G+E, 9 floor-only),
   **bench reach 0** (Frank's Q5 ruling).
8. **Cost by counted loads** (§B.5): K106 128,040,002 → 3; wrapper 16,003 → 6 with both
   matches; floor-only `a{0,4}\A` 63,994 → 4; trailing matches 1.0001×. Two shapes read
   3.00×, both the final-newline two-seed walk (`\s+$`, `\s*?$`), which is rev-end's own cost
   and B3's (the match-end mark, D164). G3 is RED on them until B3 lands, by design.
9. **Stamps.** `<PREFIX>_COMPOUND` on every artifact (`"none"`, a row name, or
   `"forced-off"`). Every stamp is classified pattern-level (P's) or machine-level (the
   compound's defined value: `"compound"` for the route family; per-stamp sentinels for the
   rest), and the parts keep their own machine-level stamps under part prefixes (§A.7).
10. **Captures on demand is a named client** (§D.1): `select-by-arg(caps == NULL →
    a `--no-captures` part; otherwise P's VM part)`, triggered by the persisting caps/nocaps
    class gap (D119 ledgers: `auto-nocaps` carried 65 of cycle 1's 91 win/tie rows).
11. **Build (§F):** B0 EMIT-ENTRIES internal → B1 part mode and options → B2 derivation →
    B3 the match-end mark (D164, its own abi event) → B4 the compound driver, split pin-only,
    the stamp (THE abi event) → B5 S+F on its trigger → B6 VM parts → B7 captures on demand
    on its trigger → B8 the cross-call hook with [FINDALL-NEXT].

## A. The tool

### A.1 What a client declares

```c
typedef struct {
    const char *role;          /* 1-3 chars: part prefix <prefix>__<role>             */
    PcrecDeriveFn derive;      /* AST -> AST at the composer hook, or NULL (none)     */
    uint64_t flags_set;        /* pcrec_options flags forced ON for this part          */
    uint64_t flags_clear;      /* ... forced OFF (e.g. the guards, the utf check)     */
    PcrecEngine engine;        /* AUTO, DFA or VM: stated, never inherited silently   */
    PcrecPartBound bound;      /* PB_NONE, or PB_ONE_ATTEMPT (start_max = search_from) */
    unsigned need;             /* PART_NEED_*: what the part must deliver (see below) */
} CompPart;

typedef struct {
    const char *name;          /* stamped <PREFIX>_COMPOUND "<name>"                    */
    bool (*pre_admits)(const CompIn *in);   /* plain selections + derivation only    */
    bool (*admits)(const CompIn *in);       /* ... plus the parts' own compiles      */
    const CompPart *parts; int nparts;
    const CompExpr *controller;             /* a combinator expression (§A.2)        */
    const CandRead *reads; int nreads;      /* declared projection reads (§A.3)      */
    unsigned state_words;                   /* §C; 0 until [FINDALL-NEXT]            */
} CompRow;

static const CompRow compound_rows[] = {
    { "split", split_pre_admits, split_admits, split_parts, 2, &split_ctrl,
      split_reads, 2, 0 },
    /* later clients, each behind its own trigger (§D) */
};
```

**No silent default (arch M3, memory `pcrec-no-silent-defaults`).** Every `CompPart` states all
seven fields; a table-build self-check refuses a part whose `engine` is the zero value or whose
`flags_set & flags_clear` is non-zero. A part's options are P's options with `flags_set` OR-ed
in and `flags_clear` masked out. Nothing else is inherited by accident: `tune`, `analysis`,
`features`, `encoding` and every cap are P's by the stated rule "parts compile under P's
options except the named flags", which is a rule written once, not a default per field.

**`need`** is what the controller reads from the part, so the closure (§A.4) can be computed:
`PART_NEED_SEARCH` (the search entry), `PART_NEED_MATCH_CAPS`, `PART_NEED_NEXT_POS`,
`PART_NEED_VALID_UPTO` (the prologue's reach check reads P's, so this is the F part's when F
is P under a bound). It replaces revision 1's undefined `need`.

**For split**:

| part | role | derive | flags_set | flags_clear | engine | bound | need |
|---|---|---|---|---|---|---|---|
| F | `f` | none | `PCREC_NO_STARTPOS_GUARD` | `PCREC_FORCE_UTF_CHECK`, `PCREC_FORCE_STARTPOS_ALIGN` | DFA | `PB_ONE_ATTEMPT` | SEARCH, NEXT_POS, VALID_UPTO |
| Q | `q` | `derive_split_q` | `PCREC_NO_STARTPOS_GUARD` | `PCREC_FORCE_UTF_CHECK`, `PCREC_FORCE_STARTPOS_ALIGN` | DFA | `PB_NONE` | SEARCH |

`engine = DFA` on both is the first build's A4 (§B.4) stated as an option: a part that cannot
compile on the DFA refuses, and a refusing part declines the row.

### A.2 Controllers are combinators over the locate × finish vocabulary (arch M2)

`locate_finish.md` §1.2 types every locator's result as `(I, e, D)` keyed on `CT_*` bits
(`SPAN` = `CT_START`, `LOWER` = `CT_LOWER`, `AT` = a point request, `NOMATCH` = `CT_VERDICT`,
`ENDSET`), and FINISH as four actions (`nomatch`, `report`, `verify-at`, `search-from`). A
part entry call is one of those at the artifact boundary: `<part>_search(from)` hands a `SPAN`
(match), a `NOMATCH`, or a give-up; a bounded part's search is `verify-at` at a point; a
`next_pos` is a `LOWER` relocation. A controller is an expression over five combinators, each
a generic emitter parameterized by part names; a row never writes C itself.

| combinator | meaning, in the vocabulary | first client |
|---|---|---|
| `first-nonzero(A@x, B@LOWER(g(x)))` | ask A at `x`; a `SPAN` or give-up is final; on `NOMATCH` relocate to `LOWER = g(x)` and ask B there (FINISH `search-from`) | split: `F@f`, then `Q@next_pos(f)` |
| `min-start-then-finish(L1..Lk; V)` | each locator hands `SPAN`/`LOWER`; take the minimum start; FINISH `verify-at` with V there; the losers' results are §C's cache | 4c, per-branch locators (§D.3) |
| `locate-then-finish(L; V)` | L hands an exact `SPAN`; V `verify-at` the start with a ceiling (the hybrid's shape, across parts) | DFA locate + VM finish (§D.2) |
| `select-by-arg(p; A, B)` | a predicate on the CALL's arguments picks the whole sub-expression | captures on demand (§D.1) |
| `dispatch(level; A1..Ak)` | a run-time CPU level picks the part | arch variants (§D.5) |

**Type check at table build.** Each combinator states the result types it accepts and hands;
each part's entry states what it hands (from its `need` and `bound`). A row whose expression
does not type-check is a table-build error, the same check `locate_finish.md` §2.3 makes for
FINISH totality.

**In-Job LOCATE row or compound part? (arch M2's question).** A part is the unchanged pipeline
on a derived input; an in-Job row is a selection inside one machine. The rule:

- If the second machine is P under ERASURE only (same tree, same options, D31), it is an
  in-Job row: the hybrid's prefilter, `rev-end`, a FINISH `verify-at`. K108's case (a nullable
  pattern whose hybrid prefilter is declined though a full exact search would be linear) is
  therefore better as an in-Job change, lifting the nullable decline when the locator is exact
  (`locate_finish.md` §4), than as client §D.2.
- If the second machine needs a DIFFERENT TREE (split's Q, 4c's per-class searches) or
  DIFFERENT OPTIONS (captures on demand, [ADAPTIVE-ARM], arch levels), it is a compound part.

### A.3 The driver: `compound_rows[]` at the driver tier

The table lives in a new `src/core/compound.c`, the driver tier beside `compile_driver`.

1. **The plain compile runs first, exactly as today.** It is the fallback (the refusal set
   cannot grow, except under §G Q1's `--fast-or-fail` question) and the admission's input.
2. **The walk.** For each row: `pre_admits` reads the plain compile's selections through the
   row's declared reads (arch S5): `CandRead { slot, route }` pairs answered by a projection
   function `cand_plain_selection(job, slot, route)`. In the trace build every read the
   predicate makes is held to the declared set, the check `CandNode.reads` already has
   (`[cand-no-name-strcmp]`'s machinery). `pre_admits` also runs the row's derivations (cheap
   tree passes). If it passes, the parts compile (each through `compile_driver` with part
   mode, §A.5), then `admits` reads the parts' own selections (A3/A4 for split).
3. **A part's own failure declines the row** (refusal, cap overflow, a degraded ladder rung:
   chk S12). The walk continues; if no row succeeds, the plain output ships.
4. **The choice is attempt-level state** (arch M4). The current `compound_rows[]` selection is
   a field of the attempt loop's state in `compile_driver`, and T1 (`fit_rungs[]`) can retry
   with it cleared (§A.8). There is no second ladder.
5. **Assemble** (§A.5), then check the caps on the assembled text.

**Why the driver tier, not `cand_rows[]`.** A compound selects among whole compiled machines
under different trees or options. `cand_rows[]` selects a strategy inside one machine.
`match_split_pinonly.md` spliced split into the attempt body and the r1 panel found a
miscompile in that splice.

### A.4 Linkage: [EMIT-ENTRIES]' closure, with controller edges (arch M6)

The entry table and per-engine dependency edges are revision 1's §A.2 (kept): every entry is
EXPORTED, KEPT STATIC or OMITTED, by
`linkage(e) = EXPORTED` if requested; else `KEPT STATIC` if requested kept or reachable through
the edges from an EXPORTED or KEPT entry; else `OMITTED`. Revision 1's one-TU probe still
stands, re-run with revision 2's parts and a generator (`twin/probes2.py one-tu`,
`twin/results/one_tu_probe2.txt`): F + Q + the controller compile clean in one TU under
`-Werror` with every part entry exported; made static with nothing omitted they fail with 27
errors, 18 "static declaration follows non-static declaration" (the parts' `.h` declarations)
and 9 "defined but not used". Declarations must follow the linkage and unused entries must be
omitted, which is the closure's job.

**What changed: keep is EDGES, not a bitmask.** The compound's exported entries are the
default set (`match_api.md` §3¶1). The controller's combinator expression contributes edges
`(compound entry → part entry)`: split's `<p>_search → <p>__f_search`, `<p>_search →
<p>__f_next_pos`, `<p>_search → <p>__f_valid_upto` (under `-futf-check`), `<p>_search →
<p>__q_search`, and for the match-here entries `<p>_match{,_caps} → <p>__f_search` (§B.3). The
closure is computed over the union graph (plain artifact's edges + parts' edges + controller
edges), so a part entry is KEPT exactly when a path from an exported entry reaches it.

**The hybrid is the first customer.** `emit_vm.c:12761`'s
`pcrec_emit_dfa_engine(cx, prefn, "static ")` hard-codes "this embedded engine's search is
static". At B0 it becomes a request through `pcrec_entry_linkage`: the hybrid's VM search
entry has an edge to the embedded DFA search, which is therefore KEPT STATIC by the closure.
Its text is byte-identical (zero movers), which is B0's positive control that the closure
reproduces a shipped linkage decision.

### A.5 Part mode

Part mode is an internal `Ctx` field set by the driver, never a `pcrec_options` bit. It
changes emission only (revision 1 §A.3, kept), plus:

- **Names and the `__` reservation (arch N1).** A part renders with prefix `<prefix>__<role>`.
  Part entries are static or omitted, so two compounds in two translation units cannot
  collide. One TU holding two artifacts can: a user prefix `a__f` beside a compound with
  prefix `a` would redefine `a__f_search`. So `__` is reserved for parts: `valid_prefix`
  (`src/core/compile.c:141`) refuses a user prefix containing `__`. Population in the tree: 0
  (`grep -E -- '-p [A-Za-z0-9_]*__'` over `tests/`, `scripts/`, `examples/`). This is a
  refusal-set move, so it is §G Q2. Under K79 the part's emitters see the placeholder plus
  `__<role>` (a fixed length), so no selection depends on the caller's prefix length.
- **The shared blocks** (ABI block, includes, `PCREC_FEATURE_SET`/`_MODULES`) are omitted
  from a part; the compound header has them once.
- **No `rx_info`, no `main`** in a part. The part keeps its stamp family under its prefix.
- **The bound.** `PB_ONE_ATTEMPT` makes the part's BOUND slot select `attempt-gstart`'s
  payload (`start_max = search_from`) whatever P's own BOUND would be. It is a part option
  read by the start table as a fact deny on the other BOUND rows, not a tree edit (§B.1).
- **`noclone` (arch S4).** Parts' search entries come from `emit_search_head`, which already
  emits `__attribute__((noclone))` (K24's fix), so a part cannot be split into a `.part.0`
  clone. Whether a part entry should also be `noinline` (so the controller stays small) is
  decided at B4 by the short-call scratch cell (§E.3); the default is to let gcc inline.

### A.6 The controller prologue (sem MF1/MF2/MF4, arch M5)

The controller owns ONE prologue, computed from P, and every part is compiled guards-off
(`flags_set |= PCREC_NO_STARTPOS_GUARD`, `flags_clear |= PCREC_FORCE_UTF_CHECK | PCREC_FORCE_STARTPOS_ALIGN`):

```c
int <p>_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2])
{
    /* P's boundary guard, P's option:                                            */
    /*   refuse: mid-character from -> PCREC_ERR_STARTPOS (the K50 guard)        */
    /*   align:  advance from to the next character start (D133)                  */
    /*   none:   nothing                                                           */
    /* P's -futf-check, with P's lookbehind reach (P's VALID_LB, from P's tree    */
    /* BEFORE the prune): if (<p>__f_valid_upto(s, n, from) != n) return -9;      */
    if (from > n) return 0;
    ... the combinator body, with f = from (now aligned) ...
}
```

- **One check, P's reach.** Q's lookbehind reach can be smaller than P's after the prune:
  `^(?<=é)a|b` has P's reach 1 and Q = `b` reach 0. A check with Q's reach accepts a subject
  P refuses (arch M5's witness). The prologue reads F's `valid_upto`, which is P's (F is P
  under a bound). Plant 2 (Q's reach) fires on that witness in the twin.
- **The floor-only compound keeps P's refusals** (sem MF2): `a{0,4}\A` under `-e utf8
  -futf-check` at `from = 1/2` returns `-7`/`-9` from the prologue. Plant 3 (no prologue)
  fires.
- **The aligned floor** (sem MF4): under `align`, `f` is the aligned position, F's bounded
  attempt sees `\G` at `f` (as P does), and `qf = next_pos(f)`. Revision 1 passed the raw
  `from`, which re-opened the atomic witness `(?>\Ga|ab)c` on `c3 a9 61 62 63`. Twin: 0
  differences on all six arms of that witness. That witness is a VM P; the `qf = next_pos(aligned f)`
  correction reaches the DFA route through CMP-13's `\Ga$|b$` (rev-end Q) under
  `-fstartpos-guard=align`. That witness is in the twin's case list for `byte` only
  (`hand:g1`, `results/cases2.tsv`, plus `tests/assertions/rev_end.rxt:338`), where the align
  arm does not exist; its utf8 × align arm was ABSENT from the list and is OWED: the row is in
  `results/cases2_owed.tsv` (§R2.1); one run (6 arms, 13,523 cells, 0 differences) is recorded
  in `results/cases2_owed_run.tsv`, and the twin has no plant that hands F the raw `from` (plants 1-3 only), so CMP-13's
  DFA detection is by the answer suites, not yet by a twin plant.
- **No double check.** Revision 1 checked validity in every part; now it is checked once.
- **Measured** (sem MF1's witness): `\A\s+|\s+\z` under `-e utf8 -futf-check` has P's reach > 0
  (`\A` raises it) and Q = `\s+\z` none, so a check with Q's reach answers where P refuses;
  the twin's plant 2 goes red on it, on a DFA P with a rev-end Q. The emitted reach confirms
  it and confirms that F can carry P's check: `<p>_VALID_LB` is 1 for P compiled default,
  `-futf-check` or `-fno-startpos-guard` alike (a parse-time fact, not a flag's), and 0 for
  Q = `\s+\z`.

Measured by the twin (§E.2): 177 case-arms, every utf8 case under the six arms
{refuse, none, align} × {`-futf-check` off, on}, 0 differences against today's artifact
compiled with the same arm.

### A.7 Stamps: pattern-level and machine-level (arch S1)

Every stamp is one of two kinds, and the kind decides its value on a compound:

| kind | meaning | value on a compound | examples |
|---|---|---|---|
| pattern-level | true of the pattern and the caller contract, whichever machine runs | P's (computed once, by the plain compile) | `_ENCODING`, `_NCAPS`, `rx_info.flags`, `_TUNE`, `_FINDINGS`, `_NAME`, pattern text, `_VARS`, the budgets (per part call), `_ENGINE` ("vm" if any part is VM: "can a call give up") |
| machine-level | describes one machine's route or strategy | a DEFINED compound value; the parts' own values stay under their part prefixes in the `.c` | `_DFA_SCAN`, `_DFA_PREFILTER`, `_DFA_START`, `_DFA_MATCH` (and `rx_info.scan`/`prefilter`/`search_form`/`match_form`): `"compound"`; `_REQ_BYTE`, `_REQ_RUN`, `_REQ_WHY`, `_VM_*`, `_START_SCAN`, `_RESEED`, ...: each its declared compound sentinel |

**The sentinel table.** D156 addendum 2's generated-stamp rule (`locate_finish.md` L2.1)
already gives every machine-level stamp an off-path value. A compound is one more cell in that
generator: each machine-level stamp's catalogue row gains a `compound` value (`"compound"`
for the string route family; for the others the value the generator already uses for "not on
this path", stated per stamp in `match_api.md` §6.3). No reader infers a fact from absence
(`RX_REQ_HANDOFF` Q3 (a)'s rule). The full table is B4's spec hunk; its readers are found by
macro NAME (§E.5).

**The policy stamp.** `<PREFIX>_COMPOUND` on every artifact: `"none"` (no row admitted),
the row name (`"split"`), or `"forced-off"` (the harness lever was set and the default build would have shipped a row
name, §A.11; never merely because a `pre_admits` passed). It is pattern-level.

### A.8 Size: the caps, and `drop-compound` as a T1 row (arch M4)

- The caps measure the ASSEMBLED text (D88 item 3: the unit is one artifact). Parts compile
  under P's caps, each with its own ladder; a degraded part declines the row (chk S12).
- **`drop-compound`** is a row of `fit_rungs[]` (`src/core/compile.c`), on `FIT_L_SIZE`,
  placed FIRST among the size rungs: dropping the compound returns exactly the plain
  artifact, which already fits, so it must be tried before any rung that degrades P's own
  machine. Its action clears the attempt-level `compound_rows[]` state and restarts (the
  plain output is reused, not recompiled). It is DEGRADING in D135's sense, so its `fof`
  cell decides whether `--fast-or-fail` refuses or ships the plain output: §G Q1.
- **Measured** (`twin/results/sizes2.tsv`, generator `twin/probes2.py sizes`, chk S11): linked
  `.text`+`.rodata`+`.data.rel.ro` of a binary calling only `rx_search`, gcc 15.2 `-O2
  --gc-sections` standing in for the omission:

  | cell | Q | today | compound | ratio |
  |---|---|---|---|---|
  | trim | `\s+$` | 981 B | 2,975 B | 3.03× |
  | wrapper | `\}\s*$` | 1,175 B | 2,767 B | 2.35× |
  | floor-only `a{0,4}\A` | never | 967 B | 1,031 B | 1.07× |
  | concat-sqli (B5) | derived | 194,443 B | 224,503 B | 1.15× |

  F is P's machine again (the bound acts at emission), so a pin-only compound is about today
  plus Q's small end-pinned machine plus the controller: about 2 KB in absolute terms on the
  idioms. Revision 1's `sizes.tsv` agrees within 3%.

### A.9 Budgets under D158 (sem notes)

- **Each part entry initializes its own budget.** A compound search makes at most one call
  per part.
- **DFA parts have no budget** (the first build). Nothing to show.
- **VM parts (B6): the give-up surface is NOT a subset in either direction.** A compound can
  ANSWER where the plain artifact gives up (Q is P minus dead arms; a fresh budget per part),
  and in principle the reverse (engine choices are not monotone in the tree; the bounded F
  may cost a step more at the floor). So revision 1's "drop-in, answer for answer" is
  dropped. What the compound guarantees: on every subject and call, a non-give-up answer of
  the compound equals P's answer; a give-up of a part is returned at once (`first-nonzero`
  treats it as final). B6's gate is the give-up differential: 0 cells where the plain
  artifact answers and the compound gives up (§E.3). The other direction is §G Q3.
- **Caller buffers (VM parts).** One region sized by the max over parts; the controller builds
  each part's descriptor per call.

### A.10 Where it lives; the table kit (arch S3)

- **Files.** `src/core/compound.c` (`compound_rows[]`, the driver, the assembler, the
  combinator emitters), `src/opt/derive.c` (derivations), part mode and
  `pcrec_entry_linkage` in `src/gen/`.
- **The table kit**, as every house table has it:
  - the C1 trace site key `compound` (records the row walked, `pre_admits`/`admits`
    verdicts, the declared reads);
  - a `TABLE_ROOTS` root for `call_graph.py --family compound`;
  - a row-reach witness per row in `tests/compound/`, asserted by stamp;
  - the trace build's declared-read check (§A.3).
- **No `--list-axes` projection**: there is no axis (D163 add. 2 item 2). The table is visible
  through the artifact's `--emit-ir`/`--emit-facts` listing (the row and each part's listing
  under its role; `ir_listing.md`/`facts_listing.md` hunks at B4), which describes what an
  artifact IS, not a switch.

### A.11 Always on: the one harness-only lever (D163 add. 2 item 2)

**There is no public deny.** No flags bit (bit 55 stays free), no `-fno-...`, no
`strategy_denials` entry, no `--list-axes` row, no `tuning.md` section, no `.rxt` config word.

**The lever.**

- **Library.** An internal options struct, declared in `src/core/internal.h` only:
  `typedef struct { unsigned compound_off : 1; } PcrecHarnessOptions;` and one entry
  `pcrec_compile_harness(pattern, const pcrec_options *, const PcrecHarnessOptions *, ...)`,
  an unadvertised name that no header a caller includes declares (it is not in `lib/pcrec.h`,
  the contract). It carries `__attribute__((visibility("hidden")))` as hygiene for a shared
  build only. **Hidden visibility does NOT fence the shipped static archive.** `libpcrec.a`
  ships; visibility is a dynamic-symbol-table property, so the archive member keeps the
  symbol global (`nm -g --defined-only` lists it, measured on a hidden-attribute probe) and an
  executable that links the archive resolves it statically: a caller who declares the
  prototype can call it. The fences that hold are the three below, none of them the
  attribute:
  1. **The obscure name**: unadvertised, in no public header, in no spec or guide sentence.
  2. **The symbol-allowlist check** (NEW; `tests/compound/run_symbol_allowlist.sh`, a
     `make test` section, built at B4). Verified by grep that no such check exists:
     `tests/memfn/run_link_checks.sh` C15 asserts only that every global of `build/libpcrec.a`
     begins `pcrec_` (`pcrec_compile_harness` passes it), and
     `tests/spec_mod0/check01_isolation.sh` is the enabled-set isolation `nm` check, whose
     named-exception count is pinned at exactly 1 (a lever row there would break that pin and
     is the wrong host). The new check: read `nm -g --defined-only build/libpcrec.a`; the
     PUBLIC SET is the names `lib/pcrec.h` declares (derived from the header by the same
     extraction the registry tests use, never hand-listed); every other global must be a row
     of `tests/compound/symbol_allowlist.tsv` (`symbol<TAB>reason`, a non-empty reason per
     entry). It fails on a global with no row (a new export), on a row naming no global
     (stale), and on an empty reason. Population: today's archive has 566 globals of which 6
     are public, so the list is born with about 560 rows, generated once from `nm` with the
     declaring internal header as each row's reason; the lever's row is one of them and its
     reason is hand-written ("harness lever, `build/pcrec-harness` only"). Controls: a planted
     undeclared global is flagged; a planted stale row is flagged; floors on both
     populations (K35). Its sabotage row is CMP-17 (§E.4).
  3. **`run_lever_fence.sh`** (described next), with its grep scope widened to `tests/`, `scripts/`
     and `cli/` as well as the prose directories, allowlisting the harness's own legitimate
     uses (the `-DPCREC_HARNESS` object of `cli/main.c`, `build/pcrec-harness`'s callers, the
     lever arm of `tests/axes/run_axes.sh`, the emit_sweep lever arm, `tests/compound/`).
- **CLI.** `cli/main.c` compiled a second time with `-DPCREC_HARNESS` into
  `build/pcrec-harness`, which accepts one extra option `--harness=no-compound` and calls the
  harness entry. The shipped `build/pcrec` has no such option: in a normal build the word is
  an unknown option. `make` builds both (the second is one more object of `main.c`).
- **The artifact marks itself, exactly when the lever changed it.** `pre_admits` passing is
  NOT "the default build admitted a row": admission continues through Q's derivation, Q's own
  ladder check (A4/S12) and the assembled text's caps, and `drop-compound` (§A.8) can still
  reject the row after `pre_admits` passed. Stamping `"forced-off"` on a `pre_admits` pass
  alone would mark an artifact whose default build ships plain with `"none"`, so the lever
  would move a stamp line on an artifact it changed nothing about. So under the lever the
  walk runs the COMPLETE admission, the same code as the default build, including the part
  compiles and the caps, and replaces only the last step (ship the compound text) with ship
  the plain text. The stamp is `"forced-off"` ONLY when the default build WOULD have shipped a
  row name, and `"none"` otherwise. Hence the exact property: (a) wherever the default stamp
  is `"none"` the lever output is byte-identical to the default output; (b) wherever the
  default stamp is a row name the lever output is the plain output plus `"forced-off"` (and
  the `-o`-basename-independent stamp line, nothing else); (c) no artifact the lever changed
  can pass for a shipped one. The lever build pays the part compiles (harness only).

**How the harness uses it.**

- **test-axes** (`tests/axes/run_axes.sh`): its axis list is derived from `--list-axes`, so the
  lever is a separately DECLARED internal arm (`INTERNAL_ARMS=(no-compound)`) run through
  `build/pcrec-harness`. Answer identity is checked exactly as for an axis. Its population
  floor is the count of artifacts whose default build stamps a row name (K35), and it asserts
  the exact property above both ways: lever `"none"` ⇔ default `"none"` and byte-identical
  (the lever moves nothing else); lever `"forced-off"` ⇔ default stamps a row name, with the
  stamp line the only difference from the plain output. A `"forced-off"` where the default
  stamps `"none"`, or a `"none"` where the default stamps a row, is a failure (CMP-15).
- **Bisects and triage.** "Is the compound responsible?" is `pcrec` vs `pcrec-harness
  --harness=no-compound` on the failing cell.
- **emit_sweep** gains a lever arm (G6's comparison, §E.3).

**Kept from becoming a de-facto public flag:** it is not in the shipped binary, not in the
public header, not in any `--help` or listing; the artifact self-marks; and a check
(`tests/compound/run_lever_fence.sh`) fails if `--harness=` or `pcrec_compile_harness` appears
in `docs/spec/`, `docs/guide/`, `README.md`, `examples/`, `lib/`, `tests/`, `scripts/` or
`cli/`, outside an explicit allowlist of the harness's own uses (listed in fence 3 above);
and `run_symbol_allowlist.sh` holds the library's export surface to the public header plus a
reasoned allowlist. The only spec sentence is
the `"forced-off"` value in `match_api.md` §6.3's `_COMPOUND` value set ("an artifact built by
the harness with the compound family declined"), because a stamp value is caller-observable
(D80).

**Alternatives declined.** An environment variable read by the CLI is invisible in `--help`
but inherited by every subprocess and copied into scripts, which is how a de-facto public
flag starts. A hidden flag in the shipped binary is the same. A `pcrec_options` field is the
contract. This is an answer-free choice with no measured cost difference, so it is the
manager's (memory `pcrec-answer-free-choices-are-mine`), recorded here.

### A.12 Compile CPU (arch N2)

A compound compile is the plain compile, F, Q and the assembly. F's NFA/DFA build is the plain
compile's (same tree, same options apart from the bound and the guards, which act at
emission), so it hits `src/opt/dfamemo.c`'s content-keyed memo. Q is one new, smaller build
(a pruned tree, end-pinned). The bound is therefore about 2× the plain compile in the worst
case. B4 adds a D45-margin row: the admitted set's compile CPU against the per-compile budget,
with the measured ratio, on the Linux dev box.

### A.13 The VM hybrid (arch N3)

The hybrid stays as it is. It differs from a compound in two ways: its second machine is P
under erasure from the same `Job` (an in-Job row by §A.2's rule), and its hand-off is wider
than an entry call (the window end becomes the MRL ceiling; the reseed rows and the landing
read DFA internals). **Trigger to re-express it as a compound:** a client needs a part
interface wider than entries (a window, a reseed protocol). Until then B0's linkage
re-expression is its only change.

## B. First client: [MATCH-SPLIT], pin-only

### B.1 The parts

- **F (role `f`) = P under `PB_ONE_ATTEMPT`.** No tree change. The bound makes F's search one
  attempt at `search_from`; P's own `^`, `\A` and `\G` keep their meaning there, and `(?R)`,
  `(?0)` target P's root (sem MF3's blocker is gone: revision 1's `A_CAT(A_GSTART, root)` made
  them re-enter `\G(?:P)`; witness `^x|a(?R)?b` on `"aabb"`). F is compiled guards-off; the
  prologue has already refused or aligned `from` (§A.6).

  In the twin the bound is the emitted line `const size_t start_max = subject_length;`
  rewritten to `= search_from;`, which is what the BOUND row `attempt-gstart` emits. On a P
  with no DFA attempt loop (VM P, the twin's VM cases) the twin uses P's `_match_caps`, which
  on the VM is the anchored body. **Not `_match` on a DFA attempt route** (finding J-2).

- **Q (role `q`) = derive_split_q(P).** Two passes in `src/opt/derive.c`:
  1. **Kill.** Every `A_GSTART` becomes the never node (an empty `A_CLASS`), REQUIRED (a `\G`
     left in Q would assert at the position the controller searches Q from). Every `A_BOL`
     with `!u.anch.multiline` (`^` without `(?m)`, and `\A`) becomes never: a route
     optimization (past the floor it is false anyway). Not killed: a node inside a
     lookbehind or inside a group called from one (it can be read below the attempt start);
     `(?m)^` (Q handles line starts itself). A `\G` the kill cannot reach declines the row.
  2. **Prune, bottom-up** (revision 1's rules: `CAT` with a never part is never, `ALT` drops
     never arms, `REP{m≥1}` of never is never, `REP{0,…}` of never is EMPTY, a positive
     `LOOK` of never is never, a negative one EMPTY), plus (sem S1):
     - **A group is never deleted if anything can still reach it**: a call target (`(?n)`,
       `(?&name)`, `(?R)` reaches the root), a backreference target (`refs[]` read as a SET,
       so a `(?J)` duplicate name keeps every group it names), or a condition's group. Such
       a group's arm is kept as a never arm instead (it cannot match past the floor, which is
       what P does), or, at B6, moved into a `(?(DEFINE)...)` block so its number, body and
       unset-ness survive.
     - In the first build (DFA parts) any such pattern declines anyway: calls and
       backreferences route the VM. The rule is stated now so B6 inherits it.
     - Calls and conditionals themselves are left as they are.
     - A pruned capture group keeps its number on the `A_CAP` node and renumbers nothing.

**Why prune** (revision 1, measured): the facts that pick Q's route are not dead-path aware;
unpruned `[^\x00-\xff]\s+|\s+$` stamps `unanchored`, pruned `\s+$` stamps `rev-end`.

**The twin derives Q the build's way** (chk M3). `twin2.py` parses P into a small tree, kills
to an empty class (not `(?!)`, which routed the VM), and prunes by these rules. Text cannot keep
a deleted group's number, so a never arm holding a capture group is kept unpruned (logged per
case as `keepcap`); the AST derivation does not need that.

### B.2 The controller

```
split = first-nonzero( F @ f ,  Q @ LOWER(next_pos(f)) )
        where f = the aligned from, and F is asked only if the floor can be live
```

```c
int <p>_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2])
{
    <prologue from P, §A.6>
    if (from > n) return 0;
    size_t qf = from;
    if (from == 0 || <HAS_G>) {                  /* the floor can be live */
        int r = <p>__f_search(s, n, from, caps);  /* one bounded attempt at f */
        if (r != 0) return r;                    /* match, give-up or refusal: final */
        qf = <p>__f_next_pos(s, n, from);        /* Q only PAST the floor */
    }
    <Q never: return 0;>
    int r = <p>__q_search(s, n, qf, caps);
    <pad slots Q lacks, only when <P>__Q_NCAPS < <P>_NCAPS>
    return r;
}
```

The soundness argument is revision 1's §B.2 items 1-4, unchanged by revision 2 except that
`f` is now the aligned position: (1) a match at the floor is P's priority answer at the
leftmost possible start, and F is P's own attempt there; (2) past the floor every killed node
is false in P too, and a false node and a never node behave identically under every
construct, so P and Q anchored at `t > f` are the same matcher; (3) with `from > 0` and no
`\G` every start is past the floor; (4) `Q.search(from)` instead of `next_pos(f)` is wrong when
an atomic or possessive group holds a floor arm (`(?>^a|ab)c` on `"abc"`), D163 add. 2 item 3.

The requirements of `match_split_requirements.md` §2.1 are met as revision 1 §B.2 lists
(R1-R12). R12 changes: there is no `-fno-match-split`; the lever (§A.11) is the harness's
arm.

### B.3 The other entries

| compound entry | body |
|---|---|
| `<p>_search` | the controller (§B.2) |
| `<p>_match`, `<p>_match_caps` | the prologue, then F's bounded search at `pos` (a `SPAN` at `pos` or `NOMATCH`), converted to the match-here return | 
| `*_in` | the un-suffixed entry with `(void)buffers` (DFA-only compounds) |
| `<p>_next_pos`, `<p>_valid_upto` | the compound's own (the encoding residual, P's reach) |
| `<p>_info` | one (§A.7) |

**Why not F's `_match`.** On a DFA attempt route `_match` is `"search-filter"`: it runs the
whole attempt loop from `pos` and filters by start. F's bounded search runs one attempt, and
its answer is the match-here answer (`match_api.md` §3.2¶1: "matches at exactly `ctx->pos`").
So the compound's `_match` becomes O(attempt) where today's is O(n · attempt) on a failing
probe (revision 1's finding I-5), and it is now stated against the right entry.

### B.4 Admission: the `split` row, pin-only

`split_pre_admits` (cheap) and `split_admits` (after the parts compile) are a conjunction of
facts read off compiles. No constant is hand-set.

| # | conjunct | where read | why |
|---|---|---|---|
| A1 | P's plain compile is on an attempt route with BOUND `all` (DFA `attempt[subject_length]`) | the plain compile's BOUND and LOCATE selections (declared reads) | today attempts every start; a fully anchored P is already one attempt and stays byte-identical |
| A2 | the derivation killed ≥ 1 floor anchor and left no `\G`; no called/referenced group was in a pruned arm (first build) | the derivation's own counts, an independent walk of Q's tree (chk M5) | §B.1 |
| A3 | no verb or callout in P (registry-keyed, §B.8) | the registry's attempt-scope column on P's nodes | §B.8 |
| A4 | every part compiled on the DFA without a degraded rung (no `size-cap-retry`, no `sel1-*`, no `prefilter-collapse`) | the parts' `ENGINE` and `ENGINE_SEL` | D158 (§A.9), and Q's cap (chk S12) |
| A5 | **PIN-ONLY:** Q is never, or Q's LOCATE selects `rev-end` | Q's own compile | chk B1: an end-pinned Q has at most the end matches per subject; an unanchored Q's many-match cost waits for B5 |
| A6 | the assembled text fits the caps | `drop-compound` (§A.8) | D84 |

**Counted.** On mssurvey's population, A1-A5 admit: S+E on `attempt[n]` 20 (its Q stamps
`rev-end`), G+E 1 (A5 decides on Q's own compile), and the 9 floor-only single-class patterns
(Q never). About 30 patterns, all corpus witnesses and idioms; **bench 0**. The 18 S+F and 13
G+F DFA patterns (concat-sqli ×2 among them) wait for B5. Every VM-route pattern waits for B6.
In the twin's case list, 43 case-arms have exactly the admitted shape (plain `dfa/attempt`,
Q `dfa/rev-end` or never), all 0 differences.

### B.5 Cost by counted loads (`twin/results/split_loads2.tsv`, `cost2.py`)

Whole find-all, subject-byte loads (the survey's `qdrv.c`), Q DERIVED by `twin2.derive`, F
bounded. Calls and matches are equal on every row (asserted). k = 16,000 unless marked.

| cell | subject | matches | today | compound | ratio |
|---|---|---|---|---|---|
| trim `^\s+\|\s+$` | `Q·\t^k·Q` (K106) | 0 | 128,040,002 | **3** | 0.00000002 |
| trim | `\t^k·Q` (floor match) | 1 | 16,002 | 16,003 | 1.0001 |
| trim | `Q·\t^k` (end match) | 1 | 16,002 | 16,003 | 1.0001 |
| trim | `\t^k·Q·\t^4000` (both) | 2 | 20,003 | 20,005 | 1.0001 |
| trim | `Q·\t^k·\n` (end before a final newline) | 1 | 16,003 | **48,007** | **3.00** |
| trim | `\t^k·Q·\t^4000·\n` | 2 | 20,004 | 28,011 | 1.40 (2.00 at k = 4,000) |
| wrapper `^\s*\{\|\}\s*$` | `{·␠^k·}` (both) | 2 | 16,003 | 6 | 0.0004 |
| wrapper | `Q·}^k·Q` | 0 | 32,003 | 3 | 0.0001 |
| wrapper | `{·␠^k·}\n` | 2 | 16,005 | 13 | 0.0008 |
| tie `^q\|a$\|a\n$` | `q·x^k·a\n` | 2 | 16,006 | 15 | 0.0009 |
| lazy tie `^q\|\s*?$` | `q·␠^k·\n` | 4 | 16,006 | **48,013** | **3.00** |
| floor-only `a{0,4}\A` | `a^k` | 1 | 63,994 | 4 | 0.0001 |
| floor-only | `x·a^k` | 1 | 63,995 | 1 | 0.00002 |

- **K106 is gone and the wrapper's n+3 attempt entries are one.** Matching subjects with a
  floor match, an end match or both read today + 1 or + 2 loads (one per Q call).
- **The only regressions are the final-newline two-seed walk**, `\s+$` and the lazy `\s*?$`,
  at 3.00×: Q's rev-end walks back from `n` and from `n−1` and resolves the tie with a forward
  run. It is rev-end's own cost, carried by every rev-end artifact today. B3 (the match-end mark,
  D164) removes the second walk, and the $-ends become ordinary ends under the DFA's
  existing priority handling. **The post-B3 factor is the match-end mark design's measurement,
  not this one's**: expected about 1.0× where no forward finish is needed (no captures asked),
  higher where captures need a forward run. G3's bound for this shape
  is whatever B3's gate states (§E.3).
- **With `_match` as F** (the wrong form, finding J-2) the same harness read K106 at
  128,040,004 and the end-match cell at 32,004 (2.00×): the search-filter `_match` runs the
  whole attempt loop.

### B.6 What falls out

- **The floor-only compound** (Q never): one bounded attempt where today attempts every
  position; mssurvey finding 6's start half (`a{0,4}\A` and kin), 9 DFA witnesses.
- **`_match` becomes one attempt** on admitted patterns (§B.3).
- **Dead floor arms** (`x^a|b$`): admitted; the floor attempt is wasted but sound.

### B.7 START+FREE (S+F, G+F): waits for its trigger (chk B1)

An unanchored Q costs forward scan + reverse start recovery + finish, where today's attempt
reads a matching span once. chk B1 measured concat-sqli find-all with 1,000 hits at 2.07×
today and `^q|a+b` with one long match at 3.00×; the 0.25× of revision 1 was no-match only.

**Trigger:** a bench reading of concat-sqli on its OWN subjects (the bench's capability and
sentinel sets), which tells whether its real subjects are match-sparse (the 0.25× regime) or
match-dense.

**The cost conjunct, its shape only** (designed at the trigger, memory
`pcrec-build-under-measurement`): admit S+F when the expected cost per subject byte of
`F + Q_forward + m·(Q_reverse + finish)` is below today's attempt cost, with `m` the expected
matches per byte read from the findings prior through [PRIOR-COST-UNIFY]'s scan-expectation
primitive (`prior_cost_unify.md` §2) and the per-route prices from its operation-kind table. No
constant: the conjunct is a comparison of two priced expressions, and a NONE prior declines.

### B.8 Declines: verbs, callouts, `\K`

- **Verbs and callouts** decline the row through a REGISTRY-KEYED predicate (sem notes): the
  registry gains an attempt-scope column (`RF_CROSSES_ATTEMPTS`) on the rows whose effect spans
  attempts or observes their order: `(*COMMIT)`, `(*SKIP)`, `(*PRUNE)`, `(*THEN)` and every
  callout spelling. A1-A3 read it off P's nodes through the SR-8 node stamping. The witness:
  `^a(*COMMIT)b|c` on `"ac"`: libpcre2 no match, a compound `(1,2)`. A new verb row states
  the column and the predicate follows; no list in `derive.c`.
- **`\K`** forces the VM, so the DFA-only build declines it (A4). The cache (§C) declines with
  `\K` or keys on the attempt start.

## C. The cross-call state hook (D163 item 1; built with [FINDALL-NEXT])

Revision 1's §C stands, with three changes:

- **`state_words` is a `CompRow` field now** (arch S7), 0 for split, so the struct exists before
  its first user.
- **`\K` (sem S3).** The reported start can exceed the attempt start, so "no Q match starts in
  `[qf, qs)`" is false under `\K`. A row's cache is declined when P has `\K`, or keyed on the
  attempt start (a fourth word).
- **The caller contract (sem notes).** The cache is valid only while the caller does not
  mutate the subject bytes the struct is bound to. The [FINDALL-NEXT] struct carries `(s, n)`
  at init, and its spec states "the subject must not change between calls that share this
  state; re-initialize after a change". A give-up is never cached (D158).

## D. Clients

### D.1 Captures on demand (D163 add. 2 item 3; arch unlock 1)

**The problem.** A pattern with capture groups routes the VM by default (`ENGINE_WHY
"capture group"`), even when the caller passes `caps == NULL` and wants the whole-match span
only. The same pattern compiled `--no-captures` routes the DFA. The D119 ledgers show the gap:
in cycle 1, `auto-nocaps` carried 65 of the 91 win/tie rows against capture-bearing
competitors (`../dev/optloop/cycle1_caps_view.md`), and 5 rows flip to a loss under the
shipped captures default.

**The row.**

| part | role | derive | flags_set | flags_clear | engine | bound | need |
|---|---|---|---|---|---|---|---|
| N | `n` | none | `PCREC_NO_CAPTURES` | — | AUTO | `PB_NONE` | SEARCH, MATCH |
| C | `c` | none | — | — | VM (as P) | `PB_NONE` | SEARCH, MATCH_CAPS |

```
captures-on-demand = select-by-arg( caps == NULL ; N , C )
   <p>_search(s, n, from, NULL)      -> N's search
   <p>_search(s, n, from, caps)      -> C's search (P's own VM artifact)
   <p>_match(ctx)                    -> N's match  (no caps by contract, §3.2¶3)
   <p>_match_caps(ctx, caps_out)     -> C's match_caps
```

**What it needs from the tool:** per-part options (`flags_set = PCREC_NO_CAPTURES`, §A.1);
the `select-by-arg` combinator; a VM part (B6's budgets and caller buffers: `_in` entries with
buffers go to C); the stamp classification (`_NCAPS` is pattern-level, P's; `_ENGINE` reads
`"vm"` since a call with captures can give up).

**Soundness.** N's span equals C's span only if the capture-erased language with P's priority
gives P's whole-match span. That is D31's erasure claim, which R21 split into "erasure
STRUCTURAL, span-equality BELIEVED-WITH-GATE" (K17/K18). So this client needs its own gate:
the whole-span differential N vs C over the corpus, every startpos and find-all, plus
libpcre2. D158: N is a DFA (no budget), so a `caps == NULL` call can ANSWER where today's VM
gives up; a `caps != NULL` call is today's artifact exactly.

**Admission:** P's plain route is VM with `ENGINE_WHY "capture group"`, and N compiles on a
faster route (the DFA, or a hybrid where P has none). Population: the capture-forced VM set
(`capsurvey` F3 counted 26 patterns VM because of a capture group in its census; the bench's
cycle-1 caps view has the 14-row `"capture group"` bucket).

**Trigger (D77):** the caps/nocaps class gap persists in the D119 ledgers after the in-flight
cycles, read as cells where `auto-nocaps` wins and `auto-caps` loses on the same pattern.

**Composing with split** (a capture-bearing pin-only pattern): one row per artifact in the
first builds; a nested compound (split whose parts are captures-on-demand compounds) is filed
(§H U7).

### D.2 Captures by DFA LOCATE + VM FINISH

Revision 1's §D.1 sketch, reclassified by §A.2's rule: where the locator is P's own erasure,
this is an in-Job change (lift the hybrid's nullable decline when the locator is exact, K108's
population), not a compound. A compound version is needed only if the locator must be built
under different options. Trigger: K108 bench reach.

### D.3 Per-branch locators / 4c (D151 add. 6 F2)

`min-start-then-finish(class searches; P verify-at)`. The tool must offer an internal entry
beyond the public set, `<part>_attempt(s, n, search_from, start, caps)` (one attempt at `start`
with `\G` at `search_from`): that is `PB_ONE_ATTEMPT` with a start other than `search_from`, a
second bound value `PB_ONE_ATTEMPT_AT`. And §C's cache for the losing classes. Trigger: the
[ENG-TACTICS] stage-1 census or a bench cell with two racing classes.

### D.4 [ADAPTIVE-ARM]

Two parts under two option derivations (`flags_set` = a deny bit), a counter in §C's state, a
`dispatch` on it. Trigger: the row's own.

### D.5 Arch-specific versions with run-time dispatch

Parts = the same pattern rendered for different levels (part options carry the level and per-
function `target` attributes under arch guards), `dispatch(level; …)` through the kit's level
query. Trigger: a SIMD form that must ship beside its scalar form at the whole-artifact grain
(D144 add. 4).

## E. Checks

### E.1 Carried over (r1 panel on `match_split_pinonly.md`, still applicable)

Revision 1's §E.1 list stands (chk M2-M6 and S1-S4, sem N1-N3), with `-fno-match-split`
replaced by the lever wherever it appeared.

### E.2 The differential on the SHIPPED config (chk M3/M4, sem S2, arch N4)

`twin2.py` is the build's gate G2 in prototype:

- **Q derived** as §B.1 (kill to the never node, prune), so Q routes as the build's will.
- **F bounded** (§B.1), the controller with its prologue (`ctrl2.c.in`).
- **Every option arm**: byte; utf8 × {refuse, none, align} × {`-futf-check` off, on}.
- **Subjects** carry the witness bytes (asserted), the pattern's own literal characters, the
  pattern's words (so keyword patterns match), and the panel's witness subjects verbatim.
- **Recorded per case-arm:** P's and Q's stamps, F's form, the derivation's counts, matches.

**Result** (`twin/results/split_differential2.tsv`, cases `results/cases2.tsv`: revision 1's 94
plus 18 panel witnesses): 177 case-arms run, 6 declined with their reason (verb, nothing
killed: lookbehind-held `^`, `(?m)`, conditional), **2,170,123 cells, 574,769 matches, 0
differences** compound vs today, 0 differences today vs libpcre2, 0 find-all differences. Q
routes: `dfa/rev-end` 79, `dfa/unanchored` 53, never 20, `dfa/attempt` 2 (A5 declines),
VM 23. One case-arm reads 0 matches (`word_lead_edge`, an S+F idiom outside the first build);
every admitted-shape case-arm matches.

**Failing direction** (`twin2.py --plant N` over nine panel witnesses, `results/plants.tsv`;
the clean controller reads 0 differences on the same case-arms):

| plant | what it breaks | case-arms that go red |
|---|---|---|
| 1 | Q searched from `from` (D163's literal text) | `atomic1`, `atomic2`, `poss1` (byte), `semMF4` (all six utf8 arms): every witness is VM |
| 2 | `-futf-check` with Q's lookbehind reach | `semMF1` `\A\s+\|\s+\z` (DFA P, DFA rev-end Q) and `archM5` (VM P), the three `-uc` arms each |
| 3 | no prologue (the parts are guards-off, so P's guard and check are lost) | 22 case-arms over `semMF1`, `semMF2`, `semMF4`, `archM5`, `trimU`: every refuse arm and every `-uc` arm |

Plant 2 fires on a DFA witness, so the "Q's reach" sabotage row is reachable in the first
build; plant 1's witnesses are all VM, so its row is UNREACHED there (§E.4).

Reproduction: `twin/CLAUDE.md` (one command per result file, including revision 1's
`sizes.tsv` and `one_tu_probe.txt`, chk S11).

### E.3 Gates

- **G1 corpus** `tests/compound/split.rxt` (own CLAUDE.md), oracle-first against libpcre2
  10.46: the twin's case list, the panel witnesses, the atomic/possessive witnesses, the
  interior-`$` and tie cells, a utf8 block under every option arm, `mc` find-all throughout.
- **G2 differential**: §E.2, promoted (compound vs `pcrec-harness --harness=no-compound` vs
  libpcre2), with ASan and UBSan arms. Per admitted ID: Q stamps `dfa` and `rev-end` (or
  never), and the generated subjects produce ≥ 1 match (chk M3).
- **G3 counted work** (`tests/compound/run_linear.sh`, promoting `cost2.py`):
  `T_compound ≤ T_lever + calls` on the named shapes (internal run, trailing run, floor + end,
  floor-only, wrapper), and `T(4k) ≤ 4·T(k) + calls` (linearity by the ratio test; any k, 4k
  pair separates 4× from 16×; k = 1,000 and 4,000 keep the run under a minute). Both bounds
  are derived from the measured excess (one seed byte per Q call), not chosen (chk S8). The
  final-newline shapes use the bound B3's gate states (§B.5); they are RED until B3. G3's
  attempt-count clause is dropped (chk M7): loads already show the wrapper's attempts.
- **G4 export.** A compound's `nm -g` set equals the plain artifact's `nm -g` set for the same
  prefix (the expected set comes from the plain artifact, not from B0's closure, §H of the
  panel); no `<p>__*` symbol is global; no part `rx_info`; the `.h` equals the plain `.h` apart
  from the stamp lines.
- **G5 derivation.** Trace build, every admitted artifact: Q's tree has no `A_GSTART`; every
  surviving `A_BOL(!multiline)` is inside a lookbehind or a group called from one; Q never ⇔
  the floor-only form; no called or referenced group was deleted.
- **G6 landing bar** (chk S10). Bench reach is 0, so EVERY bench artifact is byte-identical
  to main's at B4's parent, apart from the abi digits and the one `<PREFIX>_COMPOUND "none"`
  line ("byte-identical" means exactly this, measured by `emit_sweep.py` with that
  normalization and nothing else). Named at-risk subsets, pinned by ID: the 16 single-class
  floor DFA rows (capability and sentinel `base10num`, `ipv4`, `uuid`,
  `wild-validator-email-owasp`, `winpath` near-miss; syntax `anc-a-uc`, `anc-caret`,
  `anc-g-uc`; utf8 `asr-a-z`, `cls-dot-rep`, `lit-anchored-run`: BOUND `bot`, A1 false) and the
  2 concat-sqli rows (S+F, A5 false).
- **G7 export surface** (`tests/compound/run_symbol_allowlist.sh`, §A.11, new at B4): every
  global of `build/libpcrec.a` outside `lib/pcrec.h`'s declarations is a row of
  `symbol_allowlist.tsv` with a reason; stale rows and empty reasons fail; floors on both
  populations; the planted-global control (CMP-17).
- **The lever fence** (`tests/compound/run_lever_fence.sh`): the grep above, scope widened to
  `tests/`, `scripts/`, `cli/`.
- **The lever arm** (§A.11): answer identity default vs lever over the whole corpus, the
  population floor, the "lever moves nothing else" byte check, made exact: `"forced-off"` iff
  the default build admitted a row (the stamp pair compared artifact by artifact, both
  directions), `"none"` artifacts byte-identical.
- **The B6 give-up differential:** compound vs lever at lowered budgets on every VM-bearing
  candidate; 0 cells where the lever answers and the compound gives up.
- **Long prefix and K79:** `run_longprefix_sweep.sh` at 60 bytes and
  `run_prefix_invariance.sh` over compounds.
- **Short-call cell, scratch tier:** trim and wrapper at n ∈ {0, 1, 2, 8, 64}, compound vs
  lever, interleaved; decides `noinline` on part entries (§A.5). A loss beyond the noise floor
  becomes a K row, not a predicate.
- **D45 compile-CPU row** (§A.12).

### E.4 Sabotage rows

Ids are the manager's (main's highest S-id and the kit's reserved ranges are checked at
allocation). Each row names its witness and its reach.

| row | plant | direction | detector, reach |
|---|---|---|---|
| CMP-1 | Q from `from` (D163's literal text) | answer | `(?>^a\|ab)c` on `"abc"`. **UNREACHED in the first build**: atomic floor arms route the VM (A4). Declared, with the twin's plant 1 as its evidence |
| CMP-2 | `<HAS_G>` emitted 0 on a `\G` pattern | answer | `\Ga$\|b$` at startpos > 0 (DFA, rev-end Q) |
| CMP-3 | the kill skips `A_GSTART` | answer + G5 | `\Gab\|cd`: G+F, **UNREACHED until B5**; in the first build `\G\n\|b$` (G+E) |
| CMP-4 | `split_admits` returns false | efficiency | G3 and the per-ID `"split"` population floor |
| CMP-5 | padding loop dropped | answer | a pruned capture: VM, **UNREACHED until B6**, declared |
| CMP-6 | a part entry left EXPORTED | linkage | G4 |
| CMP-7 | `drop-compound` deleted | refusal set | a lowered-cap variant where the compound overflows and the plain fits |
| CMP-8 | F without its bound | efficiency | G3's K106 cell (128,040,002 vs 3) |
| CMP-9 | the prune drops a live `ALT` arm | answer | G2 on S+E rows |
| CMP-10 | the kill also kills `(?m)^` | answer | `^x\|(?m:^y$)`, find-all |
| CMP-11 | the prologue checks Q's reach | answer | `\A\s+\|\s+\z`, `-e utf8 -futf-check` (DFA P, rev-end Q): the twin's plant 2 fires on it (`\A` raises P's reach, Q has none); `^(?<=é)a\|b` is the VM witness for B6 |
| CMP-12 | parts compiled with the guards on, prologue removed | answer | `a{0,4}\A`, utf8, `-futf-check`, from 1/2 (floor-only, DFA): the `-7`/`-9` refusals vanish |
| CMP-13 | the align arm passes the raw `from` to F | answer | `(?>\Ga\|ab)c`: VM, **UNREACHED**; DFA witness `\Ga$\|b$` under `-fstartpos-guard=align` |
| CMP-14 | the prune deletes a called group | answer / decline | `(?:^(a)\|b)(?1)`: VM; in the first build the decline reason (A2) is asserted instead |
| CMP-15 | the lever stamps `"none"`, or stamps `"forced-off"` on a `pre_admits` pass that `drop-compound` or the caps would have rejected | lever fence | the lever arm's byte check, both directions; witness for the second plant: a lowered-cap variant where the compound overflows and the plain fits (CMP-7's) |
| CMP-17 | a new unlisted global in the library (an undeclared export, e.g. the lever entry without its allowlist row) | export fence | `run_symbol_allowlist.sh` (§A.11); control: a planted undeclared global |
| CMP-16 | `__` prefix refusal removed | refusal set | `-p a__f` on a compound |

Every decline control records and asserts its reason (chk M5): `^a(*COMMIT)b|c` (A3),
`(?<=^a)b|c$` (A2, nothing killed), `^x|\n(?m)^b$` (A2), `(?<=\G)a|b$` (A2, unkillable `\G`),
`^(\s*)\{|\}(\s*)$` (A4, VM), `^a$` (A1), concat-sqli (A5). A2's "nothing killed" is read by an
independent walk of Q's tree, not by the derivation's own counter.

### E.5 The re-pin and re-aim list: a grep by NAME (chk M6)

Run at B4 on the branch. The new stamp and the new route value move every reader of the stamp
family, so the grep is by macro and field NAME, not by route value:

```
# abi readers (D94): the current number is READ from PCREC_ARTIFACT_ABI (src/gen/emit_dfa.c),
# never typed here; the greps below take it as $ABI
ABI=$(sed -n 's/^#define PCREC_ARTIFACT_ABI \([0-9]*\).*/\1/p' src/gen/emit_dfa.c)
grep -rn "PCREC_ARTIFACT_ABI\|abi $ABI\|\.abi = $ABI\|PCREC_RX_ABI_H $ABI" src tests docs/spec scripts docs/dev/history
# readers of the route family by NAME (they meet "compound")
grep -rln '_DFA_SCAN\|_DFA_PREFILTER\|_DFA_START\|_DFA_MATCH' tests scripts docs/spec memfn
grep -rln '\.scan\b\|\.prefilter\b\|search_form\|match_form' tests scripts docs/spec lib/pcrec.h
# every machine-level stamp that gets a compound sentinel (§A.7): one grep per name in the catalogue
grep -o 'define [A-Z]*_[A-Z_]* ' build/sc/any.c | sort -u    # the name list, from an emitted artifact
# byte-count readers (one stamp line moves every artifact)
grep -rln 'EMITTED_BYTES\|VARIANT_PINS\|762[0-9][0-9][0-9]' tests scripts
# corpus census readers for tests/compound/
grep -rln 'CENSUS_FILES\|C3_PASS' tests; ls tests/startset/manifests
# fit_rungs[] readers (drop-compound)
grep -rln 'fit_rungs\|run_fallback_table\|listing_declared' tests scripts docs/design/dec_fallback
# re-aims
python3 scripts/sabotage_anchors.py --step <B4 commit>
```

## F. Build plan

| step | what | validation (positive control first) | movers / abi |
|---|---|---|---|
| **B0** | [EMIT-ENTRIES] internal: entry table, dependency edges, `pcrec_entry_linkage` at every definition/declaration site; the hybrid's `"static "` re-expressed through it | a unit check: an internal `{keep: search}` request compiles `-Werror` and leaves exactly the closure, the expected set from the plain artifact's `nm -g`; the hybrid's text byte-identical; emit_sweep 0 movers | zero movers; not abi |
| **B1** | part mode and `CompPart` options (names, `__`, omitted blocks, `PB_ONE_ATTEMPT`, guards-off) | a unit drive: F and Q of 6 witnesses plus a hand controller compile in one TU `-Werror`, long-prefix 60 bytes, K79 invariance; emit_sweep 0 movers | zero movers; not abi |
| **B2** | the derivation hook list and `src/opt/derive.c` (kill, prune, the group-keep rule, the registry attempt-scope column) | `derive` against `twin2.derive` on the twin's case list: two independent implementations, compared by language (the differential), not by text; G5's tree property | zero movers; not abi |
| **B3** | the match-end mark (D164): END_MARK lowering of path-final lookaheads; rev-end walks once | its own panel and gate | its own abi event; movers = every `$`-pinned rev-end artifact |
| **B4** | `src/core/compound.c`: `compound_rows[]` (split, pin-only), the combinators, the prologue, the assembly, `drop-compound`, the harness lever and `build/pcrec-harness` (with `tests/compound/run_symbol_allowlist.sh` + `symbol_allowlist.tsv`, born with the lever's entry, and `run_lever_fence.sh` at its widened scope), `<PREFIX>_COMPOUND` on every artifact, the stamp classification and sentinels, the `__` refusal; G1-G6, the lever arm, CMP rows. Spec: `match_api.md` §1¶2 (`__` reserved), §3¶1, §3.2 (`_match` on a compound), §6 route values `"compound"`, §6.3 the stamp, its three values and the sentinel table; `limits.md` (caps on the assembled text, `drop-compound`); `ir_listing.md`/`facts_listing.md` (the compound listing); `cli.md` (the `__` refusal) | **the abi event**: every artifact by one stamp line; the ~30 admitted by ID; bench 0 (G6) |
| **B5** | S+F/G+F: A5 widened to an unanchored Q under the cost conjunct (§B.7) | its trigger first; then G2/G3 on the new population with matching cells (chk B1's) | the admitted by ID; not abi |
| **B6** | VM parts: budgets, caller buffers, the DEFINE-style group keep | the give-up differential | the admitted by ID |
| **B7** | captures on demand (§D.1) | its trigger; the N-vs-C span gate | the admitted by ID |
| **B8** | §C's hook with [FINDALL-NEXT] at [IFACE-PUSH] | that push's | that push's |

B0-B2 are one lane's no-mover train. B4 waits for B3 so G3 lands green.

## G. Open questions (discussion: problem, forces, leaning)

Only what D163 addendum 2 left open.

**Q1. `--fast-or-fail` when a compound overflows a cap.**
*Problem:* `drop-compound` ships the plain artifact, which is slower than the compound the
selection chose. D135 calls such a rung degrading, and `--fast-or-fail` refuses on a degrading
rung. *Forces:* refusing grows the refusal set under `--fast-or-fail` for a pattern that
compiles today exactly as it always did; shipping it keeps today's behaviour but makes
`--fast-or-fail` silently accept a fallback. The population is tiny (pin-only compounds are
today plus one small end-pinned machine; none in the corpus is near a cap). *Leaning:* treat
it as degrading (`fof = IN`), the same as `drop-anchored`, because the rule should not depend on
which rung it is; record the population (expected 0) at B4.

**Q2. Reserving `__` in user prefixes.**
*Problem:* part names are `<prefix>__<role>`; a user prefix containing `__` can collide inside
one translation unit. *Forces:* the collision needs two artifacts in one TU with prefixes `a`
and `a__f` (it is a compile error, not a silent one); the refusal is a caller-observable change
with population 0 in the tree. Any other naming scheme collides with some legal prefix.
*Leaning:* refuse `__` in a user prefix at B4, with the spec hunk.

**Q3. VM parts: the compound may answer where today gives up.**
*Problem:* with VM parts (B6) a compound can return an answer where the plain artifact gives
up (a fresh budget per part; Q has fewer arms), so the lever arm of test-axes would see cells
where the default answers and the lever gives up. *Forces:* D158 forbids an optimization that
turns an answer into a give-up; this is the other direction, which no ruling forbids, but
test-axes' GIVEUP1 allowances exist for exactly that shape and would need rows derived from
stamps. *Leaning:* accept it; require 0 cells in the forbidden direction (the give-up
differential); derive the lever arm's GIVEUP1 allowance rows from the compound stamp, never by
hand. Not needed before B6.

## H. Unlocks (each with its trigger)

- **U1: re-express the VM hybrid as a compound.** Trigger: a client needs a part interface wider
  than entries (§A.13).
- **U2: dead-path pruning in the default pipeline** (mssurvey's 75 dead-anchor corpus patterns).
  Trigger: a bench cell whose route a dead arm decides.
- **U3: the public [EMIT-ENTRIES] request.** Trigger: [IFACE-PUSH].
- **U4: the floor-only compound generalizes `start_anchor`'s conservative cases.** Trigger: a
  realistic pattern in that class.
- **U5: LS+LE / E+LE rows (4b.2, K106's `(?m)` shapes, K109).** Trigger: their own (a client
  over `(?m)` locators).
- **U6: shared tables between parts** (F and Q share P's byte classes). Trigger: a compound
  whose linked size pushes it to `drop-compound` (D77).
- **U7: nested compounds** (split whose parts are captures-on-demand compounds). Trigger: a
  capture-bearing pin-only pattern in a bench cell.

## I. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime — RELEVANT.** Loads are counted subject loads of a whole find-all
   (ASan kernel-address hooks, no clock), on the Linux dev box (7700X), gcc 15.2; the counts are
   box-independent. Answers are checked against libpcre2 10.46. Only the short-call cell (§E.3)
   is a clock reading, owed as scratch tier at B4; it could change `noinline` on parts, never an
   admission. Sizes are revision 1's (gcc 15.2 `-O2 --gc-sections`).
2. **Independent control — RELEVANT.** Answers: libpcre2 and today's artifact (the lever build
   at B4), neither sharing the compound path. The twin's Q comes from a separate Python parser,
   so B2's derivation is checked against a second implementation by language. Cost: G3 compares
   against the lever on the same subject. Population: per-ID manifests (K35); every sabotage
   witness is reach-proved by the `_COMPOUND` stamp, and UNREACHED rows are declared with their
   step. G4's expected symbol set comes from the plain artifact's `nm -g`.
3. **What moves when data is regenerated — RELEVANT.** No table or calibration is involved. The
   stamp and the route value are B4's abi event (readers by NAME, §E.5; byte-count readers
   re-derived by measurement). `tests/compound/` moves the census pins. B3 moves rev-end
   artifacts as its own event. B0-B2 move nothing.

## J. Findings (for the manager)

1. **J-1. Revision 2's controller holds on the shipped configuration.** Derived DFA Q, bounded
   F, the prologue, six utf8 option arms: 177 case-arms, 2,170,123 cells, 574,769 matches, 0
   differences against today and against libpcre2; three plants fire.
2. **J-2. F must be a BOUND, not `_match`.** A DFA attempt route's `_match` is
   `"search-filter"` (the whole attempt loop, then a filter). As F it is answer-right and
   cost-wrong: K106 stays at 128,040,004 loads and an end match costs 2.00× today. The bounded
   F reads 3 and 1.0001×. The same fact fixes `_match` on a compound (§B.3).
3. **J-3. `(?R)` in Q is sound past the floor.** Q's recursion targets Q's (pruned) root; the
   pruned arms are dead past the floor in P as well, so the targets agree there. Twin:
   `^x|a(?R)?b`, 0 differences.
4. **J-4. Pin-only matching subjects cost today + one load per Q call**, except the
   final-newline two-seed walk (3.00×, two shapes, B3's).
5. **J-5. The first build's bench reach is 0**, so G6 is a whole-bench byte check, with 16
   single-class floor rows and 2 concat-sqli rows as the named at-risk subset.
6. **J-6. A user prefix containing `__` can collide with a part name inside one TU** (§G Q2).
