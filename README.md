# KISS-ICP Odometry on KITTI dataset

A small pipeline to run KISS-ICP on KITTI odometry sequences and evaluate the results using the EVO toolkit.

This repository contains a convenience script (generate_odometry.py) that:
- Runs the KISS-ICP pipeline on a specified KITTI sequence
- Finds the latest run directory containing generated poses
- Evaluates results with EVO (APE, RPE, trajectory) and saves plots/statistics

## Quick start
1. Place this repository somewhere on your machine and make sure KITTI data access is configured for the KISS-ICP pipeline.
2. From the repository root, run the script with a KITTI sequence id (default is 00):

   ```bash
   python generate_odometry.py 00
   ```

## What the script does
- Calls kiss_icp_pipeline with the specified KITTI sequence and sets an output directory.
- Locates the latest run directory inside `outputs/<SEQ>/` (or the `outputs/<SEQ>/latest` symlink if present).
- Looks for two files inside the run directory:
  - `<SEQ>_gt_kitti.txt` (ground-truth poses in KITTI format)
  - `<SEQ>_poses_kitti.txt` (estimated poses from KISS-ICP, KITTI format)
- Runs EVO commands to compute and save:
  - Absolute Pose Error (APE) plot and stats
  - Relative Pose Error (RPE) plot and stats
  - Trajectory overlay plot and stats
- All EVO outputs are saved in `run_dir/evo_results/`

## Outputs
- `outputs/<SEQ>/<run_dir>/evo_results/ape_<SEQ>.png`
- `outputs/<SEQ>/<run_dir>/evo_results/rpe_<SEQ>.png`
- `outputs/<SEQ>/<run_dir>/evo_results/traj_<SEQ>.png`
- `outputs/<SEQ>/<run_dir>/evo_results/ape_stats.txt`
- `outputs/<SEQ>/<run_dir>/evo_results/rpe_stats.txt`
- `outputs/<SEQ>/<run_dir>/evo_results/traj_stats.txt`

## Setup (Conda environment)

This repository includes an environment specification (environment.yml) to create a reproducible Conda environment named `kitti_lo`.

To create the environment:

```bash
conda env create -f environment.yml
```

If you already have the environment and want to update it:

```bash
conda env update -f environment.yml --prune
```

Activate the environment before running the script:

```bash
conda activate kitti_lo
```

If you prefer not to activate the environment, you can run the script directly using `conda run`:

```bash
conda run -n kitti_lo python generate_odometry.py 00
```

Notes:
- The environment installs dependencies via conda and pip (see environment.yml). The pip section includes `kiss-icp` and `evo` — ensure these packages are available or replace with the appropriate installation method for your system.

## Helper scripts

Two helper scripts are included to speed up setup and running:

- `create_env.sh` — creates or updates the `kitti_lo` environment from environment.yml
- `run_odometry.sh` — runs `generate_odometry.py` inside the `kitti_lo` environment using `conda run` (accepts an optional sequence id argument)

Make the helper scripts executable before use:

```bash
chmod +x create_env.sh run_odometry.sh
```

## Running the pipeline

After creating and activating the environment, run the pipeline for a sequence (default `00`):

```bash
python generate_odometry.py 00
```

Or use the helper script (no manual activation required):

```bash
./run_odometry.sh 00
```

## Notes & Troubleshooting
- If `kiss_icp_pipeline` is not in PATH, the script will fail. Make sure you can run `kiss_icp_pipeline` from the shell.
- If EVO commands are missing, install evo (`pip install evo`) and ensure the evo scripts are on your PATH.
- If the script cannot find the GT or estimated pose files, inspect the run directory (printed by the script) to verify file names and contents.
- The script expects KITTI-formatted pose files. If you use a different format, convert to the KITTI pose format first.
- If `kiss_icp_pipeline` is not found, ensure the KISS-ICP binary or entry point is installed and available on your PATH inside the conda environment. You can test by running `conda run -n kitti_lo kiss_icp_pipeline --help`.
- If `evo` commands are missing, install `evo` in the environment (`pip install evo`) or verify the pip-installed scripts are on PATH.

## Contributing
- Feel free to open issues or send pull requests to improve documentation or add features (arg parsing, additional output formats, automated plotting customization).

## License & Credit
- This README and helper script are provided as-is. The KISS-ICP pipeline and EVO are external projects; please refer to their respective repositories and licenses for usage details.

