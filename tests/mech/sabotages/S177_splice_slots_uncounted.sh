# S177 — [DD-14 wave G] THE SLOT COUNT MISSES A SPLICED SITE'S SAVE BLOCK.
#
# K27's CLASS, which is `vm_count_slots`' own header warning and which design
# §4.4c already had to be corrected about once: "the first version said LEXICAL
# ONLY and it was WRONG — the consequence is an out-of-bounds slot write".
# S-SR19 defends that for the CALLEE REGION; this row defends it for the eighth
# slot family wave G added.
#
# A SPLICED SITE ALLOCATES `|W|` SLOTS OF ITS OWN (`SLOT_SPLICE_SAVE<n>`),
# because it has no call frame and therefore no trail anchor to park the
# caller's values against — `vm_splice`'s header derives why. `RX_NSLOTS` has to
# be known before `rx_run_state` is emitted, so the count comes from the
# pre-pass and the emitter assigns from it; the two disagreeing is a write past
# the end of `slot_values[]` in EMITTED code.
#
# THE PRODUCT SIDE CATCHES IT, WHICH IS THE POINT OF THE ROW rather than a
# reason to skip it. `vm_splice` re-checks the block bound as it assigns and
# fails LOUDLY, so an under-count is a named compile-time diagnostic instead of
# a silent out-of-bounds write that ASan might or might not be pointed at. This
# row is the evidence that check runs.
SAB_ID="S177-splice-slots-uncounted"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness recursion"
SAB_HARNESS_TARGET="tests/recursion/captures.rxt"
SAB_DESC="vm_count_slots' A_CALL arm stops counting a SPLICED site's SLOT_SPLICE_SAVE block, so RX_NSLOTS is sized without it while vm_splice still assigns from it. Without the emitter's own bound re-check this is a write past the end of slot_values[] in EMITTED code -- K27's class, and vm_count_slots' own header names it."
SAB_DOC_FIGURE="PREDICTED: every spliceable call-bearing pattern whose callee CAPTURES refuses with 'the splice save block overflowed (N of 0 slots)' -- captures.rxt, spellings.rxt, slotfamilies.rxt red as pattern-compile failures. A callee with NO capture inside it has an empty W and stays GREEN, which is the pair that names the failure and is the same shape S-SR1's detector needs. Canonical figure owed from run_sabotage_matrix.sh S177. MEASURED BY HAND at the wave: '(a)(?1)' and '(x)(?1)' refuse with 'the splice save block overflowed (3 of 0 slots)'; the RECURSIVE '(a(?1)?b)' still COMPILES, because its call takes the LINKAGE and allocates no splice block -- the green half."
SAB_COUNT=1
SAB_BEFORE='        v->nsplice += v->spl_nw ? v->spl_nw[idx] : 0;'
SAB_AFTER='        /* SABOTAGE S177: the splice save block goes uncounted */'
