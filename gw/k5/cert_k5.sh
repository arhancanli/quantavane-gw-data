#!/bin/zsh
# Certificates for the k5 lane (12 Nov 2026). Each UNSAT instance: CaDiCaL 3.0.1 --lrat=true --binary=false
# --vivifyinst=false, then our STRICT checker lratcheck (no satisfied hints allowed; if a proof had them it would be
# cleaned with --write-clean and re-checked strictly). drat-trim's lrat-check is NOT used (issue #42).
#   V2_9   (vdw_cnf.py 9 2):  every colouring of [1,9] with <= 2 colours has a monochromatic 3-AP   (w(2;3) <= 9)
#   V3_27  (vdw_cnf.py 27 3): every colouring of [1,27] with <= 3 colours has a monochromatic 3-AP  (w(3;3) <= 27)
#   P19_40 (k4/gw_rgs.py 40 5 3 19 19 40): for no n in [19,40] a colouring of [1,n] with no rainbow 5-AP and no
#          monochromatic 3-AP uses >= 19 colours (n < 19 cannot carry 19 colours)
# Green controls (SAT, decoded and checked by check_k5): <= 2 colours at 8, <= 3 colours at 26.
# Red control: V3_27's proof with the last hint of its final step removed must be rejected.
# One solver at a time, nice 10; stops if the disk falls under 21 GB free. Proofs are gzipped after the check.
setopt NO_BG_NICE
D=${GW_WORK:-$PWD/work/k5cert}                 # work folder (formulas and proofs are written here)
S=${GW_ROOT:-${0:A:h:h}}                         # the folder above this one
K=$S/k5
P=${PYTHON:-python3}
CAD=${CADICAL:-cadical}                          # CaDiCaL 3.0.1
OC=${LRATCHECK:-$S/lratcheck}                    # lratcheck.c of the folder above, compiled
L=$K/cert_k5.log
mkdir -p $D; cd $D
cc -O2 -o check_k5 $K/check_k5.c
log() { echo "$(date '+%F %T') $*" | tee -a $L; }
disk_ok() { [ $(df -k /System/Volumes/Data | awk 'NR==2{printf "%d", $4/1048576}') -ge 21 ]; }
cert() {
  disk_ok || { log "STOP disk under 21 GB"; exit 1; }
  log "SOLVE $1 $(grep '^p cnf' $1.cnf) cnf sha256 $(shasum -a 256 $1.cnf | cut -c1-64)"
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
log "START cert_k5.sh"
$P -I $K/vdw_cnf.py 9 2 V2_9.cnf
$P -I $K/vdw_cnf.py 27 3 V3_27.cnf
$P -I $S/k4/gw_rgs.py 40 5 3 19 19 40 P19_40.cnf 2> /dev/null
for x in V2_9 V3_27 P19_40; do cert $x; done
$P -I - V3_27.lrat V3_27_red.lrat <<'PY'
import sys
lines = [l for l in open(sys.argv[1]).read().split('\n') if l.strip()]
for i in range(len(lines) - 1, -1, -1):
    t = lines[i].split()
    if len(t) > 2 and t[1] == '0':
        lines[i] = ' '.join([t[0], '0'] + t[2:-1][:-1] + ['0']); break
open(sys.argv[2], 'w').write('\n'.join(lines) + '\n')
PY
log "RED V3_27 with one hint removed: $($OC V3_27.cnf V3_27_red.lrat 2>&1 | tail -2 | tr '\n' ' ')"
rm -f V3_27_red.lrat
for spec in "8 2 G2_8" "26 3 G3_26"; do set -- ${=spec}
  $P -I $K/vdw_cnf.py $1 $2 $3.cnf; nice -n 10 $CAD -q $3.cnf > $3.out; rc=$?
  col=$($P -I - $3.out $1 $2 <<'PY'
import sys
m = set(int(x) for line in open(sys.argv[1]) if line.startswith('v') for x in line.split()[1:] if int(x) > 0)
n, r = int(sys.argv[2]), int(sys.argv[3])
print(''.join(str(next(c for c in range(r) if i * r + c + 1 in m)) for i in range(n)))
PY
)
  log "GREEN $3 rc=$rc (10 = SAT expected) $col: $(echo $col | ./check_k5 5 3)"
done
for x in V2_9 V3_27 P19_40; do [ -f $x.lrat ] && gzip -f $x.lrat; done
log "END cert_k5.sh"
