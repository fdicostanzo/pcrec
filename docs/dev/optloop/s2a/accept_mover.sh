#!/usr/bin/env bash
# The acceptance mover's answer check: wild-datetime-datefinder-alternation
# under --engine=vm was REFUSED at abi 40 (666,632 B > 500,000 code cap) and
# compiles at abi 41. No base artifact exists, so it is checked against the
# SAME compiler's auto artifact (a different engine route) on the answer tool's
# subjects, span + every capture + give-up, at every startpos.
set -u
W="$(cd "$(dirname "$0")/../../../.." && pwd)"
S="${OUT:-$(mktemp -d)}/accept"
mkdir -p $S
P="$(cat /Users/fdicostanzo/pcrec-bench/bench/capability/patterns/wild-datetime-datefinder-alternation.rx)"
for caps in "" "--no-captures"; do
  $W/build/pcrec --features all $caps -p pa -o $S/pa.c --pattern "$P" || exit 1
  $W/build/pcrec --features all $caps --engine=vm -p pb -o $S/pb.c --pattern "$P" 2>/dev/null || exit 1
  grep -E '^#define P[AB]_ENGINE ' $S/pa.c $S/pb.c
  gcc-16 -O1 -std=gnu11 -w -I $S -DDIFF_A_LABEL='"auto"' -DDIFF_B_LABEL='"vm"' -o $S/t \
      $W/tests/possessify/possdiff_driver.c $S/pa.c $S/pb.c || exit 1
  python3 - "$P" > $S/subj.txt <<'PY'
import random, sys
p = sys.argv[1].encode()
digits = b"0123456789"; words = [b"Jan", b"January", b"2024", b"12", b"31", b"-", b"/", b":", b" ", b"T", b"Z", b"PM", b"am", b"Monday", b"on", b"at"]
rnd = random.Random(0xD8)
def esc(b): return "".join(chr(c) if 0x21 <= c < 0x7f and c not in (0x5c,0x22) else "\\x%02x" % c for c in b)
out = {"", "2024-01-31", "Jan 31, 2024", "31/12/2024 10:30 PM", "Monday, January 1st 2024 at 12:00"}
for _ in range(300):
    out.add(esc(b"".join(rnd.choice(words + [bytes([rnd.choice(digits)])]) for _ in range(rnd.randint(1, 14)))))
print("\n".join(sorted(out)))
PY
  $S/t < $S/subj.txt || { echo "ACCEPT-MOVER [$caps]: DIVERGED"; exit 1; }
  echo "ACCEPT-MOVER [$caps]: identical"
done
