# VERIFIER brief, critic round inline-c (design)

Read /tmp/claude-1001/crit-inline-c/COMMON.md first: its scope mandate,
read-only rules, denylist and `timeout 60` rule bind you too. You are NOT a
critic: you re-check claims, you do not look for new findings.

Inputs: the critic files premise.md, simulate.md, slot.md, contract.md,
cost.md in /tmp/claude-1001/crit-inline-c/, and their probe programs under
probes/ (you may re-run them; copy into probes/verify/ before modifying).

For each item below, check the CLAIM the named findings make (quote the
cited lines, re-run the probe, or run the grep they name) and give a
verdict: HOLDS / REFUTED / PARTLY (say which part) / NOT VERIFIED (why).
Never trust a critic's consequence claim; check the fact it rests on.

V1  PREM-1, SIM-1: libpcre2 10.46 with NO_AUTO_POSSESS|NO_START_OPTIMIZE
    gives no match for `(?s).*(?C)x` on `axbx` with a callout vetoing iff
    start_match==0; adding PCRE2_NO_DOTSTAR_ANCHOR gives [1,4).
V2  PREM-2, SIM-2, SLOT-12: `(?:(?C1)(a))+` on `aa` (same flags): the second
    fire shows capture_top=2, group 1 = [0,1).
V3  PREM-3, SIM-4, SLOT-3: quote src/gen/emit_vm.c ~3670-3690
    (pcrec_vm_prefilter_window / nfa.erased), src/gen/emit_dfa.c ~9758
    (VM_RESEED exact row), src/ir/nfa.c NFA_ERASED_LOOK; confirm a hybrid
    clamps the anchored VM to the scan's window end (an emitted hybrid, e.g.
    `build/pcrec -p rx --pattern '(a(b)c)+d'`).
V4  PREM-4, SLOT-5, CON-1: src/parse/enabled.c `all` = union of every
    registry row's feature; `build/pcrec --features all --pattern '(?C)'`
    output; a `.rxt` block `features all` accepted.
V5  PREM-5, CON-4: `\K` writes slot 0 (RX_SLOT_WHOLE_START) in a VM artifact
    and the report reads slot 0 as the \K start (quote emitted lines).
V6  PREM-6, COST-7: rxt_format.md §1.6¶7-8 pin spelling and "pcrec checks
    neither"; analyze/sha256.c exists; no hasher under src/.
V7  PREM-7, SLOT-2, CON-8: `--no-captures` on a group-bearing pattern emits
    RX_NCAPS 1; pcrec_bref_mark's set is also --no-captures' keep set
    (src/opt/atomic.c, src/parse/mod_backrefs.c br_strip_caps).
V8  PREM-8, SLOT-1, COST-1: no shared capture-reading-consumer predicate;
    count `case A_BREF` arms and files; possessify.c bref_first arm.
V9  PREM-9: tests/axes/run_axes.sh + dump_diff.awk: a case REFUSED on both
    sides counts as AGREE; no `ext` consumer in tests/harness/run.sh.
V10 PREM-12: emit_dfa.c ~8600 and ~7841 "NO VERB AND NO CALLOUT"
    obligations; S475/S496 declared UNREACHED; run_ir_listing.sh asserts 0
    callouts.
V11 CON-2: tests/harness/run.sh compiles each block (fragment blocks
    included) with --pattern; rxt_format.md §4¶8.
V12 COST-2: src/gen/emit_compound.c callsite_rows[] exists, its rows, a
    `reserved r < 0` trap row and r==0 nomatch convention; compare
    match_api.md §4¶10 rows.
V13 SLOT-11, SLOT-16, COST-3: quote locate_finish.md FIN3/FIN4 and §1.3
    "ONE home"; compound.md §A.2 U6 / external-verifier sentence;
    compound_callout_alignment.md §13 U6.
V14 SLOT-8: the emitted shared-block comment on rx_matchfn ("traps on
    one") vs match_api.md §4¶10 row 4 and D163 addendum 6 Q3.
V15 SLOT-15: D163 addendum 6 Q1 text (one budget meter per exported call).
V16 SLOT-4: match_api.md §10.9¶1 and ¶6, §4¶4 wording.
V17 SLOT-10: src/core/internal.h ~4547 "ports carry no module fact"; one
    `(?C` registry row.
V18 CON-9: rxt_format.md §1.12 graduation rule wording.
V19 CON-5: match_api.md ASCII / -Werror / -Wbidi-chars promise; --list-source
    passes non-ASCII raw.
V20 CON-3: a lib definition reaches a target only through a call; an include
    fragment's blocks are not CLI targets (re-run probes/CON/inc).
V21 SLOT-17: D26 addendum's last sentence.
V22 SIM-6: pcre2callout(3) start_match/\K sentence (man page or
    /usr/share/doc) vs probe.
V23 SLOT-19, COST-8: lib/pcrec.h PCREC_BIT usage, free bits count.
V24 CON-13: the pcrec-bench report row for grp-callout (read-only).
V25 SIM-7: build/pcrec answers "(?C...) requires module 'callouts'" for
    `(?C256)` and `(?Cx)`.

Output: CREATE /tmp/claude-1001/crit-inline-c/verify.md (it does not exist
yet), written incrementally: one `### Vn` per item with verdict, evidence
(quoted lines or command + output), and one line on what it means. End with
`## DONE`. Final reply at most 100 words.
