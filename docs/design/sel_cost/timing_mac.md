# [SEL-COST] step 1 — Mac scratch timings (lane selcostdes, 2026-10-03)

**SCRATCH TIER, DIRECTIONAL ONLY.** Apple M1, gcc-16 `-O2`, compiler at
c231ffc1 (abi 54), box shared with other lanes (load1 1.8-5.1). Every number
is a median of 3 launches (5 for bucket A), each launch itself a median of 7
rounds. No base/deny noise column: these compare two DIFFERENT programs
(auto vs `--engine=vm`), so only ratios far past the ±5% Mac floor measured
in `docs/dev/reseed/timing_mac.md` are read. Answers were checked equal on
every row (span or find-all hash). Patterns compiled with `--features all`,
byte encoding unless noted.

Drivers: `percall.c` (whole-subject: `rx_search(s, n, 0)` in a calibrated
loop, ns/call) and `studies/hyb_reseed_cal/drv.c` (find-all, ns/byte).

## T1 — [SEL-SIZE]'s witness family, whole-subject, ns/call (auto / forced VM)

Subjects: `short` 40 random lowercase letters; `l4k` 4096 letters;
`prose64k` 2-9-letter words separated by spaces.

| pattern | auto artifact | short | l4k | prose64k |
|---|---|---|---|---|
| `(?:[a-z]{0,4096})\z` | DFA, 477 KB, WARNED | 134.6 / 20.2 (VM ×6.7) | 15280 / 1914 (VM ×8.0) | 8953 / 14142 (DFA ×1.58) |
| `(?:[a-z]{0,2048})\z` | DFA, 310 KB, WARNED | 134.5 / 20.2 (VM ×6.7) | 7638 / 960 (VM ×8.0) | 4447 / 7032 (DFA ×1.58) |
| `(?:[a-z]{0,256})\z` | DFA, 67 KB, not warned | 134.6 / 20.2 (VM ×6.7) | 944 / 126 (VM ×7.5) | 551 / 795 (DFA ×1.44) |
| `[a-z]{0,4096}` | DFA, 20 KB, scan edge `range` | 18.0 / 19.9 | 1756 / 1915 | 3.1 / 3.4 |
| altwide `w-256` | DFA, 985 KB, WARNED | 76.8 / 151.3 (DFA ×2.0) | 2530 / 4648 (DFA ×1.8) | 3030 / 5433 (DFA ×1.8) |

The `\z` rows carry `RX_DFA_SCAN_EDGE "none"`, `RX_DFA_START "reverse-pass"`
(and `RX_DFA_MATCH "search-filter"` at 4096); the plain row carries
`"range"`/`"pinned"`.

## T2 — bucket B (class run), find-all over 1 MiB, ns/byte (auto / forced VM)

Subjects: `prose1m` 1-10-char words over `[a-zA-F]` with spaces and commas
(159,112 matches); `runs1m` 500-letter runs separated by one space;
`sparse1m` random bytes from ` ,.;:-0123456789` (no letters).

| pattern | auto stamps (engine, prefilter, scan edge) | prose1m | runs1m | sparse1m |
|---|---|---|---|---|
| `\w+` | dfa, byte-class, bitmap | 3.29 / 2.55 (VM ×1.29) | 0.73 / 0.48 (VM ×1.53) | 5.35 / 4.90 (VM ×1.09; digits match) |
| `[[:alpha:]]+` | dfa, byte-class, bitmap | 3.32 / 3.02 (VM ×1.10) | — | — |
| `\p{L}+` (`-e utf8`) | dfa, byte-class, none | 7.19 / 4.89 (VM ×1.47) | 5.17 / 1.68 (VM ×3.08) | 0.32 / 5.42 (DFA ×17) |
| `(?a)\w+` | dfa, byte-class, bitmap | 3.59 / 3.07 (VM ×1.17) | — | — |

## T3 — bucket A (one-attempt DFA), ns/call (auto / forced VM)

Subjects: `item done here and more text after it`; the same prefix on a
1 MiB subject; `zzzz done here` (no match).

| pattern | auto stamps | short | 1 MiB | no-match |
|---|---|---|---|---|
| `^item` | dfa, attempt | 3.7 / 1.2 | 3.7 / 1.2 | 2.3 / 1.6 |
| `\Aitem` | dfa, attempt | 3.7 / 1.2 | 3.7 / 1.2 | 2.3 / 1.6 |
| `done$` | dfa, unanchored | 2.9 / 3.1 | 2.9 / 3.1 | 2.9 / 3.1 |

Controls (attempt-shape DFAs from capability@0.1, one near-miss subject
each): `ipv4-near-miss` on `192.168.001.25x` 7.9 / 40.2 (DFA ×5.1);
`wild-validator-email-owasp` on `user.name+tag@example-domain.co`
15.4 / 26.5 (DFA ×1.7).
