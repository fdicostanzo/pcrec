# soundness findings

## Findings

### SOUNDNESS-1 (answer, CONFIRMED) The earned skip's "exact" has no definition that excludes a run whose position sets over-cover the attempt (a PRODUCT cover), and today's run already is one
- Sheet §3.4 (earned skip preconditions), §3.3 item 3 ("c IS the least occurrence"), §2.1 (`core` = necessity only).
- Repro (today's build tree binary): `$B --engine=vm --emit-facts --pattern '(?:ac|ca)xyz'` -> `req_whole_run 616178797a/fdfdffffff`, i.e. `[ac][ac]xyz`, 5 positions = every consumed byte, omin = K = 0 (fixed), no anchor/lookaround/backref. Every literal precondition of §3.4 holds ("the run is the WHOLE attempt", "omin equals the run's largest offset", "no condition beyond the run's positions": the alternation's correlation is not a position and is not named as a condition). A kit verifying the whole run (ver_lo 0, ver_len 5, every position against its whole set, §2.2) yields c = 0 on `aaxyz`; pcrec reports (0,5) without its finish. libpcre2 10.46: `(?:ac|ca)xyz` on `aaxyz` NOMATCH; on `aaxyz caxyz` (6,11). Today's VM matcher answers both correctly (the finish runs).
- Same shape latent under set form (D187): `-e utf8` `[éĀ]` is {c3,c4}x{a9,80}, which admits `À`/`ĩ`; today's cube analysis breaks the run there (probed `qwertyu[éĀ]bcdefgh` -> run starts after the class), but §2.1 moves positions to general sets.
- Fix: the earned skip needs a stated pcrec fact "the run's byte language EQUALS the product of its position sets over the whole attempt" (sufficiency), distinct from `core` (necessity); name its home and producer, and add `(?:ac|ca)xyz` on `aaxyz` (expected NOMATCH) as the witness whose plant is "skip on necessity only".
- Effort S (doc) + a pcrec fact (M). Blast: every VM/`-fno-prefilter` whole-attempt run over an alternation.

### SOUNDNESS-2 (answer, CONFIRMED for captures by oracle + hand execution; SUSPECTED for the empty-match retry) The earned skip names CONDITIONS only; the match's other OUTPUTS and the call's MODE are not preconditions
- Sheet §3.4: "pcrec reports the hit as the match without its finish: the attempt start is c - K, and the match bounds are pcrec's consumed offsets from it".
- Captures: `(bar)(?=baz)` at L2 is run `barbaz`, omin = K = 0, attempt = run, no condition beyond the positions: every literal precondition holds. The skip reports bounds only. libpcre2 on `barbaz`: ((0,3), group 1 (0,3)); skipping the finish leaves group 1 unset. Same for `(?<=foo)(bar)` at L3, and `(*MARK:x)` names.
- `\K` (E2 makes it stop cutting the run, D191 item 3): `bar\K(?=baz)` -> libpcre2 (3,3). "consumed offsets from the attempt start" gives (0,3) unless the consumed fact already folds `\K`; the sheet does not say.
- Empty-match retry: `(?=barbaz)` (all-lookahead run, consumed 0; libpcre2 (0,0), then from 1 (6,6)). match_api §3.1.3 / L1063-1068: after an empty match at q the next call is ONE anchored NON-EMPTY attempt at q (NOTEMPTY_ATSTART). If that attempt passes the run pre-check, the skip reports (q,q) again. Confirm by reading whether the retry entry reaches the run part.
- Fix: precondition "the match has no output beyond its bounds (no capture, `\K`, MARK) and the call is the unanchored default mode", or the skip also reconstructs them; witnesses `(bar)(?=baz)` on `barbaz` (VM), `bar\K(?=baz)`.
- Effort S (doc). Blast: every earned-skip pattern with a group.

### SOUNDNESS-3 (check, CONFIRMED by hand execution + probe) C1's earned-skip plant cannot fail as specified, and its witness has no run pre-check on the default route or at the seam unit
- Sheet §2.4 C1: "a plant that reports `ver_len` one larger than the text verifies ... `bar(?=baz)` on `barbaq barbaz`, expected (7,10): pcrec skips its finish at `barbaq` and answers (0,3)". libpcre2 confirms (7,10).
- (i) For `barbaq` (0) to be yielded, the TEXT must not test position 5 (`q` vs `z`). The skip needs the reply `ver_lo 0, ver_len n` = 6. "One larger than the text verifies" gives 6 only if the text verifies exactly [0,5) AND the scan is not position 5. If the kit verifies the whole run (K38-1 reproduces today: P3's 8-position window covers a 6-run), the plant says 7: `ver_len n` fails, no skip, the answer stays (7,10), and the plant passes. If the kit scans `z` (§4 itself says "scan maybe `z`"), `barbaq` is never a candidate under any plant. So the plant reaches only under one kit choice among several.
- (ii) Route: `$B --features lookaround --emit-facts --pattern 'bar(?=baz)'` -> `RX_REQ_WHY "dominated"` on the default route (no run pre-check emitted); `"emitted"` only on `--engine=vm` / `-fno-prefilter`. And at K38-2 pcrec states `omin 0, K >= 0: no extension yet`, so the run is `bar` (n 3, `req_whole_run 626172`), not `barbaz`: the witness exists only from L2. Any C1 check run at the seam unit is vacuous.
- Fix: plant in the RENDERER (drop the compare of the last claimed position while the reply keeps `ver_len n`), build the subject FROM the reply (near-miss differing at a claimed-but-untested position), name the route (VM), and give a seam-unit witness that is a whole-attempt run with no lookaround (e.g. `--engine=vm` `barbaz` on `barbaq barbaz` -> (7,13)).
- Effort S. Blast: C1 is the only answer control for the skip.

### SOUNDNESS-4 (check, CONFIRMED by hand execution + oracle) W-K2 is not buildable as written, and W-L14's own instance cannot show its plant
- Sheet §3.5 W-K2: "a re-entry witness of span_arms W-L14's shape, the kit's half"; no pattern, subject, start or expected answer.
- W-L14's instance (`(?<=ab)ab(\w)\1` on `xababab-` from 0/3/4) is NOMATCH everywhere (libpcre2 confirms). Under W-K2's plant (re-entry floor = `lo`): from 3, re-ask at 4 from floor 4 finds no `abab` -> NOMATCH; the correct floor 2 gives c 3, attempt 5 fails -> NOMATCH. Same answer: the plant passes.
- A witness that reaches: `(?<=ab)ab(\w)\1` on `abababcc` from 0 (VM route, K = omin = -2). Correct: c 0, attempt 2 fails; re-ask at lo 3, floor 1, c 2, pos max(3,4) = 4 -> (4,8), libpcre2 ((4,8), g1 (6,7)). Plant (floor 3): no `abab` at or after 3 -> NOMATCH.
- Note it is pcrec-driven only from L3; at the seam unit it must be a G2 case (the kit's generated presence space with omin -2, re-entry lo 3 on `abababcc`, expected candidate 2).
- Effort S (doc).

### SOUNDNESS-5 (check, CONFIRMED by reasoning) W-K4's guard page cannot catch its own plant; only ASan can, and only at a misaligned subject
- Sheet §3.5 W-K4: plant "a vector form reads its block aligned down from `floor`"; witness "the subject at a page start, a guard page below offset 0"; fails "a fault (G2) or an ASan report".
- An aligned-down load never crosses a page boundary (page size is a multiple of every vector width), so with the subject at a page start, aligning down from offset 0 lands ON offset 0: no read below 0 at all, no fault. With the subject anywhere else the aligned-down block stays inside the subject's own page: still no fault. The guard page fires only for an UNALIGNED read below 0 (e.g. an unclamped `lo + omin` used as a pointer), which is not the stated plant.
- ASan catches the aligned-down read only when the subject start is NOT aligned to the vector width (malloc gives 16: an AVX2/AVX-512 block aligned down reads 16-48 bytes of the left redzone); at a 16-aligned SSE2 subject it reads nothing below.
- Fix: two plants, each with its reaching subject: (a) unaligned read from an unclamped floor -> guard page at page-start subject; (b) aligned-down read -> ASan with the subject at offset 1..W-1 from a W-aligned heap start, per level. Goal 4's "no read below 0" otherwise has no failing witness for the aligned idiom.
- Effort S (doc + G2 harness).

### SOUNDNESS-6 (check, CONFIRMED by reading) W-K3's observable is pcrec's record, which does not exist where the sheet runs it
- Sheet §3.5 W-K3 fails via "`req_pick_shadow`'s `landmark` record disagrees"; the sheet then says W-K1..W-K4 are G2 witnesses at the seam unit because pcrec states no negative `omin`/K before L3 (K38-2's pcrec hunk: "omin 0 and K >= 0").
- `req_pick_shadow` is pcrec's (`src/gen/emit_dfa.c:11146`); G2 drives the kit alone. At the seam unit no pcrec site has K < 0, so no record can disagree; in G2 there is no pcrec margin to compare with. The plant (twin reads K unsigned) ships green through K38-2.
- Fix: give W-K3 a G2 observable read off the kit's own output with an independent expectation (e.g. the landmark port's admission bit for K in {-32..-1} must equal the admission at K 0, generated from the stated spec rule, not from `presence.c`), and keep the pcrec-record form for L3.
- Effort S.

### SOUNDNESS-7 (check, SUSPECTED; confirm by building the lever) C4's seam-unit lever does not exist, contradicts the lever contract, and its typical difference is invisible to C4's check
- Sheet §2.4 C4: at the seam unit "the kit's test-only lever (`mf_lever`, a reversed tie) supplies the difference"; the check reads "`@idx` names the position whose SET the emitted find scans".
- `mf_lever` today lists one lever, `pres-window` (`memfn/src/compose.c:1400-1403`), and its contract is "restores, on this art, the OLD form a kit change replaced" (`memfn/include/memfn.h:1471-1477`). A reversed tie is not an old form: a new lever kind, unnamed in K38-1/K38-2's unit rows.
- Ties come from `rate[]`, which is indexed by BYTE VALUE (`pcrec_find_run_scan_index`, `src/core/findings.c:745-764`): under the default prior and the measured rates, tied run positions are overwhelmingly positions holding the SAME byte (`abab`, `eeeee`). Reversing such a tie moves the scan to another position with the identical set, so the emitted find scans the same set and C4's "position whose set" comparison passes under the plant. It reaches only where tied positions hold DIFFERENT bytes, i.e. the all-tie regime (`--analysis=uniform`) or `-e utf8` NONE.
- Fix: the check compares the find's OFFSET (position), not only its set; name the regime the seam-unit C4 runs in (all-tie); add the lever to the K38 unit that builds it, with its own contract sentence.
- Effort S.

### SOUNDNESS-8 (doc/check, CONFIRMED by reading) Three sheet statements about where `scan` lies contradict each other; C2 would red a legal lossy scan
- §2.3: "`scan` need not lie inside the verified extent (a scan by a lossy cover is not a proof)", and `ver_len` 0 = none proven (§2.2).
- §6 Q2 recommended (a): "the verified extent with `@` the scan INSIDE it". With `scan` outside `[ver_lo, ver_lo+ver_len)` or `ver_len` 0, (a) has no spelling.
- §2.4 C2: G2 classifies "the run part's find byte is `scan`'s set". Under D187 add. 1 a lossy covering cube is the reader's legal private test, so the find's byte set is a SUPERSET of `scan`'s set: C2 reds a correct text. (Soundness itself holds: a superset scan misses no occurrence, so §3.3 item 2 survives.)
- Fix: Q2(a) spells "`@` the scan position, which may lie outside the shown extent; extent empty when `ver_len` 0"; C2 reads "the find's byte set CONTAINS `scan`'s set, and equals it unless the reply says the scan is lossy" (which then needs a reply bit, or C2 accepts containment only).
- Effort S.

### SOUNDNESS-9 (check, CONFIRMED by hand execution; minor) W-L1's plant "scans from `lo`" is invisible under one natural spelling
- Sheet §3.5 W-L1 / §2.4 C1 second plant: `(?<=foo)bar` from 3 on `foobar`, expected (3,6) (libpcre2 confirms, also from 0,1,2; NOMATCH from 4).
- If the plant moves the CANDIDATE floor to `lo` (position j searched from `lo + j`), every scan j misses: NOMATCH, the plant fires. If it moves the BYTE-search start to `lo` (position j searched from offset `lo` instead of `floor + j`), then for any scan j >= 3 (`b`,`a`,`r`) the byte is still found at offset j >= 3, c = 0, answer (3,6): the plant passes. Whether it fires depends on the kit's scan pick (rates).
- Fix: state the plant as "the candidate floor is `lo`" and add a subject where the needed occurrence's SCANNED byte also lies below `lo` (or pin the scan to a lookbehind position with the C4 lever).
- Effort S (doc).

## PROBED-AND-HELD

Held (hand-executed against libpcre2 10.46 answers; 30 oracle probes, 22 compiles):
- §3.3's floor `max(0, origin + omin)` with fixed placement (omin = K): least occurrence at or after the floor gives the leftmost attempt at or after `search_from`, including the clamp at 0 (`(?<=foo)bar` from 0..4 on `foobar`: (3,6)x4, NOMATCH; `(?<=a)a` on `aaa` from 0,1,2: (1,2),(1,2),(2,3), lookbehind into the previous match), and the overlapping lookahead case (`bar(?=bar)` on `barbarbar` from 0, 3: (0,3), (3,6)).
- pcrec's move `max(posvar, c - K)` at signed K, entry and re-entry: W-L13/W-L14 shapes and `abababcc` (SOUNDNESS-4) hand-run to libpcre2's answers; no backward move, no repeat when compared signed; non-fixed placement re-yields the same c only while posvar is inside its serving range, so it terminates.
- §2.3's lossy scan is sound for answers (a superset scan misses no occurrence; §3.3 item 2).
- W-K1 (`(?<=foo)bar` from 1, size_t wrap -> NOMATCH vs (3,6)) reaches as spelled.
- utf8: today's cube analysis breaks the run at a non-product class (`[éĀ]`) and at `(?i)s`/`(?i)k` (probed); `[éè]` stays an exact cube. Latent only under set form (SOUNDNESS-1).
- Default route `bar(?=baz)` is `dominated` (no run pre-check); VM and `-fno-prefilter` emit it (probed).
- Today's VM matcher answers `(?:ac|ca)xyz` correctly (`aaxyz` nomatch, `aaxyz caxyz` 6 11).
