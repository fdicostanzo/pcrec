# kit_proof — [KIT-VERIFY] U1: REPORT WITHOUT AN ENGINE, with D161 addendum 16's context spans

Status: DESIGN NOTE, revision 1 (lane `u1design`, 2026-10-18, main `a016b3bfa`, abi 80,
`MF_SITE_ABI` 16, `MF_CLASS_V` 3). Nothing under `src/` or `memfn/` changes. A critic panel
follows; each section ends with "where to attack".

Evidence: single-pattern `build/pcrec` compiles at main `a016b3bfa`, one SIZE-ONLY hand
twin (`kit_proof/cover_twin.py`), and the committed kvcensus run (`docs/dev/kvcensus.md`,
`docs/dev/kvcensus/tables.md`; recounted by kind and groups in `kit_proof/counts.py` →
`kit_proof/counts.txt`). Nothing was timed.

Inputs: D161 addenda 4-16 (16 is the ruling this implements), D157, D158; review r2
(`docs/dev/reviews/2026-10-18-r2-kitverify-proof.md`), whose critics' findings bind this
design and are cited by id (`kvp-cost`, `kvp-contract`, `kvp-unlock`); `window_contract.md`
§2-§4 and T-NEED/T-PROOF (§9); `r17b_prime.md` §4.3-§4.6; `locate_finish.md` §1-§2, §5.1;
plan rows [KIT-VERIFY] and [MATCH-KNOWN]; memfn R-25.

---

## 0. Answers first

| question | answer |
|---|---|
| what U1 is | a search whose kit site PROVES the whole sub-problem at every candidate it yields returns the first candidate as the match, with no DFA, no start recovery and no handback (§1) |
| where it sits | ONE new LOCATE row, `cover`, between `rev-end` and `composite`. It hands `SPAN`/`NOMATCH`, which the EXISTING `FIN2 report`/`FIN1 nomatch` finish. There is no new FINISH row. T-PROOF stops being a table of its own: its rows become `cand_rows[]` members that share one deny, `-fno-kit-proof` (§2.1) |
| what the entry loses | the forward machine's tables and scan loop, the start recovery (`end-minus-width`, the reverse pass and its machine), the K82 handoff and any pre-check. `foobar`'s hand twin: `.text` 2,047 → 1,425 B, `rx_search` 100 → 61 instructions (SIZE ONLY, §2.3) |
| stage 1 population (native) | DFA-finisher artifacts with a kit site at the match start: **71 bench / 686 corpus** sites (`counts.txt` A). Context spans add **6 / 84** DFA patterns, among them `(?m)…$`, which the census had counted as an end anchor (§3.4). Out of stage 1, counted: hybrids 6 / 225, VM 0 / 39, VM-context 4 / 23, and anchored or end-pinned bodies with no kit site 11 / 185 (§1.2) |
| the `\b` rewrite | NOT a rewrite in the lowering. It is READ off the route's anchored machine: its seed table (what precedes the origin) and its class-indexed accept (what follows the end). That reading is the positional rewrite, computed from the same machine the engine runs, so it is an equivalence by construction. Its control is libpcre2 (§3) |
| facts pcrec states (R-26) | on span 0: `prefix_stated`, `exact_len`, `consumable_len`. On a CONTEXT span: `absent` and `consumable`. On the site: `site_kind = REPORT` (new) and `span_lo` = 0 as the read floor. Every enum has an UNSTATED zero that is refused where read (§4) |
| what the kit returns (R-26) | `mf_class.proven[d]` for every origin offset `d` in `[-MF_MAX_BACK, MF_MAX_FWD)`, generalising `proven0` (`d` = 0) and `proven_prev` (`d` = -1). Layer-invariant, deny-variant (§4.2) |
| the helper | `pcrec_known_derive`, the first member of [MATCH-KNOWN]. It takes pcrec's language facts and the kit's sets and returns `prefix`, `cover`, `suffix_lo` and the context verdicts. `cover`'s predicate is its one reader in U1 (§5) |
| events | Z0 R-25 (kit, 0 movers), then Z1 R-26's layout with today's facts stated (one `MF_SITE_ABI` event, 0 movers), then Z2 the producer, helper and row, routed only in the trace build (0 movers), then **B1, the one byte-moving event**: pcrec abi +1 together with the kit's proving text, one flag bit, stamps, spec hunks and the bench inbox note (§6, §7) |
| questions for Frank | Q1 captures (stage 1 is DFA-only), Q2 is `cover` source-neutral, Q3 is the `\b` reading acceptable as his "rewrite", Q4 one family deny vs one per row (§8.4) |

---

## 1. WHOLE-COVER

### 1.1 The definition

A kit site's sub-problem is **WHOLE-COVERED** at a candidate `c` when every condition
below holds. pcrec decides all of them at compile time; none is decided per call.

1. **Origin = the match start.** The site's origin is the match start (`head_max` 0, T-CUT
   `segment-0` with no head). Excluded are the census's 288 `scan-restart` sites (span 0 is
   a context byte, or the byte the reverse pass walks back from; kvcensus §0) and the
   `landmark` and `presence` origins (`head_max` > 0, or no span 0). The consumer must not
   recover anything (`window_contract.md` §2.1: "no head pcrec cut off").
2. **A fixed-width, exact language.** The sub-problem's language `L` (read off the route's
   anchored machine, §1.5) is a set of strings of one width `k`, with `1 ≤ k ≤
   MF_MAX_SPAN_POS` (32). It equals the cross product `S_0 × … × S_{k-1}` of its
   per-position byte sets, so `exact_len = k` for THIS artifact's encoding (kvp-contract S1:
   exactness is a property of a prefix and is per encoding; 65 patterns differ only under
   `-e utf8`, kvcensus §4). The census's leftmost-first shapes qualify: `in|instanceof`
   (`k` = 2), `/user|/users` (5), `\.tar|\.tar\.gz` (4), `foo|foobar` (3). For each of them
   the anchored machine kills the longer arm at `k`, so priority decides the end at
   compile time.
3. **Accept at exactly `k`, nothing after.** No row reached at a depth `d < k` accepts, and
   every row reached at depth `k` accepts with no live successor. So the end is `c + k`
   and there is no other priority end (O2). `abc|ab` fails this: at depth 2 the `ab` arm
   accepts while `c` is still live.
4. **The kit proved it.** For every `d` in `[0, k)`, `proven[d] ⊆ S_d` (§4.2). By
   condition 2, every yielded candidate then begins a string of `L`.
5. **No unproven context.** Every item that reads outside `[c, c + k)` is a CONTEXT span
   (§3), and the kit proved each one under its stated `absent` rule. This covers `\b`/`\B`
   at either edge, width-1 lookbehinds, `(?m)^`, `(?m)$` and trailing class lookaheads.
   An item the anchored machine cannot express as a per-position set declines the row.
6. **No assertion unproven inside.** The walk of condition 3 meets no view-dependent or
   class-indexed accept inside the span, except the trailing one condition 5 resolves.
7. **No captures asked beyond the whole match.** Stage 1 runs on DFA-finisher routes
   only (`CR_DFA`, `CR_ATTEMPT`). There a group ≥ 1 is never live: it is written
   `PCREC_UNSET` on a success, which is the shipped `FIN2` dead-group fill
   (`match_api.md` §3.1¶4). Live groups mean the VM, which is stage 2 (§8.3 U1b, Q1).
8. **No end anchor left to the engine.** A non-multiline `$`/`\Z`/`\z` body is end-pinned.
   `rev-end` (A2) is selected ahead of `cover` (§2.2), or the body has no kit site at all.
   Census check: of the patterns that become whole-cover only "with an end anchor as
   pcrec's length compare", **every one that has a kit site is `(?m)…$`** (`counts.txt` C:
   2 bench, 9 corpus DFA, 1 VM). `(?m)$` is a per-position after-span, `{\n}` with absent
   SATISFIES (§3.4), so it joins through condition 5. The length compare the census named
   belongs to the sibling rows with no kit site (§8.2, U-anch).

`cover` is the conjunction. `pcrec_known_derive` (§5) computes it, and the LOCATE row reads
it (§2).

### 1.2 Which sites qualify, counted (K35)

The census population, recounted by consumer kind and by whether the artifact carries
groups ≥ 1 (`counts.py` reads `sites.tsv.gz` and `patterns.tsv.gz`; the census's own
enumerator is [ARTREV]'s, imported). Origin is `start` throughout.

| population (native / utf8) | bench sites | corpus sites | in stage 1? |
|---|---:|---:|---|
| DFA_SCAN PF, no groups | 24 / 15 | 359 / 216 | yes |
| DFA_SCAN OFS, no groups | 43 / 30 | 228 / 190 | yes |
| DFA_SCAN, dead groups only (DFA artifacts with NCAPS ≥ 2) | 4 / 4 | 93 / 88 | yes (FIN2's dead-group fill) |
| DFA_HAT | 0 / 0 | 6 / 0 | yes (the re-seeding scan is bypassed whole) |
| **stage 1 total** | **71 / 49** | **686 / 494** | |
| + context joins (DFA engine, every item expressible, `counts.txt` D) | 6 / 3 | 84 / 69 | yes (§3) |
| HYB_PF (an exact hybrid; groups on 4 / 4 bench, 101 / 57 corpus) | 6 / 4 | 225 / 57 | NO: stage 2, U1b |
| VM_ATTEMPT (all carry groups) | 0 / 0 | 39 / 0 | NO: stage 2, U1b |
| context joins on the VM (`(?<=item )done`, `item(?= done)`) | 4 / 3 | 23 / 19 | NO: stage 2, U1b |
| whole-cover, no kit site (anchored `^`/`\A`/`\G`) | 3 / 3 | 23 / 17 | NO: sibling U-anch |
| end-anchored, no kit site (validators, `rev-end` bodies) | 8 / 6 | 162 / 152 | NO: sibling U-anch |

The bench stage-1 cells are kvcensus §6's list minus the VM rows: litrun (all nine),
bounded (dig-exact-2/8/16, year4, floor), capability/sentinel (file-ext-order,
keyword-prefix-order, router-prefix-order, the foo|foobar semdiv cell, json begins,
floor-byte), the DFA half of syntax, and utf8's literal and class cells. The context joins
are capability/hex8-bounded, syntax/asr-wb and asr-nwb, utf8/asr-b-ascii and asr-b-cyr, and
capability/utf8-lead-no-cont.

### 1.3 Find-all, empty matches, `search_from`, `\G`, guards, utf8

- **Find-all.** `_search` stays one-shot. The match_api §3.1.3 loop calls it again from the
  returned end `c + k`. The stream is ascending and complete from `lo`, so the next call's
  first candidate is the next leftmost match. A candidate overlapping the reported match is
  below `lo` and is never yielded. The D165 iterator, which carries the stream's state
  across calls, is a later fit (§8.3 U-iter).
- **Empty matches.** These cannot occur. Condition 2 needs `k ≥ 1`, and a nullable body
  (`pcrec_nullable`) declines. The empty-match advance therefore never arises on a `cover`
  artifact.
- **`search_from`.** Every candidate is `≥ search_from` (the stream's range). Context reads
  go BELOW `search_from` down to the subject start, which is PCRE2's lookbehind and `\b`
  semantics (`locate_finish.md` O5). The site states `span_lo` = 0 as its read floor (§3.5).
  Today's `search_from > subject_length` return stays in front of the site, and the site's
  range is empty when `search_from + k > n`.
- **`\G`.** A body containing `\G` declines. Its only start is `search_from`, so there is no
  stream to ask; that case is the anchored sibling (U-anch). Non-multiline `^`/`\A` bodies
  have no kit site today and stay where they are.
- **Startpos and utf-check guards.** The K50 `PCREC_ERR_STARTPOS` prologue
  (`RX_STARTPOS_GUARD`) and the `-futf-check` validation run before the site, unchanged.
  `cover` adds no refusal and no give-up.
- **utf8 alignment.** A candidate is a character start because `S_0` contains no
  continuation byte. `window_contract.md` §2.3 asserts this "where it relies on it", and
  under `cover` the producer DECLINES instead of asserting (a decline is answer-safe). The
  end `c + k` is a character boundary because the lowered machine accepts only after whole
  characters (O6). A context byte at `-1` may be a continuation byte of the preceding
  character. Its verdict is still exact (§3.3).

### 1.4 The give-up surface (D158)

On stage 1's routes no budget meters anything: the DFA is not budgeted, and neither is the
kit's stream. The deny arm (`composite` on the same route) is not budgeted either. So the
posture cell is N/A (`locate_finish.md` §1.5 rule (e)), and "an answer never becomes a
give-up" holds because neither arm can give up. `cover` adds no `PCREC_ERR_*` producer.
An EMPTY stream is NOMATCH outright: the site states an `absent` rule on every context span
(§3.4), so no edge is left for pcrec to try (`window_contract.md` §2.4's coverage rule). The
stage-2 cells (VM, hybrid) would be ONE_WAY, since attempts are removed, and
direction-checked by GIVEUP1, with D158 applied per measured cell.

### 1.5 Where `L` is read from

From the ROUTE'S ANCHORED MACHINE: `job->adfa` (A) on `CR_DFA` and the attempt machine
(ATT) on `CR_ATTEMPT`. These are the machines the match-here entry and the attempt loop
already run, and they are priority-aware (K17/K18), which condition 2's leftmost-first
shapes need. Where A was not built (`anchored_ok` false, over the DFA cap), the row
declines, and Z2 counts those declines. The reading is the census's `kvdfa.lang`/`whole`
walk (kvcensus §2), done by pcrec over its own tables: subsets of rows from the entry, depth
by depth. It reads, per depth `d`, the reached rows `R_d`; `S_d` (the live bytes); whether
every row in `R_d` allows the same `S_d` (exactness); and, at `k`, accept with no live
successor. It runs per artifact, once, at most 32 + 8 deep. The facts layer
(`src/facts/`) is NOT the home: it precedes the machines, and an NFA walk without priority
would refuse `in|instanceof`.

**Where to attack §1.** (a) Condition 3 under leftmost-first priority: a body where the
anchored machine keeps a live successor past a shadowed arm, or kills one that PCRE2 keeps.
(b) Condition 2's product rule on a caseless class under utf8 (`(?i)é`), and on the 65
utf8-born mixed patterns. (c) An end anchor that reaches `cover` without being `(?m)$`:
`rev-end`'s stage-1 conjunct fails and the body still has a kit site. (d) Dead groups:
a DFA artifact with NCAPS ≥ 2 whose group is live. (e) Find-all after a match that ends at
`n`.

---

## 2. The REPORT finisher as a row of the existing table

### 2.1 Why a LOCATE row, and what becomes of T-PROOF

`FIN2 report` already exists (`emit_dfa.c:9922`). It takes `SPAN` on `CR_DFA` and
`CR_ATTEMPT` and returns `(s, e)`. What U1 adds is a PRODUCER of `SPAN` that needs no
machine: the kit's proven stream. In `locate_finish.md`'s model a producer of the result
product is a LOCATOR (§1.1): a walk named by its seed, direction and language, which hands
a point of `(I, e, D)`. The `cover` walk is the kit's stream from `search_from`. Its first
element `c` is `[c, c]` with `e` and `D = {c + k}`, which is `SPAN`. An exhausted stream is
`I = ∅`, which is `NOMATCH`. So U1 is one LOCATE row, and FINISH is unchanged. It is the
fifth path-changing locator, after `empty`, `rev-end` and `[START-LANDING]`'s two RECOVER
rows, and the stamp rule needs no edit (§2.4).

**T-PROOF folds into `cand_rows[]`.** `window_contract.md` §9 drafted T-PROOF as its own
first-match table (`report` → `dfa-exact-prefix` → `vm-literal-prefix` → `verify-rest` →
`ignore`). Its rows do not compete for one decision. Each consumes a proof in a different
SLOT:

| T-PROOF row | the slot it is a row of | lands |
|---|---|---|
| `report` | LOCATE `cover` → FINISH `FIN2`/`FIN1` | U1 (this note) |
| `dfa-exact-prefix` | the composite's NEXT → VERIFIER entry state (the DFA enters at `δ*(s0, proven)`) | U2, held (kvcensus §8.2) |
| `vm-literal-prefix` | the VM entry (`CR_VM`'s FINISH hats) | U3, no population (kvcensus §8.3) |
| `verify-rest` | a kit VERIFY site beside NEXT (direction 1) | filed |
| `ignore` | every row that reads no proof | already the default |

A separate table would be a second walk over the same choices (`locate_finish.md` §2.2's
argument for one array). So T-PROOF becomes a FAMILY: rows of `cand_rows[]` that read
`pcrec_known_derive` (§5) and carry ONE shared deny field, `PCREC_NO_KIT_PROOF`
(`-fno-kit-proof`, the deny `window_contract.md` §4.3 proposed). `--list-axes` lists the
`kit-proof` axis with its member rows. The §9 row in `window_contract.md` is an owed sibling
edit: T-PROOF becomes a family note (§6.2).

### 2.2 The row

```c
/* [KIT-VERIFY] U1 `cover` (kit_proof.md §2): the kit's site PROVES the whole
 * fixed-width sub-problem, context included, at every candidate it yields, so
 * the first candidate IS the leftmost match: SPAN [c, c + k]; an exhausted
 * stream is NOMATCH. No machine runs. PRESENCE is answered by the stream
 * (`whole`). The site is the window site of window_contract §5.2 for segment 0,
 * never NEXT's per-shape builder, so NEXT, WINDOW, FIRST and RECOVER are off
 * the path. After `rev-end` (an end-pinned body walks k steps from n, not a
 * scan of the subject), before `composite`. */
{ .c = { "cover", PCREC_NO_KIT_PROOF, locate_cover_applies }, .slot = CAND_SLOT_LOCATE,
  .routes = CR_DFA | CR_ATTEMPT, .tok = "cover", .map = CM_NONE,
  .hands = CT_START | CT_VERDICT,
  .list = { [CAND_ROUTE_DFA] = { "locate", 2, "cover", PCREC_NO_KIT_PROOF } },
  .desc = "the kit's search site proves every byte of the fixed-width match and its context at every candidate it yields: the first candidate is the match, reported with no scan and no start recovery",
  .needs = { [CAND_ROUTE_DFA]     = { 0, 0, CN(CAND_SLOT_PRESENCE) },
             [CAND_ROUTE_ATTEMPT] = { 0, 0, CN(CAND_SLOT_PRESENCE) } },
  .u.locate = { .emit = { [CAND_ROUTE_DFA] = emit_cover, [CAND_ROUTE_ATTEMPT] = emit_cover },
                .scan = { [CAND_ROUTE_DFA] = "cover", [CAND_ROUTE_ATTEMPT] = "cover" },
                .whole = true, .fin = CT_START | CT_VERDICT } },
```

- **Order:** `empty` → `rev-end` → `cover` → `composite`. `rev-end` comes first because an
  end-pinned body walks `k` steps back from `n`, while a stream scans the subject. `empty`
  first as today.
- **Predicate** `locate_cover_applies` is `pcrec_known_derive(...).cover` (§5). It is a
  declared read, LOCATE → ask(site). The site's description depends on the language facts
  only, never on FIRST's or NEXT's selection, so no edge points forward and the
  `table-read-cycle` check holds (`r17b_prime.md` §4.5 rule 5).
- **Needs:** NO machine, and PRESENCE (as the front, answered by `.whole`, so `RX_REQ_WHY`
  reads `dominated` per `locate_finish.md` §5.1). The match-here entry is a separate path
  root. It keeps its own FINISH ask (`FIN3 verify-at` on A, or `FIN4`), so A stays a
  member where it is built today and F and R drop out.
- **Totality:** `cover` hands `SPAN` and `NOMATCH`, which `FIN2` and `FIN1` take on both
  routes (`emit_dfa.c:9915-9925`), so the self-check's (locator route, finisher route)
  triple table gains no unreached cell.
- **Listing slot:** the `locate` axis lists `rev-end` 1, `cover` 2, `unanchored` 3. That
  re-numbers `unanchored`'s listing index, a `--list-axes` mover inside B1 (§6.1).

### 2.3 The emitted entry

Today, `foobar` (main `a016b3bfa`, abi 80): `rx_search` declares three forward tables
(byte class, 42 next-states, 42 accept bytes), runs the forward scan loop with
`rx_ofsskip` (which already compares all six bytes, `rx_w4(…"foob") && rx_w4(…"obar")`),
steps the DFA six bytes from the candidate, and recovers `match_start_position =
last_accept_position - 6` (`RX_DFA_START "end-minus-width"`). `\bcat\b` adds a K82
`rx_reqrun` handoff, a `rx_forward_seed_state` table read at every candidate
(`subject[scan_position - 1]`), and `rx_forward_is_accepting_by_class` for the trailing
`\b`.

Under `cover` (DFA hat; the ATTEMPT hat is the same text):

```c
int rx_search(const unsigned char *subject, size_t subject_length, size_t search_from,
              ptrdiff_t (*capture_spans)[2])
{
    if (search_from > subject_length) return 0;
    size_t cand = rx_cover(subject, subject_length, search_from);  /* the kit's site */
    if (cand >= subject_length) return 0;
    if (capture_spans) { capture_spans[0][0] = (ptrdiff_t)cand; capture_spans[0][1] = (ptrdiff_t)(cand + 6); }
    return 1;
}
```

Groups ≥ 1 on a dead-group artifact get FIN2's existing `PCREC_UNSET` fill under the same
`if`. The startpos and utf-check prologues stay in front.

**REMOVED from the search path:** the forward machine's tables and step helpers (F leaves
the members, so `RX_DFA_TABLE` and `_SCAN_EDGE` fold over what is left), the scan loop and
its `last_accept_position` bookkeeping, the scan-edge peel, the start recovery (the
`end-minus-width` subtraction, or the reverse pass and R's tables), the K82 handoff, the
presence pre-check, and the seed-state read. **KEPT:** `_match`/`_match_caps` on A (their
own FINISH), `_next_pos`, `_valid_upto`, `rx_info`, and the kit's helper text.

**Size (hand twin, SIZE ONLY):** `kit_proof/cover_twin.py` on `foobar`, gcc 15.2 `-O2 -c`:
`.text` 2,047 → 1,425 B, `rx_search` 100 → 61 instructions with the site inlined in both.
The kit's text is unchanged in that twin because `run-pinned` already compares every byte.
On a one-byte PF site (`\d{4}`, `0R` today) the kit's text grows by the verification it
chooses (§4.3).

### 2.4 Stamps (the generated rule, `locate_finish.md` §5.1; no per-stamp edit)

| stamp | on a `cover` artifact | why |
|---|---|---|
| `RX_DFA_SCAN`, `rx_info.scan` | `"cover"` (NEW value) | LOCATE's listed name |
| `RX_DFA_START` | `"attempt-start"` | RECOVER not asked: its absence value (`cand_absent[]`, `emit_dfa.c:11079`), which is true here (the candidate is the start) |
| `RX_END_WINDOW`, `RX_REQ_HANDOFF`, `RX_DFA_PREFILTER`, `_PREFILTER_OFFSETS` | `"none"` | WINDOW, FIRST, NEXT not asked: absence |
| `RX_REQ_WHY` | `"dominated"` where `REQ_BYTE ≠ "none"` | PRESENCE asked, `.whole` |
| `RX_REQ_BYTE`, `RX_REQ_RUN` | unchanged | facts about the pattern |
| `RX_DFA_TABLE`, `RX_DFA_UNIFORM_FOLDS`, `RX_DFA_SCAN_EDGE` | folded over the members (A only, where built) | §2.7's member fold |
| `RX_DFA_MATCH`, `rx_info.match_form` | unchanged | the match-here entry's own FINISH |
| the kit's site record (`memfn_stamps.c`) | the site's own record | the site is a new emitter call site (§6.1, manifest) |

The site that `RX_DFA_PREFILTER` used to name is now described by the kit's record, and
`RX_DFA_SCAN "cover"` says the path.

### 2.5 The ask, and `site_kind` REPORT

A site's facts must be TRUE (D161 add. 4), and `site_kind` is the consumer. On a `cover`
artifact nothing consumes the candidate except `FIN2`, so the honest kind is a new one,
`MF_SK_REPORT` (unbudgeted; NONE answer-safe, as on DFA_SCAN). Whether the consumer is
REPORT depends on the proof, and the proof is the kit's answer to the description. The
cycle closes through the PURE ask (`r17b_prime.md` §4.5 rule 1):

1. During LOCATE's selection pcrec asks the `cover` DESCRIPTION. That is span 0 `=
   S_0..S_{k-1}` with `consumable_len = k`, its context spans with `consumable` YES, and
   `site_kind` REPORT.
2. If `pcrec_known_derive` says `cover`, the row is selected and that same description is
   DEFINED. Rule 2's agreement then holds by construction, and the trace build re-asks and
   compares.
3. If not, `cover` declines and the composite's own description (today's) is asked and
   defined as today. Every non-`cover` site is byte-identical (§7, Z2's gate).

Two pure asks on a qualifying artifact cost compile time only. This is not the rejected
`mf_ask` two-pass of r2 (add. 16): that one re-asked with a forced `need`, which made NONE
illegal and needed a price. Here `need` is unchanged between the two descriptions. Span 0
offset 0 stays REQUIRED (T-NEED's "the FIND definition requires it") and the rest is
OPTIONAL. The two asks differ only in TRUE consumer facts.

**Where to attack §2.** (a) Is `cover` really a locator, or is it a FINISH row with a fused
search? Test it against `locate_finish.md` §1.2's product. (b) The path derivation: a
reader of "is F a member" that runs on a `cover` artifact and assumes F (`dfa_uniform_folds`,
the orientation block, `emit_vm.c:11330`'s hybrid gate, which cannot meet `cover` in stage
1). (c) The two-ask order under the size ladder: is a rung re-emit's ask the same as the
first? (d) `compound.c:199`/`:235` read LOCATE's selection by name (`"composite"`,
`"rev-end"`), so a compound part that selects `cover` changes their verdicts. B1's reader
census re-reads both. (e) The `--list-axes` index move.

---

## 3. Context spans before and after the origin

### 3.1 What exists today

pcrec does not rewrite `\b` by position (kvcensus §0). `src/parse/mod_assertions.c:131-134`
lowers it to `A_CTX(W, BOUNDARY)`, the VM tests both sides (`emit_vm.c:8355`), and the DFA
gets the positional effect only implicitly, from its SEED TABLE. `\bcat\b`'s artifact reads
`rx_forward_seed_state[rx_forward_byte_class[subject[pos - 1]]]` at every candidate and
`rx_forward_is_accepting_by_class` after the last byte. Two partial forms ship already: the
MLINE context predicate (`{\n}` at -1, `proven_prev`), and the 23 `scan-restart/ctx` sites,
which send a width-1 lookbehind as a shifted origin (span 0 IS the context byte, kvcensus
§6).

### 3.2 Where the rewrite goes: it is READ, not lowered

Frank's ruling (add. 16): "a rewrite of `\b` automatically gets added to the sent span".
This note implements that as a STATED FACT derived from the route's anchored machine (§1.5).
It is not a tree rewrite.

- **Before the origin** (the seed table). For every predecessor byte class `p`, the machine
  enters at row `e(p)`, and at the subject start at `e(⊥)`. The context set is `C_-1 = {b :
  e(class(b)) is live}`. It is EXPRESSIBLE iff every live entry is the same row `r0`. `r0`
  is then the constant entry (census: constant on 64 of 64 real machines checked). `absent`
  is SATISFIES iff `e(⊥) = r0`, and FAILS iff `e(⊥)` is dead. Any other `e(⊥)` declines.
- **After the end** (the class-indexed accept). Let `R_k` be the rows at depth `k`. `C_k =
  {b : every row in R_k accepts under class(b)}`, expressible iff the rows agree on that set
  and have no live successor. `absent` is SATISFIES iff every row accepts at the subject
  end.

This IS the positional rewrite. Before a word byte the seed for a word predecessor is dead,
so `C_-1 = ¬W` with `absent` SATISFIES, which is `(?<!\w)`. Before a non-word byte it gives
`(?<=\w)`. A straddling next set (`\b[a-z-]`) gives two live entries and declines. It is
computed rather than pattern-matched, so one reading covers `\b`, `\B`, `(?m)^`, `(?m)$`,
the width-1 lookbehinds and the trailing lookaheads the DFA admits (`z(?=a)`, `z(?![ab])`,
`(?<![a-z])cat`: 84 corpus DFA context joins, `counts.txt` D).

**Why not in the lowering.** A rewrite in `mod_assertions.c` or a facts-layer IR pass has
three problems:

1. It MOVES every engine's bytes and the `--emit-ir` listing on every `\b` artifact, for
   no answer change.
2. It is a second spelling of what the seed table already encodes, which is what D122 and
   memory `pcrec-general-mechanisms-not-special-cases` forbid.
3. Its safety would rest on a pattern-matcher's case analysis. The machine reading is an
   equivalence by construction: it reads the machine the DFA would run.

The census's C4 (6,510 cells against PCRE2, 0 differences) measured the rewrite's
equivalence, and the build's X1 re-measures it on the built artifacts (§6.4). The VM-only
context joins (`(?<=item )done`) have no machine to read. They are stage 2's, through a
facts-layer reading of the leading `LOOK` node (U1b).

### 3.3 What is expressible

| item | per-position form | `absent` | stage 1 |
|---|---|---|---|
| `\b` before a word / non-word byte | `C_-1 = ¬W` / `W` | SATISFIES / FAILS | yes |
| `\B` before a word / non-word byte | `C_-1 = W` / `¬W` | FAILS / SATISFIES | yes |
| `\b`/`\B` after the end | `C_k` (the mirror) | the mirror | yes |
| `(?<=X)`, X a byte set (width 1) | `C_-1 = X` | FAILS | yes, where the DFA admits it |
| `(?<!X)`, X a byte set (width 1) | `C_-1 = ¬X` | SATISFIES | yes |
| `(?m)^` | `C_-1 = {\n}` | SATISFIES (position 0) | yes |
| `(?m)$` | `C_k = {\n}` | SATISFIES (the subject end) | yes |
| `(?=X)` / `(?!X)` width 1 after the end | `C_k = X` / `¬X` | FAILS / SATISFIES | yes |
| positive lookbehind of fixed byte width w > 1 with an exact product | `C_-w..C_-1` | FAILS | NO: the DFA reads one seed byte; VM, stage 2; ≤ `MF_MAX_BACK` (8, CHOSEN) |
| `(?<!ab)`, `(?<!é)` (a negative of width > 1) | a disjunction | — | never (add. 16) |
| non-multiline `$`/`\Z`/`\z` | not per-position (`$` reads `n - 1`) | — | never; `rev-end`, or the anchored sibling |
| UCP `\b` under utf8 | — | — | refused by the parser today (`mod_assertions.c:123-129`) |

**utf8.** `\w` is ASCII on every encoding pcrec builds, since UCP `\b` is refused under
utf8. A continuation byte is therefore a non-word byte. PCRE2 judges the preceding
CHARACTER, and a multi-byte character is non-word under ASCII `\w`, so the one-byte verdict
equals PCRE2's. The same holds for a width-1 positive or negative lookbehind over an ASCII
set: a continuation byte is never a member. The census agrees: 11 of 11 utf8 bench machines
and 47 of 47 corpus machines had a constant seeded entry, with 0 differing rewrite cells.

### 3.4 The absent-byte bit

At `c = 0` there is no byte at -1, and at `c + k = n` there is none at `k`. `absent` says
whether the context HOLDS there. `(?<!\w)` holds at offset 0; `(?<=\W)` does not; `(?m)^`
holds at 0 and `(?m)$` at `n`. It is stated per CONTEXT span with an UNSTATED zero
(§4.1). Once every context span states it, no position is uncovered, so pcrec's EDGE attempt
(`window_contract.md` §2.4) is not needed on a `cover` artifact. An exhausted stream is
NOMATCH outright, and the edge code is not emitted.

MLINE's existing context predicate is restated at Z1 as CONTEXT with `absent` FAILS and
`consumable` NO. That is exactly today's behaviour: the kit yields no candidate whose -1 is
absent, and pcrec tries the edge itself. It moves no byte. On a `cover` artifact the same
`(?m)^` states SATISFIES, and the edge code is gone. Retiring MLINE's edge everywhere is an
unlock (U-mline).

### 3.5 Reads before `search_from`

The kit may read `subject[c - 1]` when `c = search_from > 0`. That is the real byte before
the start, and PCRE2 reads it (O5). It may never read before the subject start, where
`absent` decides instead. The bound is the site's `span_lo` (the proven range, an existing
field), stated as 0 on every site that carries a context span. The kit's obligation is that
every read lies in `[span_lo, n)`, which is `window_contract.md` §2.3's "reads" rule with
the floor named.

### 3.6 How the readers see it, and one-way safety

- **DFA:** its machine and emission are unchanged. A `cover` artifact runs no DFA in
  `_search`. A non-`cover` artifact sends no context span in stage 1, so no kit text moves
  there. Sending context spans to seeded DFA_SCAN sites as a filter is U4.
- **VM:** the program keeps `A_CTX`, and nothing reads the fact in stage 1.
- **Listings:** `--emit-ir` is unchanged (the IR is untouched). `--emit-facts` gains the
  [MATCH-KNOWN] member row for each site with a `cover` verdict (§5.3), which owes a
  `facts_listing.md` hunk. `--list-axes` gains the `cover` and `kit-proof` lines.
- **One-way safety.** A context span is used two ways, and each is safe in one direction.
  (i) As a FILTER: every match satisfies it (it is an equivalence), so a kit that drops
  candidates failing it drops no match. (ii) As a PROOF: `cover` consumes it only when the
  kit proved it. An item that cannot be read exactly is not stated and declines the row,
  and a decline is today's path. No direction can turn an answer into a different answer
  or into a give-up. A producer bug that OVER-states a context set would be a wrong answer.
  Two independent checks guard that direction: X1 (against libpcre2) and the S1130/S1137
  plants (§6.3).

**Where to attack §3.** (a) A DFA seed table whose live entries agree on the row but
whose accept depends on the predecessor class elsewhere: a view read deeper than offset
-1. (b) `absent` under `(?m)^` with `search_from > 0` and `subject[search_from - 1] ≠ '\n'`.
(c) The after-span on a row that accepts at the end AND has a live successor (`cat\b` in
`cat\b\w*`?). (d) A width-1 lookbehind the DFA admits over a set containing ≥ 0x80 bytes
under utf8. (e) Whether reading through `span_lo` changes any shipped site's range: MLINE's
does not, since it states FAILS.

---

## 4. The facts pcrec states and what the kit returns: R-26

### 4.1 What pcrec states

| fact | where | values (zero = UNSTATED, refused where read) | today's truth (Z1) | on a `cover` site (B1) |
|---|---|---|---|---|
| `prefix_stated` | `mf_pred`, span 0 of a FIND site | 1 = the two below are stated | 1 | 1 |
| `exact_len` | the same | 0..`MF_MAX_SPAN_POS`: positions `[0, L)` are EXACT, i.e. the cross product of the sent sets over `[0, d]` equals the sub-problem's length-(d+1) prefixes for every `d < L`, for this artifact's encoding. Replaces add. 10's `byte_form` (design-only, never built). An under-statement is sound | 0 everywhere at Z1 (sound); the producer's value from Z2 on | `k` |
| `consumable_len` | the same | 0..`exact_len` (more is refused): "if you prove `[0, N)`, my consumer will not re-test those positions". A statement about pcrec's consumer, not an order and not a price | 0 everywhere: today's consumers (the DFA scan, the hat, the hybrid's prefilter, the VM) re-test every position, so 0 is true | `k` |
| `span_class` CONTEXT | `mf_pred` (the reserved value, now built) | a predicate whose terms lie below the origin or at or after the sub-problem's width | MLINE's `{\n}` | each context item |
| `absent` | `mf_pred`, CONTEXT only (0 elsewhere, refused otherwise) | SATISFIES, FAILS (§3.4) | MLINE: FAILS | per §3.3 |
| `consumable` | `mf_pred`, CONTEXT only | YES = "if you prove this span, I will not re-test it"; NO | MLINE: NO | YES |
| `need` | per term (built) | unchanged. T-NEED: REQUIRED only where K64-K66/D158 or the FIND definition demand it | as today | span 0 offset 0 REQUIRED; positions 1..k-1 and context OPTIONAL (unbudgeted route) |
| `site_kind` | `mf_site` (built) | adds `MF_SK_REPORT` | — | REPORT (§2.5) |
| `span_lo` | `mf_site` (built) | the read floor (§3.5) | as today | 0 |

`consumable_len` is one number, as Frank ruled. Every prefix consumer reads a prefix, and
a uniform position after a non-uniform one occurs on 25 of 3,673 measured sites (kvcensus
§5). It is STATED by pcrec, not derived from the language. On the 288 scan-restart sites
the language would claim more than the consumer can take (kvcensus §8.4).

Context spans get their own `consumable` bit rather than an extension of `consumable_len`,
because they are not part of span 0's prefix. The seeded-entry consumer of U4 consumes
-1 alone, and `cover` consumes everything.

### 4.2 What the kit returns

`mf_class` (`MF_CLASS_V` 3 → 4, appended LAST):

```c
/* (MF_CLASS_V 4, R-26; kit_proof.md §4.2) the PER-OFFSET PROOF: proven[d - MF_PROOF_LO]
   is a bitset (mf_term.set's layout) such that at EVERY candidate the site yields, the
   byte at offset d from the candidate lies in it, OR offset d lies outside the subject
   and the CONTEXT span covering d states absent SATISFIES. All ones = nothing proven.
   It states only what the committed form TESTS (R-25); it is never wider than a
   REQUIRED term's set at d (proven ⊇ need, in the binding sense: obligation 4). Equal
   under -fno-memfn-simd, -fmemfn-simd at every level and every layer: LAYER-INVARIANT.
   A --memfn= deny may change it: DENY-VARIANT (add. 16, r2 kvp-contract M3).
   proven0 == proven[0] and proven_prev == proven[-1] (asserted in the trace build) */
#define MF_PROOF_LO (-MF_MAX_BACK)
#define MF_MAX_FWD  (MF_MAX_SPAN_POS + MF_MAX_AHEAD)
uint8_t proven[MF_MAX_FWD - MF_PROOF_LO][32];
```

- **Bounds.** `MF_MAX_SPAN_POS` = 32 is a SHAPE BOUND derived from
  `PCREC_MAX_REQ_RUN_SCAN` (`src/core/limits.def:405`), and pcrec asserts the two equal
  (the `MF_CMT_NONESSENTIAL` precedent). `MF_MAX_BACK` = 8 exists, labelled CHOSEN in
  `memfn.h:150`. `MF_MAX_AHEAD` = 8 is new and also CHOSEN: the after-context width in
  stage 1 is 1. Both carry their trigger (memory `pcrec-suspect-tuning-constants`): a
  declined site counted at Z2 or later whose context exceeds the bound. The array is
  48 × 32 B = 1,536 B per class.
- **`proven0`, `proven_prev`:** KEPT as aliases with an asserted invariant, because their
  readers (G1, R4, `landing` L4, kit P2) read them today. Their retirement is a later
  zero-mover cleanup, deferred to [MATCH-KNOWN] (§5.4).
- **Language vs membership.** `proven[d]` is a MEMBERSHIP fact at any offset. pcrec's
  helper uses it as a LANGUAGE proof only for `d < exact_len` (kvp-contract S1/S2).
  Membership past that point still serves R4/G1.
- **Whether to prove is the kit's.** The kit decides from its own costs (equal test cost,
  a `continue` in its loop against pcrec's re-test). NONE stays legal. A `cover` artifact
  exists only where the kit chose to prove. There is no "cover bit" telling the kit what
  the proof is worth: D161 add. 6 dropped consumer price, and §8.4 Q3 asks whether to
  revisit that.

### 4.3 R-26, drafted (main files it after R-25 lands; facts only, D157)

> **R-26 (draft, pcrec manager) — the per-offset proof, `consumable_len`, prefix
> exactness, CONTEXT spans with an absent rule, and the REPORT consumer**
>
> **Customer:** [KIT-VERIFY] U1, `docs/design/kit_proof.md` (D161 addendum 16; review r2
> kitverify-proof; census docs/dev/kvcensus.md). **After R-25** (`proven0` honours `need`),
> because the per-offset proof generalises the field R-25 fixes, and 524 native OFS sites
> already send OPTIONAL offset-0 terms (kvcensus §3).
>
> | item | what pcrec needs (facts) | landing bar |
> |---|---|---|
> | R-26.1 | span 0 of a FIND site carries `prefix_stated`, `exact_len` and `consumable_len` with the meanings of kit_proof.md §4.1. An UNSTATED `prefix_stated` is refused at `site_check` (`mf_define`, `mf_ask`). `consumable_len > exact_len` is refused | one `MF_SITE_ABI` event, readers found by grep. ZERO artifact movers on every emit_sweep arm, with pcrec stating `prefix_stated` 1, `exact_len` 0 and `consumable_len` 0 on every site in the same change (the builder lines may be the kit lane's, as in R-23) |
> | R-26.2 | `span_class` CONTEXT is honoured: terms below the origin, or at or after span 0's extent. Each CONTEXT span states `absent` (SATISFIES/FAILS) and `consumable` (YES/NO), UNSTATED refused. The stream's COMPLETENESS and BINDING read `absent`: under SATISFIES a candidate whose context offset lies outside the subject is yielded when the other spans hold; under FAILS it is not. Reads lie in `[span_lo, n)` | MLINE restated as CONTEXT/FAILS/NO: zero movers. A G2 fixture per `absent` value at `c = 0` and at `c + k = n`, with completeness checked by the byte-loop oracle |
> | R-26.3 | `site_kind` `MF_SK_REPORT`: the candidate is the answer, with no engine behind it. Unbudgeted, so NONE is answer-safe (the DFA_SCAN cell of `r17b_prime.md` §4.6) | refused before R-26; admitted by the finder gate (`finder.c`) wherever DFA_SCAN is |
> | R-26.4 | `mf_class.proven[]` as kit_proof.md §4.2 states it. `proven0`/`proven_prev` equal `proven[0]`/`proven[-1]` | `MF_CLASS_V` 4. G2: at every candidate of every generated site, every proven offset holds, including negative offsets, offsets after the span, and the absent rule. C-PROOF: identical across SIMD off and every live level (deny-variant). The trace build's re-ask asserts the define's class equals the ask's |
> | R-26.5 | `MF_MAX_SPAN_POS` (32, derived from pcrec's `PCREC_MAX_REQ_RUN_SCAN`, asserted equal by pcrec) and `MF_MAX_AHEAD` (8, CHOSEN, labelled so) declared in `memfn.h` | declarations only |
>
> **Not asked:** any method. Whether the kit proves positions 1..N-1, with which form, and
> whether it pre-scans, are the kit's (D157, D161 add. 6). pcrec reads only what `mf_ask`
> answers.
>
> **Sequencing:** R-25 → R-26.1-R-26.5 at zero movers (Z1) → pcrec's Z2 → the B1 commit,
> which carries the kit's proving text for the `cover` sites (a kit byte move is a pcrec
> abi event in the same commit, memfn/CLAUDE.md, D146/D147).
>
> **Sabotage ids:** pcrec-side S1130-S1138 PROPOSED (kit_proof.md §6.3). Kit-side ids on
> request: a form claiming an untested offset; an absent-SATISFIES candidate dropped; an
> absent-FAILS candidate yielded; a proof bit set only by a SIMD row (C-PROOF).

### 4.4 R-25 first

R-25's fixture (an OPTIONAL offset-0 term the selected row skips reads all ones) is the
`d = 0` instance of R-26.4's rule "states only what the committed form TESTS". Landing
R-26 first would carry R-25's latent over-claim into 48 offsets. R-25 is live on 524 native
OFS sites today (kvcensus §3).

**Where to attack §4.** (a) A field whose zero is used, not refused: `exact_len` 0 is a
STATED value, so check that no reader treats "unstated" and "0" alike (the `prefix_stated`
bit is the distinction). (b) `consumable` on CONTEXT vs one number: is there a consumer
that consumes span 0's prefix but not the context, or the reverse, that the two facts
cannot say? (c) Absent-rule completeness when a context offset is below `span_lo` but
inside the subject. (d) `MF_MAX_AHEAD` against a trailing `(?=X)` wider than 8 on the VM,
stage 2. (e) Is `proven ⊆ tested` checkable by G2 from outside the kit, or does it share
the kit's own source?

---

## 5. ONE pcrec-side helper, and [MATCH-KNOWN] as its home

### 5.1 The record and the helper

[MATCH-KNOWN] is "ONE general record of what is ALREADY KNOWN about the subject at each
point of the emitted matcher". Its trigger is reached: [KIT-VERIFY]'s build is the third
consumer (kvp-unlock B1). This note builds that record's FIRST MEMBER: what is known at a
kit site's candidate, from the kit's proof. Placement is `src/gen/known.c` and
`internal.h`, in the gen layer, because it reads the kit's class and the built machines:

```c
/* [MATCH-KNOWN] member 1 (kit_proof.md §5): what is KNOWN about the subject at one
   program point, relative to an origin. The point is a kit site's yielded candidate. */
typedef enum { MK_AT_UNSTATED = 0, MK_AT_KIT_CANDIDATE } MkAt;
typedef enum { MK_SRC_UNSTATED = 0, MK_SRC_KIT_PROOF } MkSrc;
typedef struct {
    MkAt     at;
    MkSrc    src;
    uint8_t  set[MF_MAX_FWD - MF_PROOF_LO][32]; /* bytes known at origin + d; all ones = none */
    uint8_t  absent_ok[(MF_MAX_FWD - MF_PROOF_LO + 7) / 8];
} MkKnown;

/* pcrec's LANGUAGE facts for the sub-problem at that origin (the producer, §1.5/§3.2):
   S_d, exact_len, the width k (0 = not fixed-width), the end with no live successor,
   the context spans with their absent rules, and why a fact is absent. */
typedef struct MkLang MkLang;

typedef struct {
    uint8_t     prefix;     /* largest L <= exact_len with set[d] ⊆ S_d for d < L */
    uint8_t     cover;      /* §1.1, every condition */
    int8_t      suffix_lo;  /* first offset of the trailing proven run inside the span, or -1 */
    uint8_t     ctx_before, ctx_after;   /* every context span on that side proven */
    const char *why;        /* the first failing condition: "origin", "width", "exact",
                               "live-after", "unproven", "context", "groups", "anchored-machine" */
} MkDerived;

MkDerived pcrec_known_derive(const MkLang *lang, const MkKnown *known);
```

- **Pure.** The helper reads the record and the language facts, writes nothing, and is
  memoised per site per compile.
- **Its readers in U1:** `locate_cover_applies` (`cover`) and `emit_cover` (`k`). It also
  writes the CANDTRACE record `KNOWN <site> prefix=… cover=… why=…`, which the Z2 gate and
  the K35 count read (§6.4).
- **Its readers later**, each a T-PROOF family member (§2.1): U2 reads `prefix`, U4 reads
  `ctx_before`, and [PF-KNOW]'s trailing segment reads `suffix_lo`. None is built here.

### 5.2 The producer of `MkLang`

The walk of §1.5 and §3.2 over the route's anchored machine, once per artifact. Its two
outputs are `MkLang` (read by the helper) and, from Z2 on, the TRUE `exact_len` stated on
span 0 of every start-origin FIND site. That second output is zero movers while
`consumable_len` stays 0 there: the kit cannot prove anything new for a consumer that
re-tests everything. Sites with any other origin keep stating 0, which is sound.

### 5.3 What of [MATCH-KNOWN] this builds, and what it defers

| [MATCH-KNOWN] | U1 builds | deferred (each to its own trigger) |
|---|---|---|
| the record type | `MkKnown` with `at`/`src` enums whose zeros are UNSTATED | other points: a VM pc, a DFA state, a prefilter window end |
| members | `MK_SRC_KIT_PROOF` | [PF-KNOW]'s prefilter proof (D142); K23 MRL `minw`; [START-LANDING]'s landing and `end-minus-width`; the D164 end set; the K82 landmark K; the compound floor attempt; [VM-LEN-HOIST]'s length fact |
| derivations | `prefix`, `cover`, `suffix_lo`, `ctx_*` in one helper | containment ("is byte set X proven at d"), which would retire the three "dominated" spellings (kvp-unlock U5) |
| readers | `cover` | migrating G1, R4 and L4 from `cls.proven0` to the record (zero movers, a cleanup); every T-PROOF member |
| listing | the member's row in `--emit-facts` (kvp-unlock U6) | the record's own listing section once a second member exists |
| propagation | none: one point, no lattice | the dataflow lattice over the program (the plan row's "bytes proven at offsets, length bounds, position pins, context known") |

**Where to attack §5.** (a) Is the helper's `cover` the SAME predicate the census measured
(kvdfa.whole), or does it drift on the scan-restart or view-bounded classes? (b) Does any
existing reader compute one of `prefix`/`cover` privately (G1's domination test, `landing`
L4's `exists`)? If so it is a second spelling. (c) `MkKnown`'s origin-relative layout
against a future VM-pc member, which has no origin.

---

## 6. abi events, spec hunks, sabotage rows, checks, populations

### 6.1 The events and their readers (found BY GREP at `a016b3bfa`; re-grep at the build commit)

| event | step | readers (grep) |
|---|---|---|
| `MF_SITE_ABI` 16 → +1 (R-26 layout, the REPORT kind) | Z1 | `memfn/include/memfn.h:39` (the history), `src/gen/memfn_sites.{c,h,def}`, `src/gen/CLAUDE.md`, `tests/memfn/run_finder.sh`, `rows_check.py`, `form_checks.py`, `run_arm_pins.sh`, `prov_check.c`, `site_manifest.tsv` |
| `MF_CLASS_V` 3 → 4 | Z1 | `memfn/src/compose.c:297`, `:305`, the trace re-ask (`mf_defined`'s `cls`) |
| pcrec abi 80 → +1 (B1: the `cover` entry, the kit's proving text on `cover` sites, the stamp value) | B1 | `src/gen/emit_dfa.c:54` `PCREC_ARTIFACT_ABI` (emitted at `:138`, `:2101`, `:3085`); `docs/spec/match_api.md:168`, `:169`, `:172`, `:1260`, `:1401` and §6¶17; `docs/dev/history/abi_changelog.md` (the only home of the log); `src/gen/CLAUDE.md`; `tests/codegen/run_codegen_tests.sh` (the abi pins); `tests/codegen/run_recursion_identity.sh` (the (B) pin); the four byte-identity gates' pins (re-pinned by recompiling their witnesses, since byte COUNTS move without citing the number, coding_guide §3.1); then the suites that count: registry, codegen, rxtsource (D94 addendum) |
| `RX_DFA_SCAN`/`rx_info.scan` vocabulary + `"cover"` | B1 | `match_api.md` §6 row 20 and §6.3.4; `src/core/compound.c:199`, `:235` (readers of LOCATE by name); `tests/registry/axes_registry_check.sh`, `run_registry_tests.sh`; `tests/memfn/site_census.py`, `site_manifest.tsv`, `run_deleg_sites.sh`, `c10_onebyte.tsv`, `c10_presence.tsv`; `tests/startset/startset_checks.py`, `dfahat_checks.py`; `tests/revend/gen_rev_end.py`, `window_twin.py`; mech anchors that quote the scan stamp (S738, S768, S770, S773, S490, S910, S1091 among those grep finds); pcrec-bench's closed enum (`testees/pcrec/adapter.py`, `pcrecbench/report.py`, `tools/selfcheck.py`), via an `[inbox]` note (D78) |
| a new flag bit `PCREC_NO_KIT_PROOF` | B1 | `lib/pcrec.h` (bits 0-54 and 56 used, 8 free: 55, 57-63; this leaves 7, above [IFACE-PUSH]'s hard trigger of ≤ 4), `src/core/axes.def`, `tuning.md`, `cli.md`, `--list-axes` |
| the site manifest's new row (`emit_cover`'s call site) | B1 | `tests/memfn/site_manifest.tsv`, `site_census.py` |
| `--list-axes` `locate` re-index (`unanchored` 2 → 3) | B1 | `tests/registry/axes_registry_check.sh` and the listing pins |

Data regeneration: §8.1 (3).

### 6.2 Spec hunks owed (D80), each in its step

- **Z1:** none. No caller-observable change.
- **Z2:** `facts_listing.md`, the [MATCH-KNOWN] member's `--emit-facts` row (a listing, not
  an artifact abi event).
- **B1:**
  - `match_api.md` §3.1¶21 ("four forms to recover the match start" becomes five: the
    `cover` form recovers nothing, the kit's candidate is the start; answer-identical,
    differing in cost and size);
  - `match_api.md` §6 row 20 and §6.3.4 (the value `"cover"`);
  - `match_api.md` §6.3.1¶5a: the absence statement already covers `_DFA_START
    "attempt-start"`, so check it, do not edit it;
  - `tuning.md`: one entry for `cover` and the `-fno-kit-proof` axis. The D158 preamble
    covers it and no ONE_WAY marker is needed, since nothing is budgeted;
  - `cli.md`: the flag;
  - abi §6¶17.
- **Sibling design edits (not spec):** `window_contract.md` §9's T-PROOF row becomes a
  family note (§2.1); §2.2's `byte_form` paragraph is superseded by `exact_len` (add. 16
  already says so; the text still describes it); §4.3's per-span `proven` bitmask is
  superseded by the per-offset sets.

### 6.3 Sabotage rows (PROPOSED; next free main ledger id S1130 per
`worktrees/.mgr/sabotage_ids.txt`; the ledger is not edited here)

Each row has a REACH witness ([MECH-REACH]) and an expectation from libpcre2 or from a
check that does not read the row's predicate.

| id | plant | witness (reaches `cover`) | caught by |
|---|---|---|---|
| S1130 | the producer states `C_-1` as every byte (context over-stated) | `\bcat\b` on `"concat"` (bench syntax/asr-wb): PCRE2 no match; the plant reports `(3,6)` | X1 |
| S1131 | the exactness test is skipped (`exact_len := k`) | `ac\|bd` on `"ad"`: PCRE2 no match | X1 |
| S1132 | the "no live successor at `k`" conjunct is dropped | `abc\|ab` on `"abc"`: PCRE2 `(0,3)`, the plant `(0,2)` | X1 |
| S1133 | the before-side `absent` is flipped (SATISFIES → FAILS) | `\bcat` on `"cat"`: PCRE2 `(0,3)`, the plant returns 0 | X1 |
| S1134 | the after-side `absent` is flipped | `(?m)done$` on `"done"` (bench syntax/anc-m-dollar): PCRE2 `(0,4)`, the plant 0 | X1 |
| S1135 | the report skips the dead-group `PCREC_UNSET` fill | bench syntax/rec-define on `"12:34"`: group 1 left unwritten | `tests/codegen/run_nomatch_caps.sh`-style group check |
| S1136 | the origin conjunct is dropped (admits a `scan-restart/ctx` site) | `(?<=\$)\d` on `"$5"`: PCRE2 `(1,2)`, the plant `(0,1)` | X1 |
| S1137 | `span_lo` is stated as `search_from` (the floor dropped) | `\bcat\b` on `"concat"`, `search_from` 3: PCRE2 no match | X1's `search_from` sweep |
| S1138 | the emitter defines the composite's description while the predicate read the REPORT ask (§2.5's order) | any `cover` site (`foobar`) | the trace build's ask-vs-define agreement assertion (rule 2), which shares no source with the predicate |

### 6.4 Checks, each against a source the subject does not share

- **X1, the libpcre2 differential over the whole-cover population.** Every artifact that
  selects `cover` in the Z2 trace build (≈ 71 + 6 bench and 686 + 84 corpus native, plus
  utf8) is compiled and run against libpcre2 10.46 (`pcre2_match` with `startoffset`, the
  PCRE2 find-all loop). Subjects:
  - product samples embedded at random offsets;
  - one-position mutants;
  - word and non-word neighbours on both sides;
  - `c = 0` and `c + k = n`;
  - `search_from` at every offset, including inside and right after a match;
  - utf8 subjects with multi-byte neighbours;
  - the D27 lesson: neighbours drawn from the bytes ADJACENT to each `S_d`, not only
    from the pattern's own alphabet.

  The expectation is PCRE2's, which shares nothing with pcrec's machine. The census's C3
  (17,721 checks, 0 failures) and C4 (6,510, 0) are X1's precursors on the reading, not on
  built artifacts.
- **X2, the plants** (§6.3), each with its reach witness. X2 checks that X1 and the
  agreement assertion can fail.
- **X3, the trace build's run-time re-test.** A trace-build `cover` artifact re-tests every
  consumed proven offset, context included, before it returns: `window_contract.md` §4.3's
  "pcrec's trace build re-tests every proven position it consumes". It checks the KIT'S
  TEXT against the stated sets and does not read the kit's form choice.
- **X4, C-PROOF** (kit-side): `proven[]` identical across SIMD off and every live level.
- **X5, the deny twin.** `make test-axes` gets the `-fno-kit-proof` arm, answer-identical
  to default over the corpus. Its expectation is the composite path, a different engine
  but pcrec's own. It is a second control, not the oracle.
- **K35, who counts the population.** The CANDTRACE `KNOWN … cover=` records count the
  SELECTED population. The census's whole-cover list counts the ELIGIBLE one; it was
  enumerated by [ARTREV]'s `census.py` and read by `kvdfa` off the emitted tables. Both
  read pcrec's machines, so the comparison is a RECONCILIATION, not a control. Its rule:
  every census whole-cover start-origin site on a DFA-finisher route is either selected or
  carries a named `why` (§5.1). The `why` histogram is published, so a class the corpus
  does not populate shows as an empty stratum, and kit declines are counted on their own
  row.

**Where to attack §6.** (a) A reader of the abi number or the scan vocabulary that the
greps above miss. A byte-count manifest is the known class. (b) Whether S1135's witness
reaches FIN2's fill, or a different writer. (c) X1's subject generator. Does it reach the
leftmost-first shapes at subject positions where two arms both fit? (d) The K35
reconciliation's `why` vocabulary: is "the kit declined" one reason, or does it hide two?

---

## 7. Staging

| step | what | who | movers | gate |
|---|---|---|---|---|
| **Z0** | R-25: `proven0`/`proven_prev` honour `need` | kit | 0 | R-25's own bar |
| **Z1** | R-26.1-R-26.5's layout; pcrec states today's truth on every site (`prefix_stated` 1, `exact_len` 0, `consumable_len` 0; MLINE as CONTEXT/FAILS/NO) | kit (+ the builder lines) | 0 | emit_sweep 0 movers on every arm; G2 extensions; one `MF_SITE_ABI` event |
| **Z2** | pcrec: the producer (§5.2), `MkKnown`, `pcrec_known_derive`, the `cover` row and `emit_cover`, ROUTED ONLY IN THE TRACE BUILD (a `routed` bit, `r17b_prime.md` §1.6's precedent; the default build's predicate reads it); true `exact_len` stated; the `--emit-facts` row | pcrec | 0 (default build) | emit_sweep 0 movers; X1 and X3 on the trace build's `cover` artifacts; the K35 reconciliation; the agreement assertion |
| **measure** | directional hand timing (dev box, a window cleared with Frank, memory `pcrec-box-shared-with-frank`): Z2 trace-build `cover` artifacts against default on lit-l8, year4, file-ext-order, hex8-bounded, `match`/`search_short`/`throughput` | lane | — | [KIT-VERIFY]'s D77 trigger: a measured consumer re-read cost on real cells. GO/NO-GO for B1 (memory `pcrec-cost-benefit-pushback`) |
| **B1** | THE ONE BYTE-MOVING EVENT: the routed bit flips in the default build; the kit's proving text on `cover` sites (the kit's choice, rendered); `PCREC_NO_KIT_PROOF`; stamps and the `"cover"` value; abi +1 with every reader of §6.1; spec hunks §6.2; S1130-S1138 land; the bench `[inbox]` note | pcrec + the kit's text in one commit | the `cover` population (≈ 71 bench, 686 corpus native) | the full battery (the manager's), mech for every new and moved anchor, `make test-axes` with the new arm |
| **official** | the bench's verdict on the targeted hardware after B1 (D144 add. 4) | bench, via main | — | — |

The kit builds R-25, R-26, its proving forms (its choice), G2's extensions and C-PROOF.
pcrec builds the builders' statements, the producer, the helper, the row, the emitter, the
stamps, the deny, X1/X3, the reconciliation and the spec hunks.

**Where to attack §7.** (a) Is Z2 truly zero-mover with a trace-build-only route? Does the
trace build ship anything a gate reads? (b) Does Z1's MLINE restatement move any kit text?
(c) Can B1 split into "pcrec's entry" and "the kit's text"? It cannot: one depends on the
other's proof. (d) Do the D161 add. 15 Q-WR-3 zero-mover posture steps (through ST3)
constrain B1's ordering against R17-b′'s routing?

---

## 8. Standing questions, the sibling family, unlocks, questions for Frank

### 8.1 The three standing questions (`docs/design/CLAUDE.md`)

1. **The measurement regime — RELEVANT.**
   - Every payoff figure here is DERIVED, from armread's Zen 4 constants (C_match 3.2-7.5
     ns at m = 8192 plus about 1.6 ns per in-match byte, kvcensus §6) and the census's
     compile-side counts. The size twin is size only.
   - The regime that could flip the decision is the kit's side: on a one-byte PF site in a
     dense regime (`\d{4}` over digit-dense text), the kit's added verification runs on
     every false candidate. That should be no more than the DFA's steps plus its re-entry,
     but nobody has measured it, and a SIMD row may decline a class position (kvp-cost m2).
   - So the `measure` step in §7 is the gate. It is a short, directional, same-box run
     over `match` (dense, per-call), `search_short` and `throughput` (sparse). The
     official verdict is the bench's on the targeted hardware (D144 add. 4).
   - The savings are per MATCH, so a sparse `throughput` cell should read near-null, and
     that is expected, not a failure.
2. **The independent control — RELEVANT.** §6.4. X1 reads libpcre2, X2 plants failing
   directions with reach witnesses, and X3 re-tests the kit's text at run time. The K35
   count is a reconciliation, stated as such, because the census and the selection both
   read pcrec's machines.
3. **What moves when data is regenerated — RELEVANT.** The kit's choice to prove may read
   the analysis object (frequency, D162). Regenerating or re-measuring that data can flip
   an artifact between `cover` and `composite`. Its answers stay identical, but its bytes
   move, which is an abi event (D162 ruling 1, "data regeneration that moves an emitted
   byte"). `RX_DFA_SCAN` shows the flip, and the [KNOW-SRC] `consulted` stamp shows the
   data was read. Regenerating the census moves nothing: it is evidence, not an input.

### 8.2 The SIBLING-FAMILY lens

- **"The match is fully known here, so report":** `cover` (the kit's proof, this note);
  [PF-KNOW]'s whole-program skip (an exact hybrid's prefilter proves the window, 164
  `det_all` hybrids, D142); RECOVER `end-minus-width` and `pinned` (a known start, so no
  reverse pass); `rev-end`'s SPAN (a known end); and the ANCHORED whole-cover with no kit
  site (`^item`, `\Gitem`, `^\d{5}$`: 11 bench / 185 corpus, including the census's "end
  anchor as pcrec's length compare"). That is at least three members of one shape, past
  the forest-for-trees threshold. **Proposal:** `cover` is SOURCE-NEUTRAL. Its predicate
  reads [MATCH-KNOWN]'s `cover` whatever the record's source. Stage 1 fills only
  `MK_SRC_KIT_PROOF`. [PF-KNOW]'s proof and an anchored compare become further sources of
  the same row (Q2), so they do not become new rows.
- **Context as a per-position fact:** MLINE's `{\n}` predicate (add. 7), the 23
  `scan-restart/ctx` shifted origins, the DFA seed table, the VM's `A_CTX`, the `-bounded`
  view family, and D164's end set. This note's machine reading (§3.2) is the general form
  for the DFA side. The shifted origins are re-expressible as a context span at -1 with
  the origin at the match start (U-ctxorigin).
- **The absent rule:** `\A`/`^` (absent required at -1), `\z` (absent at `k`), MLINE's
  edge, `\G`'s `search_from`. Here they share one bit per context span. Non-multiline
  anchors stay pcrec's.
- **The proven family** (kvp-unlock's 12 members): `proven0`, `proven_prev`, PRES
  `proven_by`/P2 `dominated`, `mf_result.proven` (superseded by §4.2), `proven_len`
  (pcrec-side `prefix`), `span_lo`/`span_hi`, LOCATE × FINISH's proven bit, the K82
  handoff, [PF-KNOW] segments, [START-LANDING], MRL `minw`/[VM-LEN-HOIST], and the D164
  end set. All of them belong under [MATCH-KNOWN] (§5.3).

### 8.3 UNLOCKS, each with its trigger (filed, not designed beyond it)

| id | unlock | trigger (D77) |
|---|---|---|
| U1b | `cover` on `CR_VM` and hybrids. Either FIN2 with CONSTANT-OFFSET group writes (in a fully known fixed-width match each group's span is a fixed pair from `c`), or a runtime split: report when `caps == NULL`, else FIN3's VM hat with ceiling `c + k`. Also VM-only context through a facts-layer `LOOK` reading. Population: bench 6 hybrid + 4 VM-context, corpus 225 + 39 + 23 | a bench cell among grp-cap/grp-named/rec-*/lka-pos/lkb-pos, or a hybrid whole-cover cell in the `match` regime, measured with VM share ≥ 10% of time (the [CAPTURES-DFA-MB] bar) |
| U-anch | the anchored and end-anchored whole-cover with no kit site: pcrec's length compare plus a kit VERIFY site (direction 1) or pcrec's own compare at the one position. 11 bench / 185 corpus | a validator cell (`^\d{5}$` shape) in the `match` regime where the anchored DFA's k steps show in the profile |
| U2 | the DFA entry past the proven prefix (`dfa-exact-prefix`) | a timed class-led cell (kvcensus §8.2: median consumable 1, ~0.38 ns/candidate) |
| U4 | send context spans to seeded DFA_SCAN/DFA_HAT sites as a filter and enter at the constant seeded row from `proven[-1]` (60 + 89 seeded sites, kvcensus §5) | a measured seeded cell (`\b…`-led) where the seed read or the re-seed shows |
| U-mline | MLINE states `absent` SATISFIES with `span_lo` 0, and pcrec's edge attempts at 0 and `search_from` retire (33 native sites) | a `(?m)^` cell whose edge attempt is measured |
| U-ctxorigin | re-express the 23 shifted-origin sites as a context span at -1 with origin = the match start, so they are no longer scan-restart sites and can be whole-cover | one such site appears in a losing bench cell |
| U-iter | the D165 iterator drives `cover`'s stream with state carried across calls | D165's build |
| U-match | `_match` on a `cover` artifact via a kit VERIFY of `k` positions instead of the anchored DFA | a `match`-regime cell measured on a `cover` artifact |
| U-union | offset-pinned union spans raise `exact_len` through a narrow multi-byte class (add. 10 unlock (b)); 65 utf8-born mixed patterns, 12 bench | the first losing utf8 cell inside a `cover` consumer's prefix |

### 8.4 Questions for Frank (discussion: problem, forces, leaning)

**Q1 — captures in U1.** *Problem:* 8 bench whole-cover cells carry live groups
(grp-cap, grp-named, rec-*), and 225 + 39 corpus sites sit on hybrids or the VM. Report
with no engine needs the groups too. *Forces:* in a fully known fixed-width match every
group's span is a constant offset pair, so the report could write them with no VM. That is
a new writer of groups, and O3 ("only the VM hat writes groups ≥ 1") would need an
exception. A runtime `caps == NULL` split keeps O3 but makes the entry's cost depend on the
caller. The bench's per-call cost for captures (I-100) says caps-wanting callers are real.
*Leaning:* stage 1 DFA-only, as drafted; U1b with the constant-offset writer as its
preferred form, since it is a [MATCH-KNOWN] fact and not a special case, when its trigger
fires.

**Q2 — is `cover` source-neutral?** *Problem:* three "fully known, so report" mechanisms
exist or are filed (§8.2). *Forces:* a source-neutral row is the general mechanism
(memory `pcrec-general-mechanisms-not-special-cases`) and costs nothing now, because only
the kit's source is filled. Naming it after the kit would invite a second row for
[PF-KNOW]. *Leaning:* source-neutral, `cover`, as drafted.

**Q3 — the `\b` "rewrite" is a reading.** *Problem:* the ruling says "a rewrite of `\b`
automatically gets added to the sent span". This note derives the context set from the
anchored machine's seed table and class-indexed accept rather than rewriting the tree.
*Forces:* the reading is an equivalence by construction and moves no byte off the `cover`
path. A tree rewrite would move every `\b` artifact on every engine and would be a second
spelling of the seed table. The cost of the reading is that VM-only patterns get no
context fact until a facts-layer reading exists (stage 2). *Leaning:* the reading, with
the facts-layer `LOOK` reading filed under U1b. Does this match what he meant?

**Q4 — one deny for the proof family, or one per row.** *Problem:* `-fno-kit-proof` would
be the first deny shared by rows in different slots (`cover` now, U2/U3/U4 later). Flag
bits are scarce: 8 free, and the hard trigger is at ≤ 4. *Forces:* one bit per T-PROOF
member would spend 4 bits for one idea and push the interface push sooner. One shared bit
cannot deny `cover` alone once U2 lands. A per-row `--memfn=`-style value deny would cost
no bit but is a new mechanism. *Leaning:* one shared bit now, and a per-row split only if
a measurement needs `cover` alone denied, filed as its trigger.

The answer-free choices are made in the note and are not questions: the row spelling
`cover`, `MF_SK_REPORT`, the two-ask order, `MF_MAX_AHEAD`'s label, and the sabotage
numbering.

**Where to attack §8.** (a) Is the regime caveat in (1) enough, or is there a cell where
`cover` is SLOWER (the kit's verification on a dense false-candidate stream that the DFA
would have rejected in one step)? (b) Does source-neutrality make `cover`'s predicate a
union whose sources can disagree about `k`? (c) Does each unlock's trigger name a
measurement that exists, rather than one that would need building first?
