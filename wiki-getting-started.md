# Getting Started Guide

Complete step-by-step instructions to set up and run the German Power Grid project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Data Setup](#data-setup)
4. [Verification](#verification)
5. [Running the Project](#running-the-project)
6. [Next Steps](#next-steps)

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Python** | 3.8 | 3.9-3.11 |
| **RAM** | 4 GB | 8 GB |
| **Disk Space** | 2 GB | 5 GB |
| **OS** | Any | Linux/macOS |

### Required Software

**Python 3.8 or higher:**
- Download from https://www.python.org/downloads/
- Verify: `python --version`

**Git (optional but recommended):**
- Download from https://git-scm.com/downloads
- Verify: `git --version`

## Installation

### Step 1: Clone the Repository

Using Git:
```bash
git clone https://github.com/mccloska/German-Power-Grid.git
cd German-Power-Grid
```

Or download manually:
- Visit https://github.com/mccloska/German-Power-Grid
- Click "Code" → "Download ZIP"
- Extract and navigate to folder

### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

✓ Your terminal prompt should now show `(venv)` prefix

### Step 3: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- numpy, pandas, scipy (data processing)
- matplotlib, cartopy (visualization)
- ipython (interactive shell)
- chaosmagpy (geophysics)

**Installation time:** 5-10 minutes (varies by system)

### Step 5: Verify Installation

```bash
python -c "import numpy, pandas, matplotlib, scipy, ipython, cartopy, chaosmagpy; print('✓ All packages installed successfully')"
```

Expected output: `✓ All packages installed successfully`

## Data Setup

### Create Data Directory

```bash
mkdir -p data/gadm36_DEU_shp
cd data
```

### Download CHAOS Magnetic Model

**Option A: Using wget (Linux/macOS)**
```bash
wget http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/CHAOS-7.2.mat
```

**Option B: Using curl**
```bash
curl -O http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/CHAOS-7.2.mat
```

**Option C: Manual download**
- Visit: http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/
- Download: CHAOS-7.2.mat
- Save to: `data/`

**File size:** ~50 MB  
**Verify:** `ls -lh CHAOS-7.2.mat`

### Download German Boundaries Shapefile

```bash
cd gadm36_DEU_shp

# Download and extract
wget https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_DEU_shp.zip
unzip gadm36_DEU_shp.zip

# Verify files
ls gadm36_DEU_1.*
```

Expected files:
- `gadm36_DEU_1.shp` (geometry)
- `gadm36_DEU_1.shx` (index)
- `gadm36_DEU_1.dbf` (attributes)
- `gadm36_DEU_1.prj` (projection)

### Prepare Observatory Data

You need to obtain `IAGA_obs.csv` from the IAGA network:

**Steps:**
1. Visit: https://www.iaga-aiga.org/observatories/
2. Select German/European observatories
3. Export data in IAGA2002 ASCII format
4. Place in `data/` as `IAGA_obs.csv`

**Expected columns:**
```
code, name, latitude, longitude, elevation, Bx, By, Bz, ...
```

### Final Data Structure

```
data/
├── CHAOS-7.2.mat              # ✓ Downloaded
├── IAGA_obs.csv               # ✓ Obtained (May need to provide)
└── gadm36_DEU_shp/
    ├── gadm36_DEU_1.shp       # ✓ Downloaded
    ├── gadm36_DEU_1.shx
    ├── gadm36_DEU_1.dbf
    └── gadm36_DEU_1.prj
```

## Verification

### Check Installation

```bash
cd ..  # Back to project root
python --version          # Should be 3.8+
pip list | grep -E "numpy|pandas|cartopy"  # Check key packages
```

### Check Data Files

```bash
# Verify all required files exist
ls -la data/CHAOS-7.2.mat
ls -la data/gadm36_DEU_shp/gadm36_DEU_1.shp
ls -la data/IAGA_obs.csv
```

### Quick Python Test

```python
python
>>> import numpy as np
>>> import pandas as pd
>>> from scipy.io import loadmat
>>> chaos = loadmat('data/CHAOS-7.2.mat')
>>> print("✓ CHAOS model loaded successfully")
>>> exit()
```

## Running the Project

### Module 1: Geomagnetic Analysis (geomag)

**Start IPython:**
```bash
cd geomag
ipython
```

**Run the pipeline:**
```ipython
%run binder.ipy
```

**Expected output:**
```
Loading observatory data...
Data loaded: 10 stations
Performing SECS interpolation...
Interpolation complete
Generating visualizations...
Results saved to: results/
```

**Output files:**
- `results/field_map.png` - Spatial field map
- `results/gic_distribution.png` - GIC estimates
- `results/processed_data.csv` - Clean observations

### Module 2: Geoelectric Field (geoelec1D)

**Start IPython:**
```bash
cd ../geoelec1D
ipython
```

**Run the pipeline:**
```ipython
%run geoelec_calc_main.py
```

**Expected output:**
```
Loading geomagnetic field data...
Computing geoelectric field...
E-field calculation complete
Generating maps...
Results saved to: results/
```

**Output files:**
- `results/E_field_map.png` - E-field visualization
- `results/E_magnitude.h5` - Field data (HDF5)

## Troubleshooting Installation

### Issue: "ModuleNotFoundError: No module named 'cartopy'"

**Solution:**
```bash
pip install --upgrade cartopy
```

For persistent issues on macOS:
```bash
brew install proj
pip install cartopy
```

### Issue: Virtual environment not activating

**Windows - Try this:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### Issue: Permission denied on Linux/macOS

```bash
chmod +x venv/bin/activate
source venv/bin/activate
```

### Issue: "No such file or directory: CHAOS-7.2.mat"

```bash
# Verify file exists
ls -la data/CHAOS-7.2.mat

# If missing, download again
cd data
wget http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/CHAOS-7.2.mat
cd ..
```

## Next Steps

1. **Explore the output** - Check the generated maps and data files
2. **Read documentation:**
   - [Architecture Guide](wiki-architecture.md) - Understand the design
   - [Data Management](wiki-data-management.md) - Learn about data handling
3. **Modify parameters** - Edit configuration in the main scripts
4. **Use modules programmatically** - Integrate into your own analyses

## Performance Tips

| Optimization | Impact | Difficulty |
|--------------|--------|------------|
| Use SSD storage | 2-3x faster | Easy |
| Increase RAM | 10-20% improvement | Medium |
| Reduce grid resolution | 50% faster | Medium |
| Use PyPy | 20-30% faster | Hard |

## Getting Help

**Still stuck?** Check these resources:

1. [Troubleshooting Guide](wiki-troubleshooting.md) - Common problems
2. [Data Management Guide](wiki-data-management.md) - Data issues
3. [Architecture Guide](wiki-architecture.md) - Understanding code
4. Main [README](README.md) - Project overview

---

**Congratulations!** You've successfully set up the German Power Grid project. 🎉

**Next:** Try running the [first analysis](README.md#running-analysis)

