# minw — searches stop where too few bytes remain ([FIND-MINW])

Lane minw (opus), 2026-11-12, branch `lane/minw` from main b2f893ffd. Brief: the
manager's LANE minw message; build go Frank 2026-11-12 "ok proceed with S1".

## STATE AT HANDOFF

- Part A BUILT and committed on `lane/minw` (abi 100 -> 103). Part B (the kit
  seam) is DESIGN ONLY: the draft kit request is under FINDINGS, for the
  manager to file as R-40. The measurement card: not added; the card format
  does not fit this stop (FINDINGS F5).
- Rulings file `docs/dev/lanes/minw_rulings.md`: empty at every checkpoint; no
  entry applied.
- Local validation (nice): `make strict` clean; `make test-codegen` green
  (21/21); `make test-cand-oracle` green (187/0, after the witness rows
  below); test-compound, test-partlayout, test-startset, test-rxtsource green;
  test-resource and test-cpset-structure green after re-pins (byte drift
  only, read; CHANGES); `make cloud-check` 15/0; a 529-case differential (13 patterns x 23 edge subjects x
  both engines, default build against the `--harness=no-min-width` stock form,
  script `$PCREC_TMPDIR/scratch/minw/diff/run.sh`, not committed): 0 diffs.
- The sabotage anchors of every row whose SAB_FILE this change touches (247
  rows) still match with their SAB_COUNT; S556 re-aimed (below), S693 re-aimed
  by the abi ritual.
- Full `make test`: dispatched to the cloud as this lane's last act
  (`scripts/cloudrun --owner main --kind test --name minw`); the axes kind is
  OWED after test is green (the change moves emitted code, and adds an
  internal axes arm).

## FINDINGS

**F1. The premise held.** `build/pcrec --emit-facts -p rx --pattern
'abc[0-9]+xyz'` reads `width [7,inf)`, and the emitted DFA search ran its
skip and scan to the subject's end with no width stop (main b2f893ffd).

**F2. Soundness, by route.** The minimum width is a lower bound on the bytes a
match consumes from its own (attempt) start, so a start with fewer bytes left
holds no match. Checked against the brief's stop list:
- lookbehind: contributes 0 (`pcrec_minw`'s A_LOOK arm; the `width` walk passes
  assertions), the context lies before the start: sound. `(?<=q)abc` reads
  `[3,3]`.
- `\K`: consumes nothing; the width counts from the ATTEMPT start, which is
  where the stop applies (`ab\Kcd` reads `[4,4]`): sound.
- lookahead past the end: adds no width: sound.
- `(*ACCEPT)` and the backtracking verbs: NOT REACHABLE today (`(*...)`
  requires module 'verbs'; ACCEPT is ROADMAP_NONE, the rest ROADMAP_NEVER), so
  no route is excluded for them. When verbs land, `pcrec_minw` and the `width`
  walk need an ACCEPT arm anyway (the VM's MRL clamps already rely on the same
  number), and this stop inherits that fix.
- partial matching: pcrec has none (no partial-match option in `lib/pcrec.h`).
- the VM hybrid's DFA prefilter: not given the stop (its language is widened by
  erasures; the VM entry checks the pattern's own width once). No exclusion was
  needed for soundness, only for path consistency (the front runs only on the
  caller-facing body).

**F3. What part A covers, and the tail it leaves (90% rule).**
Covered: the DFA forward-then-reverse search entry (`<PREFIX>_DFA_SCAN
"unanchored"`), its candidate-start skip block (every NEXT form ends in
`pf_close`, so all axis-B forms, the kit FIND forms included, get it at the
landing), the VM search entry (every VM artifact with root minw >= 2) and the
VM attempt loop's bound. Not reached, listed:
- `"attempt"` (ENG_ATTEMPT): the route has NO width source: the E3 `width`
  fact is sealed on the unanchored machine only (`decline:attempt-unwrapped-nfa`).
  The front reads WIDTH there (path-consistent) and reads `none`. Covering it
  needs a route-free width fact (e.g. an E2 `min_width` = `pcrec_minw` of the
  lowered root, the VM's own number), which would also give the VM and DFA one
  source instead of two. Proposed as the follow-up, not built (a new fact and
  listing row).
- `"cover"`, `"rev-end"`, `"landmark-walk"`, `"char-step"` bodies: no front
  WIDTH read (their LOCATE rows' `front` is PRESENCE only). `cover` already
  states its whole fixed window to the kit, so its search needs no stop.
- the forward DFA scan with NO candidate-start skip: stops only at the entry; a
  per-byte start-state test would cost every byte.
- the kit's own searches (pre-check, skip finds): part B.
- the VM's start-set seek loops (`while (attempt_position < subject_length &&
  ...)`): still run to the end; the attempt bound ends the search after the
  next failed attempt.

**F4. Where the fact cannot ride today (the brief's "today end_back").**
`mf_site.end_back` is no longer a host field: since D172 S2 commit 6 it is THE
RENDERER INTERFACE, written only by the window family's translation
(`memfn/src/window.c` `translate`), and a window site stating it is REFUSED.
pcrec states D11's holdback as a core `{1: any}` window position
(`find_window`, src/gen/emit_dfa.c), from which the translation derives
`end_back` 1 (`legacy_ok`). That vocabulary cannot carry the width: a core
full-set position at offset k-1 is bounded by `MF_WREACH` (64) and
`MF_WSPAN_POS`, and the translation takes a full-set reach of 1 only (`chi > 1`
falls out of the legacy rows), while k reaches `PCREC_MINW_MAX` (2^40). So the
fact needs its own site field; see the draft below.

**Part B — DRAFT KIT REQUEST (for the manager to file as R-40; facts only, D157).**

> R-40 (draft): pcrec states, per search site, how many bytes a USEFUL
> candidate needs after it.
>
> THE FACT. For a site whose candidates are positions c in the subject, pcrec
> states `k`: no candidate c with fewer than `k` bytes from c (inclusive) to
> the subject's end n (n - c < k) can lead to a match, so the consumer treats
> such a c exactly as it treats a miss. k >= the bytes the site's own terms
> read from c; k = 0 states nothing beyond them. It is a PROVEN lower bound;
> pcrec never states a k larger than every match proves.
>
> WHERE IT RIDES. A new frame fact on the window site and on the pre-check's
> FUNC parts, appended LAST (an `MF_SITE_ABI` move), wide enough for k up to
> pcrec's width ceiling (2^40; a 64-bit count), with an UNSTATED value refused
> where it is read (memory pcrec-no-silent-defaults): pcrec states it on every
> FIND and pre-check site, 0 included. It does not ride `end_back` (the
> renderer interface, refused on a window site) and is not a span position
> (MF_WREACH 64 cannot hold it). D11's holdback stays stated as today's
> `{1: any}` core position; where both are stated the larger bound holds. How
> the kit honours the fact (a narrower range, an earlier miss, nothing) is the
> kit's; a site that ignores it stays correct.
>
> HOW PCREC COMPUTES k, per site kind (W = the proven minimum match width in
> bytes of the route that owns the site: the `width` fact's `bmin` on the DFA
> routes, `pcrec_minw` of the root on the VM; 0 where unknown):
> - PF, the forward scan's candidate-start find (every axis-B form, DFA and
>   the VM hat): the candidate is a match start: k = max(W, 1 + holdback).
> - OFS, the offset-set skip: the candidate is a match start: k = W.
> - MLINE, the `(?m)^` skip (term at -1): the candidate is the match start
>   after the newline: k = W.
> - LMHIT, the landmark walk's occurrence search: the candidate is an
>   occurrence of the landmark L at a top-level position: k = 1 + the minimum
>   width of the elements after L (the suffix's `pcrec_minw`).
> - PRE / SETREST, the pre-check's presence parts (a necessary byte or run R
>   anywhere in [search_from, n)): k = max(len(R), W - maxoff(R)), maxoff the
>   member's (or run window's) maximum byte offset from the match start
>   (`req_set_maxoff`, `req_run_maxoff`); where maxoff is unbounded, k =
>   len(R) (no gain). A tighter k (the suffix width after R) needs a new
>   analysis and is not asked for.
> - cover: the stated window already spans the match: k = its width (states
>   nothing new).
> - The in-match ADVANCE sites (STAY, EDGE, VMSPAN, VMSTRIDE), N7 and VMRUN:
>   not match-start searches; their analogue (the continuation's minimum
>   remaining bytes, the VM's `minrest`) is NOT part of this request.
>
> WHY. Frank asked (2026-11-10) whether the kit's find window gets the minimum
> required bytes; it does not (sites trim only by their own term:
> `memchr(subject + pos + 1, 'b', n - pos - 1)` for `abc[0-9]+xyz`'s skip).
> pcrec's own loops stop at W since lane minw (tuning.md §2.55); the kit's
> searches are the remaining tail. TRIGGER for building the kit side (D77):
> the plan row's: short subjects with W a sizeable share of the subject, or a
> find-all whose final failing search dominates.

**F5. The measurement card does not fit.** The cards
(`memfn/data/cards/*.tsv`, pcrec's `tests/landwalk/card_lwalk.sh`) price a
METHOD a priced choice can pick against another. This stop is not pickable:
no row, set or argmin reads it, it fires wherever W >= 2, and its cost is one
comparison per search entry and per skip landing, against a whole search it
removes. So no card was added. What would show its benefit is a bench case of
the plan row's trigger (short-subject find-all), not a card.

**F6. Proposed ids** (the manager writes them): none needed beyond the plan
row; R-40 is the manager's to file.

## CHANGES

Commits on `lane/minw` (all `src/`, spec and test edits in the same series):
- `src/gen/emit_dfa.c`: the WIDTH slot is asked on every route
  (`cand_nodes[WIDTH]` CAND_ALL_ROUTES, `CAND_FRONT_DFA` gains WIDTH); a new
  first-match row `min-width` (`cand_min_width_applies`: W >= 2, W by route,
  `cand_min_width`) between the VM's `ceiling` and `width-none` (now on every
  route); `cand_front_min_width` reads it on the DFA fronts
  (`emit_unanchored`, `attempt_entry`); `pcrec_emit_min_width_check` is the one
  entry text both engines write; `DfaForm.minw` + `pf_close` end the scan's
  start-state skip block where fewer than W remain past the landing;
  `PCREC_ARTIFACT_ABI` 100 -> 103.
- `src/core/internal.h`: `CandWidth.ceiling` (the VM's stamped spelling)
  beside `.check`; `pcrec_emit_min_width_check`; harness lever bit
  `no_min_width`.
- `src/gen/emit_vm.c`: WIDTH read once ahead of the pre-check; `min-width`
  emits the shared check there; the ceiling block, its `_VM_ROOT_MINW` stamp
  and `--emit-ir` `root-minw` row read `.ceiling` (contract unchanged:
  `match_api.md` §6.3.8¶9); the attempt loop's bound is `subject_length - W`
  where no anchored bound applies.
- `cli/main.c`: `--harness=no-min-width` (test build only), the inverse lever
  (memory pcrec-flag-follows-caller-effect: no public bit, it only removes
  work).
- `tests/axes/run_axes.sh`: the lever joins INTERNAL_ARMS.
- `docs/spec/tuning.md` §2.55 (new, the contract); `docs/spec/match_api.md`
  abi readers; `docs/dev/history/abi_changelog.md` 103 entry;
  `tests/codegen/run_codegen_tests.sh` ABI_EXPECT + message;
  `tests/mech/sabotages/S693_abi_not_bumped.sh` and
  `S556_root_minw_unchecked.sh` re-aimed; `docs/dev/plan.md` [FIND-MINW]
  status line.
- `tests/codegen/cand_oracle_witnesses.tsv`: `min-width` witness
  `a(b|c)+d`; `width-none` now `a(b|c)*` and the lever form of `a(b|c)+d`.
- `tests/ci/cloud_axes_shards.tsv`: regenerated (`cloud_reweight.sh axes`)
  with the new arm (ESTIMATE weight).
- Re-pins, diffs read: `tests/resource/run_resource_tests.sh` cap witness
  767075 -> 767195 (+120: entry + skip-landing checks, width 5);
  `tests/codegen/manifests/m5_stage1_stamps.tsv` six EMITTED_BYTES rows (five
  VM rows +106: entry check + `attempt_max`; one DFA row +120), no stamp
  moved; notes beside each pin.

Emitted text (the premise pattern, DFA): one line after the head,
`if (subject_length - search_from < 7ULL) return 0;`, ahead of the pre-check;
one line in the skip block, `if (subject_length - scan_position < 7ULL)
return 0;`. VM: the same entry line after the range guard, and
`const size_t attempt_max = subject_length - 7ULL;` read by the attempt loop's
end test. Under the lever every artifact is the stock form (only the abi digits
differ).

## OWED

- `make test` in the cloud: `scripts/cloudrun --owner main --kind test --name
  minw`, dispatched as this lane's last act; verdict via the manager's
  queuewatch/monread.
- The cloud AXES kind, after test is green (emitted code moved; the new
  internal arm `--harness=no-min-width` joins the sweep). Not dispatched here.
  `tests/ci/cloud_axes_shards.tsv` is GENERATED (`tests/ci/cloud_units_plan.py
  axes`) and has no row for the new arm yet; regenerate it if the planner
  requires every arm to be listed.
- Mech rows S556, S693 (re-aimed): not run here.
