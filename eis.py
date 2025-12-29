import pandas as pd
import numpy as np
from impedance.models.circuits import CustomCircuit
import plotly.graph_objects as go

RB_MAX = 0.05

PARAM_RANGES = {
    "Rb": (0.0, 0.05),
    "R_SEI": (0.0, 0.05),
    "R_CT": (0.0, 0.1),
    "CPE_SEI": (0.0, 10.0),
    "CPE_DL": (0.0, 10.0),
    "Warburg": (0.0, 0.05),
}


def normalize(val, mn, mx):
    return max(0.0, min(100.0, (val - mn) / (mx - mn) * 100))


def load_eis_csv(path):
    df = pd.read_csv(path)

    freq = df.iloc[:, 0].astype(float).values
    z_real = df.iloc[:, 1].astype(float).values
    z_imag = df.iloc[:, 2].astype(float).values

    Z = z_real + 1j * z_imag

    mask = np.isfinite(freq) & np.isfinite(Z.real) & np.isfinite(Z.imag)
    return freq[mask], Z[mask]


def fit_equivalent_circuit(freq, Z):
    # Manual low-frequency filtering (robust across impedance.py versions)
    mask = freq > 1e-3
    freq = freq[mask]
    Z = Z[mask]

    circuit = "R0-p(R1,CPE1)-p(R2,CPE2)-W1"
    initial_guess = [
        0.01,     # Rb
        0.02,     # R_SEI
        1e-4,     # CPE_SEI_Q
        0.8,      # CPE_SEI_n
        0.05,     # R_CT
        1e-3,     # CPE_DL_Q
        0.9,      # CPE_DL_n
        0.01      # Warburg
    ]

    model = CustomCircuit(circuit, initial_guess=initial_guess)
    model.fit(freq, Z)

    # Flatten parameter names safely
    names = []
    for p in model.get_param_names():
        if isinstance(p, list):
            names.extend(p)
        else:
            names.append(p)

    raw = dict(zip(names, model.parameters_))

    extracted = {
        "Rb": raw["R0"],
        "R_SEI": raw["R1"],
        "CPE_SEI": raw["CPE1_0"],
        "R_CT": raw["R2"],
        "CPE_DL": raw["CPE2_0"],
        "Warburg": raw["W1"],
    }

    results = {}
    for k, v in extracted.items():
        mn, mx = PARAM_RANGES[k]
        results[k] = {
            "value": round(v, 6),
            "indicator": normalize(v, mn, mx)
        }

    return results


import numpy as np
import plotly.graph_objects as go


def bode_plot(freq, Z):
    freq = np.asarray(freq)
    Z = np.asarray(Z)

    mag = np.abs(Z)
    phase = np.angle(Z, deg=True)

    fig = go.Figure()

    # Magnitude
    fig.add_trace(
        go.Scatter(
            x=freq,
            y=mag,
            mode="lines+markers",
            name="|Z| (Ω)",
            yaxis="y1"
        )
    )

    # Phase
    fig.add_trace(
        go.Scatter(
            x=freq,
            y=phase,
            mode="lines+markers",
            name="Phase (deg)",
            yaxis="y2"
        )
    )

    fig.update_layout(
        title="Bode Plot",
        xaxis=dict(
            title="Frequency (Hz)",
            type="log",
            range=[
                np.log10(freq.min()),
                np.log10(freq.max())
            ],
            ticks="outside"
        ),

        yaxis=dict(
            title="Magnitude (Ω)",
            type="log",
            tickformat=".2e",
            showgrid=True
        ),

        yaxis2=dict(
            title="Phase (deg)",
            overlaying="y",
            side="right",
            range=[-90, 90],
            showgrid=False
        ),

        legend=dict(
            x=1.02,
            y=1,
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        ),

        margin=dict(l=80, r=80, t=60, b=60),
        template="plotly_white",
        height=500
    )

    return fig.to_html(full_html=False)


def nyquist_plot(freq, Z_measured, Z_fitted=None):
    freq = np.asarray(freq)
    Zm = np.asarray(Z_measured)

    fig = go.Figure()

    # --------------------------------------------------
    # 1. Measured data (colored by frequency)
    # --------------------------------------------------
    fig.add_trace(
        go.Scatter(
            x=Zm.real,
            y=-Zm.imag,
            mode="markers",
            name="Data",
            marker=dict(
                size=7,
                color=np.log10(freq),
                colorscale="Viridis",
                colorbar=dict(
                    title="log₁₀(f / Hz)"
                ),
                showscale=True
            ),
            customdata=freq,
            hovertemplate=(
                "Z′ = %{x:.4f} Ω<br>"
                "-Z″ = %{y:.4f} Ω<br>"
                "f = %{customdata:.2e} Hz"
            )
        )
    )

    # --------------------------------------------------
    # 2. Fit curve
    # --------------------------------------------------
    if Z_fitted is not None:
        Zf = np.asarray(Z_fitted)
        fig.add_trace(
            go.Scatter(
                x=Zf.real,
                y=-Zf.imag,
                mode="lines",
                name="Fit",
                line=dict(width=3, color="orange")
            )
        )

    # --------------------------------------------------
    # 3. Rs (high-frequency intercept)
    # --------------------------------------------------
    idx_hf = np.argmax(freq)
    Rs = Zm.real[idx_hf]

    fig.add_trace(
        go.Scatter(
            x=[Rs],
            y=[0],
            mode="markers+text",
            name="Rs",
            marker=dict(color="red", size=10),
            text=[f"Rs = {Rs:.4f} Ω"],
            textposition="top right"
        )
    )

    # --------------------------------------------------
    # 4. Warburg region (low-frequency tail, ~45°)
    # --------------------------------------------------
    n_tail = max(3, int(0.2 * len(Zm)))
    Z_tail = Zm[-n_tail:]

    x0 = Z_tail.real.min()
    x1 = Z_tail.real.max()
    y0 = -Z_tail.imag.min()
    y1 = y0 + (x1 - x0)  # 45° slope

    fig.add_trace(
        go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode="lines",
            name="Warburg (~45°)",
            line=dict(dash="dash", color="gray", width=2)
        )
    )

    # --------------------------------------------------
    # Layout (CRITICAL for Nyquist correctness)
    # --------------------------------------------------
    fig.update_layout(
    width=850,
    height=500,
    margin=dict(l=70, r=120, t=60, b=60),

    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="black",
        borderwidth=1
    ),

    coloraxis_colorbar=dict(
        title="log10(freq)",
        x=1.05
    ),

    xaxis=dict(
        title="Z'(ω) [Ω]",
        zeroline=True,
        zerolinecolor="black",
        zerolinewidth=1
    ),
    yaxis=dict(
        title="-Z''(ω) [Ω]",
        zeroline=True,
        zerolinecolor="black",
        zerolinewidth=1,
        scaleanchor="x",
        scaleratio=1
    )
)


    return fig.to_html(full_html=False)

def compute_soh(Rb):
    """
    Compute State of Health from bulk resistance.
    Accepts either a float or a dict with a 'value' key.
    """

    if isinstance(Rb, dict):
        Rb_value = Rb.get("value")
    else:
        Rb_value = Rb

    if Rb_value is None:
        raise ValueError("Rb value missing for SOH computation")

    RB_MAX = 0.05  # reference max resistance
    soh = (Rb_value / RB_MAX) * 100

    return round(min(100.0, soh), 2)