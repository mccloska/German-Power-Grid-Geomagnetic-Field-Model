# Architecture & Design

This guide explains the overall architecture and design decisions of the German Power Grid project.

## Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [Module Architecture](#module-architecture)
4. [Data Flow](#data-flow)
5. [Class Hierarchy](#class-hierarchy)
6. [Workflow Orchestration](#workflow-orchestration)

## Overview

The German Power Grid project is organized into two main computational modules that work together to assess space weather impacts:

```
┌─────────────────────────────────────────────┐
│      Input: Geomagnetic Observatory Data    │
└────────────┬────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  Module 1: geomag                            │
│  (Geomagnetic Analysis & GIC Calculation)    │
│                                              │
│  ├─ Get_Obs.py    (Data acquisition)         │
│  ├─ Get_SECS.py   (Spatial interpolation)    │
│  └─ callable/     (Core classes)             │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  Module 2: geoelec1D                         │
│  (1-D Geoelectric Field Calculation)         │
│                                              │
│  ├─ geoelec_calc_main.py (Orchestration)     │
│  ├─ efield_funcs.py      (Calculations)      │
│  └─ callable/            (Support modules)   │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────┐
│   Output: GIC Estimates & Field Maps        │
└─────────────────────────────────────────────┘
```

## Design Philosophy

### 1. **Modular Decomposition**
The project separates concerns into distinct modules:
- **geomag** handles all geomagnetic data processing
- **geoelec1D** handles geoelectric field calculations
- Each module is independently testable and reusable

### 2. **Object-Oriented Design**
Core functionality is encapsulated in classes:
- `DatLib`: Observatory data management
- `SECSLib`: Spherical Elementary Current Systems interpolation
- Benefits: Encapsulation, reusability, maintainability

### 3. **Separation of Data and Logic**
- Raw data stored in external files (not in code)
- Algorithms are reusable functions/methods
- Configuration is externalized where possible

### 4. **Pipeline Architecture**
- Workflow orchestrated through main scripts (binder.ipy, geoelec_calc_main.py)
- Clear input → process → output stages
- Easy to extend and modify individual stages

### 5. **IPython-Based Execution**
- Interactive execution environment for research flexibility
- Allows inspection of intermediate results
- Suitable for exploratory analysis and debugging

## Module Architecture

### Module 1: geomag (Geomagnetic Analysis)

**Purpose:** Process geomagnetic observations and estimate GICs

**Key Components:**

```
geomag/
├── binder.ipy                 # Orchestration script
├── Get_Obs.py                 # Stage 1: Data acquisition
├── Get_SECS.py                # Stage 2: Spatial interpolation
├── README.md                  # Documentation
└── callable/
    ├── Obs.py                 # DatLib class
    ├── SECS.py                # SECSLib class
    ├── gd2gc.py               # Coordinate conversion
    └── __init__.py
```

**Workflow:**

```
1. binder.ipy (Main Orchestrator)
   │
   ├─→ Get_Obs.py
   │   └─→ Uses DatLib (from Obs.py)
   │       └─→ Loads IAGA_obs.csv
   │       └─→ Preprocesses observatory data
   │       └─→ Exports processed observations
   │
   └─→ Get_SECS.py
       └─→ Uses SECSLib (from SECS.py)
           └─→ Reads processed observations
           └─→ Applies SECS interpolation
           └─→ Generates spatial field grids
           └─→ Estimates GIC values
```

### Module 2: geoelec1D (Geoelectric Field Calculation)

**Purpose:** Calculate 1-dimensional induced electric fields

**Key Components:**

```
geoelec1D/
├── geoelec_calc_main.py       # Orchestration & main script
├── efield_funcs.py            # Core calculation functions
├── README.md                  # Documentation
└── callable/
    ├── SECS.py                # SECSLib class (reused)
    └── __init__.py
```

**Workflow:**

```
1. geoelec_calc_main.py (Orchestrator)
   │
   ├─→ Load geomagnetic data from geomag module
   │
   ├─→ efield_funcs.py
   │   └─→ Compute geoelectric field components
   │   └─→ Apply 1-D conductivity model
   │   └─→ Generate field visualizations
   │
   └─→ Output results and maps
```

## Data Flow

### Complete Pipeline Flow

```
┌─────────────────────────┐
│  External Data Sources  │
├─────────────────────────┤
│ • IAGA Observatory CSV  │
│ • CHAOS-7.2 model       │
│ • GADM Shapefiles       │
└────────────┬────────────┘
             │
             ▼
    ┌────────────────┐
    │  geomag/       │
    │  Get_Obs.py    │
    └────────┬───────┘
             │
             ▼
    ┌─────────────────────┐
    │  Processed Data:    │
    │  - Obs coordinates  │
    │  - Obs field values │
    │  - Timestamps       │
    └────────┬────────────┘
             │
             ▼
    ┌────────────────┐
    │  geomag/       │
    │  Get_SECS.py   │
    └────────┬───────┘
             │
             ▼
    ┌──────────────────────┐
    │  Interpolated Data:  │
    │  - Regular grid      │
    │  - Field components  │
    │  - GIC estimates     │
    └────────┬─────────────┘
             │
             ▼
    ┌────────────────────────┐
    │  geoelec1D/            │
    │  geoelec_calc_main.py  │
    └────────┬───────────────┘
             │
             ▼
    ┌─────────────────────┐
    │  Final Output:      │
    │  - E-field maps     │
    │  - GIC maps         │
    │  - Visualizations   │
    └─────────────────────┘
```

## Class Hierarchy

### DatLib (Observatory Data Management)

```
DatLib
├── Attributes:
│   ├── filename          # Input CSV file
│   ├── locations         # Observatory locations
│   ├── field_values      # Magnetic field measurements
│   └── timestamps        # Time information
├── Methods:
│   ├── load_data()       # Load from CSV
│   ├── preprocess()      # Clean and prepare data
│   ├── interpolate()     # Spatial operations
│   └── export_data()     # Save processed data
```

### SECSLib (Spatial Interpolation)

```
SECSLib
├── Attributes:
│   ├── obs_locations     # Input observation points
│   ├── obs_values        # Values at observations
│   ├── grid_definition   # Target grid specification
│   └── coefficients      # SECS basis coefficients
├── Methods:
│   ├── set_input_data()  # Configure input
│   ├── define_grid()     # Set up target grid
│   ├── solve_system()    # Compute SECS basis
│   ├── interpolate()     # Perform interpolation
│   └── get_output()      # Retrieve results
```

## Workflow Orchestration

### Geomag Module Workflow (binder.ipy)

```python
# 1. Initialize
import geomag.callable.Obs as ObsModule
import geomag.callable.SECS as SECSModule

# 2. Load and preprocess observatory data
x = ObsModule.DatLib()
x.load_data('IAGA_obs.csv')
x.preprocess()

# 3. Perform SECS interpolation
y = SECSModule.SECSLib()
y.set_input_data(x.locations, x.field_values)
y.define_grid(target_region='germany')
y.solve_system()
y.interpolate()

# 4. Output results
y.save_results('geomag_output/')
```

### Geoelec1D Module Workflow (geoelec_calc_main.py)

```python
# 1. Load geomagnetic field data
from geoelec1D import efield_funcs

B_data = load_geomag_data('geomag_output/')

# 2. Calculate geoelectric field
E_field = efield_funcs.calculate_efield_1d(
    B_data,
    conductivity_model='1D_german'
)

# 3. Generate visualizations
visualize_results(E_field, B_data)

# 4. Save output
save_results(E_field, 'geoelec_output/')
```

## Key Design Decisions

### 1. Why IPython Scripts?
- **Rationale:** Research-oriented execution allows inspection of intermediate results
- **Trade-off:** Not suitable for production deployment (consider containerization)

### 2. Why Separate Data & Callable?
- **Rationale:** Keeps working scripts clean, reusable modules in dedicated location
- **Benefit:** Easy to import and test modules independently

### 3. Why SECS Method?
- **Rationale:** SECS provides excellent spatial interpolation with minimal assumptions
- **Reference:** Amm & Viljanen (1999)

### 4. Why 1-D Geoelectric Fields?
- **Rationale:** Simplifies calculations while capturing main effects
- **Limitation:** Doesn't account for lateral conductivity variations

## Extension Points

Future development can easily extend:

1. **New Data Sources**
   - Add new observatory formats in `Get_Obs.py`
   - Extend `DatLib` class with new preprocessing methods

2. **Advanced Interpolation**
   - Implement 3-D SECS in addition to 1-D
   - Add alternative interpolation methods to `SECSLib`

3. **3-D Geoelectric Fields**
   - Extend `efield_funcs.py` with 3-D calculation
   - Add complex conductivity models

4. **GIC Modeling**
   - Add power network topology module
   - Implement GIC coupling to specific transmission lines

## Performance Considerations

| Operation | Typical Time | Scalability |
|-----------|--------------|-------------|
| Load observatory data | < 1 second | Linear |
| SECS interpolation | 5-30 seconds | O(n²) for n observations |
| Geoelectric calculation | 10-60 seconds | Linear |
| Visualization | 5-20 seconds | Linear |

**Total pipeline execution:** ~1-2 minutes for typical dataset

---

**Next:** [Geomagnetic Module Details](wiki-geomag.md)
