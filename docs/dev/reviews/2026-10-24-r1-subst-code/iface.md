# IFACE lens — subst critic round (code), SUBJECT 1222b31be

Lens: contract-interface (subst_api.md §1,§3-§10; cli.md §1.19-§1.20; D174/D80) + GOALS (replace_design §R4).

### IFACE-1  §10¶10 promises replace-all "returns 0" where it returns the match count
- status: CONFIRMED (repro: d1.c probe: `rx_subst_replace_all` over `(a)|(b)` / `[$1|$2]` on "xaby" returns 2, as §10¶7 and §6¶8 say; §10¶10 says "For every input on which §6¶4's recipe returns 0, rx_subst_replace_all returns 0 with the same bytes")
- severity: doc
- effort: S ; blast radius: a reader of the equivalence promise (and any test written from it) compares the wrong return value
- where: docs/spec/subst_api.md §10¶10
- body: §10¶7 (count, `>= 0`) and §10¶10 (0) contradict inside one section. The fix is one clause: "returns a count >= 0 with the same bytes".

### IFACE-2  §8¶1's code table omits replace-all from BADSPAN/UNSET/UNSET_VAR (and ERR_ITER), and says "context helper"
- status: CONFIRMED (repro: d1.c `RA STRICT` -> -14 PCREC_SUBST_UNSET from rx_subst_replace_all; an ENDED iterator -> -10 PCREC_ERR_ITER; §10¶9 itself lists BADSPAN/UNSET/UNSET_VAR as returned "as it is")
- severity: doc
- effort: S ; blast radius: a caller writing a switch over replace-all's codes from §8's table
- where: docs/spec/subst_api.md §8¶1 table, "returned by" column; row UNSET_VAR says "element, context helper" (the function is the context SETUP, §7¶3)
- body: the table is the codes' index; it should list replace-all on BADSPAN, UNSET, UNSET_VAR, name the context setup by its name, and note ERR_ITER / the iterator's give-ups pass through replace-all (§10¶7, §10¶9).

### IFACE-3  §4¶11 omits the element's no-map MISMATCH (numbered ref >= ctx->ncap, or a named ref with map NULL)
- status: CONFIRMED (repro: d1.c: `num_render` (`[$1|$2]`) with a hand-filled ctx `ncap = 2`, map NULL -> -15 PCREC_SUBST_MISMATCH; emitted `<p>_subst_slot` returns -3 for `!map && (k < 0 || k >= nc)`)
- severity: doc
- effort: S ; blast radius: hand-filled-ctx callers (the §3¶12 path)
- where: docs/spec/subst_api.md §4¶11 vs src/gen/emit_subst.c (the emitted `_subst_slot`)
- body: §4¶11's list says the run-walk slot test "can only fire on a map the check never saw", and names no no-map case. The code (correctly, for memory safety) also refuses the no-map out-of-range number and the no-map named reference. Add "with no map, a numbered reference k >= ctx->ncap or a named reference" to the list.

### IFACE-4  replace-all reports two CAPACITY shortfalls as PCREC_SUBST_MISMATCH, where the element reports the same shortfall as NOSPACE with `need`
- status: CONFIRMED (repro: d1.c: `o.cap = NUM_PIECES - 1` -> rx_subst_replace_all returns -15 MISMATCH, `o.need` 0; the element on the same short `pc` returns -11 NOSPACE with `need` set (§4¶14). d4.c: pattern `(a){300}`-style, 301 caps, valid map-free check (ctx_init 0) -> replace-all -15 MISMATCH)
- severity: design (D174 lens: the code names the wrong behaviour)
- effort: S ; blast radius: any caller with a small piece array, and every pattern with more than 255 groups (no remedy short of recompiling the support unit's TU with a bigger RX_SUBST_BATCH_PAIRS)
- where: docs/spec/subst_api.md §10¶7 (`k == 0` is MISMATCH), §8¶1 MISMATCH meaning ("does not belong to the call"); src/gen/emit_subst.c's replace_all text (`if (k == 0) return PCREC_SUBST_MISMATCH;`)
- body: §8¶1 defines MISMATCH as "a record, rx, map, flag, option or context that does not belong to the call" and NOSPACE as "pc ... too small; need says what suffices". `o->cap < P` is exactly "pc too small" and the element (§4¶14) answers it NOSPACE + need = P; replace-all answers MISMATCH with no size, so a caller's generic "grow on NOSPACE" path never fires and the same short array gets two codes from the two entry points. The >RX_SUBST_BATCH_PAIRS case is also a capacity (the function's own stack batch), not a mismatch: the check and the setup accept the rx, the element accepts it, only replace-all refuses, and under a code that tells the caller its record or map is wrong. Options: NOSPACE with `o->need = P` for the cap case; for the pairs case either fall back to a k = 1 path through `o->pc` (the function already has one for scratch) or give it its own documented code. At minimum §8's table should list the two capacity meanings under MISMATCH.

### IFACE-5  The default prefix `rx` emits `rx_subst_info` (and `-p pcrec` emits `pcrec_subst_info`): artifact names inside the reserved families, one spelled exactly as its struct tag
- status: CONFIRMED (repro: `pcrec -o defp.c --subst '<$1>'` -> defp.h line 473 `extern const struct rx_subst_info rx_subst_info;`; links and runs (e7.c, `2 [z<a><>]`). `pcrec -p pcrec -o pc.c --subst a` -> rc 0, record `pcrec_subst_info`)
- severity: design
- effort: S ; blast radius: every caller who takes the default prefix (the spec's own `ip`/`dmy` examples avoid it), every reader of `&rx_subst_info` vs `struct rx_subst_info`
- where: docs/spec/subst_api.md §1¶2 ("none of it names a prefix. Those names start with rx_subst, rx_group, pcrec_subst or pcrec_support"); cli.md §1.6¶2 row 4 refuses only `rx_subst`/`pcrec_subst`/... "alone or followed by `_`"
- body: row 4's purpose is that an artifact's names never enter the block's families, but the record's suffix `_subst_info` puts the default prefix's record at `rx_subst_info`, a member of `rx_subst_*`, and spelled identically to the tag `struct rx_subst_info`. It compiles today only because tags and objects are separate C namespaces; a future block object or macro named `rx_subst_info` (e.g. an info getter) would collide with every default-prefix subst artifact, and `&rx_subst_info` reads as a type error to a C reader. Either refuse `rx`/`pcrec` as a subst prefix (and say so in row 4), or note the case in §1¶2 and keep the block from ever defining `rx_subst_info`/`pcrec_subst_info` as an ordinary identifier.

### IFACE-6  One function family, two prefixes with no stated rule: `pcrec_subst_check`/`pcrec_subst_map_names` beside `rx_subst_ctx_init`/`rx_subst_flatten`/`rx_subst_replace_all`/`rx_group_run`
- status: CONFIRMED (read: the types block and the support unit, dmy.h lines 351-462)
- severity: design (naming)
- effort: S now (pre-release, no caller yet), L after release
- where: docs/spec/subst_api.md §1¶2, §3¶8, §3¶13, §7¶3, §10¶1
- body: the check and the setup are both `static inline` in the same block and called in sequence, yet one is `pcrec_subst_*` and the other `rx_subst_*`; the two support helpers split the same way. No paragraph says what the prefix means (owner? lifetime? support-unit vs block? — it is neither: check is block/pcrec_, ctx_init is block/rx_; map_names is unit/pcrec_, flatten is unit/rx_). A caller cannot predict a spelling from the family, and every new member re-opens the choice. Pre-release this is a rename; after the first user it is an abi/API break. Pick one rule (e.g. everything a caller calls is `rx_subst_*`; `pcrec_support_id` stays as the unit's identity) and state it in §1¶2.

### IFACE-7  §10¶6a admits a BOUND iterator but does not say what happens to matches it already consumed
- status: CONFIRMED (repro: d4.c: "aXbYa" over `(a)|(b)`, one `ab_next` first, then setup + replace-all -> returns 2, output `aX[|b]Y[a|]`: the consumed first match is copied UNREPLACED as part of the first gap, and the count excludes it)
- severity: doc
- effort: S ; blast radius: a caller that peeks one match (e.g. "is there any?") and then calls replace-all expecting the whole find-all substituted
- where: docs/spec/subst_api.md §10¶6a/¶7 ("0 means no match: out holds the subject unchanged" is also false for a BOUND iterator that consumed matches and then finds none)
- body: the behaviour is coherent (gaps start at o->prev = 0, the same as rx_iter_at's prefix copy, matching pcre2's copy-before-start-offset), but §10¶7's "0 means no match / subject unchanged" and the count's meaning both silently assume a FRESH iterator. One sentence: "on a BOUND iterator, the matches it already returned are copied as subject bytes and not counted".

### IFACE-8  GOALS: §R4 states no ranked, checkable goals; its leading ruling list (R4.0) is amended by R9/R11/R13 without a marker, so the shipped interface cannot be traced to a priority order
- status: CONFIRMED (read: docs/design/replace_design.md lines 65-121 (§R4.0), 1000-1075 (§R4.16-§R4.17); grep for goal/rank/priority across §R4 finds none)
- severity: design
- effort: S (a 6-row ranked table at the top of §R4) ; blast radius: the next design round on subst (extract-to-struct, G2-names, G4 in-place) has no tiebreak to cite
- where: docs/design/replace_design.md §R4.0, §R4.16, §R4.17
- body: §R4 is organized as rulings applied in revisions (R4.0 items 1-5, R5-R13), not as goals. The goals it implies are checkable and the shipped code meets each one I could test: (1) template compiled independently of the regex, numbers joined by an optional map — held (d1: map NULL identity, hand map, by-name helper, NOGROUP, ABSENT); (2) no malloc — held (no allocator call in the support unit or any emitted element); (3) pieces, bytes written only for case forcing, into caller scratch, sized exactly first — held (d2/d5: sneed exact, nothing committed past a failing match); (4) a support unit only when needed — held (byte-mode case inline, `-o -` self-contained, utf8 case needs the unit); (5) `--emit-support` standalone and byte-stable — held. But nothing RANKS them, and the rulings that conflict are left unreconciled in the text a reader meets first: §R4.0 item 4 still says "NO fused 'substitute with this regex' one-call form. The user can write it", item 5 still says `{const char *ptr, size_t len}`, while the spec ships `rx_subst_replace_all` (R11) plus a one-call `sub_all` wrapper as a tested recipe (§6¶9, F0) and `const unsigned char *` (R9). The resolution is defensible (replace-all is generic over `rx_nextnfn`, not regex-specific), but the design never says which goal outranked ruling 4 or why. IFACE-4 is a symptom: "no allocation, fixed stack batch" was ranked above "replace-all works for every rx the check admits", silently. Proposal: a short ranked goal table at the head of §R4 (independence > no-alloc > answers = PCRE2 > one-call convenience > ...), with R4.0 items 4/5 marked "[amended by R9/R11/R13]".

### IFACE-9  Two numbered contracts in the tree: docs/design/subst_api_r4_draft.md survived the build, diverges from the spec, and names a symbol that no longer exists
- status: CONFIRMED (read: the draft's header says it "replaces docs/spec/subst_api.md at build time, when this comment goes"; the comment is still there; `diff` of the two (anchors stripped) is 275 lines; the draft's §10¶6/¶7 name `RX_FOREACH_PAIRS` (RX_FOREACH was dropped, D175; the shipped name is `RX_SUBST_BATCH_PAIRS`). replace_design.md §R4.16 also still says `RX_FOREACH_PAIRS` and "returns 0 with *len"; §R4.17 says the extended module "is refused at compile as today"; §R4.2's one-page interface lists check/setup as `static`, not `static inline`, and omits replace-all)
- severity: doc
- effort: S ; blast radius: any reader or later lane that follows the design's "draft §N¶K" cites (the design cites the draft, not the spec, throughout §R4)
- where: docs/design/subst_api_r4_draft.md (whole file), docs/design/replace_design.md §R4.2, §R4.16, §R4.17
- body: D80 makes docs/spec/ the contract; the design is background. But §R4 cites "draft §N¶K" everywhere, and the draft is a full numbered contract in the same form, so a reader has two contracts that disagree (IFACE-1's "returns 0" came from exactly this R4b text surviving into the spec). Retire the draft as its own header says (delete, or a one-line stub pointing at the spec) and mark §R4.16's superseded sentences.

## PROBED-AND-HELD
(scratch: /tmp/claude-1001/crit-subst/iface/, drivers d1-d5.c, e1-e7.c, so/m.c, lk/{lib,app}.c; compiler and support unit at SUBJECT)
- CLI §1.19/§1.20/§5¶1/§5¶3: 47 command lines. Every pattern option tried (-i, --no-captures, --engine, --emit-main, --trace, --tune, --memfn, --ucp, --analysis) refused rc 1; --pattern/--pattern-esc/file operand/queries (--list-*, --emit-ir, --count-groups, --explain)/--emit-support refused with --subst; two templates refused; --features other than exactly `subst-extended` refused (incl. a duplicate list and ''); --emit-support refuses -p/-e/--features/--pattern/--subst; missing -o refused; template refusal names the template offset; --subst-file byte-for-byte (NUL, newline, quote, backslash, trigraph `??/`, `*/` in the provenance comment all escaped; compiles).
- Reserved prefixes (cli §1.6¶2 rows 1, 4): rx_subst, rx_subst_a, pcrec_support, rx_group, pcrec_subst_x (pattern side too), a__b refused; rx_substa, pcrec_subst2, pcrec_supportX accepted as the rule says. Stamp-collision survey: no subst stamp suffix (NREFS/PIECES/MAXNUM/NVREFS/SUBST_MODULES) equals any of 80 rx stamp suffixes or a block macro, so cross-kind prefix collisions are impossible.
- Check (§3¶8-¶12): 15 cases: abi, ncaps 0, unknown flag, encoding both directions, composed rx without map, nslot/nrun short (bad_ref -1), slot past ncaps, run count 0, run past nslot, named ref without map (bad_ref 0), support id mismatch: all as specified.
- By-name helper (§3¶13-¶16): 8 cases incl. unknown opts, short nrun/nslot, MISSING_REF with bad_ref, MAP_ABSENT nabsent=2/bad_ref=first absent, abi.
- Element (§4): 22 cases: k*P count with/without GAPS, k=0 checks flags, room NOSPACE with exact need and n unchanged, end past len, unset whole span, start<prev only under GAPS, group end<start, prefix commit on BADSPAN (n, prev), STRICT UNSET (plain and inside chosen conditional text), NOGROUP under STRICT renders empty, vars NULL / nvars short MISMATCH, ERR_UNSET_VAR at setup and in the element, USES_SCRATCH with scratch NULL MISMATCH, scratch sneed exact, sneed stops before a BADSPAN / UNSET match (§4¶14).
- replace-all (§10¶6-¶9): exact cap, one-short (NOSPACE, *len total), size-only (NULL,0) returns the count, NULL with cap>0, no match / no match one-short, STRICT, GAPS flag refused, ENDED iterator ERR_ITER, ctx/iterator mismatch, map short, scratch per-match fallback (scap 1 -> NOSPACE with *len untouched, sneed), rx_iter_at, BOUND; utf8 case through the unit (ß, é).
- Coexistence (§1¶3, §1¶4): two subst prefixes + an rx + a subst sharing prefix `ab` in one TU compile and run; case-only prefix pair hits the #error; a foreign PCREC_RX_ABI_H hits the abi #error.
- Support unit (§10¶2-¶3a): `-o FILE`, stdout, `-o -` byte-identical; STATIC build of all artifacts in one TU gives identical answers to the IMPLEMENTATION build; a STATIC library TU plus an IMPLEMENTATION app TU link without a clash, each record checks against its own copy; abi-suffixed external names; content id equals the record's.

## NOT COVERED
- Answer identity of the template language against libpcre2 (other lenses); the case table's per-code-point correctness.
- A real abi skew (BASE emits the same abi 84; simulated with a hand-defined PCREC_RX_ABI_H only), and a real two-content-id program (simulated by flipping a record's support_id).
- The `INT_MAX` count clamp, SIZE_MAX overflow paths, composed rx from a real `.rxt` composition (simulated via an rx_info copy), and multi-threaded use (§7¶5).
- examples/subst/ and tests/subst/ recipes were not run (no make).

## DONE
