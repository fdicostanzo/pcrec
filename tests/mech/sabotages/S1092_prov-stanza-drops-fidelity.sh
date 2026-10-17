#!/usr/bin/env bash
# S1092 ([MEMFN] R-24, lane r24; MF_SITE_ABI 15) -- THE PROVENANCE MAPPING
# DROPS THE BLOCK'S FIDELITY. `mf_prov` carries the answering block's `bytes`
# and `fidelity` (an UNSTATED zero, the findings vocabulary's three tokens as
# the other enumerators); pcrec's mapping, `pcrec_memfn_prov_stanza`
# (src/gen/memfn_sites.c), is the one place a stanza's `fidelity` word becomes
# the enumerator. The plant writes the UNSTATED zero whatever the block says,
# which is exactly the lie D162 add. 4 forbids in the other direction: a
# `synthesized` block read as one that declares nothing.
#
# WHERE IT IS SEEN. No artifact moves (no kit row reads the field before B3a
# and nothing on this base calls the mapping). The finder check's family L
# (tests/memfn/finder_check.py, via tests/memfn/prov_check.c) maps every token
# of the closed set read off `pcrec --list-schema` and demands its own
# nonzero enumerator, so the plant fails for each of the three. Arm memfnfinder.
SAB_ID="S1092-prov-stanza-drops-fidelity"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="memfnfinder"
SAB_DESC="pcrec's provenance mapping writes fidelity UNSTATED whatever token the answering block declares, so a verbatim, adapted or synthesized block reaches the kit as one that states none"
SAB_DOC_FIGURE="HAND-MEASURED by lane r24: see docs/dev/lanes/r24_report.md (the solo mech run of this row)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    p->fidelity = fid;'
SAB_AFTER='    p->fidelity = MF_FID_UNSTATED; (void)fid;   /* SABOTAGE S1092 */'
