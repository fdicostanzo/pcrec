# NOTES — history, lessons and rationale for this directory

Not auto-injected. CLAUDE.md is the orientation guide; text moved here verbatim from it (2026-10-22, size limit) lives below.

## Stage 3 entries: dfahat_f1, compile_fuzz, dfahat_paths

- `dfahat_f1.rxt` + `gen_dfahat_f1.py` — the ss3 D6 panel's BLOCKER
  sound-F1 witnesses (`(?<=\w) *a` and eleven more): a byte of `S` leaves
  every seed state where it is, so the old `T = S & E*` dropped a start byte
  and its `T == S` assertion REFUSED them at default flags. With `T = S` the
  admission declines and the artifact is the deny arm's. GENERATED (libpcre2,
  every startpos; byte-tier blocks python-verified too). Every block must
  compile (the harness), equal the deny arm byte for byte ([dfa-deny]) and
  answer as libpcre2 does; the pre-fix compiler fails all 322 cases.
- `compile_fuzz.py` — the COMPILE-ONLY arm (the panel's lesson: an answer
  differential cannot see a pattern that no longer compiles): 9,000
  generated seeded patterns (a fixed seed; 30% from an F1-shaped template),
  each `-fno-start-set` compile must be matched by a default compile, and an
  internal error on either arm fails; floors on the deny-compiling
  population and on the DFA-hat reach. On the pre-fix compiler it reads 70
  hits (4 in 9,000 with `TEMPLATE=0`, the critic's grammar); ~25 s.
- `dfahat_paths.rxt` — hand-written, python-verified: the SET form's
  clamp-path witness `\B(?<!a)[de]` on "xd" (S483) and S488's nullable-S
  seeded skip `\b\B|\b(?:ab|cd)`.
