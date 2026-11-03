#!/usr/bin/env bash
# S1856 ([MEMFN] span_pick unit 1g fix lane sp1gfix; MF_SITE_ABI 22) -- A KIT
# ROW READS `mf_akind.digest`. The analysis object's digest is the payload's
# identity, handed so the kit's trace can name it (span_pick row 1); NO kit
# row may decide on it (D186 add. 2: the kit does not tell a default table
# from a bundle). `kit_byte_rate` is the one place the kit reads the object;
# the plant makes it return no table for an odd digest, which moves a
# rate-reading site's decisions with the digest alone.
#
# WHERE IT IS SEEN. No artifact moves (pcrec's digests are fixed per table).
# The finder check's family L (tests/memfn/finder_check.py): the static scan
# "no memfn/src file names `digest`" and the render loop over the rate-reading
# sites (pre-lead, pre-lead-run, pre-opt), which differ across digests 0 and 1,
# with their reach shown against the no-object render. Arm memfnfinder.
# Successor of S1092 (the provenance mapping, retired with the stanza).
SAB_ID="S1856-kit-byte-rate-reads-digest"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="memfnfinder"
SAB_DESC="kit_byte_rate returns no table for an odd mf_akind.digest, so a kit row decides on the payload's identity and the same rates render differently under a different digest"
SAB_DOC_FIGURE="HAND-PLANTED by lane sp1gfix: finder_check L goes RED (sp1gfix_report.md); the matrix run is the manager's gate shard."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            return an->kinds[i].present == MF_KIND_PRESENT
                 ? (const uint32_t *)an->kinds[i].payload : NULL;'
SAB_AFTER='            return an->kinds[i].present == MF_KIND_PRESENT && !(an->kinds[i].digest & 1)   /* SABOTAGE S1856 */
                 ? (const uint32_t *)an->kinds[i].payload : NULL;'
