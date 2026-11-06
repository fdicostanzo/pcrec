# nswk.py K N L: K concatenated alternations, each N words of L bytes with
# pairwise distinct first byte and distinct last byte (no M/P/S rewrite applies)
import random, sys
K, N, L = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
safe = [c for c in range(0x21, 0x7f) if chr(c) not in '\\^$.|?*+()[]{}#-/']
pool = safe + list(range(0x80, 0x100))
def esc(b): return chr(b) if b < 0x80 else '\\x%02x' % b
r = random.Random(1)
alts = []
for k in range(K):
    ws = []
    for i in range(N):
        first, last = pool[i], pool[(i * 7 + 3 + k) % len(pool)]
        mid = [r.choice(range(0x61, 0x7b)) for _ in range(L - 2)]
        ws.append(''.join(esc(b) for b in [first] + mid + [last]))
    alts.append('(?:' + '|'.join(ws) + ')')
print(''.join(alts) + 'Z')
