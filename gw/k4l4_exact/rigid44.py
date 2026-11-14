# Residue-block cubes (12 Nov 2026).  For a prime p = 1 (mod 3) and a central block B = [C-h, C+h] of [1,n]
# (C = (n+1)/2), cube t (t = 0..p-1) fixes x(X, cls((X - t) mod p)) for every X in B with X != t (mod p), where cls is the
# cubic class (primitive root g, cls(g^k) = k mod 3); points X = t (mod p) in B stay free.  Used with the --no-rgs
# encoding: a good colouring that agrees with SOME cubic-residue colouring mod p on B up to renaming colours (scaling by
# a unit only permutes the three classes, so it is a renaming too) can be renamed to satisfy cube t for its zero-class
# position t.  So all p cubes UNSAT means: no good exact 4-colouring of [1,n] agrees with a cubic-residue colouring
# mod p (any shift, any unit, any renaming, any colours on the zero class) on B.
# Usage: rigid44.py n p h out.txt [R] [--start A --len L]   (block [A, A+L-1] instead of the central one)
import sys
n, p, h, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
R = int(sys.argv[5]) if len(sys.argv) > 5 and not sys.argv[5].startswith('--') else 4
def prim_root(p):
    fac = [q for q in range(2, p) if (p - 1) % q == 0 and all(q % s for s in range(2, q))]
    return next(g for g in range(2, p) if all(pow(g, (p - 1) // q, p) != 1 for q in fac))
g = prim_root(p); cls = [None] * p; x = 1
for k in range(p - 1): cls[x] = k % 3; x = x * g % p
C = (n + 1) // 2; B = range(C - h, C + h + 1)
if '--start' in sys.argv:
    A0 = int(sys.argv[sys.argv.index('--start') + 1]); L0 = int(sys.argv[sys.argv.index('--len') + 1]); B = range(A0, A0 + L0)
with open(out, 'w') as f:
    for t in range(p):
        lits = [(X - 1) * R + cls[(X - t) % p] + 1 for X in B if (X - t) % p]
        f.write(f'a{B[0]}t{t} ' + ' '.join(map(str, lits)) + '\n')
print(f'p={p} g={g} block [{B[0]},{B[-1]}] ({len(B)} points), {p} cubes -> {out}', file=sys.stderr)
