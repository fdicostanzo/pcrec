# Critic round "iter" — lens CONTRACT (opus)

Subject 588714855 vs base 02f357b39. Probes: /tmp/claude-1001/crit-iter/contract/ (drv.c = artifact vs
libpcre2 global loop per pcre2demo.c, plus next_n at k=1,2,3,7,64, NULL-caps counts, next/next_n
alternation, copy-at-every-point, info->next; edge.c = state machine/start-position edges;
sweep.py/targeted.py = drivers). Box was under boxlock (test-recursion-identity); my sweeps ran
serially under nice -n 19.

## Findings

### CONTRACT-1 — CONFIRMED, answer: the DFA retry machine treats `^` as true at every retry position

`<prefix>__retry` (dfa-root form) is built by `build_notempty_dfa`
(src/core/compile.c:350-364) rooted at `nfa.anch_start`, the root a match at offset 0 reads from,
where `^` holds. It runs at `q > 0` too, so a `^`-anchored alternative matches at the retry position.
The VM's guard form is right, `_match`/`_search` at the same position are right (`match@2 = 0` for
` *|^x+` on `"  x"`), so only the iterator is wrong.

Repro (default engine = dfa, byte and utf8 alike):

    build/pcrec -p rx -o art.c --pattern ' *|^x+'      # RX_ITER_RETRY "dfa-root"
    subject "  x":   libpcre2 global loop: (0,2) (2,2) (3,3)
                     rx_next:              (0,2) (2,2) (2,3) (3,3)    <- (2,3) is ^x+ at offset 2
    --pattern '|^x'  subject "xx": PCRE2 (0,0)(0,1)(1,1)(2,2); rx_next adds (1,2)
    --pattern '|(?:^a|b)' subject "aab": PCRE2 (0,0)(0,1)(1,1)(2,2)(2,3)(3,3); rx_next adds (1,2)
    --engine=vm on the same patterns: all OK.

Expected per §3.8¶2: "the preferred NON-EMPTY match anchored at q (PCRE2's retry under
NOTEMPTY_ATSTART | ANCHORED)". Found by the random sweep (pattern `[ab]?|a??b{0,2}^.`, 2 of 114
compiled utf8 groups), then minimized. Class: an empty-matchable alternative beside a `^`-anchored
non-empty one (`\s*|^#.*`-shaped patterns are realistic). Effort: small (root the retry at a
not-at-start root when q > 0, or two roots chosen by q == 0, or decline dfa-root when the pattern has
a start anchor and take vm-guard). Blast radius: every DFA artifact with `^` in an alternative that
also reports empty; the existing cells (tests/findall/cells.tsv) evidently carry no such shape at a
retry position > 0 — the checks' population gap is worth a cell.
`\A` is hit the same way (`--features all`, `|\Ax` on "ax", "xx", " x", "a\nx": rx_next adds (q,q+1)
on all four, dfa and auto). HELD on the same probe: `\b`, `\B`, `(?<=a)`, `(?<!a)`, `\G`, `(?m)^`,
`x\b` (all dfa-root, 4 subjects each, 0 DIFF), so only the start-of-subject root is confused.

### CONTRACT-2 — CONFIRMED, answer (minor): under `-fstartpos-guard=align -futf-check`, `it.lo` after a PCREC_ERR_UTF refusal is the UNALIGNED start, not "the position `<prefix>_valid_upto` is asked from"

§3.8¶9: "on a `PCREC_ERR_UTF` refusal, [lo is] the position `<prefix>_valid_upto` is asked from".
`<p>__bind_checks` (emitted by src/gen/emit_iter.c, the bind prologue) aligns a local
`search_from`, asks `__valid_upto` from the ALIGNED position, and writes `*pos` only on success, so
the refusal leaves `lo` at the caller's unaligned position.

    build/pcrec -p rx -e utf8 -futf-check -fstartpos-guard=align -o art.c --pattern 'a|'
    subject 61 c3 a9 80 ff 61, rx_iter_at(&it, 2):  rc=-9, lo=2
    valid_upto was asked from 4 (2 aligns past a9 and the stray 80 to ff); valid_upto(s,n,2)=2,
    valid_upto(s,n,4)=4 — a caller who re-asks valid_upto from lo gets the wrong offset.

Effort: one line (write the aligned position before the UTF check, or spec "the caller's start").
Blast radius: align+utf-check artifacts, refusal path only. Probe: contract/ua.c.

### CONTRACT-3 — DOC: §3.8.2's generic loops do not compile for the caller they are written for

§3.8.2¶1 says the caller holds ONLY `rx_info` and needs no artifact header, but both examples size
their buffers with the compile-time `NCAPS` (`ptrdiff_t caps[NCAPS][2]; /* info->ncaps pairs */`,
`ptrdiff_t buf[8 * NCAPS][2];`), which such a caller does not have. The text should show the real
spelling (a VLA `ptrdiff_t caps[info->ncaps][2]`, or a caller bound `MAXCAPS` with a check that
`info->ncaps <= MAXCAPS`, or malloc). the branch spec, iterator section (lines 1152-1170 at the subject). Effort: trivial. Severity: doc
(a copy-paste caller gets a compile error, not a wrong answer).

### CONTRACT-4 — DOC (nit): §3.8¶6a "whatever the subject holds" is false for a start past `n`

`rx_iter_vars` with an UNSET `${p}` and `rx_iter_at(&it, 9)` on `"ab"` ends with rc = 0, not
PCREC_ERR_UNSET_VAR — consistent with `rx_search(...,9,...)` = 0 (the `> n` test precedes the vars
check), so the code is right and ¶6a over-claims. Add "a start past n ends with rc 0 before any check".
Probe: contract/vr.c, contract/vs.c.

### CONTRACT-5 — NOTE (D174, not retroactive): `<PREFIX>_ITER_RETRY` values `"dfa-root"` / `"vm-guard"`

They name the mechanism, not what the caller sees. Shipped at I1 (38a439e25, 2026-10-21), before
D174 (2026-10-22), so not a finding; list it for [IFACE-PUSH]. Every name I4 added (`next_n`,
`rx_nextnfn`, `rx_info.next_n`) describes behaviour. Every observable change I checked has its spec
hunk (§1, §2, §3.8.1, §3.8.2, §4¶9a, §6 rows 30/31, §6.3.13); D80 held.

### CONTRACT-6 — DOC: neither design note states ranked, checkable goals (architecture.md "A design states its goals")

docs/design/findall_iter.md (rev 3) and docs/design/findall_iter_i2.md (rev 2) open with revision
logs and "Answers first"; neither has a Goals section, a priority order or NON-GOALS. Both predate
the rule (7596be6e8, 2026-10-23), so this is a doc gap, not a process failure; but the notes are the
record the next stage ([FINDALL-NEXT] st, D173's substitution driver) designs from, and I1 is also
stale in place (it still describes `rx_iter_batch`, `PCREC_ITER_OPT_BATCH 0x80`, `rc_next`; the
delivered §3.8¶5a makes 0x80 reserved). Fix: a short Goals block on findall_iter_i2.md (or a
stage-neutral one on findall_iter.md) carrying the list below.

GOALS THE DESIGNS IMPLY, ranked (my reading of D165 add. 2 Q1, D171, D175, the parity gates):

1. ANSWERS — for every caller of find-all: `_next`/`_next_n` report exactly libpcre2's global-loop
   spans (pcre2demo.c: NOTEMPTY_ATSTART|ANCHORED retry, then one character on) on every well-formed
   subject, every engine and encoding. Check: differential vs libpcre2 over the corpus, 0 DIFFs.
   (Ill-formed subjects: the two named §3.8¶2a differences only.)
2. NO SLOWER THAN THE HAND LOOP — for the caller replacing §3.1.3's loop: a find-all over `_next`
   costs no more than the hand `_search` loop on dense subjects (c1, c3, c4), within the A/A floor;
   fixed setup up to ~2 ns accepted on degenerate cells (D171).
3. BATCH GAIN — for dense cheap matches: `_next_n` is faster than `_next` (F/I < 1 − floor on c3
   R2) and loses nowhere gated (c1, c4, c6), with an early stop costing no unseen searches.
4. GENERIC REACH — for a header-less caller (catalog, dlsym): iterate through `rx_info.next` /
   `next_n` alone, at ≤ ~0.5% over a direct call (D175's 0.3-0.4%).
5. MISUSE IS CHEAP TO DETECT where it is cheap — a never-initialized/zeroed struct or a late setter
   refuses (PCREC_ERR_ITER); end is sticky; no per-call owner check (D165 add. 3).
Priority: 1 > 2 > 3 > 4 > 5 (D175 dropped RX_FOREACH because genericity cost speed: 2/3 over 4).
NON-GOALS: internal batching / callback entry (withdrawn, I2 §1.2); newline-convention CRLF
stepping ([DD-11]); libpcre2's restart on ill-formed subjects (K75); owner checks across artifacts;
a stable rx_info layout separate from abi (U-I2-7).

JUDGEMENT: the delivered interface serves 2-5 in that order (two entries, no macro, header-less
pointers, a four-state header). It FAILS goal 1, the top goal, on the DFA retry form (CONTRACT-1),
and the gates that would have caught it were built from cells chosen by the code's own alphabet
(no `^` alternative beside an empty one at a retry position > 0). Goal 4 is served by the entries
but undercut by the spec's own example (CONTRACT-3).

## PROBED-AND-HELD

Each driver case compares, per subject: libpcre2's global loop (G) against `rx_next` (I) on spans,
every capture pair and the final rc; then `next_n` at k = 1, 2, 3, 7, 64 (spans, caps, rc, and lo when
rc < 0); `next`/`next_n(NULL)` counts; `next`/`next_n(2)` alternating; a copy of the iterator taken
at every point and run to the end; `info->next`; stickiness after the end (returns 0, rc unchanged,
caps untouched); "r == k but ENDED" / "r < k but live".
- Random sweep, byte, std1 features: 156 artifacts (auto/vm/dfa), 3,304 subjects, 0 DIFF.
- Random sweep, utf8 (subjects with é), std1: 114 artifacts, 2,494 subjects; only DIFF was
  CONTRACT-1's pattern.
- Targeted list (spec's own examples `|a`, `a*?`, `x*|y`, `a??b?`, CSV idiom, `$`, `^`, nested empty
  groups, `(a|)*`, `.*?`, 200-byte dense subjects across batch boundaries): std1 byte 1,426 subjects,
  0 DIFF; `--features all` byte (adds `\K`, `\G`, lookaround, `\b`, `(?m)`, atomic, possessive,
  backrefs, branch reset) 2,967 subjects, 0 DIFF other than the `^`/`\A` shapes above.
- Not completed (stopped at the manager's call): the `--features all` utf8 targeted run and the
  200-pattern `--features all` random byte sweep; no output was lost that held a DIFF (buffered).
- State machine (3 artifacts, byte/utf8/utf8+utf-check): zeroed struct -> 0, rc -10; k = 0 on a zeroed
  struct (caps and NULL) -> not refused, hdr untouched; setter on BOUND -> rc -10, lo unchanged;
  setter on ENDED -> nothing; reserved 0x80 bit -> FRESH; k = 0 keeps FRESH and setters still apply;
  k = SIZE_MAX with caps and with NULL; next_n after end; re-init; info.next/next_n non-NULL, ncaps
  = NCAPS.
- Start positions 0..n+5 and SIZE_MAX against `rx_search` from the same position, under plain,
  `-futf-check`, `-fstartpos-guard=align`, both: codes and order agree with `_search` (the one lo
  mismatch is CONTRACT-2).
- Give-ups (`--engine=vm --step-budget=200`): in the search after two matches (rc -2, lo 2) and inside
  the anchored retry (`|(a|aa)*c`, rc -2, lo 1 = the retry position), identical for next and next_n
  k = 1..5.
- Variables (`${p}|`, dfa and vm): set, set + at, UNSET (rc -8, lo = start), none bound (rc -8), EMPTY,
  empty subject; next_n k = 1 agrees.
- Caller buffers (`<prefix>_iter_buffers`, vm): 0/1 frames -> rc -3 = `search_in`'s; 2/3 frames ->
  same spans as the artifact's own storage.
- D80: every caller-observable addition found in the diff has its spec hunk. D174: CONTRACT-5.
