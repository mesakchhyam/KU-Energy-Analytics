# KU-EnergyAnalytics

Python-based calculation and graph-generation tool developed for energy consumption and power-quality analysis of the main transformer at Kathmandu University, Nepal.

## Overview

This software was developed to process downloaded smart-meter data and generate electrical energy and power-quality analyses.

The software does **not** automatically acquire data from the IAMMETER cloud platform. Historical smart-meter data are downloaded from the IAMMETER cloud platform and subsequently loaded into the Python graphical user interface (GUI) for analysis.

The tool is intended for calculation, analysis, visualization, and report generation rather than automatic data acquisition.

## Study Scope

Kathmandu University has seven IAMMETER smart meters installed across the campus. The analysis presented in the associated research paper focuses on the meter installed at the **main transformer**.

The remaining six meters are outside the scope of the present analysis.

The phase-wise Transformer A, B, and C datasets are loaded into the GUI for the summer, winter, and festival periods.

## Main Functions

The software provides the following analysis functions:

- Peak and off-peak load analysis
- Voltage analysis
- Energy consumption analysis
- Daily load profiles
- Active power curves
- Reactive power curves
- VUF/CUF charts
- VUF trends
- CUF trends
- Hourly-averaged active power distribution
- Hourly-averaged VUF distribution
- Hourly-averaged CUF distribution
- Full PDF report generation

## Data Processing

The input data consist of phase-wise voltage and current measurements for the transformer.

The software processes the loaded Transformer A, B, and C datasets and performs the required electrical calculations and graphical analysis.

The analysis workflow is:

1. Historical smart-meter data are downloaded from the IAMMETER cloud platform.
2. The downloaded data are loaded into the Python GUI.
3. Transformer A, B, and C datasets are processed for each study period.
4. Electrical parameters and hourly-based analyses are calculated.
5. Individual graphs and a complete PDF analysis report can be generated.

The original Kathmandu University measurement data are not included in this repository.

## Data Availability

The original Kathmandu University smart-meter measurement datasets are not included in this repository.

The software accepts compatible CSV or Excel datasets containing phase-wise voltage and current measurements.

## Requirements

- Python 3.x
- pandas
- numpy
- matplotlib
- openpyxl
- tkinter

## Installation

Clone or download this repository and install the required Python packages using:

```bash
pip install -r requirements.txt
```

## Usage

Run the Python program using:

```bash
python Transformer_Analyzer_Code.py
```

After starting the GUI:

1. Load the Transformer A, B, and C datasets for the required season.
2. Confirm that the required phase datasets have been loaded.
3. Select the required analysis option from the **Analysis Options** section.
4. Generate individual graphs or use **Generate Full PDF Report** for the complete analysis report.

## Repository Contents

- `Transformer_Analyzer_Code.py` - Main Python GUI and analysis program
- `requirements.txt` - Required Python packages
- `README.md` - Project documentation

## Reproducibility

This repository provides the Python software used for the calculations and graphical analysis associated with the research work.

The repository does not contain the original Kathmandu University smart-meter datasets. Therefore, users wishing to reproduce the analysis with the original measurements require access to the corresponding measurement data.

## Associated Research

This repository supports the energy analytics study conducted at Kathmandu University, Nepal.

The software is provided to support reproducibility of the calculations and graphical analysis presented in the associated research work.
