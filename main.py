from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
from backend.eis import nyquist_plot
from backend.utils import generate_cell_id, generate_barcode
from backend.eis import load_eis_csv, fit_equivalent_circuit, bode_plot, compute_soh
from backend.schematic import draw_equivalent_circuit

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

os.makedirs("uploads/csv", exist_ok=True)

DEFAULT_META = {
    "cell_condition": "Recycled",
    "manufacturer": "Molicel",
    "model": "INR21700-P45B",
    "cell_type": "Li-ion",
    "form_factor": "Cylindrical 21700",
    "mass_g": 70.0,
    "height_mm": 70.15,
    "diameter_mm": 21.55,
    "volume_cm3": 25.59,
    "nominal_voltage": 3.6,
    "nominal_energy": 16.2,
    "nominal_capacity": 4.5,
    "voltage_range": "2.5–4.2",
    "current_cont": 8.61,
    "current_peak": 17.5,
    "power_cont": 25.6,
    "power_peak": 50.0,
    "energy_density_g": 154,
    "energy_density_v": 375,
    "power_density_g": 837,
    "power_density_v": 2.04,
}


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    cid = generate_cell_id()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "cell_id": cid,
            "barcode": generate_barcode(cid),
            "meta": DEFAULT_META,
            "params": None,
            "soh": None,
            "bode": None,
            "circuit_img": None,
        },
    )


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    csv_file: UploadFile = File(...),
    image_file: UploadFile = File(...)
):
    cid = generate_cell_id()

    csv_path = f"uploads/csv/{csv_file.filename}"
    with open(csv_path, "wb") as f:
        shutil.copyfileobj(csv_file.file, f)

    freq, Z = load_eis_csv(csv_path)
    params = fit_equivalent_circuit(freq, Z)
    soh = compute_soh(params["Rb"]["value"])
    bode = bode_plot(freq, Z)
    nyquist_html = nyquist_plot(freq, Z)


    circuit_path = draw_equivalent_circuit(params)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "cell_id": cid,
            "barcode": generate_barcode(cid),
            "meta": DEFAULT_META,
            "params": params,
            "soh": soh,
            "bode": bode,
            "nyquist": nyquist_html,
            "circuit_img": "/" + circuit_path,

        },
    )
