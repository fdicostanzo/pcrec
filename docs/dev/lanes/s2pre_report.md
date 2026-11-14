# s2pre — S2 landing cloud axes red: precheck-assign-byte floors

STATE: stopped (staged delivery). The cause is named and RIGHT for every loss found by
targeted compiles. The full list of lost patterns is OWED by the queued sweep
`kit-s2pre-sweep`. No floor or witness was changed: that is the follow-up's step 4.

## Summary

The red: cloud axes run 43535669918 on lane/s2land 692e5f431, shard 7, memfn arm. Row
precheck-assign-byte, cell c-default, both layers, has DIFFER counts 123 < 131 (byte)
and 178 < 189 (utf8).

The row (memfn/src/precheck.c `precheck_assign_byte_applies`) applies only to an
ASSIGN pre-check whose kept landmark is ONE byte. It renders that pre-check as one
`memchr`. Under the deny, the generic row renders the same site.

Cause found: [RUN-POS-SET] stage 3 lets a class next to the landmark byte JOIN the
necessary run. The landmark is then a multi-position set run, searched by
`rx_reqrun`, so the one-byte ASSIGN site no longer exists and the deny has nothing to
move. This is the intended consequence of set runs (s2land's movers table: "longer
runs"). It is RIGHT, not a regression: the pre-check still applies, with a stronger
landmark. I found no regression.

Named corpus loss: `(?:\d{1,3}\.){3}\d{1,3}` (tests/litscan/handoff.rxt, the dotted4
shape s2land already re-aimed elsewhere). Targeted compiles cannot name the remaining
~7 byte and ~10 utf8 losses (net counts), so the sweep is queued as 599-kit-s2pre-sweep.
It starts after 01:00 behind the kit's hold gate.

## What moved and why

Builds:
- base: the merge-base 0b7a2ece5 (abi 105), s2axes's scratch build.
- tip: lane/s2land 692e5f431 plus s2axes's test-only commits (abi 106). The worktree
  build was up to date (`make` reported nothing to do), and no src/cli/lib/memfn/src
  file differs from 692e5f431.

Both are frozen as /var/tmp/pcrec-pcrec/scratch/memfn/s2pre/bin/pcrec_{base,tip}.
Probe tool: s2pre/differ.py compiles each pattern with and without the deny, the way
memfn_arm does (`-p rx --features all`, `-e utf8`, `-o -`).

| pattern | corpus? | base | tip | why |
|---|---|---|---|---|
| `(?:\d{1,3}\.){3}\d{1,3}` | yes (handoff.rxt) | D | S | `[0-9]` joins `\.` in the run; landmark is the set run |
| `[a-z]{2,5}@[a-z]+` | probe only | D | S | base `RX_REQ_BYTE "64"`, `RX_REQ_RUN "none"`, HANDOFF 5, `memchr(...,64,...)`; tip `RX_REQ_RUN "[61-7a][61-7a]40[61-7a]@2"`, HANDOFF 3, `rx_reqrun` |
| `a.{1,5}z`, `a.{1,5}\dz`, `a.{1,5}[xy]z`, `[ab].{1,5}z`, `a\d{1,5}z`, `(?:.{1,3}\.){3}.{1,3}` | mixed | D | D | landmark still one byte (a `.` neighbour is no set position) |
| `abc+d`, `\w+z`, `a+z`, `a.*z`, 6 others | mixed | S | S | never this row's site |

The probe also covered R-41 (a declared unbounded head_max, so the kit declines the
landmark). The s2land report places R-41's movers on VM artifacts (`(a+)+zq` shape).
This row's c-vm floors are 0, so R-41 cannot explain a c-default loss. The sweep
confirms whether any c-default pattern moved for that reason.

## Floors and witnesses

Unchanged in this lane: tests/axes/memfn_arm.py is not edited. That is step 4, which
waits for the sweep to confirm every loss is RIGHT.

Ready for the follow-up: these siblings DIFFER at the tip (single compiles, c-default):
- `[a-z]{2,5}.@[a-z]+`, byte and utf8.
- `(?:.{1,3}\.){3}.{1,3}`, byte and utf8.
- `(?:\d{1,3}.\.){3}\d{1,3}`, byte.

`[a-z]+.@[a-z]+` does NOT differ, so a sibling must keep the bounded head. Following
s2axes's method, the follow-up adds one sibling per lost corpus pattern as a
witness-only pattern to both precheck-assign-byte entries. It lowers a floor only where
a loss has no sibling, and names why.

## Checks

- Each probe line above is a pair of single compiles, with and without the deny, on the
  frozen binaries (about 110 compiles in total, inside the hold's light-work bound).
- The sweep script was checked on 3 patterns (s2pre/minitest/changed.txt): it reports
  both named losses as LOST in all four cells and `a.{1,5}z` as differing on both
  sides. Its dry run and `--ready` were run: the hold gate returns 75 before 01:00.
- No suite was run, and no C or check was changed.

## Owed runs

OWED: kit-s2pre-sweep (queued as 599-kit-s2pre-sweep; script
/var/tmp/pcrec-pcrec/scratch/memfn/s2pre/jobs/sweep.sh).

Completion line: `s2pre-sweep: patterns 5492`. Results:
- /var/tmp/pcrec-pcrec/scratch/memfn/s2pre/sweep/changed.txt: per-cell differ counts
  for base and tip, and every LOST/GAINED pattern for byte/utf8 × default/simd at
  c-default.
- status.tsv: the full per-pattern matrix, with membership in the base and tip
  corpora.

The follow-up must:
- Check that the tip counts reproduce the cloud's 123/178.
- Classify each LOST pattern. The expected class is "set run absorbed the byte
  landmark". Any other cause is a possible regression: report it and stop for a ruling.
- Then apply step 4.

## STATE AT HANDOFF

Branch lane/memfn-s2axes: this report only (no code or check change). No rulings file
was named.

OWED: 599-kit-s2pre-sweep, as above. Mechanism: stage 3 set runs absorb the one-byte
landmark (RIGHT). One corpus loss is named; the rest come from the sweep.
