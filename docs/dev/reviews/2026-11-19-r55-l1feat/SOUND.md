# CRITIC sound — round r55 l1feat

## Findings

No findings. Every guard/meet/never step derived in src/facts/req.c at 40e2e8626 was read to an alignment proof, and no answer differential (about 1,500 compiles, byte and utf8, three engine selections) and no `dead` claim failed. I also found no suspected unsound fact value that is not yet read.

## PROBED-AND-HELD

Code read (SUBJECT `git diff 07c840368 40e2e8626 -- src/facts`, plus desc.c's head and description combinators) and alignment argued for each step:
- CAT-R/CAT-L (`rn_guard_onto_head/_tail`): a head stores its FIRST positions and a truncated tail its LAST (`rn_app`/`rn_pre`), so a forward meet at the right factor's start and a backward meet at the left factor's end are at equal subject offsets even when truncated. The leftover slice assumes width == stored n, and that holds only where `all` (which is false on truncation; zero-width units store 0 and have width 0). CAT-EDGE crosses only `all` neighbours.
- ALT post-step: `lg` is the common tail (each branch's `lg` ends at the shared alternation start), and `rg` is the common head (each starts at the end of the branch that matched). Both are right for unequal branch widths.
- REP: `rr_pow`'s X^c (c <= m) guards hold in X^m by self-similarity of the copies. The guards of `rr_rep_split` come from p = X^c; at m=0, p is the unit, so it has no guards and no never. `rb_rep_unit_val` m=0 carries nothing, and m>=1 carries the body's guards. `rb_rep_best_val` carries never only.
- Item: the lookahead head (`pcrec_ph_*`) is conservative: REP/BREF/CALL are walls, ALT takes the min-h union, and closed is required before appending `rg`. Lookbehind `pcrec_pd_tail_head` reads the last stored positions of each width group (hull-merged supersets, right-aligned). A nested lookbehind/lookahead `lg`/`rg` is relative to the body start/end, which is the cursor. For `A_CTX`, NEXT/PREV only, and an `onebyte_max` bound keeps utf8 to ASCII.
- TOP set step: `run.off` is the K82 upper bound of the run start (head 0, tail maxw-n with the last n stored), so `off+i` is an "at most" bound. A byte already in the set keeps its own (possibly looser) bound, which is not unsound.
- never/dead: the empty-class leaf, empty consumed meets, empty guard-guard meets, ALT EVERY, CAT ANY, and the lookaround BODY rows. Negative lookarounds and DEFINE/call targets are not walked (checked: `(?(DEFINE)(?<n>(?=a)b))c` is not dead).

Answer differential (kit fuzz.py, every start offset, vs libpcre2-8), SUBJECT tree:
- Hand witness set w1, 106 patterns: guards across all/non-all neighbours; alternations of unequal width; lookarounds in `?`/`*`/`+`/`{m}`/`{m,n}`/`{0,n}` and nested repeats; nested ahead-in-behind and behind-in-ahead; `$` `\z` `\Z` `\b` `\G` `(?m)` `\K` backrefs recursion atomic possessive `(?*` caseless one-char A_CTX; `.`/`(?s)`; empty `(?:)`. VM: 101 OK, 3 refused (conditionals, `\K` in a lookbehind), 2 GCC-FAILED (callouts; the kit driver has no callout). DFA: 38 OK, the rest refused (multi-char lookarounds are VM-only).
- Observed mover population (kit compare observed.tsv, 316 rows):
  - The 125 non-uprop movers: VM 125 OK; DFA 38 OK, 87 refused.
  - The 191 uprop `dead` movers (byte): 105 checked against libpcre2-8 on a subject of all 256 bytes (non-UTF) gave N. 86 are Age/Block (pcrec extensions libpcre2 lacks); argued instead: no member <= 0xFF.
  - Every other `dead` mover was checked as a real contradiction, including the utf8-only `\w{1,3}(?=a)\W`, `a{1,3}?(?=\w)\W` and `\p{Cs}` (surrogates).
- Random generator (gen.py: positive look(ahead/behind) nested <= 2, quantified, alternations, alphabet abc):
  - r1, 300 patterns, VM: 296 OK, 4 oracle-err. 205/300 reached >= 1 pcre2 match, 106,029 match answers, longest match 30.
  - r2, 150 one-char (A_CTX) patterns, DFA: 150 OK, 112/150 with matches.
  - A facts sweep base vs subject on r1 (emit_sweep, facts stream): 33 movers, all among the fuzzed.
- Utf8 (my fuzzu.py: a character alphabet, character-boundary offsets only): 29 witnesses (Kelvin sign `(?i)(?=k)\x{212a}`, long s, `é`/`É` caseless, 2-byte guards, `(?=\w)\W`, empty classes), VM 29 OK. Plus 10 utf8 movers.
- DEFAULT engine selection. KIT CAVEAT: `--engine=vm` emits `RX_VM_PREFILTER "none"`, so a VM-forced fuzz never reads the run. The hybrid/DFA prefilters read it (run-pinned, offset-set, memchr, handoff, byte-class, as seen in emitted rx.c). Results:
  - 261 patterns (w1 + 125 movers + 33 r1 movers) in byte mode: 256 OK, 3 refused, 2 callout GCC-FAILED.
  - w2u in utf8: 29 OK.
  - u3 in utf8: 10 OK.
- Truncation and handcrafted long witnesses (oracle.sh vs match.sh, VM and DFA): 22 cases, all equal to pcre2 (DFA refused where multi-char).
  - Lookbehinds and lookaheads of 33-42 literal bytes against `[ab]{33..50}`, `[ab]+`, and `(?:[ab]{20}(?<=a{19}b)){2}c`.
  - Repeats with interior guards: `(?:[ab](?=[bc])){3,}c`, `(?:(?:(?=ab)a)+b)+c`.

Minimum witness length reached: random pools are length 0..10/12, with matches up to 30 bytes. Handcrafted witnesses go up to 51 bytes, past the 32-position run store (PCREC_MAX_REQ_RUN_SCAN).

CRITIC COMPLETE
