# Builds the colourings of the paper's constructions (written for papers/gw-2026, independent of the lane scripts)
# and prints lines "k l colouring" for gwcheck. Colours: symbols 0-9a-z.
import sys
SYM = '0123456789abcdefghijklmnopqrstuvwxyz'
def classes(p, m):
    e = (p - 1) // m
    vals = sorted({pow(a, e, p) for a in range(1, p)})
    idx = {v: i for i, v in enumerate(vals)}          # class index 0..m-1 (any fixed naming of the m classes)
    return lambda a: idx[pow(a % p, e, p)]
def split(m, p, l, z):
    """Theorem 2.3 (split zero class): [1,(l-1)p+1], residue class of x-1 off the zero class, m + z on it."""
    cls = classes(p, m); N = (l - 1) * p + 1
    return ''.join(SYM[m + z[(x - 1) // p]] if (x - 1) % p == 0 else SYM[cls(x - 1)] for x in range(1, N + 1))
def plain(m, p, l):
    """Theorem 2.4 (one new colour on the zero class): [1,(l-1)p]."""
    cls = classes(p, m); N = (l - 1) * p
    return ''.join(SYM[m] if (x - 1) % p == 0 else SYM[cls(x - 1)] for x in range(1, N + 1))
def z_of(s): return [int(ch) for ch in s]
out = []
# Theorem 2.3 with m = 2 (quadratic residues; k = 3): l, p, zero-class colourings
for l, p, zs in [(4, 17, ['0110', '0112']), (5, 73, ['01001', '01002']), (6, 193, ['010010', '001002']),
                 (7, 617, ['0100100', '0010020']), (8, 881, ['01121223'])]:
    for zz in zs: out.append((3, l, split(2, p, l, z_of(zz)), f'Thm split m=2 p={p} l={l} z={zz}'))
# Theorem 2.4 (plain) instances
for m, l, p in [(2, 4, 17), (2, 5, 73), (3, 4, 109), (3, 5, 307), (4, 4, 353), (5, 4, 751), (3, 3, 19), (4, 3, 17)]:
    out.append((m + 1, l, plain(m, p, l), f'Thm plain m={m} p={p} l={l}'))
# Theorem 2.3 with m = 3, 4 (k = 4, 5)
for m, l, p, zs in [(3, 3, 19, ['011', '012']), (3, 4, 109, ['0110', '0120']), (3, 5, 307, ['01213']),
                    (3, 6, 1777, ['012234']), (4, 3, 17, ['011', '012']), (4, 4, 353, ['0110', '0112', '0123']),
                    (4, 5, 4937, ['01231'])]:
    for zz in zs: out.append((m + 1, l, split(m, p, l, z_of(zz)), f'Thm split m={m} p={p} l={l} z={zz}'))
# Theorem 2.6 (k >= m + 2, run condition only)
for m, k, l, p, zs in [(3, 5, 3, 19, ['011', '012']), (3, 5, 4, 109, ['0112', '0123']), (3, 5, 5, 307, ['01231', '01223']),
                       (4, 6, 3, 37, ['011', '012']), (4, 6, 4, 353, ['0123']), (4, 6, 5, 4937, ['01234']),
                       (5, 7, 3, 31, ['012']), (5, 7, 4, 751, ['0123'])]:
    for zz in zs: out.append((k, l, split(m, p, l, z_of(zz)), f'Thm pigeonhole m={m} k={k} p={p} l={l} z={zz}'))
# The period-28 colouring of Theorem 4.1: c(X) = T[(X-1) mod 4][class of (X-4) mod 7]
T = [[0, 3, 1], [2, 0, 1], [2, 1, 0], [1, 3, 0]]
Q = {1, 2, 4}
def col28(X):
    b = (X - 4) % 7
    return T[(X - 1) % 4][0 if b in Q else (2 if b == 0 else 1)]
out.append((4, 3, ''.join(SYM[col28(X)] for X in range(1, 57)), 'period-28 colouring on [1,56]'))
# The aligned colouring of [1,328] (GW(4;4,4) >= 329): cubic class of x-1 mod 109 (primitive root 6, class = exponent
# mod 3), zero class 1, 110, 219, 328 coloured 0, 3, 3, 0
def col328(x):
    if (x - 1) % 109 == 0: return [0, 3, 3, 0][(x - 1) // 109]
    a = (x - 1) % 109; e = next(t for t in range(108) if pow(6, t, 109) == a)
    return e % 3
out.append((4, 4, ''.join(SYM[col328(x)] for x in range(1, 329)), 'aligned colouring of [1,328]'))
# red controls (must be BAD)
s56 = out[-2][2]
out.append((4, 3, s56 + s56[0], 'red: period-28 colouring extended to [1,57] periodically'))
out.append((3, 4, split(2, 41, 4, [0, 1, 1, 0]), 'red: p = 41 (1 mod 8 but has runs of 4)'))
out.append((5, 5, split(4, 4957, 5, [0, 1, 2, 3, 1]), 'red: p = 4957 (next prime 1 mod 4 after 4937)'))
for k, l, s, name in out:
    print(f'# {name}')
    print(k, l, s)
