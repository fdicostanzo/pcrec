# 2026-08-25 r36 — [DD-14.FB] frame-buffer CODE HALF critic panel (pre-merge)

Subject: lane/srFBc at 79873cb (rebased onto main df5cbf3 as 454c5b0;
10 commits, 39 files, +2791/−191 vs main). Two read-only critics (D6):
critFB-engine (opus; the three `_in` entries, the run-state split, the
sizing surface + `_Static_assert`s, init/reset, the size_t widening,
the program-region diff, K33's causal control) and critFB-checks
(sonnet; framebuffer.rxt + the `frames-buffer=` directive, RXTROUTE,
ts4/stackdepth, fb_mmap + fb_exact drivers, the codegen block, the four
identity gates' behaviour, S179-S184 + four re-anchors, the suite fixes,
docs/CLAUDE.md coverage, Makefile). Neither ran `make` in the repo; the
engine critic may build a private archive copy in the scratchpad.
Manager verification before the panel: S174 on the rebased tip is
byte-identical to main's baf9e60; anchors "all resolve" on the tip.

## Findings and dispositions

| # | axis | severity | finding | disposition |
|---|------|----------|---------|-------------|
| E1 | engine | doc-mismatch (contract) | emit_dfa.c:704's emitted comment tells every caller to compute `bytes / <P>_RESUME_FRAME_SIZE`; :693-694 stamp both sizes 0 on a DFA artifact — the header's own formula divides by zero (UB/SIGFPE; hard error under -Werror), on exactly the "one call site against both engines" rationale of spec §10.4. The lane's own harness driver guards it privately. | FIX (a): emitted comment + spec §10.4 gain "a stamped 0 means this engine takes no buffers — check before dividing, pass NULL"; the 0s stay (rx_info's honest signal). Sent to srFBc. |
| E2 | engine | nit, PRE-EXISTING | At `rx_L3` three RX_SET restores read `run->trail[run->resume_stack[run->call_top].trail_mark+0..2]` before the `rx_call_frame >= resume_cap` guard; identical at base 08ddcbd. | Filed K36; not this lane's. |
| E3 | engine | nit | `_in`'s 144 B is a -O2 number; -O3 inlines `_run` and gives 224 B (the 131 KB never reaches `_in`). | docs say "at -O2" once. Sent. |
| C1 | checks | BLOCKING | The live identity gate (run_recursion_identity.sh, pinned ac4917d) compares full `-p rx -o -` output after a three-line `stamp_strip`; the unconditional FB surface makes every artifact differ → red on next run; nothing in the diff acknowledges it. | RULED (refined on the lane's objection that deleting CHANGED lines from both sides erases a difference): do NOT re-pin; TWO comparisons — (A) the program region unfiltered beyond the three D37 stamps, the call-bearing capacity-site change a named counted exception; (B) the remainder: ADDED lines stripped by named pattern with a per-class count, CHANGED lines normalized by an explicit old→new rewrite table, each pair counted — never deletion. THEN MEASURED by the lane: line-level stripping over-strips (the anchored entry signatures) and under-covers (blank lines) — RULED option (B): the gate SPLITS — program region vs ac4917d unfiltered (73/0, 28/0, DFA 0, call-bearing 96/4 named exception); whole file re-pinned to the lane's last src commit (8fc1e51) with the D40 reason; both printed. First run 03:49: default (A) 2206/0/elided 4, (B) 2210/0 — two defects in the script: a bash syntax error at line 965, and the elision expectation transplanted from the whole-file gate into the region comparison (vm axis: 0 differ is correct — same VM program); per-axis re-derivation ordered. |
| C2 | checks | should-fix | `rx_match_in`/`rx_match_caps_in` have zero behavioural coverage — only `rx_search_in` is ever driven. | Route harness `m`/`g` lines through them under `frames-buffer=`/RXTROUTE=null; NULL spread to all three; one framebuffer.rxt block per entry with a give-up cell. Sent. |
| C3 | checks | should-fix | run_stackdepth_tests.sh:137 accepts ANY signal ≥128 as "K33 confirmed". | Require SIGSEGV (139); print the signal otherwise. Sent. |
| C4 | checks | should-fix | run_frame_buffer.sh:255-260 has no else — a missing `null342` row fires neither info() nor bad(); per-row RSS printed, not bounded. | `else bad()`; RSS ceiling. Sent. |
| C5 | checks | should-fix | tests/possessify/CLAUDE.md and src/core/CLAUDE.md unchanged though their files changed. | Update. Sent. |
| C6 | checks | nit | run_ir_listing.sh/run_possessify_tests.sh comments call the old grep "vacuous"; the critic tested it — both already reached bad() on empty. | Reword: the fix improved the message. Sent. |
| C7 | checks | nit | test-stackdepth hard-fails without `-lpthread`; RXTROUTE=null is manual-only (like RXTFLAGS). | Preflight + skip loudly; say so in docs/testing.md. Sent. |

## Verdict
Both critics: MERGE-WITH-FIXES. Engine axis: NO MISCOMPILE on ~14
angles (NULL-equivalence byte-for-byte across 401 subjects × 3 entry
pairs + 468 oracle cases on 14 patterns; capacity honoured downward
1→1 … 1024→512, counts not bytes; zero/NULL storage → clean FRAMES
give-up; reuse/interleave clean; ASan+UBSan on exact heap buffers incl.
--trace; init/reset hands-off; -Wconversion 0; program-region diff
0/0/4 lines; `_Static_assert` fires on a tampered stamp; K33 control at
98,432 B with 25% headroom; P-3 refuted outright). Checks axis: the
directive positional and hard-failing on malformed input; asymmetric
and downward capacities verified; the codegen block derives nothing
from the artifact; TS-1 zero-diff; KRESET rule 3 +2/−0; S174 on the tip
byte-identical to main's. Merge waits on C1 (the gate) and the batch.
