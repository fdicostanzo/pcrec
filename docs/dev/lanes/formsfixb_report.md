# formsfixb report — code review r35 F12-F17, F20, F23, F29 (G2's coverage of the span forms, the lever's parse, one tokenizer)

Lane formsfixb (opus), 2026-11-17, branch `lane/memfn-formsfixb` cut from `lane/memfn-forms` @ 7506bca30.
Review of record: the kit's code review r35 of lane forms (2026-11-17, R-45 plan A; not in this tree, the kit
manager holds it) and its RULED dispositions; R-45 plan A in memfn/docs/requests.md.
Rulings file `docs/dev/lanes/formsfixb_rulings.md`: R1 applied (the twins derived from the kit's bounds).

## Summary

- G2's window family now reaches the regime the shipped default H(64) loops in, and checks every loop it renders:
  - three new streams, each on its own RNG so no older site moves: REPEATED-CLASS sites at every finite grid head
    (one in three MIXED: a second WIDE class from h + 1 or h + 2), STRADDLE sites (every family's own facts plus
    a one-class stretch across the head, h + 1..h + 4; 448, about 7 per (family, head)), and WIDE REPORT sites
    (k in 1..128, stated as spans of G2W_MAXPOS);
  - LONG ROWS of 500 and 1024 positions (1024 = the longest stretch one alternative states in this tree;
    4095 after the [COVER-CAP] stage 2 raise, by arithmetic), answered by G2's own byte loop, in three states in
    the default pass: the head, the deny (no loop anywhere: the deny's witness past 64) and the force;
  - the generator reads every loop (at or past the head; one WIDE core set over tested entries) and, where the
    form's skipped entry is known, PINS each loop's start and end exactly;
  - the driver BREAKS every stated stretch deterministically: its first two and last two entries, the head's
    three, the stop's sides, and a mixed stretch's class boundary (class swaps);
  - one pass per finite grid head (0 1 2 4 8 16 24 32 64), every (family, head) pair floored, the mixed sites
    too; head 0 also runs ASan+UBSan, and the default pass (sanitized) now loops.
- The twins are DERIVED (ruling R1): G2W_MAXPOS = min(128, MF_WSPAN_POS), G2P_MAXRUN = min(64, MF_WSPAN_POS),
  the long row = min(4095, G2W_MAXSPAN x G2W_MAXPOS); G2W_REACH 256. Here 32 / 32 / 1024; under the raise
  128 / 64 / 4095. Each `_Static_assert`ed against the kit's bound; printed in the runtime record
  (`G2W twins ...`, `G2P twins ...`).
- The lever `--harness=span-head=N` takes decimal digits only (`-0`, `+8`, ` 8`, `` refused), N up to
  `MF_SPAN_HEAD_MAX` (memfn.h, `MF_WREACH - 1`; the kit's own bound, which compose.c now reads too).
- One `--memfn=` tokenizer (`opt_next`) for `mf_opts_check`, `kit_opt_denied` and `kit_opt_state`.
- Plants S3280-S3284 added; S3276, S3277, S3279's detectors re-described (now deterministic).
- Movers: none (see Validation).

## Fixes

| finding | fix | commit |
|---|---|---|
| F12 | G2W_REACH 256; G2W_MAXPOS / G2P_MAXRUN / the long row derived from the kit's bounds (R1: 32 / 32 / 1024 here, 128 / 64 / 4095 under the raise), each `_Static_assert`ed; REPORT k in 1..128 (wide REPORT stream); every family at h-1..h+4 for every grid head (straddle stream); long rows 500 and 1024 (4095 under the raise); runtime record `G2W twins` / `G2P twins` and per-head walls | e957797b1, ab4625f53 |
| F13 | one pass per finite grid head (0 1 2 4 8 16 24 32 64); a floor for every (family, head) pair, and the default's | e957797b1, ab4625f53 |
| F14 | the generator's exact pin of each loop's start and end (where the skipped entry is known: E-find's dropped stop, the floor's none), floored per head (`PIN_FLOOR_<h>`); sibling plants S3280 (`<` read as `<=`) and S3282 (the lever read as 0) | e957797b1, ab4625f53 |
| F15 | the long rows under `no-span-loop` must loop nowhere (8 deny witnesses at widths 500 and 1024, floored); plant S3281 (deny ignored). The cards.py arm-I zero-loop assertion is formsfixa's file: NOT done here | e957797b1, ab4625f53 |
| F16 | the repeated-class stream's MIXED variant at every head, counted (`mixed=`) and floored per head | e957797b1, ab4625f53 |
| F17 | deterministic breaks at every stated stretch's edges, the head's three entries, the stop's sides, the class boundary, and the long rows' breaks; counted (`G2W breaks`) and floored; plant S3283 (a looped entry reads its neighbour) | e957797b1, ab4625f53 |
| F20 | the default pass (ASan+UBSan) now loops (the forms streams and the long rows: 16 looped long rows); the head-0 pass also runs ASan+UBSan | e957797b1 |
| F23 | `cli/main.c`: digits only, bound `MF_SPAN_HEAD_MAX` (memfn.h, `MF_WREACH - 1`; kit.h's `KIT_SPAN_HEAD_MAX` removed, compose.c reads the same constant); the comment's "the kit validates N" claim dropped | a6d435ea7 |
| F29 | `options.c` `opt_next`, the one tokenizer of `mf_opts_check`, `opt_has` (`kit_opt_denied`, `kit_opt_state`) | a6d435ea7 |

Deviations, each with its trigger:
- G2W_MAXPOS and G2P_MAXRUN are 32, not 128 and 64, in THIS tree: MF_WSPAN_POS is 32 until the [COVER-CAP] stage
  2 raise, and a twin past it states what the kit refuses. They are derived (R1), so the combined branch
  (lane/covs2b, MF_WSPAN_POS 4095) runs 128 / 64 with no edit. G2 reaches past offset 64 here by stretches of
  several spans. Constants checked for the raise: G2W_REACH 256 <= MF_WREACH 4096; the long row's offsets
  0..4094 < MF_WREACH; G2W_MAXSPAN 32 x 128 >= 4095 (32 spans <= MF_WMAX_SPAN 32); the driver's long subject
  `LONG_SUBJ` 4112 >= 4095 + the 5 + 3 offsets it adds; `G2P_RUNCAP` 64 sizes the presence sites' arrays. None
  blocks it. Not run on the raised tree (not in this lane's scope).
- The long row is 1024, not 4095, here (the same bound; 4095 under the raise).
- An EMPTY set counts as WIDE (kit_pos_class_of/shape), so wf_loop_len loops an empty-meet stretch; answer-neutral
  (no subject byte passes it either way). G2's reading accepts it. Kit doc note for the manager: window.c's span
  forms comment could say "WIDE includes the empty set".
- The default pass pins no site exactly (G2 does not know the kit's shipped head, an internal `WF_SPAN_HEAD`);
  head 64's pass pins the same sites at the same head (`PIN_FLOOR_64`), and the default and head-64 loop counts
  are equal.

Doc lines for formsfixa (its files):
- cli/CLAUDE.md, the harness option (12): "N in 0..4095" -> "N decimal digits only, 0..MF_SPAN_HEAD_MAX
  (memfn.h, MF_WREACH - 1)".
- memfn/tests/CLAUDE.md, the `run_g2_win.sh` line: "~25 s alone" is now ~150 s on the dev box (niced); new env
  `G2W_RC_SITES`, `G2W_ST_SITES` (448), `G2W_WR_SITES` (60), `G2W_FORMS_ONLY=1`, `G2W_HEADS` (default all
  nine finite grid heads), `G2W_SPAN_HEAD`; plants S3280-S3284 (mech arm g2win). Detail is in memfn/tests/NOTES.md.
- r45_reply.md §3 "Answers, controlled by G2": the twins derived (R1), 32 / 32 / 1024 in a tree before the raise.

## Validation

All local, niced, at most -j4 / PROCS=4, each under `gnutimeout`, on the dev box, at ab4625f53 (the report,
the history line and the g2_units.tsv weight committed after it; none is read by a check below except the
weight, a balance input).

| check | verdict |
|---|---|
| `make strict` | rc 0 ("whole tree compiles clean with -Werror -Wshadow") |
| `make test-codegen` | rc 0 (202 s) |
| `make test-registry` | rc 0 (29 s) |
| `make test-rxtsource` | rc 0 (77 s) |
| `make test-memfn-finder` | rc 0 (68 s) |
| `make test-memfn-link` | rc 0 (3 s) |
| `make test-resource` | rc 0 (278 s; absorbs 0) |
| `make test-memfn-g2` (quick) | rc 0, checks failed 0 (959 s at G2_JOBS=4); window 27332 passed, traced 19072 passed |
| `make test-memfn-g2-full` | rc 0, checks passed 446420836, failed 0 (2502 s) |
| `run_g2_win.sh` alone | 27332 passed, 0 failed; ASan+UBSan default pass 6492 passed 0 failed (it loops: 16 long rows, the forms streams); head 0 ASan+UBSan green |
| `cloud_mech_check.sh` | PASS: 90 shards hold the 1320 sabotage ids exactly once (table regenerated, `--measured --slots 30 --waves 3`) |
| emit_sweep `--ref 7506bca30` (full corpus) | DONE rc 0; movers 0 on every stream (c-default, c-vm, emit-ir-vm, facts, emit-ir-auto x4, stderr, composition, dumps); argv population 7071 |

Sabotage rows (`run_sabotage_matrix.sh S3276 .. S3284`, PROCS=2 JOBS=2): `== mech run COMPLETE: 9 rows
(unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0) at ab4625f53`:
- S3276-span-loop-end-short: g2win:1331fail/17737pass DETECTED
- S3277-span-loop-mixed-sets: g2win:264fail/18804pass DETECTED
- S3278-span-loop-force-ignored: axesmemfn:4fail/396pass DETECTED
- S3279-span-head-lever-ignored: g2win:96fail/18972pass DETECTED
- S3280-span-loop-head-late: g2win:34fail/19034pass DETECTED
- S3281-span-loop-deny-ignored: g2win:2fail/19066pass DETECTED
- S3282-span-head-lever-read-as-zero: g2win:23fail/19045pass DETECTED
- S3283-span-loop-reads-next: g2win:1291fail/17777pass DETECTED
- S3284-span-loop-short-past-64: g2win:204fail/18864pass DETECTED

G2 runtime record (the dev box, niced, alone): `run_g2_win.sh` 103 s at 7506bca30 -> 151 s here (per head pass
5-7 s, head 0 with ASan 16 s; the default pass's ASan build is the bulk: the long rows cost -g's variable
tracking ~100 s of compile, so the ASan build is now -g1, 35 s). The quick unit `win` (runs it plain + traced)
reweighed 54 -> 79 in memfn/tests/g2_units.tsv (x 151/103, labelled); under the table's rule (total/8 = 115);
`g2_parts.py predict` N=8 max/min 1.07. The record prints `G2W twins maxpos=32 long=500,1024 reach=256
(MF_WSPAN_POS 32, MF_WMAX_SPAN 32)` and `G2P twins maxrun=32 (MF_WSPAN_POS 32)`.

Loop populations measured (seed 20261022), loops per family at head 0 / 8 / 32 / 64: parked 33/25/14/5,
report 41/31/16/8, repeated 80/63/35/14, mixed 27/25/16/9; exactly pinned sites 302/224/128/55; breaks
2756/3499/2797/2557. Floors ~90 % of each, at least 1 (run_g2_win.sh's MEASURED block).

## STATE AT HANDOFF

- Rulings: last entry applied R1 (formsfixb_rulings.md).
- Branch tip: TIP_PLACEHOLDER.
- OWED: none
