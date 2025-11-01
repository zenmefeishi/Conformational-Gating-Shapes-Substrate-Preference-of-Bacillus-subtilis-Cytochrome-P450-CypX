#!/usr/bin/env bash
# cypx_1us_segment_runner.sh
# Run production MD to **1 µs** in segments (default 20 × 50 ns) with dt read from step5_production.mdp.
# Matches user's real workflow: analysis window 100–1000 ns; uses step4.1_equilibration.gro as the start.
#
# Requirements (in current directory):
#   - topol.top
#   - index.ndx
#   - step4.1_equilibration.gro  (as starting coordinates for seg_01)
#   - step5_production.mdp       (your production settings; we read dt from it)
#
# Outputs:
#   - seg_01 … seg_20 (.tpr/.gro/.cpt/.edr/.log/.xtc) totaling 1000 ns by default
#
# Tunables (export before running, or pass inline "VAR=... bash ..."):
#   GMX_CMD=gmx
#   USE_GPU=0/1                # mdrun -nb gpu -pme gpu if 1
#   NTOMP=8 PIN=on DLB=auto    # threading & domain decomposition
#   TOT_NS=1000 SEG_NS=50      # total nanoseconds and per-segment length
#   MAXWARN=2                  # grompp -maxwarn
#   DEFNM_PREFIX=seg_          # file prefix for segments
#
# Example:
#   USE_GPU=1 NTOMP=8 SEG_NS=50 TOT_NS=1000 bash cypx_1us_segment_runner.sh
#
set -Eeuo pipefail

GMX_CMD="${GMX_CMD:-gmx}"
USE_GPU="${USE_GPU:-0}"
NTOMP="${NTOMP:-8}"
PIN="${PIN:-on}"
DLB="${DLB:-auto}"
TOT_NS="${TOT_NS:-1000}"
SEG_NS="${SEG_NS:-50}"
MAXWARN="${MAXWARN:-2}"
DEFNM_PREFIX="${DEFNM_PREFIX:-seg_}"

TOP="topol.top"
NDX="index.ndx"
C0="step4.1_equilibration.gro"
MDP_PROD="step5_production.mdp"

gpu_flags(){ if [[ "$USE_GPU" == "1" ]]; then echo "-nb gpu -pme gpu"; else echo ""; fi; }
die(){ echo "[FATAL] $*" >&2; exit 1; }
log(){ echo -e "\n[INFO] $*\n"; }

need(){ [[ -e "$1" ]] || die "Missing required file: $1"; }

get_dt_ps(){
  # parse 'dt = 0.002' (ignore comments/blank)
  awk '
    BEGIN{dt=""}
    /^[ \t]*([;#]|$)/{next}
    /^[ \t]*dt[ \t]*=/{gsub(/[ \t]/,""); sub(/^dt=/,""); dt=$0}
    END{if(dt=="") dt="0.002"; print dt}
  ' "$MDP_PROD"
}

calc_steps(){
  local seg_ns="$1" dt_ps="$2"
  # steps = (seg_ns * 1000 ps/ns) / dt_ps
  awk -v seg_ns="$seg_ns" -v dt="$dt_ps" 'BEGIN{printf("%.0f", (seg_ns*1000.0)/dt)}'
}

write_seg_mdp(){
  local base_mdp="$1" out_mdp="$2" nsteps="$3"
  awk -v nsteps="$nsteps" '
    BEGIN{done=0}
    /^[ \t]*([;#]|$)/{print; next}
    /^[ \t]*nsteps[ \t]*=/{print "nsteps                   = " nsteps; done=1; next}
    {print}
    END{if(!done) print "nsteps                   = " nsteps}
  ' "$base_mdp" > "$out_mdp"
}

main(){
  command -v "$GMX_CMD" >/dev/null 2>&1 || die "Cannot find $GMX_CMD"
  need "$TOP"; need "$NDX"; need "$C0"; need "$MDP_PROD"

  local dt_ps; dt_ps="$(get_dt_ps)"
  log "Parsed dt from $MDP_PROD: dt = ${dt_ps} ps"

  # integer division ok because we ensure equal segments
  local nseg=$(( TOT_NS / SEG_NS ))
  (( nseg > 0 )) || die "Invalid nseg (TOT_NS/SEG_NS): $nseg"
  log "Plan: ${nseg} segments × ${SEG_NS} ns = ${TOT_NS} ns total"

  local steps; steps="$(calc_steps "$SEG_NS" "$dt_ps")"
  log "Per-segment nsteps = $steps"

  mkdir -p logs

  for i in $(seq -w 01 "$nseg"); do
    seg="${DEFNM_PREFIX}${i}"
    mdp_seg="${seg}.mdp"
    tpr_seg="${seg}.tpr"
    log "=== Preparing segment $i ($SEG_NS ns) ==="

    write_seg_mdp "$MDP_PROD" "$mdp_seg" "$steps"

    if [[ "$i" == "01" ]]; then
      # Start from equilibrated structure
      "$GMX_CMD" grompp -f "$mdp_seg" -c "$C0" -p "$TOP" -n "$NDX" -o "$tpr_seg" -maxwarn "$MAXWARN" \
        2>&1 | tee "logs/${seg}_grompp.log"
      "$GMX_CMD" mdrun -deffnm "$seg" -ntomp "$NTOMP" -pin "$PIN" -dlb "$DLB" $(gpu_flags) \
        2>&1 | tee "logs/${seg}_mdrun.log"
    else
      prev=$(printf "%s%02d" "$DEFNM_PREFIX" $((10#$i - 1)))
      # Continue from previous GRO+CPT
      "$GMX_CMD" grompp -f "$mdp_seg" -c "${prev}.gro" -t "${prev}.cpt" -p "$TOP" -n "$NDX" -o "$tpr_seg" -maxwarn "$MAXWARN" \
        2>&1 | tee "logs/${seg}_grompp.log"
      "$GMX_CMD" mdrun -deffnm "$seg" -ntomp "$NTOMP" -pin "$PIN" -dlb "$DLB" $(gpu_flags) \
        2>&1 | tee "logs/${seg}_mdrun.log"
    fi
  done

  log "All segments finished."
  echo "To concatenate trajectories (keep PBC treatment consistent with your analysis!):"
  echo "  echo $(printf '%s%02d.xtc ' \"$DEFNM_PREFIX\" $(seq -w 01 \"$nseg\")) | xargs -n 1 -I {} echo {} > xtc_list.txt"
  echo "  $GMX_CMD trjcat -f $(printf '%s%02d.xtc ' \"$DEFNM_PREFIX\" $(seq -w 01 \"$nseg\")) -o prod_1us.xtc -cat"
  echo "  $GMX_CMD eneconv -f $(printf '%s%02d.edr ' \"$DEFNM_PREFIX\" $(seq -w 01 \"$nseg\")) -o prod_1us.edr"
}

main "$@"
