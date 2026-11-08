CRITIC readiness (opus): spanarms3

Read /var/tmp/pcrec-pcrec/scratch/crit-spanarms3/COMMON.md FIRST, in full. Your lens name is
`ready`; your dir is /var/tmp/pcrec-pcrec/scratch/crit-spanarms3/ready/ and your findings file
(it does NOT exist yet; create it first) is /var/tmp/pcrec-pcrec/scratch/crit-spanarms3/ready/findings.md.
Append each finding the moment you have it, one append per finding.

The one question: is unit L1 of span_arms.md rev 2 READY TO BUILD at main 36072b2a0?

Part 1 (primary, do this first): can EVERY L1 witness fail? For each witness in §8's L1 gate
(W-L2, W-L4, W-L5, W-L6, W-L7, W-L8, W-F4, W-F5, W-A1, W-S1, W-N1, W-N2, W-RG, W-C1, W-E1, W-T1,
FACT W-S4, W-D1..W-D6, the equal-run-under-`-fno-ctx-node` checks): run `--emit-facts`, `kinds`,
`RX_DFA_SCAN` and `RX_REQ_WHY` on it at the build tree and check the §5.7 "today" cells; check the
expected answer with the oracle (on the stated subject AND every start offset); apply the rule as
written and the described sabotage, and record the observed difference (listing / stamp /
answer). A witness whose sabotaged fact stays under a floor or out of a reader's domain in BOTH
builds cannot fail: that is a finding. Plant at a real existing site where cheap (e.g. W-S4's
`reqcube_check.py` check 4 against a hand-edited listing; the -fno-ctx-node equality).
Part 2: (a) do L1's cites (file:line, functions, spec paragraphs) hold at the build tree, is it
complete (every reader of what L1 changes, found by grep: the new `dead` why token, the walk-parameter
record replacing `pcrec_req_walk`'s signature, `desc.c`'s new item combinator, CAT-SET's set change,
the `harness:` token if L1 is the first unit to build the table), and is the §12 D168 addendum
consistent with D168 as frozen; (b) is L1 SEPARABLE from L2/L3 (nothing in L1's gate or text needs
L2/L3 code, and its depends-on on E1/E2/R1 is stated correctly)?

Close with a per-witness table (witness, can fail: yes/no, observed difference) under
PROBED-AND-HELD, and a final line `VERDICT: ready | ready with listed text fixes | not ready`
with the listed fixes. Then run the lanecheck from COMMON and end on DONE.
