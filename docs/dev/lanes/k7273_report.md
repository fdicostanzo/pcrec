# k7273 — K72 fixed, K73 measured and HELD for a ruling

Lane `k7273` (sonnet, 2026-09-29), branch `lane/k7273` from `31979ed3`.
Docs and `src/` under `worktrees/k7273` only; scratch in `build/scratch/`
(gitignored); two light probe compiles on ubuntubudu (`/tmp`, removed).

## K72 — FIXED (`\h`/`\v` under `-e utf8`)

- **Lists** (libpcre2 10.46, PCRE2_UTF, no UCP): `\h` = U+0009 U+0020 U+00A0
  U+1680 U+180E U+2000-U+200A U+202F U+205F U+3000; `\v` = U+000A-U+000D
  U+0085 U+2028 U+2029. The byte sets lacked every wide member, not only
  U+3000.
- **Mechanism used, and why it is the general one**: `DEF_ENCODING_UTF8` was a
  declared `DefTag` with no producer (`definitions.c` answered `false`). It
  now answers "the encoding's universe is Unicode's" (`max_cp >= 0x10FFFF`,
  asked of the encoding, DD-12 (7)). `h_def`/`H_def`/`v_def`/`V_def` gain a
  leading `DEFK_SET` entry under it (`registry.c`), built by the existing set
  producer from `pcrec_ucp_set_hspace`/`_vspace` (`mod_ucp.c`; `t_blank`
  shared with UCP's `[:blank:]`). Same route `\d \s \w` take under UCP; no
  parallel mechanism. In-class and negated forms ride the same port.
- **Not an abi event**: no emitted scaffolding moved (the parsed class did).
  `make test-codegen` and the identity gates were NOT run (see OWED).
- **Witness**: `tests/utf8/hv_space.rxt`, 17 blocks / 420 cells (every member,
  24 edge non-members, nine bracketed/negated spellings, run-lengths, `byte`
  control). Oracle: all 408 utf8 cells re-read on **libpcre2 10.46**
  (ubuntubudu) and identical to the file and to local 10.48
  (`docs/dev/lanes/k7273_evidence/hv_space_10.46.txt`, `pr1.c`). Pre-fix
  binary 361/420 (59 fail), fixed 420/420.
- **Spec hunk**: `docs/spec/cli.md`, bullet on `\h \H \v \V` in the `--ucp`
  section. `known_issues.md` K72 marked FIXED with the original diagnosis kept.
- **Re-pins moved by the new corpus file** (found by running the suite that
  counts): `tests/rxtsource/run_rxtsource_tests.sh` CENSUS 252/4181/30967 ->
  253/4198/31387, RUNSH 228/4181/30967 -> 229/4198/31387, `C3_SKIP`
  16975 -> 17395, `C3_SKIP_PCRE2ONLY` 2966 -> 3386 (reconciliation
  13903+17395+89 = 31387). `tests/utf8/CLAUDE.md` gained the file's entry.

## K73 — STOPPED: a contract question, with the measured rule

**Oracle rule (10.46, transcript `k73_startskip_10.46.txt`; 10.48 identical).**
Under PCRE2_MATCH_INVALID_UTF a start offset — the implicit 0 included, and
also an explicit one, anchored or not — that lands on a CONTINUATION byte
(0x80-0xBF) is advanced to the next non-continuation byte before any attempt,
whatever the pattern: `\x80` -> (1,1), `\x80\x80` -> (2,2), `\x80\xc3\xa9` ->
(1,1) for `''`, `\B`, `x*`, `(?=)`; `^` on `\x80` finds nothing; `\xc3\xa9` at
startoffset 1 -> (2,2). Every other ill-formed lead (0xFF, truncated 0xE3, 0xC0,
0xED A0..) is a valid start and answers (0,0) as pcrec does. So K73 is not
about the empty pattern: any empty-matching pattern is affected, as is any
pattern whose first attempt would begin on the continuation byte.

**Why pcrec differs.** `enc_utf8`'s emitted start guard exempts 0
(`search_from == 0 || ...`, `rx_search` head), so the first candidate on a
subject that begins with continuation bytes is a non-boundary — which
contradicts `match_api.md` §3.1's "every position the ENGINE generates is a
character boundary of the encoding" and disagrees with §3.1.1's own normative
advance (skip 0x80-0xBF).

**Why this lane did not fix it.**
1. The fix is emitted text: the guard (and the equivalent on the anchored and
   `_in` entries) changes for every `-e utf8` artifact — an `abi` event with
   the D76/D94 ritual and identity re-pin, which this lane, with the full
   `make test` OWED, should not start unasked.
2. It is a contract choice: §3.1 says "neither arm ROUNDS the caller's
   startpos" for the mid-character refusal. Options: **(a) recommended** —
   round ONLY the default start 0 over leading continuation bytes (pure
   ill-formed-subject behaviour, since a well-formed subject never starts on
   one; explicit mid-character `startpos>0` keeps the K50 refusal, a
   deliberate, stated divergence from MATCH_INVALID_UTF); (b) also round
   explicit `startpos` on continuation bytes of ill-formed subjects (matches
   the oracle everywhere, but reverses K50's measured refusal ruling for that
   population); (c) remove the 0 exemption and refuse (`PCREC_ERR_STARTPOS` on
   `\x80` — contradicts `axis03`'s `n "\x80"` cells and the "ill-formed
   matches nothing, no error return" sentence, §8.2). Anchored entries would
   follow the same choice (the oracle rounds them too).
3. Sites, if (a) is ruled: `pcrec_enc_start_guard` (`src/enc/enc_utf8.c`) /
   `pcrec_startpos_guard_text` (`emit_dfa.c:638`) for the DFA entries and
   `emit_vm.c:12912`'s three `_run` statics, plus `-fno-startpos-guard` staying
   byte-identical (it must remain "the caller's position honoured").

`known_issues.md` K73 now carries the measured rule and reads "OPEN, held for
a ruling". No `known_fail` repro was filed (it would move the rxtsource census
and the known-fail ratchet for a held item); the exact cells are in the
transcript and in this report: `m "\x80" 1 1`, `m "\x80\x80" 2 2`,
`m "\x80\xc3\xa9" 1 1` for pattern `` under `encoding utf8` (pcrec answers
`0 0` on all three; `m "\xff" 0 0`, `m "\xe3\x80" 0 0` already agree).

## Validation

- `make strict CC=gcc-16`: clean.
- `make test-registry`: rc 0 (PC-3 213/0, definitions oracle 354 cells /
  101,244+101,244 comparisons, 0 disagreements; log `build/scratch/reg.log` in
  the worktree).
- `make test-rxtsource` (PROCS=2): 270 passed / 1 recorded (standing py3.9
  RECORD) / 0 failed, after the re-pins (10 failed before them).
- `tests/harness/run.sh tests/utf8 tests/classes tests/ucp` (PROCS=2): see the
  handback message for the result (`build/scratch/h.log`).
- **OWED**: full `make test`; `make test-codegen`/identity gates were not run
  (no emitted-text change is claimed; the manager's full run confirms).
