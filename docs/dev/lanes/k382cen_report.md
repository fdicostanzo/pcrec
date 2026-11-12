# k382cen — the K38-2 census's P2s cover rule reads the find's OFFSET (gate 601's 91 rows)

Lane k382cen (opus), branch lane/memfn-k382, 2026-11-12. Brief: the kit manager's, after triage
`$PCREC_TMPDIR/scratch/memfn/triage601/triage.md`.

## Summary

- **The 91 rows were a census defect, not a mover.** The P2s cover rule judged a find by its BYTE
  VALUE: a find byte that occurs anywhere in the run was refused, and the find's OFFSET was ignored.
  Its find reader also knew one form only (`memchr(rx_mfK_s + rx_mfK_c + N, B,`).
- **The rule now tests the sheet's rule.** A cover find is outside the run when (a) its offset lies
  past the run in every placement (offset > `req_run_maxoff` + len - 1, from BASE's facts), or (b)
  none of its bytes is a run byte. Anything else, or an unreadable find, is refused. Byte value alone
  never refuses any more.
- **The reader covers every E-find form the kit prints,** found by grep of `memfn/src/window.c`
  (B-memchr, B-pair, B-walk, B-fn) and `memfn/src/ofsskip.c` (fn-memchr, fn-pair bodies). A window
  site with no readable find (B-hors, a SIMD row) is refused.
- **Four of the five red patterns were census defects. The fifth was an undeclared mover.** It is
  `z(a){3,}?` under `-fprefilter-collapse`: a run pin on an UNCUT run (2 rows). The trace shows the
  cause is §4.2's ruled clip meeting a count-collapsed walk shorter than the run. Per the kit
  manager's ruling it is declared as population P4c: a census rule over that cause, a §5.1 addendum,
  answer identity on the witness, and a plant.
- **`/abcd[xy]/user` is explained (i), not a mover.** Its find reads offset 6, the second `/`; the run
  `/abcd` is at offsets 0..4. The find did not move; only the `@0` was dropped.
- **Non-vacuity:** a new `--control plant-in-run` rewrites every cover find to read the run's first
  position. It turns all 86 P2so artifacts of the three patterns (and `abcdefg(?=x)`'s 79) UNEXPLAINED.
- **The scan_search order changed:** a run-pinned prefilter now refuses before the cover row. Before,
  a cover find outside the run explained an artifact whose run-pinned prefilter reads a run member.
- **Gate results: 593 (sample 300 + named), 594, 595 and 596 (all three identity shards) are GREEN.**
  Over the three shards: P2so 288, P4c 4, P2r 78, 0 unexplained.

## The 91 rows by pattern

The 91 rows covered FIVE patterns, not the triage's three. They are counted from the red shard's
output (`$PCREC_TMPDIR/scratch/memfn/k382cen/census.1.before.tsv`, a copy of
`scratch/memfn/k382/gate/ident/census.1.tsv` saved before the re-run). The failed log is
`worktrees/.boxqueue/failed/20261112T032810.965794512-601-kit-k382-ident1/job.log`.

| pattern | rows | arms | BASE / tip `RX_REQ_RUN` | the find (offset, byte) | run offsets (BASE facts) | reading | fixed census |
|---|---|---|---|---|---|---|---|
| `[a[.b]c]d.]` | 81 | c-default, c-comments, c-simd and 78 `x:*` arms | `635d64@1` / `635d64` | +5, 93 (`]`, the last `]`) | maxoff 1, len 3: 1..3 | outside; the byte `]` is also in the run, so the old byte rule refused it | P2so, 0 unexplained |
| `/abcd[xy]/user` | 3 | `x:axis-fno-req-run-fold`, `x:start:-fno-req-run-fold`, `x:start:-i` (c-default) | `2f61626364@0` / `2f61626364` | +6, 47 (the second `/`) | maxoff 0, len 5: 0..4 | outside; the same byte-value refusal | P2so, 0 unexplained |
| `a{3}(?i:cat)` | 2 | `x:axis-fno-req-run-fold`, `x:start:-fno-req-run-fold` | `616161@2` / `616161` | B-fn `rx_mf1_ofsskip`, fn-pair at +3, bytes 67/99 (`C`/`c`) | maxoff 0, len 3: 0..2 | outside; the old regex could not read the `memchr(subject + ha, ..)` form | P2so, 0 unexplained |
| `a{2}(?:(?<!\w)\|)b` | 3 | `x:memfn-fd-d1`, `x:start:--memfn=no-fd-d1`, `x:start:utf8+--memfn=no-fd-d1` | P2s | a form the old regex could not read | | "no readable memchr find" | P2so, 0 unexplained (98 P2so arms) |
| `z(a){3,}?` | 2 | `x:axis-fprefilter-collapse`, `x:start:-fprefilter-collapse` | NOT P2s: a run-pin move, see below | | | an undeclared mover; traced to §4.2's clip, so declared | P4c, 0 unexplained |

**`z(a){3,}?` under `-fprefilter-collapse`: traced to §4.2's ruled clip, so DECLARED (kit manager's
ruling path 2).** BASE has `RX_DFA_PREFILTER "memchr"`, OFFSETS `"none"`, facts `run_pin=none` and
`req_run=7a616161@0`. The tip has `"run-pinned"`, `"0*,1"`, `run_pin=0:0+2`, a new `rx_ofsskip` (memchr
`z`, memcmp `"za"`) and rx_info `.prefilter = "run-pinned"`.

- **The path.** `pcrec_run_pin` (`src/facts/kset.c`) at the tip clips the stretch per placement:
  `l = min(e0 - s0, nwalk - ro)`. The pin needs `l >= 2` and the pick inside it. BASE's same function
  pinned only where the whole window fit: `ro + l <= o->nwalk`. This is §4.2's RULED clip (r1.1/r1.2
  F-B, main's Q8), "so no pin is lost by length".
- **Why only on `-fprefilter-collapse`.** The count-collapsed prefilter machine's k-set walk is
  `122,97` (nwalk 2): `(a){3,}?` is collapsed, so the walk proves only `za`. The default machine's walk
  is `122,97,97,97`, and there BASE and the tip both pin `0`. With nwalk 2, BASE could not fit the
  4-position run (no pin, so the plain memchr prefilter). The tip clips it to the 2 positions the walk
  proves.
- **The route.** Given the pin, the existing [OPT-LITSCAN] run-pinned prefilter row takes it, as it
  does for any 2-position pin at BASE. The route choice is that row's, unchanged. Only the pin fact
  is new.
- **The miss.** The sheet predicted §4.2's movers "on runs over 8 positions". It missed walks shorter
  than the run, which the count collapse produces.
- **Census rule P4c** (`clip_of`, from BASE's facts, never a pattern list). It holds on an UNCUT run
  with an exact stretch of the whole run that the walk's singletons spell from some placement `ro`
  for `min(e0 - s0, nwalk - ro) >= 2` positions, where `nwalk - ro < e0 - s0` (the stretch reaches
  past the walk). It is an allowance, not a MUST, because the rate pick is not in the listing. rx_info's
  `.prefilter` line is classified P4 (RX_DFA_PREFILTER's mirror). The fixed census gives
  `z(a){3,}?` P4c 2, 0 unexplained.
- **Answers.** `zwit.sh` (scratch) builds BASE's and the tip's `--emit-main` matchers under
  `-fprefilter-collapse` and runs 64 subjects. 0 differ.
- **Non-vacuity.** `--control plant-p4-move` plants a `-> run-pinned` prefilter stamp move on every
  arm. Off CUT and CLIP it must be refused:
  - `z(a){3,}?`: 31 arms UNEXPLAINED; the 3 CLIP arms are admitted, as the rule says.
  - `q(?:zaaa)+`: 110 arms UNEXPLAINED.

**The shard re-runs found one more shape: P2r, the `@` RE-POINTED on an uncut run** (595, `(?i)x/1234`, 3
rows; 596, `(?:cat|bat)(?<=[cb]at|a{1,3}t)s`, 75 rows). In each case the only moved line is the stamp:
- `"582f31323334@0/dfffffffffff"` -> `@1`;
- `"62617473@0/feffffff"` -> `@3`.

The run-pinned prefilter is byte-identical on both sides:
- `memchr(subject + pos + 1, 47, ..)`, OFFSETS `0,1*,2,3,4,5`, BASE `run_pin 1:1+5`;
- `memchr(subject + pos + 3, 115, ..)`, `0,1,2,3*`, `1:1+3`.

The tip's `@` is §4.1's table row 2: the member the prefilter reads (starred offset - `o` + `at`).
BASE's `@0` was pcrec's own index, which pointed at the masked first position. The census gains rule
P2r (`pinned_at`): hex and mask unchanged, `@` on both sides, the tip run-pinned, and the tip's `@` equal
to that member, and the emitted prefilter text identical BASE vs tip (`prefilter_text`: its stamps and
ofsskip/prefilter functions; kit manager's condition 1). `--control plant-p2r` (the tip's `@` one position off) turns every one UNEXPLAINED
(few.py: `(?:cat|bat)..` P2r 74 -> 74 UNEXPLAINED; `(?i)x/1234` P2r 3 -> 3). `--control plant-p2r-code`
(a prefilter code move under the stamp move) turns `(?i)x/1234`'s 3 P2r rows UNEXPLAINED with
`RX_REQ_RUN` among their reasons.

The triage was right about the three patterns it named. Its "@6" for `/abcd[xy]/user` was the find's
offset; BASE's `@` is `@0`.

## Census rule fixes

All in `docs/dev/lanes/k382_evidence/census.py`:

- **`cover_finds(text)`** reads every window site's find. The handles come from `const unsigned char
  *H_s = ` (window.c `wf_nm`). The output is a list of (offset from the candidate start C, bytes or
  None for a set test). It returns None when any site prints no readable find. The forms, by grep of
  the renderers:
  - B-memchr `memchr(H_s + H_c[ +|- d], B,` (window.c `wf_b_search`/`wf_at`);
  - B-pair `if (H_ha < H_c[ +|- d]) H_ha = ..` with `memchr(H_s + H_ha|H_hb, B,` (`ofs_pair_text`);
  - B-walk `while (H_c[ +|- d] < H_n && !(` (bytes None);
  - B-fn `H_c = F(H_s, H_n, H_lo)`, F's body (ofsskip.c): `memchr_body`'s `memchr(subject + pos[ + k], B,`,
    or `pair_body`'s `if (ha < pos[ + k]) ha = ..` with `memchr(subject + ha|hb, B,`.
  - B-hors and the SIMD PREFIX rows print none of these, so such a site is unreadable and refused.
- **The P2s cover branch.** The run starts at an offset s in [smin, smax] from C. smax is BASE's
  `req_run_maxoff`; for P2s, BASE's window is the whole run. smin is not in the facts, so it is not
  used. A find at offset N with bytes Bs is OUTSIDE if:
  - N > smax + len - 1, or
  - Bs is known and no member, masked, is a run byte.

  The artifact is P2so only when every find is outside. Otherwise it is UNEXPLAINED, with the
  offsets and bytes in the reason. Disagreeing placements (§5.1 `[k382fix]` F3) are NOT credited,
  because the census cannot prove them without smin. Such an artifact surfaces as UNEXPLAINED.
- **`scan_search` order:** reqrun block, then run-pinned prefilter, then cover (was: reqrun, cover,
  run-pinned).
- **`--control plant-in-run`** is the negative control (see "Non-vacuity plants").
- The docstring and `k382_evidence/README.md` say the same.

## /abcd[xy]/user ruling evidence

`build/pcrec -p rx -o - --pattern '/abcd[xy]/user' -fno-req-run-fold`, BASE (k382m's e889ba64c build)
against the tip. The whole diff, abi digits aside:

    < #define RX_REQ_RUN "2f61626364@0"
    > #define RX_REQ_RUN "2f61626364"

The cover find is the same on both sides:

    memchr(rx_mf1_s + rx_mf1_c + 6, 47, rx_mf1_n - (rx_mf1_c + 6))

followed by the 8-byte compares of `/abcdx/u` and `cdx/user`. BASE's facts give `req_run 2f61626364@0`
and `req_run_maxoff 0`, so the run `/abcd` occupies pattern offsets 0..4. Offset 6 is the `/` of
`/user`, outside the run.

- At BASE, `@0` was pcrec's own index, and no search read run position 0.
- On the tip, §4.1's table row 2 asks for the cover site's `run_member`. The find reads no run member,
  so the stamp correctly drops `@` (row 3; the F3 addendum's "a find outside the run").

**Ruling: (i), explained by the declared P2s population (P2so) once the rule reads offsets.** It is
not an undeclared mover, so the STOP clause does not apply. Under the fixed census its 4 P2s artifacts
are P2so, 0 unexplained.

## Non-vacuity plants

`--control plant-in-run` rewrites every cover find form on the tip text before the judgment. Each
find reads offset smax (the run's first position) and, for byte finds, the run's first byte (masked
on caseless arms). The run was a scratch driver, `$PCREC_TMPDIR/scratch/memfn/k382cen/few.py`, which
calls `census.one()` on named patterns with every arm (283 per pattern):

| pattern | fixed census, no control | `CONTROL=plant-in-run` |
|---|---|---|
| `[a[.b]c]d.]` | P2so 80, unexplained 0 | unexplained 80 ("may read the run at offsets 0..3 (offset, bytes: [(1, [99])])"; 1 caseless arm [67], 2 B-walk arms 'set') |
| `/abcd[xy]/user` | P2so 4, unexplained 0 | unexplained 4 ((0, [47])) |
| `a{3}(?i:cat)` | P2so 2, unexplained 0 | unexplained 2 ((0, [97]), the B-fn pair body) |
| `abcdefg(?=x)` (the sheet's 2s example) | not run | unexplained 79 |

Every P2so artifact turns UNEXPLAINED under the plant, so the offset reading, the B-fn reader and the
B-walk reader are each shown live.

## Checks

| check | file / command | result |
|---|---|---|
| census parses | `python3 -I docs/dev/lanes/k382_evidence/census.py --help` | ok |
| three red patterns, every arm | `few.py` over the three patterns (census.one, 283 arms each) | 0 unexplained (P2so 80 / 4 / 2) |
| the triage's two missed patterns | `few.py 'a{2}(?:(?<!\w)\|)b' 'z(a){3,}?'` | P2so 98, 0 unexplained / P4c 2, 0 unexplained (after P4c) |
| P4c plant | `CONTROL=plant-p4-move few.py 'z(a){3,}?' 'q(?:zaaa)+'` | 31 / 110 UNEXPLAINED |
| P2r and its plant | `few.py` / `CONTROL=plant-p2r few.py` on `(?i)x/1234`, `(?:cat\|bat)(?<=[cb]at\|a{1,3}t)s` | P2r 3 / 74, 0 unexplained; plant 3 / 74 UNEXPLAINED |
| z witness answers | `zwit.sh` (scratch), BASE vs tip `--emit-main` under `-fprefilter-collapse` | 64 subjects, 0 differ |
| plant | `CONTROL=plant-in-run few.py` (four patterns) | every P2so turned UNEXPLAINED (table above) |
| census sample 300 + the three patterns | queue job 593-kit-k382cen-census | see Gate jobs |
| 601's shard re-run | queue job 594-kit-k382cen-ident1 (a copy of 601) | see Gate jobs |
| pre-commit staged checks | commit hook | passed |

## Gate jobs

All four are GREEN. Logs are under `worktrees/.boxqueue/done/`; census outputs are
`$PCREC_TMPDIR/scratch/memfn/k382/gate/ident/census.{1,2,3}.tsv` and
`$PCREC_TMPDIR/scratch/memfn/k382cen/census.tsv`.

| job | what | census commit | verdict | P2so | P4c | P2r |
|---|---|---|---|---|---|---|
| 593-kit-k382cen-census | sample 300 + the three named patterns (303 tasks) | 1723277c5 | GREEN, 0 unexplained (181 s) | 87 | 0 | n/a |
| 594-kit-k382cen-ident1 | 601's shard 1, all arms + dumps | 1723277c5 (before P2r; P2r only narrows) | GREEN, 0 unexplained, floor held, dumps 2/2 (697 s) | 187 | 2 | 0 |
| 595-kit-k382cen-ident2 | shard 2 | 6369424df (started 05:15:41, after its 05:13:27 commit) | GREEN, 0 unexplained, floor held (1032 s) | 81 | 2 | 3 |
| 596-kit-k382cen-ident3 | shard 3 | 6369424df (started 05:32:54) | GREEN, 0 unexplained, floor held (751 s) | 20 | 0 | 75 |
| three shards | | | GREEN | 288 | 4 | 78 |

The earlier failures were mine to triage:
- **593 (first run) and 594 (first run): POPULATION-OVER.** census.py echoed `== census COMPLETE`/`== floor`
  and the jobs grep them from the tsv again, so each line printed twice. The fix (1723277c5) leaves the
  verdict lines in `--out` only.
- **595 (cancelled by me):** it started on the pre-fix census.
- **595 and 596 RED:** P2r, as above. Both were re-run green.

These counts are in the sheet's §5.1 addendum `[k382cen]`.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| 1. the P2s rule tests the find's OFFSET against the run's range; not byte value alone; the reader widened to every emitter find form, found by grep | yes: `cover_finds`, the P2s cover branch, the forms listed above from window.c/ofsskip.c |
| 2. `/abcd[xy]/user` BASE vs tip C, ruled (i) or (ii) | yes: (i), evidence above |
| 3. non-vacuity plant refused | yes: `--control plant-in-run`, 86/86 on the three patterns |
| 4. ONE census job (three patterns + sample 300), then 601's shard re-run as a queued copy, GREEN | yes: 593 GREEN, 594 GREEN; 595/596 also GREEN (the three-shard count) |
| population count changes in the sheet's §5.1 addendum, same change | yes, addendum `[k382cen]` with the three-shard counts |
| P2r ruling: prefilter text identical, shifted-@ plant, addendum line | yes: `prefilter_text`, `plant-p2r` + `plant-p2r-code`, "2r, short runs: @ re-pointed to the read member" |
| ruling on `z(a){3,}?`: trace the cause; declared -> rule, addendum count over 3 shards, answers, plant | yes: §4.2 clip, P4c, all three shards queued (595/596 beside 594), 64 subjects 0 differ, plant-p4-move |
| report sections per k382cen_deliver.txt, an `OWED:` line, lanecheck DONE rc=0 | yes |

OWED: none
