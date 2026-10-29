# PREM critic, inline-c (premise + goals lens)

Subject: /tmp/claude-1001/crit-inline-c/subject_inline_c.md (inline_c rev 0). Source read at main 8f4fd7631.
No denylisted file opened; no auto-injection observed.

## Findings

### PREM-1  The reference flags omit PCRE2_NO_DOTSTAR_ANCHOR: libpcre2 with the note's two flags is NOT the unoptimized backtracking order
- status: CONFIRMED. Probe /tmp/claude-1001/crit-inline-c/probes/prem/p.c (libpcre2 10.46), a callout that vetoes when `start_match == 0`, subject `axbx`:
  `(?s).*(?C1)x` with `PCRE2_NO_AUTO_POSSESS|PCRE2_NO_START_OPTIMIZE` -> rc=-1 (no match: PCRE2 auto-anchors a leading dotall `.*`, so start 1 is never tried);
  the same plus `PCRE2_NO_DOTSTAR_ANCHOR` -> `[1,4)`. pcrec has no dot-star anchoring (src/facts/startanch.c answers only BOT/GSTART/NONE; `(?s).*(a)x` emits `RX_VM_START "unanchored"`), so pcrec's VM computes `[1,4)`.
- severity: answer (goal 2's measurable form is red by construction on this shape; the spec sentence would name the wrong PCRE2 configuration)
- effort: paragraph edit
- blast radius: inline_c §1.7, Goal 2, §9.2 flags line, §10 Q1's wording ("compatible with PCRE2 with auto-possessification and start optimization off") and the requirements' P-probes re-oracled under the corrected flags
- where: inline_c §1.7 (L265-272), Goals L36-38, §9.2 L959-960, §10 Q1 L1001-1003
- argument: the note's claim "the unoptimized backtracking order ... which is libpcre2 with PCRE2_NO_AUTO_POSSESS | PCRE2_NO_START_OPTIMIZE" is false; PCRE2 has (at least) a third answer-moving optimization under callouts, dot-star auto-anchoring, which neither flag disables (PCRE2 disables it only for backref'd captures and (*PRUNE)/(*SKIP), not for callouts). Any other start-position optimization in PCRE2 that callouts do not disable is in the same class; the note asserts the set is two without a survey.
- proposed fix: make the reference flags `PCRE2_NO_AUTO_POSSESS | PCRE2_NO_START_OPTIMIZE | PCRE2_NO_DOTSTAR_ANCHOR`, say so in Q1's plain-words text, add the `(?s).*(?C..)x` start-veto case to stage 1's differential, and state how the flag set was established (a pcre2api survey of every NO_* option, not two probes).

### PREM-2  Goal 2's "zero disagreements" is unreachable by design: the textual `ncap` hides groups PCRE2 shows at a looped site
- status: CONFIRMED. libpcre2 10.46, `(?:(?C1)(a))+` on `aa`, no-optimize flags: the second fire reports `pos=1 top=2 g1=(0,1)`. inline_c §1.3 sets `ncap = 1 + the highest group number whose opening parenthesis precedes the site` = 1 here (group 1 opens AFTER the site), so `RX_CAP_SET(1)` is false in pcrec while the §9.2 adapter ("`RX_CAP_S(n)` reads `offset_vector` under `capture_top`") reads it set. A predicate `return RX_CAP_SET(1) ? RX_FAIL : RX_PASS;` answers `[0,2)` in PCRE2 terms differently: PCRE2 vetoes iteration 2, pcrec passes it.
- severity: answer (or: goal 2's checkable form is false as written; the stage-1 differential goes red on a valid supported position, §1.9 row 5 "quantified groups")
- effort: paragraph edit (pick one: widen the view, or narrow the goal)
- blast radius: §1.3, Goal 2, §9.2, §7's porting table row `capture_top`, the spec hunk for match_api §5
- where: inline_c §1.3 L149-151, Goal 2 L35-41, §9.2 L957-964; engine_m4.md L785-790 (the textual rule's origin)
- argument: the note treats the textual watermark as given (engine_m4.md §3.4's "honest reading of D38.6") and simultaneously promises PCRE2 answer-equality for capture-reading predicates. Both cannot hold for a site inside a repeated group that precedes a later-numbered group. The "deterministic regardless of path" motive is also met by `ncap = ngroups + 1` with every readable group publish-at-close (an unset/never-closed group reads `-1` either way), which is PCRE2's observable view.
- proposed fix: either make the site's readable set "every group, published-at-close where a site can read it" (ncap = ngroups+1) and drop the textual rule, or keep it and state the divergence in Goal 2/§1.7/§9.2 as a declared exclusion with its own test showing the difference.

### PREM-3  "A `W_PRED` site erases to the empty string" collides with the existing exactness machinery: either `scan-end` is unreachable, or the VM's prefilter-window ceiling loses vetoed matches
- status: CONFIRMED (by reading the derivation; no build exists to run). `VM_RESEED "exact"` is the row `cand_rs_exact_applies` = `s->vm->mrl_win` (src/gen/emit_dfa.c:9758), and `mrl_win` is `pcrec_vm_prefilter_window` = `fit.prefilter && !nfa.erased` (src/gen/emit_vm.c:3686-3688). The same predicate turns on `VM_PRUNE_CEILING "prefilter-window"`: the VM's anchored body is clamped to the scan's span end (see any exact hybrid, e.g. `build/pcrec -p rx --pattern '(a(b)c)+d'`: `rx_match_anchored(&ctx, run, window_end)` with `window_end = window[0][1]`), and `pcrec_cand_lang_exact` (emit_dfa.c:11338) reads it too.
  Horn A: the build lane records a callout erasure in `Nfa.erased` (the only sound reading: a vetoing site makes the erased language a strict superset). Then `VM_RESEED` is never `"exact"` on a callout pattern, inline_c §4.3 row 6 (`end-unproven`) fires for EVERY pattern, and row 7 `scan-end` is dead code; stage 4's goal 3b cannot be met.
  Horn B: it does not record it (the note's text, §1.8 L297-299, reads a `W_PRED` erasure as language-neutral). Then the hybrid clamps the VM to the scan's leftmost-first end. Pattern `(?:a|ab)(?{c,verify: return RX_POS == 1 ? RX_FAIL : RX_PASS;})` on `ab`: scan answers `[0,1)`, the segment vetoes, the §4.2 step-3 fallback VM at 0 tries `ab` but `pos 2 > window_end 1` is pruned, answer "no match"; the reference (and PCRE2) answer `[0,2)`. The same holds for the row 2-6 "inline / hybrid without scan-end" downgrades whenever the prefilter is admitted.
- severity: answer (horn B) / design (horn A)
- effort: section rewrite of §1.8 last paragraph + §4.2/§4.3 row 6 + §4.4 item 2
- blast radius: stage 4's eligibility table, the `hyb-reseed` and prune-ceiling rows, `pcrec_cand_lang_exact`'s boundary projection, the S-IC15..17 sabotage set (none of them targets the ceiling)
- where: inline_c §1.8 L297-305, §4.2 L568-577, §4.3 row 6 L588, §4.4 item 2 L607-611
- argument: the note's premise is that "the scan proves the match END" is one fact the existing stamp already carries. It is two facts: (i) the scan's end is R's leftmost-first end (needed by §4.4 item 2; true when R has no erasure and T is the tail), and (ii) the scan's end bounds the WHOLE pattern's match end (what `mrl_win`/prefilter-window means; false as soon as any site can veto). The existing derivation conflates them because, before callouts, every erasure widened the language and a callout-free tail never vetoed.
- proposed fix: say explicitly that a callout site records an erasure (`NFA_ERASED_CALLOUT`, so `mrl_win`, prune ceiling and `VM_RESEED` read inexact, sound by the existing machinery), and give `scan-end` its own end-proof predicate: "the erasure set restricted to R is empty" (R = the pattern minus the tail run), read from the lowering, not from `VM_RESEED`. State that the §4.2 step-3 fallback VM runs with the subject-end ceiling, and add a sabotage row "the fallback keeps the prefilter-window ceiling" with the `(?:a|ab)` witness.

### PREM-4  `features all` already enables every registry module: the gate's "nothing else enables it" is false unless the note excludes code modules from `all`
- status: CONFIRMED (current code). src/parse/enabled.c:262-268: `"all"` is the OR of `rows[i].feature` over EVERY registry row. inline_c §1.1 L120-121 / §2.1 make `(?{` (and tagged `(?C`) a registry row owned by module `code-<lang>`; so `features all` in a block (rxt_format.md §1.5¶5), in a config body (§1.1¶2), on a config's `pcrec` line (`--features all`), on the CLI, or through the library's feature spec enables `code-c` with no `--allow-code`.
- severity: trust (goal 1, rank 1)
- effort: paragraph edit + one row in stage 2's refusal list
- blast radius: §5.1's bullet list, §2.4 row 3, goal 1's per-entry-point refusal tests, `enabled.c`'s `all` and any future named set (D37 frozen sets), `--list-syntax`'s module column
- where: inline_c §5.1 L647-654, §2.4 L410-412, Goal 1 L28-34
- argument: the note tests only the literal spelling `features code-c`; the premise that a module becomes enabled only by being named is false today. A file author writes `features all` and the invoker who never passed `--allow-code` compiles code.
- proposed fix: state that `code-*` modules are outside every feature spec (`all`, named sets, explicit lists) and are reachable only through the `--allow-code`/`pcrec_options` member, i.e. a separate mask the feature resolver cannot set; add `features all` (block, config, `pcrec` line, CLI, library) to goal 1's refusal-per-entry-point tests and a sabotage row "`all` includes code-c".

### PREM-5  Slot 0 is NOT free mid-match: it is `\K`'s trailed start, so the site's "one store" changes the reported match start
- status: CONFIRMED (current emitted code). `build/pcrec --features assertions -p rx --pattern 'a\Kb(x)c'`: `\K` emits `RX_SET(RX_SLOT_WHOLE_START, scan_position)` (slot 0, trailed), and the report reads `capture_spans[0][0] = run->slot_values[0] != PCREC_UNSET ? run->slot_values[0] : match_start` with the comment "PCREC_UNSET means no \K was crossed on this path".
  Under inline_c §1.2 item 2 / §1.3 ("Write slot 0's start: `stv[0] = attempt start`"), `a\Kb(?C1)c` on `abc`: `\K` sets slot 0 = 1, the site stores 0, the report reads 0, answer `[0,3)`; PCRE2 (and the reference) answer `[1,3)`. Conversely, if the store were skipped, the callee reading `RX_START` after a `\K` sees the `\K` position, not PCRE2's `start_match` (which the note says it must be).
- severity: answer
- effort: paragraph edit (§1.3 slot-0 bullet) plus one test and one sabotage row
- blast radius: §1.3, §3.2 `RX_START`, §7's porting row `start_match`, stage 1 tests, the "costs one store, no rx_ctx field" claim (R-P3 resolution, §10a item 6)
- where: inline_c §1.2 L138, §1.3 L164-169 ("On a completed match the entry overwrites slot 0 as today" is false: the entry READS slot 0 as the `\K` start); §1.9's position table has no `\K` row
- argument: the premise that slot 0 is unused until completion holds only for `\K`-free patterns. Slot 0 is a live, trailed register in every `\K` VM artifact (`\K` forces the VM, match_api §3.1¶20, so every `\K` + callout pattern hits it).
- proposed fix: at a site, save slot 0, store the attempt start, call, restore (two extra moves, still no `rx_ctx` field), or declare `\K` and callouts mutually refused in v1 (a §1.9 row); add `a\Kb(?C"see")c` to stage 1's differential (it checks both the reported start and the callee's `RX_START`) and a sabotage row "the site's slot-0 store is not restored".

### PREM-6  The pin is a second spelling of an existing fact, and SHA-256 already exists in-tree: the note proposes both as new
- status: CONFIRMED. (a) rxt_format.md §1.6¶7 already pins a file's contents in the same format: `@file:"path" [as <id>] [sha256 <hex64>]`, keyword-then-value, hex compared case-INsensitively (parser: src/parse/rxt_source.c:2125-2140). inline_c §5.3 proposes `sha256=<64 lowercase hex digits>` (key=value, lowercase only) for `include`/`lib`, without citing the precedent. (b) analyze/sha256.c + analyze/sha256.h is a zero-dependency FIPS 180-4 one-shot SHA-256 (`pcrec_analyze_sha256_hex`), built by the Makefile:356 rule; inline_c §5.5 L709-711 proposes "a small in-tree FIPS 180-4 implementation under `src/core/`" as if none existed.
- severity: design / maintenance
- effort: paragraph edit
- blast radius: §5.3 grammar, §5.5, `--list-schema` rows, stage 3's NIST-vector control (it would be the third consumer of the vectors, or the second implementation of them)
- where: inline_c §5.3 L670-678, §5.5 L709-711
- argument: house rule "general mechanisms, not special cases" and the standing sibling question: a file-content pin is a family with one member already; a second member with a different spelling and a different case rule is exactly the dispersed-sibling shape. The duplicate implementation needs at least a sentence (analyze/ may not link src/, per analyze/CLAUDE.md, but src/ can host the shared copy and analyze can keep its own, or the note argues why two).
- proposed fix: spell the pin as the format already does (`include "frag.rxt" sha256 <hex64>`), name §1.6¶7 as the precedent, and say where the one SHA-256 implementation lives (reuse or move analyze/sha256.c; state the duplication if kept).

### PREM-7  `verify` row 5 keys on the wrong fact: `<PREFIX>_NCAPS > 1` is "delivers groups", not "the site reads groups" (`--no-captures` breaks §4.4 item 2)
- status: CONFIRMED for the premise; the failure is by construction. `build/pcrec --no-captures --features backrefs -p rx --pattern '(a+)x\1'` emits `RX_NCAPS 1` while keeping `RX_SLOT_GROUP1_START/END/PENDING` live for the reader: under `--no-captures` a group-bearing pattern has NCAPS 1. inline_c §4.3 row 5 (`captures`: "`<PREFIX>_NCAPS > 1`") therefore passes `(\d+)(?{c,verify: return RX_CAP_LEN(1) <= 3 ? RX_PASS : RX_FAIL;})` under `--no-captures` to `scan-end`, whose view (§4.2 step 1) is `ncap = 1`, so `RX_CAP_LEN(1)` reads -1 and the segment always passes; the reference (site `ncap = 2`, §1.3) vetoes `1234`'s 4-digit path. Different answers; §4.4 item 2's "with no capture slots beyond 0 (row 5), the reference's view at that fire is exactly the one step 1 builds" is false here.
- severity: answer
- effort: paragraph edit (row 5's predicate and §4.4 item 2's wording)
- blast radius: §4.3 row 5, §4.4 item 2, S-IC16's witness, `make test-axes` corpus (add a `--no-captures` verify case; test-axes compares deny flags, not `--no-captures`, so it would not catch this on its own)
- where: inline_c §4.3 L587, §4.4 L610-611
- argument: the premise "no delivered groups => the tail sees no groups" conflates the output axis with the site's view. The site's `ncap` is textual (§1.3) and independent of `--no-captures`.
- proposed fix: row 5's predicate becomes "some tail site's `ncap > 1`" (the site can read a group), read from the node, not the stamp; keep `NCAPS > 1` as a separate reason only if the VM walk is otherwise needed for delivery.

### PREM-8  "Each pass already answers for `A_BREF` ... read the callout through that same predicate" assumes a predicate that does not exist, and `A_BREF` is the wrong analog in at least one pass
- status: CONFIRMED (code reading). There is no shared "capture-reading consumer" predicate: `grep -rn "case A_BREF" src` = 63 switch arms (134 mentions) across 16 files (opt/atomic.c 16, emit_vm.c 19, possessify.c 12, revdet.c 10, mrl.c 8, facts/*.c, ir/nfa.c ...), mostly exhaustive switches with no default (startanch.c's header: "a node kind added after this file is written must be a COMPILE ERROR here under -Wswitch"). Every one of them needs an `A_CALLOUT` arm, chosen per pass. And the analog differs by pass: possessify.c:540-549 gives `A_BREF` a NARROW FIRST set from the referenced groups' bodies when arm B is on ([ART-POSS-ARMS] `bref_first`), which a callout has no equivalent of; startset.c:120-133 treats zero-width gates (`A_LOOK`, `A_KRESET`) as transparent and `A_BREF` as "every byte". The right analog for a `W_PRED` site is the zero-width GATE (`A_LOOK`: 0xff+nullable in possessify, transparent in startset/widths), and for `W_ANY` it is `A_VAR` (opaque consumer); capture-reading is an ADDITIONAL property (the marked set, deferred capture writes such as the span-cursor/revdet forms), not the class.
- severity: design (and answer if a lane copies `A_BREF`'s arms literally: arm B on `\d+(?C1)` would need a FIRST set the callout cannot supply)
- effort: paragraph edit of §1.8; the build-stage cost (63 arms) should be stated, not hidden behind "one rule"
- blast radius: §1.8, stage 1's scope estimate, S-IC3 (possessification ignores a site) and S-IC6b, which cover two of the 16 files
- where: inline_c §1.8 L281-289
- argument: the general statement is good; its mapping onto "the same class as `A_BREF`" is not. A site is position-reading (like `A_LOOK`) AND capture-reading (like `A_BREF`) AND, for `W_ANY`, an opaque consumer (like `A_VAR`); the passes key on those as separate kinds today.
- proposed fix: state the site as "a gate (`W_PRED`) or opaque consumer (`W_ANY`) that additionally reads `pos` and groups `1..ncap-1`", name the per-pass analog table (`A_LOOK` / `A_VAR` + the capture-reader marks), say the `-Wswitch` exhaustiveness is what enumerates the sites, and give the sabotage set a row per family of pass (first-set, width/required-run, deferred-capture), not two.

### PREM-9  The note's main answer control (`make test-axes`) does not reach the callouts corpus as designed: it would AGREE vacuously
- status: SUSPECTED (the build does not exist; the premise is checked against the sweep as it stands). tests/axes/run_axes.sh sweeps the whole tree through tests/harness/run.sh with `RXTFLAGS=<axis flag>` and compares RXTDUMP lines; a case refused at compile on both sides dumps `trc=REFUSED` with the same diagnostic text on both sides, and dump_diff.awk's first bucket is "AGREE: trc and out identical on both sides". inline_c §5.7 puts `--allow-code=c` only in "the callouts section's runner", and §3.6 puts the user-C link in an `ext harness` block the harness does not consume today (no `ext` consumer in tests/harness/run.sh or verify_rxt.py). So under test-axes every callouts case is either REFUSED (no opt-in) or a link failure on BOTH sides: zero MISMATCH, green. What would confirm: run_axes over a callouts file once stage 2 exists, or a written statement of how RXTFLAGS/run.sh carry the opt-in and the link step.
- severity: trust (the control for goal 2 and for §1.8's "one rule, every pass" and §4.4's equivalence; the note names test-axes as THE control in §1.8 L287-289, §4.4 L626-628 and Goal 2)
- effort: paragraph edit + a reach-count check in stage 1's test list
- blast radius: Goal 2's measurable form, stage 1 and 4 test lists, §5.7 (an opt-in the sweep passes corpus-wide would also flip the T2 "refused elsewhere" check under test-axes)
- where: inline_c Goal 2 L39-41, §1.8 L286-289, §4.4 L626-628, §5.7 L724-730, §3.6 L539-548
- argument: learnings §3 / memory check-design-lessons: a control whose population nobody counts. The [MECH-REACH] sentence in standing question 2 is about sabotage witnesses, not about the sweep's population.
- proposed fix: say how test-axes passes `--allow-code=c` and links the stubs for the callouts section only (a per-file opt-in the harness reads, not RXTFLAGS), and require run_axes to report the count of NON-REFUSED, built callouts cases per axis with a floor; red when it is zero.

### PREM-10  `#line` under `pattern-esc`: the source is ONE line, the decoded text is many, so gcc's lines after the first decoded `\n` are wrong (goal 4's measurable form)
- status: CONFIRMED (spec reading). rxt_format.md §1.5¶3: `pattern-esc "<quoted>"` is a single source line whose value is DECODED (`\n` -> newline) — "multi-line CAPABILITY ... without multi-line SYNTAX". inline_c §3.4 L522-524 sets the `#line` to "the source line of the segment's first byte, counting the newlines a `pattern-esc` value carries", and §3.1 emits the decoded text after ONE `#line`. For `pattern-esc "(?{\n  int x = ;\n  return 0; })"` on source line 7, gcc reports the syntax error at line 8 (one `#line 7` plus one decoded newline), but the file has no such content on line 8; every line of a multi-line escaped segment after the first is mis-attributed, and columns are shifted by every escape's width. "Counting the newlines" moves the first byte's line, which is also wrong: every byte of the value is on the opener's line.
- severity: doc / goal-4 (diagnostics land on the wrong line; no answer impact)
- effort: paragraph edit
- blast radius: §3.4, §3.1's padding rule, DT-3.3's test (add a multi-line `pattern-esc` row)
- where: inline_c §3.4 L522-524, §3.1 L436-437; goal 4 L51-54
- argument: the premise that one `#line` plus the decoded text reproduces source positions holds for `pattern` lines and CLI text only.
- proposed fix: for a `pattern-esc` segment emit `#line <opener line>` before EVERY decoded line (all map to the one source line) and drop the column padding there; state goal 4's form as "the pattern file's own line" (column only for unescaped text).

### PREM-11  Goal 1's entry-point population names a set that is empty today and is silent on the reviewer's own tool
- status: CONFIRMED. `build/pcrec --help`: the `--list-*` modes are `--list-axes/-definitions/-families/-limits/-schema/-source/-syntax/-verbs`; none compiles a pattern. The pattern-parsing modes that are not C-writing targets are `--emit-ir`, `--emit-facts`, `--count-groups`, `--probe-ask`, `--explain` (tests/cli/run_cli_tests.sh:1112). Goal 1 (L29-31) and stage 2's test list (L897-899) say "every `--list-*` that compiles", which today is the empty set, and the only future member is §5.6's `--list-callouts`, the REVIEWER'S view, which must show the decoded code of a file whose invoker has NOT yet granted `--allow-code` (that is when one reviews it). Read literally, goal 1 makes `--list-callouts` refuse the segments it exists to display.
- severity: trust / doc (goal 1 is the rank-1 goal and its population is how it fails)
- effort: paragraph edit
- blast radius: Goal 1, §5.6, stage 2/3 test lists
- where: inline_c Goal 1 L28-34, §5.6 L715-721, §9.1 stage 2 L897-899
- argument: a measurable form with an uncounted or empty population cannot fail (architecture.md: "a way to fail"). The relevant population is "every mode that writes C or an artifact" (FILE targets, `--pattern`, `-o -`, `--emit-main`, the library's compile entries, the harness), and separately "modes that only describe" (`--emit-ir`, `--emit-facts`, `--explain`, `--list-callouts`), which should parse code without the opt-in and emit no C.
- proposed fix: enumerate the two populations by mode name in goal 1, with the count; state `--list-callouts` works without `--allow-code` and that its output is not C (no `#line`, no compilable artifact).

### PREM-12  The tree already holds registered obligations for "the kind that adds a callout": the note does not name them
- status: CONFIRMED. src/gen/emit_dfa.c:8600-8606, the req handoff's conjunct (g): "NO VERB AND NO CALLOUT ... the kind that adds one must add a `PF_KIND_*` bit (src/facts/kinds.c's exhaustive switch is its alarm) and decline here. Sabotage S475 ships UNREACHED." emit_dfa.c:7841-7845, the start-set seek: "NO VERB AND NO CALLOUT ... the kind that adds one must decline here. Sabotage S496 ships UNREACHED." tests/mech/sabotages/S475_verb_conjunct_dropped.sh and S496_vmhat_verb_conjunct.sh are DECLARED UNREACHED "until a verb or callout compiles". Also tests/codegen/run_ir_listing.sh:493-520 asserts the `--emit-ir` callouts count is 0 "because module 'callouts' has no producer". facts.h:275-281 has no `PF_KIND_CALLOUT`. inline_c §1.1 ("no callout clause in the selector"), §1.8 and §8.1 do not mention any of these; stage 1's sabotage list (S-IC1..6b) does not take over S475/S496.
- severity: maintenance / answer-risk (the decline obligation exists because a skipped attempt could hide an answer-relevant event; the note must either honour it or argue it away)
- effort: paragraph edit + stage-1 scope lines
- blast radius: stage 1 scope (a `PF_KIND_CALLOUT` bit, two declines or a ruling retiring them, S475/S496 become reachable and owe figures), the ir_listing test and `ir_listing.md`'s callouts section
- where: inline_c §1.1 L119-125, §1.8, §9.1 stage 1 L871-890
- argument: the note's premise is that callouts enter a tree with no prior commitments ("`VE_CALLOUT` is reserved ... with no producer"), and it found that one reservation; three more are on file in the same shape. Under the note's own fire contract (§1.7: fires on abandoned paths are unspecified; pure callouts) a skipped no-match attempt cannot change an answer, so the decline may be retirable for callouts while staying for verbs — but that is a ruling the note should make, with the sabotage rows re-scoped to verbs only.
- proposed fix: add a stage-1 bullet: `PF_KIND_CALLOUT`; for each of (g)/S475 and the start-set conjunct/S496 either decline (cost: the handoff and the seek are lost on every callout pattern, which goal 3b's comparison will see) or retire the callout half with the purity argument; flip run_ir_listing's callouts expectation in the same change.

### PREM-13  `verify` with a `consume` tail: "each site erased by its width class" makes the scan's end the wrong `pos`
- status: CONFIRMED (spec reading; no build). §4.2 L566-567 builds the `scan-end` scan from "the capture-erased DFA of the pattern with each site erased by its width class (1.8)", and §1.8 erases a `W_ANY` site to "any bytes, any length". A tail segment `c,verify,consume` (both attributes are legal together, §2.2; no §4.3 row excludes it) gives the scan language `R·Σ*`, whose leftmost-first end is the subject end (greedy any-bytes), so §4.2 step 1 calls the segment with `pos = len`, not at R's end. `a(?{c,verify,consume: return octet_match(ctx);})` on `a255x`: the reference calls the segment at pos 1; `scan-end` calls it at pos 5. §4.4's proof only covers a tail that adds nothing to the scan language ("`R` has no callout", "the scan proves the end of `R`'s leftmost-first answer"), which is true only when the tail erases to the empty string.
- severity: answer
- effort: paragraph edit
- blast radius: §4.2, §4.3 (a row or a rule), §4.4 item 2, stage 4's tests (add a `verify,consume` case or its refusal/downgrade)
- where: inline_c §4.2 L566-568, §4.3 L582-589, §2.2 L343-357
- argument: the premise that the stage-4 language rule (width-class erasure, correct for the inline hybrid's START filter) also gives `scan-end` its end is false for `W_ANY` tails.
- proposed fix: for `scan-end`, the scan is R's own machine (every tail site erased to the empty string regardless of width); width-class erasure stays the rule for the ordinary prefilter. Or add a downgrade row `consuming-tail`.

### PREM-14  `scan-end` is a second call site, against §1.2's "no other site calls a callout" and the Q2 constraint as the note states it
- status: CONFIRMED (internal contradiction). §1.2 L142-143: "One emitter function, parameterised by a BINDING ROW (1.4); no other site calls a callout." §4.2 step 1 L570-572: the hybrid's attempt loop "call[s] the tail segments in order", with its own view builder (`ncap = 1`, `caps[0] = {s, UNSET}`), outside the VM program.
- severity: design / doc
- effort: paragraph edit
- blast radius: §1.2, §4.2, the "one test population" claim of the Q2 constraint (scan-end's call path needs its own sabotage, S-IC15..17 do not cover the view it builds)
- where: inline_c §1.2 L142-143, §4.2 L570-577, Design constraint L60-63
- argument: Q2 (binding) asks for one emitter / fire contract / return table / test population. The attempt-loop call can satisfy it only if it goes through the same emitter function with the view as a parameter; the note says neither that nor the opposite.
- proposed fix: state that `scan-end`'s call is emitted by the §1.2 function with a second VIEW row (site view vs attempt-loop view), and add a sabotage row on the attempt-loop view (e.g. it passes `caps = NULL` / `ncap = 0`).

### PREM-15  GOALS lens: the goals are ranked and mostly checkable, but three of four measurable forms fail by construction or have no margin, and the default mode's cost has no goal
- status: CONFIRMED (cross-reading the findings above against architecture.md "A design states its goals, ranked, in checkable form": three to five goals, who benefits, comparison AND margin, priority order, non-goals).
  Present and good: four goals, each with a beneficiary, a priority order (1>2>3>4) with a stated tie-break rationale, non-goals, and a ruled-not-ranked constraint (Q2) kept separate.
  Defects: (a) Goal 1's population is the empty `--list-*` set and misses `features all` (PREM-11, PREM-4). (b) Goal 2's "zero disagreements" is unreachable as written (PREM-1 flags, PREM-2 textual `ncap`), and its corpus control may be vacuous (PREM-9). (c) Goal 3b depends on `scan-end`, which is either dead or unsound as designed (PREM-3). (d) The INLINE mode, which every embedded segment gets by default and which moves a DFA-eligible pattern onto the VM, has no goal with a margin: standing question 1's stage-2 card "confirms Frank's 'the only cost is the drop into vm' and nothing else is decided by it" (L79-80) is a measurement with no way to fail. (e) Sections 6 and 7 (artifact as callout, PCRE2 wrapper) serve no listed goal; they are Q6 rulings, which is fine, but goal 2 or a fifth goal should name composition so their tests have a margin to meet.
- severity: design (goals)
- effort: paragraph edits in Goals and standing question 1
- blast radius: the build lanes' briefs (they restate goals), stage 2's measurement card
- where: inline_c Goals L21-58, standing question 1 L76-85
- proposed fix: fix (a)-(c) per the findings; give the inline mode a checkable form (e.g. "a callout-bearing artifact's search time is within X of the same pattern's `--engine=vm` callout-free artifact plus one call per fire", which isolates the call-site cost from the engine change) or state the engine drop as an accepted, unmargined cost in the non-goals.

### PREM-16  Smaller premises that do not hold as written (one line each)
- status: CONFIRMED unless marked. severity: doc / speed / maintenance. effort: sentence edits.
- (a) §1.6 L249-250 "Their cost is one compare on the success path": row 10 at a `W_ANY` site under UTF-8 is a bound compare plus a guarded load-and-mask of `subject[pos+ret]` (two compares and a load), and rows 3-8 are a further range test on every return of an extern binding (gcc can fold them only for an inlined code segment). Say "a few compares, folded for inlined `W_PRED` segments".
- (b) §3.2 L471 `RX_G_<name>` "its number": pcrec supports duplicated group names (src/core/internal.h:5617-5621, the marked set's "EVERY member of the run"), so a duplicated name has no single number. Say what `RX_G_<dup>` is (refused, the first, or absent).
- (c) §5.5 L706-707 "`--list-source` stays a pure function of the file's bytes": already false for `include` (rxt_format.md §1.1 table: "the RESOLVED REAL PATH in `name` — the one deliberate exception"). Say "stays as pure as today; it verifies no pin".
- (d) §3.3 L497 `code-header` includes "after pcrec's own includes", i.e. ahead of the whole generated matcher: every macro the user's header defines then applies to pcrec's own code (`subject`, `result`, `window`, `run`, `group`, `ctx` are emitted identifiers, e.g. in rx_search_run). Since the segment definitions are already LAST (§3.1), emitting the user's includes immediately before the first segment definition confines them to the user's code at no cost. (SUSPECTED as a practical hazard; CONFIRMED that the placement exposes the identifiers.)
- (e) §1.3 L169 / §10a item 6 "costs one store per fire ... no `rx_ctx` field": see PREM-5; with `\K` the cost is a save/store/restore, or a refusal row.
- (f) §3.1 L432-435 "the artifact's bytes do not depend on the output file name": true, but they now depend on the INPUT path as typed (`#line "../x/ipv4.rxt"` vs `"ipv4.rxt"`), so the identity gate and any reproducibility claim must pin the invocation's spelling; one sentence.

## PROBED-AND-HELD

libpcre2 10.46 probes (probes/prem/p.c, s.c; 22 runs):
- Error codes as the note states: `(?{x})` 111, `(*{x})` 160, `(?Cx)` 182, `(?C256)` 138 (4/4).
- Accepted as callouts: ``(?C`c: return 0;`)``, ``(?C`c,verify: x`)``, `(?C"name")` (3/3).
- P7: `(\d+)(?C)` + `<=255` check on `1234` = `[1,4)` default, `[0,3)` under NO_AUTO_POSSESS|NO_START_OPTIMIZE (2/2).
- PCRE2 end rule: `}}` decodes to `}`, a doubled backtick to one, `{`-delimited code with inner braces decodes as §2.3 says, `(?x)` does not touch the string (4/4).
- Retention: `(a(?C1)b)+` on `abab` shows group 1 = (0,2) at the second fire (previous iteration), as §1.3 states (1/1).
pcrec CLI probes (7): every `(?C` spelling -> "(?C...) requires module 'callouts'"; `(?{` -> "unrecognized character after (? or (?-"; `--features all` -> "is not implemented yet". No corpus `.rxt` contains `(?C` (0 files; only cli/reject/ir-listing/mech scripts), so "zero movers in the existing corpus" holds for stage 1's emitted bytes (the ir_listing expectation is a test reader, PREM-12).
Code/spec facts that hold (24):
- Registry `(?C` row: `GROUP_XA_CALLOUT`, module `callouts`, `VM_ONLY`, `RF_CROSSES_ATTEMPTS`, `NO_PORT` today (registry.c:1026, :286).
- Three named-group rows share `pcrec_ngport_declare` (registry.c:928/934/963).
- `forces_registry` is generic and returns the row's own `syntax` as the why (select_engine.c:338-366): no callout clause needed.
- `VE_CALLOUT` reserved with no producer (emit_vm.c:283).
- Namespace table row 2 `callout-bindings` reserved "with its first producer" (compile.c:157); a prefix containing `__` is refused (ns_parts); no existing `<prefix>__code*` role (11 roles: bind_checks, enter, find, match_notempty, next_pos, one, one_call, one_local, retry, step, step_own).
- `rx_ctx` has exactly the 8 fields §1.2 fills; `caps` is `const ptrdiff_t (*)[2]`; the VM's `slot_values` is `ptrdiff_t[]` with the capture region first (`RX_SLOT_WHOLE_START 0` ... `GROUPk_START 2k`), and slot 1 is not written mid-match.
- PUBLISH-AT-CLOSE exists keyed by the marked set = union of `A_BREF` refs (`pcrec_bref_mark`, internal.h:5617; emit_vm.c:474-486); a group outside the set emits the old two writes.
- match_api §4¶10 rows 1-8 are as §1.6 copies them; §4¶10 already names "a callout site" as the future second producer.
- `PCREC_ERR_*` codes and `PCREC_RX_ABI_H` cross-abi `#error` guard exist as described.
- `<prefix>_match` exported unconditionally, typed `rx_matchfn`, reads `ctx->vars` (emit_vm.c:13660-13700); §3.1¶19 consumed length; §3.2¶6 search-filter skim.
- `pf_admits[]` is a declared first-match table with construct rows (backref, linked-call, var) of the shape §1.8 adds.
- The hybrid's scan uses the same DFA scan machinery/stamps as a DFA artifact (`foo[0-9]+bar` vs `(foo)[0-9]+bar`: both `DFA_PREFILTER memchr`, `DFA_START reverse-pass`); its forward machine is priority-pruned (leftmost-first end: `(x)(?:a|ab)` accepts and dies after `xa`).
- `pcrec_options` has `uint64_t flags` (bits used to 56) and a separate `features` spec, so a new member rather than a bit is consistent with [IFACE-PUSH].
- rxt_format §1.1¶2/¶2a refuse `--analysis`/`--measures` on a `pcrec` line; §1.12 `ext <consumer>` exists; an `include`d fragment holds only blocks and `include` lines.
- No environment variable injects CLI flags (getenv only for traces).
- gcc 15.2 -O2 inlines a later-defined `static` segment into an earlier caller (probe inl.c: 0 calls).
- Trigraphs: ignored under the house `-std=gnu11` (warning only); active under `-std=c11`, where a `??>` or `"??/"` mismatch is a LOUD compile error, never a silent miscompile (held, with that caveat).
- The §3.2 macro names are disjoint from all 85 `RX_*` names emitted today across 9 sample artifacts (stamps and internal `RX_SET`/`RX_SLOT_*`/`RX_R_*`).
- D38 items 1-4 and 6 match the note's citations; D38 item 7's "any spelling that reinterprets a currently-valid pattern is module-gated" is met by module `code-c`.
Totals: 22 libpcre2 runs, 7 CLI probes, 24 code/spec facts held; 16 findings (PREM-1..16).

## DONE
