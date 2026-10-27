# CONTRACT — ic1b-code
critic: contract, model: opus; started 2026-10-26; status: COMPLETE

## CON-1 `(?C"name,")` (a trailing empty attribute) is accepted; spec refuses an empty attribute
- status: CONFIRMED
- severity: answer (refusal contract: accepts what §11.7¶2 refuses)
- effort: S ; blast radius: named callouts whose string ends in `,`; `--callout N:` / `.rxt callout N` with an empty list (see below)
- where: src/parse/mod_callouts.c:171-175 + 72-97 (`pcrec_callout_attrs`); spec match_api.md §11.7¶2, pattern_language.md §7.11¶1
- repro: `build/pcrec -p rx --features classes,modifiers,callouts -o x.c --pattern '(?C"a,")'` -> rc=0 (artifact emitted, binding rx_callout_a, no attributes).
  Siblings that ARE refused: `(?C"a,,consume")` -> "unknown callout attribute ''"; `--callout 1:consume,` -> "empty callout attribute after ','".
  Cause: the caller consumes the ident's `,` and calls `pcrec_callout_attrs(.., n - id - 1 = 0, ..)`; the "empty after sep" check lives inside the `while (i < n)` loop, which never runs for n == 0.
- related (spec-silent, same mechanism): `--callout 1:` (empty ATTRS) and a `.rxt` line `callout 1` with no attributes are accepted (cli/main.c:1063 comment says the list "may be empty"). cli.md §1.21 says "a malformed value [is] refused" and rxt_format §1.5¶13a writes `callout <n> <attrs>` with attrs required by its shape. Either the spec should say an empty list is a no-op declaration, or the code refuses it; today the code's own comment and the spec disagree.
- argument: §11.7¶2 "An unknown, repeated or empty attribute is refused." One grammar home (`pcrec_callout_attrs`) answers differently for the same empty item depending on whether the comma was eaten by its caller.

## CON-2 A non-atomic lookahead before a site is treated as SEALED: class 2 derived and `once` accepted on a site that fires 3 times in one attempt
- status: CONFIRMED
- severity: answer (the `once` refusal contract and the reported firing class are wrong; any later stage that relies on class 1/2 would miscompile)
- effort: S (code) + S (spec sentence) ; blast radius: patterns with `(?*...)` / `(*napla:...)` holding a choice point before a site
- where: src/opt/callout.c:63-66 and 86-90 (`co_choice`: `case A_LOOK: return false` without reading `u.look.atomic`, the field internal.h:1710-1717 says is "the whole difference between the two families"); spec match_api.md §11.8¶2 ("one inside an atomic group, a possessive quantifier or a lookaround that completes before the site is SEALED") — the spec sentence carries the same error.
- repro: `build/pcrec -p rx --features classes,callouts,lookaround -o p.c --pattern '(?*a+)(?C"x,once")a+c'` -> rc=0; `--emit-ir` callouts row: `L2 1 rx_callout_x check once-per-start - no repeat and no live choice point before it`. Linked with a pass-everything binding, `rx_search` on `aaabc` fires x THREE times with caps[0]={0,-1} (one attempt at start 0: the engine backtracks into the lookahead's `a+`), then twice at start 1. Same pattern with `(?=a+)` fires once per start (correct).
- argument: §11.8¶1 class 2 promises "at most one fire per attempt"; §11.7 `once` "a site of class 3 is refused". Here a class-3 site is classed 2 and `once` is accepted. D62 control 3 (cited at the A_LOOK definition) names exactly this failure: a `case A_LOOK:` that does not read the atomicity field. Fix: `case A_LOOK: return !a->u.look.atomic && co_choice(cx, a->l);` (or true when non-atomic), and the spec sentence says "an atomic lookaround".

## CON-3 The compliance page's generated construct index was not regenerated: `(?C1)` reads `unbuilt` with the old PLANNED note, and the new `(?Cx)` malformed row is missing
- status: CONFIRMED
- severity: doc (the page whose header says it "cannot drift from the compiler" disagrees with the compiler)
- effort: S (`compliance_section.py --write`) ; blast radius: docs/pcre2_compliance.md generated index (SR-4)
- where: docs/pcre2_compliance.md:2275 ("142 rows") and :2346 (`| after (? | (?C1) | REJECTED | unbuilt | planned | callouts | vm | callout to user code: (?C) (?C1) (?C{text}) -- PLANNED (D36): M4-hosted ...`)
- repro: `build/pcrec --list-syntax | grep -vc '^#'` -> 143 (the diff adds the `(?Cx)` REJECTED row, src/parse/registry.c:1041); its `(?C1)` row reads `built` and the new note "the engine calls rx_callout_<n> or rx_callout_<name> (extern, user-defined) ...". The page's index still says 142 rows, `unbuilt`, and the old note; the `(?Cx)` row is absent. The prose annotation (line 2019ff) WAS refreshed, so the page contradicts itself (top: "ships OK-GATED"; index: "unbuilt").
- argument: the brief asks whether --list-syntax / compliance agree with the compiler: they do not. The index's own header says `make test` fails on this drift (`compliance_section.py --check`), so either the gate was not run on SUBJECT or it does not see this; worth the coordinator confirming which (I did not run it: COMMON forbids suites).

## CON-4 New caller-visible prefilter token `no-callout` (and its `-fprefilter` refusal) has no spec hunk; its note names a plan row
- status: CONFIRMED
- severity: doc (D80 + D174)
- effort: S ; blast radius: `--emit-ir` `summary` prefilter row of every callout pattern; `-fprefilter` on a callout pattern
- where: src/opt/select_engine.c:714-719; spec ir_listing.md §3.1.1¶1's token table (lines 83-95) — "the vocabulary is append-only" — lists `no-backreference`, `no-linked-call`, `no-variable` (each with its `-fprefilter refuses` clause) but not `no-callout`.
- repro: `build/pcrec --features classes,callouts --emit-ir --pattern 'a(?C1)'` -> `prefilter	no-callout	callout site -- a callout pattern's prefilter is not admitted yet (a later stage of [INLINE-C] admits it under the inexact-erasure rule); no flag changes this, and -fprefilter refuses`. `build/pcrec ... -fprefilter --pattern 'a(?C1)'` -> refused "-fprefilter cannot be honoured for a pattern containing a callout ...". Neither the token nor the refusal appears in docs/spec (grep `no-callout` over docs/spec: 0 hits; match_api §11¶1 says only "compiles to the VM engine").
- argument: D80 (a caller-observable token/refusal ships with its spec hunk); ir_listing §3.1.1 is the declared, append-only vocabulary. D174 (new caller-facing text names behaviour, never "lane or row ids"): the note's "[INLINE-C]" and "inexact-erasure rule" are a plan-row id and an internal mechanism. Suggested note: "callout site -- a callout pattern has no prefilter yet; no flag changes this, and -fprefilter refuses".

## CON-5 A site that can never run (`(?:..(?C1)){0}`, an uncalled `(?(DEFINE)` body) still counts as a site: the binding is stamped as needed, `--emit-main` refuses, and `_CALLOUTS` disagrees with `--emit-ir`'s `callout-sites`
- status: CONFIRMED
- severity: doc (contract wording) / design (minor)
- effort: S ; blast radius: patterns with a callout only in a never-run group
- where: match_api.md §11.2¶2-¶3 and §6.3 stamp rows ("`<PREFIX>_CALLOUT_BINDINGS` (the binding symbols the artifact needs)"); ir_listing.md §3.7¶1 ("The COUNT is summary's callout-sites row")
- repro: `build/pcrec -p rx --features classes,callouts -o e.c --pattern '(?:a(?C1)){0}b'` -> header `RX_CALLOUTS 1`, `RX_CALLOUT_BINDINGS "rx_callout_1"`, `extern const rx_callout_ref rx_callout_1;`, but e.c never references `rx_callout_1` (0 hits) and links without it; `--emit-ir` says `callout-sites 0` and "none: this pattern has no callout site". Same with `(?(DEFINE)(?<n>a(?C"dead")))b(?C"live")`: `RX_CALLOUTS 2`, bindings "rx_callout_dead,rx_callout_live", IR `callout-sites 1`. `--emit-main ... '(?(DEFINE)(?<n>(?C"z")))a'` -> refused "cannot define the binding rx_callout_z" though the artifact needs nothing.
- argument: "needs" is false for a dead site (no link error results, so §11.2¶2's "an unbound binding is a link error" does not hold either); the two "count" surfaces use the same words for different populations without saying so (`_CALLOUTS` = pattern sites, `callout-sites` = emitted sites, which also differs under unrolling: `(?:a(?C1)){3}` -> stamp 1, IR 3, which ir_listing §3.7¶1 does document). Minimal fix is spec wording: `_CALLOUTS` "the number of callout sites in the pattern as written", `_CALLOUT_BINDINGS` "the bindings the pattern names"; or drop dead sites before stamping. The `--emit-main` refusal on a dead-only pattern is harmless but follows from the same choice.

## CON-6 Class 1's "a passing fire IS the match" does not hold under `<prefix>_next`'s empty-match retry, and §11.8¶2's list of exceptions omits it
- status: CONFIRMED
- severity: doc (contract) / design (anything that later relies on class 1, e.g. a commit-on-pass mode)
- effort: S (spec sentence) ; blast radius: class-1 sites in a nullable pattern driven by the find-all iterator (`RX_ITER_RETRY "retry-budgeted"`)
- where: match_api.md §11.8¶1 row 1 + ¶2; the emitted `rx__match_notempty` program carries the site (it2.c:214-240 of a `(?C"x")` artifact)
- repro: `build/pcrec -p rx --features classes,callouts -o it2.c --pattern '(?C"x")'` (`--emit-ir`: `once-per-match tail`). Driver: `rx_iter it = rx_iter_init("ab",2); while (rx_next(&it,c)==1) ...` with x always returning 0 prints: fire pos=0 attempt=0 / match [0,0] / fire pos=0 attempt=0 / fire pos=1 attempt=1 / match [1,1] / ... The second fire at pos 0 is the not-empty retry's anchored run at start 0: the site PASSES and the run returns no match.
- argument: §11.8¶1 row 1 says "a passing fire IS the match"; ¶2 names the cases a class does not bound (different start positions, the tiered default's re-run) but not the iterator's not-empty retry, where the same start position gets a second anchored run whose accept is refused for being empty. Either list the retry beside the tiered re-run ("the find-all iterator's retry after an empty match re-runs the attempt under a not-empty rule; a pass there is not a match") or classify a nullable-tail site differently. Stage 1b relies on nothing here, so this is a contract-text fix today.

## CON-7 A site inside a `lib` definition is refused at the DEFINITION's offset but attributed to the calling target's line and pattern
- status: CONFIRMED (the attribution); SUSPECTED pre-existing for every refusal raised inside a composed definition (not checked)
- severity: doc (diagnostic location; low)
- effort: S-M ; blast radius: `.rxt` sources composing a `lib` definition that holds a callout
- where: the refusal in src/opt/callout.c `co_site` (pcrec_ctx_fail(cx, at, ...), `at` = the site's offset in the definition's own text) reported through the target's context
- repro: d.rxt `pattern zzzz(?C"inlib")` / `name d`; t.rxt `lib "d.rxt"`, target t2 `pattern x(?C1)y(?&d)`. `build/pcrec -o DIR/ --target t2 t.rxt` -> "t.rxt:9: target 't2': a callout inside a group reached by a subroutine call ... (pattern offset 4)". Offset 4 of t2's pattern is the `1` of t2's OWN `(?C1)`, which is legal; the offending site is at offset 4 of d.rxt's pattern. The user is pointed at the wrong callout.
- argument: §11.1 promises the refusal "by name"; a refusal that names the wrong site defeats it when the target has its own callouts. Fix: name the definition (`in lib definition 'd' (d.rxt:1), pattern offset 4`), or point at the call `(?&d)`.

## CON-8 `--emit-facts` and `--count-groups` accept `--callout` and silently ignore it: wrong facts for a `consume`-declared site, and no refusal of an unused number / unknown attribute
- status: CONFIRMED
- severity: answer (the facts listing describes a different pattern than the compile builds) + refusal contract
- effort: S ; blast radius: the two pattern-bearing queries that do not route through `pcrec_compile_callouts`
- where: cli/main.c (the `--emit-facts` / `--count-groups` paths never read `st.callouts`; the compile at :3102 and `--emit-ir` do); spec cli.md §1.21¶1
- repro: `build/pcrec --features classes,callouts --emit-facts --callout 1:consume --pattern 'a(?C1)b' | grep req_set_maxoff` -> `97:0,98:1` (b at offset <= 1), identical to the undeclared pattern; the named twin `--pattern 'a(?C"x,consume")b'` -> `98:unbounded` (correct; the compile of the declared pattern does consume: `axxb` matches [0,4)). `build/pcrec ... --emit-facts --callout 9:bogus --pattern 'a(?C1)b'` -> rc 0; `--count-groups --callout 9:consume ...` -> prints 0, rc 0. The same declarations under `--emit-ir` or a compile are refused ("names callout 9, which the pattern does not use").
- argument: cli.md §1.21 states the refusals without a mode exception; the facts listing is the observable statement of what the compiler derives, and here it derives from a pattern with the declaration dropped. Either apply the declarations in every mode that reads `--pattern` (the [K98] "above every mode" placement is the precedent) or refuse `--callout` in modes that cannot honour it.

## CON-9 A pattern ENDING at `(?C` is refused as "requires module 'callouts'" without the module, and as malformed with it
- status: CONFIRMED
- severity: doc (diagnostic tier; low)
- effort: S ; blast radius: patterns whose text ends exactly at `(?C`
- where: src/parse/mod_callouts.c:121-129 (the comment documents the tail-less recogniser answering "yes"); src/parse/registry.c `(?Cx)` REJECTED row; spec pattern_language.md §7.11¶3 ("a malformed `(?C` ... with or without the module")
- repro: `build/pcrec -p rx --features classes -o x.c --pattern 'a(?C'` -> "(?C...) requires module 'callouts'"; with `--features classes,callouts` -> "malformed callout: ...". Every other malformed form (`(?C1`, `(?C"a"`, `(?C256)`, `(?C@a@)`, `(?Cx)`) is refused as malformed at both gate states.
- argument: the point of the gate-independent malformed row is that enabling the module never turns into the advice; here the first diagnostic tells the user to enable a module, and enabling it yields a different refusal. D26 puts wording low, but the tier (shape 1 vs the malformed/grammar shape) is the thing §7.11¶3 states.

## CON-10 Small contract-text nits
- status: CONFIRMED
- severity: doc
- effort: S ; blast radius: spec text only
- (a) match_api.md §11.7¶1 cites "the `.rxt` `callout <n> <attrs>` line (`rxt_format.md` §1.1)"; the line is specified at rxt_format.md §1.5¶13a (§1.1 is "The head"). The design (inline_c.md §8.2) also said §1.1; the spec landed it in §1.5 and the citation was not moved.
- (b) §11.1 says a site inside a lookbehind is "refused by name". A `consume` site there is refused by the lookbehind width check instead: `--pattern '(?<=a(?C"x,consume"))'` -> "variable-length lookbehind is not implemented ... (this one is unbounded)", which never mentions the callout. Refused, never miscompiled, so only the "by name" half misses; the walk that names it (callout.c `co_site`, `behind`) runs after the width check.
- (c) cli.md §1.21¶1 lists the refusals as unused number / unknown attribute / malformed value; the code (and match_api §11.7¶2) also refuse a number declared twice and a repeated attribute. §1.21 should list them or point at §11.7¶2.

## GOALS lens
- Stage 1b ships no code segments, so Goal 1 (trust) is untouched; nothing here opens a door to code. Goal 2 (defined answer): 16 hand-built veto cases agree with libpcre2 10.x run with the three answer-moving flags off (below), and the view/returns match §11.3-§11.4. Goal 3(a) (zero movers): not checkable here (main's build/pcrec is not at BASE: main has moved to 12b5bd70c with stage 0 merged, and the binary's source is unknown), so I built nothing and left it to the identity gate. Goal 4 is stage 2+.
- Against the rulings: CON-2 contradicts Frank's ruling (6) in plan_row_bodies/INLINE-C.md ("`once` ... refused with the reason if the site can fire more than once per match attempt"). Nothing else shipped contradicts a ruling: check-by-default with a `consume` opt-in (ruling 5), read-only `const rx_ctx *` (3), one step per fire with no budget access (4), the libpcre2-with-optimizations-off oracle (manager FR1 reading), and `once` needing a non-retryable prefix with the possessive/atomic hint (rev 1 ruling 2).

## PROBED-AND-HELD
- Spellings: 8 delimiters (`` ` ' " ^ % # $ {} ``) accepted; `@` refused as malformed; `(?C)` binds rx_callout_0; `(?C01)`/`(?C000)` -> 1/0; `(?C256)`, `(?C1x)`, `(?C-1)`, `(?C 1)`, `(?Cx)`, unterminated `(?C"a`, `(?C1`, `(?C"a"` refused as malformed at both gate states (except CON-9). 40 forms total.
- Names: `""`, `"a b"`, `"1a"`, `"a""b"` (a doubled delimiter decodes to a non-identifier), `{a}}b}` refused; `__` anywhere in the name refused by name; `_a`, `a_`, mixed case accepted, and case is preserved under `(?i)`; `verify` refused by name (shape 2); unknown, repeated and `,,` attributes refused (except CON-1).
- Not quantifiable: `?` `*` `+` `{2}` `{0}` `??` `*+` all refused; `(?:(?C1))*` accepted.
- Placement: lookbehind (`(?<=`, `(?<!`, `(?<*`, `(*naplb:`, and lookahead nested in a lookbehind) refused by name; `(?1)`, `(?R)`, `(?&n)`, `(?-1)`, a called DEFINE group, and a lib definition refused; lookahead, negative lookahead, non-atomic lookahead, atomic group, alternation and backreference contexts accepted; a conditional is refused by the conditionals module (unbuilt), so the condition case cannot be reached yet.
- Literal contexts: `\Q(?C1)\E`, `[(?C1)]`, an `(?x)` comment are not sites; `(?x)a (?C1) b` is.
- `--callout`: 0-255 range, `256`/`-1`/overflow/`1x`/`:x`/leading space refused as malformed; unused number, declared twice (the same or different attrs), unknown attribute, `verify`, repeated attribute, and a trailing comma refused; combined with a file operand refused; `.rxt` `callout N ATTRS` gives the same refusals with file:line (300 refused at the shape layer).
- `--emit-main` refusal text matches cli.md §1.10¶2 for numbered and named bindings.
- Namespace: `-p rx_callout`, `rx_callout_`, `rx_callout_x` refused naming the family; `rx_calloutx`, `RX_CALLOUT`, `x_rx_callout` accepted (row 2 has no "any case" clause, unlike row 4).
- Stamps: `_CALLOUTS` = pattern sites; `_CALLOUT_BINDINGS` sorted, distinct, comma-separated; one extern per binding; two callout headers in one TU compile (guarded family); a non-callout header emits no callout text.
- View (10 drivers): ncap = groups+1 even under `--no-captures`; a group is `{-1,-1}` until it closes; a repeated group keeps its previous iteration until it closes again (nested and looped cases); backtracked-out groups read unset; caps[0] = {attempt start, -1} and is unmoved by `\K`; `user` is the binding's; vars/nvars are passed through (and NULL/0 without vars, including the iterator's retry path).
- Returns: 0 passes; -1 backtracks (check and consume); consume k moves pos and the enclosing group spans it; consume past the end, off a UTF-8 boundary, a positive return from a check, -7 and -10 trap; -2..-5, -6, -8, -9 propagate unchanged; a callee FRAMES give-up is not escalated (one fire, no tier re-run).
- Budget: fires charged (`--step-budget=10` with 10+ fires -> -2; 5 fires -> match); `--fno-step-budget` emits no counter.
- `--engine=dfa` with a site refused; `-fprefilter` refused (but see CON-4).
- Firing classes, 29 shapes: atomic, possessive and atomic-lookahead sealing, `{n}` vs `{n,m}`, lazy, a call before the site, an optional group, `{0,1}`, tail detection through a group close, an empty group, `{0}` inert follower. All are consistent with §11.8 except non-atomic lookaround (CON-2). The `once` refusals carry the hint.
- PCRE2 differential (flags off), 16 veto cases including the two §11.6¶2 shapes, alternation retry, atomic, lookahead/negative lookahead, non-atomic lookahead, empty pattern, `^`, repeated groups and nested quantifiers: 16/16 same.
- A pcrec artifact bound as a `consume` callee (`inner_match` for `\d+`): 4/4 subjects as expected.
- Consume against the facts: `^a(?C"x,consume")b$`, an unanchored consume, a `{2}` repeat with consume, `\z` and lookahead followers all answered correctly (the compile path honours `--callout` consume; only `--emit-facts` does not, CON-8).
