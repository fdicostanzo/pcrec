# CRITIC MOVE: l3feat (r65)

## Findings

### MOVE-1 — SUSPECTED (maintenance, low): the K < 0 landmark init in `emit_unanchored` is a dead branch with no witness
- Where: src/gen/emit_dfa.c:14182-14201 (subject 3f02ca8ab), the `pcrec_req_site_in_prefilter` arm's `k.v < 0` branch
  (`size_t landmark_position;` + `emit_req_reentry_use(..., "search_from")`).
- Claim checked: the code says it is NOT reached while R-1's decline holds. It holds on every route I could find, by code and by
  probe. By code: `pcrec_req_site_in_prefilter` -> `req_scan_reentered` -> NEXT must select a row with
  `scan == PF_SCAN_LANDMARK`; the only such row is `handoff-reentry` (emit_dfa.c:10964), whose `pf_handoff_applies` returns
  false on `!req_k_reentry_sound(req_landmark_k)`. `cand_select` (:11330) has no force path that skips `applies`, and with
  `!u->whole` the K that row tests (`req_landmark_k`) is the same K the emitters print (`req_handoff_k`, :9296). By probe:
  none of the ~350 subject-tree artifacts (all routes and part layouts below) contains `size_t landmark_position;`. Every
  `RX_DFA_PREFILTER "handoff"` artifact had K >= 0 (`o?(?<=foo)bar` 1, `(?:oo)?(?<=foo)bar` 2, `\w{1,3}(?<=foo)bar` 2, ...).
- So the branch is unexercised: no test reaches it, and no plant can show that a test reaches it. Its text (a gate re-asked
  at the entry of the prefilter, with a miss answering `return 0` from the prefilter) would ship with no witness on the day
  L2 lifts the decline. D77 (build under measurement) argues for deleting it now and letting L2 write it with its witness.
  A cheaper alternative is an internal-error `pcrec_ctx_fail` there, so the stated "not reached" is checked rather than
  trusted. No answer is at stake today.
- Effort: trivial (delete, or swap in a fail). Blast radius: none today (unreached).

## PROBED-AND-HELD

Instruments: a loop script, `move/drill/run.sh`. It compiles ONCE per (tree, pattern, route), then runs every subject at
EVERY start offset 0..n against libpcre2-8 10.46 (`kit/p2probe` via `oracle.sh`). Answers compared are group 0, M/N, and a
pcrec E -7 under utf8 is not counted. Cases are `move/drill/cases{,2,3,4,5}.tsv`, results are `move/drill/r{1..5}/results.tsv`.
Compiles: 294 + 234 + 50 + 72 + 42 = 692, plus about 10 single emits (cap 800).

- Answers held. 0 wrong answers on SUBJECT and on BASE over 103 distinct pattern x option sets, 242 distinct (pattern, subject)
  pairs (756 subject-tree runs), and every start offset (7,059 subject-tree start answers in all). Routes were default, `--engine=vm` and
  `-fno-prefilter`. Five pattern/subject pairs also ran under `--part-layout=prefilter:inline`, `prefilter:shared`,
  `find:inline,wrap:inline,compound:inline`, `--part-inline-rank=R0 --part-residual=inline` and
  `--engine=vm --part-residual=inline`. The K values reached were -1, -2, -3, -4, -5, -6, -16 and -20.
  - Lookbehind bytes not reached by a match: starts inside them, just past them and before them.
  - W-L16's shape, a subject that ends inside the lookbehind or just at its end:
    `(?<=Content-Length: )\d` / `\d+` on `Content-Length: `, `xContent-Length: `, the run three times over, and
    `Content-Length:  Content-Length: 1`.
  - Overlapping runs: `(?<=aa)a` on aaaaa and aabaabaaa; `(?<=abab)ab`; `(?<=ab)ab`.
  - Stale first occurrences (the re-ask boundary at pos - hit = B, B + 1): `(?<=foo)bar` on foobxfoobar,
    foobafoobxfoobar, fofoobar and foofoofoob.
  - W-L17's shape (`\d*`/`.*` heads absorbed into the start state): `(?<=foobar)\d*x` on foobar12foobar34x;
    `(?<=foo)(?:\d*x)+`; `(?s)(?<=foo).*x`; `(?<=foo)[^x]*x`; `(?<=\u65e5)\d*x` and `(?<=\u00e9)\d*x` under utf8.
  - Empty matches: `(?<=foo)`, `(?<=xyzzy)`, `(?<=a)`, `(?<=foo)b*`, `(?<=foo)(?:bar|)`, `(?<=foo)(?=bar)`, `(?<=foobar)`.
    The empty subject was checked directly against p2probe, because the kit's `${SUBJECT_HEX:-...}` turns an empty hex
    into the subject "x". A kit limitation, noted for the coordinator.
  - search_from = n: every start includes n.
  - utf8 round-up: `(?<=\u0100|\u1100)x` (a masked run whose hit lands on a continuation byte), `(?<=\u00e9\u00e9)`,
    `(?<=\u65e5\u672c)\u8a9e`, and caseless `(?<=ss)`, `(?<=\u00e9)`, `(?<=foo)`. The emitted round-up sits inside the
    moving branch at both the entry and the re-entry (r4 `9.vm.subject/rx.c`:502-507, 560-564).
    `(?i)(?<=k)x` and `(?i)(?<=s)x` under utf8 (Kelvin sign, long s: variable byte width) DECLINE the join, with K none.
  - Lookbehind overlapping consumed bytes: `x(?<=foox)bar`, `o(?<=foo)bar`, `\w(?<=foo)bar`, `bar(?<=foobar)`,
    `ba(?<=fooba)r` and `bar(?<=obar)` move at their K < 0. `o?`, `o{1,2}`, `(?:fo|o)`, `\w{1,3}`, `.?` and `[a-z]{0,2}`
    heads join nothing, with K >= 0.
  - Negative and conditional shapes keep the lookbehind out of the run: `(?!(?<=foo))bar`, `(?<!(?<=x)foo)bar`,
    `(?:(?<=foo)x){0}bar`, `(?:(?<=foo)x)?bar` and `(?(DEFINE)...)(?&l)bar`. `(?(?<=foo)...)` is refused (conditionals
    are not implemented).
  - `\G(?<=foo)bar`, `(?<=foo)ba\Kr`, `(?<=foo)(bar)\1`, `(?<=foo)bar$` and `\z`, `(?m)(?<=^foo)bar`, `(?<=\Afoo)bar`,
    and alternations of lookbehinds (`(?:(?<=foo)|(?<=goo))bar`, masked run at -3; `(?<=fo|foo)bar`, run `[fo]obar` at -2).
- `return 0` in every context the clamp is printed. The entry clamp and the re-entry clamp are printed only inside
  `rx_search_run`, the VM search loop: once in its body and once at the attempt loop's retry. Here `0` is NOMATCH to every
  caller: `rx_search`, `rx_search_in`, and `rx__step` -> `rx_next`/`rx_next_n`, which ends the iterator with rc 0. No
  compound or part layout moves the text into a prefilter or part function (5 layouts checked, read in
  `r3/b/*/rx.c`). The kit's floor is printed as `(pos >= B ? pos - B : 0)` at both sites, and it equals the -K of every
  artifact sampled.
- Sub-part, R-1's VM claim ("an attempt there is a real fresh start"): HELD. Each attempt runs `rx_match_anchored` with
  `ctx.pos = attempt_position` over the WHOLE subject (`ctx.subject = subject`), so a lookbehind reads the real bytes
  before the attempt, including those before search_from. Run state is reset per attempt (`rx_reset_for_next_attempt`).
  An attempt can report only a match that begins at its own position; `\K` moves only the REPORTED start, and was
  drilled. A match begun EARLIER was therefore its own earlier attempt, which already failed. The forward-scan hazard
  (a DFA start state carrying an in-flight thread whose lookbehind lies further back) has no VM counterpart.
  On the default route the hybrid's prefilter is re-asked only from the attempt position, and its handoff row is
  declined at K < 0 (MOVE-1), so the attempt loop's re-entry never prints there (`pcrec_artifact_has_dfa_scan`). It
  prints on `--engine=vm`, `-fno-prefilter`, and on default artifacts whose `RX_VM_PREFILTER` is "none".
- Arithmetic, read from the text. The entry's floor gives `hit >= max(0, pos - B)`. The re-entry's re-ask keeps
  `pos - L <= B`, and a kept L is still the least hit at or above the new floor (it was least above a lower one). The
  clamp `len - hit < B` comes before any `hit + B`. Nothing wraps. A false (stretch-only) hit near the end implies
  that every true hit is at or after it, so the clamp's NOMATCH stays right.
- Minimum witness size reached: subjects of 0 to 41 bytes; B from 1 to 20; up to 3 run occurrences per subject.

CRITIC COMPLETE
