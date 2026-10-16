# pcscope — the PRESENCE + HANDOFF side of D161 add. 14's one window request (scoping, read-only)

Lane `pcscope` (opus, 2026-10-14). Branch `lane/memfn-pcscope`, cut from
`lane/memfn-r17`. Read-only scoping: no `src/` edit. The code of record is
main `4e6464777` (pcrec abi 78, `MF_SITE_ABI` 10), read in the detached
worktree `worktrees/pcscope-main`, which was built twice: plain, and with
`-DPCREC_CAND_TRACE`. The kit branch is a different state: pcrec abi 77
(R17-b) and `MF_SITE_ABI` 12, which already carries R17-a's window fields
W0-W2 (`mf_pred.window_stated/move_back/overshoot`) and `mf_locals`. Main
has none of these. Main's own 77/78 are the endmark/compound events, a
different change from the kit's 77.

The sibling lane `sbscope` scopes the FIND side's form choices (emit_dfa.c's
cand rows, VMSTART, MLINE's `attempt_cand`). This report covers presence, the
handoff, and how they join the find in one request. Facts and scope only; no
design ruling is taken.

Instruments (committed): `docs/dev/lanes/pcscope/census.py` (one row per
artifact from the trace build's `CANDTRACE` records plus the stamps) and
`docs/dev/lanes/pcscope/kinds.py` (folds a row into one presence/handoff
kind).

## 0. Summary

- **The merge already exists in one place.** The K82/L1 handoff's PRE site
  (`ALL_PRESENT` + `ASSIGN` on `ret_pred`) gives an empty result = `return 0`
  and a non-empty result = the first landmark hit. Its re-entry is that
  stream's next element. The ruling generalizes this shape to every PRE site
  and joins it with the start-set FIND.
- **The give-up obligation is confined to routes with NO DFA scan in front.**
  On those routes the presence answer is the call's only linear no-match
  proof. That is 248 corpus artifacts at default, 256 under `-e utf8`, 2,299
  under `--engine=vm`, and 1 rwquest question (M04).
  - Every DFA-scan front enforces the necessary set and run by itself,
    linearly, including a count-collapsed one. `src/ir/nfa.c:803`:
    `X{m,n} -> X{min(m,1),}` keeps every `rmin >= 1` byte.
  - So on those routes dropping presence moves neither an answer nor a
    give-up.
- **Three merge hazards, each with a witness compiled and run on main (§2.3):**
  1. Dropping or narrowing presence on a proof-only route reopens the K65/K66
     give-ups.
  2. Asking for presence AFTER pcrec's context-edge attempt gives up where
     today's call answers NOMATCH.
  3. An "unconstrained" reply ("present, no position information") on a VM
     route turns a match into a `frames` give-up. Start-set witness:
     `tests/startset/giveup.rxt`.
- **Presence fits window_contract.md's span terms as a span whose offset is
  bounded below and unbounded above**, which today's contract cannot state.
  - `MF_MOVE_UNBOUNDED` is permanently refused (D161 add. 5).
  - §2.2 conflates "below the origin" with "context predicate".

  The obligation it must carry is RANGE-level, not per-candidate: the
  stream is empty if the span is absent anywhere in the range, decided before
  any element is yielded. Per-candidate use is a permitted, true fact (§3).
- **Zero movers is reachable as an implement-then-replace routing step,** under
  three conditions:
  - the kit ports pcrec's five prior-priced picks verbatim, with a shadow
    comparator;
  - S1's analysis object (byte-rate, with each encoding's NONE) lands first,
    because a NULL analysis would make D162's LINER default move bytes;
  - the site keeps today's use points (entry, re-entry, VM `_run`, in-loop
    find).

  Not zero-mover: a match-start-origin framing of the handoff, the
  `--emit-facts` `used` column if pcrec sends the whole set everywhere, and
  the `--list-axes` `req-admit`/`req-use` rows plus `-fno-req-set-lead` once
  their rows move to the kit (§5).

## 1. Inventory (main 4e6464777)

### 1.1 The facts (src/facts/, `facts.def:45-55`)

| fact | owner | what it is |
|---|---|---|
| `req_set` (+ `rightmost`) | `req.c:638` `pcrec_req_walk` (`rb_walk` :488) | bytes every match contains. Alternation INTERSECTS. A lookaround body, backref, call or variable is never descended (`req.c:607-626`) |
| `req_set_maxoff` | `req.c` (`rb_union` :189) | each member's max byte offset from the attempt start (min across factors, max across branches) |
| `req_whole_run` (+ `whole_mask`, `whole_maxoff`) | `req.c:638` | the most informative contiguous run of (T,K) positions (byte or two-member cube), never joined across a repeat iteration or an assertion |
| `req_run` (window), `req_run_maxoff` | `req.c:667` `pcrec_req_window` | DERIVED: the ≤ 8-position window and scan index cut from the whole run by the prior (`findings.c:522`, `:586`) |
| `req_byte` | `req.c:709` `pcrec_req_pick` | DERIVED: the run's exact scan member, else `pcrec_find_set_pick` (`findings.c:476`; under NONE: uniform-mass argmin, ties to the rightmost) |
| `req_landmark_maxoff` | `req.c` | DERIVED: K = the run window's max offset where a run shipped, else the one byte's |
| `start_set` | `startset.c` | a superset of the first consumed byte (the FIND's span 0; sbscope's side) |

### 1.2 The decisions

All are rows of the one start table `cand_rows[]`. The PRESENCE rows are at
`emit_dfa.c:9055-9091` and the FIRST rows at `:9093-9109`. `req_admits[]` and
`req_uses[]` were deleted into these at [START-TABLE] C4.

| decision | file:line | predicate (facts read) | prior? |
|---|---|---|---|
| PRESENCE `presence-none` | `:7686` | `req_byte < 0 && req_run.len < 2` | no |
| PRESENCE `one-attempt` (G2) | `:7623` `req_route_one_attempt` | the route tries one start (BOUND's `one`). On the VM, also linear: exact hybrid (`fit.prefilter && !prefilter_collapsed`) or `vm_frameless` (K64) | no |
| PRESENCE `dominated` (G1) | `:7694`, `:7664` `req_byte_dominated_by` | the body's LOCATE `whole` (rev-end/empty) answers presence itself; or the candidate scan `cs` tests the same byte (identity); or, for a run, `cs.run_verified`; or one-byte + memchr form + `pcrec_find_no_commoner` | density arm yes |
| PRESENCE `set-leads` | `:7718` | run shipped, and `pcrec_find_pick` over {run scan cube, set pick} picks the set pick (strictly rarer; tie keeps the run) | yes |
| PRESENCE `emitted` | row :9082 | fallback | — |
| FIRST `handoff` | `:7833` `req_handoff_applies` | admission emits; the path has a DFA scan to move (`CAND_MF/MATT`); K finite; NOT `prefilter_collapsed` (Q10); not VM + `\G` seed + prefilter window (d') | no |
| FIRST `scan-from-startpos` | row :9105 | fallback | — |
| NEXT `handoff-reentry` | `:9157`, `:7943` `pf_handoff_applies` | forward, finisher not VM, FIRST = handoff, and `req_landmark_admits` (`:7920`): `1/h − K > 1/m` against the start-byte row below it (`h` the landmark hit ppm `:7887`, `m` that row's set mass) | yes |
| K65 set rest | `:1413` `req_set_rest_members` | no DFA scan (`pcrec_artifact_has_dfa_scan`, `:469`) → every set member not already tested, ascending | no |
| K66 whole run | `:1112` `req_run_tests` | no DFA scan and `whole_len > len` → the whole run compared too | no |
| gate need | `req_site_define` `:1532` | set-leads lead `MF_OPTIONAL` on a DFA-scan route, `MF_REQUIRED` otherwise; every other predicate REQUIRED | no |

### 1.3 What the kit receives today (site `PRE`, DELEG_SITES `memfn_sites.def:39`)

- `mf_site`:
  - `op` = `ALL_PRESENT`, `form` = STMT;
  - `handoff` = `ON_MISS` | `ASSIGN`;
  - `ret_pred` = the landmark;
  - `use` = DISCARD | POSITION, `empty` = MISS, `consumer` = ENGINE;
  - `on_miss_leaves` = 1;
  - `preds[]` in order: [gate byte] [run window] [K66 whole run] [K65 rest
    bytes].
- Run predicates come from `ofs_pred_of` with RQ-2's ranking `rank_*`
  (`emit_dfa.c:1179`).
- `mf_hooks` at define: `fn_name`, `note_tag`. At use (`:1648`): `s`, `n`,
  `lo`, `on_miss` (`return 0;`), `result` (`handoff_position`), `miss`
  (MISS_N under ASSIGN), `note`.
- The re-entry is a SECOND use of the same handle (`:1690`, `result`
  `landmark_position`, `lo` = `scan_position`).
- Manifest rows (`tests/memfn/site_manifest.tsv`):
  - `PRE` delegated (M1);
  - `SETREST` delegated, the composite's trailing preds;
  - `VERIFY` delegated, the RUN term inside PRE/OFS;
  - `PF`/`MLINE` delegated (the find side);
  - `OFS` delegated (the offset-skip find; sbscope's).
- pcrec text after the site: `emit_req_handoff_rest` (`:1279`). It
  subtracts K, rounds up under utf8 (`PCREC_START0_ROUNDUP`) and declares
  `landmark_position`. The forward scan's re-entry block is `pf_emit_handoff`
  (`:7033`).
- Readers outside the site, all reading pcrec's decisions:
  - stamps `REQ_BYTE` (`:13659`), `REQ_RUN`, `REQ_WHY` (`:13713`) and
    `REQ_HANDOFF` (`:13722`);
  - the prologue's `#include <string.h>` (`:13495-13510`);
  - `--emit-facts`' `used`/`why` columns;
  - the trace records;
  - the `--list-axes` `req-admit`/`req-use` listing (`cand_rows[]` `list`);
  - the denies `-fno-req-byte`, `-fno-req-run`, `-fno-req-run-fold`,
    `-fno-req-set-lead`, `-fno-req-handoff`.

### 1.4 What a merged request would need beyond §1.3

The FIND side's needs are sbscope's. On the presence side the request needs:

1. **The whole presence material, unpicked.** Every set member as its own
   one-byte presence span, and the whole run with its mask. Today pcrec sends
   only the pick and the prior-cut window, except on no-DFA routes.
2. **Per-span `need`.** REQUIRED on give-up-exposed routes; OPTIONAL
   elsewhere (§2).
3. **Offsets relative to the chosen origin.**
   - `req_set_maxoff`, `whole_maxoff` exist.
   - omin does not exist: 0 is a sound under-estimate.
   - K becomes `h_max` when the origin is the landmark.
4. **The set's `rightmost` member.** It is the tiebreak `pcrec_find_set_pick`
   reads, and zero movers needs it (§5).
5. **The analysis object's `byte-rate` with its per-encoding NONE** (D162,
   window_contract S1). It is needed because pick, window, set-leads, G1's
   density arm and the landmark admission all read it.
6. **Consumer facts the gates read.**
   - One start (G2's BOUND).
   - The body decides presence itself (LOCATE `whole`).
   - The use: DISCARD where positions may not be skipped (Q10's collapsed
     hybrid, (d')).

   The alternative is that pcrec simply withholds presence where G2 or
   `whole` holds (D161 add. 4: pcrec chooses the sub-problem). §5 discusses
   this.
7. **A kit result the stamps can read**, or pcrec's own derivation kept as
   the stamps' source (a shadow) through the zero-mover step.

## 2. The give-up obligation, per site

### 2.1 Where today's pre-check converts a give-up into NOMATCH

- **No DFA scan in front** (`RX_VM_PREFILTER "none"`). This covers a
  backreference, a linked call or a `${...}` VM, and every `--engine=vm`
  artifact. Here the presence answer is the only linear no-match proof.
  - **K65** (`known_issues.md:866`): the whole set, `req_set_rest_members`.
  - **K66** (`:803`): the whole run, `req_run_tests` `t[1]`.
  - **K64** (`:914`): G2 declines only a LINEAR one attempt.
  - Populations: GIVEUP1 groups E1-E5 and F (`tests/axes/run_axes.sh`
    ~:782-957). They are 64 `-fno-req-byte` cells across `k65_precheck_whole_set.rxt`,
    `k66_precheck_whole_run.rxt`, `k64_precheck_forced_vm.rxt`,
    `recursion/d27/sr_depth.rxt` (K34) and `litscan/reqcube.rxt`, plus
    12 `-fno-req-run` cells and H2 (`composition_d27.rxt:8336`).
- **A DFA-scan front (exact OR count-collapsed hybrid, or a DFA body).**
  Presence is speed only. The scan itself proves the absence of any
  necessary byte or run linearly.
  - The req walk takes bytes only from constructs every superset keeps:
    `rmin ≥ 1` repeats (the collapse keeps `min(m,1)`, `nfa.c:818-821`) and
    no lookaround body.
  - GIVEUP1 F2/F3 are measured empty on exactly this argument.
  - Tested: `(x?)([a-zZ]+)+ZZZ(?:@[ab]){1,16000}` (count-collapsed,
    presence = run `ZZZ` only, `@` untested) answers NOMATCH in 0.00 s on
    `a`×31+`ZZZ`. The collapsed prefilter still needs `@`.

  This is an argument plus one probe, not a check; a control is proposed in
  §6 (P8).
- **The handoff's skip (Q10).** Positions below `c − K` are skipped only
  where the prefilter is exact. On a collapsed prefilter the skipped VM
  attempts could give up, so FIRST declines there (`:7843`). This is a
  consumer rule (use = DISCARD), not a presence rule.

### 2.2 What a merged request must guarantee

- **G-1 (empty ⇒ NOMATCH, K65).** On a give-up-exposed consumer, every
  presence span pcrec marks REQUIRED binds the stream. If any one is absent
  from the range, the stream is EMPTY. This covers every set member and the
  WHOLE run (K66, no window).
- **G-2 (decided first).** EMPTY or the first element is returned only after
  every REQUIRED presence span has been established over the whole range.
  No candidate may precede a later discovery of absence: an attempt at an
  early candidate can give up before the absence is found.
- **G-3 (before the edge).** pcrec's own edge attempt (`(?m)^` at
  `search_from`/0, D161 add. 7) comes AFTER the presence verdict. That is
  pcrec's emission-order obligation, and it is today's order: the pre-check
  is at the entry.
- **G-4 (no unconstrained reply where span 0 binds).** On a give-up-exposed
  consumer the find's span 0 must stay as tight as today's (complete and
  exact) under the default rows. Today's VM hat skips only failing attempts
  (D148 Q6). A reply of "every position ≥ lo" re-creates the `-fno-start-set`
  arm's give-ups. GIVEUP1 F5 allows those for the DENY only, not for a
  default kit choice.
- **G-5 (one-way only).** An empty complete stream can only turn a give-up
  into NOMATCH, never the reverse. Candidate skipping (a non-empty stream)
  can turn a give-up into an answer. Two policies live on main and a merged
  stream has to pick one per consumer:
  - D148 Q6 ALLOWS that for the start-set hat.
  - Q10 FORBIDS it for the handoff ("never moves the give-up surface, no
    exception").

  Recorded as an open question, not ruled.

### 2.3 Witnesses (compiled with the detached main build, run with gcc -O2)

| # | hazard | pattern / subject | today | merged-request failure mode |
|---|---|---|---|---|
| W1 | narrowing/dropping REQUIRED presence (K65) | `(x?)([a-z]+)+Z.@\1`, `a`×31+`Zb` | exit 1 (nomatch), 0.00 s | `-fno-req-byte` stands in for "no presence": exit 3 (give-up), 1.56 s (K65's own repro, GIVEUP1 E1) |
| W2 | presence asked after the context edge (G-3) | `(?m)^(x?)([a-z]+)+Z.@\1`, `a`×31+`Zb` | exit 1 (nomatch), 0.00 s | `-fno-req-byte` (the edge attempt runs unprotected): exit 3 (give-up), 1.49 s. Same artifact otherwise (`RX_VM_START_SCAN "first-class"`, `VM_PREFILTER "none"`) |
| W3 | "present, no position info" on a VM route (G-4) | `(?=(?:a|b|x)*c)x`, `--engine=vm --backtrack-frames=8`, `ababababababababababababxc` | `match 24 25` (presence `x` emitted and PRESENT; the hat skips to `x`) | `-fno-start-set` (presence still emitted, no positions): `frames`, rc 3 |
| W4 | collapsed-front control (presence speed-only) | `(x?)([a-zZ]+)+ZZZ(?:@[ab]){1,16000}`, `a`×31+`ZZZ` | NOMATCH 0.00 s with `@` untested | none: the count-collapsed hybrid itself proves the absence of `@` |

W1-W3 are main's own behaviour under a deny. Each shows the give-up a merged
request would produce if the kit's choice reproduced that deny's effect.

## 3. How presence and the find merge into one request

### 3.1 Presence in window_contract.md's terms

- A presence span is a necessary span whose offset `d` from the origin
  satisfies `d ≥ omin` and is UNBOUNDED above.
  - `omin ≥ −h_max` when the origin's head is bounded.
  - When the head is unbounded (rev-inner), `omin` is `−∞` and the span is a
    fact about the call's range, not the origin.
  - Lookaround bodies are never in the set, so presence bytes lie inside
    `[match start, match end)`.
- Today's contract cannot state this, for three reasons:
  - `move_back = omax` must be finite: `MF_MOVE_UNBOUNDED` is permanently
    refused (§2.3; D161 add. 5).
  - `window_stated 0` is refused on a window site (R17-a).
  - §2.2 reads every below-origin predicate as a CONTEXT check, which is not
    a fact of every match. A set member before a landmark origin (offset in
    `[−K, maxoff]`) IS a fact of every match.
- So the contract needs a third span class beside "bounded span" and
  "context predicate": PRESENCE. It carries `omin`, has no `omax`, and has
  its own binding rule (§3.2).
- The SEQUENCE rule (`spans_seq`) does not apply to presence spans. They
  carry no pairwise distance.

### 3.2 The stream semantics (add. 7) with presence

- **Range binding (the obligation).** If a REQUIRED presence span does not
  occur in `[lo + omin, n)`, the stream is EMPTY. On the first call `lo` is
  `search_from`; for a head-0 origin this is exactly today's `[posvar, n)`
  window. EMPTY means NOMATCH, and that is the pre-check's "absent". G-2's
  ordering holds: nothing is yielded before the verdict.
- **COMPLETE, ASCENDING, span-0 starts.** Unchanged for the find's spans.
- **Per-candidate use (a permission, a true fact).** A candidate `c` with no
  occurrence of the presence span in `[c + omin, n)` can begin no match. The
  kit MAY therefore end the stream after the last occurrence minus `omin`.
  Whether it does is the kit's choice; it is never required.
- **Re-asked ranges.**
  - The binding is per CALL range. A later call with a raised `lo'` may
    re-check presence only over `[lo' + omin, n)` with `omin ≤ 0`, i.e. from
    `lo' − h_max`, not from `lo'`.
  - Today's re-entry is sound only because it runs at the start state with
    no accept pending and a head-0 landmark. That is a pcrec condition, kept
    in pcrec's text.
- **EMPTY at `lo ≥ n` or a NULL subject.** `MF_EMPTY_MISS` is kept: a pattern
  with a necessary byte cannot match zero bytes.

### 3.3 "Unconstrained" beside presence

- The legal unconstrained reply is a RANGE `[lo, hi']` of every position:
  - `hi' = p − omin` for a verified occurrence `p` of each REQUIRED presence
    span;
  - `hi' = n` only when no REQUIRED presence span exists.
- "Present, but no position information" is that range with `p` = any
  verified occurrence. When the consumer passes `hi'`, the next call
  re-verifies beyond it.
- That is legal for presence. It is NOT legal for a REQUIRED span 0 on a
  give-up-exposed consumer (G-4, W3). There, span 0 binds every candidate,
  so an all-positions range breaks completeness of skips the default
  promises.
- Where span 0 is OPTIONAL (a linear DFA consumer), the range reply is
  legal. It is exactly "run your own loop" (Frank's point 2: the kit may
  choose not to scan).

### 3.4 The handoff in the one request

- **(a) Origin = the landmark** (window_contract §2.5 as written).
  - The stream is landmark positions; pcrec keeps `max(lo, c − K)`, the
    utf8 round-up and the re-entry.
  - The start set lies in the head and is NOT in the same request.
  - The landmark admission (`req_landmark_admits`, which prices landmark
    against start-set) becomes a pcrec ORIGIN choice. D161 add. 9 says the
    origin is pcrec's only choice, and this one is prior-priced.
  - Zero-mover.
- **(b) Origin = the match start.**
  - Span 0 is the start set at (0,0); the landmark is a span at
    `[omin, K]`; the rest are presence spans.
  - The kit's chain (D161 add. 5) owns the landmark-vs-start-set choice and
    yields exact span-0 starts.
  - This is the general form, but it is not zero-mover. Today's DFA
    consumes a LOWER BOUND `c − K` and steps every byte from it.
  - It needs window_contract unlock (b) only for the k-set's offsets 1..k,
    not for the start set at offset 0. The first consumed byte is at offset
    0 of every non-empty match.

## 4. R-18 / window_contract.md impact

D161 add. 14's clarification supersedes these passages:

- **requests.md R-18 (`:392-416`).** The bullet "Presence sites carry no
  window (their own table)". Also the deliverable's "serve every degenerate
  site", because the PRE composite stops being a separate degenerate site.
- **window_contract.md:**
  - **§0 item 2 ("Presence sites keep the VERDICT reply").** Deleted.
  - **§2.2.** Add the PRESENCE class (§3.1). Split "below the origin" into
    necessary-before-origin (a span with a negative bounded offset) and
    CONTEXT (not a fact of the match).
  - **§2.3.** Carve presence out of the "bounded only" rule as its own
    class, rather than reviving `MF_MOVE_UNBOUNDED`.
  - **§2.4.** Delete the ALL_PRESENT → VERDICT row. Add:
    - (i) range binding, EMPTY ⇒ NOMATCH;
    - (ii) G-2 decided-first;
    - (iii) per-candidate use as a permission;
    - (iv) the range form of an unconstrained reply.

    "A bounded span's presence is part of FIND" becomes "every span's
    presence is part of FIND".
  - **§2.5 table.** Rewrite the "run pre-check (unbounded offset) → VERDICT"
    and K82/L1 rows.
  - **§5.4a T-PRES.** Superseded. `dominated` becomes the kit's (internal to
    the chain), `presence` stops being a separate site, and `none` stays
    pcrec's sub-problem choice.
  - **§11's R-18 outline.** Change it in step.
  - **§13 unlock (c), "presence as a chain link".** Now the contract; its
    trigger dissolves.
- **What the revision must add:**
  - the presence span class;
  - the empty-means-NOMATCH clause (G-1);
  - the decided-first ordering (G-2);
  - the give-up applicability rule. A kit row that drops, narrows (picks one
    member or a window of a REQUIRED run) or answers unconstrained over a
    REQUIRED span does not apply (K96). pcrec marks REQUIRED exactly where
    the consumer is give-up-exposed.
  - the per-consumer statement of G-5's direction policy (the open D148 Q6
    vs Q10 question).
- **`mf_site.consumer`** (unread; slated to retire at S3) does not carry the
  needed fact by itself. `need` per span does.

## 5. Zero-mover first step

**Feasible,** as implement-then-replace in R4c/R17-a's shape: shadow
comparator, then replace. It needs every one of these:

1. **The facts of §1.4 stated, and S1's analysis object landed first.** With
   `mf_site.analysis` NULL, D162's total default (LINER) would pick
   differently from today's prior-read picks. With the object present, the
   kit reads `byte-rate` as `prior-authored` (byte) or `prior-none`
   (utf8: uniform mass argmin, rightmost tie). A kit rule reading only
   `measured` provenance (D162 add. 1) must not gate these rows.
2. **Default rows that port pcrec's five priced decisions verbatim:**
   - `pcrec_find_set_pick` (with `rightmost`);
   - `pcrec_find_run_scan_index` / `pcrec_find_run_window_start`;
   - set-leads (`pcrec_find_pick`);
   - G1 (identity / `run_verified` / density via `pcrec_find_no_commoner`);
   - the landmark admission.

   The structural rows port as stated facts: none, G2's VM-linear arm,
   K65/K66 as REQUIRED-all, and gate `need`.
3. **The same use points and the same text.**
   - PRE at the DFA/VM entry (`emit_dfa.c:1648`; `emit_vm.c:13214`, the VM
     `_run` entry).
   - The re-entry inside the forward scan (`:1690`).
   - The find's in-loop use, unchanged.

   One request, several uses. The kit branch already has the host capability
   (`mf_locals`, one handle).
4. **The handoff in framing (a)** (§3.4).
5. **The stamps.**
   - `REQ_BYTE`/`REQ_RUN`/`REQ_WHY`/`REQ_HANDOFF` and the `<string.h>`
     decision keep reading pcrec's derivation (the shadow), or read a kit
     result with identical values.
   - `REQ_BYTE`/`REQ_RUN` are `SK_PATTERN` stamps, the ANALYSIS's facts, so
     pcrec keeping them is consistent.

**Not zero-mover:**

- **Framing (b) of the handoff.** Exact span-0 starts against today's
  lower-bound consumption (§3.4).
- **`--emit-facts`' `used` column.** Today `req_set` is asked on the no-DFA
  route only (`req_set_rest_members`'s own comment). Sending the whole set
  everywhere flips `used` on thousands of artifacts: emit_sweep's
  identity-required facts stream. Fix: the builder asks it only where today
  does, or the move is declared.
- **The registry.** The `--list-axes` `req-admit`/`req-use`/`prefilter
  handoff` rows (projections of `cand_rows[]`) and the deny
  `-fno-req-set-lead` move once the rows are the kit's. The latter becomes a
  `--memfn=no-…` option: a registry event, not artifact bytes.
  `-fno-req-byte`/`-fno-req-run`/`-fno-req-run-fold`/`-fno-req-handoff` stay
  pcrec's, because they change what is sent or how it is consumed.
- **Any reordering that asks presence after the edge attempt.** It moves
  bytes and breaks G-3 (W2).
- **The compound route** (`REQ_WHY "compound"`, 48 artifacts) is out of
  scope. Its parts own their entries.

## 6. Request lists

**pcrec-side facts for main to file (D157), by DELEG/manifest id:**

| id | fact | sites | size |
|---|---|---|---|
| P1 | presence spans unpicked: every set member + the whole masked run, each with `need` | PRE (+SETREST, VERIFY) | M |
| P2 | `need` REQUIRED exactly on give-up-exposed consumers (`!pcrec_artifact_has_dfa_scan`, including framed one-attempt VM per K64) | PRE | S |
| P3 | presence `omin` (new walk half; 0 sound now) + `req_set_maxoff`/`whole_maxoff` as offsets; K as `h_max` | PRE, handoff | M |
| P4 | the set's `rightmost` member (pick tiebreak) | PRE | S |
| P5 | consumer facts G2 (one start, linear) and LOCATE `whole`, OR a ruling that pcrec withholds presence there | PRE | S |
| P6 | `use` DISCARD where skipping is barred (Q10 collapsed, (d')) — exists, restated per merged site | PRE/PF | S |
| P7 | emission order: presence verdict before the context-edge attempt (G-3), stated as pcrec's obligation | MLINE/VMSTART entries | S |
| P8 | control: "every DFA-scan front enforces the necessary set and run" checked (the §2.1 argument as a census over collapsed hybrids, a planted collapse that drops `rmin`) | check | M |
| P9 | stamps source decision (pcrec shadow vs kit `mf_result`) | stamps | S |

**Kit-side work:**

| id | work | size |
|---|---|---|
| K1 | the PRESENCE span class in the window site (field spelling, refusal rules, G2 refusal cases) | M |
| K2 | stream obligations G-1/G-2 + range-form unconstrained reply; applicability rule (§4) | M |
| K3 | default rows reproducing PRE's composite (`precheck`, `precheck_assign`, `precheck_assign_byte`) inside the merged site at its several uses, zero movers | L |
| K4 | port the five priced picks with a shadow comparator against pcrec's | L |
| K5 | G2 families: absent-at-end (lazy-discovery hazard), REQUIRED-all on proof routes, re-asked ranges with `omin < 0` | M |
| K6 | `--memfn=` option for set-leads' row; registry floor | S |

Sabotage: R-18's allocated S871-S880 fit the obvious rows. Each needs its own
plant, and a plant that reads green on a DFA route only is vacuous here
(§2.1). The rows:
- K65-narrow, K66-window;
- decided-late;
- edge-first;
- unconstrained-on-REQUIRED;
- `omin` mis-sign.

## 7. Population census

**Method.** Trace build of main; `python3 -I docs/dev/lanes/pcscope/census.py`
then `kinds.py` (paths in §0). The corpus is 4,624 distinct pattern lines
from `--list-source` over `tests/**/*.rxt`. Refused: 381 (default), 380
(`--engine=vm`), 369 (`-e utf8`). rwquest is the 177 questions with their
own flags (inline `i/m/s`, `utf` → `-e utf8`, `ucp` → `--ucp`); 5 refused.

| kind | corpus default | corpus utf8 | corpus vm | rwquest |
|---|---|---|---|---|
| compound | 48 | 49 | 0 | 0 |
| none (nothing necessary) | 1,728 | 1,703 | 1,761 | 36 |
| declined G2 one-attempt | 268 | 269 | 184 | 0 |
| declined G1 dominated | 1,437 | 1,271 | 0 | 41 |
| handoff, entry only | 225 | 449 | 0 | 31 |
| handoff, re-entered (L1) | 117 | 71 | 0 | 25 |
| presence: K65 set rest | 67 | 74 | 462 | 1 (M04) |
| presence: K66 whole run | 4 | 4 | 41 | 0 |
| presence: set-leads | 5 | 2 | 17 | 9 |
| presence: run window | 52 | 56 | 381 | 16 |
| presence: one byte | 292 | 307 | 1,398 | 13 |
| compiled | 4,243 | 4,255 | 4,244 | 172 |

**The give-up obligation (presence is the call's only linear proof, no DFA
scan in front):**

| | default | utf8 | `--engine=vm` |
|---|---|---|---|
| one-byte | 160 | 165 | 1,398 |
| K65 | 67 | 74 | 462 |
| K66 | 4 | 4 | 41 |
| set-leads | 5 | 1 | 17 |
| run window | 12 | 12 | 381 |
| total | 248 | 256 | 2,299 |

- The VM one-attempt declines (59/60/184) are all `vm/none`
  frameless = linear, so they are not exposed.
- Collapsed-hybrid fronts number 1 corpus and 2 rwquest (P03, B07).
- Handoffs on the VM hybrid number 121 default / 197 utf8.
- G1's dominators at default: 674 DFA-route, 763 VM-hybrid-exact. They
  split by the scan's form as memchr 835, offset-set 274, run-pinned 125,
  first-memchr-bounded 37 and no prefilter 166. The last can only be
  LOCATE `whole`: `req_byte_dominated_by` is false without a scan byte.

**rwquest kind × mode:**

| kind | count | find-all | first | line |
|---|---|---|---|---|
| none | 14 | 20 | 0 | 2 |
| decl-dom | 13 | 27 | 1 | 0 |
| H-reentry | 9 | 11 | 3 | 2 |
| H-entry | 4 | 24 | 1 | 2 |
| K65 | 0 | 1 | 0 | 0 |
| set-leads | 1 | 8 | 0 | 0 |
| run | 0 | 16 | 0 | 0 |
| byte | 1 | 12 | 0 | 0 |

- 56 of 172 compiled questions take the handoff; it is the dominant presence
  shape in the blinded population.
- One question, M04 `<h([1-6])[^>]*>(.*?)</h\1>`, carries the K65
  obligation.
- Question ids per kind are in `build/pcs/census/rows.tsv` (regenerable).

## 8. Open questions (no ruling taken)

- **Q-PC-1.** G-5: one give-up direction policy per consumer, or the stricter
  Q10 rule everywhere a merged stream is consumed as positions?
- **Q-PC-2.** G2's structural decline and LOCATE `whole`: does pcrec state
  them as consumer facts so the kit declines, or withhold presence (sub-problem
  choice)? Either is zero-mover.
- **Q-PC-3.** Is the handoff's framing (a) (origin = landmark) the
  zero-mover step, with (b) a later byte move behind its own deny?
- **Q-PC-4.** May the kit's per-candidate cut-off (§3.2) be the default on
  find-all? It removes the K5 quadratic walk_survey found. That needs R-19's
  call mode (`mf_site.body`) to carry a verdict across calls.
