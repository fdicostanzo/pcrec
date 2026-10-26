# emitbidi2 report -- make every emitted byte ASCII ([EMIT-BIDI] follow-up)

Premise test: `-fcomments` on `a(b|c)+d` printed 3 lines with bytes >= 0x80 (non-zero, as expected).

## Sites found and fixed (pcrec-owned, all string literals that write emitted text)
Scanner (comment-stripping, string-literal aware, also catches octal/hex escapes >= 0x80) over src/, cli/, lib/ found only two characters in src/gen: U+2014 (em dash) and U+00A7 (section sign). Fixed spelling: em dash -> `--`, section sign -> `section ` (everywhere).
- src/gen/emit_dfa.c: the rx_abi block "working storage (spec section 10)" (was an OCTAL-escaped `\302\247`, which a raw-byte scan misses; reaches every .h), the give-up-code comment in emit_comb's twin, plus 17 non-emitted literals (axes `.desc` rows, next_keys text, `pcrec_ctx_fail` internal-error text).
- src/gen/emit_vm.c: resume-stack comment (PRIVATE TO THIS FILE), two `[DD-14.FB]` comments, the candidate / step-counter comments, the VE_NOTE zero-iteration note (query listing), internal-error texts.
- src/gen/emit_comb.c: "Unreachable on this engine" give-up comment (2 lines).
- src/gen/known.c: one internal-error text.
- src/enc, src/core/sb.c, src/gen/*.h: none.
Other tree literals with em dashes/section signs (src/parse/registry.c, src/dump/*, src/opt/*, src/core/compile.c, cli/main.c, limits.def, ...) are diagnostics / query-listing tables, never written into a C artifact; left alone (changing them is not this lane's rule).
Side effects: tests/codegen/manifests/ir_listing_baseline/8503088e.ir line 129 (the VE_NOTE text) re-pinned; two sabotage anchors (S480, S486) quoted the old `§`, updated (m6read_check_sab_anchors: all 1001 resolve).

## Empirical cross-check (after the fix)
`-fcomments` (and default) artifacts for 21 shapes (DFA unanchored/anchored, VM, backrefs-free features-all shapes, lookaround, named groups, `--emit-main`, utf8/ucp, `--no-captures`, subst template, `--emit-support`) and every tests/**/*.rxt (297 files, 292 compile; 5 are expected-error sources) with `-fcomments`: zero bytes >= 0x80 in any .c/.h. Before the fix every DFA/VM artifact had them (the `.h` working-storage comment in all; VM resume-stack comment, `[DD-14.FB]` comments; DFA give-up comment).

## Kit-owned literals (memfn/src), NOT edited
Bytes >= 0x80 (all `§`) in string literals: finder.c:237 (a `why` text), window.c:96,316,625,629,696, compose.c:1141,1158 (the %s ones are error/explain text), plan_cost.def:30,33,40,43,46,49 and fields.def:192,221,250,265,340,343 (description columns). NONE reached any artifact in the sweep above (no -fsimd/kit-heavy shape was seen to emit them), so the check's own artifacts are ASCII. If a future kit-emitted site reaches output, the artifact ASCII arm fires; the literal scan excludes memfn/src by name (another owner's; the manager files the kit request if wanted: ask the kit to make these literals ASCII or to adopt the scan).

## Guard
tests/codegen/run_ctext_ascii.sh: arm (1) is back to the pure-ASCII assertion on .c and .h per label (latin-1 decode fix kept); new arm (4) `[litscan]`: comment-stripping literal scan over src/gen/*.c,*.h, src/enc/*.c, src/core/sb.c (21 files) failing on any byte >= 0x80, raw or octal/hex-escaped, with a synthetic control file proving it flags exactly 2 of 4 candidates (a comment and a char constant are not flagged). 14 checks now (was 12). S1620 description restored. S1622 (em dash planted in the rx_abi working-storage literal, src/gen/emit_dfa.c): measured DETECTED (codegen 1 fail / 330 pass).
`make test-codegen`: the only red was SABANCHOR (fixed above) and run_ir_listing (re-pinned, 155/0); not re-run whole after those two fixes (queued job does).

## Spec / abi
docs/spec/match_api.md (~1783): widened to "every byte of the artifact, .c and .h, is ASCII under every option" (no kit exception found). abi stays 86; a line added to its abi_changelog entry. src/gen/CLAUDE.md rule already says ASCII-only; unchanged.

## STATE AT HANDOFF
Rulings file: no entries (none yet) applied. Commits on lane/emitbidi after 3ab67df98. Job file updated (ctext=14, mech S1620 S1621 S1622 = 3 rows; codegen=19 unchanged) and re-queued as emitbidi-landtest3.
