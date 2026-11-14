# van der Waerden CNF (k5 agent, 12 Nov 2026): a colouring of [1,n] with at most r colours and no monochromatic 3-AP,
# colours numbered in order of first appearance (point i may use colours 0..min(i, r-1); colour c >= 1 needs colour c-1
# earlier). UNSAT means every colouring of [1,n] with r or fewer colours has a monochromatic 3-AP.
# For r <= 4 a rainbow 5-AP is impossible, so UNSAT at n = w(r;3) gives GW(r;5,3) <= w(r;3).
# Usage: vdw_cnf.py n r out.cnf
import sys, itertools
n, r, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
v = lambda i, c: i * r + c + 1
cl = []
for i in range(n):
    cl.append([v(i, c) for c in range(min(i + 1, r))])
    for c in range(min(i + 1, r), r): cl.append([-v(i, c)])
    for a, b in itertools.combinations(range(r), 2): cl.append([-v(i, a), -v(i, b)])
for a in range(n):
    for d in range(1, n):
        if a + 2 * d >= n: break
        for c in range(r): cl.append([-v(a, c), -v(a + d, c), -v(a + 2 * d, c)])
for i in range(1, n):
    for c in range(1, r): cl.append([-v(i, c)] + [v(j, c - 1) for j in range(i)])
with open(out, 'w') as f:
    f.write(f'p cnf {n * r} {len(cl)}\n')
    for c in cl: f.write(' '.join(map(str, c)) + ' 0\n')
