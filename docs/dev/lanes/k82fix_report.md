# k82fix — K82's knob-free half: (A) the rarer guard leads, (C) PICK's NONE answer prices size (2026-10-04, lane k82fix, opus)

Branch `lane/k82fix` from main `940fa06e` (abi 59). **abi 59 -> 60.** Not
merged. Charter: `docs/dev/known_issues.md` K82 ("PLAN RULED"),
`docs/dev/lanes/k82diag_report.md` §4. Frank DECLINED the diagnosis's
`run-common` 16-bit row as a knob, so it is not built; cause (B) waits for
[FINDINGS.B4]'s cost-model reader.

## 0. Summary

| | what | where |
|---|---|---|
| (A) | the whole-window pre-check's admission is a FIRST-MATCH ROW TABLE (`req_admits[]`, `DFA_SELECT`): `none` / `one-attempt` (G2) / `dominated` (G1) / **`set-leads`** / `emitted`. `set-leads`: where a run pre-check is admitted and the necessary SET's pick is strictly rarer than the run's scan member, the set pick's one-byte `memchr` is emitted BEFORE the run search | `src/gen/emit_dfa.c` (`req_admits[]`, `req_set_leads_applies`, `emit_req_one_byte`), `tuning.md` §2.29/§2.40 |
| (C) | `pcrec_find_pick`'s NONE answer = MASS's uniform mass (cardinality) argmin, ties to the reader's `rightmost`; one loop for both arms | `src/core/findings.c`, `findings.md` §4 |
| deny | `-fno-req-set-lead` (bit 45) for the `set-leads` row (D144 item 4: every optimization carries its own deny). (C) has NO deny of its own: it is a primitive's answer, below any flag (D126 Q4 keeps NONE inside the primitive); `-fno-req-run-fold` (bit 44) removes every masked run, so it already restores the pre-(C) program on every (C) mover | `lib/pcrec.h`, `src/core/axes.def` |
| list | the admission table is listable: `--list-axes` axis `req-admit`, walked live off `pcrec_req_admit_row` (Frank's [LIST-TABLES] direction) | `src/dump/axes_dump.c` |
| stamp | `<PREFIX>_REQ_WHY` keeps its FOUR tokens: `set-leads` reads `"emitted"` (the token answers WHETHER a pre-check is emitted, and pcrec-bench's adapter enumerates the closed set) | `match_api.md` §6.3 |

**Movers (pre-bump byte diff, BASE abi 59 vs NEW): exactly the predicted
set, 0 off the diagonal** (`docs/dev/optloop/s4/k82fix/k82_movers.log`):

| row | bench (auto) | corpus |
|---|---|---|
| (A) set-leads | `wild-secrets-username-password-pair` (userpass), `stack-frame`, `cls-h`, `cls-n-uc`, `cls-s-lc`, `cls-v`, `mod-s` — 7 patterns, 28 artifact-configs | 24 artifact-configs (13 (pattern, flags) pairs) |
| (C) PICK NONE | `alt-shared-char` — 4 artifact-configs | 3 patterns, 6 artifact-configs (`(?:😀\|😁)`, `[😀😁]`, `a-z` under `-i -e utf8`) |

That is k82diag §4.3's row-4 list exactly, plus its PICK-NONE row
(`alt-shared`). **k82diag's "~10 exact-run bench movers" are REFUTED for this
build**: they were row 3's (`run-common`), which is declined; of the ten, only
`stack-frame`, `cls-n-uc` and `cls-s-lc` move, and through row 4 (set-leads),
as §4.3 already listed them. `sfx-*`, `asr-*`, `qnt-*` do not move.

Cause (B)'s movers — `mod-i`, `mod-r`, `cls-fold-pair`, `cls-pair-ctl`,
`ci-strasse` — are byte-identical to abi 59 (left for [FINDINGS.B4]). C3's
customers `union-select` (empty set) and `ci-ascii-ctl` are byte-identical
too. The short per-call term (k82diag §2) is untouched.

## 1. (A) — the rarer guard leads

### 1.1 The table

```c
static const ReqAdmitRow req_admits[] = {
    { { "none",        0,                      req_none_applies        }, REQ_ADMIT_NONE,  ... },
    { { "one-attempt", 0,                      req_one_attempt_applies }, REQ_ADMIT_ONE_ATTEMPT, ... },
    { { "dominated",   0,                      req_dominated_applies   }, REQ_ADMIT_DOMINATED, ... },
    { { "set-leads",   PCREC_NO_REQ_SET_LEAD,  req_set_leads_applies   }, REQ_ADMIT_SET_LEADS, ... },
    { { "emitted",     0,                      cand_always             }, REQ_ADMIT_EMITTED, ... },
};
```

The old if-chain's three declines are rows 1-3, unchanged predicates, same
order (so every artifact the declines decided before is decided the same
way). `set-leads` is a SHAPE of an admitted pre-check, so it follows every
decline: a pre-check that is not emitted has no first byte. k82diag §4.2
numbered it before G1 "so G1 asks about the candidate they select" — that
argument was about row 3 (`run-common`, which changes the candidate); row 4
alone does not, so after G1 is the order that keeps every declined artifact
byte-identical.

### 1.2 "Rarer" is one PICK

`req_set_leads_applies` asks the existing PICK primitive over
`[the run's scan cube (bytes[idx], mask[idx]), the set's pick]` with
`rightmost = 0`, the run first:

- under the byte-rate: the set pick leads iff its rate is strictly below the
  scan cube's summed rate (a tie keeps the run alone);
- under NONE, through (C): one member's uniform mass against the cube's
  member count, so a byte leads a two-member pair and NEVER an exact byte.

No new number and no new kind (the report's "set pick mass < scan member
cube mass", spelled through the primitive instead of a reader-side compare,
so D126 Q4's no-reader-NONE rule holds by construction). The set pick is
`pcrec_find_set_pick` over the `req_set` fact, the reader `req_byte`'s case
(ii) already answers through.

### 1.3 Emission

`pcrec_emit_req_byte_check`: where a run shipped and the verdict is
`set-leads`, `emit_req_one_byte(set pick)` then the run call(s), then K65's
rest. `emit_req_one_byte` is the one-byte text both forms now share (S265's
anchor kept at its column). `emit_req_set_rest` marks the lead tested.
`req_admit_emits` is the one spelling of "a pre-check is emitted" for the
three readers (the run blocks, the byte check, the `<string.h>` decision).

userpass after the fix (cap, VM hybrid):

```c
    if (subject_length <= search_from ||
        !memchr(subject + search_from, 61, subject_length - search_from))
        return 0;
    if (rx_reqrun(subject, subject_length, search_from) >= subject_length) return 0;
```

### 1.4 What `-fno-req-set-lead` does

Removes the row (DFA_SELECT skips a denied row), so the artifact is the
abi-59 program apart from the abi digits: measured identical on every
non-(C) artifact of the census (§3). Masked out of `rx_info.flags`.

## 2. (C) — PICK's NONE answer

```c
static uint32_t cube_mass(const uint32_t *rate, int t, int k)
{   ... if (!rate) return uniform_mass(1 << __builtin_popcount((unsigned)f)); ... }

int pcrec_find_pick(...)
{
    int i, best = rightmost;
    uint32_t lo = cube_mass(rate, cand[best], care ? care[best] : 0xFF);
    for (i = 0; i < n; i++) { ... if (m < lo) { lo = m; best = i; } }
    return best;
}
```

One argmin for both arms; ties to `rightmost` when it is among the minima,
else the earliest. Every caller passes `rightmost = 0`, so the rate arm is
byte-identical; the NONE arm answers `rightmost` on every all-byte list (set
pick, kset, exact runs: unchanged) and an exact position before a pair on a
masked run. `alt-shared` (`日本|日曜|日付`, -e utf8): `REQ_RUN
e697a5e4@3/fffffffd` -> `@2`, `REQ_BYTE 230` -> `165` (0xA5, k82diag twin
T2's scan). It is MASS's own NONE answer applied inside the primitive, so
D126 Q4's ban on reader-side NONE rules holds; its old objection to a
uniform table (`cand[0]`, the run's leftmost) is answered by the tie rule.
It reverses `litscan_s4.md` §2.3.3's "accepted, stated" sentence (annotated
there).

## 3. Mover census — the biconditional

`docs/dev/optloop/s4/k82fix/k82_movers.py` imports `c3_movers.py`'s
populations (every bench export x {auto, vm} x {caps, nocaps}; every corpus
`pattern` row as written x {auto, vm}) and compiles BASE (abi 59, main
`940fa06e`), NEW (this branch BEFORE the abi bump, so no normalization) and
NEW `-fno-req-set-lead`. The PREDICTION is recomputed in Python from NEW's
`--emit-facts` rows and `--list-analysis default`'s ppm, never from the C:

```
== bench: 1348 distinct artifact-configs (1380 rows)
  identical pred=-     1223
  moved     pred=A       28
  moved     pred=C        4
  deny arm: 1255 identical-or-(C), 0 not
== corpus: 7324 distinct artifact-configs (8884 rows)
  identical pred=-     6551
  moved     pred=A       24
  moved     pred=C        6
  deny arm: 6581 identical-or-(C), 0 not
k82_movers: PASS (0 off-diagonal, deny or refusal failures)
```

The first run read 34 off-diagonal cells; every one was the PREDICTOR's bug
(it read `rate:none(utf8)->rightmost` as a rate because the token contains
`rate:`), fixed in the predictor alone and re-run — the compiler did not
change between the two runs.

## 4. abi 59 -> 60 (D76/D94)

Readers found by grep (`abi 59`, `ABI_EXPECT`, `PCREC_RX_ABI_H`,
`PCREC_ARTIFACT_ABI`): `src/gen/emit_dfa.c:52`; `docs/spec/match_api.md`'s
K80 block (two digits) and §6's change log (the new head entry);
`tests/codegen/run_codegen_tests.sh`'s `ABI_EXPECT` and its message. The
other `abi 59` hits are history ("since `abi` 59", "(abi 59)" in comments)
and stay. Identity-gate re-pins: §6.

## 5. Checks and sabotage rows

- `tests/codegen/run_prechecks.sh` §5.11 (new): the lead read off the TEXT
  (the first `!memchr(…, B, …)` above the first `rx_reqrun(` call) on 11
  witnesses, expected bytes derived by hand from `--list-analysis default`:
  userpass shape (lead 61, auto and VM), its deny (no lead), `cat\s+sat` (an
  EXACT run under the rate: lead 99), `(?i:xqz)\d+e` (rate says no: e is
  commoner than the z pair), union-select (empty set), `(?i:elect)\d+=`
  under utf8 (NONE: byte leads a pair), `é@` utf8 (NONE tie: no lead), and
  the (C) rows (`日本|日曜|日付` @2, `x(?i:elect)` @0, `(?i:elect)` @4).
  §5.8/§5.9: the K65/K66 witnesses whose set member now leads read rq_set
  `none`, each with a new `-fno-req-set-lead` row reading the old value.
  Witness note: under `-e utf8` `(?i)s` is NOT a pair (it folds with U+017F
  too), so the utf8 witnesses use `elect`, not `select`.
- `tests/codegen/reqcube_check.py`: the s2b check reads the lead together
  with K65's `rq_set` ('S' must be tested: in the lead for s2b, in rq_set
  for the new s2c witness).
- `tests/litscan/reqcube.rxt` (`gen_reqcube.py`, python3 `re`): new S2c
  blocks, `(x?)([a-z]+)+S\d(?i:s)qz\1` — S2b's shape with 'S' commoner than
  the run's exact scan byte 'z', so no lead tests it and only K65's rest
  does. 287/287 cases pass.

| row | plant | detector | result (single-row mech, this tree) |
|---|---|---|---|
| S457 | `set-leads` never applies | prechecks §5.11, §5.8/§5.9 | DETECTED, reach ok, prechecks 6 fail |
| S458 | a tie leads (PICK `rightmost` = the set pick) | prechecks §5.11 `é@` | DETECTED, reach ok, prechecks 3 fail |
| S459 | K65's rest re-tests the lead | prechecks §5.8/§5.9 | DETECTED, reach ok, prechecks 2 fail |
| S460 | the lead emitted after the run call | prechecks §5.11 | DETECTED, reach ok, prechecks 4 fail |
| S461 | PICK NONE prices every cube as one member (the abi-59 answer) | prechecks §5.11 (C) rows | DETECTED, reach ok, prechecks 3 fail |
| S462 | `set-leads`'s deny bit dropped | prechecks §5.11 deny row | DETECTED, reach ok, prechecks 3 fail |
| S294 (re-anchored) | PICK's tie to the LAST candidate (the leftmost); its old anchor `if (!rate) return rightmost;` is gone | prechecks §3.6/§4.9 | OWED-FILL |
| S452 (re-aimed) | K65's rest marks a pair T proved; S2b's 'S' now leads, so the witness moved to S2c | harness reqcube.rxt S2c, reqcube_check | OWED-FILL |

S462 was first written with the registry suite as a second detector; the
plant ran registry 0 fail (the `--list-axes` deny column walks the same row,
a control sharing its source), so the row names prechecks alone.

## 6. Validation

OWED-FILL (suites, make strict, make test, test-axes).

## 7. Directional Mac timing

OWED-FILL.

## 8. C3's alpha control

`alpha_c3.sh`'s loglines A0/B control `stack-frame` MOVES at abi 60 (a
set-leads mover: `(`... the set pick is rarer than the run `at `'s scan byte
`a`), so it is no longer the same program on both sides of a later pin. It is
replaced by `level-context` (`REQ_RUN "none"` at abi 58, 59 and 60, so no C3
or K82 row can reach it); `kv-quoted` stays the class-B control.
`alpha_k82.sh` is K82's own Linux alpha block (BASE abi 59, NEW this branch,
DENY `-fno-req-set-lead`; cell kinds A / P / C, §0 of the script).

## 9. Not built, and why

- `run-common` (k82diag row 3, the 16-bit floor under the rate): DECLINED by
  Frank as a knob. Cause (B) stays open in K82 for [FINDINGS.B4].
- Lead dominance: where the DFA's own candidate scan is `memchr` on the set
  pick (identity), the lead is a second pass on the same byte with a run
  search between them. No mover of this census is in that shape (G1 runs
  first and the movers are all `emitted`); D77, its trigger is such a mover.
- A `REQ_WHY` token for the lead: the closed four-token set answers whether,
  and the bench adapter enumerates it; the lead is visible in the text.

## 10. Resume notes

OWED-FILL.
