# Verifier, critic round inline-c

### V1
HOLDS. Re-ran probes/verify/p (copy of probes/prem/p.c; flags 0x14000 = NO_AUTO_POSSESS|NO_START_OPTIMIZE), callout vetoes iff start_match==0:
`(?s).*(?C1)x  axbx  opt=0x14000 rc=-1` ; with NO_DOTSTAR_ANCHOR (0x1c000) `rc=1 [1,4)`. (Plain `.*(?C1)x` without (?s) matches [1,4) either way, so the (?s) form is the one that shows it.)
Means: the note's two reference flags do not give unoptimized backtracking order for leading dot-star.

### V2
HOLDS. `(?:(?C1)(a))+` on `aa`, flags 0x14000: fires `pos=0 top=1`; `pos=1 start=0 top=2: g1=(0,1)`; `pos=2 top=2: g1=(1,2)`. Second fire shows capture_top=2, g1=[0,1).
Means: PCRE2 shows a group at a looped site (after one iteration) that a textual ncap would hide.

### V25
HOLDS. build/pcrec -p rx --pattern '(?C256)' and '(?Cx)' and '(?C)' each: `pcrec: (?C...) requires module 'callouts' (pattern offset 0)`. (PCRE2 itself: 138 "greater than 255" / 182 "unrecognized string delimiter", so pcrec's wording differs, a D26-tier matter.) With --features all: `module 'callouts' is enabled but (?C...) is not implemented yet`.
Means: SIM-7 premise holds.

### V3
HOLDS (facts as cited). src/gen/emit_vm.c:3687-3689: `bool pcrec_vm_prefilter_window(Ctx *cx) { return cx->job->fit.prefilter && !cx->job->nfa.erased; }`; src/ir/nfa.c:723 `case A_LOOK: b->nfa->erased |= NFA_ERASED_LOOK;`; src/gen/emit_dfa.c:9758 `cand_rs_exact_applies ... return s->vm->mrl_win;` (R1 hybrid retry, exact). Emitted hybrid for `(a(b)c)+d` (probes/verify/h.c): `RX_VM_RESEED "exact"`, `RX_VM_PRUNE_CEILING "prefilter-window"`, and L385/392 `window_end = (size_t)window[0][1] < subject_length ? ... ; result = rx_match_anchored(&ctx, run, window_end);` i.e. the anchored VM is clamped to the prefilter window's end.
Means: a window clamp exists exactly when nothing is erased; a callout/consume tail that makes the scan end wrong is a real interaction with this clamp.

### V4
HOLDS. src/parse/enabled.c:262-268: `if (!strcmp(spec, "all")) { for each kind k: rows = pcrec_registry(kinds[k], &n); for i: mask |= rows[i].feature; } label = "all";` (union of every registry row's feature). `build/pcrec --features all -p rx --pattern '(?C)'` -> `pcrec: module 'callouts' is enabled but (?C...) is not implemented yet` (so `all` does include the callouts module). A `.rxt` block with `features all` is in use (tests/startset/giveup.rxt:17 `features all`, many more files; rxt_format.md §1.5¶5 documents `features <list>`).
Means: once a `(?C` registry row exists, `all` enables it with no further edit, so "all" population / unit tests pick it up automatically.

### V5
HOLDS. `build/pcrec -p rx --features all --engine=vm --pattern 'a(c)\Kb'` (probes/verify/k.c): L45 `#define RX_SLOT_WHOLE_START 0`; L191 `RX_SET(RX_SLOT_WHOLE_START, (ptrdiff_t)scan_position);` at the \K site; L214-217 `/* \K: the reported start is where the winning path last crossed a \K (slot 0, trailed) ... */ capture_spans[0][0] = run->slot_values[0] != PCREC_UNSET ? run->slot_values[0] ...`.
Means: slot 0 doubles as the \K start in the report, so a callout view that reads slot 0 as "match start" would see \K's position.

### V6
HOLDS. rxt_format.md §1.6¶7 "`sha256 <hex64>` pins the file's contents, exactly 64 hex digits, case-insensitively compared"; ¶8 "**`pcrec` checks neither the hash nor the 64-digit syntax**: `--list-source` performs no file I/O ...; `run.sh` additionally refuses ... when no sha256 tool is available". analyze/sha256.c and sha256.h exist (ls analyze/). Under src/ lib/ cli/ `sha256` appears only as a parsed field name (rxt_source.c:2134-2139, internal.h:6381 `*sha256` string field) and the 64-bit `pcrec_find_rows_digest`; no SHA-256 function.
Means: a pcrec-side content hash for inline-C text would be a new hasher (or a link to analyze/'s), not a reuse.

### V7
HOLDS. `build/pcrec -p rx --no-captures --pattern '(a)(b)'` emits `#define RX_NCAPS 1` (probes/verify/nc.h:268); same pattern without the flag emits `RX_NCAPS 3` (pl.h:268). mod_backrefs.c:835-838: `if (!cx->want_caps && cx->ncap > 0) { ... pcrec_bref_mark(root, keep, nkeep); root = br_strip_caps(root, keep, nkeep); }` -- the keep set under --no-captures IS pcrec_bref_mark's marked set (src/opt/atomic.c:653, marks A_BREF/A_VAR refs).
Means: --no-captures keeps only groups something reads; a callout reading a group is not in that set unless added to pcrec_bref_mark.

### V8
PARTLY. Count holds: `grep -rn "case A_BREF" src` = 65 lines in 24 files (emit_vm.c 10, atomic.c 11, possessify.c 7, revdet.c 5, mrl.c 4, ...; a few may be comment text); possessify.c:471 `static bool bref_first(Fq *q, const Ast *a, First *out)` is the Arm-B reader of a->u.bref.refs[]. Refuted part: "no shared predicate" is too strong -- `pcrec_has_bref` (atomic.c:570) exists and feeds `PF_KIND_BREF` (facts/kinds.c:34, facts.h:275), which select_engine.c reads (`has_bref`), and `pcrec_bref_mark` (atomic.c:653) is a shared marked-set predicate. What is true: those are whole-tree "is there a bref" facts; the ~65 per-node arms each decide their own handling, with no single "this node reads capture state" predicate.
Means: a new capture-reading node (callout) needs the kinds bit + bref_mark + per-arm decisions; the shared facts help but do not cover the per-arm sites.

### V9
PARTLY. (a) REFUSED-on-both-sides => AGREE: REFUTED as stated. dump_diff.awk END: `if (a_trc == "REFUSED") { refused++; emit_row("REFUSED", ...); continue }` runs BEFORE `if (b_trc == a_trc && b_out == a_out) { agree++ }`, so any axis-side REFUSED lands in the REFUSED bucket, and run_axes.sh:1387-1431 promotes a REFUSED text not matching the axis's REFUSAL_PATTERN to `AXIS FAIL ... UNDOCUMENTED refusal` (red, not green). So a corpus-wide REFUSED callouts section would turn test-axes RED, not vacuously green. (b) What does hold: a case that fails to LINK produces NO dump line on either side (run.sh header L125-128 "A case whose block fails to LINK ... still produces NO line"); dump_diff only reports LOST for keys in base_seen, so absent-on-both-sides is silent: that path is vacuous. (c) HOLDS: `ext <consumer>` is parsed at run.sh:3330-3345 only to open an OPEN SUBTREE ("nothing is dispatched by any leg"; L2619 "an `ext` body is interpreted by nobody at all").
Means: PREM-9's consequence ("green") is wrong for the compile-refusal path and right only for the link-failure/absent-key path.

### V10
HOLDS. emit_dfa.c ~8600: `(g) NO VERB AND NO CALLOUT: ... STRUCTURALLY ABSENT today -- the AST has no node kind for either (`(*COMMIT)` and `(?C)` are refused before a tree exists) ... the kind that adds one must add a `PF_KIND_*` bit (src/facts/kinds.c's exhaustive switch is its alarm) and decline here. Sabotage row S475 ships UNREACHED.` ~7841: `NO VERB AND NO CALLOUT: a (*COMMIT) in a skipped attempt could end the whole search. STRUCTURALLY ABSENT today ... the kind that adds one must decline here. Sabotage S496 ships UNREACHED.` tests/mech/sabotages/S475_*.sh and S496_*.sh both `SAB_EXPECT=UNREACHED` ("no figure is owed until a verb or callout compiles"). tests/codegen/run_ir_listing.sh:493,520: "module 'callouts' has no producer, so both must be 0" (listing callout-sites vs artifact must both be 0).
Means: the tree holds registered decline obligations and a zero-callout assertion that a callout build must flip.

### V11
HOLDS. rxt_format.md §4¶8: "A **cell** is what the closure produces: one (block, cases) unit per `pattern` block anywhere in the closure, entry or fragment, run as part of the entry's own turn". run.sh:1894 `"$PCREC" -p rx "${pflags[@]}" -o "$bdir/gen.c" --pattern "$cur_pattern"` (and the batch path L1644 the same with `-p "$px"`): each block, fragment blocks included, is compiled as a separate `pcrec ... --pattern <block>` invocation.
Means: a library-definition block in an include fragment is itself compiled as a target by the harness, so it must compile standalone.

### V12
HOLDS. src/gen/emit_compound.c:60-69 `callsite_rows[]` = span (`r > 0`, CS_SUCCESS), nomatch (`r == 0`, CS_NOMATCH), give-up (`r >= PCREC_ERR_FLOOR && r <= -2`), internal, utf, startpos (CS_TRAP), unset-var, `{ "reserved", CS_TRAP, cs_always, "r < 0" }`; header comment L25 "shared by parts and (when they build) callouts"; callsite_emit L98-101: "the `nomatch` edge `fail` as the straight-line continuation (only `r == 0` reaches it ...)". match_api.md §4¶10 table has the same 8 rows (1 match, 2 no match `0`/`-1`, 3 give-up, 4 INTERNAL, 5 UTF, 6 STARTPOS trap, 7 UNSET_VAR, 8 "any other code below 0" trap) and says "when module `callouts` builds, a callout site". Note the C table's nomatch test is `r == 0` (search-entry convention), the spec row says `0` / `-1` (rx_matchfn).
Means: the table exists and already names callout sites as a consumer; a callout site must use it or amend §4¶10.

### V13
HOLDS (quotes). locate_finish.md:378 "After L0 "verify a candidate" has ONE home."; §1.3 FIN3 row (L353): "`CR_VM`: `SPAN`, `AT` (**never `ENDSET`**, LR-S3) | ... | one anchored VM attempt at `s`, ceiling `e` (a `SPAN`) or `n` (an `AT`)"; FIN4 (L354) "the attempt loop from `s`; ... RETRY on failure". compound.md §A.2 L304-309: "an external callee of type `verify-at` (a pcrec-compiled or caller-bound matcher with the `rx_matchfn` shape) type-checks as the finisher of `locate-then-finish(Q; external verifier)`, because a callout and a part are one thing at two binding times (alignment §4, unlock U6). No client uses it yet"; combinator table L297 `locate-then-finish(L; V)` "(the hybrid's shape, across parts)". compound_callout_alignment.md:609-611 "U6. The compound type check admits external callees (§4): a combinator over a part and a callout-bound artifact (e.g. `locate-then-finish(Q; external verifier)`). Trigger: a client whose finisher is not pcrec-compiled."
Caveat: the critics' conclusion (scan-end duplicates FIN3/FIN4) is an argument, not checked here; the quoted facts are accurate. U6 is stated as a trigger-gated unlock, not a ruling that callouts must use it.
Means: the precedent text exists as cited.

### V14
HOLDS. Emitted shared block (probes/verify/pl.h:44, every artifact): ` * generated call site that invokes an rx_matchfn traps on one.` (re `PCREC_ERR_INTERNAL`). match_api.md §4¶10 row 4: "`PCREC_ERR_INTERNAL` | propagate unchanged". decisions.md D163 addendum 6 Q3 (L9628): "`PCREC_ERR_INTERNAL` from a callee PROPAGATES instead of trapping." So the emitted comment is stale against a ruling. (Whether fixing it is an abi event with every-artifact movers follows from "comment in the emitted shared block" per the root CLAUDE.md abi row; not run here.)
Means: two homes disagree today; the ruling is on the table's side.

### V15
PARTLY. decisions.md D163 addendum 6 Q1 (L9626): "one budget meter per EXPORTED call -- every compound part and every pcrec-matcher callee charges the caller's meter; decided before B6." The note has no sentence adopting or deferring it: `grep -n -i budget` finds only L621 (§4.4 item 6, about scan-end answering where the VM gives up), nothing on a callee's budget; L825 `- rx_ctx: unchanged (slot 0 carries the attempt start, 1.3).` Minor correction to SLOT-15: "budget" does not appear in §1.6 row 3 (that row says "give-up", L240); L880 mentions a binding returning PCREC_ERR_STEPS in the stage-1 test list only. Whether the ruling's carrier needs an rx_ctx member is the critic's reading of the alignment note, not checked.
Means: the ruling is not reflected in the note; the omission fact holds.

### V16
HOLDS (wording). match_api.md §10.9¶1: tier re-runs "on `PCREC_ERR_FRAMES` and on no other outcome"; ¶6: "`PCREC_ERR_FRAMES` from an un-suffixed entry means the STAMPED DEFAULT ran out, never the fast tier."; §4¶4: "A returned `PCREC_ERR_STEPS` still means one attempt exhausted a full budget."; §4¶3: FRAMES "names a RESOURCE, not an array and not an owner" but "From an un-suffixed entry it always means the stamped default ran out, never the fast tier". The collision (a propagated callee FRAMES hitting the outer tier trigger) is an inference from these texts; the texts are as quoted.
Means: §4¶3 declines to name an owner in general but ¶3 last sentence/¶6 do name one for un-suffixed entries.

### V17
HOLDS (facts). src/core/internal.h:4547-4549: "Ports are DATA about production; they carry no diagnostic and no module fact (those stay on the row -- R11/M5's rule that a handler must not be a second home for tier-2 facts)." src/parse/registry.c:1026: exactly ONE row `GROUP_XA_CALLOUT('C', "(?C1)", callouts, VM_ONLY, "callout to user code: ... PLANNED (D36) ...", QF_NO)`; `--list-syntax` shows one `group C (?C1) callouts ... planned` row. Consequence (that a tagged-string owner `code-c` would need a port-carried module fact) is the critic's inference.
Means: the registry has one module per `(?C` row and ports may not carry module facts, as stated.

### V18
HOLDS (wording). rxt_format.md §1.12¶9 "The day something in an `ext` block needs pcrec to ACT on it, it must GRADUATE to a real production. Aux never grows semantics in place."; ¶10 "'Act on' means any of: a build reads it, a check reads it, a diagnostic cites its VALUE ... or any pcrec surface other than the faithful dump reports it."; ¶14 "Nothing in pcrec -- no test, no dump summary or count, no refusal, no diagnostic, no selection -- may take a value that CHANGES when an aux body changes, except the faithful per-line rows reporting that body itself." inline_c §3.6 (L537-548): "The harness is the consumer; pcrec only carries the block." Whether the harness counts as "pcrec" for ¶14 is the open reading; the rule's own list includes "a build reads it, a check reads it" and "no test".
Means: the text of the rule is as cited and plausibly covers a harness that builds/links from an aux body.

### V19
HOLDS. match_api.md:1783-1789: "every byte of the artifact, `.c` and `.h`, is ASCII under every option, and it compiles clean under `-Wall -Wextra -Werror -Wbidi-chars` for any pattern" (echoed caller text is spelled `\xNN` / `\NNN`). Re-ran `build/pcrec --list-source probes/CON/bidi.rxt` on a pattern containing U+202E and U+00E9: row `pattern	1			a<E2 80 AE>b<C3 A9>` (shown by cat -v as `aM-bM-^@M-.bM-CM-)`), i.e. non-ASCII bytes pass through RAW. Whether inline_c's verbatim segment emission (§3.1) breaks the artifact promise and whether `--list-callouts` would behave like --list-source is inference; the promise text and the raw pass-through are as stated.
Means: the existing promise is stated for "any pattern", and the only comparable listing prints non-ASCII raw.

### V20
HOLDS (probes as stated). Re-ran probes/CON/inc into probes/verify/inc: `m2.rxt` (`lib "lib.rxt"`, target pattern `x(?&ld)y`) builds m2.c/m2.h; `m3.rxt` (`lib "lib.rxt"`, `target rx = ld`) -> `pcrec: [value-shape] .../m3.rxt:2: 'target rx' -> no definition 'ld'; searched the source's own directory (no --lib-path)`; `main.rxt` (`include "frag.rxt"`, `target rx = fr`) -> `... no definition 'fr'; searched the source's own directory`. Caveat: this covers a plain-pattern lib/fragment; the harness path (run.sh compiles each block incl. fragment blocks via --pattern, V11) is a different route, which is what CON-2/CON-3 argue about.
Means: through the CLI a lib's or fragment's blocks are not targets; they reach an artifact only via a call.

### V21
HOLDS (quote). decisions.md:1587 D26 addendum last sentence: "A difference is a PCRE2 bug only with evidence against the standard's own data or text; a PCRE2 choice the standard leaves open is not a bug and pcrec follows PCRE2." inline_c L270-273 invokes the addendum for the wording only ("compatible with PCRE2 run without its auto-possessification and start optimizations") and flags it as a semantics choice, section 10 Q1. Whether that framing omits the counter-force is the critic's reading; the sentence is as quoted.
Means: the addendum's operative sentence does lean toward "follow PCRE2" for choices the standard leaves open.

### V22
HOLDS. pcre2callout(3) (/usr/share/man/man3/pcre2callout.3.gz): "The start_match field normally contains the offset within the subject at which the current match attempt started. However, if the escape sequence \K has been encountered, this value is changed to reflect the modified starting point." Re-ran probes/verify/pc (copy of simulate/pc.c, libpcre2 10.46): `ref 'a\K(?C0)b' 'xab'` -> `fire pos=2 start=1` (attempt start 1, \K at 2); `ref '(a\K)(?C0)' 'a'` -> `pos=1 start=0`; `def 'ab\K(?C0)c' 'abc'` -> `pos=2 start=0`; `ref '(?:a\K)+(?C0)b' 'xaab'` -> `pos=3 start=1`. start_match is never the \K-moved value, contrary to the manual.
Means: the note's "attempt start, NOT a \K-moved start" matches the binary and contradicts the manual; the note says neither.

### V23
PARTLY. lib/pcrec.h `PCREC_BIT(n)` is used for n = 0..54 and 56 (last: L1197 `#define PCREC_NO_REV_END_ONEWALK PCREC_BIT(56)`, whose comment L1196 says "Bit 55 is the kit's (`-fno-kit-size-drop`, R17-b)"); no other BIT(55) or BIT(57..63) definition in lib/pcrec.h. So bit 55 is RESERVED by the kit, not free: free = 57..63 = 7 bits, not 8 (SLOT-19's count is off by one). decisions.md:9900 files bit 57 as the [IFACE-PUSH] candidate `PCREC_NO_WINDOW_REPORT` (working name), leaving 6 unfiled. plan.md (line cited at freeze) [IFACE-PUSH] "HARD TRIGGER ... the push opens when <= 4 flag bits remain in the 64-bit `flags` word (55 of 64 used after [START-LANDING])". Two stage-4 bits (deny + force) would take free from 7 to 5, as SLOT-19 argues (the argument's arithmetic survives; its "8" does not).
Means: the trigger is nearer than SLOT-19 stated (7 not 8 free), strengthening rather than weakening the finding.

### V24
HOLDS (the row; the "after stage 1 it fails at LINK" part is a forecast, not checkable). pcrec-bench/reports/2026-10-26-syntax-0.1-ryzen7700x-rebaseline-6b2dbd3e.subject-grain.tsv has `did_not_compile	grp-callout	f-aaab	match-compliance	...	pcrec_6b2dbd3e_auto-caps-simdna	did-not-compile ... pcrec: module 'callouts' is enabled but (?C...) is not implemented yet (pattern offset 2)` (offset 2 fits `ca(?C1)t`; the literal `ca(?C1)t` occurs in pcrec-bench/store/records/syntax@0.1/... jsonl). libpcre2 rows for the same pattern are measured (jit 245,422.8 ns/call, interp 1,298,433.3 ns/call on large-subject-throughput, report .md L2406-2413). The "PCRE2 ignores callouts when no function is set" sentence in CON-13 was not re-checked here.
Means: the bench already carries a callout pattern that pcrec currently refuses, so the outcome class will change when callouts build.

## DONE
