import itertools, random, string, sys
fam, n = sys.argv[1], int(sys.argv[2])
al = string.ascii_lowercase
if fam == "ladder":
    base = ["".join(t) for t in itertools.product(al[:14], repeat=3)][:n]
    ws = [w for b in base for w in (b, b+"q", b+"qr", b+"qrs")]
elif fam == "dense":
    ws = ["".join(t) for t in itertools.product(al[:8], repeat=5)][:n]
elif fam == "rand":
    r = random.Random(n); ws = sorted({"".join(r.choice(al) for _ in range(8)) for _ in range(n)})
print("(?:" + "|".join(ws) + ")Z")
