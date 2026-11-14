#!/bin/zsh
# Certificates for the row GW(r;4,3) (rainbow 4-AP, monochromatic 3-AP), k4 agent, 12 Nov 2026.
# Each UNSAT instance: CaDiCaL 3.0.1 --lrat=true --binary=false --vivifyinst=false, then our STRICT checker lratcheck
# (if a proof still has satisfied hints: lratcheck --write-clean, and the clean proof is checked strictly).
# drat-trim's lrat-check is NOT used (it accepts a satisfiable formula with an empty proof, issue #42).
#   A4_57 (gw_cnf.py 57 4 4 3): no good colouring of [1,57] with <= 4 colours
#   P5    (gw_rgs.py 57 4 3 40 5 57): for no n in [40,57] a good colouring of [1,n] with >= 5 colours
#   P7    (gw_rgs.py 39 4 3 37 7 39): for no n in [37,39] one with >= 7 colours
#   P9    (gw_rgs.py 36 4 3 24 9 36): for no n in [24,36] one with >= 9 colours
#   P10   (gw_rgs.py 23 4 3 10 10 23): for no n in [10,23] one with >= 10 colours
#   U56   (gw_cnf.py 56 4 4 3 + 28 blocking clauses): the 28 colourings in extremal56_rgs.txt are the only good
#         colourings of [1,56] with <= 4 colours (colours named in order of first appearance)
# Green controls (must be SAT; decoded and checked by check_k4.py): <= 4 colours at 56; exactly 5, 6 at 39;
# exactly 7, 8 at 36; exactly 9 at 23. Red control: P10's proof with one hint removed must be rejected.
# One solver at a time, nice 10; stops if the disk falls under 21 GB free. Proofs are gzipped after the check.
setopt NO_BG_NICE
D=${GW_WORK:-$PWD/work/k4cert}                 # work folder (formulas and proofs are written here)
S=${GW_ROOT:-${0:A:h:h}}                         # the folder above this one
K=$S/k4
P=${PYTHON:-python3}
CAD=${CADICAL:-cadical}                          # CaDiCaL 3.0.1
OC=${LRATCHECK:-$S/lratcheck}                    # lratcheck.c of the folder above, compiled
L=$K/cert_k4l3.log
mkdir -p $D; cd $D
log() { echo "$(date '+%F %T') $*" | tee -a $L; }
disk_ok() { [ $(df -k /System/Volumes/Data | awk 'NR==2{printf "%d", $4/1048576}') -ge 21 ]; }
cert() {  # name ; $1.cnf exists
  disk_ok || { log "STOP disk under 21 GB"; exit 1; }
  log "SOLVE $1 $(grep '^p cnf' $1.cnf) sha256 $(shasum -a 256 $1.cnf | cut -c1-64)"
  s=$(date +%s); nice -n 10 $CAD -q --lrat=true --binary=false --vivifyinst=false $1.cnf $1.lrat > $1.out; rc=$?
  log "SOLVE $1 rc=$rc (20 = UNSAT) $(( $(date +%s) - s ))s proof $(stat -f %z $1.lrat) bytes"
  [ $rc = 20 ] || return
  out=$(nice -n 10 $OC $1.cnf $1.lrat 2>&1 | tail -2 | tr '\n' ' ')
  log "STRICT $1: $out"
  if ! echo "$out" | grep -q "s VERIFIED"; then
    nice -n 10 $OC --write-clean $1.clean.lrat $1.cnf $1.lrat > /dev/null 2>&1
    mv $1.clean.lrat $1.lrat
    log "STRICT $1 (after --write-clean): $(nice -n 10 $OC $1.cnf $1.lrat 2>&1 | tail -2 | tr '\n' ' ')"
  fi
  log "SHA256 $1 lrat $(shasum -a 256 $1.lrat | cut -c1-64) ($(stat -f %z $1.lrat) bytes)"
}
green() {  # name n encoder-args... ; SAT expected, decode via map (gw_rgs) or direct (gw_cnf)
  name=$1; shift
  nice -n 10 $CAD -q $name.cnf > $name.out; rc=$?
  if [ -f $name.map ]; then col=$($P -I $K/decode_rgs.py $name.out $name.map)
  else col=$($P -I - $name.out $name.n <<'EOF'
import sys
m = set(int(x) for line in open(sys.argv[1]) if line.startswith('v') for x in line.split()[1:] if int(x) > 0)
n = int(open(sys.argv[2]).read())
print(''.join(str(next(c for c in range(4) if i * 4 + c + 1 in m)) for i in range(n)))
EOF
)
  fi
  log "GREEN $name rc=$rc (10 = SAT expected) $col"
  log "GREEN $name check: $($P -I $K/check_k4.py 4 3 $col)"
}
log "START cert_k4l3.sh"
# UNSAT instances
$P -I $S/gw_cnf.py 57 4 4 3 A4_57.cnf > /dev/null
$P -I $K/gw_rgs.py 57 4 3 40 5 57 P5.cnf 2> /dev/null
$P -I $K/gw_rgs.py 39 4 3 37 7 39 P7.cnf 2> /dev/null
$P -I $K/gw_rgs.py 36 4 3 24 9 36 P9.cnf 2> /dev/null
$P -I $K/gw_rgs.py 23 4 3 10 10 23 P10.cnf 2> /dev/null
$P -I $S/gw_cnf.py 56 4 4 3 U56.cnf > /dev/null
$P -I - U56.cnf $K/extremal56_rgs.txt <<'EOF'
import sys
cnf, rots = sys.argv[1], [s.strip() for s in open(sys.argv[2]) if s.strip()]
lines = open(cnf).read().split('\n')
hdr = lines[0].split(); nv, nc = int(hdr[2]), int(hdr[3])
body = [l for l in lines[1:] if l.strip()]
for s in rots: body.append(' '.join(str(-(i * 4 + int(ch) + 1)) for i, ch in enumerate(s)) + ' 0')
open(cnf, 'w').write(f'p cnf {nv} {nc + len(rots)}\n' + '\n'.join(body) + '\n')
EOF
for x in P10 P9 P7 A4_57 P5 U56; do cert $x; done
# red control: drop the last hint of the final (empty-clause) step of P10's proof
$P -I - P10.lrat P10_red.lrat <<'EOF'
import sys
lines = open(sys.argv[1]).read().split('\n'); lines = [l for l in lines if l.strip()]
for i in range(len(lines) - 1, -1, -1):
    t = lines[i].split()
    if len(t) > 2 and t[1] != 'd' and t[1] == '0':          # empty clause step: "id 0 hints 0"
        hints = t[2:-1]; lines[i] = ' '.join([t[0], '0'] + hints[:-1] + ['0']); break
open(sys.argv[2], 'w').write('\n'.join(lines) + '\n')
EOF
log "RED P10 with one hint removed: $($OC P10.cnf P10_red.lrat 2>&1 | tail -2 | tr '\n' ' ')"
rm -f P10_red.lrat
# green controls
$P -I $S/gw_cnf.py 56 4 4 3 G4_56.cnf > /dev/null; echo 56 > G4_56.n; green G4_56
$P -I $K/gw_rgs.py 39 4 3 39 5 5 G5_39.cnf --map G5_39.map 2> /dev/null; green G5_39
$P -I $K/gw_rgs.py 39 4 3 39 6 6 G6_39.cnf --map G6_39.map 2> /dev/null; green G6_39
$P -I $K/gw_rgs.py 36 4 3 36 7 7 G7_36.cnf --map G7_36.map 2> /dev/null; green G7_36
$P -I $K/gw_rgs.py 36 4 3 36 8 8 G8_36.cnf --map G8_36.map 2> /dev/null; green G8_36
$P -I $K/gw_rgs.py 23 4 3 23 9 9 G9_23.cnf --map G9_23.map 2> /dev/null; green G9_23
for x in P10 P9 P7 A4_57 P5 U56; do [ -f $x.lrat ] && gzip -f $x.lrat; done
log "END cert_k4l3.sh"
