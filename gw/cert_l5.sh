#!/bin/zsh
# GW(r;3,5) row certificates (coordinator, 11 Nov 2026 21:xx). Replaces the any-colour anchor at 294, which timed out
# on Modal (gw-25004099, 8,400 s). Three UNSAT instances, each solved by CaDiCaL 3.0.1 with an LRAT proof that is
# checked by drat-trim's lrat-check and by our lratcheck, then compressed:
#   A3_293: no good colouring of [1,293] with <= 3 colours        (gives GW(3;3,5) <= 293)
#   A5_294: no good colouring of [1,294] with <= 5 colours        (with P294: no good colouring of [1,294] at all)
#   P294:   for no n <= 294 a good colouring of [1,n] with >= 6 colours (gw_prefix.py)
# Green controls (must be SAT, decoded and checked by check_rm.py): <= 3 colours at 292, <= 5 colours at 293.
# Runs one solver at a time at nice 10; stops if the disk falls under 27 GB free.
D=${GW_WORK:-$PWD/work/l5cert}                 # work folder (formulas and proofs are written here)
S=${GW_ROOT:-${0:A:h}}                           # this folder
P=${PYTHON:-python3}
CAD=${CADICAL:-cadical}                          # CaDiCaL 3.0.1
LC=${LRAT_CHECK:-lrat-check}                     # drat-trim's lrat-check
OC=${LRATCHECK:-$S/lratcheck}                    # lratcheck.c of this folder, compiled
mkdir -p $D; cd $D
log() { echo "$(date '+%F %T') $*" | tee -a $D/cert_l5.log; }
disk_ok() { [ $(df -k /System/Volumes/Data | awk 'NR==2{printf "%d", $4/1048576}') -ge 27 ]; }
green() {  # name n R
  $P -I $S/gw_cnf.py $2 $3 3 5 $1.cnf >> cert_l5.log
  nice -n 10 $CAD -q $1.cnf > $1.out; rc=$?
  log "GREEN $1 rc=$rc (10 = SAT expected)"
  if [ $rc = 10 ]; then
    $P -I - $1.out $2 $3 > $1.col <<'EOF'
import sys
m = set(int(x) for line in open(sys.argv[1]) if line.startswith('v') for x in line.split()[1:] if int(x) > 0)
n, R = int(sys.argv[2]), int(sys.argv[3])
print(''.join(str(next(c for c in range(R) if i * R + c + 1 in m)) for i in range(n)))
EOF
    log "GREEN $1 check: $($P -I $S/check_rm.py 5 $(cat $1.col))"
  fi
}
cert() {  # name (cnf already written)
  disk_ok || { log "STOP disk under 27 GB"; exit 1; }
  log "SOLVE $1 start ($(head -1 $1.cnf))"
  nice -n 10 $CAD -q --lrat=true --binary=false $1.cnf $1.lrat > $1.out; rc=$?
  log "SOLVE $1 rc=$rc (20 = UNSAT) $(ls -la $1.lrat | awk '{print $5}') bytes"
  [ $rc = 20 ] || return
  log "LRATCHECK $1 drat-trim: $(nice -n 10 $LC $1.cnf $1.lrat | tail -2 | tr '\n' ' ')"
  log "LRATCHECK $1 ours: $(nice -n 10 $OC $1.cnf $1.lrat | tail -2 | tr '\n' ' ')"
  log "SHA $1 $(shasum -a 256 $1.cnf $1.lrat | awk '{print $1}' | tr '\n' ' ')"
  nice -n 10 xz -T4 -6 $1.lrat && log "XZ $1 $(ls -la $1.lrat.xz | awk '{print $5}') bytes"
}
log "START cert_l5"
green g3_292 292 3
green g5_293 293 5
$P -I $S/gw_cnf.py 293 3 3 5 A3_293.cnf >> cert_l5.log; cert A3_293
$P -I $S/gw_cnf.py 294 5 3 5 A5_294.cnf >> cert_l5.log; cert A5_294
$P -I $S/gw_prefix.py 294 5 6 P294.cnf >> cert_l5.log; cert P294
log "END cert_l5"
