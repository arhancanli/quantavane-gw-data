# One explicit colouring for every lower bound in Table 2 of the paper (written for papers/gw-2026):
# Theorem 3.2 (split zero class, s >= 2 new colours), Proposition 3.4 (aligned, one new colour) and Theorem 3.5
# (k >= m + 2). For each (k, l, m, p) and each admissible number of colours r, a zero-class colouring z with the
# right number of colours and no rainbow k-AP is taken from the exhaustive search in smax.py. Output: "k l colouring".
import itertools
SYM = '0123456789abcdefghijklmnopqrstuvwxyz'
def classes(p, m):
    e = (p - 1) // m
    vals = [1] + sorted({pow(a, e, p) for a in range(1, p)} - {1})
    idx = {v: i for i, v in enumerate(vals)}
    return lambda a: idx[pow(a % p, e, p)]
def rainbow_free(z, k):
    l = len(z)
    return all(len({z[a + j * d] for j in range(k)}) < k for a in range(l) for d in range(1, l) if a + (k - 1) * d < l)
def zero_pattern(k, l, s):
    for z in itertools.product(range(s), repeat=l):
        if len(set(z)) == s and rainbow_free(z, k): return list(z)
    return None
def split(m, p, l, z):
    cls = classes(p, m); N = (l - 1) * p + 1
    return ''.join(SYM[m + z[(x - 1) // p]] if (x - 1) % p == 0 else SYM[cls(x - 1)] for x in range(1, N + 1))
def aligned(m, p, l):
    cls = classes(p, m); N = (l - 1) * p + 1
    return ''.join((SYM[0] if (x - 1) // p in (0, l - 1) else SYM[m]) if (x - 1) % p == 0 else SYM[cls(x - 1)]
                   for x in range(1, N + 1))
rows = [  # (k, l, m, p, r values via split, aligned?)
    (3, 4, 2, 17), (3, 6, 2, 193), (3, 7, 2, 617), (3, 8, 2, 881), (3, 9, 2, 2377), (3, 5, 2, 73),
    (4, 3, 3, 19), (4, 4, 3, 109), (4, 5, 3, 307), (4, 6, 3, 1777),
    (5, 4, 4, 353), (5, 5, 4, 4937), (6, 4, 5, 751),
    (5, 3, 3, 19), (6, 3, 4, 37), (6, 5, 4, 4937), (7, 3, 5, 31), (7, 4, 5, 751)]
for k, l, m, p in rows:
    if k == m + 1:
        print(f'# aligned k={k} l={l} m={m} p={p} r={m + 1} bound {(l - 1) * p + 2}')
        print(k, l, aligned(m, p, l))
    s = 2
    while True:
        z = zero_pattern(k, l, s)
        if z is None: break
        print(f'# split k={k} l={l} m={m} p={p} s={s} r={m + s} z={"".join(map(str, z))} bound {(l - 1) * p + 2}')
        print(k, l, split(m, p, l, z))
        s += 1
