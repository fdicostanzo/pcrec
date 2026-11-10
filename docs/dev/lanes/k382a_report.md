# k382a — R-38 K38-2a: the in-run stop as a reader, the probe lever, G2's presence family

Lane k382a (opus), branch `lane/memfn-k382a`, cut from main 7658295b3 (K38-1 landed). Charter:
`docs/design/memfn/span_runs_sheet.md` rev 1.3 §5's K38-2a row (with §2.4 C2, §3.3, §3.5 and §5's
Order paragraph); the oracle seam `docs/dev/lanes/k382a_oracle_iface.md`. MF_SITE_ABI 26 unchanged;
ZERO emitted bytes at default (measured below).

## Summary

- **The in-run stop** (window.c `a_mass_choose`, Table A's stop inside a verify-YES run) now asks
  `kit_run_decide`, the ONE run decision, and is a counted reader in `decider_census.py` section D
  (`a_mass_choose: 1`). It reproduces today's stop under the incumbent tie (proof sketch in its comment;
  measured: no byte moved).
- **The probe lever `run-tie-left`** (test-only): `mf_lever(art, "run-tie-left")` sets
  `KIT_LEVER_RUN_LEFT`; the decision's options (`kit_run_opts_of`, presence.c) then break its ties
  LEFTMOST (TIE row `T_RUN_LEFT`, `TIE_LOWER`). One function, so scan, stretch, twin mass, ranking and
  the in-run stop move together; the verify-NO prefilter member stays on `T_MASS_STRETCH` on purpose.
  pcrec's arm: `pcrec-harness --harness=run-tie-left` (cli/main.c, `PcrecHarnessOptions.run_tie_left`,
  src/gen/memfn_sites.c).
- **G2's presence family** (`memfn/tests/run_g2_pres.sh`, run_g2.sh section 4p): GENERATED pre-check
  sites in today's form (omin 0, K >= 0) on routes P0/P2/P3/P9, laid out as a host lays them out, one
  pass per U2 target (x86-64-v3, x86-64, generic) x {default, run-tie-left}. It reaches the run part
  on every route that has one, counted per route; P2, which has none by C2's third clause, is held by
  its refusal control. 558,119 checks, 0 failed, 64 s.
- **The oracle seam**: every run-part call through an entry or re-entry use writes one record in
  exactly the k382a_oracle_iface.md format (50,178 records over the six passes), `reads` from the
  compiler's own instrumentation of the kit's text. **`tests/memfn/occurrence_oracle.py` does not
  exist in this tree: the oracle step prints `ORACLE OWED` and counts no pass.** That is the oracle
  author's (lane k382o) half, not this lane's; no oracle was written here.
- **C2's text classifier** agrees with today's kit on the whole generated space (COVER, EXTENT, SCAN,
  SOUND; P2's control).
- **Plants**: S3007 (A) RED, S3009 (C) RED, S3008 (B, the oracle's plant) OWED with its reach
  measured by hand; mech rows S3007-S3009 on the new arm `g2pres`, REACH_ONLY reached on all three.
- **Gate jobs 540-549** (`kit-k382a-*`) written and dry-run, NOT queued.
- **Re-anchored**: S1095 (the decision's tie now arrives in its options, `o.tie`) and S3006 (the
  ranking's call spells the options); `scripts/m6read_check_sab_anchors.py`: all anchors resolve.

Commits: bdf5c2ff4 (kit + pcrec arm + census), c879cd088 (the family, mech arm, rows), and this
report's commit.

## The in-run stop as a reader

K38-1's finding was that `a_mass_choose` read `T_MASS_STRETCH` through `kit_pick_takes` directly: a
second spelling of the run decision's tie inside a verify-YES run. The kit ruling [r1.3 K7] asked
for it to become a counted reader of `kit_run_decide` before the lever landed.

- **What changed** (window.c `a_mass_choose`): when the alternative states a verify-YES run R, the
  stop inside R is no longer every stretch position's own argmin. It is the position the run
  decision names. The function walks the decision's ranking (`kit_run_decide` with `after`, as
  `translate` does) to the first position that is a legal stop (`stop_ok`) and a stretch position.
  Every other stretch position inside R is skipped. Positions outside R, and every set position,
  compete exactly as before. A verify-NO run, and an alternative with no run, are untouched.
- **Why no byte moves at default:** under the incumbent tie the decision IS today's least-mass,
  ties-to-the-higher-offset pick over R's sets. Today's loop applied the same row (`T_MASS_STRETCH`)
  to the same masses at stretch positions. Its winner inside R is therefore the decision's first
  legal-stop position, and the comment in `a_mass_choose` carries the sketch. Measured, not only
  argued: the hand sample below and gate jobs 541-543's identity arms.
- **Counted:** `tests/memfn/decider_census.py` section D now maps `kit_run_decide` to
  `{kit_pres_picks: 1, run_member: 1, translate: 1, a_mass_choose: 1}`.
  - `MEMBER_COUNT` 65 to 66: the new member `kit_run_opts_of`, a row in `decider_census.tsv`
    (T-VERIFY,TIE).
  - `HITS` 60 to 61: the `TIE_LOWER` in the new TIE row.
  - The `translate:run-rank` anchor was re-aimed. The census run: 96 passed, 0 failed.
- **The census backstop caught one shape on its own:** the lever bit was first named
  `KIT_LEVER_RUN_TIE_LEFT`, and its `TIE_` matched the backstop's tie grep. It was renamed
  `KIT_LEVER_RUN_LEFT` rather than widening the backstop.

## The probe lever

- **Kit:**
  - `KIT_LEVER_RUN_LEFT` (kit.h) and the row `{ "run-tie-left", KIT_LEVER_RUN_LEFT }` in compose.c
    `kit_levers[]`.
  - `kit_run_opts` (`{ kit_run_stretch st; int tie; }`) is `kit_run_decide`'s new options argument.
  - `kit_run_opts_of(art, st)` (presence.c) is the ONE place the lever is read. It gives `T_RUN_LEFT`
    under the lever and `T_MASS_STRETCH` otherwise.
  - All four readers pass `kit_run_opts_of(...)`: `kit_pres_picks` (scan, P3's window, the twin's
    mass), window.c `run_member` (verify YES), `translate` (the RQ-2 ranking) and `a_mass_choose`.
    So the lever moves them together by construction.
  - The verify-NO member (`run_member`'s other arm) still calls `kit_run_member` with
    `T_MASS_STRETCH`: the charter's "the lever leaves the verify-NO member behind on purpose".
  - New TIE row `wf_ties[T_RUN_LEFT]`: TIE_LOWER, code "none: no shipped compile reads it". Its
    basis is C4's reaching regime.
  - The C-member rule string in window.c is RESPELLED to name both tie rows. It has no reader (no
    code prints or compares it), and the hand sample's artifacts are identical. The traced output
    BASE vs HEAD is gate job 544's (reach_equal).
- **pcrec:** `--harness=run-tie-left` (cli/main.c, the harness binary only), carried as
  `PcrecHarnessOptions.run_tie_left` (src/core/internal.h, the seventh harness bit). It is applied in
  src/gen/memfn_sites.c by `mf_lever(job->mf, "run-tie-left")`; a refusal is an internal error.
  - It is NOT an axes arm (cli/CLAUDE.md item 7).
  - The lever fence (`tests/compound/run_lever_fence.sh`) passes: 3 checks, 4 controls.
  - No `docs/spec` hunk: a `--harness=` option is fenced OUT of the spec by that check, and nothing
    a caller of `pcrec` sees moved.
- **Observed:**
  - `pcrec-harness --harness=run-tie-left -e utf8 abcd` stops at `req_run_member`'s agreement check:
    "the window family's run member 0 is not the run window's own index 3". That is the sheet's
    expectation before K38-2: the kit moved leftmost, pcrec's index stayed rightmost.
  - A pattern with no tie compiles byte-identical with the lever.
  - Its G2 observable is the presence family's lever witnesses (below): 24 of 24 per target moved.

## The presence family

Files (all under `memfn/tests/`, written by the lever's author, not D27-blinded; its own process and
RNG stream):
- `g2/g2_pres.h`: the site table, no memfn.h.
- `g2/g2_pres_gen.c`: the generator, the only kit caller.
- `g2/g2_pres_run.c`: the driver.
- `run_g2_pres.sh`: the runner; run_g2.sh section 4p, so `make test-memfn-g2` runs it.

- **Generator:**
  - Each site gets:
    - a run of 2-32 positions, each one member or a one-bit pair. A quarter of the runs are
      caseless, the only shape whose scan is a pair, which is what reaches the SIMD rows;
    - 0-3 set members;
    - rates of four kinds: none, skewed, uniform (all ties), or tie-heavy over the site's own bytes.
  - It states the presence spans as `req_pres_spans` does: members in descending byte order, the run
    last, omin 0.
  - It routes the site:
    - P0: every span REQUIRED, the VM attempt's consumer kind;
    - P3: OPTIONAL;
    - P9: OPTIONAL under `--memfn=no-fd-pres-pick`;
    - P2: OPTIONAL with the start search's proof standing for the leading check.
  - The route is READ BACK from `mf_class.pres_row` through `mf_finder_rows`, never assumed.
  - It asks `mf_pres_ports` and `mf_ask`, then lays the parts out as `req_site_define` does, held
    by the kit's own `pres_layout_check`: the head member, then the run's window, then the whole run
    where the link keeps it whole and it is longer, then the rest ascending.
  - It defines the site and renders the ENTRY use (lo `search_from`) and, on an ASSIGN site (a run
    part is `ret_pred`, K 0-39), the RE-ENTRY use (lo `posvar`).
  - It also renders 24 LEVER WITNESSES per pass: 4-8 distinct exact bytes under uniform rates, on P0
    and P3.
- **The generated file**, per pass, in this order:
  - the target's family guard and `mf_include_c` lines;
  - the recorder's libc block;
  - the target's region around the kit's text;
  - after each definition, a direct call of each rendered part (`g2p_part_<id>_<k>`, the
    classifier's), then `#define <fn>(...)`, which sends every later call through the recorder;
  - the entry and re-entry wrappers.
- **Population per pass**, identical across targets and lever states:
  - 424 sites; 347 rendered (P0 92, P3 175, P9 80); P2 77, every one an untested link, held by its
    control.
  - 369 run parts.
- **Reach, counted per route, per pass** (entry + re-entry run-part calls, the least over passes):
  P0 2132, P3 4162, P9 2032; of them re-entry 744, 1540, 790. P2 has no run part by contract; its 77
  sites are each refused when a run part is laid out anyway (`p2_refused`).
- **Both layers, every admitted level:**
  - SIMD sites (a run part with a w16 / w32 arm): x86-64-v3 20 and 20; x86-64 20 and 0; generic
    (the OFF layer) 0 and 0.
  - A level the target does not admit must render NOTHING: exact-0 checks.
  - The SIMD arms RAN: vector loads of the subject seen by the recording build, x86-64-v3 1,314 and
    x86-64 1,104.
  - Host gate: x86-64-v3 runs only where the host has AVX2+BMI2. A skipped arm prints `SKIPPED ARM`
    and counts as a failure (the floors are per pass).
- **Builds per pass:**
  - plain `-O1 -Wall -Wextra -Werror` (the kit's text compiles warning-free);
  - the RECORDING build: the kit's text at `-O2 -fsanitize=kernel-address --param
    asan-instrumentation-with-call-threshold=0 --param asan-stack=0 --param asan-globals=0`, so
    every load is an outlined `__asan_load*_noabort` call the driver supplies;
  - the ASan+UBSan build.
- **The oracle records:**
  - `site` is `<target>.<lever>.<id>.p<part>`. `call` is entry or re-entry. `origin` is the `lo`
    the part was called with.
  - `omin` is 0. `sets` are the part's own positions, in the seam's bitmap encoding (checked by
    hand: byte 0x43 lands on hex digit 47, value 8).
  - `ver_lo`/`ver_len` are `mf_wdecide`'s stretch for the part's own statement. `result` is the
    candidate, or `MISS` at `>= n`.
  - `reads` are every subject offset the part read during the call: instrumented loads plus the
    libc reads (memchr up to and including its hit, memcmp and memcpy their whole lengths).
  - The family holds its own records to the seam's format (column count, hex, sets, decimals)
    before the oracle step.
  - The oracle step pipes all passes' records (one header) to `python3 -I
    tests/memfn/occurrence_oracle.py`. Green needs exit 0 AND a trailer `rows=<every record>
    violations=0`.
  - Absent, it prints `ORACLE OWED: ... N records written, NOT checked (not a pass)`.
- **The records are in the PART frame.** A run part is a function of its own statement: the
  window's positions on P3, the whole run on P0/P9. Its candidate `c` is the subject offset of the
  part's position 0, so `sets` and `ver_*` are the part's. Today a P3 window candidate can lie below
  the origin in WHOLE-run coordinates; that frame is K38-2's matter (negative omin), not
  representable at omin 0.
- **Floors** (K35): literals in run_g2_pres.sh, the least over the six passes less ~10%, sharing no
  source with the family. Every floor is per pass.

## The text classifier

C2 (§2.4) says the reply describes the text: the run part's find byte set CONTAINS the scan's set,
its compares cover exactly `[ver_lo, ver_lo + ver_len)`, and there is no run part where the link is
untested. The classifier reads the RENDERED TEXT by behaviour, through a direct call of each part,
never the decision function. Per part:

| check | what it holds | how |
|---|---|---|
| COVER | the find's set contains the scan's set (a superset or an ANDed second position still finds) | every member of every position placed in an occurrence strictly above `lo` (ending at n, short, and long enough for a SIMD arm) must be yielded |
| EXTENT | the compared positions are exactly the reply's stretch | an occurrence broken at position j (the filler, a byte in no set) is yielded iff j lies outside `[ver_lo, ver_lo + ver_len)`; short and long subjects. Per site, the union of the parts' measured extents must equal the site's reply (P3's window, or the whole run), and some part must state it |
| SCAN | the text's find reads the reply's scan position | the first subject read on a no-candidate subject of `len + 2` bytes (short enough for the scalar body), part frame, then site frame against `mf_pres_ports`' `run_scan` |
| SOUND | a yielded candidate holds | on random subjects (to len + 120) any yield is `>= lo`, inside the subject, and holds every compared position |
| untested link | no run part where the link is untested | the generator's P2 control: a run part laid out on a P2 site is refused by `mf_define` (77 per pass; the refusal names "no presence link verifies a span") |

Per pass: COVER 12,729-12,783 probes, EXTENT 6,254, SCAN 369 parts (92/175/80 sites), SOUND 8,856.
All agree with today's kit on the whole generated space, all six passes.

A finding about the SCAN definition, taken into the check rather than left as a red:
- On subjects long enough for a SIMD arm, the "first read" is the compiler's scheduling of the
  ANDed second position's load. On three sites in 344 it named another position (e.g. a pair
  scanned at 1 whose ANDed word at 0 loaded first).
- C2 allows the AND, so SCAN is measured on the scalar body (subject `len + 2`), and the SIMD arms
  are held by COVER.
- The text's scan offset in a SIMD arm is therefore not read directly; that is a limit of this
  classifier, stated, not a pass.

## Guard and ASan placements

§3.5's W-K4 placements, built now on today's form (omin 0), so K38-2's negative-omin sites inherit
them unchanged:
- **Layout U**: the subject ends at a guard page (`s + n`). Every direct part call (the classifier's)
  and every entry/re-entry call runs here; the records come from this layout.
- **Layout L** (W-K4a's): the subject at a page START with a guard page below offset 0. Every
  entry/re-entry call runs again here. A fault is caught (SIGSEGV/SIGBUS, `siglongjmp`) and is a
  failure naming the layout. 8,784 calls per layout per pass.
- **Layout A** (W-K4b's, the ASan+UBSan build):
  - Placement: the subject at offset 1..W-1 (W 16 and 32) from a W-aligned `posix_memalign` block
    of EXACTLY `off + n` bytes. The block's whole 8-byte granules below the subject are poisoned
    (`ASAN_POISON_MEMORY_REGION`).
  - Calls: every part directly, the entry and the re-entry.
  - Count: 15,962 placements per pass, on every target's text (x86-64-v3's w32 and w16 arms
    included).
  - **Stated limit:** ASan's shadow cannot poison the `off % 8` bytes just below `s` in the same
    granule. A read up to 7 bytes below the subject inside the block's first granule is NOT seen.
    The guard page of layout L covers the page-start case.
- The ASan+UBSan driver also runs the whole classifier: 46,101-46,155 checks per pass, 0 failed.

## Plants

| id | plant | detector | measured |
|---|---|---|---|
| S3007 (A) | runcmp.c `rc_emit_words`: position 0 never compared (mask and value 0x00) | C2's classifier, EXTENT | `--plant S3007` RED: "EXTENT: part at 0 len 6: position 0 is NOT compared, the reply's stretch is [0, 6)" |
| S3008 (B) | ofsskip.c `memchr_body`: a verified candidate equal to the call's `lo` is skipped, so a candidate ABOVE the least occurrence is yielded | the ORACLE STEP (§3.3 item 2) | `--plant S3008` reads **OWED** ("its detector is the oracle step, and the oracle is OWED: NOT DETECTED"); reach measured by hand, below |
| S3009 (C) | presence.c `kit_run_opts_of` ignores the lever (ties stay rightmost) | the lever witnesses | `--plant S3009` RED: "LEVER: a tie witness's text scans 5, the stated rule (run-tie-left: leftmost) is 0" |

- **Plant C's witness**, read in G2 only (no pcrec observable before K38-2):
  - The witness is an all-tie run of distinct bytes under uniform rates.
  - Its text's scan is read as the first subject read and held to the STATED rule: rightmost by
    default, leftmost under the lever. The expectation comes from the rule, never from the reply.
  - The runner also requires every witness's scan to MOVE between the default and the lever pass of
    the same target: 24 of 24 on each of the three targets.
- **Plant B is the oracle's plant**:
  - The classifier puts its occurrences strictly above `lo` on purpose: the occurrence contract is
    the oracle's, not a second copy of it in the family.
  - **The first form was REJECTED.** Starting the search at `lo + 1` shifted the text's first read,
    and the family's SCAN went red. The plant was moved to a form whose reads are unchanged until a
    candidate verifies.
  - Its reach, measured by hand (`$PCREC_TMPDIR/scratch/memfn/k382a/hand_b.py` over one generic
    pass's records): 415 records hold an occurrence at their origin. The clean kit yields the origin
    on all 415 (0 moved); the planted kit moves 322.
  - An oracle implementing item 2 must therefore red; until it lands the row is declared UNDETECTED
    and listed **OWED**. It flips to DETECTED in the change that lands
    `tests/memfn/occurrence_oracle.py`.
- **Mech:**
  - Rows `tests/mech/sabotages/S3007_*`, `S3008_*` (two sites in one file, `SAB_FILE2`) and
    `S3009_*`, on the new arm `g2pres` in `tests/mech/run_sabotage_matrix.sh`. The arm runs the
    sabotaged tree's `run_g2_pres.sh` with `G2P_NOASAN=1`.
  - Their reach probe is `run_g2_pres.sh --reach`, a ~5 s census on the clean tree printing
    `REACH-G2P-WORDS-COMPARE`, `REACH-G2P-MEMCHR-FORM` and `REACH-G2P-LEVER-PASS`.
  - `REACH_ONLY=1` over S3007 S3008 S3009 S1095 S3006 at c879cd088: 3 reached, 0 unreached, 2 no-probe
    (S1095, S3006 declare no probe, as before).
  - Ids are the top of the free range (S3005/S3006 were the highest).

## Gate jobs

`/var/tmp/pcrec-pcrec/scratch/memfn/k382a/jobs/`, keys `kit-k382a-*`, numbers 540-549, copied from
`k381g/jobs` and re-pointed:
- TREE is `worktrees/k382a`, BASE is `7658295b3`.
- REF is the niced plain BASE build from `git archive 7658295b3`, at
  `scratch/memfn/k382a/base/build/pcrec`, built by this lane.
- Outputs go to `scratch/memfn/k382a/gate/`.
- Every job's `--dry-run` passes. NOT queued (the kit manager queues).

| job | what | change from K38-1's set |
|---|---|---|
| 540 strict | `make strict` | re-pointed |
| 541-543 ident | 71 identity arms (67 declared at 7658295b3 + 4 targets), BASE vs HEAD, every arm identical | re-pointed (K38-2a moves no byte) |
| 544 reach | reach equality, 21 arms, + basis.py | re-pointed |
| 545 test | `make test` via perfrun; rows_check §P plants, RUN CALLERS plants | + `== k382a presence family PASS` (run_g2.sh 4p inside test-memfn-g2) |
| 546 plants | window plants (26, each RED) | + THE PRESENCE FAMILY whole (with ASan) + `--plants`: S3007/S3009 RED, S3008 OWED |
| 547-549 mech | K38-1's 75 rows | + rows_for over K38-2a's changed files: S526 (memfn.h); cli/main.c S1228 S1245 S1380 S1582 S1740 S1867; src/core/internal.h S1187 S1340 S1440 S1480 S236; src/gen/memfn_sites.c S1031 S1294 S1332 S1870 S1885 S2902 S2904 S2905 S2911 S571 S678 S994; and S3007 S3008 S3009. 102 rows, 34 per shard, est 3300 s, cap 7200 s |

The three pcrec files each gained ONE additive test-only harness option. Their rows run as
drift witnesses, following K38-1's rule (every row planting in a changed file).

## Charter-vs-committed checklist

| charter item (brief / sheet §5 K38-2a row) | committed | where / evidence |
|---|---|---|
| 0. the in-run stop a counted reader of `kit_run_decide`; census section D moves | YES | window.c `a_mass_choose`; decider_census.py RUN_CALLERS `a_mass_choose: 1`; census 96/0 |
| 1. lever `run-tie-left`, ties leftmost, test-only, pcrec `--harness=` arm; moves scan, stretch, twin mass, ranking, in-run stop together | YES | `kit_run_opts_of` (one reader of the bit) passed by all four readers; cli/main.c + internal.h + memfn_sites.c; fence green |
| 1. respell the stale window.c rule string only if no default trace byte moves | YES (respelled) | the C-member rule string has no reader (no code prints or compares it); hand sample's artifacts identical; MF_TRACE output BASE vs HEAD is gate job 544's (reach_equal) |
| 2. generator: set-member spans + a run span, today's form (omin 0, K >= 0) | YES | g2_pres_gen.c |
| 2. routes P0/P2/P3/P9, both layers, every admitted level of the U2 list | YES | per-route census read back from `pres_row`; 3 targets; SIMD exact-0 / floors |
| 2. the derived run part, run on generated subjects | YES | entry/re-entry uses, layouts U/L/A |
| 2. REACH the run part on every route it generates, counted per route | YES (P2 by its control) | `G2P reach` floors per route per pass; P2 has no run part by C2, held by `p2_refused` |
| 3. one record per run-part call (entry and re-entry), exact seam format, reads instrumented | YES | g2p_rec; format self-check; 50,178 records |
| 3. pipe to `occurrence_oracle.py` if present, else report OWED (not a pass); do NOT write an oracle | YES (OWED) | the file is absent at c879cd088; no oracle written |
| 4. C2's text classifier agrees with today's kit on the whole space | YES | COVER/EXTENT/SCAN/SOUND + P2 control, 0 failures on six passes (SCAN on the scalar body: stated limit) |
| 5. guard-page and ASan placements W-K4 needs (§3.5) | YES | layouts U, L (guard below 0), A (offset 1..W-1, W 16/32; granule limit stated) |
| 6A. plant: drop one compare; classifier reds | YES | S3007 RED (EXTENT) |
| 6B. plant: candidate above the least; oracle's plant, sabotage row whose detector is the oracle step, listed OWED | YES (OWED) | S3008, declared UNDETECTED; reach 322 of 415 by hand |
| 6C. plant: lever leaves the tie rightmost; reach witness shows a moved scan offset; G2 only | YES | S3009 RED; 24/24 moved per target |
| 6. new sabotage ids from S3007; REACH_ONLY=1 on each row | YES | REACH_ONLY 3 reached |
| if a default byte must move: STOP | not triggered | hand sample identical; identity arms in 541-543 |
| validation: make -j2, strict, the family at cap 2, G2 quick, finder/rows/link, census, anchors, test-codegen, BASE-vs-tip sample (default, and lever OFF identical) | see below | |
| gate jobs 540-549, dry-run, not queued | YES | above |
| CLAUDE.md files | YES | memfn/src, memfn/tests (cli/CLAUDE.md at bdf5c2ff4) |

**Validation (this lane, on the dev box):**

- `nice make -j2`: rc 0. `make strict`: rc 0.
- The presence family alone (one process; runs its passes in sequence): 558,119 passed, 0 failed,
  64 s.
- `--plants`: S3007 RED, S3008 OWED, S3009 RED, 108 s.
- `scripts/m6read_check_sab_anchors.py`: 1227 rows, all anchors resolve.
- The lever fence: PASS.
- BASE(7658295b3)-vs-tip single-compile sample, after the final kit change:
  - 41 patterns x 13 arms, 533 compiles: 493 artifacts, 40 refusals.
  - `diff -r` BASE vs tip: identical. Tip `pcrec` vs tip `pcrec-harness` (the lever arm compiled
    in, OFF): identical.
- `make test-memfn-finder`: 3,420 passed, 0 failed. `make test-memfn-rows`: 239 passed, 0 failed,
  the decider census 96 passed, 0 failed. `make test-memfn-link`: 11 passed, 0 failed.
- `make test-codegen` (PROCS=2): 21 of 21 scripts passed.
- `make test-memfn-g2` (the G2 quick tier, `taskset -c 0,1`, G2V_JOBS/G2A_JOBS 2): rc 0, 70,358,661
  checks passed, 0 failed, 967 s. Section 4p ran inside it: presence family PASS (558,119), lever
  24/24 on each target, `ORACLE OWED`.
- Not run by this lane (box rules): `make test`, the mech matrix, emit_sweep. They are gate jobs
  545, 547-549 and 541-543.

Owed: none of this lane's. The occurrence oracle (`tests/memfn/occurrence_oracle.py`) is lane
k382o's; this lane's seam is in place for it, and S3008's flip to DETECTED rides with it.
