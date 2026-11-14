# Cube generator for gw44_cnf.py instances (12 Nov 2026).  Variable numbering as in gw44_cnf.py:
#   x(i,c) = i*R + c + 1 (0-based point i);  u(i,c) (c >= 1, colour c occurs on points 0..i) = n*R + (c-1)*n + i + 1.
# Cube kinds (each line "TAG lit lit ..."):
#   b3 T1-T2,T3-T4,...      first occurrence b of colour R-1 (1-based) in [T1,T2], ...: lits u(T2-1,R-1), -u(T1-2,R-1)
#   points P1,P2,...        all colour patterns of the listed 1-based points (each point: colours allowed by the colour
#                           order, i.e. c <= P-1), crossed with the b3 cubes if both are given
#   window A-B              all colour patterns of the consecutive points A..B that have no monochromatic l-AP and no
#                           rainbow k-AP inside the window (the others are refuted by the CNF's own clauses, so dropping
#                           them keeps coverage; coverage is certified anyway by cover44.py); --k/--l default 4
# Usage: cubes44.py n R out.txt [--b3 SPEC] [--points LIST] [--seed S --sample K]
import sys, itertools, random

def X(i, c, R): return i * R + c + 1
def U(i, c, n, R): return n * R + (c - 1) * n + i + 1

def main():
    a = sys.argv[1:]
    n, R, out = int(a[0]), int(a[1]), a[2]
    b3 = []
    if '--b3' in a:
        for part in a[a.index('--b3') + 1].split(','):
            t1, t2 = map(int, part.split('-'))
            lits = [U(t2 - 1, R - 1, n, R)]
            if t1 >= 2: lits.append(-U(t1 - 2, R - 1, n, R))
            b3.append((f'b{t1}-{t2}', lits))
    else:
        b3 = [('all', [])]
    pts = [int(p) for p in a[a.index('--points') + 1].split(',')] if '--points' in a else []
    win = None
    if '--window' in a:
        A, B = map(int, a[a.index('--window') + 1].split('-')); pts = list(range(A, B + 1))
        k = int(a[a.index('--k') + 1]) if '--k' in a else 4; l = int(a[a.index('--l') + 1]) if '--l' in a else 4
        def good(cols):
            m = len(cols)
            for st in range(m):
                for d in range(1, m):
                    if st + (min(k, l) - 1) * d >= m: break
                    if st + (l - 1) * d < m and len({cols[st + j * d] for j in range(l)}) == 1: return False
                    if st + (k - 1) * d < m and len({cols[st + j * d] for j in range(k)}) == k: return False
            return True
        win = good
    cubes = []
    for tag, lits in b3:
        doms = [range(min(p - 1, R - 1) + 1) for p in pts]
        for cols in itertools.product(*doms):
            if win and not win(cols): continue
            t = tag + ('_' + ''.join(map(str, cols)) if pts else '')
            cubes.append((t, lits + [X(p - 1, c, R) for p, c in zip(pts, cols)]))
    if '--sample' in a:
        random.seed(int(a[a.index('--seed') + 1]) if '--seed' in a else 1)
        cubes = random.sample(cubes, min(int(a[a.index('--sample') + 1]), len(cubes)))
    with open(out, 'w') as f:
        for t, lits in cubes: f.write(t + ' ' + ' '.join(map(str, lits)) + '\n')
    print(f'wrote {len(cubes)} cubes to {out}', file=sys.stderr)

if __name__ == '__main__':
    main()
