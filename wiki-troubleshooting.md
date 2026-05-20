# Troubleshooting Guide

Common issues and their solutions.

## Installation & Environment

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Cause:** Package not installed or virtual environment not activated

**Solutions:**

```bash
# 1. Verify virtual environment is activated
# Should see (venv) prefix in terminal prompt

# 2. Reinstall requirements
pip install -r requirements.txt

# 3. Check installation
pip list | grep numpy

# 4. Try upgrading pip first
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "SyntaxError: invalid syntax" in Python 2

**Cause:** Python 2 installed instead of Python 3.8+

**Solution:**
```bash
python --version  # Check version
python3 --version  # Try Python 3

# Use Python 3 explicitly
python3 -m venv venv
python3 -m pip install -r requirements.txt
```

### Issue: Virtual environment won't activate

**Windows:**
```cmd
# Try this:
python -m venv venv
venv\Scripts\activate.bat

# Or use Python launcher
py -3.8 -m venv venv
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Issue: Cartopy installation fails

**Cause:** Missing system dependencies for cartopy

**Solution (Ubuntu/Debian):**
```bash
sudo apt-get install libproj-dev proj-data
pip install cartopy
```

**Solution (macOS):**
```bash
brew install proj
pip install cartopy
```

**Solution (Windows):** Use conda instead of pip
```bash
conda install cartopy
```

## Data Issues

### Issue: "FileNotFoundError: CHAOS-7.2.mat not found"

**Cause:** Model file not downloaded or path incorrect

**Solution:**
```bash
# 1. Verify file exists
ls data/CHAOS-7.2.mat  # Linux/macOS
dir data\CHAOS-7.2.mat  # Windows

# 2. Download if missing
wget http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/CHAOS-7.2.mat
mv CHAOS-7.2.mat data/

# 3. Check file size (should be ~50 MB)
ls -lh data/CHAOS-7.2.mat
```

### Issue: "FileNotFoundError: IAGA_obs.csv not found"

**Cause:** Observatory data file not present

**Solution:**
```bash
# 1. Download from IAGA
# Visit: https://www.iaga-aiga.org/observatories/

# 2. Place in data directory
cp IAGA_obs.csv data/

# 3. Verify format
head -5 data/IAGA_obs.csv
```

### Issue: "Error reading shapefile: gadm36_DEU_1.shp not found"

**Cause:** Shapefile not extracted or path incorrect

**Solution:**
```bash
# 1. Download and extract
wget https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_DEU_shp.zip
unzip gadm36_DEU_shp.zip -d data/

# 2. Verify all files present
ls data/gadm36_DEU_shp/gadm36_DEU_1.*

# Should see: .shp, .shx, .dbf, .prj files
```

### Issue: "ValueError: No data in DataFrame"

**Cause:** Observatory data file is empty or incorrectly formatted

**Solution:**
```python
# Check file format
import pandas as pd
df = pd.read_csv('data/IAGA_obs.csv', nrows=10)
print(df.head())
print(df.info())

# Verify expected columns
expected_cols = ['code', 'latitude', 'longitude', 'Bx', 'By', 'Bz']
if not all(col in df.columns for col in expected_cols):
    print("Missing columns!")
```

## Execution Issues

### Issue: "IOError: invalid MATLAB file"

**Cause:** CHAOS model file corrupted or incomplete download

**Solution:**
```bash
# 1. Verify file size (should be ~50 MB)
ls -lh data/CHAOS-7.2.mat

# 2. Re-download
rm data/CHAOS-7.2.mat
wget http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/CHAOS-7.2.mat -P data/

# 3. Test loading
python -c "from scipy.io import loadmat; loadmat('data/CHAOS-7.2.mat')"
```

### Issue: IPython script doesn't run or produces no output

**Cause:** Execution mode or path issues

**Solution:**
```bash
# 1. Verify you're in the project directory
pwd  # Linux/macOS
cd  # Windows

# 2. Start IPython correctly
ipython

# 3. In IPython, use correct path
%run geomag/binder.ipy

# 4. Alternative: Run directly with python
python -m IPython geomag/binder.ipy

# 5. Check for errors - run step by step
import sys
sys.path.insert(0, '.')
exec(open('geomag/binder.ipy').read())
```

### Issue: "ImportError: cannot import name 'DatLib'"

**Cause:** Module not in Python path or import statement incorrect

**Solution:**
```python
# 1. Verify module exists
import os
os.path.exists('geomag/callable/Obs.py')

# 2. Add to path if needed
import sys
sys.path.insert(0, './geomag/callable')

# 3. Import correctly
from Obs import DatLib
# or
from geomag.callable.Obs import DatLib
```

### Issue: "RuntimeError: The number of SECS basis functions exceeds the number of observations"

**Cause:** Not enough observation points for SECS interpolation

**Solution:**
```python
# 1. Check number of observations
print(f"Number of observations: {len(observations)}")

# 2. SECS needs at least 4-6 observations per basis function
# Reduce basis function complexity or add more observations

# 3. In Get_SECS.py, adjust parameters:
n_basis = 20  # Reduce if needed
n_observations_needed = n_basis * 4  # Minimum
```

## Performance Issues

### Issue: Code runs very slowly

**Causes and solutions:**

1. **Large dataset:**
   ```python
   # Reduce data size for testing
   data = data[:100]  # Use first 100 rows
   ```

2. **Grid resolution too fine:**
   ```python
   # In Get_SECS.py, increase grid spacing
   grid_spacing = 0.5  # degrees (from 0.25)
   ```

3. **SECS computation slow:**
   ```python
   # Use sparse matrices
   from scipy.sparse import lil_matrix
   # or reduce number of basis functions
   n_basis = 20  # from 50
   ```

### Issue: "MemoryError" or running out of RAM

**Solutions:**

```python
# 1. Process data in chunks
chunk_size = 100
for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    process_chunk(chunk)

# 2. Use lower precision
grid_data = grid_data.astype('float32')  # instead of float64

# 3. Delete unnecessary variables
del large_array
import gc; gc.collect()
```

## Output & Visualization Issues

### Issue: Plots don't display in Jupyter

**Solution:**
```python
# Add at beginning of notebook
%matplotlib inline
# or
%matplotlib notebook

import matplotlib.pyplot as plt
```

### Issue: "OSError: [Errno 2] No such file or directory" when saving plots

**Cause:** Output directory doesn't exist

**Solution:**
```python
import os

output_dir = 'geoelec_output'
os.makedirs(output_dir, exist_ok=True)

# Now save
plt.savefig(f'{output_dir}/figure.png')
```

### Issue: Cartopy map not showing boundaries

**Cause:** Shapefile not loaded or path issue

**Solution:**
```python
import cartopy.crs as ccrs
import cartopy.feature as cfeature

ax = plt.axes(projection=ccrs.PlateCarree())

# Add features explicitly
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.COASTLINE)

# Or use shapefile
import geopandas as gpd
boundaries = gpd.read_file('data/gadm36_DEU_shp/gadm36_DEU_1.shp')
boundaries.plot(ax=ax, alpha=0.3, edgecolor='k')
```

## Data Format Issues

### Issue: "ParserError: Error tokenizing data in column X"

**Cause:** CSV file has inconsistent columns or encoding issues

**Solution:**
```python
import pandas as pd

# Try different encodings
encodings = ['utf-8', 'latin-1', 'iso-8859-1']
for enc in encodings:
    try:
        df = pd.read_csv('data/IAGA_obs.csv', encoding=enc)
        print(f"Successfully read with {enc}")
        break
    except:
        continue

# Check for issues
print(df.info())
print(df.describe())
```

### Issue: "ValueError: could not convert string to float"

**Cause:** Column contains non-numeric data

**Solution:**
```python
import pandas as pd

# Load with error handling
df = pd.read_csv('data/IAGA_obs.csv')

# Check for problematic columns
for col in ['Bx', 'By', 'Bz']:
    try:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    except:
        print(f"Issue in column {col}")
        print(df[col].unique()[:10])
```

## Getting Help

If issues persist:

1. **Reproduce the error** with minimal code
2. **Check error messages carefully** - they often indicate root cause
3. **Search existing issues** on GitHub
4. **Contact the developers:**
   - Aoife McCloskey: aoife.mccloskey@dlr.de
   - Leonie Pick: Leonie.Pick@dlr.de

### Preparing a bug report

Include:
- Python version: `python --version`
- Installed packages: `pip list`
- Error traceback (full output)
- Minimal reproducible example
- Data sample (if possible)
- Operating system and Python environment

---

**Previous:** [Architecture Guide](wiki-architecture.md)  
**Home:** [Wiki Home](wiki_home.md)
