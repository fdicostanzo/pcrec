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
| (pending) | | | | |

## Verdict
(pending both reports)
