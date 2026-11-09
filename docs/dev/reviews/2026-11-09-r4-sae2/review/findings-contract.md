## Findings


### CONTRACT-1 — `<PREFIX>_REQ_BYTE`'s spec ("a byte every match must contain") is false under `\K`, and E2 makes the pick land BEFORE the reported start in new cases; the REQ_RUN rewording was not carried to REQ_BYTE
CONFIRMED. Severity: doc (answers hold; contract sentence false). Effort: small (one sentence in each of 4 places). Blast radius: caller-facing spec + public header comments.
Where: docs/spec/match_api.md §6.3.7¶4 (and its example comment "every match contains '>'"), docs/spec/tuning.md §2.27¶1 ("Where every match of a pattern must contain some literal byte") and §2.27¶3 ("Every member is a byte every match contains"), docs/spec/facts_listing.md §1¶2 ("the byte every match must contain"), lib/pcrec.h:797 and :870.
Ruling context: R-d says REQ_BYTE keeps "a byte every match contains"; D191 item 2 spells it "a byte every match CONSUMES". The two DIFFER under `\K`: "consumes" (a successful attempt consumes it, attempt-relative) is what the subject delivers and is true in every row below; "contains" read as the REPORTED match is false. The spec text states "contain". D191 item 3 (§12b) "a run outside the match is ONE run value, every reader raised together" — REQ_BYTE is `bytes[idx]` of that run (§6.3.7¶7) so it is a reader, and its sentence was not raised with ¶6.
Repro: `contract/facts.sh PAT` (BASE vs SUBJECT `--emit-facts` req_byte), `python3 -I pcre2_bounds.py PAT SUBJ` (libpcre2 reported bounds). Table (byte in decimal; IN = byte value inside reported match):
| pattern | subject | BASE byte | SUBJECT byte | libpcre2 bounds | BASE in? | SUBJECT in? |
|---|---|---|---|---|---|---|
| ab\Kcd | xxabcd | 99 c | 98 b | (4,6) | yes | NO (new) |
| q\Kab | zqab | 98 b | 113 q | (2,4) | yes | NO (new) |
| qz\K(?<=qz)wv | qzwv | 118 v | 122 z | (2,4) | yes | NO (new) |
| [a-z]ab\Kcd | zabcd | 99 c | 98 b | (3,5) | yes | NO (new) |
| ab\K(?<=ab)cd | abcd | 99 c | 98 b | (2,4) | yes | NO (new) |
| xy\Kz | -xyz | 120 x | 122 z | (3,4) | NO | yes (fixed by E2) |
| abc\K | abc | 98 b | 98 b | (3,3) | NO | NO (pre-existing) |
| k\Kj | kj | 106 | 106 | (1,2) | yes | yes |
| \d\K[a-z]abcd | 1zabcd | 98 | 98 | (1,6) | yes | yes |
| r\Ka(?=bq|bc)bc | rabc | 98 | 98 | (1,4) | yes | yes |
| (?:q\K|z)abc | qabc | 98 | 98 | (1,4) | yes | yes |
| (ab)\K\1 | abab | 98 | 98 | (2,4) | yes (by value; the necessary occurrence is the first copy) | same |
| foo\b-bar | foo-bar | 45 | 45 | (0,7) | yes | yes |
| xyz(?<=yz)abc | xyzabc | 98 | 122 | (0,6) | yes | yes |
| ab(?=cd)cd | abcd | 99 | 98 | (0,4) | yes | yes |
| ab\Gcd | abcd | 99 | 98 | nomatch | - | - |
So the PICK does not honour R-d read as the reported match (5 new violations, 1 removed, 1 pre-existing); it honours D191's "consumes" everywhere. Only `\K` moves the byte outside: no lookaround body is read, so E-5 joins never put a byte outside.
Readers: the emitted pre-check scans `[search_from, n)` and every attempt starts at or after search_from, so no reader needs the byte inside `[reported start, end)`; differential below holds. Fix: reword ¶4 / §2.27¶1,¶3 / facts_listing §1¶2 / pcrec.h comments to ¶6's attempt form ("a byte every successful attempt consumes"; under `\K` it can lie before the reported start), or have the owner restate R-d as D191's "consumes".

### CONTRACT-2 — sibling sentences of the "every match contains/at a fixed offset from every match's start" family that E2 newly falsifies under `\K`, left unchanged
CONFIRMED. Severity: doc. Effort: small. Blast radius: spec only (values are attempt-relative and answers hold).
(a) docs/spec/tuning.md §2.30¶1: the run-pinned rows apply "Where the pattern's necessary run ... sits at a fixed offset from every match's start". `run_pin` is attempt-relative: `[a-z]ab\Kcd` SUBJECT `run_pin=1`, run `abcd` at attempt+1, reported start attempt+3 (libpcre2 (3,5) on `zabcd`), i.e. the pinned run begins 2 bytes BEFORE the match's start (BASE: run `cd`, pin 3 = reported start + 0). Also `ab\K(?<=ab)cd` pin 2 -> 0, `[a-z]ab\K(?=c)cd` pin 3 -> 1. `--emit-facts`' `run_pin` sentence (facts_listing §4.1.2¶7) names no origin at all. Pre-existing for `(?:q\K|z)abc` (pin 1, reported-start offset 0 or 1), but E2 adds the before-the-start case. Emitted DFA_PREFILTER "run-pinned" on `[a-z]ab\Kcd`, `[qz]ab\Kcd`, `\d\K[a-z]abcd`, `(?=ab)\Kabcd`, `r\Ka(?=bq|bc)bc` answer-identical to libpcre2 at every start offset.
(b) docs/spec/facts_listing.md 4.1.2 para 8c (lane/sae2) (`req_pieces`): declines "where some part of the pattern ... is a zero-width item (`decline:not-fixed-width`)" — false since E2: `x(?:ab|c)\bde`, `x(?:ab|c)\Kde`, `x(?:ab|c)(?=d)de`, `x(?:ab|c)(?<=b)de`, `x(?:ab|c)\Gde` all went from `none [decline:not-fixed-width]` (BASE) to `4:[120][99][100][101]|5:[120][97][98][100][101]` (SUBJECT). And "every match of length W" is false under `\K` (`x(?:ab|c)\Kde` reported length 2, pieces 4/5). No caller reads it but the listing; the sentence is the listing's contract.
(c) docs/spec/tuning.md §2.28¶3: "everything that breaks the byte analysis breaks the run", with §2.27¶2 "any assertion contributes the empty set (which disables the check)" — read together they still say an assertion breaks the run, which E2 reversed (§2.28¶1 was reworded, ¶3 in the same section not). Needs "a node that consumes nothing joins the run (CAT's unit)".
(d) facts_listing §4.1.2¶8a (`req_set_maxoff`): "from the attempt start (some occurrence of the byte in every match begins at most K bytes in)" — origin right, parenthesis wrong under `\K`; pre-existing (req_set_maxoff unchanged by E2 in every probe), listed for the same rewording pass.
Held (not a finding): match_api §6.3.7¶11 "every match begins at most K bytes before an occurrence of the landmark" stays TRUE under `\K` because the reported start >= attempt start >= hit - K; req_run_maxoff (¶8), req_landmark_maxoff (¶8b), §2.41¶8b already say "from the attempt start".

## PROBED-AND-HELD
- Answer identity, SUBJECT matchers vs libpcre2 at EVERY start offset (contract/cmp.sh: rx_search(subject, n, startpos) for startpos 0..n vs pcre2_match at the same offset), default engine AND --engine=vm: 52 patterns x 2 engines x 6-7 subjects, 0 diffs. Covers `\K` before/inside/after the run, in a group, an alternation branch, a `+`/`?`/`{2}` repeat, an atomic group, doubled `\K`; joins across `\b`, `$`, `\Z`, `(?=..)`, `(?!..)`, `(?<=..)`, `(?<!..)`, `\G`, `(?:)`, `(?:\b)*`, a check callout; routes hit: hybrid run-pinned/run-pinned-bounded, handoff (DFA K=3, VM attempt loop K=0..3), cover, rev-end, attempt, memchr. 4 UTF-8 `\K`/`\b` patterns x 4 subjects (emit-main vs pcre2 --utf): 0 diffs.
- Offset facts: req_run_maxoff, req_landmark_maxoff, req_set_maxoff, run_pin, REQ_HANDOFF are all measured from the ATTEMPT start (confirmed on 12 `\K` patterns: e.g. `[a-z]ab\Kcd` maxoff 1, pin 1, HANDOFF "1"); their spec sentences facts_listing §4.1.2¶8/¶8b/¶8a and tuning §2.41¶8b say "attempt start" (true); match_api §6.3.7¶11 holds weakly (reported start >= attempt start). Only §2.30¶1 / ¶7 and ¶8a's parenthesis misstate (CONTRACT-2).
- `@n` in REQ_RUN is an index into the run, not an offset; REQ_BYTE == bytes[idx] held in every probe (§6.3.7¶7).
- match_api §6.3.7¶6 as reworded: true for `\K` in a group, alternation, repeat (last crossed `\K` sets the start; run still between attempt start and end). `\K` inside a lookaround body is REJECTED by pcrec ("\K is not allowed inside a lookaround"), so the reported start can never precede the attempt and the run can never lie after the reported end; the wording is complete for what pcrec accepts. Verbs ((*ACCEPT) etc.) and conditionals are rejected, so no zero-width node that ends the match early reaches T3.
- `(*ACCEPT)`-like hazard for T3 "consumes nothing => bytes on both sides adjacent": none reachable (verbs module rejects).
- Restore lever: `harness=restore=zero` reproduces BASE values on `ab\Kcd`, `x(?:ab|c)\bde`, `xyz(?<=yz)abc`, with `harness:zero` on every derived fact (4.1.3 para 4a (lane/sae2)).
- Names (D174): no caller-facing name changed except arm `zero` / token `harness:zero`, which describes the behaviour. Internal `rb_assert_into` now also serves restored `A_EMPTY` (comment updated; internal name, not D174's scope).
