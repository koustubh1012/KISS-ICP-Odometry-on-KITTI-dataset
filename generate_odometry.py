#!/usr/bin/env python3
"""
KITTI Odometry Evaluation Pipeline using KISS ICP and EVO.
This module provides utilities to process KITTI odometry sequences using the KISS ICP
pipeline and evaluate the results using the EVO (Evaluation of Visual Odometry) toolkit.
The script performs the following steps:
1. Runs the KISS ICP pipeline on a specified KITTI sequence
2. Locates the latest run directory with generated poses
3. Computes and visualizes odometry evaluation metrics (APE, RPE, trajectory comparison)
Usage:
    python generate_odometry.py [sequence_number]
    Example:
        python generate_odometry.py 00  # Process KITTI sequence 00
        python generate_odometry.py 05  # Process KITTI sequence 05
Command-line Arguments:
    sequence_number (optional): KITTI sequence ID (default: "00")
Environment Variables:
    kiss_icp_out_dir: Set by the script to specify output directory for KISS ICP
Output:
    - Poses files: {SEQ}_gt_kitti.txt, {SEQ}_poses_kitti.txt
    - Evaluation plots: ape_{SEQ}.png, rpe_{SEQ}.png, traj_{SEQ}.png
    - Statistics: ape_stats.txt, rpe_stats.txt, traj_stats.txt
    All outputs are saved to: outputs/{sequence_number}/evo_results/
Requirements:
    - kiss_icp_pipeline: KISS ICP command-line tool
    - evo: Evaluation of Visual Odometry toolkit (with evo_ape, evo_rpe, evo_traj commands)

"""

import os
import subprocess
from pathlib import Path
import sys

KITTI_ROOT = Path(__file__).parent
SEQ = sys.argv[1] if len(sys.argv) > 1 else "00"
OUT_ROOT = KITTI_ROOT / "outputs" / SEQ

def run_kiss_icp():
    """
    Execute the KISS ICP pipeline for KITTI odometry sequence processing.
    
    This function sets up and runs the kiss_icp_pipeline command with KITTI dataset
    configuration. It creates the output directory if it doesn't exist and passes
    the output path as an environment variable to the subprocess.
    
    The pipeline processes a single KITTI sequence specified by SEQ variable
    and runs with visualization enabled.
    
    Raises:
        CalledProcessError: If the kiss_icp_pipeline subprocess fails or returns
                          a non-zero exit code.
        FileNotFoundError: If the kiss_icp_pipeline command is not found in PATH.
    """
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
    """
    Evaluate odometry results using EVO (Evaluation Metrics for Odometry).

    Computes and visualizes Absolute Pose Error (APE), Relative Pose Error (RPE),
    and trajectory overlay comparisons between ground truth and estimated poses.

    Args:
        run_dir (Path): Directory containing ground truth and estimated pose files.
                        Expected files:
                        - {SEQ}_gt_kitti.txt: Ground truth poses in KITTI format
                        - {SEQ}_poses_kitti.txt: Estimated poses in KITTI format

    Raises:
        FileNotFoundError: If ground truth or estimated pose files are missing.

    Returns:
        None: Generates evaluation plots and statistics files in run_dir/evo_results/

    Output Files:
        - ape_{SEQ}.png: Absolute Pose Error visualization
        - rpe_{SEQ}.png: Relative Pose Error visualization
        - traj_{SEQ}.png: Trajectory overlay comparison
        - ape_stats.txt: APE statistics and metrics
        - rpe_stats.txt: RPE statistics and metrics
        - traj_stats.txt: Trajectory statistics
    """
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
    """
    Main function to run KISS-ICP odometry estimation and evaluation.
    This function orchestrates the following workflow:
    1. Executes KISS-ICP algorithm for odometry estimation
    2. Locates the latest run directory containing results
    3. Verifies the existence of ground truth and estimated pose files
    4. Lists directory contents if required files are missing
    5. Evaluates the odometry results using EVO (Evaluation of Odometry)
    The function expects:
    - Ground truth file: {SEQ}_gt_kitti.txt
    - Estimated poses file: {SEQ}_poses_kitti.txt
    Returns:
        None
    """

    run_kiss_icp()
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
