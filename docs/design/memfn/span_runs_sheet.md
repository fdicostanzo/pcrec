# span_runs_sheet — R-38's interface sheet: the necessary run as one uncut span (design, rev 0)

Lane r38s, 2026-11-09. DESIGN ONLY: no code, no build go. It answers R-38 (`memfn/docs/requests.md`
on main, "R-38"), the kit request of `docs/design/span_arms.md` rev 2.2 §8.2 AS AMENDED by the
owner's rulings §12a (2026-11-08) and §12b (2026-11-09), and D191. Where §8.2 and §12a differ,
§12a wins, and this sheet follows it: nothing about consumption crosses (no `cons` at the seam),
the run is never cut by pcrec, and the scan position and verify extent are ONE decision, the
kit's.

Base: the joint U2+U3 tree (lane/u3mech 404cff6ea, `MF_SITE_ABI` 26 in `memfn/include/memfn.h`).
The newer design text is read from main (`span_arms.md` rev 2.2, R-38, D191) and from
lane/memfn-s30a (`plan_frame.md` rev 2.2). File:line cites are at this base.

What is the seam's and what is the kit's. Sections 2-4 are the SEAM: facts pcrec states, facts
pcrec reads back, and the contracts both rely on (D157: facts, never a method). Section 5 is the
KIT'S OWN build sketch, marked as such; its method choices are not questions. Section 6 holds the
open questions for main and Frank.

## 1. Goals

Ranked; a higher goal wins a conflict.

| # | goal (who benefits) | measurable form |
|---|---|---|
| 1 | **One statement, one decision** (pcrec's L2/L3 lanes; the next editor of either side) | the run crosses the seam ONCE per compile, in set form (D187), and exactly ONE kit function decides its scan position and verified extent. `grep` finds no pcrec computation of a run scan index on the member path, and the kit's decider census names one run decider. Today there are three deciders (`pcrec_find_run_scan_index`, the window family's `run_member`, presence's P3) and two agreement checks |
| 2 | **No answer changes; the seam unit moves only named bytes** (every user) | answer identity against libpcre2 over the corpus on every `--memfn=` deny arm and both SIMD layers. `emit_sweep` byte-identical at the seam unit except the populations §6 names (each counted, two-sided) |
| 3 | **pcrec can build L2 and L3 against this sheet without asking again** (the L2/L3 build lanes) | every field pcrec states or reads has its type, home, value range, none state and meaning here; every pcrec reader of the reply is named (§4) |
| 4 | **The step back is sound and bounded** (users of lookbehind patterns; a find-all caller paying it per call) | no read below subject offset 0 or at or past `n` on any layer or target (a guard page below offset 0 in G2, ASan); the step back per call is at most `lb_bytes` (pcrec's cap) |

**Non-goals.** Any priced row (span_pick stage 3). Which positions the run CONSUMES (pcrec's own
fact; nothing about it crosses). [MATCH-KNOWN]'s prefix-skip build (it will read §3.2's fact; no
build here). Cutting, splitting or windowing the run on pcrec's side. A second wider run beside
the run (§12b Q3: one value). A set-side change: the one-byte landmark and its agreement check in
`req_site_define` (`emit_dfa.c:1576-1580`) stay as they are.

## 2. Part A: the run as ONE uncut span

### 2.1 What pcrec states

The run is a presence span of the pre-check site, as today (`mf_site.pspans`, the run last), but
its positions now cross in SET form as one D172 span, and it is the ONLY place the run crosses.

The seam stays D172's LIST of span statements, and every other span of the list is unchanged. "One
uncut span" (R-38, as clarified by main 2026-11-09) means only that the necessary run is ONE entry of
that list, never cut by pcrec into a window or into several pieces.

| fact | where it lives | type | value |
|---|---|---|---|
| the run's positions | the run's `pspans` entry, through the `mf_pred` window-statement members that today serve only FUNC parts: `nalt` 1, `alts[0]` = {`entry` `MF_ENTRY_NONE`, `nspan` 1, `spans[0]`}, `wfloor` `MF_WFLOOR_SUBJECT` | `mf_wspan` | `start` 0 (positions are relative to the occurrence's position 0), `len` n (2..`MF_WSPAN_POS`), `set[j]` position j's byte set (256-bit, D187; a cube is never stated beside it), `table_ref[j]` 0, `core` STATED over all n positions (every successful attempt holds every position inside the subject), `verify` per §2.5 |
| no RUN term | the same entry | — | `nterm` 0. The `MF_T_RUN` term with its `run`/`mask` arrays leaves `pspans` (a cube shape, which D187 retires at the seam). Set-member spans keep their one SET term |
| placement | the same entry's `omin` | `int32_t` | the smallest offset, from the ATTEMPT start, at which the occurrence's position 0 can lie. Part B (§3) widens its sign |
| need, class | the same entry | as today | `need` per route (REQUIRED where no DFA scan fronts the route), `span_class` `MF_SPAN_PRESENCE`, `member_order` 0 |
| the run part | the pre-check's `preds[]` | `mf_pred` FUNC part | ONE run part (`fn_ref` its name id) with NO window statement of its own (`nalt` 0): the kit derives the part from the run's presence span. pcrec no longer states [K66]'s second whole-run part (`req_run_tests`'s `t[1]`); "whole or not" is the kit's verified extent (§2.3). `ret_pred` names the run part where the site ASSIGNs its landmark, as today |

- **No maxoff crosses.** The only reader of the run's largest offset is the landmark, and that
  is `head_max` (K, §3.2). No other field is added (memory `pcrec-no-silent-defaults`; D157).
- **No cut.** pcrec states the whole stored run, every position its analysis holds. The length
  bound is `MF_WSPAN_POS` (32), DERIVED from `MF_MAX_TERM`, which equals the analysis bound
  `PCREC_MAX_REQ_RUN_SCAN` (32, `src/core/limits.def`). TOP's extensions are clipped at the
  stored bound (span_arms §5.2 TOP), so the bound holds; pcrec asserts `n <= MF_WSPAN_POS` where
  it states the span. `PCREC_MAX_REQ_RUN_EMIT` stops shaping what the kit sees. Any length limit
  on what the kit verifies is the kit's own priced choice.
- **Why the presence span and not a window site.** The run's attempt-relative placement (`omin`,
  and K) already lives on the presence statement. Today the run crosses TWICE: as the presence
  RUN term and as a fabricated window site (`req_run_member`, `emit_dfa.c:1058-1076`). Keeping the
  presence span and giving it the window span's set form makes it once.

### 2.2 The entry pcrec calls at fact-derivation time

A NEW pure entry, beside `mf_wdecide`:

```
#define mf_run_decide MF_NS(run_decide)
typedef struct {
    uint8_t scan;      /* the run position (0..n-1) the kit's search finds first           */
    uint8_t ver_lo;    /* THE VERIFIED EXTENT: positions [ver_lo, ver_lo + ver_len)         */
    uint8_t ver_len;   /*   every candidate the kit yields is PROVEN to hold, each against  */
                       /*   its whole set (§3.2 of this sheet); 0 = none proven             */
} mf_run_reply;
int mf_run_decide(const mf_art *, const mf_pred *run, const char *opts, mf_run_reply *out);
```

- **Input.** `run` is the run's presence span exactly as §2.1 states it, the SAME object pcrec
  later places in `pspans`; `opts` is the `--memfn=` string pcrec gives every site (`mf_site.opts`,
  `memfn.h:785`). The art supplies the rates, the measure set, the denies, the layer and the
  target list.
- **Contract.** Pure, as `mf_wdecide` is (span_pick D186 add. 2): no text, no handle, no art
  state, no trace record. `*out` is zeroed whole first, on every return. It returns -1 exactly
  where the define would refuse the span (`kit_presence_check`'s rules for a run span). The
  decision reads ONLY the span, the art and `opts`: never `handoff`, `head_max`, the set-member
  spans or `pres_proof`. So the reply pcrec reads at fact time is, by construction, the decision
  the pre-check's define renders later for the same span on the same art.
- **Why a new entry, not an existing one.**
  - `mf_wdecide` decides a SITE's window statement: its alternatives, entry, floor and a FIND
    candidate. Asking it about the run means stating the run a second time as a window site
    (today's `req_run_member`), which is the double statement this request retires. Under
    `plan_frame.md` 3.0b it also carries a frame and a call kind, which the run does not have.
  - `mf_pres_ports` answers a whole presence SITE: set picks, P2's proof, and the landmark
    admission, which reads `handoff` and `head_max`. pcrec decides those (`req_use`, the
    handoff's K) AFTER fact derivation, from facts this reply feeds. Asking the ports at fact
    time would either state values that are not yet known or make the decision depend on them.
  - The run decision depends on neither. So the entry takes exactly what it reads. Inside the
    kit it is a thin face over the ONE function the PRES rows and the run part's rendering call
    (§5, K38-1). It is not a second decision.
- **pcrec's call site** (pcrec-side, named for main; not the kit's): the facts derivation that
  today cuts the window (`pcrec_req_window`, `src/facts/req.c:826-858`) asks `mf_run_decide`
  instead and stores the reply in the run fact. That needs the Job's art at fact time:
  `pcrec_memfn_art` already begins it lazily per Job, with the measure set and analysis built
  eagerly by `compile_driver` (`src/gen/memfn_sites.c:183-212`). Reaching it from `src/facts/`
  is a layering question for main (§6 Q6).

### 2.3 The kit's reply: ONE decision

- `scan` and `[ver_lo, ver_lo + ver_len)` are one decision, over ANY run position, consumed or not
  (§12a: "the scan bytes should come from any span position"). The kit may scan one position and
  verify any contiguous stretch, the whole run included, or verify nothing beyond its find.
- `scan` need not lie inside the verified extent (a scan by a lossy cover is not a proof).
- The reply describes EVERY text the kit may render for this span on this art: each SIMD layer,
  and each target in the art's list (U2/U3). A form that would prove less than `ver_len` on some
  variant is either held to it or reported at the minimum. This is stronger than `plan_frame.md`
  §2.3's stated gap (the frame part names the OFF variant only), and it must be: pcrec's earned
  skip (§3.4) drops its own finish on the reply's word.

### 2.4 Which agreement checks retire, and what replaces their control

| today's check | where | what it holds equal | fate |
|---|---|---|---|
| `req_run_member`'s "internal error: the window family's run member N is not the run window's own index" | `src/gen/emit_dfa.c:1058-1076` | pcrec's `r->idx` (`pcrec_find_run_scan_index`) and the window family's member over pcrec's fabricated run-window site | RETIRES with the function: pcrec has no index of its own. Every reader (`req_run_tests`, `req_note_run`, `req_set_leads_own`, `req_pick_shadow`, both stamps) reads the fact-time reply. `plan_frame.md` §4.2's ASK-2 (this call with call NONE) has nothing left to change |
| `pres_layout_check`'s RUN half | `memfn/src/compose.c:704-718` | P3's `run_scan` inside the window, and the run part(s) equal to pcrec's window (`part_is_run`: bytes, mask, `plan_pos`, length) and to the whole run | RETIRES: pcrec lays out no run window. What STAYS is a statement rule, not a pick agreement: exactly one run FUNC part where the run's link verifies, at its chain order, stating no window of its own |
| `pres_layout_check`'s head and rest halves | `compose.c:697-703`, `:719-729` | set members | unchanged (out of scope) |

**The replacement controls** (`docs/dev/learnings.md` §3: a control must not share a source with
the thing it controls). The retired checks compared two deciders; with one decider, an equality
between its own outputs would share its source. So each control below reads an INDEPENDENT source.

| # | what is controlled | checked against (the independent source) | witness and plant |
|---|---|---|---|
| C1 | the kit's candidates are sound: no occurrence lies in `[floor, c)` (§3.3) | libpcre2's answers (the corpus, `make test-axes` on every deny arm, both layers) | a plant that reports `ver_len` one larger than the text verifies, on an earned-skip witness (§3.4: `bar(?=baz)` on `barbaq barbaz`, expected (7,10)): pcrec skips its finish at `barbaq` and answers (0,3). A plant that scans from `lo` instead of the floor: W-L1 (§3.5) |
| C2 | the reply describes the text | the RENDERED TEXT, classified by G2 (the run part's find byte is `scan`'s set; its compares cover exactly `[ver_lo, ver_lo + ver_len)`), the `plan_frame.md` Goal 2 pattern: the expectation is read off the define's output, not off the decision function | a plant in the decision function that answers `ver_len` + 1 while the renderer renders the old extent: G2 red |
| C3 | the fact-time reply equals the define's decision | the purity harness: `mf_run_decide` interleaved with defines, whole-reply `memcmp`; and a trace-build re-ask at the pre-check's define, as `plan_frame.md` Goal 2's kit-side check | shares the function BY DESIGN (it proves purity, not correctness; C1 and C2 cover correctness). Plant: a static counter that the decision reads; the harness reds |
| C4 | pcrec reads the reply at every reader (no reader keeps its own pick) | the ARTIFACT TEXT: a pcrec codegen check that `<PREFIX>_REQ_RUN`'s `@idx` names the position whose set the emitted find scans | a pcrec plant that feeds one reader (the stamp) `pcrec_find_run_scan_index`'s index. It reaches its site only where the two rules differ: `bar(?=baz)` from L2 on; at the seam unit, the kit's test-only lever (`mf_lever`, a reversed tie) supplies the difference |

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
- **The assigned value's meaning** (new, stated explicitly): where the site ASSIGNs its landmark,
  the value is the position of the occurrence's position 0, whatever stretch the kit verified or
  scanned. Today it is "where the run window begins". The window cut retires, so the landmark is
  the run's position 0 and K is that position's offset (§6 Q1: K stops depending on a cut).
- **None state: the kit's, unchanged.** `head_max` is read only where `handoff == MF_H_ASSIGN`,
  and is 0 (refused otherwise) elsewhere. A signed 0 on an ASSIGN site is a STATED K of 0. pcrec
  keeps its own stated/none bit for K (span_arms §8 L3), which never crosses.
- **The twin admission.** The kit's landmark port (`presence.c:199-222`, today
  `unsigned long long k = s->head_max`) reads K signed and admits by `max(K, 0)`: a landmark that
  begins at or before the attempt start costs no step back. That equals pcrec's margin
  `pcrec_landmark_margin` at `max(K, 0)`, which `req_pick_shadow`'s `landmark` record compares.
  Its mass term reads the reply's verified extent instead of P3's 8-position window (one decision).

### 3.3 The occurrence contract, at entry and at re-entry

With `origin` the attempt start (entry: `search_from`; re-entry: the hook's `lo`) and
`floor = max(0, origin + omin)`, computed with no unsigned wrap:

1. **Candidate floor.** Every candidate `c` the run part yields (and ASSIGNs) satisfies
   `floor <= c`.
2. **Least.** No occurrence of the WHOLE run (every position in its set) has its position 0 in
   `[floor, c)`. A miss means no occurrence has its position 0 at or after `floor`.
3. **Exact where verified.** Every yielded `c` holds every position in
   `[ver_lo, ver_lo + ver_len)`. Where that is the whole run (`ver_lo` 0, `ver_len` n), `c` IS the
   least occurrence at or after `floor`, the contract R-38 names.
4. **Reads.** Every read lies in `[0, n)`. The candidate floor is below `origin` when `omin < 0`;
   the read floor is the subject's 0 (`integration.md` §14.7's `floor` rule, with `floor` the
   SUBJECT). No text may assume reads at or above `origin`.
5. **Re-entry** is the same contract with the re-entry's `lo` as origin. pcrec's move after it,
   `max(posvar, c − K)` with K signed and no `size_t` wrap, is pcrec's (span_arms §5.4 A3, §8.1).

`floor` is the kit's text (span_arms §8.1: not a pcrec call site). Its spelling must not wrap:
`lo + omin` in `size_t` with `omin < 0` and `lo < -omin` gives a huge floor and a false NOMATCH
(the plant of §5's W-K1).

### 3.4 What pcrec does with the verified extent (use, not method)

- **The earned skip** (D187 add. 1; §12a "validate the entire span and finish"). Where pcrec's own
  facts say the run is the WHOLE attempt, exact and at a fixed placement (`omin` equals the
  run's largest offset, and the attempt holds no condition beyond the run's positions), and the
  reply says `ver_lo` 0, `ver_len` n, pcrec reports the hit as the match without its finish:
  the attempt start is `c − K`, and the match bounds are pcrec's consumed offsets from it. The
  kit is told nothing about consumption, and that the skip happens at all.
- **[MATCH-KNOWN]'s prefix skip** (D142, D191 item 4) reads the same fact later. No build here.
- **The stamps and the listing** read `scan` and the extent (§4).

### 3.5 Part B's witnesses (answers measured with libpcre2 by the build)

| id | plant | pattern / subject | fails how |
|---|---|---|---|
| W-L1 (span_arms §5.7, the kit's) | the run part scans from `lo`, not `floor` | `(?<=foo)bar` from 3 on `foobar`: (3,6) | the scan from 3 misses `foobar`: NOMATCH |
| W-K1 (new) | `floor` spelled `lo + omin` in `size_t`, no clamp | `(?<=foo)bar` from 1 on `foobar` (`lo` 1 < 3 = `-omin`): (3,6) | the floor wraps to about 2^64: NOMATCH |
| W-K2 (new, re-entry) | the re-entry floor read from `lo` | a re-entry witness of span_arms W-L14's shape, the kit's half | the re-ask misses an occurrence below `lo` that a later attempt needs |
| W-K3 (new, twin) | the twin admission reads K unsigned | any L3 pattern whose K is negative on an ASSIGN site (span_arms W-L13's `(?<=foo)bar(\w)\1`) | the twin declines while pcrec's margin admits: `req_pick_shadow`'s `landmark` record disagrees |
| W-K4 (new, below-zero reads) | a vector form reads its block aligned down from `floor` | a G2 site with the subject at a page start, a guard page below offset 0, `omin` −8..−32, every admitted level of every target in the art's list (U2) | a fault (G2) or an ASan report |

pcrec states no negative `omin` before L3, so W-K1..W-K4 are G2 witnesses at the seam unit
(G2's generated presence space grows a negative `omin` and a signed K), and pcrec-driven again at
L3.

## 4. What pcrec reads (and where)

| reply member | pcrec reader | today's source it replaces |
|---|---|---|
| `scan` | `<PREFIX>_REQ_RUN`'s `@idx` (`pcrec_fact_stamp_req_run`, `src/facts/facts.c:911-917`), `--emit-facts`' `req_run` row, `req_note_run`, `req_set_leads_own`, `req_pick_shadow` | `ReqRun.idx` (`pcrec_find_run_scan_index`) through `req_run_member` |
| `ver_lo`, `ver_len` | the `req_run` row and stamp's shown stretch (§6 Q2); the earned skip (§3.4); [MATCH-KNOWN] later | `ReqRun.at`/`len`/`bytes` (pcrec's cut window) |
| the assigned `c` | `emit_req_handoff_rest`, `emit_req_landmark_move` (pcrec's move, K signed) | the window's begin |
| none | `<PREFIX>_REQ_BYTE` | stays PCREC'S pick among CONSUMED positions (§12a, D191 item 2): a byte every match consumes. It no longer copies the scan pick, so where L2/L3 extend the run the two may differ (`bar(?=baz)`: scan maybe `z`, `REQ_BYTE` among `bar`) |

pcrec's facts keep the reply in the run fact (names are pcrec's; e.g. `ReqRun.scan`, `ver_lo`,
`ver_len`), and `ReqRun.idx`/`at`/`bytes`/`len` retire with the cut. The prefilter's own window
statement (`pf_window_of`, `ofs_window_of`) is a different site with its own reply
(`mf_wreply.run_member`/`run_lo`); it states the run positions pcrec's pin proves, from the whole
run, and is unchanged by this sheet except that it no longer reads the cut window (span_arms A5).

## 5. Kit-side build sketch (THE KIT'S; not a question)

Sabotage ids are taken at build time from the top of the free range. Every heavy run is a
boxqueue job. Sizes: S under a day of lane work, M a lane, L a lane plus a fix round.

| unit | size | content | check | the plant that makes it fail |
|---|---|---|---|---|
| K38-1 | M | ONE run decision inside the kit, NO seam move: P3's run scan and window, the whole-run keep (P0/P9), the window family's member for pre-check run parts and the twin admission's mass term all call one function `run_decide(rates, opts, span) -> (scan, ver)`; its first rule REPRODUCES today (the incumbent: `kit_run_member`, today's P3 window, whole under P0/P9) | `emit_sweep` byte-identical on every arm (default, each `--memfn=no-X`, `--engine=vm`, both layers); `decider_census` names one run decider; REACH equality | a plant in `run_decide`'s tie moves BOTH the presence layout and the part's text together (before K38-1 the same plant in one reader fired `pres_layout_check`); a plant that leaves one reader on its old pick turns `decider_census` red |
| K38-2 | L | THE SEAM EVENT, Parts A and B together: §2.1's statement form (pspans run in set form, `nterm` 0, the run part with no window), `mf_run_decide` and `mf_run_reply`, `omin < 0` admitted on the run span, `head_max` `int64_t`, the floor `max(0, lo + omin)` at entry and re-entry, the twin admission at `max(K, 0)`, the run part derived from the span, the retired members (§5.1), the refusal texts. pcrec's same-commit hunks: `req_pres_spans` states the new form (`omin` 0 and K >= 0: no extension yet), facts ask `mf_run_decide`, `req_run_member` and the cut retire, every reader of §4 reads the reply | C1-C4 (§2.4); G2's presence space with negative `omin` and signed K, both layers; W-L1 and W-K1..W-K4 (§3.5); `emit_sweep` zero movers except the named populations (§6 Q1, Q2, Q5), counted two-sided | as §2.4 and §3.5 |
| K38-3 | S | the measurement card cell (§5.2) and W-K4's guard-page population over every level the U2 target table admits | the card's run record (span_cards §4) | a level that reads below its floor faults W-K4 |

Order. K38-1 after `plan_frame.md` 3.0a lands: both restructure `window.c`'s Table B rendering and
`wf_parts_prepare`, and K38-1's run part renders through 3.0a's search, stream and check tables.
K38-2 after 3.0b (recommended): 3.0b is the nearer landing and zero-mover; whichever lands second
takes the next `MF_SITE_ABI` number and re-baselines. If K38-2 lands first, 3.0b's ASK-2 is void
(the call it edits is gone). K38-3 rides with K38-2 or follows it.

### 5.1 The numbers

- **`MF_SITE_ABI`: ONE event for Parts A and B together** (the kit manager's leaning; this sheet
  agrees). Both parts change the same members (the run's `pspans` entry, `omin`'s refusal,
  `head_max`'s type) and the same refusals; L3 needs both and L2 needs A; B's kit work is the
  floor arithmetic and the twin's sign, small beside A. Two events would re-pin the same readers
  twice. The number is the next at landing (never a literal); readers by grep (`git grep -n
  MF_SITE_ABI`, `plan_frame.md` §3's reader classes).
- **`MF_CLASS_V`: moves in the same commit.** `mf_link.member` on the RUN span (`memfn.h:1147-1149`,
  "0, the WHOLE run tested, or 1 + the start of the one window") retires to 0: the extent is the
  run reply's.
- **Members whose meaning moves or that retire**: `mf_pred.omin` (origin the attempt start;
  negative on the run span), `mf_site.head_max` (`int64_t`; position 0's offset), the `pspans`
  RUN term (retired for the set form), `mf_pres_picks.run_scan`/`run_window` (retired: the run
  reply owns them; `mf_pres_ports` keeps the set, P4, P2 and landmark answers), `MF_PRES_WINDOW`
  (no longer a host-visible bound: "pcrec asserts its own equal" retires with pcrec's cut).
- **pcrec abi**: an abi event in the same commit only if a pcrec byte moves (§6 Q1, Q2, Q5's
  populations); with the movers all ruled away, none.

### 5.2 What the kit measures (memory `pcrec-new-method-needs-measurement-card`)

R-38 adds no new find, scan or verify METHOD: the finds and compares are today's rows over cube
positions, and scanning a guard position is the same `find_byte` method at another offset. It
adds one CELL dimension: the per-call STEP BACK. The `enter` card (`span_cards.md`) gains cells at
step-back t in {0, 3, 8, 16, 32} bytes (re-read cost per call, find-all regime, hit-sparse and
hit-dense subjects), so a later priced row can weigh a back-reaching scan against a
consumed-position scan. Until measured the cells are visibly UNMEASURED (no decision reads them in
R-38). The first run position that is a GENERAL set (not a cube) is a new verify method (a set
test at a run position) and adds its `verify_set` card in that change, not here.

## 6. Open questions for main and Frank (each with a recommendation)

1. **Does K become the run's position-0 offset?** With no cut, the landmark the kit assigns is the
   occurrence's position 0, and K its largest offset (the whole run's, `whole_maxoff`), no longer
   the window's (`omin + at`). The move `max(posvar, c − K)` lands on the same position (both `c`
   and K shift by `at`), so no answer moves, but the stamp `RX_REQ_HANDOFF`, the listing's
   `req_landmark_maxoff` and the margin admission's K move on runs pcrec cut today
   (`xabcdefghijkq\w`: `req_run 65666768696a6b71@7` at `at` 5, K 5 today; K 0 after, measured on
   main's binary). **Recommend yes**: tying K to the kit's extent would make pcrec's handoff read
   the kit's method, and position 0 is stated before any extent exists. The margin movers are a
   decision change counted at the seam unit.
2. **What does `<PREFIX>_REQ_RUN` (and the `req_run` row) show?** (a) the verified extent with
   `@` the scan inside it, or (b) the whole run with `@` the scan. **Recommend (a)**: the stamp
   says what the artifact proves; on every route where the kit keeps today's 8-position window it
   is today's value. It moves where the kit verifies the whole run (the whole-run route: VM
   attempt routes and `--memfn=no-fd-pres-pick`, runs over 8 positions), a counted population.
   (b) moves every run over 8 positions.
3. **The run span's verify flag is NO.** R-38 says "the verify flag as today", but today's run
   part window states YES, and YES forbids the kit's choice of extent (§12a gives the kit that
   choice). NO is D187 add. 1's DOWN fact: pcrec's exact finish follows, except where the reply
   earns the skip. **Recommend: confirm NO.**
4. **Parts A and B in one `MF_SITE_ABI` event** (§5.1). **Recommend yes** (the kit manager's
   leaning). Consequence: L2 waits for B's kit work too, which is small.
5. **One run part instead of two.** The whole-run route's two blocks (`<p>_reqrun`,
   `<p>_reqrun_whole`) become the kit's one part. Its block names move unless pcrec's name hook
   hands the kit a second name. **Recommend accepting the name movers** in the seam unit's abi
   event over a pcrec name-id convention that presumes the kit's layout (D157).
6. **Layering of the fact-time call.** The facts module (`src/facts/`) must reach the Job's art
   (`src/gen/memfn_sites.c`). **Recommend** a facts-side hook to `pcrec_memfn_art`, set by the
   compile driver; the art is per Job and its inputs are built before facts are derived. pcrec's
   call, named so L2/L3's lane does not discover it.

## 7. The three standing questions (`docs/design/CLAUDE.md`)

1. **Measurement regime: RELEVANT, for §5.2's cells only.** No decision in R-38 reads a measured
   number beyond today's rates (K38-1 reproduces today). The step-back cells are per-call cost in
   a find-all regime, Linux dev box, `taskset`-pinned, both layers, hit-sparse and hit-dense; the
   first priced row that reads them names its own regime. A different regime cannot flip an R-38
   decision because none is priced.
2. **Independent control: RELEVANT.** §2.4's C1-C4: libpcre2's answers, the rendered text, and
   the artifact text, none of them the decision function; C3 shares it by design and is named
   so. Population counts: the movers of §6 are counted two-sided by `emit_sweep` (pcrec's
   artifact diff, never the kit's `moved`, K35). Each witness of §3.5 names its plant and must
   reach its site; C4 reaches only where two rules differ, so its seam-unit form uses the kit's
   test-only lever.
3. **What moves when data is regenerated: RELEVANT.** The scan and the extent read the art's
   rates and measure set, so a regenerated measure set or rate table can move `scan`, hence
   `REQ_RUN`'s `@idx` and the emitted find: an abi event (`integration.md` §21.3), as today for
   the run member. The step-back cells move no byte until a priced row reads them.
