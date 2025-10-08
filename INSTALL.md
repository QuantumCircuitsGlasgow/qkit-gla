# Qkit Installation Guide

## Install from PyPI (after publishing)
```bash
pip install qkit
```

## Install from source (development)
```bash
# Clone the repository
git clone https://github.com/qkitgroup/qkit.git
cd qkit

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e .[dev]

# Or install with all optional dependencies
pip install -e .[all]
```

## Install specific requirement sets
```bash
# Core dependencies only
pip install -r requirements-pinned.txt

# Development dependencies
pip install -r requirements-dev.txt

# Test dependencies
pip install -r requirements-test.txt
```

## Build and publish (for maintainers)
```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Upload to PyPI
twine upload dist/*
```

## Pre-commit hooks setup
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Dependencies Summary

### Core Dependencies (5 packages):
- ipython==8.12.3
- pyqt5==5.15.11
- pytest==8.4.2
- pyzmq==26.2.1
- setuptools==75.8.0

### Missing Dependencies (64 packages):
- ConfigParser (needs to be installed manually)
- DAC_LTC2666_communication (needs to be installed manually)
- EdwardsBridgeReadout (needs to be installed manually)
- Keysight_VNA_E5080B (needs to be installed manually)
- PIL (needs to be installed manually)
- PyQt4 (needs to be installed manually)
- Queue (needs to be installed manually)
- RPi (needs to be installed manually)
- _Spectrum_M2i2030 (needs to be installed manually)
- _Spectrum_M3i2132 (needs to be installed manually)
- _Spectrum_M4i2211 (needs to be installed manually)
- bitstring (needs to be installed manually)
- cPickle (needs to be installed manually)
- calibration (needs to be installed manually)
- circle_fitter (needs to be installed manually)
- circlefit (needs to be installed manually)
- ctypes (needs to be installed manually)
- distutils (needs to be installed manually)
- dpkt (needs to be installed manually)
- enum (needs to be installed manually)
- getopt (needs to be installed manually)
- grpc (needs to be installed manually)
- h5py (needs to be installed manually)
- helper_functions (needs to be installed manually)
- imp (needs to be installed manually)
- instruments (needs to be installed manually)
- ipywidgets (needs to be installed manually)
- lib_oled96 (needs to be installed manually)
- matplotlib (needs to be installed manually)
- nidaq_syncIV (needs to be installed manually)
- numpy (needs to be installed manually)
- numpy as np (needs to be installed manually)
- pandas (needs to be installed manually)
- peakutils (needs to be installed manually)
- pg_time_axis (needs to be installed manually)
- pkg_resources (needs to be installed manually)
- plasma1_gui (needs to be installed manually)
- proto_gen (needs to be installed manually)
- pyftdi (needs to be installed manually)
- pyqtgraph (needs to be installed manually)
- pyvisa (needs to be installed manually)
- qgrid (needs to be installed manually)
- qkit (needs to be installed manually)
- qm (needs to be installed manually)
- resonator (needs to be installed manually)
- rpyc (needs to be installed manually)
- runner (needs to be installed manually)
- scipy (needs to be installed manually)
- select (needs to be installed manually)
- sendMail (needs to be installed manually)
- serial (needs to be installed manually)
- sklearn (needs to be installed manually)
- smbus (needs to be installed manually)
- smtplib (needs to be installed manually)
- spidev (needs to be installed manually)
- switch (needs to be installed manually)
- tip_client (needs to be installed manually)
- uncertainties (needs to be installed manually)
- utilities (needs to be installed manually)
- visa (needs to be installed manually)
- visa_prologix as visa (needs to be installed manually)
- winpcapy (needs to be installed manually)
- zerorpc (needs to be installed manually)
- zhinst (needs to be installed manually)
