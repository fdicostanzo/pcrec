# s2pre2 — precheck-assign-byte floors after [RUN-POS-SET] stage 3

STATE: delivered (branch lane/memfn-s2axes, 6aedc0c4a + this report).

## Summary

Sweep job 599 (green) found 9 lost patterns at byte/c-default and 11 at utf8/c-default.
The lists are the same at both layers, and nothing was gained. The counts are base 132 to
tip 123 (byte) and 189 to 178 (utf8), which match the cloud's 123/178.

Every loss is RIGHT. At base, each pattern's pre-check had a one-byte landmark, searched
by `memchr`, and the deny moved that site. At the tip, [RUN-POS-SET] stage 3 builds a
set run around that landmark (`RX_REQ_RUN` is no longer `none`, and the site is
`rx_reqrun`). So the one-byte ASSIGN site is gone, and the deny is byte-identical on
these patterns. That is the cause stage 1 named. Some of the set positions come from
alternation branches rather than a class (`true|false`, `ERROR|WARN`), but they are
the same stage 3 mechanism. I found no pattern explained by R-41 or another Part D
change, and NO REGRESSION.

Fix: I added eleven witness-only siblings to both precheck-assign-byte entries in
tests/axes/memfn_arm.py. Each one puts a `.` between the landmark and its set
neighbours. With them the counts project to byte 133 against a floor of 131, and utf8
189 against 189. No floor was lowered.

## Every lost pattern

Each row below was checked by single compiles of base (`pcrec_base`, 0b7a2ece5) and tip
(`pcrec_tip`, lane/s2land 692e5f431), with and without the deny, using
s2pre2/probe.py (`-p rx --features all`). "base" is the landmark byte, with
`RX_REQ_RUN none` in every row. "tip" is the tip's `RX_REQ_RUN`.

| lost pattern | cells | base landmark | tip RX_REQ_RUN | verdict |
|---|---|---|---|---|
| `(?:[0-9]{1,3}\.){3}[0-9]{1,3}` | byte+utf8 | 46 `.` | `[30-39]2e[30-39]@1` | RIGHT: set run |
| `(?:[0-9a-f]{1,4}:){4,7}[0-9a-f]{1,4}` | byte+utf8 | 58 `:` | `[30-3961-66]3a[30-3961-66]@1` | RIGHT: set run |
| `(?:\d{1,3}\.){3}\d{1,3}` | byte+utf8 | 46 | `[30-39]2e[30-39]@1` | RIGHT: set run |
| `(?:^\|[\s,;])(?:true\|false)(?:$\|[\s,;])` | byte+utf8 | 101 `e` | `[6174][6c72][7375]65@3` | RIGHT: alternation positions join the run |
| `(?:ab\|cd\|aqr\|cst){8}z` | byte+utf8 | 122 `z` | `[61637173][62647274][6163][62647173]@2` | RIGHT: set run from the repeat body takes the site |
| `(?m)^ERROR\|WARN` | byte+utf8 | 82 `R` | `[4557][4152]52[4e4f]@2` | RIGHT: alternation positions join the run |
| `(\d{2,4})-(\d{2,4})` | byte+utf8 | 45 `-` | `[30-39][30-39]2d[30-39][30-39]@2` | RIGHT: set run |
| `[a-c]{2,4}x[0-9]{2,4}y[A-C]{2,4}z[j-l]{2,4}w[x-z]{2,4}` | byte+utf8 | 122 `z` | `[41-43][41-43]7a[6a-6c][6a-6c]@2` | RIGHT: set run |
| `\b\d{1,3}\.\d` | byte+utf8 | 46 | `[30-39]2e[30-39]@1` | RIGHT: set run |
| `(?:ab\|ba\|aa\|bb){24}c` | utf8 only | 99 `c` | `[6162]` x many | RIGHT: set run (at byte, base was already S) |
| `x(?:1[éà]\|q2\|r3)y` | utf8 only | 121 `y` | `78[317172][3233c3]@0` | RIGHT: set run (at byte, base was already S, landmark `x`) |

On base, every row's deny diff is exactly the landmark `memchr` turning into the generic
row's loop. On the tip, every row is SAME under the deny. Corpus source:
/var/tmp/pcrec-pcrec/scratch/memfn/s2pre/sweep/changed.txt.

## Floors and witnesses

tests/axes/memfn_arm.py (6aedc0c4a): the new lists `PAB_BOTH` (10 patterns, differ at
byte and utf8) and `PAB_U8` (1 pattern, utf8 only) are folded into `PAB_WIT`. Both
precheck-assign-byte entries (default and simd) use `PAB_WIT`, which also keeps the old
witness `((?:a(?!b)|ab)(?:cd){0,3}b)`. A comment names the cause, the sweep, and the
counts.

Sibling per lost pattern, in table order:
`(?:[0-9]{1,3}.\.){3}[0-9]{1,3}`, `(?:[0-9a-f]{1,4}.:){4,7}[0-9a-f]{1,4}`,
`(?:\d{1,3}.\.){3}\d{1,3}`, `(?:^|[\s,;])(?:tr.e|fal.e)(?:$|[\s,;])`,
`(?:a.|c.|a.r|c.t){8}.z`, `(?m)^ER.ROR|WA.RN`, `(\d{2,4}).-.(\d{2,4})`,
`[a-c]{2,4}.x.[0-9]{2,4}.y.[A-C]{2,4}.z.[j-l]{2,4}.w.[x-z]{2,4}`, `\b\d{1,3}.\..\d`,
`(?:ab|ba|aa|bb){24}.c`, and (utf8 only) `x.(?:1[éà]|q2|r3).y`.
None of them is in the tip corpus (checked against status.tsv's hex column).

Rejected candidates, which do not differ at the tip:
- `(?:ab|cd|aqr|cst){8}.z` and `[a-c]{2,4}x[0-9]{2,4}y[A-C]{2,4}.z.[j-l]{2,4}w[x-z]{2,4}`:
  another set run still forms elsewhere.
- `(?m)^E.R.O.R|W.A.N` and `(?:a.|c.){8}z` at byte: SAME on both sides.
Their s2pre2/cand1.txt results are kept.

Projected counts are the sweep's tip count plus the new witnesses that differ:

| cell (both layers) | tip | new witnesses differ | projected | floor |
|---|---|---|---|---|
| byte/c-default | 123 | 10 | 133 | 131 |
| utf8/c-default | 178 | 11 | 189 | 189 |
| byte/c-vm, utf8/c-vm | 0 | 0 | 0 | 0 |

No floor was changed. The utf8 projection meets its floor exactly.

## Checks

- The new witnesses were run through memfn_arm.py's own `compile_c` and `MEMFN_CLASS`
  by /var/tmp/pcrec-pcrec/scratch/memfn/s2pre2/wit_arm.py, on the worktree build
  (byte-identical to `pcrec_tip`). It covers every row, both layers (simd =
  `-fmemfn-simd=x86-64-v3`), both encodings and both streams. Log:
  s2pre2/wit_arm.log, `wit arm: OK`.
- precheck-assign-byte: every new witness differs in its cell. The default and simd
  layers give the same counts, 10 at byte and 11 at utf8.
- Other rows: no new witness is refused under any row, and none differs under any
  ASSERT_ZERO row. Each other row's cells change only by the increases below:
  - fd-d1 +1 at byte/c-default and +1 at utf8/c-default.
  - fd-pres-g1 +1 at byte/c-default.
  - fd-pres-pick +1 at byte/c-default and +2 at utf8/c-default.
  These are the same at both layers. All three are DIFFER rows, so an increase only
  adds margin above the floor. No other row's entry was edited.
- This row only, through the real file: `memfn_arm.py --every 50 --subset` with the two
  precheck-assign-byte cells, which is all the row-only form supports.
  - Result: `memfn arm: OK`, checks passed 82, failed 0.
  - That covers the population, the cell flags, every witness in its cell, refused=0,
    the null arm, and the controls.
  - The floors are not applied at `--every 50`.
  - Log: s2pre2/arm_every50.log.
- I did not run the full-corpus row-only run, which is about 88k compiles. The brief
  limits me to single compiles and no suites, and the kit manager's cloud axes run
  applies the floors.
- The pre-commit staged checks passed (52, 0 failed). No C was changed.

## Owed runs

OWED: none. The kit manager's cloud axes run applies the full-corpus floors. Expect
byte/c-default 133 and utf8/c-default 189 at both layers.

## STATE AT HANDOFF

Delivered on lane/memfn-s2axes: 6aedc0c4a (memfn_arm.py witnesses) plus this report.
Every lost pattern is RIGHT, and no regression was found. No rulings file was named.
OWED: none (the kit manager runs the cloud axes).
