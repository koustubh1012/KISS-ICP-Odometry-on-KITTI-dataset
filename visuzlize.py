#!/usr/bin/env python3
import numpy as np
import open3d as o3d
from pathlib import Path

RUN_DIR = Path("/home/koustubh/Downloads/KITTI/outputs/01/latest")  # adjust as needed
SEQ = "01"

EST_FILE = RUN_DIR / f"{SEQ}_poses_kitti.txt"
GT_FILE  = RUN_DIR / f"{SEQ}_gt_kitti.txt"   # optional overlay

def load_kitti_poses(path: Path) -> np.ndarray:
    # KITTI pose txt: each line = 12 numbers (3x4)
    P = np.loadtxt(str(path)).reshape(-1, 3, 4)
    T = np.repeat(np.eye(4)[None, :, :], P.shape[0], axis=0)
    T[:, :3, :4] = P
    return T

def make_lineset(points_xyz: np.ndarray):
    lines = [[i, i+1] for i in range(len(points_xyz) - 1)]
    ls = o3d.geometry.LineSet(
        points=o3d.utility.Vector3dVector(points_xyz),
        lines=o3d.utility.Vector2iVector(lines),
    )
    return ls

def main():
    est_T = load_kitti_poses(EST_FILE)
    est_xyz = est_T[:, :3, 3]

    geometries = []

    est_ls = make_lineset(est_xyz)
    est_ls.paint_uniform_color([0, 1, 0])  # green
    geometries.append(est_ls)

    # Optional: overlay GT if available
    if GT_FILE.exists():
        gt_T = load_kitti_poses(GT_FILE)
        gt_xyz = gt_T[:, :3, 3]
        gt_ls = make_lineset(gt_xyz)
        gt_ls.paint_uniform_color([0, 0, 1])  # blue
        geometries.append(gt_ls)

    # Coordinate frame for reference
    geometries.append(o3d.geometry.TriangleMesh.create_coordinate_frame(size=5.0))

    o3d.visualization.draw_geometries(
        geometries,
        window_name=f"KITTI {SEQ} Trajectory (Green=EST, Blue=GT)",
        width=1280,
        height=720,
    )

if __name__ == "__main__":
    main()
