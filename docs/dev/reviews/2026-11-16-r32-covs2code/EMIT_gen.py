import sys, random
# gen.py SEED_HEX OUT : subjects (hex) around a planted match
seed = bytes.fromhex(sys.argv[1]); out = sys.argv[2]; random.seed(len(seed))
alpha = b"0123456789abcdefgxyzABCDEFG -_\n" + "éαβω".encode()
k = len(seed); S = []
S.append(seed); S.append(seed[:-1]); S.append(seed + seed); S.append(b"x" + seed + b"x"); S.append(b"0" + seed + b"0")
S.append(b"g" + seed); S.append(seed + b"g"); S.append(b" " + seed + b" "); S.append(b"\n" + seed + b"\n"); S.append(b"")
for pos in sorted(set([0, 1, k // 2, k - 2, k - 1])):
    for rep in (b"g", b"Z", b" ", b"0", b"a"):
        m = bytearray(seed); m[pos:pos + 1] = rep; S.append(bytes(m)); S.append(b"q" + bytes(m) + seed[:3])
for i in range(12):
    n = random.randint(0, 2 * k + 5); S.append(bytes(random.choice(alpha) for _ in range(n)))
    j = random.randint(0, 6); S.append(bytes(random.choice(alpha) for _ in range(j)) + seed + bytes(random.choice(alpha) for _ in range(random.randint(0, 6))))
S.append(seed[1:] + seed); S.append(seed[: k // 2] + seed)
open(out, "w").write("\n".join(s.hex() for s in S) + "\n")
