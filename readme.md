# KU-EnergyAnalytics

Python-based calculation and graph-generation tool developed for
energy consumption and power-quality analysis of the main transformer
at Kathmandu University, Nepal.

## Overview

This software was developed to process downloaded smart-meter data
and generate electrical energy and power-quality analyses.

The software does not automatically acquire data from the IAMMETER
cloud platform. Historical smart-meter data are downloaded from the
IAMMETER cloud platform and subsequently loaded into the Python
graphical user interface (GUI) for analysis.

## Study Scope

Kathmandu University has seven IAMMETER smart meters installed across
the campus. The analysis presented in the associated research paper
focuses on the meter installed at the main transformer.

The remaining six meters are outside the scope of the present analysis.

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

The input data consist of phase-wise voltage and current measurements
for the transformer.

The software processes the loaded data and performs the required
calculations and generates graphical outputs and PDF reports.

The analysis uses the loaded Transformer A, B, and C datasets for
the respective summer, winter, and festival periods.

## Data Availability

The original Kathmandu University smart-meter measurement datasets
are not included in this repository.

The software can be used with compatible CSV or Excel datasets.

## Requirements

- Python 3.x
- pandas
- numpy
- matplotlib
- openpyxl
- tkinter

## Installation

Install the required Python packages using:

    pip install -r requirements.txt

## Usage

Run the Python program using:

    python Transformer_Data_Analyzer.py

Load the Transformer A, B, and C datasets through the GUI for the
required seasons.

After loading the datasets, select the required analysis option from
the Analysis Options section.

The software can generate individual graphs as well as a complete
PDF analysis report.

## Repository Contents

- `Transformer_Data_Analyzer.py` - Main Python GUI and analysis program
- `requirements.txt` - Required Python packages
- `README.md` - Project documentation

## Associated Research

This repository supports the energy analytics study conducted at
Kathmandu University, Nepal.

The software is provided to support reproducibility of the
calculations and graphical analysis presented in the associated
research work.
