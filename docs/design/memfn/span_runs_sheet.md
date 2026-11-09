# span_runs_sheet — R-38's interface sheet: the necessary run as one uncut span (design, rev 1)

Lane r38s1, 2026-11-09. DESIGN ONLY: no code, no build go. Rev 1 applies readiness review
2026-11-09 r2 r38s AS RULED (`docs/dev/reviews/2026-11-09-r2-r38s.md`, "Manager rulings"): F1-F11,
the PLAN unit K38-2a, and the owner/manager answers to §6 Q1-Q6. Changed text is marked `[r1 F<n>]`.
Rev 0 (lane r38s, `0de3cadec`) is in git history.

## Revision log

| rev 1 item | what changed | section |
|---|---|---|
| F1 the earned skip | rewritten: pcrec's decision on two pcrec facts per run (SUFFICIENT, OUTPUTS-DETERMINED) plus the kit's verified extent; the start is `c − omin`; the kit never infers exactness; D187 add. 1's noted gap cited; no unit of this sheet builds it | §3.4, §2.3, §6 P1 |
| F2 the seam | the ask moves from fact derivation (`src/facts/`) to pre-check SITE CONSTRUCTION (`src/gen/`, `req_pres_ask`); NO new entry: the reply rides `mf_ask`'s class (`mf_class.run`), read beside the run span's link; `req_whole_run` stays the pattern fact | §2.2, §4, §6 Q6 |
| F3 reply closed | none state read off the link; `has_scan` for the no-find shape; invariants; the exact input list incl. levers; "every level the define may render" | §2.2, §2.3 |
| F4 Goal 1's scope | scoped to the pre-check; the prefilter window site's run member named as a second, kept decider; REQ_BYTE's rule and function named; C4 restricted to `RX_REQ_WHY "emitted"` | §1, §2.5, §4.1, §2.4 C4 |
| F5 spec hunks | K38-2's pcrec half lists every `docs/spec/` paragraph it rewrites | §4.4, §5 K38-2 |
| F6 readers and movers | the run-pin choice (the pin reads the WHOLE run, a counted population); every unnamed reader with its fate; sabotage fates per unit | §4.2, §4.3, §5 |
| F7 checks that cannot fail | C1, C2, C4, W-L1, W-K2, W-K3, W-K4 and K38-1's census plant rewritten with reaching inputs; new unit K38-2a (G2 presence family + the probe lever) AHEAD of K38-2 | §2.4, §3.5, §5 |
| F8 pcrec abi | K38-2 IS a pcrec abi event; the D76/D94 ritual is its content | §5.1 |
| F9 statement shape | the two moving refusals; the derived part's unread fields; the two meanings of "verify" named apart; run-span constants as true facts or refused; `member` unread on the run | §2.1, §5.1, §6 P3 |
| F10 departures from R-38 | `maxoff` not stated, verify NO, "least occurrence" read as "least candidate": each said, with why | §2.1, §3.3 |
| F11 nits | §2.5 cite fixed; Q1's movers corrected; landmark cite `emit_dfa.c:1557-1565`; compose.c −23 after 3.0a; constraints split from ranked goals | §1, §2.4, §6 Q1 |
| SEAM-7 (PLAN, answer asked) | K38-2 adds NO entry; the general form is noted with its unlocks | §6 Q6 |
| §6 Q1-Q6 | recorded RULED | §6 |

It answers R-38 (`memfn/docs/requests.md` on main, "R-38"), the kit request of
`docs/design/span_arms.md` rev 2.2 §8.2 AS AMENDED by the owner's rulings §12a (2026-11-08), §12b
(2026-11-09) and §12c (the F1 correction), and D191. Where §8.2 and §12a differ, §12a wins:
nothing about consumption crosses (no `cons` at the seam), the run is never cut by pcrec, and the
scan position and verify extent are ONE decision, the kit's.

Base: the joint U2+U3 tree (lane/u3mech 404cff6ea, `MF_SITE_ABI` 26). File:line cites are at this
base; once `plan_frame.md` 3.0a lands, every `memfn/src/compose.c` cite below `pres_layout_check`'s
head moves by −23 lines (no cited name is renamed; `fd_find` gains an argument). Cites by function
name are preferred and hold across 3.0a.

What is the seam's and what is the kit's. Sections 2-4 are the SEAM: facts pcrec states, facts
pcrec reads back, and the contracts both rely on (D157: facts, never a method). Section 5 is the
KIT'S OWN build sketch; its method choices are not questions. Section 6 records the rulings and
the remaining questions.

## 1. Constraints and goals `[r1 F11]`

**Constraints** (gates every option passes; never traded against a goal):

- **Answer identity** against libpcre2 over the corpus, on every `--memfn=` deny arm and both SIMD
  layers (D26: what a pattern matches is exact).
- **In-bounds reads**: no read below subject offset 0 or at or past `n`, on any level of any target
  in the art's list.
- **The owner rulings**: the run is ONE uncut entry of D172's span list; its scan and verified
  extent are ONE decision, the kit's (§12a, D191 item 2); nothing about consumption crosses; the
  earned skip is pcrec's decision on pcrec's facts (§12c); no silent defaults.

**Goals** (ranked; a higher goal wins a conflict):

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **pcrec can build L2 and L3 against this sheet without asking again** (the L2/L3 build lanes) | every field pcrec states or reads has its type, home, value range, none state and meaning here; every pcrec reader of the reply and of the retiring cut is named with its fate (§4) |
| 2 | **One decision for the pre-check's run** (the next editor of either side) `[r1 F4]` | on the PRE-CHECK site, pcrec computes no run scan index and no run window: `git grep` finds `pcrec_find_run_scan_index` called only from `pcrec_req_pick` (REQ_BYTE, §4.1) and `pcrec_find_run_window_start` gone. Inside the kit, `kit_run_member(` and `kit_pres_picks`' run half are called only from `run_decide` (a counted caller check, K38-1). The prefilter window site's run member stays a second decider for a different site, named and counted (§2.5) |
| 3 | **The seam unit moves only named bytes** (every user) | `emit_sweep` at K38-2: zero movers outside the populations §5.1 names, each counted two-sided (pcrec's artifact diff, never the kit's `moved`, K35) |
| 4 | **The step back is bounded** (lookbehind users; a find-all caller pays it per call) | the step back per call is at most `lb_bytes` (pcrec's cap; the kit states no bound, §3.1) |

**Non-goals.** Any priced row (span_pick stage 3). Which positions the run CONSUMES (pcrec's own
fact; nothing about it crosses). BUILDING the earned skip (§3.4: the unit is main's to name,
§6 P1) and [MATCH-KNOWN]'s prefix-skip (they read §2.2's extent; no build here). Cutting,
splitting or windowing the run on pcrec's side. A second wider run beside the run (§12b Q3: one
value). A set-side change: the one-byte landmark and its agreement check in `req_site_define`
(`src/gen/emit_dfa.c:1557-1565`) stay as they are `[r1 F11]`.

## 2. Part A: the run as ONE uncut span

### 2.1 What pcrec states

The run is a presence span of the pre-check site, as today (`mf_site.pspans`, the run LAST), but
its positions now cross in SET form as one D172 span.

The seam stays D172's LIST of span statements, and every other span of the list is unchanged. "One
uncut span" (R-38, as clarified by main 2026-11-09) means only that the necessary run is ONE entry of
that list, never cut by pcrec into a window or into several pieces.

| fact | where it lives | type | value |
|---|---|---|---|
| the run's positions | the run's `pspans` entry, through the `mf_pred` window-statement members that today serve only FUNC parts: `nalt` 1, `alts[0]` = {`entry` `MF_ENTRY_NONE`, `nspan` 1, `spans[0]`}, `wfloor` `MF_WFLOOR_SUBJECT` | `mf_wspan` | `start` 0 (positions are relative to the occurrence's position 0), `len` n (2..`MF_WSPAN_POS`), `set[j]` position j's byte set (256-bit, D187; a cube is never stated beside it), `table_ref[j]` 0, `core` STATED over all n positions (every successful attempt holds every position inside the subject), `verify` `MF_VERIFY_NO` (§6 Q3) `[r1 F11]` |
| no RUN term | the same entry | — | `nterm` 0. The `MF_T_RUN` term with its `run`/`mask` arrays leaves `pspans` (a cube shape, which D187 retires at the seam). Set-member spans keep their one SET term |
| placement | the same entry's `omin` | `int32_t` | the smallest offset, from the ATTEMPT start, at which the occurrence's position 0 can lie. Part B (§3) widens its sign |
| need, class | the same entry | as today | `need` per route (REQUIRED where no DFA scan fronts the route; `site_kind_of`, a `src/gen` fact), `span_class` `MF_SPAN_PRESENCE`, `member_order` 0 |
| the run part | the pre-check's `preds[]` | `mf_pred` FUNC part | ONE run part (`fn_ref` its name id) with NO window statement of its own (`nalt` 0): the kit derives the part from the run's presence span, and renders it only where the run's link is tested (§2.2). pcrec no longer states [K66]'s second whole-run part (`req_run_tests`'s `t[1]`). `ret_pred` names the run part where the site ASSIGNs its landmark, as today |

**True facts, or refused.** `[r1 F9]` Every constant above is a TRUE fact the kit may read, and the
kit refuses the run span where one is not: `start` 0 (positions are occurrence-relative by
definition), `table_ref[j]` 0 (pcrec emits no table for a run position), `entry`
`MF_ENTRY_NONE` (the run is no window site's alternative), `nalt` 1 (one statement). On the derived
run part the `mf_pred` fields that state a span (`need`, `nterm`, `term`, `omin`, `verify`, `nalt`)
are UNREAD and must be 0: the span's own fields are the facts, stated once (refused if nonzero).

**Two meanings of "verify", named apart.** `[r1 F9]` The span's VERIFY FACT (`mf_wspan.verify`,
pcrec's, D172/D187 add. 1's DOWN fact: whether pcrec's own exact check follows) and the link's
TESTED BIT (`mf_link.verify`, the kit's decision: the span is tested at all). This sheet writes
"verify fact" and "tested" for them.

- **No maxoff crosses: a stated departure from R-38's list.** `[r1 F10]` R-38 Part A and §12a list
  `omin`/`maxoff`; this sheet states no `maxoff`. The PRESENCE class is bounded below only (`omin`,
  no `omax`, `memfn.h:543-545`), no kit row reads a run's upper offset, and where the largest offset
  IS read (the ASSIGNED landmark) it crosses as `head_max` (K, §3.2). Stating it anyway is an unused
  field (memory `pcrec-no-silent-defaults`; D157). Trigger to add it: the first kit reader of a
  span's offset RANGE, D176 Q4 ([MEMFN-UNBOUNDED-SPANS], telling a bounded stop candidate from a
  presence-only span); that unit adds the field. The earned skip's fixed placement is pcrec's own
  fact and needs no crossing (§3.4).
- **No cut.** pcrec states the whole stored run, every position its analysis holds. The length
  bound is `MF_WSPAN_POS` (32), DERIVED from `MF_MAX_TERM`, which equals the analysis bound
  `PCREC_MAX_REQ_RUN_SCAN` (32, `src/core/limits.def`). TOP's extensions are clipped at the stored
  bound (span_arms §5.2 TOP); pcrec asserts `n <= MF_WSPAN_POS` where it states the span.
  `PCREC_MAX_REQ_RUN_EMIT` retires (§4.3). Any length limit on what the kit verifies is the kit's
  own priced choice.
- **Why the presence span and not a window site.** The run's attempt-relative placement (`omin`,
  and K) already lives on the presence statement. Today the run crosses as the presence RUN term
  AND as a fabricated window site (`req_run_member`, `emit_dfa.c:1058-1076`). Keeping the presence
  span and giving it the window span's set form makes it once on the pre-check site.

### 2.2 Where pcrec asks: pre-check site construction, through `mf_ask` `[r1 F2, F3]`

**The reply is a SITE decision, not a pattern fact.** Two inputs of the define's run decision exist
only at site construction: the route (`need`: P0 keeps the run whole where it is REQUIRED, P3 picks
a stretch where OPTIONAL) and the site's proof (`pres_proof`: P2's dominance renders NO run part at
all). Measured at the base: `xabcdefghijkq\w` and `a.*xabcdefghijkq` state the same run record;
the first renders no run part (`RX_REQ_WHY "dominated"`), the second an 8-position part. So pcrec
asks where the pre-check site is BUILT, in `src/gen/`, never at fact derivation.

**No new entry.** The question is already asked there: `req_pres_ask` (`src/gen/emit_dfa.c`, the
one constructor's ask, called by the admission verdicts in `req_admit` and by `req_site_define`)
runs `mf_ask(art, site, hooks, &cls)`, the pure define-time query, which answers each span's link
(`mf_class.pres[i]`) from the same rows the define runs. The run's reply joins that answer as ONE
record of the class, so the run's tested bit and its extent come from one decision in one call,
and no second slot says "is the run verified" (rev 0's `mf_run_reply` beside `mf_link` held it
twice):

```
typedef struct {                /* mf_class.run (MF_CLASS_V moves, §5.1)                      */
    uint8_t has_scan;  /* 1: every rendered candidate filter tests `scan`'s set (others may   */
                       /*    be ANDed in, e.g. vrun's w32 second position); 0: no single find */
                       /*    position (the floor/byte-loop shape)                             */
    uint8_t scan;      /* the run position the find reads; unread where has_scan is 0         */
    uint8_t ver_lo;    /* THE VERIFIED EXTENT: positions [ver_lo, ver_lo + ver_len); every    */
    uint8_t ver_len;   /*   candidate the run part yields holds each of them in its set;      */
                       /*   ver_len 0 = none verified, and then ver_lo is 0 and unread        */
} mf_run_reply;
```

- **None state: read off the link.** pcrec reads the reply ONLY where the run span's link is
  tested (`cls.pres[run].verify` 1). Where the run renders no part (P2: `proven_by` 1; or no run
  span stated), `cls.run` is all zero and UNREAD: pcrec's readers take the "no run part rendered"
  branch from the link, never from a zero `scan`.
- **Invariants** (a text reader can check a record): `scan < n` where `has_scan`;
  `ver_lo + ver_len <= n`; `n <= MF_WSPAN_POS`, so `uint8_t` holds every member. `scan` may lie
  outside `[ver_lo, ver_lo + ver_len)` (§2.3).
- **`mf_link.member` on the run span is UNREAD** (no longer "0 = the whole run tested"): the extent
  is `cls.run`'s. On set-member spans `member` keeps its meaning.
- **Inputs, closed** (what a text round trip of the ask carries, and all it carries): the site as
  stated (the run span with its `need`, `omin` and verify fact; the set-member spans; `pres_proof`;
  `policy`; `denies`; `opts`), the define hooks, and the art's {byte-rate payload and its state,
  measure-set rows, target row and its admitted levels, `levers`}. The run's reply does NOT read
  `handoff` or `head_max`: pcrec decides those AFTER this ask (`req_use`, the handoff's K) and may
  change them before the define, so a reply that read them could differ from the define's. The
  landmark admission reads the reply, never the reverse.
- **Purity and the define.** `mf_ask` is pure (no text, no handle, no art state) and answers what
  `mf_define` renders for the same site, hooks and art state; a trace build re-asks at the define and
  fails on a difference (`mf_result.cls`, §4.5 rule 2 of r17b_prime). `cls.run` inherits both
  properties; it is part of the class.
- **The Job keeps the defined site's reply.** pcrec keeps the reply of the ask whose site it
  DEFINES (`req_site_define`'s `req_pres_ask`) on the Job's pre-check record beside the links
  (pcrec's names; e.g. a `req_run_reply` member), and every reader of §4 reads it there. The
  admission verdicts' own asks (`req_admit`, with the start search's proof) read only links, as
  today; a reader that runs before the define asks the same site through `req_pres_ask` (pure, so
  equal for the same site). `req_whole_run` stays the route-free PATTERN fact;
  no reply value is stored in a fact (D124: the record holds no route or emission decision).
  `--emit-facts` lists pcrec's run; the scan shows where the site and the stamps are rendered.
- **The art lifecycle question retires.** The ask runs where the art is live (site construction,
  inside the Job's attempt), so rev 0's facts-to-art hook and the forced-listing ask after
  `pcrec_memfn_art_end` (review SEAM-8) do not arise.

### 2.3 The kit's reply: ONE decision

- `scan` and `[ver_lo, ver_lo + ver_len)` are one decision, over ANY run position, consumed or not
  (§12a: "the scan bytes should come from any span position"). The kit may scan one position and
  verify any contiguous stretch, the whole run included, or verify nothing beyond its find.
- `scan` need not lie inside the verified extent: a find on a covering set (D187 add. 1: a lossy
  cover is the reader's legal private test) proves nothing about `scan`'s position.
- **The kit reports how far it verified, and nothing more.** `[r1 F1]` `ver_len` says which
  positions every yielded candidate HOLDS, each against its whole stated set. It never says the
  candidate is a match: per-position sets are a COVER of the attempt, not its language
  (`(?:ac|ca)xyz` states `[ac][ac]xyz`, which admits `aaxyz`), and the kit holds neither fact that
  would make it one (§3.4). The kit never infers exactness from its own sets.
- **Every rendered variant.** `[r1 F3]` The reply describes EVERY text the define may render for
  this site: each level in the site's `policy` that the art admits, for each target in the art's
  list (U2/U3). A form that would verify less than `ver_len` on some variant is either held to it or
  the reply reports the minimum. This is stronger than `plan_frame.md` §2.3's stated gap (the frame
  part names the OFF variant only), and it must be: pcrec's earned skip reads `ver_len`.

### 2.4 Which agreement checks retire, and what replaces their control

| today's check | where | what it holds equal | fate |
|---|---|---|---|
| `req_run_member`'s "internal error: the window family's run member N is not the run window's own index" | `src/gen/emit_dfa.c:1058-1076` | pcrec's `r->idx` (`pcrec_find_run_scan_index`) and the window family's member over pcrec's fabricated run-window site | RETIRES with the function: pcrec has no pre-check run index of its own. Every reader of §4.2 reads the Job's reply. `plan_frame.md` §4.2's ASK-2 (this call with call NONE) has nothing left to change |
| `pres_layout_check`'s RUN half | `memfn/src/compose.c:704-718` (−23 after 3.0a) | P3's `run_scan` inside the window, and the run part(s) equal to pcrec's window (`part_is_run`: bytes, mask, `plan_pos`, length) and to the whole run | RETIRES: pcrec lays out no run window. What STAYS is a statement rule, not a pick agreement: exactly one run FUNC part where the run's link is tested, none where it is not, stating no window of its own. Its chain-order clause compares the kit's `mf_link.order` with the part's index in pcrec's `preds[]`: a duplicated slot kept by a check, named as such `[r1 F9]` |
| `pres_layout_check`'s head and rest halves | `compose.c:697-703`, `:719-729` | set members | unchanged (out of scope) |

**The replacement controls** (`docs/dev/learnings.md` §3: a control must not share a source with
the thing it controls). With one decider, an equality between its own outputs would share its
source, so each control reads an INDEPENDENT source. `[r1 F7]` Each row names the unit where its
witness first reaches.

| # | what is controlled | checked against (the independent source) | witness, plant, where it reaches |
|---|---|---|---|
| C1 | the kit's candidates are sound: no whole-run occurrence lies in `[floor, c)` (§3.3); and, once a skip exists, a skipped finish is right | libpcre2's answers (the corpus, `make test-axes` on every deny arm, both layers) | At K38-2a/K38-2 the soundness half is the G2 family's occurrence oracle (C1 needs pcrec's answers, and pcrec states no extension yet). Plant "the candidate floor is `lo`": W-L1 (§3.5). The SKIP half reaches only at the unit that builds the skip (§6 P1), on the VM route (`--engine=vm`; the default route of `bar(?=baz)` is `dominated`, no run part): plant in the RENDERER, the compare of the last claimed position dropped while the reply keeps `ver_len` n; subject built FROM the reply, a near-miss differing at that position: `barbaz` on `barbaq barbaz`, expected (7,13) (libpcre2), plant (0,6). Pre-L2 this is a whole-attempt literal run, no lookaround needed |
| C2 | the reply describes the text | the RENDERED TEXT, classified by G2's presence family (K38-2a): the run part's find byte set CONTAINS `scan`'s set (a superset is a legal cover; an ANDed second position is allowed); its compares cover exactly `[ver_lo, ver_lo + ver_len)`; no run part where the link is untested. The expectation is read off the define's output, not off the decision function (`plan_frame.md` Goal 2's pattern) | plant in the decision: the reply says `ver_len` + 1 while the renderer renders the old extent; G2 red. Plant in the renderer: one compare of the extent dropped; G2 red. Reaches at K38-2a on today's statement form (`omin` 0, K >= 0) |
| C3 | the ask's class equals the define's | the purity harness: `mf_ask` interleaved with defines, whole-class `memcmp` (`cls.run` included); and the trace build's re-ask at the define (`mf_result.cls`) | shares the function BY DESIGN (it proves purity, not correctness; C1 and C2 cover correctness). Plant: a static counter the run decision reads; the harness reds |
| C4 | pcrec reads the reply at every reader (no reader keeps its own pick) | the ARTIFACT TEXT: a pcrec codegen check that `<PREFIX>_REQ_RUN`'s `@scan` names the OFFSET of the position the emitted run-part find reads (not only its set). Population: artifacts with `RX_REQ_WHY "emitted"` and a tested run link, counted; on `dominated`/`cover` artifacts the find is another site's | plant: one reader (the stamp) fed `pcrec_find_run_scan_index`'s index. The two rules agree by construction at K38-1, and default-prior ties fall mostly on positions holding the SAME byte, so the check runs (a) in the all-tie regime (`--analysis=uniform`), where ties fall on different bytes, and (b) under the probe lever `run-tie-left` (K38-2a, §5): the kit breaks the run decision's ties LEFTMOST, pcrec's index stays rightmost, and the planted stamp names the wrong offset. Reaches at K38-2 |

### 2.5 The run on the prefilter's window site `[r1 F4]`

The run-pinned prefilter (`pf_window_of`, `ofs_window_of`, `emit_dfa.c:6815-6870`) states the run's
pinned stretch again, on a DIFFERENT site (the DFA's prefilter, not the pre-check), and
`mf_wdecide` names its member (`mf_wreply.run_member`/`run_lo`/`run_len`) by the window family's
rule: on a verify-NO stretch the least-mass EXACT position, ties to the higher offset. The
pre-check's rule (`kit_run_member`: least set mass, ties rightmost) shares the tie direction and
differs only by that EXACT restriction (the verifier's reading). This sheet keeps it: it is that
site's own decision, and §12a's "one decision" holds on the pcrec side (pcrec picks nothing on
either site). Consequences:

- Goal 2 is scoped to the pre-check. On an artifact with both sites the run crosses twice, once
  per site.
- `decider_census.tsv` lists `mf_wdecide`'s run member as a run decider beside `run_decide`, so the
  population is counted (K35). The unlock that would merge them is §6 Q6's general form, trigger
  "K38-1's caller check finds a compile where the two members differ for the same run position".

## 3. Part B: a negative `omin`, a signed K, and the earned skip

### 3.1 `omin` may be negative

- The origin of `omin` is the ATTEMPT start (§8.2 part B): `search_from` at entry; at re-entry,
  the scan or attempt position the hook's `lo` names (`.lo = posvar`, unchanged). At the attempt
  start's equal to the match start (every pattern without `\K`) this is today's meaning.
- On the run span `omin` may be NEGATIVE: the occurrence's position 0 may lie up to `-omin` bytes
  before the attempt start (L3, a positive lookbehind's bytes). Set-member spans keep `omin` 0
  (the set takes no guard byte, span_arms §5.4 A4); a negative `omin` there stays refused.
- **The kit's bound: none.** The run span's positions are relative to the occurrence (`start` 0),
  so `MF_MAX_BACK` (8, window span starts) and `MF_PROOF_LO` do not apply. The scan is memory-safe
  at any `omin` (§3.3's clamp). The field's range is its type's, `int32_t`; PCRE2's largest
  declared lookbehind (65535 characters, 4 bytes each under `utf8`) fits. So the step-back bound
  pcrec reads is `lb_bytes` alone (span_arms §5.5): min(`lb_bytes`, the kit's bound) = `lb_bytes`.
  The kit can never honour a statement by clamping `omin` towards 0: that would drop occurrences
  and answer NOMATCH wrongly. A kit that ever needs a bound REFUSES past it, loudly, and says so
  in this sheet's successor.

### 3.2 `head_max` (K) is signed

- `mf_site.head_max` becomes `int64_t`. K is the largest offset, from the attempt start, of the
  ASSIGNED landmark's position 0: the run occurrence's position 0 where a run part is the
  landmark, else the one-byte landmark's. With `omin < 0` it may be negative or zero.
- **The assigned value's meaning** (new, stated explicitly; §6 Q1 RULED): where the site ASSIGNs
  its landmark, the value is the position of the occurrence's position 0, whatever stretch the kit
  verified or scanned. Today it is "where the run window begins". K is the whole run's position-0
  offset (`whole_maxoff`), a pcrec fact stated before any extent exists.
- **None state: the kit's, unchanged.** `head_max` is read only where `handoff == MF_H_ASSIGN`,
  and is 0 (refused otherwise) elsewhere. A signed 0 on an ASSIGN site is a STATED K of 0. pcrec
  keeps its own stated/none bit for K (span_arms §8 L3), which never crosses.
- **The twin admission.** The kit's landmark port (`kit_pres_picks`' landmark half,
  `presence.c:199-222`, today `unsigned long long k = s->head_max`) reads K signed and admits by
  `max(K, 0)`: a landmark that begins at or before the attempt start costs no step back. That
  equals pcrec's margin `pcrec_landmark_margin` at `max(K, 0)`, which `req_pick_shadow`'s
  `landmark` record compares. BOTH mass terms read the reply's verified extent `[r1 F6]`: the kit
  twin's, and pcrec's `req_landmark_hit_ppm` (which today multiplies the cut window's masses); they
  move in the same commit, or the `landmark` record disagrees on every run over 8 positions where
  the kit verifies the whole run.

### 3.3 The occurrence contract, at entry and at re-entry

With `origin` the attempt start (entry: `search_from`; re-entry: the hook's `lo`) and
`floor = max(0, origin + omin)`, computed with no unsigned wrap:

1. **Candidate floor.** Every candidate `c` the run part yields (and ASSIGNs) satisfies
   `floor <= c`.
2. **Least.** No occurrence of the WHOLE run (every position in its set) has its position 0 in
   `[floor, c)`. A miss means no occurrence has its position 0 at or after `floor`.
3. **Held where verified.** Every yielded `c` holds every position in
   `[ver_lo, ver_lo + ver_len)` in its set. Where that is the whole run (`ver_lo` 0, `ver_len` n),
   `c` IS the least occurrence of the run's SETS at or after `floor`, the contract R-38 names. It is
   not thereby a match (§2.3, §3.4).
4. **Reads.** Every read lies in `[0, n)`. The candidate floor is below `origin` when `omin < 0`;
   the read floor is the subject's 0 (`integration.md` §14.7's `floor` rule, with `floor` the
   SUBJECT). No text may assume reads at or above `origin`.
5. **Re-entry** is the same contract with the re-entry's `lo` as origin. pcrec's move after it,
   `max(posvar, c − K)` with K signed and no `size_t` wrap, is pcrec's (span_arms §5.4 A3, §8.1).

**This narrows R-38's sentence, deliberately.** `[r1 F10]` R-38 Part B says pcrec relies on the
reply's OCCURRENCE being the least at or after the floor. The sheet promises the least CANDIDATE
(items 1-2) and the occurrence only where the extent is whole (item 3). R-38's literal form would
force a whole-run compare at every hit, which removes the extent choice §12a and D191 item 2 give
the kit. The weaker promise is sound for every pcrec use: the move `max(posvar, c − K)` (any
match's attempt start `a` has its occurrence at `p >= c`, so `a >= p − K >= c − K`), the miss (no
candidate implies no occurrence), and the earned skip (gated on the whole extent). R-38's sentence
was written over a pcrec-cut window. The pcrec texts that state the stronger form get the same
narrowing in K38-2's spec hunks (§4.4): `match_api.md` §6.3.7¶11 ("returns the LEAST position ...
at which the landmark occurs") and `tuning.md` §2.41.

`floor` is the kit's text (span_arms §8.1: not a pcrec call site). Its spelling must not wrap:
`lo + omin` in `size_t` with `omin < 0` and `lo < -omin` gives a huge floor and a false NOMATCH
(W-K1's plant).

### 3.4 The earned skip: pcrec's decision on pcrec's facts `[r1 F1]`

D187 add. 1's "earn a skip", per run, as §12a stated it and §12c corrected it. pcrec reports a
run-part hit as the match WITHOUT its finish only when all three hold:

1. **SUFFICIENT** (a pcrec fact about the run, stated per run): every string the stated position
   sets admit, at the run's one fixed placement (`omin` equals the run's largest offset), is an
   attempt of the pattern over that span. The product of the sets is then exactly the attempt's
   language. `core` (necessity) is not this fact. Counterexample it excludes: `(?:ac|ca)xyz`,
   run `[ac][ac]xyz` (`req_whole_run 616178797a/fdfdffffff`), whole attempt, fixed: a whole-run
   verify yields `aaxyz`, libpcre2 NOMATCH. Under D187's general sets the same holds wider
   (`-e utf8` `[éĀ]` as {c3,c4}x{a9,80}).
2. **OUTPUTS-DETERMINED** (a pcrec fact about the pattern over the span): the match's reported
   bounds and every capture follow from the attempt position alone: no capture inside the span,
   no `\K`, no MARK or verb name the match reports. Counterexamples: `(bar)(?=baz)` on `barbaz`
   (libpcre2 group 1 (0,3)); `bar\K(?=baz)` (libpcre2 (3,3)).
3. **The kit's reply says it verified the whole run** (`ver_lo` 0, `ver_len` n, read beside a
   tested run link, §2.2).

Then the attempt start is `c − omin` (a pcrec fact on every route; rev 0's `c − K` read a field
stated only on ASSIGN sites), and the bounds and captures are pcrec's from it.

- **Whose decision.** pcrec's, on its own facts. The kit's part is ONLY to report how far it
  verified (item 3); it is told nothing of SUFFICIENT or OUTPUTS-DETERMINED and never infers
  exactness from its own sets. Neither fact crosses the seam.
- **The kit's extent choice is blind to the skip's value.** That is D187 add. 1's NOTED GAP (the
  trade needs pcrec's finish cost as a stated fact, F4 no-blindness; stated when kit pricing
  opens), not a design property. Harmless while no row is priced (K38-1 reproduces today; a
  6-position `barbaz` lies inside today's 8-position stretch).
- **Call mode** (review F1's proposal; unverified whether the entry reaches the run part): a call
  whose mode constrains the match beyond the attempt (the not-empty-at-start retry after an empty
  match, match_api §3.1.3) takes the finish. pcrec states this at the skip's unit.
- **No unit of this sheet builds the skip.** span_arms L2/L3's rows predate §12a; main names the
  unit and the SUFFICIENT fact's producer (§6 P1). Its witnesses: `(?:ac|ca)xyz` on `aaxyz`
  (expected NOMATCH; plant: skip on necessity only), `(bar)(?=baz)` on `barbaz` (expected group 1
  (0,3); plant: skip ignoring captures), and C1's skip half (§2.4).
- **[MATCH-KNOWN]'s prefix skip** (D142, D191 item 4) reads the same extent later. No build here.

### 3.5 Part B's witnesses (answers measured with libpcre2 by the build) `[r1 F7]`

pcrec states no negative `omin` before L3. So each witness has a G2 form, which reaches at K38-2
in the G2 presence family (K38-2a builds the family on today's form; K38-2 extends it to negative
`omin` and signed K), and a pcrec form, which reaches at L3 (VM route).

| id | plant | G2 form (K38-2) | pcrec form (L3) | fails how |
|---|---|---|---|---|
| W-L1 (span_arms §5.7) | the CANDIDATE floor is `lo`, not `floor` | run `foobar`, `omin` −3, origin 3, subject `foobar`: expected candidate 0. A second case with the art's rates set so the scan falls on a position whose byte lies below `lo` (G2 states the rates), so the spelling "byte search starts at `lo`" also reaches | `(?<=foo)bar` from 3 on `foobar`: (3,6) | NOMATCH / no candidate |
| W-K1 | `floor` spelled `lo + omin` in `size_t`, no clamp | run `foobar`, `omin` −3, origin 1: expected candidate 0 | `(?<=foo)bar` from 1 on `foobar`: (3,6) | the floor wraps to about 2^64: no candidate / NOMATCH |
| W-K2 (re-entry) | the re-entry floor read from `lo` | run `abab`, `omin` −2, subject `abababcc`, re-entry `lo` 3: expected candidate 2 | `(?<=ab)ab(\w)\1` on `abababcc` from 0: (4,8), group 1 (6,7) (the entry candidate 0 gives attempt 2, which fails; the re-ask at `lo` 3 must find 2) | plant floor 3: no candidate / NOMATCH. (span_arms W-L14's own instance answers NOMATCH everywhere and cannot show this plant) |
| W-K3 (twin) | the twin admission reads K unsigned | the landmark port's admission bit for K in {−32..−1} equals its bit at K 0; the expectation is generated from the stated rule `max(K, 0)`, never from `presence.c` | `req_pick_shadow`'s `landmark` record on `(?<=foo)bar(\w)\1` (span_arms W-L13), where K < 0 on an ASSIGN site | the bit differs / the record disagrees |
| W-K4a (below-zero reads) | an UNALIGNED read from an unclamped floor | the subject at a page start, a guard page below offset 0, `omin` −8..−32, every admitted level of every target in the art's list (U2) | — | a fault (G2) |
| W-K4b | a vector block read aligned DOWN from `floor` | ASan, the subject at offset 1..W−1 from a W-aligned heap start, per level of width W (an aligned-down load never leaves its page, so the guard page cannot see it) | — | an ASan report |

## 4. What pcrec reads, what retires, and the contract text (and where)

### 4.1 Readers of the reply

All in `src/gen/`, reading the Job's pre-check record (§2.2), and only where the run link is tested:

| reply member | pcrec reader | today's source it replaces |
|---|---|---|
| `scan` (where `has_scan`) | `<PREFIX>_REQ_RUN`'s `@scan` (`pcrec_fact_stamp_req_run` renders the whole run from the fact and takes `@scan` from the record), `req_note_run`, `req_set_leads_own`, `req_pick_shadow` | `ReqRun.idx` (`pcrec_find_run_scan_index`) through `req_run_member` |
| `ver_lo`, `ver_len` | the landmark mass term (`req_landmark_hit_ppm`, §3.2); the run's trace records (`req_pick_shadow`, MFPRES); the earned skip (§3.4, when built); [MATCH-KNOWN] later | `ReqRun.at`/`len`/`bytes` (pcrec's cut window) |
| the assigned `c` | `emit_req_handoff_rest`, `emit_req_landmark_move` (pcrec's move, K signed) | the window's begin |
| none | `<PREFIX>_REQ_BYTE` | **stays PCREC'S pick** (§12a, D191 item 2) `[r1 F4]`: `pcrec_req_pick` (`src/facts/req.c`) returns the byte of `pcrec_find_run_scan_index` over the whole run's CONSUMED positions where that position is exact, else the set's pick. At K38-2 every position is consumed (no extension yet), so the value equals today's (today's window always contains the whole run's scan member). From L2 the two may differ (`bar(?=baz)`: the kit may scan `z`, REQ_BYTE stays among `bar`), and they may differ on UNEXTENDED runs at the first kit rule change or regenerated measure set. `req_byte_dominated_by` (`emit_dfa.c:8583-8592`), which reads REQ_BYTE as "the byte the emitted memchr tests", reads the reply's `scan` set instead |

Where the run link is untested (P2, or no pre-check site asked on the artifact), `<PREFIX>_REQ_RUN`
shows the whole run with no kit scan (§6 Q7).

### 4.2 The run pin reads the WHOLE run `[r1 F6]`

The run-pin family reads the cut window today: `pcrec_run_pin` (`src/facts/kset.c:294-318`,
`cand[PCREC_MAX_REQ_RUN_EMIT]`, loops `r->len`), the `run_pin` listing row (`facts.c:863`),
`us_run_pin`/`pf_run_applies_common` (`emit_dfa.c:7361-7380`), `ofs_test_of`'s `t->run_bytes`
(`emit_dfa.c:7419-7423`), `ofs_test_verifies_run` (`emit_dfa.c:7487-7505`, which decides
`RX_REQ_WHY "dominated"`) and `pf_window_of`. **Choice: they read the WHOLE run** (arrays sized
`PCREC_MAX_REQ_RUN_SCAN`). Keeping a private 8-position window for the pin would keep pcrec's cut
under another name, against §12a's no-cut ruling. Consequence: the pin's offset and stretch, the
prefilter's compare length and possibly `RX_REQ_WHY` move on run-pinned artifacts whose run is
over 8 positions (measured at the base: `[a-z]abcdefghijkl\d+` `run_pin 5`,
`\w\wabcdefghijklmnop[0-9]+x` `run_pin 7`, `(?:a|b)abcdefghijklmn\d*z` `run_pin 6`, each
`run-pinned`/`dominated`). A population of K38-2, counted two-sided (§5.1). This is a pcrec-side
choice; main may reverse it at K38-2's brief, and the population then leaves the count.

### 4.3 Readers of the retiring cut, the RUN term and K, with fates `[r1 F6]`

| reader | today | fate at K38-2 |
|---|---|---|
| `ReqRun.idx`/`at`/`bytes`/`mask`/`len`, `pcrec_req_window`'s cut, `pcrec_find_run_window_start` | the cut window | RETIRE; `pcrec_req_window` keeps only the run's `maxoff` (= `whole_maxoff`, Q1) |
| `ReqRun.len >= 2` "a run shipped" (`emit_dfa.c:1172, 1542, 1600, 7376, 7491, 8586, 8588, 8607, 8658, 11048`; `facts.c:318, 332, 581, 828, 833, 915`) | the window's length | read `whole_len >= 2` (mechanical: `facts.h:69`, `whole_len` is 0 exactly when `len` is) |
| K's derivation (`facts.c:318-335` `req_landmark_maxoff = req_run.maxoff`; `req.c` `maxoff = whole_maxoff + at`) | the window's offset | `whole_maxoff` (§6 Q1) |
| `req_site_define` (`emit_dfa.c:1555-1556`), `req_pres_head`, `req_parts_in_whole` (`:8869-8872`): find the run span by `term[0].kind == MF_T_RUN` | the RUN term | find it by POSITION: pcrec states the run LAST in `pspans` (its own layout fact) |
| `req_parts_in_whole`'s K66 guard (`whole_len > len && member != 0`) | the two-part form | RETIRES with the second part (§6 Q5) |
| `req_run_tests` `t[1]`, `req_pick_shadow`'s `window`/`rwin`/`rwhole` records (`emit_dfa.c:11229-11336`) | pcrec's window, `k.run_window` | `t[1]` retires; the records read the reply's extent |
| `_Static_assert(MF_PRES_WINDOW == PCREC_MAX_REQ_RUN_EMIT)` (`emit_dfa.c:11185`) | the shared bound | RETIRES with both names |
| `PCREC_MAX_REQ_RUN_EMIT` (`limits.def`; `facts.h:65,77`; `kset.c:297-298`; `findings.c:780-800`; `tests/registry/limits_check.sh:161`) and `PCREC_MAX_REQ_RUN_SCAN`'s text ("Sized at four times ...") | sizes the cut | RETIRES (no role left after §4.2); `PCREC_MAX_REQ_RUN_SCAN`'s comment restated |
| MFPRES trace line (`src/gen/memfn_sites.c:741-757`, `head_max` as `%llu`) and its golden `tests/memfn/c10_presence.tsv` (`runlen`, `head_max` "the run window's largest offset") | unsigned K, window length | print signed; the golden's columns re-meant (whole run, position-0 K) and re-recorded |
| `tests/findings/structural_check.py` `KNOWN_READERS` | `pcrec_find_run_scan_index`, `pcrec_find_run_window_start` | the second leaves; the first's reader is `pcrec_req_pick` only |
| the `pres-window` lever (`mf_lever`, `KIT_LEVER_PRES_WINDOW`, `precheck.c:161`; pcrec `--harness=pres-window`, `src/core/internal.h:177-181`, `memfn_sites.c:217-219`; `tests/axes/run_axes.sh` `INTERNAL_ARMS`) | restores a window part beside the whole run | RETIRES: its old form is not constructible once the run is one derived part (memfn.h text, the kit row, pcrec's harness bit, the axes arm) |
| the listing rows `req_run` and `req_run_maxoff` (`facts_listing.md` §4.1.2¶8/¶8b) | the cut window | show the WHOLE run (equal to `req_whole_run`) and its position-0 offset; no reply value (D124). Whether `req_run` then retires into `req_whole_run` is pcrec's (§6 Q7) |

### 4.4 The contract text K38-2 rewrites (D80) `[r1 F5]`

K38-2's pcrec half carries these `docs/spec/` hunks in the same commit (the REQ_BYTE/REQ_RUN
cross-check breaks at K38-2, not at L2, so the hunks are K38-2's):

- `tuning.md` §2.28¶5 (the scan member rule and the 8-position truncation become the kit's reply;
  the truncation retires) and ¶7 (REQ_BYTE "exactly `bytes[idx]`" withdrawn: REQ_BYTE is pcrec's
  consumed-position pick); §2.29¶4 (the two-part whole-run route becomes one kit part); §2.41 (¶1
  "the run's window" becomes the run; ¶8b; the least-candidate narrowing of §3.3).
- `match_api.md` §6.3.7¶5 and ¶7 (REQ_BYTE vs REQ_RUN; `@scan` the kit's; the whole run shown,
  Q2), ¶11 (the LANDMARK is the run, position 0; K is position 0's offset; the least-candidate
  narrowing; worked examples re-measured: `(?i)straße`, "before the window `TRA`"), §6.3.1¶5a
  ("`_REQ_RUN`'s `@idx` with the `_REQ_BYTE` it implies").
- `facts_listing.md` §4.1.2¶8/¶8b (`req_run_maxoff` no longer a window's).
- `findings.md` §4: the "necessary run's scan member" and "necessary run's window" rows, and ¶2
  (the handoff reads the window).

Main drops ¶5/¶7/¶11 and findings.md §4's window row from span_arms L2's CHECKED-UNCHANGED list
(§6 P4).

## 5. Kit-side build sketch (THE KIT'S; not a question)

Sabotage ids are taken at build time from the top of the free range. Every heavy run is a
boxqueue job. Sizes: S under a day of lane work, M a lane, L a lane plus a fix round. The
"existing sabotages" column gives each committed sabotage the unit moves its fate (re-aimed,
retired with its control named, or kept), checked at build with `REACH_ONLY=1` `[r1 F6]`.

| unit | size | content | check | the plant that makes it fail | existing sabotages |
|---|---|---|---|---|---|
| K38-1 | M | ONE run decision inside the kit, NO seam move: P3's run scan and stretch, the whole-run keep (P0/P9), the window family's member for pre-check run parts and the twin admission's mass term all call one function `run_decide(rates, opts, span) -> (has_scan, scan, ver)`; its first rule REPRODUCES today (the incumbent: `kit_run_member`, today's P3 window, whole under P0/P9) | `emit_sweep` byte-identical on every arm (default, each `--memfn=no-X`, `--engine=vm`, both layers); REACH equality; a CALLER check: `kit_run_member(` and `kit_pres_picks`' run half are called only from `run_decide`, counted `[r1 F7]` | a tie plant in `run_decide` that must move EVERY reader's bytes together on a tie witness (S1095's `-e utf8 abcd`), counted per reader (layout, part text, twin mass); a reader left calling `kit_run_member` directly reds the caller check (`decider_census` checks a declared map and cannot see it) | S1095 re-aimed onto `run_decide`'s tie (it becomes the per-reader plant); S1096 re-aimed onto `run_decide`'s stretch choice; S1107 (`pres_layout_check` unchecked): its RUN half can no longer disagree, so re-aimed onto the head/rest halves, or retired with the per-reader tie plant named as its control |
| K38-2a (NEW, PLAN; ahead of K38-2) `[r1 F7]` | M | THE G2 PRESENCE FAMILY on the CURRENT `MF_SITE_ABI`: a generator of pre-check sites (set-member spans and a run span in today's form, `omin` 0, K >= 0, P0/P2/P3/P9 routes, both layers, every admitted level of the U2 target list), the derived run part, an OCCURRENCE-CONTRACT ORACLE (§3.3 items 1-4 including "least", written from the contract text; D27 spec-first author recommended, denied `memfn/src`), C2's text classifier, the guard-page and ASan placements W-K4 needs; and the PROBE LEVER `run-tie-left` with its pcrec `--harness=` arm | the family reaches the run part on every route it generates (counted per route); the oracle and the classifier agree with today's kit on the whole generated space | plant A: the run part drops one compare of its extent: the classifier reds. Plant B: the kit yields a candidate one above the least occurrence: the oracle reds. Plant C: the lever leaves the tie rightmost: its own reach witness (an all-tie run with distinct bytes, `--analysis=uniform`) shows no moved scan offset | none moved (new family) |
| K38-2 | L | THE SEAM EVENT, Parts A and B together: §2.1's statement form (the run in set form, `nterm` 0, the run part with no window), `mf_class.run` answered by `mf_ask`/`mf_defined`, `omin < 0` admitted on the run span, `head_max` `int64_t`, the floor `max(0, lo + omin)` at entry and re-entry, the twin admission at `max(K, 0)` with its mass on the reply's extent, the run part derived from the span, the retired members and the moved refusals (§5.1), the refusal texts, `pres-window` retired. G2's presence family extended to negative `omin` and signed K. pcrec's same-commit hunks: `req_pres_spans` states the new form (`omin` 0 and K >= 0: no extension yet), `req_pres_ask` keeps the reply on the Job's pre-check record, `req_run_member` and the cut retire, every reader of §4.1-§4.3 moves, the spec hunks of §4.4, the pcrec abi ritual (§5.1) | C2-C4 (§2.4); C1's oracle half in G2; W-L1, W-K1..W-K4b in G2 (§3.5); `emit_sweep` zero movers except §5.1's populations, counted two-sided | as §2.4 and §3.5 | S278 (`finder.c` `k.member = pk.run_window + 1`): retired, `member` is unread on the run; control the statement rule's plant. S1543, S1544 (`precheck.c`, the R-30 window beside the whole part): retired with the two-part form; control the statement rule "one run part where the link is tested". S449 (K66 whole-run block): retired with the second part. S329 (`pcrec_find_run_scan_index` data tie): kept, re-aimed at a REQ_BYTE witness (its one surviving reader). S453 (`pcrec_req_pick`'s `bytes[idx]`): re-anchored on the new REQ_BYTE text. S285 (`runcmp.c` run-pinned compare length): re-aimed at a run over 8 positions (§4.2 lengthens the pinned run) |
| K38-3 | S | the measurement card cell (§5.2) and W-K4a/W-K4b's populations over every level the U2 target table admits | the card's run record (span_cards §4) | a level that reads below its floor faults W-K4a or reds W-K4b under ASan | none |

**Order.** K38-1 after `plan_frame.md` 3.0a lands (both restructure `window.c`'s Table B rendering
and `wf_parts_prepare`; K38-1's run part renders through 3.0a's search, stream and check tables).
K38-2a after K38-1 (its lever acts on `run_decide`); its generator and oracle may start beside
K38-1. K38-2 after K38-2a, and after 3.0b (recommended: 3.0b is the nearer landing and
zero-mover; whichever lands second takes the next `MF_SITE_ABI` number and re-baselines; if K38-2
lands first, 3.0b's ASK-2 is void). K38-3 rides with K38-2 or follows it. K38-1 and 3.0b both touch
`wf_part_site`/`wf_parts_prepare`; whichever lands second rebases (a cost, not a block).

### 5.1 The numbers

- **`MF_SITE_ABI`: ONE event for Parts A and B together** (§6 Q4 RULED, with K38-2a first). The
  strong reason: `head_max` changes MEANING in Part A (K becomes position 0's offset) and TYPE in
  Part B (`int64_t`), and `omin`'s origin moves on the span Part A restates; one event states each
  member's contract once. (Re-pin cost is not the reason: plan_frame rev 2.2 §3 found no literal
  pins and G2 symbolic.) The number is the next at landing (never a literal); readers by grep
  (`git grep -n MF_SITE_ABI`, `plan_frame.md` §3's reader classes). Fallback if K38-2a cannot land
  before L2 needs Part A: A first (L2's gate), B as a second small event (L3's gate).
- **`MF_CLASS_V`: moves in the same commit.** `mf_class` gains `run` (§2.2); `mf_link.member` on
  the RUN span (`memfn.h:1147-1149`, "0, the WHOLE run tested, or 1 + the start of the one
  window") becomes UNREAD.
- **Members whose meaning moves, whose refusal moves, or that retire** `[r1 F9]`: `mf_pred.omin`
  (origin the attempt start; negative on the run span); `mf_pred.nterm` (0 is refused today,
  `memfn.h:667`, Q-G2-10: admitted on the run span, still refused elsewhere); `mf_pred`'s
  `nalt`/`alts`/`wfloor` (refused off FUNC parts today, `memfn.h:729-741`: admitted on the run's
  `pspans` entry); `mf_site.head_max` (`int64_t`; position 0's offset); the `pspans` RUN term
  (retired for the set form); `mf_pres_picks.run_scan`/`run_window` (retired: `cls.run` owns
  them; `mf_pres_ports` keeps the set, P4, P2 and landmark answers); `MF_PRES_WINDOW` (no longer a
  host-visible bound); the `pres-window` lever (retired, §4.3).
- **pcrec abi: K38-2 IS a pcrec abi event** `[r1 F8]`, with the D76/D94 ritual as its content:
  every reader of the current abi number found by grep (the `.abi` stamp, test expectations, spec
  sentences, the identity gate's (B) pin), `make test-codegen`, then the registry, codegen and
  rxtsource suites. Its populations, each counted two-sided by `emit_sweep`:
  1. **Q1, K**: DFA-route `RX_REQ_HANDOFF` and the emitted move constant on runs cut today at
     `at > 0`, each to the value the VM artifact of the same pattern already stamps
     (`(?:ab|cd)xabcdefghijkq` 7 -> 2, `\s?xabcdefghijkq` 6 -> 1, `x\wabcdefghijklmn\w+` 7 -> 2);
     the `req_landmark_maxoff`/`req_run_maxoff` listing rows on every route; NEW DFA handoffs where
     the smaller K now clears the margin row (`tuning.md` §2.41¶8a; predicted, counted).
  2. **Q2, the stamp**: `<PREFIX>_REQ_RUN` on every run over 8 positions, every route (e.g.
     `xabcdefghijkq`: `65666768696a6b71@7` -> `786162636465666768696a6b71@12`).
  3. **Q5, block names**: the whole-run route's `<p>_reqrun`/`<p>_reqrun_whole` become one part.
  4. **§4.2, the run pin**: run-pinned prefilters on runs over 8 positions.

### 5.2 What the kit measures (memory `pcrec-new-method-needs-measurement-card`)

R-38 adds no new find, scan or verify METHOD: the finds and compares are today's rows over cube
positions, and scanning a guard position is the same `find_byte` method at another offset. It
adds one CELL dimension: the per-call STEP BACK. The `enter` card (`span_cards.md`) gains cells at
step-back t in {0, 3, 8, 16, 32} bytes (re-read cost per call, find-all regime, hit-sparse and
hit-dense subjects), so a later priced row can weigh a back-reaching scan against a
consumed-position scan. Until measured the cells are visibly UNMEASURED (no decision reads them in
R-38). The first run position that is a GENERAL set (not a cube) is a new verify method (a set
test at a run position) and adds its `verify_set` card in that change, not here.

## 6. Questions: the rulings, and what remains

**RULED** (review 2026-11-09 r2 r38s, manager rulings; owner and manager answers):

1. **K becomes the run's position-0 offset: YES.** K = `whole_maxoff`, a pcrec fact stated before
   any extent exists; tying K to the kit's extent would make pcrec's handoff read the kit's method.
   No answer moves (`c` and K shift together). It unifies the engines' K: the VM attempt loop
   already stamps the whole run's offset. Movers (§5.1 item 1) `[r1 F11]`: not `xabcdefghijkq\w`
   (its DFA artifact states no handoff; its VM artifact already stamps 0; only its listing rows
   move), but DFA routes with an emitted handoff on a run cut at `at > 0`:
   `(?:ab|cd)xabcdefghijkq` 7 -> 2, `\s?xabcdefghijkq` 6 -> 1. `RX_REQ_HANDOFF` moves on runs cut
   today: spec hunk and identity record in the same change (pre-1.0 abi rules).
2. **`<PREFIX>_REQ_RUN` shows the WHOLE run with `@scan` marking the kit's scan position (b).** Not
   the verified extent: (a) had no spelling for a scan outside the extent or an empty extent, and
   made the stamp a priced, per-route method output; (b) is §12b Q3's one run value. Today's VM
   stamp (the cut window, although the whole run is compared) is fixed by it. The extent shows in
   the site's trace records, not in `--emit-facts` (D124: the listing holds no route or emission
   decision, F2).
3. **The run span's verify fact is NO: CONFIRMED.** R-38's "the verify flag as today" names the
   FIELD (D172's per-span flag), not today's value `[r1 F10]`: today's YES is stated on pcrec's cut
   window (`req_run_member`), and the RUN term carries no flag at all; YES on the uncut span would
   force a whole-run compare (movers on every run over 8 positions) and remove the kit's extent
   choice. In D187 add. 1's words: pcrec's exact finish follows, UNLESS pcrec earns the skip
   (§3.4: SUFFICIENT, OUTPUTS-DETERMINED, and the reply verifies the whole run).
4. **Parts A and B in one `MF_SITE_ABI` event: YES, with K38-2a first** (§5.1).
5. **One run part instead of two: ACCEPT the block-name movers**, counted two-sided, in K38-2's abi
   event. Conditions: the one part exists only where the run's link is tested (none under P2); its
   name never encodes the extent (else the next extent change is a name mover again). A pcrec
   name-id convention for "window" vs "whole" would state the kit's layout (D157).
6. **Where pcrec asks: `src/gen`, at pre-check site construction** (F2; reverses rev 0's facts-side
   hook). §2.2. **Answer to the review's SEAM-7 PLAN item** (is K38-2's entry the general form?):
   K38-2 adds NO entry. The run's reply is part of the pre-check site's class from `mf_ask`, the
   existing pure phase-1 query, so there is no third phase-1 entry to unify. The general form the
   review names (one statement-level `mf_wdecide` over any window statement, its reply
   `mf_wreply`'s run triple) stays a noted unlock, each with its trigger: (1) one member rule for
   the pre-check and the prefilter window site (§2.5), trigger: K38-1's caller check finds a
   compile where the two members differ for the same run position; (2) a verified extent per
   set-member span, trigger: [MATCH-KNOWN]'s prefix-skip build or the set-side change (§6 P3); (3)
   one serialized reply record for the plan-as-text seam, trigger: `plan_frame.md` 3.0b lands.

**OPEN for main** (each with a recommendation):

7. **What `<PREFIX>_REQ_RUN` shows where no run part renders** (P2 `dominated`, `cover`, or no
   pre-check site asked). Ruled (b) needs a spelling with no kit scan. **Recommend**: the whole run
   with no `@` (a stamp grammar change in §4.4's `match_api.md` §6.3.7¶7 hunk), rather than a scan
   the kit chose for a part it never renders. And the `--emit-facts` `req_run` row, which then
   equals `req_whole_run`: **recommend** retiring it into `req_whole_run` (one run value) in the
   same hunk.

**PLAN items for main** (from the review, recorded so they are not lost):

- P1 (F1): name the unit that builds the earned skip (span_arms L2's amended text is the natural
  home), with the SUFFICIENT fact's producer, the OUTPUTS-DETERMINED fact, the call-mode clause and
  the witnesses of §3.4 and C1's skip half.
- P2 (F10): record R-38's three readings in its response: `maxoff` not stated (trigger D176 Q4),
  the verify FIELD carried with value NO, "least occurrence" as "least candidate".
- P3 (F9): a plan row to unify set-member presence spans as 1-position wspans, so `pspans` spells
  one span kind one way (after K38-2 the run crosses through `alts[0]`, the set members through a
  SET term). Trigger: [MATCH-KNOWN]'s prefix-skip build or the set-side change.
- P4 (F5): drop `match_api` §6.3.7¶5/¶7/¶11 and findings.md §4's window row from span_arms L2's
  CHECKED-UNCHANGED list; K38-2 owns those hunks.

## 7. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT, for §5.2's cells only.** No decision in R-38 reads a measured
   number beyond today's rates (K38-1 reproduces today). The step-back cells are per-call cost in
   a find-all regime, Linux dev box, `taskset`-pinned, both layers, hit-sparse and hit-dense; the
   first priced row that reads them names its own regime. A different regime cannot flip an R-38
   decision because none is priced.
2. **Independent control: RELEVANT.** §2.4's C1-C4: libpcre2's answers and the G2 family's
   occurrence oracle (written from the contract text, D27), the rendered text, and the artifact
   text, none of them the decision function; C3 shares it by design and is named so. Each control
   names the unit where its witness first reaches (C1's skip half only at the skip's unit; C2 and
   the G2 forms of W-* at K38-2a/K38-2; C4 at K38-2 under the all-tie regime and the probe lever).
   Population counts: §5.1's four populations counted two-sided by `emit_sweep` (pcrec's artifact
   diff, never the kit's `moved`, K35); the prefilter window site's run member counted as a run
   decider (§2.5). Existing sabotages each have a stated fate (§5).
3. **What moves when data is regenerated: RELEVANT.** The scan and the extent read the art's
   rates and measure set, so a regenerated measure set or rate table can move `scan`, hence
   `REQ_RUN`'s `@scan` and the emitted find: an abi event (`integration.md` §21.3), as today for
   the run member. It can also split `<PREFIX>_REQ_BYTE` from `@scan` on unextended runs (§4.1);
   no contract sentence ties them after K38-2. The step-back cells move no byte until a priced
   row reads them.
