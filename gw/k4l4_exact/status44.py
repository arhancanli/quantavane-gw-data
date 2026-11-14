# Status of a run44.py log against its cube file (12 Nov 2026): a cube set is CERTIFIED only when every cube of the file
# has a FINISH line with status UNSAT_CHECKED (CaDiCaL exit 20 and our strict lratcheck printed "s VERIFIED UNSAT").
# Usage: status44.py CUBES.txt RUN.log [CUBES2.txt RUN2.log ...]
import sys, collections
a = sys.argv[1:]
for cubes, logf in zip(a[0::2], a[1::2]):
    tags = [l.split()[0] for l in open(cubes) if l.strip()]
    st, cpu, pb = {}, collections.Counter(), 0
    for line in open(logf):
        p = line.split()
        if len(p) >= 4 and p[0] == 'FINISH' and p[2].startswith('status='):
            st[p[1]] = p[2][7:]
            for f in p:
                if f.startswith('cpu='): cpu[p[1]] = float(f[4:])
                if f.startswith('proof_bytes='): pb += int(f[12:])
    cnt = collections.Counter(st.get(t, 'NOT_RUN') for t in tags)
    done = cnt['UNSAT_CHECKED']
    print(f'{cubes}: {len(tags)} cubes; ' + ', '.join(f'{k} {v}' for k, v in sorted(cnt.items())) +
          f'; solver cpu {sum(cpu[t] for t in tags if t in cpu):.0f} s (max {max([cpu[t] for t in tags if t in cpu] or [0]):.1f} s);'
          f' proofs streamed {pb / 1e9:.2f} GB; ' + ('CERTIFIED' if done == len(tags) else f'OPEN ({len(tags) - done} left)'))
