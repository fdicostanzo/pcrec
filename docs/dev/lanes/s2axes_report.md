# s2axes — S2 landing cloud axes red: the vrun utf8 floors

STATE: delivered (branch lane/memfn-s2axes, 087cabce7 + this report).

## Summary

Cloud axes run 43535669918 on lane/s2land 692e5f431 is red in the memfn arm. Every vrun
floor that dropped (vrun-trim, -w32, -w16, -pad and -kb, all at @simd utf8) has ONE
cause, and that cause is RIGHT, meaning intended. [RUN-POS-SET] stage 3 now states a
utf8 caseless `s` or `k` as a WIDE run position. The set for `s` is `[Ss\xbf]`, where
0xBF is the last byte of U+017F ſ; `k` likewise with U+212A. A run through such a
position is no longer one RUN term, so `vrun_applies` declines it. Part D says this
by design: docs/design/memfn/part_d.md §3.1 has the `vrun_applies` row "UNCHANGED:
it declines a multi-term part", and vrun on such parts is the deferred candidate
§6 C4. Under the deny `run-verify-wide`, which clips the run to its findable stretch,
vrun comes back: `(?i)stra` stamps `vrun@w32+w16` with that deny and `none` without
it. That shows the decline is the wide position and nothing else. No regression was
found.

Fix: in tests/axes/memfn_arm.py I added four witness-only utf8 patterns to the five
rows' simd witness lists. Each is a sibling of a lost corpus pattern with no wide
letter. With them every floor holds at its old value. No floor was lowered.

OUT OF BRIEF, also red in this run (shard 7), left for the manager:
precheck-assign-byte is DIFFER 123<131 on byte/c-default and 178<189 on
utf8/c-default, at both layers. Not triaged. Its reach is about 130-190 corpus
patterns, and finding them means a corpus-wide sweep, which the evening hold
forbids. I flagged it to main mid-lane.

## Per row

The same six corpus patterns left all five rows at utf8. vrun is all-or-nothing per
site, so a pattern that loses the helper loses every vrun deny at once. I measured
this by compiling the corpus's vrun-reach candidates, about 386 patterns, on both
sides at `-e utf8 -fmemfn-simd=x86-64-v3` and checking for the helper. The
candidates were every caseless or non-ASCII corpus pattern.

| pattern lost (utf8) | wide position at the tip |
|---|---|
| `(?i)select` | `s` |
| `(?i)stra` | `s` (base run `TRA@2/dfdfdf`, tip `[5373bf][5474][5272][4161]@3`) |
| `(?i)stra(ße)` | `s` |
| `(?i)straße` | `s` |
| `(?i)union.*?select.*?from` | `s` |
| `(x?)(?i:abcdefghijkl)\1` | `k` |

How each row's counts move. Cloud values are tip counts; the floors are unchanged.
"With witnesses" is the cloud count plus each witness-only pattern I confirmed to
differ by single compiles.

| row | cell | cloud (tip) | floor | witnesses added (differ) | projected |
|---|---|---|---|---|---|
| vrun-trim / -w32 / -w16 / -kb | utf8/c-default | 12 | 15 | 4 | 16 |
| vrun-trim / -w32 / -w16 / -kb | utf8/c-vm | 13 | 15 | 4 | 17 |
| vrun-pad | utf8/c-default | 10 | 13 | 3 | 13 |
| vrun-pad | utf8/c-vm | 12 | 14 | 3 | 15 |

Cause for every row: RIGHT (intended; part_d.md §3.1 vrun row, §6 C4). Change for
every row: witnesses re-aimed, floors unchanged.

## What moved and why

- Base was the pre-landing tip, the merge-base of lane/s2land and main (0b7a2ece5,
  abi 105). Tip was lane/s2land 692e5f431 (abi 106). Both were built with
  `nice make -j4`. At base, 18 patterns reached vrun on utf8/c-default; at the tip, 12.
- At base, a utf8 caseless `s`/`k` ended the stated run: the run was byte or cube
  positions only (`TRA` for `(?i)stra`). Stage 3 states the run through the wide
  position. The run is wider and more exact, but it is a SET position next to RUN
  positions. vrun's site shape needs `nterm == 1` and one RUN term (vrun.c
  `vrun_applies`), so it declines and the scalar body serves the site. vrun.c is
  unchanged by the landing. The decline is Part D's documented consequence, not a
  lost form.
- Byte encoding is unaffected: in byte mode caseless `s`/`k` are cubes. That matches
  the cloud log, where every byte cell is green.
- The c-vm counts depend on reach outside my candidate set. Cloud shows 13 at the tip
  where my candidates give 11 (12 for pad, where I get 10). So two c-vm patterns
  reach vrun without a caseless or non-ASCII spelling. The projection uses the cloud
  count, so this does not change it.
- Re-aimed witnesses, the lost pattern each one replaces, and why it stays in reach:
  `(?i)tra` for `(?i)stra`, a 3-byte run (pad's 3); `(?i)update` for `(?i)select`, a
  6-byte run (pad's 5-7); `(?i)union.*?update.*?from` for `(?i)union.*?select.*?from`;
  `(x?)(?i:abcdefghij)\1` for `(x?)(?i:abcdefghijkl)\1`, a 10-byte run, which is not
  in pad's set, so it is in VRUN_U8 but not VRUN_U8_PAD.

## Floors and witnesses

tests/axes/memfn_arm.py (commit 087cabce7):
- `VRUN_U8` holds the four patterns above. `VRUN_U8_PAD` is its first three.
- Each `("vrun-*", "simd")` entry's witness list gains `("utf8", st, w)` for both
  streams. vrun-pad uses VRUN_U8_PAD; the other four rows use VRUN_U8.
- A comment above the vrun rows names the cause, the six lost patterns, the cloud run
  and the Part D sections.
- Floors are unchanged. No other row or cell was edited. The default-layer
  ASSERT_ZERO entries are untouched.
- Side effects of the witness-only patterns: memfn_arm compiles every witness in
  every cell. In those cells, the four patterns are not refused under any of the 13
  memfn rows at either layer, encoding or stream. They differ only under the five
  vrun rows at simd, and under window-search on c-default for `(?i)tra` and
  `(?i)update`, which only raises those counts. They do not differ under any vrun
  row at the default layer, so the ASSERT_ZERO cells hold.
  (Scratch: /var/tmp/pcrec-pcrec/scratch/memfn/s2axes/refuse.out.)

## Checks

- memfn_arm.py has no pattern-subset option; `--every K` drops the floors. So I
  validated through the file's OWN `compile_c` and `MEMFN_CLASS`, imported by
  /var/tmp/pcrec-pcrec/scratch/memfn/s2axes/subset_arm.py, over the tip's measured
  utf8 vrun reach plus every vrun simd witness, on the tip build. Every witness differs
  in its cell (witnesses_missed=[] for all 10 utf8 cells). The subset counts are
  c-default 16/16/16/13/16 and c-vm 15/15/15/13/15, for trim/w32/w16/pad/kb.
  Subset pad c-vm reads 13 < 14 only because the subset misses the two c-vm
  corpus patterns the cloud counts. With the cloud's own 12, pad c-vm is 15.
  Log: /var/tmp/pcrec-pcrec/scratch/memfn/s2axes/subset_arm.log.
- The run-verify-wide control: `(?i)stra` at the tip stamps `RX_MEMFN_FORMS` `none`,
  and `vrun@w32+w16` with `--memfn=no-run-verify-wide`.
- The commit's pre-commit staged checks passed (52, 0 failed). No C was touched, so
  I did not run make strict. I ran no suite (evening hold). The full corpus floors
  are the kit manager's cloud axes run (below).

## Owed runs

OWED: none. The kit manager dispatches the cloud axes run, which checks the floors
over the full corpus. The precheck-assign-byte red (shard 7) is outside this lane's
brief and still open with the manager.

## STATE AT HANDOFF

Delivered on lane/memfn-s2axes: commit 087cabce7 (memfn_arm.py witnesses) plus this report.
OWED: none. The kit manager's cloud axes run confirms the corpus floors. No rulings file
was named. Open outside this lane: the precheck-assign-byte floors (shard 7).
