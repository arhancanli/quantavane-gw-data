# DIMACS for: a colouring of [1,n] with AT MOST R colours, no rainbow k-AP, no monochromatic l-AP (11 Nov 2026).
# Colour symmetry is broken by first-occurrence order: point 1 has colour 0, and colour c >= 1 may sit at point i only
# if colour c - 1 occurs before i. Any colouring can be renamed to satisfy this (number the colours in order of first
# appearance), so UNSAT means no such colouring exists with any R or fewer colours.
# Usage: gw_cnf.py n R k l out.cnf
import sys, itertools
n, R, k, l, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
v = lambda i, c: i * R + c + 1
cl = []
for i in range(n):
    cl.append([v(i, c) for c in range(R)])
    for a, b in itertools.combinations(range(R), 2): cl.append([-v(i, a), -v(i, b)])
for a in range(n):
    for d in range(1, n):
        if a + (l - 1) * d < n:
            for c in range(R): cl.append([-v(a + j * d, c) for j in range(l)])
        if a + (k - 1) * d < n and k <= R:
            pts = [a + j * d for j in range(k)]
            for cols in itertools.permutations(range(R), k):
                cl.append([-v(p, cc) for p, cc in zip(pts, cols)])
cl.append([v(0, 0)])
for i in range(1, n):
    for c in range(1, R): cl.append([-v(i, c)] + [v(j, c - 1) for j in range(i)])
with open(out, 'w') as f:
    f.write(f'p cnf {n * R} {len(cl)}\n')
    for c in cl: f.write(' '.join(map(str, c)) + ' 0\n')
print('wrote', out, n * R, 'vars', len(cl), 'clauses')
