# vmminw findings

## Findings

None. Every probe agreed with libpcre2, and no construct turned a match into a no-match at the W boundary. SUBJECT tree: worktrees/crit-s1 @ 3da0d446b.

Notes (not findings):
- (*ACCEPT) is refused ("requires module 'verbs'"). (*COMMIT)/(*SKIP)/(*PRUNE)/(*THEN) are refused as out of scope. Conditionals `(?(...)` are refused ("module 'conditionals' ... not implemented yet"). So no artifact today carries an early-ending or position-cutting construct that root_minw would need to discount. When verbs or conditionals land, `pcrec_minw` (src/opt/mrl.c:151) has no arm for them, and that arm must be decided then (-Wswitch forces it). (*ACCEPT) in particular must not add the width of what follows it.
- A_BREF, A_VAR, A_CALLOUT, A_LOOK (both directions), A_KRESET, A_GSTART and A_CTX all contribute 0 in `pcrec_minw`, which is exact or an under-estimate. A_CALL reads the callgraph fixpoint's `u.call.minw` (arena zero before the fixpoint, so it is safe). A_ATOMIC is transparent, which is sound because an atomic cut removes matches, not bytes.

## PROBED-AND-HELD

Method: tools/probe.py builds SUBJECT `$P` and runs `rx_search(s, n, startpos)` (tools/drv.c). For each base subject it tries prefixes ''/'z'/'zz', every startpos from 0 to len(prefix), and the subject with its last byte dropped (one byte under W). It compares the match span against libpcre2-8 pcre2_match with the same startoffset (UTF|MATCH_INVALID_UTF|UCP under -e utf8, CASELESS for -i). 100 pcrec compiles in total.

- Batch 1, UTF-8 caseless with fold partners of different byte lengths: 16 patterns x 2 flag sets = 32 artifacts (64 compiles, lever builds included), 394 cases, 0 mismatches vs pcre2, 0 differences vs `--harness=no-min-width`. Cases: K/U+212A, s/U+017F, ß/U+1E9E, U+2C65/U+023A, U+0130, U+2126/ω, as literals and through caseless backreferences `(?i)(X)\1`. The emitted W is the byte minimum over fold variants: for example, (?i)(KK) gives W=2, not 6, and (?i)(ẞ)\1 gives W=2.
- Batch 2: 28 patterns, about 950 cases, 0 mismatches vs pcre2. 24 compiled and 4 were refused (conditionals). Constructs covered:
  - recursion and subroutines: `(a|b(?1)c)d`, DEFINE+(?&g), `^(?:a|b(?R)c)$`, `^(a(?1)?b)$`, relative `(?-1)(?+1)`, calls into a group holding \K, a lookbehind or a lookahead
  - named, duplicate-name (?J) and unset-group backrefs: `(a)?\1bc`
  - atomic and possessive
  - \K and lookbehind
  - \G with startpos > 0 (anchored `ub->attempt_max` branch, entry check W=3 still emitted)
  - hybrid prefilter: `--engine=vm -fprefilter`, RX_VM_PREFILTER "hybrid", W=2, with the entry check and attempt_max both present
  - (?m)^/$ and \z
  - utf8 caseless subroutine and backref mixes
- Code read (src/gen/emit_vm.c:13565-13901): the anchored BOUND row takes precedence over the min-width bound. The entry check runs after the end-window clamp and the `search_from > subject_length` guard, so `subject_length - W` cannot wrap. A prefilter, req-byte or UTF-8 advance that seeds past attempt_max costs one failing attempt and then returns, and never skips a position <= attempt_max. The ceiling and min-width rows are disjoint (`!ceiling`). W >= 2 means no empty match, so the iterator's empty-match retry is unaffected.
- Not run: ${vars} and callouts (they need a context driver). Both are 0 in `pcrec_minw` by code read, so they can only under-estimate.
