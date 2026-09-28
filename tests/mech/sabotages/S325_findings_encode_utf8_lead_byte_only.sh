# S325 — [FINDINGS] B5 `encode-utf8` COUNTS ONLY A CODE POINT'S FIRST BYTE
# (src/core/findings.c, `pcrec_find_derive_counts`): each code point's count
# lands on its lead byte alone, so every continuation byte (0x80-0xBF) reads
# as never seen — exactly the utf8 byte-rate B5 exists to supply, gone
# wrong in the direction that makes the COMMONEST non-ASCII bytes look
# rarest.
#
# INVISIBLE ON THE SHIPPED BUNDLES: `log` and `weblog` are pure ASCII, where
# every encoding is one byte, so their digests and stamps do not move (§12
# (b) stays green). The detectors are the derivation oracle over code points
# of every UTF-8 length (tests/findings §12 (c), against Python's own codec)
# and the Latin-1 sample's 0xC3 count (§12 (d)) — which is why they exist.
SAB_ID="S325-findings-encode-utf8-lead-byte-only"
SAB_FILE="src/core/findings.c"
SAB_SUITES="findings"
SAB_DESC="pcrec_find_derive_counts's encode-utf8 arm adds a code point's count to its lead byte only, dropping every continuation byte — invisible on the ASCII-only shipped bundles, caught by the derivation oracle and the Latin-1 sample"
SAB_DOC_FIGURE="findings: §12's 'via encode-utf8' derivation check and the Latin-1 0xC3 check red; every other findings check green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S325."
# [MECH-REACH] the site answers: a non-ASCII cpfreq block derives through it
# (the listing's utf8 row answers from the cpfreq block via encode-utf8).
SAB_REACH='"$PCREC" --list-analysis weblog | awk -F"\t" "\$1 == \"byte-rate\" && \$2 == \"utf8\" { print \$5 \"/\" \$6 }"'
SAB_REACH_EXPECT="cpfreq/encode-utf8"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            n = pcrec_utf8_encode(cps[i].cp, b);'
SAB_AFTER='            n = pcrec_utf8_encode(cps[i].cp, b), n = 1;   /* SABOTAGE S325 */'
