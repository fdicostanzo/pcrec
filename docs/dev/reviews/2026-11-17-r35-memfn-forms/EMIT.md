# EMIT findings: crit-memfn-forms

## Findings

### EMIT-1: the deny `no-span-loop` (form I, "the escape hatch") is REFUSED at width 4095 for `[0-9a-f]{4095}` where the default compiles; r45 §3 names the wrong cap
- status: CONFIRMED. Repro: comb tree, pattern file `[0-9a-f]{4095}`, `build/pcrec -p rx --features all --window-search-width=4095 --memfn=no-span-loop -o a.c --pattern ...` -> rc=1 "pattern too large: 612695 bytes of emitted code (limit 500000)". Default (H(64)) and `--memfn=span-loop` both compile (24,013 / 15,172 C bytes; .text -O2 3,945 / 2,233). Deny at k=1000 is 157,314 C bytes (.text 30,697), so the refusal threshold is roughly k ~ 3,300 at ~150 B/position (estimate, not bisected).
- severity: design (a documented option refuses a compile the default accepts) + doc
- effort: S (doc) / M (decide what the deny promises past the cap); blast radius: widths > ~3,300 only (comb/covs2b), never width 32
- where: memfn/src/options.def span-loop row ("denied, every position is tested inline"); r45_reply rev 6 §3 "Scope", plan B bullet ("~630 KB at 4095, under PCREC_MAX_EMIT_BYTES 1,000,000"). The cap that bites is PCREC_MAX_VM_EMIT_CODE_BYTES 500,000 (limits.def:189, code bytes outside table initializers), not PCREC_MAX_EMIT_BYTES (limits.def:196).
- argument: the option row and r45 §3 "The option" sell the deny as today's text and pcrec's G1/identity escape hatch; at k >= ~3,300 it is a compile error instead. The same fact means plan B's "Form I alone keeps the cover legal at every width" is false on the combined tree (it names a 1,000,000 cap; the 500,000 code-byte cap refuses first). cards.py is NOT hit (C4 passes `--max-emit-code-bytes=4000000`, cards.py:309), but any axes/identity arm that runs the deny at width 4095 without that flag will see a refusal, not an answer. Either the option text/spec states the cap (deny past ~k=3,300 needs `--max-emit-code-bytes`), or the deny falls back; and r45 §3's cap citation is corrected.

### EMIT-2: r45 §3's named witness `\w{32}\B` does NOT move at h* = 32 (nor at 30) in this build: the E-find probe at offset 31 splits the run
- status: CONFIRMED. Repro (subject-h, `--features all`): `\w{32}\B` with `--harness=span-head=32` and `=30`: LOOPS=0; h=32 bytes == default bytes. Under the force (h=0) the loop is `j = 0 .. < 31` and offset 32 (the after side) is a LONE test after it, because wf_loop_len ends a stretch at entry `skip` (the probe position 31). `\d{32}\B` and `\d{32}` at h=30 loop `30 .. <32` (a two-position loop), at h=32 nothing.
- severity: doc
- effort: S; blast radius: the prediction text only (the predictor is a stated SUPERSET, so no red follows)
- where: r45_reply rev 6 §3 "Which sites move", "Named witnesses" and "h* = 32: only the cover kin above move"; window.c wf_loop_len (`(int)j == skip` ends a stretch).
- argument: the doc's re-derivation says at h* = 32 the cover kin move; in this build no site in the sample moves at h >= 31 at width 32 (13 cover sites with force loops, max loop end 32 exclusive). Harmless to answers, but the "named witness" a reviewer would use to see a move at 32 never moves; the doc should say the probe position splits a run (and the predictor may list it as predicted-not-moved).

### EMIT-3: the minimum loop length "two or more" is an unlabelled tuning constant (D149); it emits two-position loops
- status: CONFIRMED (emission); the speed cost is SUSPECTED (no timing allowed). Repro: subject-h, `\d{32}`, `--harness=span-head=30` -> `({ size_t rx_mf1_j = 30; for (; rx_mf1_j < 32; rx_mf1_j++) if (!(...)) break; rx_mf1_j == 32; })`.
- severity: speed / doc
- effort: S (label it CHOSEN/UNMEASURED, or derive it); blast radius: every H(h) with h < k at a stretch's tail, and every force-arm compile
- where: memfn/src/window.c wf_loop_len (`return j - i >= 2 ? j - i : 0`), the forms comment ("two or more consecutive offsets"); kit.h KIT_SPAN_HEAD_MAX's comment ("a loop takes two positions") treats it as definitional.
- argument: D149 / memory suspect-tuning-constants: a cut-over below which inline is used is exactly a tuning constant. Two lone range tests vs a loop with an induction variable and back-edge is a measurable choice; the cards' grid measures h, not the minimum stretch, so this number is neither measured nor labelled.

### EMIT-4: opt_has re-implements kit_opt_denied's comma tokenizer (third copy with mf_opts_check)
- status: CONFIRMED by reading. memfn/src/options.c:73-86 (kit_opt_denied) and :90-99 (opt_has, new) are the same `strchr(p, ',')` walk differing only in the compared token; mf_opts_check (:52-71) is the third.
- severity: maintenance
- effort: S; blast radius: options.c only
- where: memfn/src/options.c opt_has / kit_opt_state
- argument: guide coding.md §4 Q4 (variations looped, not inlined N times) and §4.1 (common extract first). One helper `opt_token(opts, prefix, name)` (prefix "no-" or "") serves both; kit_opt_denied becomes `opt_token(opts, "no-", name)` and kit_opt_state's force test `opt_token(opts, "", name)`.

### EMIT-5: the valued lever is a special case beside the kit_levers table, in a predicate-shaped helper that writes state
- status: CONFIRMED by reading (maintenance/design, no behaviour defect found)
- severity: maintenance
- effort: S-M; blast radius: compose.c mf_lever, kit.h
- where: memfn/src/compose.c lever_span_head + mf_lever (subject diff @@ -1623); kit.h KIT_LEVER_SPAN_HEAD
- argument: (a) lever_span_head is documented "1 iff `name` is that lever" (a predicate) but also sets art->levers, art->span_head and *bad: a side effect inside a predicate, the shape critics flag. (b) mf_lever now has two mechanisms: the name->bit table `kit_levers` and a hand-coded prefix match ahead of it (kit addendum "One table per slot"; memory general-mechanisms-not-special-cases). The general form is a lever row carrying an optional value parser/range (or a `valued` column), so the next valued lever is a row, not a second pre-table branch. Low priority: one valued lever today.

### EMIT-6: cli/main.c validates `--harness=span-head=` itself with a bare 4095, while its comment says the kit validates; the two parsers disagree on spellings
- status: CONFIRMED by reading
- severity: maintenance
- effort: S; blast radius: cli/main.c only (test-only lever)
- where: cli/main.c cli_parse `--harness=span-head=` branch (comment "N is validated by the kit, mf_lever"; code `n > 4095`)
- argument: the range is the kit's KIT_SPAN_HEAD_MAX = MF_WREACH - 1 (kit.h); the CLI hard-codes 4095 (a second home for the number; it will silently diverge if MF_WREACH moves; limits_check does not see an inline literal). strtoul also accepts `+5`, ` 5`, `-0`, which the kit's strict digit loop would refuse, but the CLI re-prints `%u` so the kit never sees them. Either let the kit be the one validator (pass the text through, report mf_art_error as the CLI error) or use MF_WREACH - 1 and drop the "validated by the kit" claim.

## PROBED-AND-HELD


- **Zero-mover at width 32 (THE claim): HELD.** BASE vs SUBJECT default vs SUBJECT deny, byte for byte (same basename a.c, `--features all`): 120 compiled corpus patterns (150 sampled: 20 hand-made cover kin incl. `\w{32}\B`, `\W{32}\B`, `\d{32}\B`, `\B\w{32}`, hex32/31, uuid, `(?i)[a-f]{32}`, `[^\n]{32}x`; 90 of the 126 rxt patterns with a count >= 8; 40 random class/count patterns; 30 refused by pcrec in all arms alike) -> 0 base!=subject, 0 subject!=deny. Variants on 10 cover/run shapes x {`-i`, `-e utf8`, `-fmemfn-simd=x86-64-v3`} x {base, subject, deny} -> 0 diffs (30 pattern-cases). 8 designed pre-check/reseed shapes (`[a-z]+[0-9]{30}z`, `(?:foo|bar)\d{31}`, `[0-9]{32}|[a-f]{32}`, ...) -> 0 diffs, and no kit loop even under the force.
- **The equivalence argument: HELD.** Under the FORCE (h = 0) over the same 150, only 13 sites loop, ALL `cover` route; the largest loop end is 32 (exclusive), i.e. the last looped offset is 31; no pre-check part, reseed or prefix site in the sample took a loop at width 32. wf_loop_len starts a loop only at an offset >= h, so H(64) cannot loop below offset 64; with the largest stated offset 32 (the after side, observed: `s[c + 32]`) nothing moves. The probe position splits runs further (EMIT-2), so the true head bound at width 32 is lower than 32.
- **Comb widths 33..4095 (moves expected): HELD apart from EMIT-1.** 10 shapes x {default, deny, force} (`--window-search-width` 32/64/128/4095): default == deny bytes where k <= 64 (hex32@32, hex40@64, hex64@64, hex66@128: the after/probe split keeps them inline); moves exactly where a stretch reaches >= 65 (`\w{100}\B` 64..98, hex500 64..498, hex1000, hex4095 64..4093, `[0-9a-f]{80}-[0-9a-f]{80}` two loops split at the `-`); `a{4095}` never loops (one-member set -> run compare, all arms identical). Sizes (gcc -O2 .text / -march=native .text): hex500 default 3,944/4,008, deny 16,200/16,216, force 2,232/2,312; hex1000 default 3,945, deny 30,697; hex4095 default 3,945, deny REFUSED (EMIT-1), force 2,233. Default C size is flat (~24 KB) past k = 500: the 64-position inline head costs ~1.7 KB .text over L per site.
- **Loop codegen: HELD.** `gcc -O2 -S` of hex500 default: the loop is 7 instructions per iteration (movzbl, lea, cmp, jbe, sub, cmp, ja), not unrolled, early exit straight to the fail label; the statement expression's `j == end` folds away; no extra register pressure visible (one induction register). `-march=native` gives the same shape.
- **wf_span_head precedence / lever range / names: HELD.** deny > force > lever > 64 as the option row says; lever 0..4095 refused past; `_j` name per handle (nested statement expressions shadow safely). D149 label on WF_SPAN_HEAD present ("UNMEASURED DEFAULT: CHOSEN grid top").
- Budget note: about 1,150 pcrec compiles (over the ~800 cap: a first 600-compile pass hashed per-arm include lines and was redone for the byte compare; its force-loop facts were kept) plus 20 gcc object builds; no timing, no make, all writes under EMIT/.

CRITIC COMPLETE
