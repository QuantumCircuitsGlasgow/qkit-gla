<p align="center">
  <img src="./images/qkit_b.png" alt="QKIT" width="300">
</p>




# Qkit-gla :  a quantum measurement suite in python
![Static Badge](https://img.shields.io/badge/QKIT-GLA-2ad0db?style=flat-square&logoSize=10)

![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FQuantumCircuitsGlasgow%2Fqkit-gla%2Frefs%2Fheads%2Frelease%2Fpyproject.toml&style=plastic)
![Build](https://github.com/QuantumCircuitsGlasgow/qkit-gla/actions/workflows/release.yml/badge.svg)

[![PyPI version](https://img.shields.io/pypi/v/qkit-gla.svg)](https://pypi.org/project/qkit-gla/)
[![TestPyPI version](https://img.shields.io/badge/dynamic/json?url=https://test.pypi.org/pypi/qkit/json&query=$.info.version&label=TestPyPI)](https://test.pypi.org/project/qkit/)



*Note: this is a adaptation measurement suite based on the KIT suite of the same name for [Quantum Circuits Glasgow](https://www.gla.ac.uk/research/az/quantumcircuitslab/)*

## Features:
  * a collection of ipython notebooks for measurement and data analysis tasks.
  * hdf5 based data storage of 1,2 and 3 dimensional data, including a viewer.
  * classes for data fitting, e.g. of microwave resonator data. This includes also a robust circle fit algorithm.
  * extended and maintained drivers for various low frequency and microwave electronics.

### Platform:
  The qkit framework has been tested under windows and with limits under macos x and linux. 
  The gui requires h5py, qt and pyqtgraph, which work fine on these platforms. 
  The core of the framework runs on __Python 3.9+__
 
## Requirements:
This project uses python 3.9+. An up to date installation of python is expected to be present.
The requirements are listed in the `requirements.txt` file. 

They can be installed automatically using
```bash
pip install -r requirements.txt
```
| Library | Usage |
| ------- | ----- |
| [pyqt5](https://pypi.org/project/PyQt5/) | GUI   | 
| [numpy](https://pypi.org/project/numpy/), [scipy](https://pypi.org/project/scipy/), [uncertainties](https://pypi.org/project/uncertainties/) | General Usage |
| [pyqtgraph](https://pypi.org/project/pyqtgraph/), [matplotlib](https://pypi.org/project/matplotlib/) | Plotting |
| [h5py](https://pypi.org/project/h5py/) | Data Stroage |
| [jupyterlab](https://pypi.org/project/jupyterlab/) | Interactive Notebooks |
| [jupyterlab-templates](https://pypi.org/project/jupyterlab-templates/) | Notebook Templating |
| [pyvisa](https://pypi.org/project/PyVISA/), [pyvisa-py](https://pypi.org/project/PyVISA-py/) | Communication with Devices |
| [zhinst](https://pypi.org/project/zhinst/) | Drivers for Zurich Instruments devices |
| [zeromq](https://pypi.org/project/pyzmq/) | Messaging |  

### Pre-requisites:
for __Windows__  : Install some version of `conda`. Miniconda3 or Anaconda would do.

## Installation:
It is recommended to install in a `virtual-env` or `conda` environment for compatibility with other dependencies. For `venv` see below. For a `conda` env :

```bash
#create a new py3.9 env
conda create -n qkit-env python=3.9

#activate the env
conda activate qkit-env

```
and install via `pip` and testPyPi

```bash
python -m pip install --upgrade pip

pip install -i https://test.pypi.org/simple/ qkit --extra-index-url https://pypi.org/simple

```



## Alternative Install methods :
Clone this repository with
```bash
git clone https://github.com/qkitgroup/qkit.git
```
In this directory, create a virtual environment with the required dependencies. Should you not have `virtualenv` installed, see below.
```bash
 #(Windows) 
python -m venv .venv-test && .venv-test\Scripts\activate

# (Unix)
source .venv-test/bin/activate
```


Now install the dependencies using (in a python 3.9 env)
```bash
pip install -r requirements.txt
```

### Installing venv
If you don't have support for virtual environments, enable it by running
```bash
pip install virtualenv
```


## Usage
Usually run within a Jupyter Notebook

1. Create a cell 
```python
import qkit

qkit.cfg['load_visa'] = True
qkit.cfg['run_id'] = 'run001'
qkit.cfg['datadir'] = path/to/data/folder
qkit.cfg['debug']='ERROR'

qkit.start()

```
