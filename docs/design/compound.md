# [COMPOUND] — the compound artifact as a general tool; first client [MATCH-SPLIT] (DESIGN NOTE, REVISION 2.2)

**Revision 2.2** (lane `cprev22`, 2026-10-12, from main `e1b73605e`): ready for the B4 (driver)
brief. Text only; no `src/`, the design of revision 2 is unchanged. It applies, in order: the
alignment note's MUST-before-B4 items (`compound_callout_alignment.md` §14.1) and its soft
items (§14.3); D163 addenda 4-6; the as-built B0-B2 (`../dev/lanes/cpb02_report.md`, merged
`2a54c3e71`); and the manager's lean on the lever's fence (§A.11). §R2.2 maps each item to the
place it is addressed. Where this revision and an older revision's text disagree, this
revision wins; §F is the build state.


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

Rulings read: D163 with addenda 1-6, D164 with addenda 1-5, D88 addendum 1, D156 (and `locate_finish.md` rev 2.1,
its typed vocabulary), D158, D135, D76/D94, D80, D104, D144 addendum 4, D155 addenda 4/4.1.
Plan rows: [COMPOUND], [MATCH-SPLIT], [EMIT-ENTRIES], [FINDALL-NEXT], [OPT-ATTEMPT-SPLIT],
[OPT-REVEND] (B3 = the match-end mark, D164), [ADAPTIVE-ARM], [V-E], [IFACE-PUSH].

Read §0 first. §A is the tool, §B the first client, §C the cross-call hook, §D the clients
(captures on demand first), §E the checks, §F the build plan, §G the open questions, §H the
unlocks, §I the standing questions, §J the findings.

## §R2.2. Revision 2.2 (lane `cprev22`, 2026-10-12): for the B4 brief, item → section

| item | source | where | what changed |
|---|---|---|---|
| **MUST-1** call-site codes | alignment §14.1 item 1, §5.2; D163 add. 6 Q3 | NEW §A.14; §A.2 table; §B.2 sketch; §B.3; §E.4 CMP-12, CMP-18; §F B4 | ONE call-site code table shared by parts and callouts, rows only for codes the callee can return. B4 emits rows 1, 2 and 8 (a dead trap under each part call). `first-nonzero`'s "final" is restated as the table's propagate rows. `PCREC_ERR_INTERNAL` PROPAGATES. The `match_api.md` §4¶10 spec hunk lands in B4's commit. |
| **MUST-2** `groups` | alignment §14.1 item 2, §6.3-§6.4; D163 add. 3 | §A.1 (`CompPart`, `CompGroups`, split table, the self-check, the coverage check); §B.2 (the pad rule is read off the map); §D.1 | `CompPart` gains `groups`. Identity for split's F and Q. The pad rule and a slot-coverage table check are read off it. |
| **MUST-3** namespace table | alignment §14.1 item 3, §8.3 | §A.5; §G Q2; §E.4 CMP-16; §F B4 | The `__` refusal is row 1 of the namespace reservation table, not a standalone check; the lever's reserved prefix is row 3. |
| text-only | alignment §14.1 end | §A.2 (a `verify-at`-typed external callee type-checks), §A.9 (INTERIM, now ruled), §B.8 (A3's callout clause conservative pending Q2), §C (the owned region), §A.7 (the link-level kind) | no mechanism changes |
| soft | alignment §14.3 | §A.5 and §F B4 (`PB_ONE_ATTEMPT` as a general emission option: as built it still reads `pcrec_is_part`); §B.8 and §F B4 (`RF_CROSSES_ATTEMPTS` wording) | B4 / B1-follow-up work, each with its check |
| add. 4 (a) | D163 add. 4 | §A.2: the in-Job-vs-part rule as a first-match table `compound_place[]` with listed conjuncts | the two bullets become rows |
| add. 4 (b) | D163 add. 4 | §A.1 (`CompRow` carries a LIST of conjuncts, not two opaque function pointers), §A.3, §B.4 (A1-A6 are the rows' data), §E.4 (decline controls assert the first failing conjunct by NAME) | each row's admission is listed conjuncts the listing can show |
| add. 4 (run-time) | D163 add. 4 | §A.2 | `select-by-arg` and `dispatch` become emitted run-time first-match row lists when their first client is built |
| add. 4 (order) | D163 add. 4; D164 add. 5 | §0 items 7-8 and 11, §B.5, §E.3 G3, §F, §J-4 | B4 no longer waits for B3. G3's two final-newline cells are gated at TODAY's rev-end cost and tighten in B3's own commit (a named obligation of that commit); B3 is now being built (D164 add. 5). |
| add. 5/6 Q1 | D163 add. 6 | §A.9, §G Q3 | one meter per EXPORTED call (agreed): the "fresh budget per part" asymmetry is gone |
| add. 5/6 Q2 | D163 add. 6 | §B.8, §D | callout purity "for now"; A3's callout clause stays conservative until module `callouts` builds (population 0) |
| add. 5/6 Q3 | D163 add. 6 | §A.14 row 4 | `PCREC_ERR_INTERNAL` from a callee propagates instead of trapping |
| cpb02 f.1 | cpb02 report finding 1 | §A.4 | a `rev-end` tie finished `verify-at` makes `<p>_search` call `<p>_match`: Q, whose route is `rev-end` by A5, needs `<p>__q_match` KEPT STATIC |
| cpb02 f.2 | finding 2 | §E.4 (the decline list), §E.2 | the A2 decline controls are re-derived from the as-built derivation; `^x\|\n(?m)^b$` is withdrawn as a decline |
| cpb02 f.3 | finding 3 | §B.1 | F's emitted bound text is cosmetic; a B4 abi event could reword it |
| cpb02 f.4 | finding 4 | §B.8, §E.4 | the attempt-scope column is on the callout row only; the verbs are refused at parse |
| cpb02 f.5 | finding 5 (B0's limits) | §A.4 | a request must reach `_search`; `info` and `main` cannot be kept static; `need`'s `VALID_UPTO` is the controller's edge |
| lever fence | §A.11's manager note (2026-10-12, at merge) | §A.11, §E.3 G7, §E.4 CMP-17, §F B4 | the B4 brief's choice: a reserved unique prefix plus one global check plus the widened grep, in place of the ~560-row symbol allowlist |
| §F | cpb02 report; D163 add. 4 | §F | B0-B2 DONE (merged `2a54c3e71`); B3 is D164's own build, not a compound step |
| bit 55 | D164 add. 5 | §0 item 2, §A.11 | the "bit 55 stays free" sentence is stale (bit 55 went to the kit, bit 56 to B3); the compound still takes no bit |

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
2. **Always on, no deny axis** (D163 add. 2 item 2). There is no flags bit (none is reserved:
   revision 2's "bit 55 stays free" is stale, bit 55 went to the kit and bit 56 to B3, D164
   add. 5), no `-f` spelling, no `--list-axes` row and no `tuning.md` section. The plain artifact is compiled anyway (it
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
   (§B.1). The controller is `first-nonzero(F at f, Q from next_pos(f))` (§B.2), and each part call's
   result is handled by the ONE call-site code table (§A.14).
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
   and B3's (the match-end mark, D164). **B4 does not wait for B3** (D163 add. 4): G3 gates
   those two cells at TODAY's rev-end cost (the compound no worse than the plain artifact's
   rev-end on the same subject) and tightens them to B3's bound in B3's own commit, a named
   obligation of that commit. B3 is being built now (D164 add. 5).
9. **Stamps.** `<PREFIX>_COMPOUND` on every artifact (`"none"`, a row name, or
   `"forced-off"`). Every stamp is classified pattern-level (P's) or machine-level (the
   compound's defined value: `"compound"` for the route family; per-stamp sentinels for the
   rest), and the parts keep their own machine-level stamps under part prefixes (§A.7).
10. **Captures on demand is a named client** (§D.1): `select-by-arg(caps == NULL →
    a `--no-captures` part; otherwise P's VM part)`, triggered by the persisting caps/nocaps
    class gap (D119 ledgers: `auto-nocaps` carried 65 of cycle 1's 91 win/tie rows).
11. **Build (§F):** B0 EMIT-ENTRIES internal, B1 part mode and options and B2 derivation
    are DONE (lane `cpb02`, merged `2a54c3e71`, zero movers). B3 (the match-end mark) is
    D164's own build, not a compound step. Next: B4 the compound driver, split pin-only, the
    stamp (THE abi event) → B5 S+F on its trigger → B6 VM parts → B7 captures on demand on
    its trigger → B8 the cross-call hook with [FINDALL-NEXT].
12. **The compound and callouts are cousins** (D163 add. 5/6, `compound_callout_alignment.md`):
    ONE call-site code table for parts and callouts (§A.14), `CompPart.groups` (§A.1), the
    namespace reservation table (§A.5), one meter per exported call (§A.9), the owner-tagged
    cache region (§C), the link-level stamp kind (§A.7).
13. **Admission and placement are tables with listed conjuncts** (D163 add. 4): `compound_place[]`
    (§A.2) says where a second machine lives (an in-Job row or a compound part), and each
    row's admission is a LIST of named conjuncts (§A.1, §B.4) the listing shows.

## A. The tool

### A.1 What a client declares

```c
typedef struct {
    const char *role;          /* 1-3 chars: part prefix <prefix>__<role>             */
    const PcrecDerive *derive; /* &pcrec_derive_none, or a derivation (NULL = unstated) */
    uint64_t flags_set;        /* pcrec_options flags forced ON for this part          */
    uint64_t flags_clear;      /* ... forced OFF (e.g. the guards, the utf check)     */
    PcrecEngine engine;        /* AUTO, DFA or VM: stated, never inherited silently   */
    PcrecPartBound bound;      /* PB_NONE, or PB_ONE_ATTEMPT (start_max = search_from) */
    unsigned need;             /* PART_NEED_*: what the part must deliver (see below) */
    CompGroups groups;         /* the group map into the compound's ONE captures array */
} CompPart;

typedef struct {               /* D163 add. 3; alignment note §6.3 point 1               */
    CompGroupsKind kind;       /* CG_UNSTATED = 0 (never a default), CG_IDENTITY,        */
                               /* CG_OFFSET, CG_TABLE                                    */
    unsigned offset;           /* CG_OFFSET: caller slot = callee group + offset         */
    const CompSlotMap *writes; /* CG_TABLE: callee group -> caller slot                  */
    const CompSlotMap *reads;  /* CG_TABLE: caller slot -> callee group; NULL = reads none */
} CompGroups;

typedef struct {               /* one LISTED conjunct of a row's admission (D163 add. 4) */
    const char *id;            /* "A1".."A6": stable; printed by the listing, asserted   */
                               /* by the decline controls (§E.4)                         */
    const char *name;          /* the words the listing shows                            */
    CompPhase phase;           /* CC_PRE: plain selections + derivation only             */
                               /* CC_POST: after the parts' own compiles                 */
    bool (*holds)(const CompIn *in);
    const CandRead *reads; int nreads;      /* declared projection reads (§A.3)      */
} CompConj;

typedef struct {
    const char *name;          /* stamped <PREFIX>_COMPOUND "<name>"                    */
    const CompConj *conj; int nconj;        /* ADMISSION: all must hold, in table order */
    const CompPart *parts; int nparts;
    const CompExpr *controller;             /* a combinator expression (§A.2)        */
    unsigned state_words;                   /* §C; 0 until [FINDALL-NEXT]            */
} CompRow;

static const CompRow compound_rows[] = {
    { "split", split_conj, 5, split_parts, 2, &split_ctrl, 0 },
    /* later clients, each behind its own trigger (§D) */
};
```

**Admission is a LIST, not two function pointers** (D163 add. 4 (b); revision 2's
`pre_admits`/`admits` were opaque). A row admits iff every conjunct holds. The walk runs the
`CC_PRE` conjuncts, then compiles the parts, then runs the `CC_POST` ones, each in table
order; the FIRST conjunct that fails ends the row and is recorded by `id` (the trace record,
and the compound's listing in `--emit-ir`/`--emit-facts` shows the row, each conjunct's
`id`, `name`, phase and verdict, and the first failure). The conjuncts' `reads` are the
declared projection reads of §A.3, one set per conjunct, so a reader of the listing can say
which fact a decline turned on. §B.4's table IS split's `split_conj[]`: its rows A1-A5 are
the data (A1-A3 are `CC_PRE`, A4-A5 `CC_POST`). A6, "the assembled text fits the caps", is
not a conjunct of the list: it is `drop-compound`, a row of T1 (`fit_rungs[]`, §A.8) that is
evaluated after assembly, and it is listed in §B.4 for completeness.

**No silent default (arch M3, memory `pcrec-no-silent-defaults`).** Every `CompPart` states all
eight fields; a table-build self-check refuses a part whose `engine` is the zero value, whose
`groups.kind` is `CG_UNSTATED`, or whose `flags_set & flags_clear` is non-zero, and a row whose
`conj` is empty, whose conjunct ids repeat, or that lists a `CC_PRE` conjunct after a
`CC_POST` one (the walk runs them in that order, so the table must state it). A part's options are P's options with `flags_set` OR-ed
in and `flags_clear` masked out. Nothing else is inherited by accident: `tune`, `analysis`,
`features`, `encoding` and every cap are P's by the stated rule "parts compile under P's
options except the named flags", which is a rule written once, not a default per field.

**`groups`: one captures array, a column not prose** (D163 add. 3; alignment §14.1 item 2).
Every part works on the compound's single captures array in the PARENT pattern's numbering.
`groups` is the part's map into it: `CG_IDENTITY` for a part derived from the parent (callee
group `g` is caller slot `g`), an offset or a table for a standalone sub-pattern part (client
7, at its trigger). Two things are read off it instead of being written beside it:
(1) **the pad rule**: the slots the map names and the part does not write. For split, Q's
pruned tree writes fewer groups than P when `<P>__Q_NCAPS < <P>_NCAPS`, and the controller
pads exactly those slots (§B.2); the rule is a function of the map and the part's own
`NCAPS`, never a hand-written condition; (2) **the slot-coverage check**, a table-build
check: every caller slot `1..ncaps-1` is written by some part on every success path the
combinator can take. For split, F covers all of them (it is P) and Q plus the padding covers
all of them. On a DFA-only build `ncaps == 1` and the check is trivial, but the field is
there so B6's VM parts and client 7 do not re-touch every row.

**`need`** is what the controller reads from the part, so the closure (§A.4) can be computed:
`PART_NEED_SEARCH` (the search entry), `PART_NEED_MATCH_CAPS`, `PART_NEED_NEXT_POS`,
`PART_NEED_VALID_UPTO` (the prologue's reach check reads P's, so this is the F part's when F
is P under a bound). It replaces revision 1's undefined `need`.

**For split**:

| part | role | derive | flags_set | flags_clear | engine | bound | need | groups |
|---|---|---|---|---|---|---|---|---|
| F | `f` | none | `PCREC_NO_STARTPOS_GUARD` | `PCREC_FORCE_UTF_CHECK`, `PCREC_FORCE_STARTPOS_ALIGN` | DFA | `PB_ONE_ATTEMPT` | SEARCH, NEXT_POS, VALID_UPTO | `CG_IDENTITY` |
| Q | `q` | `derive_split_q` | `PCREC_NO_STARTPOS_GUARD` | `PCREC_FORCE_UTF_CHECK`, `PCREC_FORCE_STARTPOS_ALIGN` | DFA | `PB_NONE` | SEARCH | `CG_IDENTITY` |

As built (B1, lane `cpb02`) `CompPart` has the first seven fields, every one stated and
checked by `pcrec_comp_part_check`; `groups`, `CompConj` and the `conj` list are B4's, its
first commit (they touch no emitted byte).

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
| `first-nonzero(A@x, B@LOWER(g(x)))` | ask A at `x` and handle its return by the call-site code table (§A.14): a `SPAN` (row 1) is final; on `NOMATCH` (row 2) relocate to `LOWER = g(x)` and ask B there (FINISH `search-from`); a give-up, `INTERNAL`, `UTF` or `UNSET_VAR` (rows 3, 4, 5, 7) PROPAGATES unchanged; `STARTPOS` and any other negative (rows 6, 8) trap | split: `F@f`, then `Q@next_pos(f)` |
| `min-start-then-finish(L1..Lk; V)` | each locator hands `SPAN`/`LOWER`; take the minimum start; FINISH `verify-at` with V there; the losers' results are §C's cache | 4c, per-branch locators (§D.3) |
| `locate-then-finish(L; V)` | L hands an exact `SPAN`; V `verify-at` the start with a ceiling (the hybrid's shape, across parts) | DFA locate + VM finish (§D.2) |
| `select-by-arg(p; A, B)` | a predicate on the CALL's arguments picks the whole sub-expression | captures on demand (§D.1) |
| `dispatch(level; A1..Ak)` | a run-time CPU level picks the part | arch variants (§D.5) |

**Type check at table build.** Each combinator states the result types it accepts and hands;
each part's entry states what it hands (from its `need` and `bound`). A row whose expression
does not type-check is a table-build error, the same check `locate_finish.md` §2.3 makes for
FINISH totality. The check accepts a callee that is NOT a part of this artifact when it is
typed: an external callee of type `verify-at` (a pcrec-compiled or caller-bound matcher with
the `rx_matchfn` shape) type-checks as the finisher of `locate-then-finish(Q; external
verifier)`, because a callout and a part are one thing at two binding times (alignment §4,
unlock U6). No client uses it yet; the clause costs the check one more admitted callee kind,
so a later client does not re-open the combinator type system.

**Run-time selectors are emitted first-match row lists** (D163 add. 4). `select-by-arg` and
`dispatch` are the two combinators whose choice is made when the call is made, not when the
compound is built. Each, when its FIRST client is built (§D.1, §D.5), emits its choice as a
run-time first-match list of (predicate, part) rows, in the table kit's shape (rows as data,
a last row, a reach witness per row), not as an `if`-chain written by the emitter. Nothing is
built for them in B4 (no client uses them); the rule is stated now so the first client does
not write a second style.

**In-Job LOCATE row or compound part? (arch M2's question; a first-match table by D163
add. 4 (a)).** A part is the unchanged pipeline on a derived input; an in-Job row is a
selection inside one machine. The rule is the table `compound_place[]`, a house table (C1
trace site key `compound-place`, a `TABLE_ROOTS` root, a reach witness per row). The
table-build self-check asks it of every part of every `compound_rows[]` row: a part must
land on row 1 or 2, and a part that lands on row 3 is an in-Job row mis-placed as a part
(a table-build error). Review asks it of every in-Job candidate. It sits beside the start
table in the kit sense (same checks, the same trace); its source file is B4's brief's to
place. The first passing row decides; the last row has no conjunct beyond "none of the
above".

| # | row | conjuncts (all must hold) | placement |
|---|---|---|---|
| 1 | `different-tree` | the second machine's tree is not P's tree under erasure (a derivation other than `pcrec_derive_none`: split's Q, 4c's per-class searches) | compound PART |
| 2 | `different-options` | the second machine's options differ from P's beyond what erasure itself sets (`flags_set`/`flags_clear` non-zero, or `engine` other than P's selection: captures on demand, [ADAPTIVE-ARM], arch levels) | compound PART |
| 3 | `erasure-only` | (no conjunct beyond rows 1-2 failing) P's tree under ERASURE only, P's options (D31): the hybrid's prefilter, `rev-end`, a FINISH `verify-at` | in-Job row (a `cand_rows[]` LOCATE or FINISH row) |

K108's case (a nullable pattern whose hybrid prefilter is declined though a full exact search
would be linear) lands on row 3, so it is better as an in-Job change, lifting the nullable
decline when the locator is exact (`locate_finish.md` §4), than as client §D.2. Row 3's
placement is the same conclusion revision 2's second bullet reached, now a row a reviewer can
point at; the rows are the two bullets, nothing new is ruled.

### A.3 The driver: `compound_rows[]` at the driver tier

The table lives in a new `src/core/compound.c`, the driver tier beside `compile_driver`.

1. **The plain compile runs first, exactly as today.** It is the fallback (the refusal set
   cannot grow, except under §G Q1's `--fast-or-fail` question) and the admission's input.
2. **The walk.** For each row, the `CC_PRE` conjuncts run first. Each reads the plain
   compile's selections through its own declared reads (arch S5): `CandRead { slot, route }`
   pairs answered by a projection function `cand_plain_selection(job, slot, route)`. In the
   trace build every read a conjunct makes is held to ITS declared set, the check
   `CandNode.reads` already has (`[cand-no-name-strcmp]`'s machinery). The row's derivations
   (cheap tree passes) run with them, because A2 reads the derivation's report. If they all
   pass, the parts compile (each through `compile_driver` with part mode, §A.5), then the
   `CC_POST` conjuncts read the parts' own selections (A4 and A5 for split). The first
   conjunct that fails is the decline reason, by `id`.
3. **A part's own failure declines the row** (refusal, cap overflow, a degraded ladder rung:
   chk S12). The walk continues; if no row succeeds, the plain output ships.
4. **The choice is attempt-level state** (arch M4). The current `compound_rows[]` selection is
   a field of the attempt loop's state in `compile_driver`, and T1 (`fit_rungs[]`) can retry
   with it cleared (§A.8). There is no second ladder.
5. **Assemble** (§A.5), then check the caps on the assembled text (`drop-compound`, §A.8,
   which is split's A6).

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

**As built (B0, lane `cpb02`, `src/gen/entries.c`).** The entry table has public rows plus
the internal ones (the VM's three `_run` bodies, the hybrid's embedded search), a per-shape
edge table, the closure, and `pcrec_entry_linkage`/`_storage`/`_emitted` at every definition
and declaration site (the `.h`, the self-contained `.c`, the header-form `.c`'s static forward
declarations, the `src/enc/` residuals through new drop/static masks). The request is the
driver-tier `PcrecEmitIn`, the new last parameter of `compile_driver`; NULL is the default
request, today's linkage. Two things B0 found that B4 inherits:

- **A `search -> match` edge on a `rev-end` tie** (cpb02 finding 1). A `rev-end` locator whose
  tie arm is finished `verify-at` makes `<p>_search` call `<p>_match` (the edge shape
  `search_match`). The check found it as a missing edge (a hand list had omitted it). It
  matters here because §B.4's A5 makes Q's route `rev-end`: Q's `<p>__q_search` reaches
  `<p>__q_match`, so **`<p>__q_match` is KEPT STATIC by the closure whenever Q's tie finish is
  built, and OMITTED when it is not**; it is never exported (G4 still holds: no `<p>__*`
  global). The controller's edge list below is therefore only the CONTROLLER's edges; a part's
  own shape edges come from the entry table, never from a split-specific list. Both failing
  directions were seen live in B0: a missing edge and an over-wide one (vars on byte).
- **B0's limits** (cpb02 finding 5; internal errors by D77, not refusals): a request must
  reach `_search`; `info` and `main` cannot be kept static; and `need`'s `VALID_UPTO` is the
  controller's edge, because the part-mode unit drive drops `_valid_upto` without
  `-futf-check`. The prologue's reach check (§A.6) is what keeps it, so the edge
  `<p>_search → <p>__f_valid_upto` is emitted under `-futf-check` only.

**The hybrid is the first customer.** `emit_vm.c:12761`'s
`pcrec_emit_dfa_engine(cx, prefn, "static ")` hard-codes "this embedded engine's search is
static". At B0 it becomes a request through `pcrec_entry_linkage`: the hybrid's VM search
entry has an edge to the embedded DFA search, which is therefore KEPT STATIC by the closure.
Its text is byte-identical (zero movers), which is B0's positive control that the closure
reproduces a shipped linkage decision. DONE in B0 (merged `2a54c3e71`): the hybrid's `"static "`
is now its closure answer.

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
  **The refusal is ROW 1 of the namespace reservation table, not a standalone check**
  (alignment §8.3, §14.1 item 3): one first-match row list, owned by `valid_prefix`'s module
  (`src/core/compile.c`) and listed in `cli.md` beside `-p`'s grammar, with a row per reserved
  name family so the next reservation adds a row rather than a second refusal:

  | row | reserved form | refused user prefix | first enforced |
  |---|---|---|---|
  | 1 `parts` | `<prefix>__<role>_*` | any prefix containing `__` | **B4** (§G Q2) |
  | 2 `callout-bindings` | `rx_callout_<name>` | a prefix equal to `rx_callout`, or starting with `rx_callout_` | [M4-CALLOUTS] step 2 (added by that step as a data row; population 0 in the tree) |
  | 3 `harness-lever` | the lever's reserved prefix (§A.11) | a prefix starting with it | **B4** (the narrower fence is the B4 brief's choice, §A.11) |

  B4 lands the table with rows 1 and 3. Each enforced row has its sabotage row (CMP-16 for row
  1, §E.4) and a reach witness (a refused `-p`).
- **The shared blocks** (ABI block, includes, `PCREC_FEATURE_SET`/`_MODULES`) are omitted
  from a part; the compound header has them once.
- **No `rx_info`, no `main`** in a part. The part keeps its stamp family under its prefix.
- **The bound.** `PB_ONE_ATTEMPT` makes the part's BOUND slot select `attempt-gstart`'s
  payload (`start_max = search_from`) whatever P's own BOUND would be. It is a part option
  read by the start table as a fact deny on the other BOUND rows, not a tree edit (§B.1).
  As built (B1): the BOUND row `attempt-gstart` takes it and the `bot` row is denied; a
  part whose route is not the DFA attempt route refuses (so the row declines).
  **Soft item, B4's lane, before the controller (alignment §14.3, §10.3, unlock U1):** the
  option is built as a general EMISSION option, and as built it is not yet: the start table
  reads it through `pcrec_part_one_attempt(cx)`, which is `pcrec_is_part(cx) &&
  part_bound == PCREC_PB_ONE_ATTEMPT`, a part-mode-only coupling. Any artifact's `_match` on
  a DFA attempt route is `"search-filter"` (the whole attempt loop, then a filter; J-2), and
  the cure for every such artifact, including a plain artifact bound as a callout, is the
  same bounded attempt. So B4 moves the option's carrier from the part-mode test to the
  emission request (`PcrecEmitIn`, B0's request), with part mode as its FIRST reader. Check:
  after the move `pcrec_part_one_attempt` (or its successor) reads the request's bound field
  and nothing about part mode, and a non-part drive that sets the request's bound compiles
  and passes the bounded-attempt answer cases. Selecting it for a plain artifact's `_match` is U1, a selection row filed
  for its own trigger, not B4.
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

**A third kind: link-level** (alignment §10.1, D163 add. 5). What the artifact NEEDS from its
link: the `rx_callout_<name>` symbols it references, which a loader ([ART-MGR]) or a composing
build wants as a list without parsing C. Parts never appear in it (parts are inside the
file, D88 add. 1). A compound's link-level set is the union over its parts. Today it is
always empty, because callouts are unbuilt and A3 declines them (§B.8). **No B4 change**:
`<PREFIX>_COMPOUND` and the sentinels stand as designed; when callouts build, `rx_info` gains
the callout-name list and this table gains the link-level row.

**The sentinel table.** D156 addendum 2's generated-stamp rule (`locate_finish.md` L2.1)
already gives every machine-level stamp an off-path value. A compound is one more cell in that
generator: each machine-level stamp's catalogue row gains a `compound` value (`"compound"`
for the string route family; for the others the value the generator already uses for "not on
this path", stated per stamp in `match_api.md` §6.3). No reader infers a fact from absence
(`RX_REQ_HANDOFF` Q3 (a)'s rule). The full table is B4's spec hunk; its readers are found by
macro NAME (§E.5).

**The policy stamp.** `<PREFIX>_COMPOUND` on every artifact: `"none"` (no row admitted),
the row name (`"split"`), or `"forced-off"` (the harness lever was set and the default build would have shipped a row
name, §A.11; never merely because the `CC_PRE` conjuncts passed). It is pattern-level.

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

### A.9 Budgets under D158 (sem notes; D163 add. 6 Q1)

**One meter per EXPORTED call** (D163 add. 6 Q1, agreed; alignment §7.3). Every part of a
compound, and every pcrec-matcher callee, charges the caller's one meter. Parts are static,
so the meter pointer is internal text; with no session (an un-suffixed entry, today's
callers) the exported entry allocates the meter on its own frame, which is a plain artifact's
behaviour today. Revision 2's "each part entry initializes its own budget" was marked INTERIM
by the alignment note and is replaced; the decision was due before B6 and is made.

- **DFA parts have no budget** (the first build, B4). Nothing to show; the sentence is the
  rule for B6.
- **VM parts (B6): D158 gets one comparison unit.** A compound's charge and the plain
  artifact's are in the same unit (one meter, one call), so the give-up differential compares
  like with like. The give-up surface is still NOT a subset in either direction (engine
  choices are not monotone in the tree; Q is P minus dead arms; the bounded F may cost a step
  more at the floor). What the compound guarantees: on every subject and call, a non-give-up
  answer of the compound equals P's answer; a part's give-up is returned at once
  (`first-nonzero` treats it as final: §A.14 row 3). B6's gate is the give-up differential: 0
  cells where the plain artifact answers and the compound gives up (§E.3). One meter makes
  that gate stricter than "fresh per part" would have: a compound can now give up where the
  fresh-per-part form would have answered, which is exactly the question the differential
  asks, so B6's gate decides it, never a multiplier. §G Q3 is restated against the one meter.
- **The tiered default (§4¶4, x2) is unaffected.** It re-runs the whole exported call, so it
  is a second exported-call meter, as today.
- **Caller buffers (VM parts).** Sequential parts share one region sized by the max over parts
  (the parts run one after another); the controller builds each part's descriptor per call. A
  spec gap belongs to B6: a compound's public `<p>_buffers` counts frames of ONE frame type,
  and parts can have different frame sizes (24 versus 40 bytes), so the compound's frame unit
  is defined as the largest part frame with the controller converting counts per part. That
  is a B6 spec hunk.

### A.10 Where it lives; the table kit (arch S3)

- **Files.** `src/core/compound.c` (`compound_rows[]`, the driver, the assembler, the
  combinator emitters), `src/opt/derive.c` (derivations), part mode and
  `pcrec_entry_linkage` in `src/gen/`.
- **The table kit**, as every house table has it:
  - the C1 trace site key `compound` (records the row walked, each conjunct's
    verdict by id, the first failing id, the declared reads);
  - a `TABLE_ROOTS` root for `call_graph.py --family compound`;
  - a row-reach witness per row in `tests/compound/`, asserted by stamp;
  - the trace build's declared-read check (§A.3).
- **No `--list-axes` projection**: there is no axis (D163 add. 2 item 2). The table is visible
  through the artifact's `--emit-ir`/`--emit-facts` listing (the row and each part's listing
  under its role; `ir_listing.md`/`facts_listing.md` hunks at B4), which describes what an
  artifact IS, not a switch.

### A.11 Always on: the one harness-only lever (D163 add. 2 item 2)

**There is no public deny.** No flags bit (none is reserved; D164 add. 5 records bit 55 gone to the kit and bit 56 to B3), no `-fno-...`, no
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
  2. **A reserved unique prefix and ONE global check** (the B4 brief's choice, the manager's
     lean at merge 2026-10-12; it replaces revision 2.1's per-symbol export allowlist).
     The lever's entry carries a RESERVED name prefix (`pcrec_harness_`; free at this
     commit, `grep -rn 'pcrec_harness' src lib cli tests scripts Makefile` is empty; the
     spelling is B4's, the properties below are the contract), which passes
     `tests/memfn/run_link_checks.sh` C15 (every global begins `pcrec_`). The checks, all in
     `tests/compound/run_lever_fence.sh` (item 3), a `make test` section:
     (a) `nm -g --defined-only build/libpcrec.a` lists EXACTLY ONE global beginning with the
     prefix, the lever's;
     (b) no header under `lib/` declares a name beginning with it;
     (c) the widened grep of item 3.
     Also a refused user prefix: namespace row 3 (§A.5). Controls: a planted SECOND global
     with the prefix is flagged; a planted declaration of the prefix in a `lib/` header is
     flagged; the lever's entry removed (zero globals with the prefix) is flagged, so the
     lever demonstrably exists; floors on the one-global count (K35). Sabotage row CMP-17
     (§E.4).
     *Why this and not the allowlist.* Revision 2.1's `run_symbol_allowlist.sh` named every
     global of the archive (566, 6 of them public: about 560 hand-reasoned rows). That list
     churns with every internal refactor, because each new helper, and each `static` dropped
     for a cross-TU call, needs a row and a reason, so the population is a by-product of the
     toolchain and says nothing about the lever. The one property the lever needs is that no
     caller can reach it through the shipped contract except by a name nobody advertises, and
     that the archive carries exactly one thing under that name; (a)-(c) check exactly
     that, and a second symbol, a declaration or a prose mention each fails a check, which
     is the same strength for this purpose at the cost of one prefix. What it does NOT do is
     police the rest of the export surface. That is a separate, optional check
     ([EMIT-ENTRIES] will want one when its public request lands, §H U3); no row of this note
     depends on it, and it is not part of B4.
  3. **`run_lever_fence.sh`** (described next), with its grep scope widened to `tests/`, `scripts/`
     and `cli/` as well as the prose directories, allowlisting the harness's own legitimate
     uses (the `-DPCREC_HARNESS` object of `cli/main.c`, `build/pcrec-harness`'s callers, the
     lever arm of `tests/axes/run_axes.sh`, the emit_sweep lever arm, `tests/compound/`).
     The grep takes BOTH the option spelling and the prefix.
- **CLI.** `cli/main.c` compiled a second time with `-DPCREC_HARNESS` into
  `build/pcrec-harness`, which accepts one extra option `--harness=no-compound` and calls the
  harness entry. The shipped `build/pcrec` has no such option: in a normal build the word is
  an unknown option. `make` builds both (the second is one more object of `main.c`).
- **The artifact marks itself, exactly when the lever changed it.** The `CC_PRE` conjuncts
  passing is NOT "the default build admitted a row": admission continues through Q's derivation, Q's own
  ladder check (A4/S12) and the assembled text's caps, and `drop-compound` (§A.8) can still
  reject the row after the `CC_PRE` conjuncts passed. Stamping `"forced-off"` on a `CC_PRE` pass
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
(`tests/compound/run_lever_fence.sh`) fails if `--harness=` or the reserved prefix appears
in `docs/spec/`, `docs/guide/`, `README.md`, `examples/`, `lib/`, `tests/`, `scripts/` or
`cli/`, outside an explicit allowlist of the harness's own uses (listed in fence 3 above), and
holds the archive to exactly one global under the prefix (fence 2). The only spec sentence is
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

### A.14 The call-site code table (D163 add. 5/6; alignment §5, MUST before B4)

`match_api.md` §4¶10 binds "a generated call site that invokes another `rx_matchfn` (a
callout, a composed submatcher)" to trap on a code below the floor, and says pcrec emits no
such site today, so the obligation binds the first that does. **B4's controller is that
first site.** A compound part is a composed submatcher, and revision 2's `if (r != 0) return
r;` would have returned `PCREC_ERR_STARTPOS` and `PCREC_ERR_INTERNAL` where §4¶10 traps. The
two sides must agree, and they agree on ONE design for parts and callouts alike (a
compound part and a callout are one thing, a pcrec-compiled callee, at two binding times;
alignment §3).

**A call site's handling of a return is a first-match table over code classes, with rows
emitted only for the codes the CALLEE CAN RETURN**, read from the callee's own facts: its
engine (a DFA never gives up), its guards (a guards-off part never refuses), its
`-futf-check` arm. Every other code reaches the last row.

| # | code class | action | a compile-time part knows | a link-time callout knows |
|---|---|---|---|---|
| 1 | `>= 0` (SPAN) / `1` | the combinator's success edge | yes | yes |
| 2 | NOMATCH (`-1` / `0`) | the combinator's failure edge (relocate, or the outer path fails) | yes | yes |
| 3 | give-up `[PCREC_ERR_FLOOR, -2]` | **propagate** unchanged (D49; D158: final) | only if the part is VM | always (unknown callee) |
| 4 | `PCREC_ERR_INTERNAL` | **propagate** (D163 add. 6 Q3; today §4¶10 traps) | only if the part has a producer (`vm_look_behind`'s negative arm) | always |
| 5 | `PCREC_ERR_UTF` | **propagate** (D133 Q11) | never: parts are `-futf-check`-clear (§A.6) | if the callee checks |
| 6 | `PCREC_ERR_STARTPOS` | **trap**: the caller generated the position, so it is a boundary (§9.5) | never: parts are guards-off | always (a callee's guard is on) |
| 7 | `PCREC_ERR_UNSET_VAR` | **propagate** (the caller's data, as UTF is) | only on a var-bearing part (VM) | always |
| 8 | anything else below the floor | **trap** (the reserved abort space, D38 item 4) | always | always |

- **B4 emits rows 1, 2 and 8.** Its parts are DFA-only (no give-up), guards-off (no
  `STARTPOS`) and check-clear (no `UTF`), so rows 3-7 have no member. Rows 1-2 are the
  combinator's own edges (§A.2), so row 8 is the only new line: `if (r < 0)
  __builtin_trap();` under each part call (§B.2, §B.3). It is dead code by construction.
  G2 cannot reach it; a trace-build assertion records that it is unreached on every
  admitted artifact. **No admitted pattern's answer changes**, since no admitted part can
  return a negative code.
- **Why emit a dead trap at all.** It turns a broken guards-off invariant into a crash
  instead of a silently returned refusal, and it is the line §4¶10 already demands.
  CMP-12's detector gains the trap as its second witness (§E.4).
- **`PCREC_ERR_INTERNAL` propagates** (D163 add. 6 Q3, agreed): row 4 reads propagate, not
  trap. That is a change to §4¶10 from "trap" to "propagate", and the row has no producer on
  a B4 part either way.
- **The table is data, in the table kit** (C1 trace site key `compound-callsite`, a
  `TABLE_ROOTS` root, a reach witness per row, each row's applicability a function of the
  callee's declared facts). B6's VM parts light rows 3, 4 and 7 through the same table
  without a new emitter; the callout module lights all of them with "always" in the last
  column.
- **The spec hunk lands in B4's commit** (D80; B4 is the first producer): `match_api.md`
  §4¶10 becomes this table, the sentence "pcrec emits no such call site today" goes, and the
  compound controller is named as the first producer. Row 7 is also a change: today's line
  traps on `PCREC_ERR_UNSET_VAR`, but variables ride `rx_ctx` from the caller, so an unset
  one is the caller's data, as UTF is. No producer exists either way.
- **Cost.** For compounds, no movers beyond B4's own abi event (the controller text is new
  anyway). For callouts, none (no call site exists). One sabotage row gains a witness
  (CMP-12) and one optional row is new (CMP-18, §E.4).

## B. First client: [MATCH-SPLIT], pin-only

### B.1 The parts

- **F (role `f`) = P under `PB_ONE_ATTEMPT`.** No tree change. The bound makes F's search one
  attempt at `search_from`; P's own `^`, `\A` and `\G` keep their meaning there, and `(?R)`,
  `(?0)` target P's root (sem MF3's blocker is gone: revision 1's `A_CAT(A_GSTART, root)` made
  them re-enter `\G(?:P)`; witness `^x|a(?R)?b` on `"aabb"`). F is compiled guards-off; the
  prologue has already refused or aligned `from` (§A.6).

  In the twin the bound is the emitted line `const size_t start_max = subject_length;`
  rewritten to `= search_from;`, which is what the BOUND row `attempt-gstart` emits. **As
  built** (cpb02 finding 3) the emitted bound reads `start_max = search_from /* fully
  \G-anchored */`: the trailing comment is the row's own payload text, and it is cosmetic
  on a part that is not a `\G` pattern. Rewording it would be an abi event, and the payload
  is shared with every artifact that selects `attempt-gstart`, so it would move those
  artifacts too (a mover set by ID). B4 is the one abi event, so the cost is only the extra
  manifest; the lean is to leave it and file it, and the B4 brief decides. On a P
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
        if (r > 0) return r;                     /* §A.14 row 1: a match is final */
        if (r < 0) __builtin_trap();             /* §A.14 row 8: dead by construction */
        qf = <p>__f_next_pos(s, n, from);        /* row 2, NOMATCH: Q only PAST the floor */
    }
    <Q never: return 0;>
    int r = <p>__q_search(s, n, qf, caps);
    if (r < 0) __builtin_trap();                 /* §A.14 row 8 */
    <on r > 0 only: pad the slots Q's map names and Q does not write, §A.1's `groups`,
     present only when <P>__Q_NCAPS < <P>_NCAPS>
    return r;
}
```

**Each part call is handled by the ONE call-site code table (§A.14).** F and Q are DFA-only,
guards-off and `-futf-check`-clear in the first build, so rows 3-7 have no member and B4 emits
exactly rows 1, 2 and 8. Revision 2's `if (r != 0) return r;` is withdrawn: it would have
returned `PCREC_ERR_STARTPOS` and `PCREC_ERR_INTERNAL` where `match_api.md` §4¶10 requires a
trap (alignment §5.1). The row-8 line is a one-line cold path that turns a broken guards-off
invariant (a part compiled with its guard on by mistake, CMP-12's plant) into a crash
instead of a silently returned refusal. **The pad is read off `groups`** (§A.1) and runs only
on a success (delivery on success: a failing call writes nothing, alignment §6.3 point 3,
which is also what `match_api.md` §3.1¶4's caps-untouched-on-failure rule says). In the
DFA-only build `ncaps == 1`, so the pad has no slot and B4 emits none; the rule is stated for
B6.

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
| `<p>_match`, `<p>_match_caps` | the prologue, then F's bounded search at `pos` (a `SPAN` at `pos` or `NOMATCH`), converted to the match-here return; F's result goes through the same call-site code table (§A.14: rows 1, 2, 8) | 
| `*_in` | the un-suffixed entry with `(void)buffers` (DFA-only compounds) |
| `<p>_next_pos`, `<p>_valid_upto` | the compound's own (the encoding residual, P's reach) |
| `<p>_info` | one (§A.7) |

**Why not F's `_match`.** On a DFA attempt route `_match` is `"search-filter"`: it runs the
whole attempt loop from `pos` and filters by start. F's bounded search runs one attempt, and
its answer is the match-here answer (`match_api.md` §3.2¶1: "matches at exactly `ctx->pos`").
So the compound's `_match` becomes O(attempt) where today's is O(n · attempt) on a failing
probe (revision 1's finding I-5), and it is now stated against the right entry.

### B.4 Admission: the `split` row, pin-only

`split_conj[]` is the row's admission: LISTED conjuncts (§A.1's `CompConj`), a conjunction of
facts read off compiles, each with an id, a name the listing shows, a phase and its declared
reads. No constant is hand-set. A decline is reported by the first failing conjunct's id
(§E.4's decline controls assert it).

| id | phase | conjunct | where read | why |
|---|---|---|---|---|
| A1 | `CC_PRE` | P's plain compile is on an attempt route with BOUND `all` (DFA `attempt[subject_length]`) | the plain compile's BOUND and LOCATE selections (declared reads) | today attempts every start; a fully anchored P is already one attempt and stays byte-identical |
| A2 | `CC_PRE` | the derivation killed ≥ 1 floor anchor and left no `\G`; no called/referenced group was in a pruned arm (first build) | `PcrecDeriveReport` (B2's counts) and an independent walk of Q's tree (chk M5; G5's walk) | §B.1 |
| A3 | `CC_PRE` | no verb or callout in P (registry-keyed, §B.8) | `pcrec_ast_crosses_attempts` (the registry's attempt-scope column on P's nodes) | §B.8 |
| A4 | `CC_POST` | every part compiled on the DFA without a degraded rung (no `size-cap-retry`, no `sel1-*`, no `prefilter-collapse`) | the parts' `ENGINE` and `ENGINE_SEL` | D158 (§A.9), and Q's cap (chk S12) |
| A5 | `CC_POST` | **PIN-ONLY:** Q is never, or Q's LOCATE selects `rev-end` | Q's own compile | chk B1: an end-pinned Q has at most the end matches per subject; an unanchored Q's many-match cost waits for B5 |
| (A6) | after assembly | the assembled text fits the caps | `drop-compound` (§A.8), a row of T1, not a conjunct | D84 |

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
  higher where captures need a forward run. **B4 does not wait for B3** (D163 add. 4): G3
  gates this shape at TODAY's rev-end cost (the compound no worse than Q's own plain rev-end
  artifact on the same subject, §E.3), and B3's commit tightens it to B3's bound, a named
  obligation of that commit.
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
  registry's attempt-scope column (`RF_CROSSES_ATTEMPTS`), read off P's nodes through the SR-8
  node stamping by A3 (`pcrec_ast_crosses_attempts`). **As built (B2, cpb02 finding 4)** the
  column is on the CALLOUT row only (`GROUP_XA`). The four attempt-crossing backtracking
  verbs, `(*COMMIT)`, `(*SKIP)`, `(*PRUNE)`, `(*THEN)`, are `ROADMAP_NEVER` and refused at
  parse, and a verb node has no per-name row today, so no node carries them. Therefore:
  - The witness `^a(*COMMIT)b|c` on `"ac"` (libpcre2: no match; a compound `(1,2)`) cannot
    reach A3 by an artifact: the compile refuses at parse. Its control is the refusal, and A3's
    verb half is **UNREACHED** in the first build, declared (§E.4). The callout half is
    UNREACHED too (module `callouts` is planned; `(?C` refuses "requires module 'callouts'"),
    exercised by B2's unit drive (`tests/compound/compound_drive.c`), which runs
    `pcrec_ast_crosses_attempts` over a node carrying a row with the column and one without.
  - A verb producer, when one lands, stamps its node with a row that states the column per
    name; no list in `derive.c`. A new row states the column and the predicate follows.
- **Wording (alignment §14.3, a soft item for B4's lane).** The column's comment in
  `internal.h` reads "the construct's effect spans attempts or observes their order". The
  alignment note asks for "observes or changes the attempt sequence", with the callout rows
  and the verb rows kept DISTINGUISHABLE (two groups) so a ruling on callouts can relabel
  them without renaming the column. B4 rewords the comment and keeps the callout row's
  `GROUP_XA` apart from the verb group's (comment and flag name only; no byte of any
  artifact moves).
- **The callout clause of A3 is conservative pending Q2** (D163 add. 6 Q2, agreed "for now"):
  with the callout PURITY contract (a callout's return depends only on what `rx_ctx` carries
  for that call; side effects see an unspecified fire sequence, PCRE2's own latitude under
  start optimizations, D36) a callout is as safe for split as for every shipped start
  optimization, and the decline can be lifted for callouts (alignment §10.5, unlock U4).
  **The decline stays until module `callouts` builds** (population 0 either way, so nothing
  moves at B4), at which point the contract is written into the callouts spec. Verbs genuinely
  cross attempts and stay declined.
- **`\K`** forces the VM, so the DFA-only build declines it (A4). The cache (§C) declines with
  `\K` or keys on the attempt start.

## C. The cross-call state hook (D163 item 1; built with [FINDALL-NEXT])

Revision 1's §C stands, with four changes:

- **The cache lives in an OWNED region** (D163 add. 5; alignment §9). With the one `rx_ctx`
  session pointer of [FINDALL-NEXT]/[IFACE-PUSH] threaded through every call, a COMPOUND USED
  AS A CALLOUT would receive the OUTER artifact's session, and its controller would read and
  write its `state_words` cache inside a struct sized and owned by a different artifact: two
  artifacts' caches in one struct, and a "Q result still valid" entry written for another
  machine. That is an answer bug, not only a cost one. So the session has two halves: a
  SHARED half (the meter of §A.9, caller counters) every callee in a chain reads and charges,
  and an OWNED cache region tagged with its owner's identity (`&<p>_info`, the one
  per-artifact address that already exists). A controller uses the cache only when the tag is
  its own; a callee seeing a foreign tag runs stateless. Answers are history-independent
  either way, so ignoring a cache is always sound. `state_words` live in the owned region.
  Cost now: none (part of [IFACE-PUSH]'s `rx_ctx` event and of B8).

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

| part | role | derive | flags_set | flags_clear | engine | bound | need | groups |
|---|---|---|---|---|---|---|---|---|
| N | `n` | none | `PCREC_NO_CAPTURES` | — | AUTO | `PB_NONE` | SEARCH, MATCH | `CG_IDENTITY` (writes no slot: its path has `caps == NULL`) |
| C | `c` | none | — | — | VM (as P) | `PB_NONE` | SEARCH, MATCH_CAPS | `CG_IDENTITY` |

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

**As built (B2, cpb02).** `pcrec_derive_split_q` is compared with `twin2.derive` by LANGUAGE
on the twin's case list (cases2 plus the owed row): 103 compared, 1,149,584 cells, 0
differences; two plants fire (killing `(?m)^` fails 2 cases, a kill that skips `\G` fails 29,
G5's property). The two implementations DISAGREE on which patterns decline, and the
disagreement is the as-built one being right (finding 2): the twin declined `^x|\n(?m)^b$`,
`(?:(?m:^a)|^b)` and a `(?m)` pattern's `\A` as "nothing killed", while the AST derivation
scopes `(?m)` per node, kills the `^x` (sound: the `(?m)` applies to the node it scopes) and
derives. Revision 2's "6 declined with their reason" is therefore the TWIN's count, not the
derivation's. §E.4's decline controls are re-aimed accordingly.

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
  are derived from the measured excess (one seed byte per Q call), not chosen (chk S8).
  **The two final-newline cells** (`\s+$`, `\s*?$`; Q's rev-end double walk, 3.00× against the
  lever in §B.5) **are gated at TODAY's rev-end cost** (D163 add. 4), not left RED: the bound is
  `T_compound ≤ T_Qalone + calls`, where `T_Qalone` is the counted loads of Q's tree compiled
  ALONE as a plain artifact (a rev-end artifact today) on the same subject, i.e. the compound
  is no worse than the plain artifact's rev-end on it. G3 (promoting `cost2.py`) gains that
  one arm. **B3's commit tightens these two cells** to its own bound (D164 add. 1 Q2: `\s+$`
  and the lazy `\s*?$` read 1.00× against the lever through the static `mark_prio` fact; a
  state-dependent shape 2.00×; the number is endmark.md's gate's, not this note's) and
  re-pins them; that tightening is a NAMED OBLIGATION of B3's commit, and B3 is being built
  now (D164 add. 5). G3's attempt-count clause is dropped (chk M7): loads already show the
  wrapper's attempts.
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
- **G7 lever fence** (`tests/compound/run_lever_fence.sh`, §A.11, new at B4): exactly one
  global of `build/libpcrec.a` begins with the lever's reserved prefix; no header under `lib/`
  declares it; the widened grep; the three controls (a planted second global, a planted
  `lib/` declaration, the lever removed); the floor on the one-global count (CMP-17).
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
| CMP-4 | a `CC_POST` conjunct of `split_conj[]` (A5) returns false | efficiency | G3 and the per-ID `"split"` population floor |
| CMP-5 | padding loop dropped | answer | a pruned capture: VM, **UNREACHED until B6**, declared |
| CMP-6 | a part entry left EXPORTED | linkage | G4 |
| CMP-7 | `drop-compound` deleted | refusal set | a lowered-cap variant where the compound overflows and the plain fits |
| CMP-8 | F without its bound | efficiency | G3's K106 cell (128,040,002 vs 3) |
| CMP-9 | the prune drops a live `ALT` arm | answer | G2 on S+E rows |
| CMP-10 | the kill also kills `(?m)^` | answer | `^x\|(?m:^y$)`, find-all |
| CMP-11 | the prologue checks Q's reach | answer | `\A\s+\|\s+\z`, `-e utf8 -futf-check` (DFA P, rev-end Q): the twin's plant 2 fires on it (`\A` raises P's reach, Q has none); `^(?<=é)a\|b` is the VM witness for B6 |
| CMP-12 | parts compiled with the guards on, prologue removed | answer + trap | `a{0,4}\A`, utf8, `-futf-check`, from 1/2 (floor-only, DFA): the `-7`/`-9` refusals vanish. **Second witness (§A.14 row 8):** with a part compiled guards-ON (the plant's first half) the part returns `-7`, and the controller's dead trap under the part call fires, a crash where `if (r != 0) return r` would have silently returned the refusal; the detector must show the trap is hit, not only that the answer moved |
| CMP-13 | the align arm passes the raw `from` to F | answer | `(?>\Ga\|ab)c`: VM, **UNREACHED**; DFA witness `\Ga$\|b$` under `-fstartpos-guard=align` |
| CMP-14 | the prune deletes a called group | answer / decline | `(?:^(a)\|b)(?1)`: VM; in the first build the decline reason (A2) is asserted instead |
| CMP-15 | the lever stamps `"none"`, or stamps `"forced-off"` on a `CC_PRE` pass that `drop-compound` or the caps would have rejected | lever fence | the lever arm's byte check, both directions; witness for the second plant: a lowered-cap variant where the compound overflows and the plain fits (CMP-7's) |
| CMP-17 | a second global under the lever's reserved prefix, or a `lib/` header declaring it (the lever reachable through a second name or the public header) | lever fence | `run_lever_fence.sh` checks (a) and (b) (§A.11); controls: a planted second global, a planted declaration, the lever removed |
| CMP-16 | the namespace table's row 1 (`parts`) removed or its pattern weakened | refusal set | `-p a__f` on a compound; the table's row 3 (`harness-lever`) has its own witness, a refused `-p` starting with the reserved prefix |
| CMP-18 (optional) | the call-site table emits a row the callee cannot return (row 3 for a DFA part) | overreach | a population-0 row: the emitted controller text has no give-up line on a DFA part (a text check, not an answer check) |

Every decline control records and asserts its reason (chk M5), by the FIRST FAILING CONJUNCT'S
ID (§A.1, §B.4: `A1`..`A5`). The list below is **re-aimed on the as-built derivation** (cpb02
finding 2; §E.2): revision 2's list was the twin's, and the twin and `pcrec_derive_split_q`
disagree about which patterns decline, the derivation being right. So **B4 derives its decline
list by RUNNING the as-built derivation and admission over a candidate set and recording each
candidate's first failing conjunct, never by importing the twin's list**; each control below is
then a pattern whose recorded id it asserts.

- `^a(*COMMIT)b|c` (A3): refused at parse, so the control is the refusal, and A3 is
  UNREACHED by an artifact (§B.8); declared.
- `(?<=^a)b|c$` (A2, nothing killed): to be RE-RUN on the derivation; expected to hold (a
  lookbehind-held `^` is not killed).
- `(?<=\G)a|b$` (A2, unkillable `\G`): to be re-run.
- **WITHDRAWN: `^x|\n(?m)^b$` (A2).** The as-built derivation scopes `(?m)` per node, kills
  `^x` and derives it; it does not decline at A2. The same holds for `(?:(?m:^a)|^b)` and for a
  `(?m)` pattern's `\A`, which the twin declined and the derivation derives. They become
  POSITIVE controls for the derivation (they derive, and a later conjunct decides), with the
  language agreement of §E.2 as their answer check.
- `^(\s*)\{|\}(\s*)$` (A4, VM).
- `^a$` (A1).
- concat-sqli (A5).

A2's "nothing killed" is read by an independent walk of Q's tree (G5), not by the derivation's
own counter.

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
# readers of the prefix grammar (the namespace table's rows, §A.5) and the call-site rule (§A.14)
grep -rn 'valid_prefix' src cli tests docs/spec
grep -rn '__builtin_trap\|rx_matchfn' docs/spec src/gen tests
# the bound's part-mode coupling (§A.5) and the attempt-scope column's wording (§B.8)
grep -rn 'pcrec_part_one_attempt\|pcrec_is_part\|RF_CROSSES_ATTEMPTS' src
# the lever's reserved prefix (§A.11): the fence's own population
grep -rn 'pcrec_harness' src lib cli tests scripts Makefile
# re-aims
python3 scripts/sabotage_anchors.py --step <B4 commit>
```

## F. Build plan

State at revision 2.2 (main `e1b73605e`): **B0-B2 are DONE** (lane `cpb02`, merged
`2a54c3e71`, zero movers and no abi event at each step, no spec hunk; the report is
`../dev/lanes/cpb02_report.md`). **B3 is D164's own build, not a compound step** (it is
the match-end mark; it has its own design note, `endmark.md` rev 2, its own panel and gate,
sabotage S881-S890, and D164 add. 5 rules its questions; it is being built now). **B4 no longer
waits for B3** (D163 add. 4): G3's two final-newline cells are gated at today's rev-end cost
and B3's commit tightens them (§E.3).

| step | what | validation (positive control first) | movers / abi |
|---|---|---|---|
| **B0** DONE | [EMIT-ENTRIES] internal (`src/gen/entries.c`): entry table, per-shape edges, closure, `pcrec_entry_linkage` at every definition/declaration site; the hybrid's `"static "` is its closure answer; the request is the driver-tier `PcrecEmitIn` | `check_entries.py`: every 8th distinct corpus pattern x 3 arms x 3 requests, `-Werror` + `nm` against the plain artifact's `nm -g`: 4,854 cells, 0 failures (full corpus once, 37,596, 0); both failing directions seen live; emit_sweep 0 movers | zero movers; not abi |
| **B1** DONE | part mode and `CompPart` (`src/core/compound.c`: names `__<role>`, omitted shared blocks, `PB_ONE_ATTEMPT` on BOUND's `attempt-gstart`, guards-off, K79 per part, the table-build self-check) | a unit drive: 6 witnesses x 5 arms x 2 prefixes (one of 60 bytes) in one TU `-Werror` with a hand controller, run against the plain artifact: 438,462 cells, 0 diffs; the no-prologue plant fails 12 answer cases + 12 builds; emit_sweep 0 movers | zero movers; not abi |
| **B2** DONE | the tree-hook list in `compile_driver` and `src/opt/derive.c` (`pcrec_derive_split_q`: kill, prune, group-keep, G5's independent walk, `PcrecDeriveReport`); `RF_CROSSES_ATTEMPTS` on the callout row + `pcrec_ast_crosses_attempts` | against `twin2.derive` by language: 103 compared, 1,149,584 cells, 0 diffs; plants (kill `(?m)^`: 2 fail; kill skips `\G`: 29 fail); emit_sweep 0 movers | zero movers; not abi |
| B3 (D164's) | the match-end mark: END_MARK lowering of path-final lookaheads; rev-end walks once (`endmark.md` rev 2; `-fno-rev-end-onewalk` is bit 56) | its own panel and gate; **tightens G3's two final-newline cells and re-pins them** | its own abi event; movers = every `$`-pinned rev-end artifact |
| **B4** | `src/core/compound.c`: `compound_rows[]` (split, pin-only) with `CompPart.groups` and the LISTED conjuncts `split_conj[]` (§A.1, §B.4), `compound_place[]` (§A.2), the combinators, the prologue, the call-site code table (§A.14) with the dead trap under each part call, the assembly, `drop-compound`, the namespace reservation table with rows 1 and 3 (§A.5), the harness lever and `build/pcrec-harness` with the reserved-prefix fence (`run_lever_fence.sh`, §A.11), `<PREFIX>_COMPOUND` on every artifact, the stamp classification and sentinels; `PB_ONE_ATTEMPT` as a general emission option and the `RF_CROSSES_ATTEMPTS` wording (soft items); G1-G7, the lever arm, CMP rows. Spec: **`match_api.md` §4¶10 becomes the call-site code table (first producer)**, §1¶2 (`__` reserved), §3¶1, §3.2 (`_match` on a compound), §6 route values `"compound"`, §6.3 the stamp, its three values and the sentinel table; `limits.md` (caps on the assembled text, `drop-compound`); `ir_listing.md`/`facts_listing.md` (the compound listing, each conjunct's verdict); `cli.md` (the namespace table beside `-p`'s grammar) | **the abi event**: every artifact by one stamp line; the ~30 admitted by ID; bench 0 (G6) |
| **B5** | S+F/G+F: A5 widened to an unanchored Q under the cost conjunct (§B.7) | its trigger first; then G2/G3 on the new population with matching cells (chk B1's) | the admitted by ID; not abi |
| **B6** | VM parts: the one meter (§A.9), caller buffers with the frame-unit spec hunk, the DEFINE-style group keep, call-site rows 3, 4, 7 | the give-up differential | the admitted by ID |
| **B7** | captures on demand (§D.1) | its trigger; the N-vs-C span gate | the admitted by ID |
| **B8** | §C's hook (owner-tagged region) with [FINDALL-NEXT] at [IFACE-PUSH] | that push's | that push's |

### F.1 What the B4 brief states (decided here, so the brief does not re-open them)

- **The lever's fence is a reserved unique prefix plus ONE global check plus the widened grep**
  (§A.11), not the per-symbol allowlist. The manager's lean, with its reason: the
  allowlist's ~560 rows churn with every internal refactor and say nothing about the lever.
  The full export-surface check stays a separate optional row for [EMIT-ENTRIES]' public
  request (U3).
- **ONE call-site code table**, B4 emitting rows 1, 2 and 8 (§A.14); the `match_api.md` §4¶10
  hunk is in B4's commit; `PCREC_ERR_INTERNAL` propagates.
- **`CompPart.groups`** and the slot-coverage check land in B4's first commit, ahead of any
  controller row.
- **Admission and placement are tables with listed conjuncts** (§A.1, §A.2, §B.4); the
  decline controls are DERIVED by running the as-built derivation (§E.4).
- **Two soft items land in B4's lane**: `PB_ONE_ATTEMPT` as a general emission option (§A.5)
  and the `RF_CROSSES_ATTEMPTS` wording (§B.8).
- **Cosmetic, B4 decides**: F's emitted bound comment (§B.1).
- **Gates**: G3's two final-newline cells at today's rev-end cost (§E.3), tightened by B3.

## G. Open questions (discussion: problem, forces, leaning)

Only what D163 addendum 2 left open. The alignment note's three questions are RULED (D163
add. 6: one meter per exported call, callout purity "for now", `INTERNAL` propagates) and are
folded into §A.9, §B.8 and §A.14; they are not repeated here.

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
*Leaning:* refuse `__` in a user prefix at B4, with the spec hunk, as ROW 1 of the namespace
reservation table (§A.5), not a standalone check.

**Q3. VM parts: the compound may answer where today gives up, and under ONE meter the reverse
is possible.**
*Problem:* with VM parts (B6) and the ruled one meter per exported call (§A.9), a compound
charges the same meter as the plain artifact, so "fresh budget per part" no longer makes it
answer more often; but Q has fewer arms (it can answer where P gives up) and the bounded F
may cost a step more at the floor (P can answer where the compound gives up). The lever arm of
test-axes will see both directions. *Forces:* D158 forbids an optimization that turns an
answer into a give-up, and that is exactly the second direction; the first direction no
ruling forbids, but test-axes' GIVEUP1 allowances exist for that shape and would need rows
derived from stamps. *Leaning:* accept the first direction; require 0 cells in the
forbidden direction (the give-up differential, §E.3); derive the lever arm's GIVEUP1 allowance
rows from the compound stamp, never by hand. Not needed before B6.

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
- **The alignment note's unlocks** (`compound_callout_alignment.md` §13, named A-U1..A-U6 here
  so they do not collide with this list's numbers) are the same family and keep their own
  triggers: A-U1 one-attempt `_match` on EVERY attempt route (the general form of §A.5's soft
  item), A-U2 validate-once across a call chain, A-U3 callout bindings resolved at compile
  time as parts, A-U4 lifting A3 for callouts (§B.8), A-U5 slot seeding from `ctx->caps`, A-U6
  the combinator type check admitting external callees (§A.2).

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
   final-newline two-seed walk (3.00× against the lever, two shapes), which is Q's own rev-end
   cost: gated at today's rev-end cost by G3 and tightened by B3's commit (§E.3).
5. **J-5. The first build's bench reach is 0**, so G6 is a whole-bench byte check, with 16
   single-class floor rows and 2 concat-sqli rows as the named at-risk subset.
6. **J-6. A user prefix containing `__` can collide with a part name inside one TU** (§G Q2).
7. **J-7. Revision 2's controller contradicted `match_api.md` §4¶10** (found by the alignment
   note, §5.1): `if (r != 0) return r;` returns `STARTPOS` and `INTERNAL` where §4¶10 traps. B4's
   controller is the first generated call site of a composed submatcher, so the obligation binds
   it now. Fixed by §A.14's one table (B4 emits rows 1, 2, 8) and the §4¶10 hunk in B4's commit.
8. **J-8. A `rev-end` tie makes `<p>_search` call `<p>_match`** (cpb02 finding 1), and Q is
   `rev-end` by A5. `<p>__q_match` is therefore KEPT STATIC, not omitted, when Q's tie finish is
   built (§A.4). The closure must read each part's shape edges from the entry table; a hand
   list for split would have missed it, as the B0 check did on its first run.
9. **J-9. The twin's decline list is not the derivation's** (cpb02 finding 2): the as-built
   per-node `(?m)` scoping derives three shapes the twin declined, and revision 2's `^x|\n(?m)^b$`
   decline control is wrong. B4 derives its decline list by running the derivation (§E.4).
10. **J-10. The attempt-scope column has one member today** (cpb02 finding 4): the callout row.
    The verbs are refused at parse, so A3's verb half and the `^a(*COMMIT)b|c` witness are
    UNREACHED by an artifact (§B.8).
11. **J-11. `PB_ONE_ATTEMPT` is part-mode-coupled as built** (`pcrec_part_one_attempt` tests
    `pcrec_is_part`), which the alignment note's soft item asks to be a general emission
    option. B4's lane moves it to the emission request, with part mode its first reader (§A.5).
12. **J-12. "Bit 55 stays free" is stale** (D164 add. 5): bit 55 went to the kit's
    `-fno-kit-size-drop` and bit 56 to B3. The compound takes no bit and reserves none, so the
    design is unchanged; the sentence is corrected in §0 and §A.11.
13. **J-13. The controller's pad runs on success only** (§B.2). Revision 2's sketch padded
    unconditionally; delivery on success (alignment §6.3 point 3, `match_api.md` §3.1¶4: a
    failing call leaves caps untouched) makes the on-success form the rule. A clarification of
    the sketch, with no effect in the DFA-only build (`ncaps == 1`), stated for B6.
