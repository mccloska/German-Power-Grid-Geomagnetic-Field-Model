# Data Management Guide

This guide covers data formats, sources, storage, and management for the German Power Grid project.

## Table of Contents

1. [Data Directory Structure](#data-directory-structure)
2. [Input Data Formats](#input-data-formats)
3. [Output Data Formats](#output-data-formats)
4. [Data Sources](#data-sources)
5. [Working with Data](#working-with-data)
6. [Data Validation](#data-validation)

## Data Directory Structure

Create and organize your data directory:

```
data/
├── raw/                          # Original unmodified data
│   ├── IAGA_obs.csv             # Observatory observations
│   └── CHAOS-7.2.mat            # Magnetic field model
├── processed/                    # Preprocessed data
│   ├── observations_clean.csv    # Cleaned observations
│   └── field_grid.nc            # Interpolated fields
├── gadm36_DEU_shp/              # German boundaries
│   ├── gadm36_DEU_1.shp
│   ├── gadm36_DEU_1.dbf
│   └── ...
└── results/                      # Output files
    ├── geomag_output/           # GIC calculations
    └── geoelec_output/          # E-field calculations
```

## Input Data Formats

### 1. IAGA Observatory Data (CSV)

**Format:** Comma-separated values with geomagnetic observations

**File:** `IAGA_obs.csv`

**Columns:**

| Column | Description | Units | Type |
|--------|-------------|-------|------|
| code | Observatory IAGA code | - | String |
| name | Observatory name | - | String |
| latitude | Geographic latitude | degrees | Float |
| longitude | Geographic longitude | degrees | Float |
| elevation | Elevation above sea level | meters | Float |
| Bx | X-component (North) | nanoTesla (nT) | Float |
| By | Y-component (East) | nanoTesla (nT) | Float |
| Bz | Z-component (Down) | nanoTesla (nT) | Float |
| Bt | Total intensity | nanoTesla (nT) | Float |
| dBx | X-component change | nanoTesla (nT) | Float |
| dBy | Y-component change | nanoTesla (nT) | Float |
| dBz | Z-component change | nanoTesla (nT) | Float |
| timestamp | Observation time | ISO 8601 | DateTime |

**Example:**

```csv
code,name,latitude,longitude,elevation,Bx,By,Bz,Bt,dBx,dBy,dBz,timestamp
GCK,Göttingen,51.52,9.95,172,-19568.5,2783.2,43526.8,47825.3,125.2,-23.1,89.3,2024-03-21T12:00:00Z
MEA,Meanook,54.62,-113.33,2368,-6524.3,27841.5,52631.2,59874.1,234.1,156.2,312.5,2024-03-21T12:00:00Z
```

### 2. CHAOS-7.2 Magnetic Model (MATLAB)

**Format:** MATLAB .mat file containing magnetic field model coefficients

**File:** `CHAOS-7.2.mat`

**Contents:**
- Spherical harmonic coefficients
- Model epochs and validity periods
- Reference spherical harmonic functions

**Source:** [CHAOS Magnetic Field Model](http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/)

**Usage in code:**
```python
from scipy.io import loadmat
chaos_data = loadmat('CHAOS-7.2.mat')
```

### 3. German Administrative Boundaries (Shapefile)

**Format:** ESRI Shapefile with German state/regional boundaries

**Files in `gadm36_DEU_shp/`:**

| File | Purpose |
|------|---------|
| gadm36_DEU_1.shp | Main shapefile (geometry) |
| gadm36_DEU_1.shx | Shape index file |
| gadm36_DEU_1.dbf | Attribute database |
| gadm36_DEU_1.prj | Projection information |
| gadm36_DEU_1.cpg | Code page (optional) |

**Source:** [GADM Database v3.6](https://gadm.org/download_country_v3.html)

**Usage in code:**
```python
import cartopy.io.shapereader as shpreader
shapefile = 'data/gadm36_DEU_shp/gadm36_DEU_1.shp'
```

## Output Data Formats

### 1. Processed Observations (CSV)

**Created by:** `geomag/Get_Obs.py`

**Contents:** Cleaned and validated observatory data

```csv
code,name,latitude,longitude,elevation,Bx_clean,By_clean,Bz_clean,quality_flag,timestamp
GCK,Göttingen,51.52,9.95,172,-19568.5,2783.2,43526.8,1,2024-03-21T12:00:00Z
```

### 2. Interpolated Field Grid (NetCDF)

**Created by:** `geomag/Get_SECS.py`

**Format:** NetCDF4 (self-describing, scientific data format)

**Dimensions:**
- `latitude`: -10° to 65°N
- `longitude`: -15° to 45°E
- `time`: Variable (depends on observations)

**Variables:**

| Variable | Description | Units | Type |
|----------|-------------|-------|------|
| Bx | X-component field | nanoTesla | Float32 |
| By | Y-component field | nanoTesla | Float32 |
| Bz | Z-component field | nanoTesla | Float32 |
| current_density | Induced current density | µA/m² | Float32 |
| gic_estimate | Estimated GIC | Amperes | Float32 |

**Usage in code:**
```python
import xarray as xr
ds = xr.open_dataset('data/processed/field_grid.nc')
Bx = ds['Bx'].values
```

### 3. Geoelectric Field Maps (HDF5)

**Created by:** `geoelec1D/geoelec_calc_main.py`

**Format:** HDF5 (hierarchical data format)

**Structure:**
```
/geoelec_output.h5
├── Ex                    # E-field X-component
├── Ey                    # E-field Y-component
├── E_magnitude           # Total E-field magnitude
├── coordinates/
│   ├── latitude
│   ├── longitude
│   └── time
└── metadata/
    ├── conductivity_model
    ├── calculation_date
    └── parameters
```

**Usage in code:**
```python
import h5py
with h5py.File('geoelec_output.h5', 'r') as f:
    E_x = f['Ex'][:]
    coords = f['coordinates/latitude'][:]
```

### 4. Visualization Output (PNG/PDF)

**Created by:** Matplotlib in both modules

**Contents:**
- Spatial field maps
- Time series plots
- Geographic visualizations

**Files:**
- `field_map_YYYY-MM-DD.png` - Spatial field visualization
- `gic_distribution.png` - GIC spatial distribution
- `timeseries.pdf` - Time evolution plots

## Data Sources

### Official Data Providers

| Data | Provider | URL | Format |
|------|----------|-----|--------|
| Observatory data | IAGA | www.iaga-aiga.org | CSV/ASCII |
| Magnetic model | CHAOS | spacecenter.dk | MATLAB |
| Boundaries | GADM | gadm.org | Shapefile |
| Space weather | NOAA/SWPC | swpc.noaa.gov | Various |

### Downloading Observatory Data

**From IAGA Website:**

1. Visit: [IAGA Geomagnetic Observatories](https://www.iaga-aiga.org/observatories/)
2. Select relevant stations
3. Download data in IAGA2002 ASCII format
4. Convert to CSV using provided scripts

**Format conversion example:**
```python
# Convert IAGA2002 to CSV
import pandas as pd

def iaga_to_csv(iaga_file, output_csv):
    # Read IAGA format
    data = pd.read_csv(iaga_file, skiprows=13, sep=' ')
    # Process and save
    data.to_csv(output_csv, index=False)
```

### Downloading Magnetic Model

```bash
# Download CHAOS-7.2 model
wget http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/CHAOS-7.2.mat
mv CHAOS-7.2.mat data/
```

### Downloading GADM Boundaries

```bash
# Download and extract GADM shapefile
wget https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_DEU_shp.zip
unzip gadm36_DEU_shp.zip -d data/gadm36_DEU_shp/
```

## Working with Data

### Loading Data in Python

**Observatory data:**
```python
import pandas as pd

obs_data = pd.read_csv('data/IAGA_obs.csv', parse_dates=['timestamp'])
print(obs_data.head())
print(obs_data.info())
```

**Magnetic model:**
```python
from scipy.io import loadmat

chaos = loadmat('data/CHAOS-7.2.mat')
coefficients = chaos['coefficients']
```

**Shapefiles:**
```python
import geopandas as gpd

boundaries = gpd.read_file('data/gadm36_DEU_shp/gadm36_DEU_1.shp')
print(boundaries.head())
```

**NetCDF files:**
```python
import xarray as xr

field_data = xr.open_dataset('data/processed/field_grid.nc')
print(field_data)
```

### Data Preprocessing

**Clean observatory data:**
```python
def clean_obs_data(df):
    # Remove duplicates
    df = df.drop_duplicates(subset=['code', 'timestamp'])
    
    # Remove outliers (3-sigma rule)
    for col in ['Bx', 'By', 'Bz']:
        mean = df[col].mean()
        std = df[col].std()
        df = df[(df[col] - mean).abs() <= 3*std]
    
    # Fill missing values
    df = df.fillna(method='ffill').fillna(method='bfill')
    
    return df
```

### Data Export

**Save to CSV:**
```python
processed_data.to_csv('data/processed/observations_clean.csv', index=False)
```

**Save to NetCDF:**
```python
import xarray as xr

ds = xr.Dataset({
    'Bx': (['lat', 'lon', 'time'], bx_data),
    'By': (['lat', 'lon', 'time'], by_data),
    'Bz': (['lat', 'lon', 'time'], bz_data),
})
ds.to_netcdf('data/processed/field_grid.nc')
```

**Save to HDF5:**
```python
import h5py

with h5py.File('geoelec_output.h5', 'w') as f:
    f.create_dataset('Ex', data=Ex_data)
    f.create_dataset('Ey', data=Ey_data)
    f.create_dataset('E_magnitude', data=E_mag_data)
```

## Data Validation

### Quality Checks

**Observatory data validation:**
```python
def validate_obs_data(df):
    checks = {
        'no_duplicates': len(df) == len(df.drop_duplicates()),
        'no_nan_spatial': not df[['latitude', 'longitude']].isna().any().any(),
        'valid_latitude': df['latitude'].between(-90, 90).all(),
        'valid_longitude': df['longitude'].between(-180, 180).all(),
        'reasonable_B_values': df['Bt'].between(0, 100000).all(),
    }
    return checks
```

**Field data validation:**
```python
def validate_field_data(field_array):
    checks = {
        'no_nan': not np.isnan(field_array).any(),
        'reasonable_range': np.abs(field_array).max() < 10000,  # nT
        'spatial_continuity': np.std(field_array) < 5000,
    }
    return checks
```

### Data Integrity Checks

```python
# Check file integrity
import hashlib

def verify_file(filepath, expected_hash=None):
    with open(filepath, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    if expected_hash:
        return file_hash == expected_hash
    return file_hash
```

## Best Practices

1. **Always keep original data in `/raw/`** - Never modify source data
2. **Document data origin** - Note source, date, and processing steps
3. **Validate early** - Check data quality immediately after loading
4. **Use meaningful names** - Clear file names indicate content
5. **Version your outputs** - Include date/time in output filenames
6. **Maintain metadata** - Document column meanings and units
7. **Archive results** - Keep processed data for reproducibility

---

**Next:** [Tutorials & Examples](wiki-tutorials.md)
