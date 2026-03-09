#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# =============================
# CONFIG
# =============================
BASE = "/mnt/e/article_2/xvg&csv"
SYSTEMS = ["APO", "PIY", "AND", "EST", "TES"]  # output one figure per system

MOUTH_FN = "d_mouth.xvg"
COVER_FN = "d_cover.xvg"

# Time window: 0–1000 ns in ps
TMIN_PS = 0.0
TMAX_PS = 1_000_000.0

# Pooled clustering
K = 3
RANDOM_STATE = 42
N_INIT = 50

# Plot style
DPI = 300
POINT_SIZE = 3
POINT_ALPHA = 0.35
STAR_SIZE = 110

# Units
NM_TO_A = 10.0  # 1 nm = 10 Å

# Axis range control
# mode = "auto_global": use pooled (all systems) global min/max once, then fix for all panels
# mode = "manual": use user-specified fixed range below
AXIS_MODE = "auto_global"

# Only used when AXIS_MODE == "manual"
X_RANGE_A = (25.0, 33.0)  # d_mouth in Å
Y_RANGE_A = (20.5, 29.5)  # d_cover in Å

# =============================
# Helpers
# =============================
def read_xvg(path: str) -> pd.DataFrame:
    """Read GROMACS .xvg with 2 columns: time(ps), value(nm)."""
    xs, ys = [], []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line[0] in ("#", "@"):
                continue
            parts = re.split(r"\s+", line)
            if len(parts) < 2:
                continue
            try:
                t = float(parts[0])
                v = float(parts[1])
            except ValueError:
                continue
            xs.append(t)
            ys.append(v)
    if len(xs) == 0:
        raise ValueError(f"No numeric data read from: {path}")
    return pd.DataFrame({"t_ps": xs, "v_nm": ys})


def load_system(sysname: str) -> pd.DataFrame:
    """Load mouth/cover, inner-join by time, filter by time window."""
    d = os.path.join(BASE, sysname)
    mouth_p = os.path.join(d, MOUTH_FN)
    cover_p = os.path.join(d, COVER_FN)

    if not (os.path.exists(mouth_p) and os.path.exists(cover_p)):
        return pd.DataFrame()

    m = read_xvg(mouth_p).rename(columns={"v_nm": "mouth_nm"})
    c = read_xvg(cover_p).rename(columns={"v_nm": "cover_nm"})

    df = pd.merge(m, c, on="t_ps", how="inner")
    df = df[(df["t_ps"] >= TMIN_PS) & (df["t_ps"] <= TMAX_PS)].copy()
    df["system"] = sysname

    if df.empty:
        raise ValueError(f"{sysname}: empty after filtering {TMIN_PS}-{TMAX_PS} ps.")
    return df


def assign_state_names(centroids_nm: np.ndarray) -> dict:
    """
    Map cluster IDs to state names based on openness score (mouth + cover).
    Open: max(score); Closed: min(score); Intermediate: remaining.
    """
    score = centroids_nm[:, 0] + centroids_nm[:, 1]
    open_id = int(np.argmax(score))
    closed_id = int(np.argmin(score))
    inter_id = [i for i in range(len(score)) if i not in (open_id, closed_id)][0]
    return {open_id: "Open", inter_id: "Intermediate", closed_id: "Closed"}


def count_fraction_table(all_df: pd.DataFrame, used_systems: list) -> pd.DataFrame:
    """Return pivot table: rows system, cols Open/Intermediate/Closed, values fraction."""
    pop = (all_df.groupby(["system", "state"]).size().rename("n").reset_index())
    total = all_df.groupby("system").size().rename("N").reset_index()
    pop = pop.merge(total, on="system", how="left")
    pop["fraction"] = pop["n"] / pop["N"]

    table = pop.pivot_table(index="system", columns="state", values="fraction", fill_value=0.0)
    for col in ["Open", "Intermediate", "Closed"]:
        if col not in table.columns:
            table[col] = 0.0
    table = table[["Open", "Intermediate", "Closed"]].loc[used_systems]
    return table


def get_global_axis_limits_A(all_df: pd.DataFrame) -> tuple:
    """Compute global axis limits in Å from pooled data (with small padding)."""
    x = all_df["mouth_A"].to_numpy()
    y = all_df["cover_A"].to_numpy()
    xmin, xmax = float(np.min(x)), float(np.max(x))
    ymin, ymax = float(np.min(y)), float(np.max(y))

    pad_x = 0.02 * (xmax - xmin) if xmax > xmin else 0.5
    pad_y = 0.02 * (ymax - ymin) if ymax > ymin else 0.5
    return (xmin - pad_x, xmax + pad_x, ymin - pad_y, ymax + pad_y)


def plot_one_system(df_sys: pd.DataFrame,
                    sysname: str,
                    centroids_A: np.ndarray,
                    id2state: dict,
                    frac_row: pd.Series,
                    axis_limits: tuple,
                    out_png: str,
                    out_pdf: str):
    """Plot a single system panel with fixed axis limits in Å."""
    xmin, xmax, ymin, ymax = axis_limits

    fig = plt.figure(figsize=(7, 7), dpi=DPI)
    ax = plt.gca()

    # Plot points by state (order fixed)
    state_order = ["Open", "Intermediate", "Closed"]
    for st in state_order:
        sub = df_sys[df_sys["state"] == st]
        if sub.empty:
            continue
        ax.scatter(sub["mouth_A"], sub["cover_A"],
                   s=POINT_SIZE, alpha=POINT_ALPHA, label=st)

    # Plot pooled centroids
    for cid in range(K):
        st = id2state[cid]
        ax.scatter(centroids_A[cid, 0], centroids_A[cid, 1],
                   s=STAR_SIZE, marker="*", edgecolors="k")
        ax.text(centroids_A[cid, 0], centroids_A[cid, 1],
                f"  {st}", va="center", fontsize=18)

    ax.set_title(sysname, fontsize=22, pad=10)

    # ✅ Axis-title fonts bigger
    ax.set_xlabel(r"$d_{mouth}$ ($\AA$)", fontsize=22)
    ax.set_ylabel(r"$d_{cover}$ ($\AA$)", fontsize=22)

    # ✅ Tick label size (optional but recommended)
    ax.tick_params(axis="both", labelsize=16)

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # fraction box
    txt = (
        f"Open {frac_row['Open']*100:.1f}%\n"
        f"Inter {frac_row['Intermediate']*100:.1f}%\n"
        f"Closed {frac_row['Closed']*100:.1f}%"
    )
    ax.text(0.02, 0.98, txt,
            transform=ax.transAxes,
            ha="left", va="top", fontsize=14,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.90, linewidth=0.8))

    ax.legend(loc="lower right", fontsize=13, frameon=True, markerscale=6)

    fig.tight_layout()
    fig.savefig(out_png)
    fig.savefig(out_pdf)
    plt.close(fig)


# =============================
# Main
# =============================
def main():
    # 1) load systems
    dfs = []
    used = []
    for s in SYSTEMS:
        df = load_system(s)
        if not df.empty:
            dfs.append(df)
            used.append(s)

    if not dfs:
        print("ERROR: No systems found with both d_mouth.xvg and d_cover.xvg", file=sys.stderr)
        sys.exit(1)

    all_df = pd.concat(dfs, ignore_index=True)

    # 2) pooled clustering on nm values (z-scored)
    X = all_df[["mouth_nm", "cover_nm"]].to_numpy(dtype=float)
    scaler = StandardScaler()
    Xz = scaler.fit_transform(X)

    km = KMeans(n_clusters=K, n_init=N_INIT, random_state=RANDOM_STATE)
    km.fit(Xz)

    all_df["cluster"] = km.labels_.astype(int)

    # 3) pooled centroids back to nm
    centroids_nm = scaler.inverse_transform(km.cluster_centers_)

    # 4) map cluster IDs -> state names
    id2state = assign_state_names(centroids_nm)
    all_df["state"] = all_df["cluster"].map(id2state)

    # 5) convert to Å for plotting/output
    all_df["mouth_A"] = all_df["mouth_nm"] * NM_TO_A
    all_df["cover_A"] = all_df["cover_nm"] * NM_TO_A
    centroids_A = centroids_nm * NM_TO_A

    # 6) output centroids
    cent_df = pd.DataFrame(
        [{"cluster": cid,
          "state": id2state[cid],
          "mouth_A": centroids_A[cid, 0],
          "cover_A": centroids_A[cid, 1],
          "mouth_nm": centroids_nm[cid, 0],
          "cover_nm": centroids_nm[cid, 1]}
         for cid in range(K)]
    )
    cent_out = os.path.join(BASE, "pooled_centroids_A.csv")
    cent_df.to_csv(cent_out, index=False, float_format="%.6f")

    # 7) table 1 populations
    table = count_fraction_table(all_df, used)
    table_out = os.path.join(BASE, "Table1_state_populations_pooled.csv")
    table.to_csv(table_out, float_format="%.6f")

    # 8) fixed axis limits
    if AXIS_MODE == "manual":
        axis_limits = (X_RANGE_A[0], X_RANGE_A[1], Y_RANGE_A[0], Y_RANGE_A[1])
    else:
        axis_limits = get_global_axis_limits_A(all_df)

    # 9) plot one figure per system (PNG + PDF)
    for s in used:
        df_sys = all_df[all_df["system"] == s].copy()
        out_png = os.path.join(BASE, f"Figure6_{s}_pooled_A.png")
        out_pdf = os.path.join(BASE, f"Figure6_{s}_pooled_A.pdf")
        plot_one_system(df_sys, s, centroids_A, id2state, table.loc[s], axis_limits, out_png, out_pdf)
        print("Wrote:", out_png)
        print("Wrote:", out_pdf)

    # 10) print summary
    print("Wrote:", table_out)
    print("Wrote:", cent_out)
    print("\nPooled centroids (Å):")
    for cid in range(K):
        print(f"  {id2state[cid]:12s}: mouth={centroids_A[cid,0]:.3f}  cover={centroids_A[cid,1]:.3f}")
    print("\nSystems used:", ", ".join(used))
    print(f"Time window: {TMIN_PS/1000:.1f}–{TMAX_PS/1000:.1f} ns")
    if AXIS_MODE == "manual":
        print(f"Axis limits (manual, Å): x={X_RANGE_A}, y={Y_RANGE_A}")
    else:
        print(f"Axis limits (auto_global, Å): x=[{axis_limits[0]:.2f},{axis_limits[1]:.2f}] "
              f"y=[{axis_limits[2]:.2f},{axis_limits[3]:.2f}]")


if __name__ == "__main__":
    main()
