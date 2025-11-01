# Molecular Dynamics Methods — CypX–EST

**Software**  
- GROMACS: *(fill with `gmx --version` for your build, e.g., 2023.x)*

**Force Field & Water**  
- Force field: **CHARMM36 (from topology includes)**  
- Water model: **TIP3P** (solvation with `spc216.gro`)

**Electrostatics & van der Waals**  
- Coulomb type: **PME** (PME)  
- Cutoff scheme: **Verlet**; neighbor list **nstlist = 20**  
- Radii: **rlist = 1.2 nm**, **rcoulomb = 1.2 nm**, **rvdw = 1.2 nm**  

**Constraints & Integration**  
- Constraints: **h-bonds**; algorithm **lincs**, **lincs-order = 4**, **lincs-iter = 1**  
- Integrator: **md**; time step **dt = 0.002 ps**  

**Thermostat & Barostat**  
- Thermostat: **v-rescale** (tau-t = 1.0, ref-t = 300 K)  
- Barostat: **C-rescale** (tau-p = 5.0, ref-p = 1.0 bar, compressibility = 4.5e-5)  

**System Preparation**  
- Box: **dodecahedron**, padding **1.0 nm**  
- Solvent: **spc216**  
- Ions: **Na⁺/Cl⁻** to neutralize and reach **0.15 M** (replace `SOL`)  

**Protocol Durations**  
- Energy minimization: **nsteps = 5000**, **emtol = 1000.0**  
- NPT equilibration: **nsteps = 125000** (≈ 0.125 ns @ dt = 0.001 ps)  
- Production: **1 µs** total, segmented **20 × 50 ns** (per-segment **nsteps = 25000000** at dt = 0.002 ps)  

**Random Seeds**  
- Equilibration: `gen-vel = yes` at `gen-temp/ref-t = 300 K`; `gen-seed = -1`  
- Production: `gen-vel = no`; `gen-seed = (n/a)`  

**Topology Components**  
- Protein moleculetype: `PROA` (include `PROA.itp` if present)  
- Heme: `HEME.itp` (included if present)  
- Ligand (EST): `EST.itp` (see ligand parameter provenance in README)  
- Ions & water parameters: `TIP3.itp` (TIP3P), standard GROMACS ions  

**Notes**  
- Filenames follow the repository convention: `step4.0_minimization`, `step4.1_equilibration`, and `seg_01…seg_20`.  
- Record your exact **GROMACS version** to `metadata/gromacs_version.txt` and hardware to `metadata/hardware_os.md`.  
