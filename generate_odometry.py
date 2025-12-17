#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

KITTI_ROOT = Path("/home/koustubh/Downloads/KITTI/combined")  # your dataset root
SEQ = "01"
OUT_ROOT = Path(f"/home/koustubh/Downloads/KITTI/outputs/{SEQ}")  # where KISS-ICP writes runs

def run_kiss_icp():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["kiss_icp_out_dir"] = str(OUT_ROOT)

    cmd = [
        "kiss_icp_pipeline",
        "--dataloader", "kitti",
        "--sequence", SEQ,
        str(KITTI_ROOT),
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, env=env, check=True)

def find_latest_run_dir() -> Path:
    latest = OUT_ROOT / "latest"
    if latest.is_symlink() or latest.exists():
        # resolve symlink to actual timestamped folder
        return latest.resolve()

    # fallback: pick most recent timestamped dir
    dirs = [p for p in OUT_ROOT.iterdir() if p.is_dir()]
    if not dirs:
        raise FileNotFoundError(f"No run directories found in {OUT_ROOT}")
    return max(dirs, key=lambda p: p.stat().st_mtime)

def main():
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

if __name__ == "__main__":
    main()
