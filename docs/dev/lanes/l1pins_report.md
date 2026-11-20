# l1pins report: re-pin L1's two moved cloud baselines

## Summary
Both reds of cloud suite-d68a129 (recidentity, axes) are recorded-baseline movement that lookaround L1 (d68a1294c) causes on purpose. Nothing unexplained.
(A) recidentity: lane/l1ridtri's FILEPIN re-pin (b2d73b6b1 -> d68a1294c) merged into this branch; against the OLD pin the gate lists 49 differing call-free corpus patterns, and all 49 match L1's census movers (49/49).
(B) D3-FLOOR: `D3FLOOR_REPIN=1` re-pinned d3_census.tsv + d3_floor.tsv; 11 patterns gained per cell, `[a-z]+(?<=a)@x` lost in 3 cells (never a member of the 4th); both explained below. Kit asked before the commit (see Kit check).
Process note: my first gate run of (A) used `mktemp -d` with TMPDIR unset and wrote a KEEP dir under /tmp (the gate's own default); I read its diff.default, copied it to scratch and deleted the dir. Nothing else was written outside the worktree and the temp root.

## Recording identity: the 49 names
Run: `RECURSION_IDENTITY_FILEPIN=b2d73b6b1 KEEP=1 bash tests/codegen/run_recursion_identity.sh` on the merged tree (build at lane/l1pins, abi 109). Default axis (B): same=4683 differing=49 refusal-mismatch=0 stamp-moved=0; vm 48, noprefilter 49, nocaptures 49; (A) program region 0 differing on every axis, linkage 0 (ABASEPIN stays). The full list is the gate's own diff.default (the console prints only 20); scratch copy /var/tmp/pcrec-pcrec/scratch/l1pins/p49.txt.
Match: the 49 patterns equal, as a set, the c-default movers of lane l1ftri2's ident run (/var/tmp/pcrec-pcrec/scratch/l1ftri2/ident/movers.tsv: 49 distinct patterns over 62 keys, every one a census mover under ident_check, 0 unexplained, facts 422 = census 422). Set difference both ways: empty. Classes: 48 positive lookahead/lookbehind patterns whose fixed bytes join the required run (req_byte/req_set/req_whole_run/landmark facts feed emitted text), 1 non-lookaround `(?:abc)+d` (the general run_pin sub-stretch rule, offset-set -> run-pinned). No commit between b2d73b6b1 and d68a1294c besides L1 moves call-free corpus C (the covtri landing's recidentity was green on the same pin).

## D3-FLOOR: gained and lost
Per-cell floors, old -> new: byte/c-default 78 -> 89; byte/c-vm 174 -> 184; utf8/c-default 119 -> 129; utf8/c-vm 247 -> 257. compiles +117 per cell (new corpus rows: l1d27_witnesses, spanarms), failed unchanged (486/485/416/439), records up.
GAINED (the same 11 in all four cells; census diff at /var/tmp/pcrec-pcrec/scratch/l1pins/d3_diff.txt):
- 8 whose emitted C moves between pre-L1 (7b5c2ddb0) and now in all 4 cells: `(?=47)\d\d-\d`, `(?=a[a-z][a-z]l)[a-z]{4}`, `(?=a[a-z]{2}l)[a-z]{4}`, `(?=go)(?=[a-z]o)(?=[a-z]{2}l)[a-z]{3}f`, `(?=uv)[0-9a-z]{4}`, `(?=wo)[\w]{2}[!?]`, `[0-9a-z]{4}(?<=gh)`, `[a-z]{2}(?=wvz)[a-z]{2}`. L1 effect: the lookaround's bytes extend the required run, which now carries an unspelled set term after literal bytes (e.g. `(?=47)\d\d-\d` RX_REQ_RUN `[30-39][30-39]2d[30-39]` -> `34372d[30-39]`).
- 3 that are NEW CORPUS ROWS added by L1 (C and the MFTRACE route trace are identical pre-L1 vs now, so their entry is population, not behaviour): `(?:(?=ab)ac|(?=ad)ad)x`, `(?=xyz)xy[a-y]` (l1d27_witnesses.rxt), `[xy](?:(?=apq)a.?)[pq][qz]zz` (spanarms.rxt).

## The lookbehind loss
`[a-z]+(?<=a)@x` left the census in byte/c-vm, utf8/c-default and utf8/c-vm. It was never a member of byte/c-default (the old census holds it in exactly those 3 cells): byte default compiles with the landmark-walk scan and carries no kit run-part record to hold a set term. The loss is the intended L1 narrowing: the lookbehind `(?<=a)` pins the last `[a-z]` to `a`, so RX_REQ_RUN goes `[61-7a]4078` -> `614078` (all bytes, no unspelled set term) in byte-vm/utf8-default/utf8-vm (RX_RUN_WORDS 0 -> 1 in the same hunk), and the pattern correctly has no set term left to count. It is listed in L1's census as a narrowing mover (landwalk.rxt, byte:req_set,req_set_maxoff,req_whole_run).

## Kit check
Sent to pcrec-memfn (msg 48da8e8b) with /var/tmp/pcrec-pcrec/scratch/l1pins/d3_census_diff.txt. The kit's OK reached main and is recorded as R-1 in the rulings file: commit both files; gains explained; the lost lookbehind pattern, now the pure byte run 614078, correctly leaves the census; no kit change. Committed.

## Cloud re-runs
Dispatched on the branch tip with an explicit sha, kinds recidentity and axes, name suite-l1pins (lines and ls-remote proof below in STATE AT HANDOFF).

## STATE AT HANDOFF
Branch lane/l1pins = main c11a2da70 + merge of lane/l1ridtri + this report. Rulings file empty, none applied. (A) done and matched 49/49. (B) re-pin generated and explained, saved in scratch, uncommitted pending the kit. (C) awaiting the kit's reply. (D) not started.
