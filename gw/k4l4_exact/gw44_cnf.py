# DIMACS encoder for the GW(4;4,4) lane (12 Nov 2026): colourings of [1,n] with colours 0..R-1, no rainbow k-AP and no
# monochromatic l-AP.  Usage:
#   gw44_cnf.py n R k l out.cnf [--exact] [--no-amo] [--mirror] [--miss] [--no-rgs] [--map out.map]
#   --mirror-strict-RED (red control only, UNSOUND): with --mirror, demand b < b' instead of b <= b'.
#   (--no-rgs: no colour order and no u ladder; with --exact every colour gets a clause "it occurs"; used when a
#   cube fixes colour names itself, e.g. the residue blocks of rigid44.py)
#
# Variables.  x(i,c) = "point i+1 has colour c" (0-based i), number i*R + c + 1 (fixed, so cubes and decoders can name
# them directly).  u(i,c), c >= 1: "colour c occurs on points 0..i" (prefix ladder).  v(i,c) (only with --mirror):
# "colour c occurs on points i..n-1" (suffix ladder).  Both ladders are defined in both directions, so they take their
# true values in every model.
#
# Clauses (each one holds for the canonical representative described below, so UNSAT means: no good colouring):
#   ALO: every point has a colour.  AMO (default; --no-amo drops it): at most one colour.
#   Colour order (restricted growth, first occurrence): x(0,0); x(i,c) false for c > i; colour c >= 2 at point i needs
#   colour c-1 on points 0..i-1 (u ladder).  Every colouring becomes one of this form after renaming its colours in
#   order of first appearance, and renaming keeps "good" and the number of colours.
#   --exact: colour R-1 occurs (u(n-1,R-1)), i.e. exactly R colours (with the order, colours 0..R-1 all occur).
#   Monochromatic l-APs: one clause per AP and colour.  Rainbow k-APs (k <= R): one clause per AP and injective
#   assignment of k colours to its terms (assignments impossible under the colour order are omitted: they are false).
#   --miss (k = R only): instead, aux m(AP,c) -> (no term of the AP has colour c), and one clause "some m(AP,c)" per
#   AP; an AP with all R colours falsifies it, and a non-rainbow AP satisfies it with m = its missing colour.
#   --mirror (needs --exact): let b(c) = least t such that the first t points carry all R colours and b'(c) the same for
#   the last t points.  b and b' do not change under renaming, and the reflection x -> n+1-x swaps them, so every good
#   colouring c has a reflection-or-identity image c* with b(c*) <= b'(c*), and so does the colour-ordered form of c*.
#   Clause per t = 1..n: (last t points carry all R colours) -> (first t points carry colour R-1).
import sys, itertools

def build(n, R, k, l, exact=False, amo=True, mirror=False, rainbow='perm', rgs=True):
    if not hasattr(build, 'strict'): build.strict = False
    X = lambda i, c: i * R + c + 1
    top = n * R
    U = {}
    for c in range(1, R):
        for i in range(n):
            top += 1; U[i, c] = top
    V = {}
    if mirror:
        assert exact
        for c in range(R):
            for i in range(n):
                top += 1; V[i, c] = top
    cl = []
    if not rgs:                                                 # --no-rgs: plain encoding, every colour occurs
        assert exact and not mirror
        for i in range(n):
            cl.append([X(i, c) for c in range(R)])
            if amo:
                for a, b in itertools.combinations(range(R), 2): cl.append([-X(i, a), -X(i, b)])
        for c in range(R): cl.append([X(i, c) for i in range(n)])
        build.aux = {}
        return top, cl + _aps(n, R, k, l, X, None, rainbow)
    for i in range(n):
        cl.append([X(i, c) for c in range(min(i, R - 1) + 1)])
        for c in range(i + 1, R): cl.append([-X(i, c)])
        if amo:
            for a, b in itertools.combinations(range(min(i, R - 1) + 1), 2): cl.append([-X(i, a), -X(i, b)])
    cl.append([X(0, 0)])
    for c in range(1, R):
        cl.append([-U[0, c]])                                  # colour c >= 1 is not on point 0
        for i in range(1, n):
            cl.append([-U[i - 1, c], U[i, c]]); cl.append([-X(i, c), U[i, c]])
            cl.append([-U[i, c], U[i - 1, c], X(i, c)])
            if c >= 2:
                cl.append([-X(i, c), U[i - 1, c - 1]])          # first-occurrence order
                cl.append([-U[i, c], U[i, c - 1]])              # implied, helps propagation
    if exact: cl.append([U[n - 1, R - 1]])
    if mirror:
        for c in range(R):
            cl.append([-X(n - 1, c), V[n - 1, c]]); cl.append([-V[n - 1, c], X(n - 1, c)])
            for i in range(n - 2, -1, -1):
                cl.append([-V[i + 1, c], V[i, c]]); cl.append([-X(i, c), V[i, c]])
                cl.append([-V[i, c], V[i + 1, c], X(i, c)])
        for t in range(1, n + 1):
            if not build.strict:
                cl.append([-V[n - t, c] for c in range(R)] + [U[t - 1, R - 1]])
            elif t >= 2:                                        # RED CONTROL ONLY (unsound): b < b'
                cl.append([-V[n - t, c] for c in range(R)] + [U[t - 2, R - 1]])
    ok = lambda i, c: c <= i
    AUX = {}                                                    # m variables of --miss: var -> (AP terms, colour)
    for s in range(n):
        for d in range(1, n):
            if s + (min(k, l) - 1) * d >= n: break
            if s + (l - 1) * d < n:
                pts = [s + j * d for j in range(l)]
                for c in range(R):
                    if ok(pts[0], c): cl.append([-X(p, c) for p in pts])
            if k <= R and s + (k - 1) * d < n:
                pts = [s + j * d for j in range(k)]
                if rainbow == 'miss' and k == R:
                    # some colour is missing from the AP: m(c) -> no term has colour c; one clause m(0) v ... v m(R-1)
                    ms = []
                    for c in range(R):
                        top += 1; ms.append(top); AUX[top] = (tuple(pts), c)
                        for p in pts:
                            if ok(p, c): cl.append([-top, -X(p, c)])
                    cl.append(ms)
                else:
                    for cs in itertools.permutations(range(R), k):
                        if all(ok(p, c) for p, c in zip(pts, cs)): cl.append([-X(p, c) for p, c in zip(pts, cs)])
    build.aux = AUX
    return top, cl

def _aps(n, R, k, l, X, ok, rainbow):
    # plain AP clauses (no colour order) for --no-rgs
    cl = []
    for s in range(n):
        for d in range(1, n):
            if s + (min(k, l) - 1) * d >= n: break
            if s + (l - 1) * d < n:
                pts = [s + j * d for j in range(l)]
                for c in range(R): cl.append([-X(p, c) for p in pts])
            if k <= R and s + (k - 1) * d < n:
                pts = [s + j * d for j in range(k)]
                for cs in itertools.permutations(range(R), k): cl.append([-X(p, c) for p, c in zip(pts, cs)])
    return cl

def main():
    a = sys.argv[1:]
    n, R, k, l = map(int, a[:4]); out = a[4]
    build.strict = '--mirror-strict-RED' in a
    top, cl = build(n, R, k, l, exact='--exact' in a, amo='--no-amo' not in a, mirror='--mirror' in a,
                    rainbow='miss' if '--miss' in a else 'perm', rgs='--no-rgs' not in a)
    with open(out, 'w') as f:
        f.write(f'c gw44_cnf.py n={n} R={R} k={k} l={l} flags={" ".join(x for x in a[5:] if x.startswith("--"))}\n')
        f.write(f'p cnf {top} {len(cl)}\n')
        for c in cl: f.write(' '.join(map(str, c)) + ' 0\n')
    if '--map' in a:
        with open(a[a.index('--map') + 1], 'w') as f: f.write(f'{n} {R}\n')
    print(f'wrote {out}: {top} vars, {len(cl)} clauses', file=sys.stderr)

if __name__ == '__main__':
    main()
