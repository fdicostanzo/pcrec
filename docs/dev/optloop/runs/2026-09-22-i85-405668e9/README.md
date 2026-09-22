# I-85 profile pass — [OPTLOOP] cycle 1, executed by the bench executor ([B73])

Raw transcripts of `docs/dev/optloop/cycle1_analysis.md` §3 (setup 0.1-0.5,
blocks M1.a-M6, the two (b) reads), run 2026-09-22 09:57-10:10 EDT on
ubuntubudu (Ryzen 5 1600) at pcrec main 405668e9 (worktree --detach from
the primary clone's main), every command rc=0, subjects 3/3 sha256-exact,
load1 <= 0.26 at every timed phase. Fetched by scp from /tmp/optloop1/out/
the same morning (pcrec manager); the bench's reading is outbox O-44
(pcrec-bench 0347420). The executor logged five mechanical deviations
(O-44): worktree --detach; repo root on sys.path for captext; M4.b's clamp
placed BEFORE the scan_position init (the stated spot would be inert);
one (b)2 rerun after a display-pipe truncation; the p2info bitmap-dump
extension M3.c asks for. The reading is docs/dev/optloop/cycle1_profile.md.
