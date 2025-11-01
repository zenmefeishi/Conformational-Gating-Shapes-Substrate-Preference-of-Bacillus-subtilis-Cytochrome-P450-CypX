# CypX–APO — MD Reproducibility Pack

This folder provides **minimal, machine‑readable inputs** and **commands** to verify the
molecular dynamics (MD) setup for the APO system of *Bacillus subtilis* CYP134A1 (CypX).  
It complements the manuscript’s **Data and Software Availability** statement.

> Generated on 2025-11-01 from your uploaded APO files.

## What’s included
- `metadata/MD_METHODS.md` — One‑page methods summary (time step, cutoffs, PME, LINCS, thermostat/barostat, stage lengths, topology includes, index groups).
- `prep_commands.txt` — Three commands to build/run **min → eq → prod** TPRs with GROMACS.
- Stage inputs: `step4.0_minimization.mdp/.tpr/.gro`, `step4.1_equilibration.mdp/.tpr/.gro`, `step5_production.mdp/.tpr/.gro`
- Topology & params: `topol.top`, `PROA.itp`, `HEME.itp`, `MG.itp`, `SOD.itp`, `CLA.itp`, `TIP3.itp`
- Index: `index.ndx` (default gating pairs in MD_METHODS.md; adjust if different)

## Quick start
```bash
# 1) (Optional) Activate your GROMACS environment
# module load gromacs/2023    # or source /path/to/gromacs/bin/GMXRC

# 2) Rebuild and run each stage (no trajectories required by JCIM)
bash prep_commands.txt
```

## Notes
- **No large trajectories** (`*.xtc/*.trr/*.edr`) are included per journal policy.
- All **stage lengths** are computed from `nsteps × dt` in the respective `.mdp` files.
- Exact GROMACS build string can be recorded via:
  ```bash
  gmx dump -s step5_1.tpr | head -n 80
  ```

## Reuse / Citation
Please cite the associated manuscript and repository release. If you make changes,
create a new tagged release so Zenodo can mint a DOI.

---
If any gating atom pairs differ from the defaults (Cα–Cα: PHE96–SER206; ARG233–THR241),
update them in `metadata/MD_METHODS.md` and (optionally) supply an `index.ndx` with
named groups for `d_in`/`d_out`.
