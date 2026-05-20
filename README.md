# German Power Grid - Main README

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: DLR](https://img.shields.io/badge/License-DLR-lightgrey.svg)]()

> A Python-based framework for assessing the impact of space weather on the German power grid.

## Overview

The **German Power Grid** project is a comprehensive computational framework that analyzes geomagnetic storms and their effects on power infrastructure. It combines two specialized modules:

1. **geomag** - Processes geomagnetic observations and calculates geomagnetically induced currents (GICs)
2. **geoelec1D** - Computes induced geoelectric fields using 1-dimensional conductivity models

This research is conducted as part of the **DLR-SO-WWE project** at the DLR Institute for Solar-Terrestrial Physics.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mccloska/German-Power-Grid.git
cd German-Power-Grid

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Download Data

```bash
mkdir -p data/gadm36_DEU_shp

# Download CHAOS magnetic model
cd data
wget http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/CHAOS-7.2.mat

# Download German boundaries
wget https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_DEU_shp.zip
unzip gadm36_DEU_shp.zip -d gadm36_DEU_shp/
cd ..
```

### Run Analysis

```bash
# Geomagnetic analysis
cd geomag
ipython
# In IPython: %run binder.ipy

# Geoelectric field calculation
cd ../geoelec1D
ipython
# In IPython: %run geoelec_calc_main.py
```

## 📚 Documentation

Complete documentation is available in the `/docs` directory or via the [Wiki Home](wiki_home.md):

| Document | Purpose |
|----------|---------|
| [Getting Started](wiki-getting-started.md) | Installation and setup instructions |
| [Architecture Guide](wiki-architecture.md) | System design and module relationships |
| [Data Management](wiki-data-management.md) | Data formats, sources, and handling |
| [Troubleshooting](wiki-troubleshooting.md) | Common issues and solutions |

## 📊 Project Structure

```
German-Power-Grid/
├── geomag/                    # Geomagnetic analysis module
│   ├── binder.ipy            # Main orchestration script
│   ├── Get_Obs.py            # Observatory data processing
│   ├── Get_SECS.py           # SECS spatial interpolation
│   ├── callable/             # Core classes and utilities
│   └── README.md             # Module-specific documentation
│
├── geoelec1D/                 # Geoelectric field module
│   ├── geoelec_calc_main.py  # Main calculation script
│   ├── efield_funcs.py       # E-field computation functions
│   ├── callable/             # Support modules
│   └── README.md
│
├── data/                      # Input data directory
│   ├── CHAOS-7.2.mat         # Magnetic field model coefficients
│   ├── IAGA_obs.csv          # Geomagnetic observatory observations
│   └── gadm36_DEU_shp/       # German administrative boundaries
│
├── requirements.txt           # Python package dependencies
├── README.md                  # This file
└── wiki_home.md              # Documentation index
```

## 🔧 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **Python** | 3.8 | 3.8-3.11 |
| **Memory** | 4 GB RAM | 8 GB RAM |
| **Disk** | 2 GB | 5 GB |
| **OS** | Linux, macOS, Windows | Linux or macOS |

## 📦 Dependencies

All required packages are listed in `requirements.txt`:

```
numpy>=1.19.1
pandas>=1.1.1
matplotlib>=3.3.1
scipy>=1.6.2
ipython>=7.18.1
cartopy>=0.18.0
chaosmagpy>=0.4
```

Install with: `pip install -r requirements.txt`

## 🎯 Module Overview

### geomag Module

**Purpose:** Process geomagnetic observations and calculate GICs

**Key Features:**
- Acquires observatory data from IAGA network
- Applies SECS spatial interpolation
- Estimates GICs in power transmission networks
- Generates field visualization maps

**Main Scripts:**
- `binder.ipy` - Orchestration script
- `Get_Obs.py` - Data acquisition and preprocessing
- `Get_SECS.py` - Spatial interpolation engine

### geoelec1D Module

**Purpose:** Compute 1-dimensional induced geoelectric fields

**Key Features:**
- Calculates geoelectric field components
- Applies 1-D conductivity models
- Generates field magnitude maps
- Produces publication-ready visualizations

**Main Scripts:**
- `geoelec_calc_main.py` - Orchestration and execution
- `efield_funcs.py` - Core calculation functions

## 💻 Usage Examples

### Running the Full Pipeline

```bash
# Activate environment
source venv/bin/activate

# Run geomag module
cd geomag
ipython
# In IPython:
%run binder.ipy
# Output: geomag/results/

# Run geoelec module  
cd ../geoelec1D
ipython
%run geoelec_calc_main.py
# Output: geoelec1D/results/
```

### Using Modules Programmatically

```python
import sys
sys.path.insert(0, './geomag/callable')

from Obs import DatLib
from SECS import SECSLib

# Load and process observatory data
obs = DatLib()
obs.load_data('data/IAGA_obs.csv')
obs.preprocess()

# Perform spatial interpolation
secs = SECSLib()
secs.set_input_data(obs.locations, obs.field_values)
secs.interpolate()

# Access results
field_grid = secs.get_output()
```

## 📖 Workflow

```
Input Data
    ↓
[geomag Module]
├─→ Get_Obs.py (load & preprocess)
├─→ Get_SECS.py (spatial interpolation)
└─→ Output: Field grids, GIC estimates
    ↓
[geoelec1D Module]
├─→ Load geomag results
├─→ Calculate E-fields
└─→ Output: Field maps, visualizations
    ↓
Results & Analysis
```

## 🔑 Key Scientific Concepts

### Geomagnetically Induced Currents (GICs)
Currents flowing in long conducting systems during geomagnetic storms. These can cause transformer damage and power system failures.

### Spherical Elementary Current Systems (SECS)
Mathematical approach for spatial interpolation of geomagnetic field observations. Allows estimation at unmeasured locations with minimal assumptions.

### Geoelectric Fields
Electric fields induced in the Earth's subsurface by time-varying magnetic fields. These drive GICs into power networks.

## 👥 Authors

- **Aoife McCloskey** (geoelec1D module)
  - DLR Institute for Solar-Terrestrial Physics
  - aoife.mccloskey@dlr.de

- **Leonie Pick** (geomag module)
  - DLR Institute for Solar-Terrestrial Physics
  - Leonie.Pick@dlr.de

## 🏢 Organization

Developed at the **DLR Institute for Solar-Terrestrial Physics** as part of the **DLR-SO-WWE research initiative**.

**More information:** https://www.dlr.de/

## 📋 Prerequisites Before Running

1. **Install Python 3.8+** - Download from https://www.python.org/
2. **Setup virtual environment** - See Getting Started Guide
3. **Install dependencies** - Run `pip install -r requirements.txt`
4. **Download data files** - See Quick Start above
5. **Verify installation** - Run `python -c "import numpy, pandas, cartopy"`

## 🚨 Troubleshooting

For common issues and their solutions, see:
- [Troubleshooting Guide](wiki-troubleshooting.md) - Comprehensive problem-solving
- [Getting Started Guide](wiki-getting-started.md) - Installation issues
- [Data Management](wiki-data-management.md) - Data-related problems

**Quick check:**
```bash
# Verify environment
python --version
pip list | grep -E "numpy|pandas|cartopy"

# Check data files
ls -la data/CHAOS-7.2.mat
ls -la data/gadm36_DEU_shp/
```

## 📈 Performance

| Operation | Typical Time |
|-----------|--------------|
| Load observatory data | < 1 sec |
| SECS interpolation | 5-30 sec |
| Geoelectric calculation | 10-60 sec |
| Visualization | 5-20 sec |
| **Total pipeline** | ~1-2 min |

## 🔗 External Resources

- **IAGA Observatory Network:** https://www.iaga-aiga.org/observatories/
- **CHAOS Magnetic Field Model:** http://www.spacecenter.dk/files/magnetic-models/CHAOS-7/
- **GADM Database:** https://gadm.org/download_country_v3.html
- **DLR Institute:** https://www.dlr.de/

## 📝 Citation

If you use this project in research, please cite:

```bibtex
@software{mccloska2022germangrid,
  title={German Power Grid: Space Weather Impact Assessment},
  author={McCloskey, Aoife and Pick, Leonie},
  organization={DLR Institute for Solar-Terrestrial Physics},
  year={2022},
  url={https://github.com/mccloska/German-Power-Grid}
}
```

## 📞 Support

For questions or issues:
- Review the [Documentation Index](wiki_home.md)
- Check [Troubleshooting Guide](wiki-troubleshooting.md)
- Contact the authors (see above)

## 🤝 Contributing

To contribute improvements:
1. Understand the [Architecture](wiki-architecture.md)
2. Follow existing code patterns
3. Ensure data validation
4. Document changes

## 📄 License

This project is developed by DLR and part of official research initiatives. See LICENSE file for details.

---

**Last Updated:** 2026-05-20  
**Version:** 1.0  
**Status:** Active Development

