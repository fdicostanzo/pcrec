# Review r1 (2026-10-22): [M4-SUBST] compiled substitution as an independent element, `replace_design.md` §R2

Panel: three read-only critics.
- `substcrit1` (opus) took semantics against PCRE2, with probes against libpcre2 10.46.
- `substcrit2` (opus) took modularity, cost, architecture and unlocks.
- `substcrit3` (sonnet) took the embedder's lens.

Target: `docs/design/replace_design.md` §R2 on `lane/subst` @ 7d44d7016 (from
`lane/i2build`, abi 84). Dispositions are the manager's. Lane `substr3` applied them
as §R3 of the note; the last column of the table says where.

**Verdict.** There was one BLOCKER, and it is real: §R2.5 rule 1 ("spans ordered and
non-overlapping by construction") is false. A `\K` reached through a subroutine call
from a lookaround reports backward and overlapping spans. The §R2.4 glue then wraps an
unsigned gap and `memcpy`s `SIZE_MAX` bytes (crit1-1, reproduced by crit1 as a stack
smash and a SEGV). The fix is a per-span check in the element, not a sentence in
match_api §3.8. crit3 filed three blockers (crit3-1..3) on codes, binding identity and
length arithmetic. All three are accepted and fixed by construction. The design changed
in four places:
- the element is BATCH-shaped (crit2-1);
- a name binds to a RUN (crit1-2);
- the binding carries the rx (crit3-2);
- the glue drives `next_n` itself (crit2-3).

| id | sev | finding (short; verbatim text below) | disposition | where (note §) |
|---|---|---|---|---|
| crit1-1 | BLOCKER | rule 1 false: `x(?=(?1))\|(b\K)` on "xb" reports `[2,1)`, `x\|(?<=(?1))y\|(\Kx)` on "xy" reports `[0,1)` then `[0,2)`; the glue wraps and smashes; PCRE2 −60 | ACCEPT: the element validates every span (`end < start`, or `start < previous end` under gaps) → `PCREC_SUBST_BADSPAN`. PCRE2 tests `start < search start`; the iterator cannot expose its search start cheaply, so the corner is DOCUMENTED with a witness (`^\|(?<=(?1))y\|(?!)(\Kz)` on "zy": pcrec renders, PCRE2 −60). Nothing added to match_api §3.8. Corpus cells: both patterns, plus the corner | §R3.6; probe 1 (§R3.14) |
| crit1-2 | MUST-FIX | a single-int binding cannot hold a duplicate-name run (`(?J)(?<n>a)\|(?<n>b)`, `[${n}]`: pcre2 `x[a][b]y`, R2 `x[a][]y`); name→run resolution exists three times | ACCEPT: a name binds to `{first, count}` rows of `rx->groups` (the slot list); the render walks per match_api §5.4¶6. One header helper `rx_group_run` does the bind's resolution; match_api §5.4¶6's prose and the compiler's `\k<name>` resolver are LATER ADOPTERS (not rewritten), with an agreement cell in phase B | §R3.2 |
| crit1-3 | NOTE | NOSPACE not compared: pcre2 −48 required 12 (counts NUL), pcrec 11 | ACCEPT: labelled and spec'd (PCRE2's minus one, D38 Q4) | §R3.5, §R3.10 row 1 |
| crit1-4 | NOTE | unset → empty matches PCRE2 only under UNSET_EMPTY; the axis should list `error` | ACCEPT: D38 Q3 already ruled "a GENERATION AXIS with a strict PCRE2-error variant"; R3 names the values `empty`/`error` and gives `error` the code `PCREC_SUBST_UNSET` | §R3.7 |
| crit1-5 | NOTE | ill-formed UTF-8: `x*` -e utf8 on "a\xffb" — pcrec 4 matches (0,1,2,3), PCRE2 MIU 3 (none at 1); pin it | PROBED (the manager's fact 2): CONSISTENT with match_api §9 and with `_search` in a loop on 15/15 cells; libpcre2's single searches agree at every offset; the difference is libpcre2's anchored NOTEMPTY retry reporting `(2,2)` from anchor 0 (match_api §9.3¶3's class). Not a defect candidate; pinned as stated behaviour; a §3.8¶2 spec candidate | §R3.14 probe 2 |
| crit1-6 | NOTE | `*outlen` unwritten on the iterator-rc and render-failure returns; pcre2 sets UNSET | ACCEPT: `*outlen`/`*nsubst` written on every path | §R3.4, §R3.5 |
| crit2-1 | MUST-FIX | a per-match out-of-TU call is not D171's class; make the element batch-shaped (`render_n`), per-match = k = 1; probably settles Q-F2 | ACCEPT: `rx_substfn` renders k matches, gaps inside (`RX_SUBST_GAPS`), length in an `rx_subst_cur`. Q-F2 restated (the remaining difference is inlining only) | §R3.1, §R3.16 |
| crit2-2 | MUST-FIX | abi coupling unstated: any rx abi event orphans every subst artifact; say "same build" or render on primitives keyed to a shape-contract version | ACCEPT the plain statement: one pcrec build (same abi), `#error` at compile and a check at bind. The shape-contract version is NOT designed; it is named as a candidate under [DD-3]/[RXINFO-REMODEL] | §R3.8; candidate C2 below |
| crit2-3 | MUST-FIX | hidden group ceiling: `RX_FOREACH` refuses `ncaps > 256` pairs; PCRE2 has none | ACCEPT, no ceiling: the glue drives `next_n` with a VLA sized from `rx->ncaps`, k = 1 above `PCREC_SUBST_PAIRS`; the stack bound is stated, and the custom glue covers huge counts | §R3.4 |
| crit2-4 | MUST-FIX | R2.8's measurement: twin = the shipped D163 composite, A/A floor, the listed cells, `pcre2_substitute` external | ACCEPT: arms SEP / SEP-PLT / K1 / COMP plus A/A repeats; cells `a`→`b` dense, `(\w+)`→`<$1>`, `$1` at ncaps≈30, `${w}` dense, `limit = 4`; PCRE2 an external row; gate `SEP/COMP <= 1 + floor` on the dense cells | §R3.13 |
| crit2-5 | NOTE | `ctx.ncap = ncaps` vs §2¶6; `ctx.user = NULL` leaves segments unbindable; "no resume after limit" unstated | ACCEPT: the element is `ncap`'s first producer (the completion reading) with a §2¶6 hunk; the binding carries `seg_user[]`; no resume after a `limit` stop, stated | §R3.1, §R3.3, §R3.4 |
| crit2-6 | SIBLING | `rx_subst_ref` duplicates `rx_group_entry`; a third version number; `.h` vs `.c` stamps; three function types over `rx_ctx` | ACCEPT: the needed shape IS an `rx_group_entry` array (`slot = -1`, `ref` for `${site.group}`), and bind is a generic shape match; no new number (the shared abi; an own number is an [IFACE-PUSH] candidate); stamps: storage/assert constants (`<S>_NREFS`, `<S>_NSEGS`, `<S>_MAXNUM`) in the `.h`, the rest `.c`-only, per match_api §6.3.1¶1; `rx_matchfn`/`rx_renderfn`/`rx_substfn` recorded as one family | §R3.2, §R3.8, §R3.12; candidate C3 |
| crit2-7 | UNLOCK | the general form is a PER-MATCH CONSUMER; build only the shared shape type and the generic bind | ACCEPT as design text: render built (phase B); extract-to-struct (trigger: a structured-extraction ask) and a pcre2-ovector adapter (trigger: the bench wants templated output from both engines) named, not built; split/count/callbacks are glue | §R3.12 |
| crit3-1 | BLOCKER | NOSPACE and a render failure both −1; `*outlen` unset on failure paths | ACCEPT: six distinct codes below `PCREC_ERR_ITER` (values PROPOSED, fixed at landing) plus the existing `PCREC_ERR_UNSET_VAR`; `*outlen` on every path | §R3.5 |
| crit3-2 | BLOCKER | `slot[]` not tied to the rx it was bound against; OOB with another rx | ACCEPT: the binding records `rx`, `ncaps` and a tag; the glue checks once per call, and the element checks `ctx->ncap == b->ncaps` once per call. A different rx with equal `ncaps` through a custom glue is UNDEFINED, stated beside §3.8¶8 | §R3.3 |
| crit3-3 | BLOCKER | unguarded length arithmetic (wrap, 32-bit, the ptrdiff_t cast colliding with codes) | ACCEPT: lengths saturate in one helper (`rx_subst_put`); overflow → NOSPACE with `*outlen = SIZE_MAX`; a length never travels in a signed return, so "render overflow" has no separate case | §R3.1, §R3.4 |
| crit3-4 | MUST-FIX | zero-length slot array when there are no named refs | ACCEPT: `<S>_NREFS = max(1, n)` | §R3.3 |
| crit3-5 | MUST-FIX | bind's single refusal code; no dlopen version check | ACCEPT: `MISMATCH` vs `MISSING_REF` with `*bad_ref`; a run-time abi compare covers dlopen | §R3.3, §R3.5 |
| crit3-6 | MUST-FIX | `${!var}` unchecked at bind | ACCEPT (specified): variables are bound to the iterator, so bind cannot see them; the glue resolves each `${!name}` once per call by name into an index-ordered view; unset follows the axis (`error` → the existing `PCREC_ERR_UNSET_VAR`) | §R3.7 |
| crit3-7 | MUST-FIX | `out` after NOSPACE; `out` overlapping `s` | ACCEPT: `out` unspecified after any failure; `restrict`, and overlap is UNDEFINED in one spec sentence | §R3.9 |
| crit3-8 | MUST-FIX | a custom glue needs a positional `rx_ctx` init; the glue reads `rx_iter` fields §3.8¶9 leaves unspecified | ACCEPT: `rx_subst_ctx_init` (subst block); a §3.8¶9 hunk naming `s`/`n`/`vars`/`nvars` and when each holds its bound value | §R3.9 |
| crit3-9 | NOTE | thread safety unstated | ACCEPT: the binding is read-only after bind and shareable; per-call state is automatic | §R3.9 |
| crit3-10 | NOTE | the PCRE2 differences; the grow-retry recipe | ACCEPT: an 11-row table and the recipe | §R3.10 |
| crit3-11 | NOTE | CLI `--subst-file`; `-o` emits the `.h`; header include order | ACCEPT | §R3.11 |
| crit3-12 | NOTE | in-place is honest only if no API ships, and the overlap rule must be explicit | ACCEPT: in-place stays contract-only (§R2.6); the overlap rule is stated | §R3.9 |

**The lane's own finding (F-R3-1).** §R2.4's glue initialized `rx_ctx` from `it->vars`
before the first call. On a FRESH iterator with no `rx_iter_vars` call that field may
hold any value (match_api §3.8¶5). The §R3.9 helper reads it only when the iterator is
BOUND or ENDED, or when it is FRESH with `PCREC_ITER_OPT_VARS` set. The R2 probe did
not see this, because it initialized `vars` to NULL.

## The two probe facts (the manager's)

The probes were run on the dev box: `lane/subst` head, abi 84, libpcre2 10.46. Sources
and transcripts are in the session scratchpad, per the brief.

1. **The I2 iterator TERMINATES on both crit1-1 patterns, short and long.**
   - `<p>_next` was capped at `4n + 16` iterations, then `RX_FOREACH` ran under the same
     cap. Both ended with `rc 0` on every subject.
   - Short subjects: `"xb"` gives `[2,1)`, `"bxbx"` gives `[1,1) [3,2)`, `"xy"` gives
     `[0,1) [0,2)`, and `"xyxyyx"` gives 5 matches.
   - Long subjects: six units repeated 1,000 and 100,000 times (up to 400,000 bytes).
   - The match count was at most `n` in every run, and no cap was hit.
   - One count shows the shape at scale: `k2` over `'xxyy'x100000` gives 300,000
     matches, of which 100,000 start before the previous match's end.
   - Nothing is fixed in `lane/i2build`.
2. **On an ill-formed UTF-8 subject the iterator is consistent with match_api §9 as
   written and with `_search` in a loop.** It is not an I1/I2 defect candidate.
   - The iterator, the §3.1.3 loop and a per-position `_search` agree on 15 of 15
     cells. Those cells are `x*`, `''` and `a|x*` over `"a\xffb"`, `"a\xe3b"`,
     `"a\x80b"`, `"\xff"` and `"a\xe3\x81b"`.
   - libpcre2's single searches (UTF|MATCH_INVALID_UTF) agree with pcrec at every
     offset.
   - libpcre2's GLOBAL iteration differs on 6 of the 15 cells. Its
     NOTEMPTY_ATSTART|ANCHORED retry at offset 0 of `"a\xffb"` returns `(2,2)`, which is
     not at the anchor. This is the class match_api §9.3¶3 already states for the
     anchored entries.
   - Pinned in the corpus as stated behaviour: `x*` → `[$0]` on `"a\xffb"` gives
     `[]a[]\xff[]b[]`, 4 substitutions.

## Candidates for the manager to number (no D/K ids taken)

- **C1 (spec).** match_api §3.8¶2 says "the matches are PCRE2's global iteration's" with
  no ill-formed-subject exception. It needs one sentence citing §9.3¶3's
  anchored-retry class (probe 2). Its home is the iterator's spec owner, or phase B's
  hunk.
- **C2 ([DD-3]/[RXINFO-REMODEL]).** A shape-contract version, so that a subst survives
  an rx scaffolding change: render on primitives, and a bind keyed to that version. The
  trigger is a caller who needs subst and rx artifacts from different builds.
- **C3 ([IFACE-PUSH]).** A subst-block version number of its own, so that a subst-block
  change is not an rx abi event.
- **C4 (adoption).** `rx_group_run` moves into the rx shared block at the next rx abi
  event. match_api §5.4¶6 then points at it.
- **C5 (decision record).** D173's design revision R3: the batch element, run binding,
  span check, same-build rule and codes.
- **Sabotage rows for phase B, PROPOSED from the S1346-S1385 reserve.** Witnesses and
  reach counts are owed at build.

  | id | sabotage | witness |
  |---|---|---|
  | S1346 | the `start < previous end` check is removed | `x\|(?<=(?1))y\|(\Kx)` on "xy" |
  | S1347 | the `end < start` check is removed | `x(?=(?1))\|(b\K)` on "xb" |
  | S1348 | the run walk takes the run's first row, not the first that participated | `(?J)(?<n>a)\|(?<n>b)` on "xaby" |
  | S1349 | the batch is not capped at the remaining `limit` | the `limit = 4` fetch count |
  | S1350 | `rx_subst_put`'s saturation is removed | a unit cell at `w` near `SIZE_MAX` |
  | S1351 | the element's `ncap == b->ncaps` check is removed | a binding against one rx with another rx's caps |
  | S1352 | `rx_subst_ctx_init` reads `it->vars` without the FRESH/OPT_VARS test | a `0xA5` dirty-init arm with `${!v}` |
  | S1353 | the NOSPACE capacity is off by one | `cap` = required − 1 and = required |
  | S1354 | `--unset=error` renders empty | `(a)\|(b)` → `[$1\|$2]` |
  | S1355 | the tail copy is dropped | `a` → `b` on "xa y" |

## Frank's questions (OPEN, for him)

Q-F1 (bind at run time), Q-F2 (the fused form), Q-F3 (count vs first/global) and Q-F4
(the in-place contract) stay open. They are restated in plain words with updated
leanings in note §R3.16. Q-M1..Q-M5 are closed by §R3.

---

## The critics' text, verbatim

### crit1

```
# substcrit1 (opus, semantics vs PCRE2) — 2026-10-22; probes in the session scratchpad substcrit1/p2.c p3.c (glue verbatim from R2.4)
BLOCKER (1): R2.5 rule 1 ("spans ordered, non-overlapping by construction, \K in lookaround refused") is false: \K reached through a SUBROUTINE CALL from a lookaround runs. `x(?=(?1))|(b\K)` on "xb": iterator reports [2,1); pcre2_substitute -60 BADSUBSPATTERN; glue need wraps, memcpy SIZE_MAX, stack smash. `x|(?<=(?1))y|(\Kx)` on "xy": [0,1) then [0,2); gap wraps; SEGV. Fix: glue checks each span (st < prev || end < st) -> PCREC_SUBST_BADSPAN; PCRE2's test is start < search start (stricter in empty-retry corner): say so or carry search start out of the iterator. Do NOT add "ordered, non-overlapping" to §3.8 (iterator legitimately reports these, as pcre2_match). Alt: rx_info publishes a compile-time "may report backward spans" fact, glue checks only then. Corpus both cells.
MUST-FIX (2): binding cannot hold a duplicate-name RUN (int slot per named ref; run members non-contiguous; render compiled without the rx). `(?J)(?<n>a)|(?<n>b)`, `[${n}]`, "xaby": pcre2 "x[a][b]y", single-int bind "x[a][]y". Fix: (first,count) range into a slot list, render walks per §5.4¶6. First-participated rule agrees with pcre2. SIBLING: name->run resolution x3 (emitted \k<name>, §5.4¶6 prose, subst bind) -> one header helper rx_group_run.
NOTES: (3) R2.3's NOSPACE row not oracle-compared: pcre2 -48 required=12 (counts NUL), pcrec 11 deliberate (Q4): label + spec the +1. (4) unset->empty matches pcre2 only under UNSET_EMPTY; pcre2 default -55; Q3 axis should list `error`. (5) invalid UTF-8 (`x*` -e utf8 on "a\xffb"): pcre2 -23 (UTF), MATCH_INVALID_UTF 3 matches none at 1; pcrec ITERATOR gives 4 (0,1,2,3) — inherited, corpus should pin. (6) *outlen unwritten on iterator-rc and render-failure returns; pcre2 sets PCRE2_UNSET.
OK: valid UTF-8 stepping byte-identical; limit=1 on a*/"bab" "[]bab"; rx_iter_at prefix copy = startoffset; lexical \K in lookaround refused; CRLF moot.
```

### crit2

```
# substcrit2 (opus, modularity/cost/arch + unlocks) — 2026-10-22
No blockers. MUST-FIX: (1) per-match out-of-TU render call is NOT D171's class (D171 = fixed per-find-all cost; I2 note: next_n k=64 0.58x of loop on prose, "gain comes from removing calls") -> batch-shaped element render_n(slot,s,n,caps_batch,k,&prev,out,cap), per-match render = k=1 case; probably settles Q-F2 (fused form) by structure. (2) abi coupling unstated: subst header embeds rx block with #error guard; any rx abi event (scaffolding, even comments, D76/D94) orphans every subst artifact; M:N only within one pcrec build -> say "same pcrec build" plainly OR render on primitives (subject, caps, vars) and bind keyed to a shape-contract version; that is [DD-3]/[RXINFO-REMODEL]'s question, file there. (3) hidden group ceiling: RX_FOREACH refuses ncaps > RX_FOREACH_PAIRS (256) with PCREC_ERR_ITER; PCRE2 has none -> buffer from rx->ncaps, fallback k=1, or refuse at BIND with named reason. (4) R2.8 measurement: twin = shipped D163 composite, A/A floor (D165), cells: a->b dense, $1 at ncaps~30, named-ref dense, limit=4 (doubling fetches 7), PLT vs static, pcre2_substitute external row.
NOTES (5): glue sets ctx.ncap=ncaps vs §2¶6 (every call site sets 0); ctx.user=NULL leaves rx_renderfn segments unbindable (needs segment-user arg); limit + "iterator finished on loop exit" = no resume, say so.
SIBLING (6): rx_subst_ref {name,number} duplicates rx_group_entry -> NEEDED shape as rx_group_entry array (slot=-1), bind = generic shape-match; 3rd info struct + 3rd version number (rx_info.abi, MF_SITE_ABI, subst) -> route Q-M3 to [IFACE-PUSH]; <S>_NREFS/_MAXNUM in .h vs rx stamps .c-only (§6.3.1) pick family rule; rx_substfn = 3rd fn type over rx_ctx (matchfn, renderfn) record family.
UNLOCKS (7): general form = PER-MATCH CONSUMER (spec over declared needed shape, bound once to offered shape, driven per batch). render = this; extract-to-struct (typed fields) trigger = structured-extraction user ask; split/count/callbacks = glue only, not elements. Build now only shared shape type + generic bind. Render on primitives works over any caps producer (composite parts, pcre2 ovector adapter) trigger = bench wants templated output from both engines. Batch render makes R2.6 sink/streaming a thin loop.
```

### crit3

```
# substcrit3 (sonnet, embedder lens) — 2026-10-22
BLOCKERS: (1) NOSPACE vs render failure both -1 (Q-M4); *outlen unset on render/iterator failure paths -> distinct codes below PCREC_ERR_FLOOR, outlen defined on every path. (2) slot[] not tied to the rx it was bound against; c[slot[i]] unchecked -> OOB when a slot bound to rxA is used with rxB (smaller ncaps): slot header (ncaps + identity/abi) checked cheaply, or prominent UB + debug assert. (3) length arithmetic unguarded (w += gap/r, w+gap>cap wrap; n+1 expansions on 32-bit; need cast to ptrdiff_t negative collides with error codes) -> saturate, NOSPACE with outlen=SIZE_MAX, render overflow error.
MUST-FIX: (4) zero-length slot array when no named refs -> NREFS max(1,n). (5) bind's single refusal code -> distinct ABI/MISSING_REF + which ref; state dlopen version check. (6) ${!var} variables unchecked at bind. (7) out contents after NOSPACE unspecified; out must not overlap s (restrict, UB sentence). (8) custom glue needs positional rx_ctx init (freezes layout) -> inline ctx_init helper; glue reads it->s/n/vars which §3.8¶9 leaves unspecified -> spec hunk first.
NOTES: (9) state thread-safety (slot read-only after bind, shareable). (10) PCRE2 differences: no NUL, unsigned char*, no extended flags, count lost on failure, NOSPACE retry = second pass; limit==0; document grow-retry recipe. (11) CLI: add --subst-file; -o emits .h; header include order. (12) in-place honest if no API ships + overlap rule explicit.
```

