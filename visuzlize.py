import time
import numpy as np
import open3d as o3d
from pathlib import Path

VELO_DIR = Path("/home/koustubh/Downloads/KITTI/combined/sequences/00/velodyne")

SLEEP_SEC = 0.02
VOXEL = 0.20  # increase if slow

def load_bin(bin_path: Path):
    pts = np.fromfile(str(bin_path), dtype=np.float32).reshape(-1, 4)[:, :3]
    return pts

bin_files = sorted(VELO_DIR.glob("*.bin"))
print("num scans:", len(bin_files), "first:", bin_files[0])

vis = o3d.visualization.Visualizer()
vis.create_window("Step1: LiDAR scan playback (sensor frame)", 1280, 720)

pcd = o3d.geometry.PointCloud()
vis.add_geometry(pcd)

opt = vis.get_render_option()
opt.point_size = 1.0
opt.background_color = np.asarray([0, 0, 0])

ctr = vis.get_view_control()
camera_set = False

for i, f in enumerate(bin_files):
    pts = load_bin(f)
    tmp = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts))
    if VOXEL and VOXEL > 0:
        tmp = tmp.voxel_down_sample(VOXEL)

    pcd.points = tmp.points

    # Make points visible (white)
    npts = np.asarray(pcd.points).shape[0]
    pcd.colors = o3d.utility.Vector3dVector(np.ones((npts, 3), dtype=np.float64))

    if not camera_set and npts > 0:
        center = pcd.get_center()
        ctr.set_lookat(center)
        ctr.set_front([1.0, 0.0, 0.0])
        ctr.set_up([0.0, 0.0, 1.0])
        ctr.set_zoom(0.35)
        camera_set = True
        vis.reset_view_point(True)

    vis.update_geometry(pcd)
    vis.poll_events()
    vis.update_renderer()
    time.sleep(SLEEP_SEC)

