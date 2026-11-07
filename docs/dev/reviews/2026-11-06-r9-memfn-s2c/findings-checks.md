# findings — checks — memfn-s2c
Method: kit checks run as `python3 -I finder_check.py` against scratch roots (kit sources built into plain+traced fx, my driver `checks/bin/runchk.sh`); baseline 1027 passed / 0 failed. Slot plants in scratch copies of slot/, dry runs only (J2, J3), one at a time. No denylisted file read.

## Findings

### CHECKS-1 — CONFIRMED — severity answer — effort S — blast: every timed find/cmp cell
The answer gate runs only each arm's `_gate` function; the `_time` function that is actually timed is never checked against the planted count. link.py WRAP_FIND/WRAP_CMP hand-write two separate loops per shape; `_time` returns k (= the hit count) but nothing compares it.
Repro: copy slot/, patch link.py WRAP_FIND `_time` loop `p < n && step(...)` to `p < n / 2 && step(...)`; `SLOT_TREE=$T python3 -I run.py dry J2 RUNDIR s2c-dry` -> rc 0, "== s2 GATE ok: 4 arms, 12 pools, 0 misses". The timed loop does half the work, the gate and all five slot sabotage rows stay green (SILENT-MOVE). Expected: GATE MISS.
Fix: in drv.c gate also call `a->time(...)` and require its return == the planted count (find: k = count; cmp: k = count; null: nc). Add sabotage row (l3).

### CHECKS-2 — CONFIRMED — severity answer (vacuous gate) — effort S
The gate's population is printed but never asserted. Repro: patch link.py arm_entry to emit nlen 0 (`% (a.name, kind, sym, sym, 0, lens, ...)`); J3 dry -> rc 0, "== s2 GATE ok: 18 arms, 0 (arm, length) pools, 0 misses". A gate that checks nothing prints ok. Fix: run.py gate() / drv `gate` compares pools to sum(len(a.lengths)) from plan.py (and arms to the plan's job size); floor it (K35).

### CHECKS-3 — CONFIRMED — severity maintenance — effort S — blast: S2d/S2e producer reads deps
Check C's card guard checks only that `form` is the first dim of a card whose deps contain `kit:form.`; it does not check what the deps name. Plants, all rc 0, 1027 passed: (a) kit-grid@3 find_byte/find_hit deps `kit:form.walk` -> `kit:form.wlak`; (b) verify_cmp deps cut from `settest;rc-words;rc-memcmp` to `settest` only; (c) an invented card `zzz@3 form ... kit:form.nonesuch` -> count 18, green. Also the reverse direction is unguarded: a new form-keyed card with deps `-` is not counted. The floor 17 equals today's exact population, so a deletion or a respelled dep goes red (verified: deleting find_hit@3 -> "16 cards ... under the floor 17"; S2931 red) but every card added later gives one slot of silent slack. Fix: resolve each `kit:form.<id>` dep (non-template) through FORM_IDS / `fx --hash` FORM lines, and pin deps per @3 card to the design's list; make the floor an equality or bump it with each added card.

### CHECKS-4 — CONFIRMED — severity maintenance (vacuity risk) — effort S
R-MS3's rename fixture is never asserted to have renamed anything. Plants in arm_fixtures.c: hash_renames reduced to a non-matching entry, and the `mf_` branch disabled (`else if (0)`): rc 0, 1027 passed. A decayed `rename_idents` leaves "rename keeps the hash" trivially true. Today it works (every canonical text contains subject/pos). Fix: emit the renamed text's hash-of-raw-text and require != the original text for every id.

### CHECKS-5 — SUSPECTED — severity design/low
run.py `run` never re-runs the gate or re-checks placement; the gate runs on launch 1 and ctl only in `dry` (launches 2-7 link different pads, same sources). `drv addr` (runtime addresses) is built but no python reads it, so the "placement read at run time" is never compared to the nm values. Confirm: grep shows no caller of "addr". Not wrong today (PIE keeps mod 4096).

### CHECKS-6 — low — non-canonical instances
Rename/edit (R-MS3) fixtures exist only for each id's canonical instance (hash_edits keyed by id). settest c1/cn and rc-words w1/w3 get distinctness + class-measure checks only. A normalization bug that only bites their texts passes. Low.

### CHECKS-7 — low — message
Deleting "V1" from arm_fixtures ids[] reports "mf_form_hash(V1) resolves before its step B4" (form.get default ("0",) reads as resolves): red but the wrong reason. Same for any LATER_FORMS id.

## PROBED-AND-HELD
- S2930 (planted copy): LOUD, 3 fails, incl. "form instances hash one text: walk - = pair -" = the stated reason; also pair row PAIR missed and pair edit; matches the row text.
- S2931: LOUD, 1 fail, the card guard's own message (first dim 'cls'); stated reason true.
- S2932: LOUD, 3 fails (own format-1 digest 5c77.. vs b3ea.., generate.py --check, --list-measurements; ks_ref too when only `format 2` is set). Digest is format-sensitive in ks_ref, own digest recomputed from rows: independent.
- slot/sabotage.sh run once: control green, j j2 k l1 l2 all DETECTED, each with the expected text (cross-launch 64 draws; per-launch 64 draws; CELL-TEXT MISMATCH ctl d767.. vs bc7b..; count 0 vs 4096; found 4096 sum differs fnv differs).
- Answer gate, count+sum-preserving wrong answer (alternate +1/-1 on hits, E even): caught by FNV (found 4096 sum 2148003840 both; fnv 2456.. vs d5f7..): 256 misses over J3's 18 arms.
- Linked .text equality: twin compiled -O0 -> "linked .text of ...#b differs" (LOUD); -O3 -funroll-loops compiles identically here (SAME, not a gap).
- ctl sha: one-byte flip at offset 4500 -> "ctl's sha-256 ... is not the window's" (LOUD). (Offset 200 was header padding: no change, SAME.)
- Entry table plants (formhash.c): settest c1 text = c2 (dup + measure red), canon swap (3 red), delete cn (2 red incl. floor 10), invent c4 (red), w3 shortened (measure red). FORM_IDS-side lists all go red on deletion/invention; floor 10 = exact instance count.
- arm_fixtures plants: ids[] delete rc-words (3 red), hash_edits delete libc (2 red), edit no-op (red), invented ids[] entry "bogus" (SAME, benign).
- Card floor: delete find_hit@3 -> 16 < 17 red; invented well-formed form-first card -> 18 passes (intended floor).
- libc/pair/settest/... hash is not pinned to an independent literal (only walk, via TEXT base); a libc emission edit in pffind.c moves the hash but is caught by byte1t/hat1/mline site-text checks (3 red). Walk and libc hashes equal BASE's (bc7b2e02f06fe955, d7672e87c1dd6d97).
- Detector independence: k's check (TU span hash vs form hash) shares formhash.c with the key by design (cell text == key text); a wrong entry-table row is caught by finder_check B (written from the design), not by the slot. The gate's expectation (gen.c, own FNV) is independent of the wrapper's inline FNV; members come from `--facts` (same entry table as the text), so a wrong member set is consistent in both (walk digit-set edit "0-8": SAME everywhere, the walk hash does not cover the table).
- ~35 scratch builds + 7 dry runs, no pattern compiles.
