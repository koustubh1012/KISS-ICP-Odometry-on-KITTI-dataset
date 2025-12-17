#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

KITTI_ROOT = Path("/home/koustubh/Downloads/KITTI/combined")
SEQ = "01"
OUT_ROOT = Path(f"/home/koustubh/Downloads/KITTI/outputs/{SEQ}")

def run_kiss_icp():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["kiss_icp_out_dir"] = str(OUT_ROOT)

    cmd = [
        "kiss_icp_pipeline",
        "--dataloader", "kitti",
        "--sequence", SEQ,
        "--visualize",
        str(KITTI_ROOT),
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, env=env, check=True)

def find_latest_run_dir() -> Path:
    latest = OUT_ROOT / "latest"
    if latest.exists():
        return latest.resolve(strict=False)

    dirs = [p for p in OUT_ROOT.iterdir() if p.is_dir()]
    if not dirs:
        raise FileNotFoundError(f"No run directories found in {OUT_ROOT}")
    return max(dirs, key=lambda p: p.stat().st_mtime)

def evaluate_with_evo(run_dir: Path):
    gt = run_dir / f"{SEQ}_gt_kitti.txt"
    est = run_dir / f"{SEQ}_poses_kitti.txt"

    if not gt.exists() or not est.exists():
        raise FileNotFoundError(f"Missing GT/EST files in {run_dir}")

    results_dir = run_dir / "evo_results"
    results_dir.mkdir(exist_ok=True)

    # APE (Absolute Pose Error)
    ape_cmd = [
        "evo_ape", "kitti", str(gt), str(est),
        "-a", "--plot", "--plot_mode", "xyz",
        "--save_plot", str(results_dir / f"ape_{SEQ}.png")
    ]

    # RPE (Relative Pose Error)
    rpe_cmd = [
        "evo_rpe", "kitti", str(gt), str(est),
        "-a", "--plot", "--plot_mode", "xyz",
        "--save_plot", str(results_dir / f"rpe_{SEQ}.png")
    ]

    # Trajectory overlay (GT vs EST)
    traj_cmd = [
        "evo_traj", "kitti", str(gt), str(est),
        "-p", "--plot_mode", "xyz",
        "--save_plot", str(results_dir / f"traj_{SEQ}.png")
    ]

    print("\nRunning EVO APE:", " ".join(ape_cmd))
    with open(results_dir / "ape_stats.txt", "w") as f:
        subprocess.run(ape_cmd, check=True, stdout=f, stderr=subprocess.STDOUT)

    print("Running EVO RPE:", " ".join(rpe_cmd))
    with open(results_dir / "rpe_stats.txt", "w") as f:
        subprocess.run(rpe_cmd, check=True, stdout=f, stderr=subprocess.STDOUT)

    print("Running EVO TRAJ:", " ".join(traj_cmd))
    with open(results_dir / "traj_stats.txt", "w") as f:
        subprocess.run(traj_cmd, check=True, stdout=f, stderr=subprocess.STDOUT)

    print("\n✅ Saved EVO outputs to:", results_dir)
    print(" -", results_dir / f"ape_{SEQ}.png")
    print(" -", results_dir / f"rpe_{SEQ}.png")
    print(" -", results_dir / f"traj_{SEQ}.png")
    print(" - ape_stats.txt / rpe_stats.txt / traj_stats.txt")


def main():
    run_kiss_icp()  # NOTE: with --visualize this may block until you close the window
    run_dir = find_latest_run_dir()
    print("Latest run dir:", run_dir)

    gt = run_dir / f"{SEQ}_gt_kitti.txt"
    est = run_dir / f"{SEQ}_poses_kitti.txt"

    print("GT exists? ", gt.exists(), gt)
    print("EST exists?", est.exists(), est)

    if not (gt.exists() and est.exists()):
        print("\nFiles in run dir:")
        for p in sorted(run_dir.iterdir()):
            print(" -", p.name)
    
    evaluate_with_evo(run_dir)


if __name__ == "__main__":
    main()
