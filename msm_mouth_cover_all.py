#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MSM/TICA analysis for mouth–cover gating in CypX
Using precomputed mouth_cover_<SYS>.dat files (dmouth, dcover).

Expected files:
  ./<SYS>/mouth_cover_<SYS>.dat   for SYS in [APO, AND, EST, PIY, TES]
Each .dat file: two columns, [dmouth, dcover] (same units as XVG 2nd column).

Macrostate definition (Open/Intermediate/Closed):
  Uses pooled centroids from Figure 6 (global centroids) and nearest-centroid assignment.
  Centroids file (preferred):
    pooled_centroids_A.csv   (columns include state, mouth_A, cover_A)
  Fallback:
    pooled_centroids_nm.csv  (columns include state, mouth_nm, cover_nm)

This ensures MSM macrostates are consistent with Figure 6 / Table 1.
"""

import numpy as np

# --- compatibility patch for NumPy >= 2.0 (PyEMMA still uses np.bool) ---
if not hasattr(np, "bool"):
    np.bool = bool  # or np.bool_

import pyemma
from sklearn.preprocessing import StandardScaler
from pathlib import Path
import pandas as pd

# ---------- user settings ----------
SYSTEMS = ["APO", "AND", "EST", "PIY", "TES"]

# lag times in frames (adjust if needed)
TICA_LAG = 10
MSM_LAG = 20

# number of microstates (k-means)
N_MICRO = 100

# random seed for reproducibility
RANDOM_STATE = 42


def load_mc_dat(path: Path) -> np.ndarray:
    """Load mouth_cover_<SYS>.dat -> array (n_frames, 2) columns [dmouth, dcover]."""
    arr = np.loadtxt(path)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 2)
    return arr


def read_pooled_centroids(here: Path):
    """
    Read pooled centroids from pooled_centroids_A.csv or pooled_centroids_nm.csv.
    Return:
      centroids (3,2) in same units as file,
      state_names list aligned with centroids rows (Open/Intermediate/Closed).
    """
    fA = here / "pooled_centroids_A.csv"
    fnm = here / "pooled_centroids_nm.csv"

    if fA.exists():
        df = pd.read_csv(fA)
        # expect columns: state, mouth_A, cover_A
        for col in ["state", "mouth_A", "cover_A"]:
            if col not in df.columns:
                raise ValueError(f"{fA} missing column '{col}'. Found: {list(df.columns)}")
        df = df.copy()
        df["state"] = df["state"].astype(str)
        # normalize state strings
        df["state"] = df["state"].str.strip().str.capitalize()
        df = df[df["state"].isin(["Open", "Intermediate", "Closed"])]

        # enforce order Open, Intermediate, Closed
        order = ["Open", "Intermediate", "Closed"]
        df = df.set_index("state").loc[order].reset_index()

        cent = df[["mouth_A", "cover_A"]].to_numpy(dtype=float)
        names = df["state"].tolist()
        units = "A"
        return cent, names, units

    if fnm.exists():
        df = pd.read_csv(fnm)
        # expect columns: state, mouth_nm, cover_nm
        for col in ["state", "mouth_nm", "cover_nm"]:
            if col not in df.columns:
                raise ValueError(f"{fnm} missing column '{col}'. Found: {list(df.columns)}")
        df = df.copy()
        df["state"] = df["state"].astype(str)
        df["state"] = df["state"].str.strip().str.capitalize()
        df = df[df["state"].isin(["Open", "Intermediate", "Closed"])]

        order = ["Open", "Intermediate", "Closed"]
        df = df.set_index("state").loc[order].reset_index()

        cent = df[["mouth_nm", "cover_nm"]].to_numpy(dtype=float)
        names = df["state"].tolist()
        units = "nm"
        return cent, names, units

    raise FileNotFoundError(
        f"Cannot find pooled centroids file in {here}. "
        f"Expected pooled_centroids_A.csv or pooled_centroids_nm.csv"
    )


def guess_units_from_data(all_concat: np.ndarray) -> str:
    """
    Very simple heuristic:
      if median dmouth > 10 -> likely Å
      else -> likely nm
    """
    med = float(np.median(all_concat[:, 0]))
    return "A" if med > 10.0 else "nm"


def convert_centroids_to_data_units(centroids: np.ndarray, cent_units: str, data_units: str) -> np.ndarray:
    """Convert centroids to match data units (nm <-> Å)."""
    if cent_units == data_units:
        return centroids
    # 1 nm = 10 Å
    if cent_units == "A" and data_units == "nm":
        return centroids / 10.0
    if cent_units == "nm" and data_units == "A":
        return centroids * 10.0
    raise ValueError(f"Unknown unit conversion: cent_units={cent_units}, data_units={data_units}")


def nearest_centroid_labels(X: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    """
    Assign each row of X (n,2) to nearest centroid (k,2) by Euclidean distance.
    Return integer labels 0..k-1.
    """
    # distances squared: (n,k)
    d2 = ((X[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(d2, axis=1)


def main():
    here = Path(".").resolve()
    print(f"[INFO] Working directory: {here}")

    # ---------- 1. load data ----------
    data_raw = []
    lengths = []

    for sys in SYSTEMS:
        f = here / sys / f"mouth_cover_{sys}.dat"
        if not f.exists():
            raise FileNotFoundError(f"Missing file: {f}")
        arr = load_mc_dat(f)
        data_raw.append(arr)
        lengths.append(arr.shape[0])
        print(f"[INFO] {sys}: loaded {f}, shape={arr.shape}")

    all_concat = np.concatenate(data_raw, axis=0)
    data_units = guess_units_from_data(all_concat)
    print(f"[INFO] Detected data units ~ '{data_units}' (heuristic).")

    # ---------- 2. pooled z-score (for TICA/MSM feature processing) ----------
    scaler = StandardScaler()
    scaler.fit(all_concat)
    data_z = [scaler.transform(a) for a in data_raw]
    print("[INFO] Z-score normalization done on pooled data.")

    # ---------- 3. TICA ----------
    print(f"[INFO] Running TICA with lag={TICA_LAG} frames...")
    tica = pyemma.coordinates.tica(data_z, lag=TICA_LAG, dim=2)
    Y = tica.get_output()
    print("[INFO] TICA done. Eigenvalues:", tica.eigenvalues)

    # ---------- 4. k-means clustering into microstates ----------
    print(f"[INFO] Clustering into {N_MICRO} microstates (k-means)...")
    cl = pyemma.coordinates.cluster_kmeans(
        Y, k=N_MICRO, max_iter=100, stride=10, fixed_seed=RANDOM_STATE
    )
    dtrajs = cl.dtrajs
    print("[INFO] k-means clustering finished.")

    # ---------- 5. MSM per system ----------
    msms = {}
    for sys, dt in zip(SYSTEMS, dtrajs):
        msm = pyemma.msm.estimate_markov_model([dt], lag=MSM_LAG)
        msms[sys] = msm
        print(f"[INFO] {sys}: active_fraction={msm.active_state_fraction:.3f}, nstates={msm.nstates}")

    # ---------- 6. Macrostate assignment using pooled centroids (Figure 6) ----------
    print("[INFO] Defining macrostates via pooled centroids (Figure 6) and nearest-centroid assignment...")
    centroids_raw, cent_state_names, cent_units = read_pooled_centroids(here)
    centroids = convert_centroids_to_data_units(centroids_raw, cent_units, data_units)
    # centroids order is [Open, Intermediate, Closed]
    print(f"[INFO] Loaded pooled centroids ({cent_units}) and converted to data units ({data_units}).")
    for name, c in zip(cent_state_names, centroids):
        print(f"  centroid {name:12s}: ({c[0]:.6f}, {c[1]:.6f}) [{data_units}]")

    # Frame-level macro labels for each system based on ORIGINAL (non-zscored) data
    macro_labels_by_sys = []
    for sys, arr in zip(SYSTEMS, data_raw):
        lab = nearest_centroid_labels(arr, centroids)  # 0=Open,1=Intermediate,2=Closed
        macro_labels_by_sys.append(lab)

    # pooled frame-level arrays for micro->macro majority vote
    dtraj_all = np.concatenate(dtrajs)                 # microstate index per frame
    macro_all = np.concatenate(macro_labels_by_sys)    # macro label per frame (0/1/2)

    # microstate -> macrostate label (0/1/2) by majority vote
    micro_to_macro = np.full(N_MICRO, -1, dtype=int)
    for s in range(N_MICRO):
        idx = (dtraj_all == s)
        if not np.any(idx):
            continue
        counts = np.bincount(macro_all[idx], minlength=3)
        micro_to_macro[s] = int(np.argmax(counts))

    # convenience mapping int -> name
    macro_id_to_name = {0: "open", 1: "intermediate", 2: "closed"}

    uniq, cnt = np.unique(micro_to_macro[micro_to_macro >= 0], return_counts=True)
    print("[INFO] Microstate -> macrostate assignment (counts of microstates):")
    for u, c in zip(uniq, cnt):
        print(f"  {macro_id_to_name[int(u)]:12s}: {c} microstates")

    # ---------- 7. Per-system macro populations + closed->open MFPT ----------
    out_lines = []
    header = "#sys  pop_open  pop_intermediate  pop_closed  MFPT_closed_to_open(frames)\n"
    out_lines.append(header)

    for sys in SYSTEMS:
        msm = msms[sys]

        # labels_model: macro label for each MSM model state (0..msm.nstates-1)
        # msm.active_set gives original microstate indices for each model state
        labels_model = np.full(msm.nstates, -1, dtype=int)
        for i, micro in enumerate(msm.active_set):
            labels_model[i] = micro_to_macro[int(micro)]

        pi_model = msm.stationary_distribution

        pop_O = float(np.sum(pi_model[labels_model == 0]))
        pop_I = float(np.sum(pi_model[labels_model == 1]))
        pop_C = float(np.sum(pi_model[labels_model == 2]))

        closed_states = [i for i in range(msm.nstates) if labels_model[i] == 2]
        open_states   = [i for i in range(msm.nstates) if labels_model[i] == 0]

        if closed_states and open_states:
            mfpt_c2o = float(msm.mfpt(closed_states, open_states))
        else:
            mfpt_c2o = np.nan

        line = f"{sys:4s}  {pop_O:8.4f}  {pop_I:8.4f}  {pop_C:8.4f}  {mfpt_c2o:12.4f}\n"
        out_lines.append(line)
        print("[RESULT]", line.strip())

    # ---------- 8. write summary ----------
    out_file = here / "msm_mouth_cover_summary.dat"
    with out_file.open("w") as f:
        f.writelines(out_lines)

    print(f"[INFO] Summary written to {out_file}")
    print("[INFO] NOTE: These macrostates are consistent with Figure 6 pooled centroids.")


if __name__ == "__main__":
    main()
