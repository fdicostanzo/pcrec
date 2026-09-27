#!/usr/bin/env bash
# The acceptance mover's answer check: wild-datetime-datefinder-alternation
# under --engine=vm was REFUSED at abi 40 (666,628 B > the 500,000 code cap)
# and compiles at abi 41. It is checked, span + every capture + give-up at
# every startpos, against:
#   - the abi-40 VM program itself: BASE --engine=vm with the RAISE-ONLY
#     --max-emit-code-bytes lifted (the cap refuses, it never reshapes, so this
#     is exactly the program main would emit if allowed) — both caps configs;
#   - the same compiler's auto artifact, --no-captures only (a DFA route).
# The first version compared against auto on both configs and exited at its
# first compile: auto REFUSES the caps config at 1,332,799 B > the 1,000,000
# whole-artifact cap on main and on the lane alike (lane s2afix, 2026-09-27),
# so that baseline cannot exist.
#   BASE=<main pcrec, abi 40>  bash accept_mover.sh
set -u
: "${BASE:?}"
W=/Users/fdicostanzo/pcrec/worktrees/s2a
S=/Users/fdicostanzo/pcrec/worktrees/s2a-scratch/chain/accept
mkdir -p $S
P="$(cat /Users/fdicostanzo/pcrec-bench/bench/capability/patterns/wild-datetime-datefinder-alternation.rx)"
python3 - "$P" > $S/subj.txt <<'PY'
import random, sys
digits = b"0123456789"; words = [b"Jan", b"January", b"2024", b"12", b"31", b"-", b"/", b":", b" ", b"T", b"Z", b"PM", b"am", b"Monday", b"on", b"at"]
rnd = random.Random(0xD8)
def esc(b): return "".join(chr(c) if 0x21 <= c < 0x7f and c not in (0x5c,0x22) else "\\x%02x" % c for c in b)
out = {"", "2024-01-31", "Jan 31, 2024", "31/12/2024 10:30 PM", "Monday, January 1st 2024 at 12:00"}
for _ in range(300):
    out.add(esc(b"".join(rnd.choice(words + [bytes([rnd.choice(digits)])]) for _ in range(rnd.randint(1, 14)))))
print("\n".join(sorted(out)))
PY
cmp_pair() {  # label, A-compiler args..., --, B-compiler args...
    local label="$1"; shift
    local a=() b=()
    while [ "$1" != "--" ]; do a+=("$1"); shift; done; shift
    b=("$@")
    "${a[@]}" -p pa -o $S/pa.c --pattern "$P" 2>/dev/null || { echo "ACCEPT-MOVER [$label]: reference refused"; return 1; }
    "${b[@]}" -p pb -o $S/pb.c --pattern "$P" || { echo "ACCEPT-MOVER [$label]: new refused"; return 1; }
    grep -E '^#define P[AB]_(ENGINE|VM_LIT_RUNS) ' $S/pa.c $S/pb.c
    gcc-16 -O1 -std=gnu11 -w -I $S -DDIFF_A_LABEL='"ref"' -DDIFF_B_LABEL='"new"' -o $S/t \
        $W/tests/possessify/possdiff_driver.c $S/pa.c $S/pb.c || { echo "ACCEPT-MOVER [$label]: driver did not build"; return 1; }
    $S/t < $S/subj.txt || { echo "ACCEPT-MOVER [$label]: DIVERGED"; return 1; }
    echo "ACCEPT-MOVER [$label]: identical"
}
rc=0
for caps in "" "--no-captures"; do
    cmp_pair "vm-abi40 vs vm-abi41 ${caps:-caps}" \
        "$BASE" --features all $caps --engine=vm --max-emit-code-bytes=1000000 -- \
        "$W/build/pcrec" --features all $caps --engine=vm || rc=1
done
cmp_pair "auto vs vm-abi41 --no-captures" \
    "$W/build/pcrec" --features all --no-captures -- \
    "$W/build/pcrec" --features all --no-captures --engine=vm || rc=1
exit $rc
