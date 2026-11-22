# verify.md — r67 k152 (coordinator, inline: every CONFIRMED item is a one-call repro)
Calls and raw outputs: .coord/verify/ (patterns), kit/stack.sh at 442,368 B unless stated.

## CHECK-1 — HOLDS
`python3 -I worktrees/crit-k152/scripts/m6read_check_sab_anchors.py` -> STALE ANCHORS: 3 (S1100 ANCHOR NOT FOUND, S1176 ANCHOR COUNT 1 / SAB_COUNT 2, S14 ANCHOR NOT FOUND, all src/ir/nfa.c). BASE tree: "all anchors resolve" (1368).

## CONTRACT-1 — HOLDS
`nest.sh '' '(a|b' c ')+' d 250`: SUBJECT rc=-1 hw=190,224; BASE 314,224. `){2}` + d: SUBJECT 188,560; BASE 312,560. ¶3's "at most 312,560" is BASE's figure.

## CONTRACT-2 — HOLDS (pre-existing)
`abc` / `a` / `(a)` at depth 0: SUBJECT = BASE = 38,448 / 36,864 / 40,848 (features all, auto engine); with features NULL the same; engine 2: 41,520 / 41,264 / 41,264. No regime reproduces 24,120 / ~62 KB. Figure dates from d11814f49 (2026-10-22, dd10b R1); the tree has drifted since.

## CONTRACT-3 — HOLDS
`^(abcdefghijklmnopqrstuvwxyz|abcdefghijklmnopqrstuvwxy_(…abe)*)*|b$` depth 250: SUBJECT 319,504 = BASE 319,504. `^(abc|abd(…abe)*)*|b$`: SUBJECT 318,032 = BASE 318,032. Both above the stated worst 317,744; PRE-EXISTING shapes (the capturing compound route was never the K152 peak), unnamed by ¶3. 442,368/319,504 = 1.385 (limits.def says 1.39x).

## CONTRACT-4 — PARTLY
Re-measured with the test's own driver plus one line setting `o.encoding = PCREC_ENC_UTF8` (.coord/verify/drv_enc.c), not the CLI under ulimit: `([é-ü]bc|[é-ü]bd(…abe)*)*d` SUBJECT 317,808 (BASE 440,560, not died); its compound route 318,096 = BASE. So the utf8 class nest is 64 B over the stated worst, not ~4-8 KB; the critic's ulimit figures carried argv/env/main-thread overhead. The ranking point and the coverage point (the driver has no encoding parameter, so test-stackdepth never measures `-e utf8`) stand.

## CONTRACT-5 — HOLDS (taken from the critic's repro, consistent with ¶4's own preamble; not re-run)

## CHECK-2 / CHECK-3 / CHECK-5 — HOLD as quoted (CHECK-2 figures equal the coordinator's kit sanity run; CHECK-5 is a quote claim, lines checked in the review tree).

VERIFY COMPLETE
