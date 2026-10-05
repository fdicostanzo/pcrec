# ssc-sound harness (r4 START-SET soundness critic) — reproduces F1 and the other twin/oracle runs
Setup: `export PCREC=/Users/fdicostanzo/pcrec/build/pcrec W=<scratch dir> PROBE=$W/fs_probe; gcc-16 -O1 -std=gnu11 -Ilib -Isrc -o $PROBE docs/design/startset/fs_probe.c build/libpcrec.a` (from the repo root).
F1 (DFA hat, T = S ∩ E, narrowed + re-seeded): `source dfa_onex.sh; one '(?:(?<=a)z|w)' '61,7a,77,78' 7 --no-captures` -> expect `narrowed_reseed_diffs=11040` (alphabet = comma-separated hex byte tokens, maxlen 7).
VM hat: `source vm_onex.sh; one '<pattern>' '<hex tokens>' <maxlen> [pcrec flags]` (patches via docs/design/startset/twin/vmtwin.py; DROP=<hex byte> for the control). Both drivers (drv2e.c/drv3e.c) decode `\xHH`, so subjects may hold '\n' and high bytes.
Oracle: `printf 'aza\n' | ./run1.sh '(?:(?<=a)z|w)' byte` (modes byte|byteucp|utf8|utf8ucp) diffs the pcrec artifact against LOCAL libpcre2 10.48 (/opt/homebrew; NOT the 10.46 reference) at every startpos.
