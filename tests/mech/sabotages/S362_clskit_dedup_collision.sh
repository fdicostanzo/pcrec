# S362 ([CLS-TREE] S1, lane clss1) -- A WHOLE-SET PAGE TABLE WITH A
# LEAF-DEDUP COLLISION.
#
# The design's third named S1 sabotage. Every deduplicated table in the kit
# (the whole-set P2/P3 leaves and blocks, PAGE64's leaves, the atom
# signatures) goes through ONE interner, `intern_records`, where the hash
# only picks a probe sequence and EQUALITY decides a match. The plant makes
# equality compare half of each record's bytes, so two 64-bit leaves that
# agree in their low 32 bits (members only in `cp & 63 >= 32` differ) are
# merged into one, and every page that owned the second now answers with the
# first's bits.
SAB_ID="S362-clskit-dedup-collision"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="clskit"
SAB_DESC="intern_records compares only the low half of each record, so two distinct page leaves that agree in their low 32 bits collapse into one and a page table answers with the wrong leaf"
SAB_DOC_FIGURE="lane clss1 2026-09-29: see docs/dev/lanes/clss1_report.md for the measured row"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (!memcmp(x, y, sizeof *x * (size_t)words)) { idx[r] = slot[p] - 1; break; }'
SAB_AFTER='            if (!memcmp(x, y, sizeof(uint32_t) * (size_t)words)) { idx[r] = slot[p] - 1; break; }'
