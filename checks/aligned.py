# Aligned zero class for three colours (Proposition 3.6 of the paper): on [1,(l-1)p+1], colour x by the quadratic
# character of x-1 (0 = residue, 1 = non-residue) when p does not divide x-1; the zero class 1+jp gets colour 0 for
# j = 0 and j = l-1 and the new colour 2 for 0 < j < l-1. Prints "3 l colouring" lines for gwcheck, and whether
# some j in 1..l-1 is a non-residue mod p (the condition of the proposition).
import sys
def chi(a, p): return 0 if pow(a % p, (p - 1) // 2, p) == 1 else 1
for l, p in [(4, 17), (5, 73), (6, 193), (7, 617), (8, 881), (9, 2377), (6, 113), (5, 17)]:
    N = (l - 1) * p + 1
    c = []
    for x in range(1, N + 1):
        if (x - 1) % p == 0:
            j = (x - 1) // p
            c.append(0 if j in (0, l - 1) else 2)
        else:
            c.append(chi(x - 1, p))
    cond = any(chi(j, p) == 1 for j in range(1, l))
    print(f'# aligned l={l} p={p} N={N} some j<l non-residue: {cond}')
    print(3, l, ''.join(map(str, c)))
