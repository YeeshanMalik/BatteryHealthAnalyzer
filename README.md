# Battery Cell Health Diagnostics using EIS

A FastAPI-based web application for lithium-ion battery health assessment using Electrochemical Impedance Spectroscopy (EIS). The system extracts real and imaginary impedance components, estimates equivalent circuit parameters, visualizes interactive Nyquist and Bode plots, and computes State of Health (SOH).

## Features
- EIS CSV ingestion and preprocessing
- Equivalent circuit parameter extraction
- Interactive Nyquist & Bode plots (Plotly)
- Rs intercept and Warburg diffusion analysis
- State of Health (SOH) estimation
- Modern single-page web interface
- PDF export and dark mode support

## Tech Stack
- **Backend:** FastAPI, Python
- **Frontend:** HTML, CSS, Jinja2
- **Visualization:** Plotly

## Run
```bash
uvicorn backend.main:app --reload
