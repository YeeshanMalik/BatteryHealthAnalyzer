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

##Directory Structure
battery_assignment/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── eis.py               # EIS processing & SOH logic
│   ├── plots.py             # Interactive Plotly plots
│   ├── schematic.py         # Equivalent circuit rendering
│   └── utils.py             # Helpers
│
├── templates/
│   └── index.html           # Single-page frontend
│
├── static/
│   └── generated plots & images
│
├── requirements.txt
└── README.md


## Run
```bash
uvicorn backend.main:app --reload
