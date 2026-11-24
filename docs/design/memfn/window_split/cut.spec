# window_split.md rev 2 §3: the cut at T a0f13ad83, read by assemble.py (and by census.py,
# bucket.py, home.py: `window.h` is then one more "file", the header's moved type text).
# Rev 2 corrections (r95): W17 boundaries (ask 2840-2876 / ren 2877-; text -3879 / floor 3880-;
# efind from 2649, vform from 4321, floor from 4608; presence.c 56-83 with kit_mass's comment);
# O1 frame / ren split; W2 primitives (kit_pos.c takes kit_mass and kit_run_member, kit_pick.c
# is the TIE table and its searchers); W3 the family vocabulary into window.h.
# `-` is no file: lines the prologues replace (window.c's SPDX/provenance head, :1-7, and its
# includes, :66-71) and lines an edits.spec block re-places verbatim (kit_tie_member_key :132-139
# -> presence.c). window.h's first piece, :8-65, is the family comment (W3).
window.h         <- window.c 8-65 73-76 152-229 583-584 757-790 792-792 1377-1448 1493-1494 1568-1578
window.h         <- window.c 1778-1796 1890-1890 1926-1933 1991-1991 2300-2304 2334-2346 2385-2393
window.h         <- window.c 2412-2419 2436-2445 3559-3573
kit_pos.c        <- window.c 231-284 937-962
kit_pos.c        <- presence.c 56-83
kit_pick.c       <- window.c 78-131 140-151
-                <- window.c 1-7 66-71 132-139
window_cands.c   <- window.c 152-230 285-459
window_check.c   <- window.c 460-580
window_stop.c    <- window.c 72-77 581-836
window_margin.c  <- window.c 837-901
window_verify.c  <- window.c 902-936 963-1229
window_decide.c  <- window.c 1230-1374
window_plan.c    <- window.c 1375-1555 4511-4607
window_legacy.c  <- window.c 1556-1775
window_frame.c   <- window.c 1776-1892 2564-2606 2691-2839
window_ren.c     <- window.c 2193-2563 2607-2648 2877-2887
window_span.c    <- window.c 1893-2065 3706-3730
window_efind.c   <- window.c 2066-2192 2649-2690 4083-4089
window_ask.c     <- window.c 2840-2876 2888-3266
window_parts.c   <- window.c 3267-3538
window_text.c    <- window.c 3539-3705 3731-3766 3847-3879 3897-3965
window_test.c    <- window.c 3779-3846
window_floor.c   <- window.c 3880-3896 3966-4035 4608-4641
window_find.c    <- window.c 4036-4082 4090-4320 4471-4510 4642-4672
window_vform.c   <- window.c 3767-3778 4321-4470
# W4 (C0b, ARV-7's B-s3): the text buffer and the sink writers into their own leaf, a pure move
kit_kb.c         <- compose.c 27-115
