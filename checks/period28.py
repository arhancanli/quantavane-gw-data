# Checks for the period-28 colouring (Section 4 of the paper), written for papers/gw-2026:
# (1) the colour classes K0..K3 in Z_4 x Z_7 coordinates; (2) cyclic goodness on Z_28 (no monochromatic cyclic 3-AP and
# no rainbow cyclic 4-AP with d != 0 mod 28); (3) the 28 windows of four consecutive points; (4) the affine maps
# X -> uX + v of Z_28 that permute the colour classes; (5) the description by multipliers of Z_56 (y = 2X - 1);
# (6) the mirror image X -> c(57 - X) on [1,56] is a rotation up to renaming.
T = [[0, 3, 1], [2, 0, 1], [2, 1, 0], [1, 3, 0]]
Q = {1, 2, 4}
def cls7(b): return 0 if b in Q else (2 if b == 0 else 1)
def col(X): return T[(X - 1) % 4][cls7((X - 4) % 7)]
block = ''.join(str(col(X)) for X in range(1, 29))
print('period block X=1..28:', block)
K = {c: sorted(((X - 1) % 4, (X - 4) % 7) for X in range(28) if col(X) == c) for c in range(4)}
for c in range(4): print('K%d =' % c, K[c])
mono = sum(1 for x in range(28) for d in range(1, 28) if col(x) == col(x + d) == col(x + 2 * d))
rain = sum(1 for x in range(28) for d in range(1, 28) if len({col(x + j * d) for j in range(4)}) == 4)
print('cyclic monochromatic 3-APs:', mono, ' cyclic rainbow 4-APs:', rain)
wins = [''.join(str(col(X + j)) for j in range(4)) for X in range(1, 29)]
print('windows:', ' '.join(wins), ' all have a repeat:', all(len(set(w)) < 4 for w in wins))
from math import gcd
units = [u for u in range(28) if gcd(u, 28) == 1]
classes = [frozenset(X for X in range(28) if col(X) == c) for c in range(4)]
sym = []
for u in units:
    for v in range(28):
        img = [frozenset((u * X + v) % 28 for X in S) for S in classes]
        if set(img) == set(classes): sym.append((u, v))
print('affine symmetries (u, v):', sym, ' count', len(sym), ' units covered', sorted({u for u, v in sym}) == units)
def jacobi(a, n):
    a %= n; r = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5): r = -r
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3: r = -r
        a %= n
    return r if n == 1 else 0
def kron_m56(U):  # Kronecker symbol (-56 | U) for odd U coprime to 7: (-56|U) = (-14|U) = (-1|U)(2|U)(7|U) (Jacobi)
    return jacobi(-14 % U, U) if U > 1 else 1
Us = []
for u, v in sym:
    # y = 2X - 1 (mod 56); X -> uX + v gives y -> U y for a unit U of Z_56 iff it is linear in y
    cand = [U for U in range(56) if gcd(U, 56) == 1 and all((2 * ((u * X + v) % 28) - 1) % 56 == (U * (2 * X - 1)) % 56 for X in range(28))]
    Us.append(cand)
print('multipliers U of Z_56 (y = 2X-1):', Us)
flat = sorted(U for c in Us for U in c)
ker = sorted(U for U in range(1, 56) if gcd(U, 56) == 1 and kron_m56(U) == 1)
print('kernel of (-56|.) on units of Z_56:', ker, ' equal to the multiplier set:', flat == ker)
s = ''.join(str(col(X)) for X in range(1, 57))
def canon(t):
    m = {}; return ''.join(str(m.setdefault(ch, len(m))) for ch in t)
mirror = s[::-1]
rots = {canon(''.join(str(col(X + t)) for X in range(1, 57))) for t in range(28)}
print('mirror image is a rotation up to renaming:', canon(mirror) in rots, ' distinct rotations up to renaming:', len(rots))
