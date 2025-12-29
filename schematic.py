import os
import schemdraw
import schemdraw.elements as elm


def draw_equivalent_circuit(params, out_path="static/circuit.png"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with schemdraw.Drawing(file=out_path, show=False) as d:
        d.config(unit=2.0)

        # ===================== Rb =====================
        d += elm.Resistor()
        rb_center = d.here
        d += elm.Label().at((rb_center[0] - 0.6, rb_center[1] + 0.9)).label(
            f"Rb\n{params['Rb']['value']} Ω",
            fontsize=10
        )
        d += elm.Line().right(1)

        # ===================== SEI PARALLEL BLOCK =====================
        sei_left = d.here

        # --- top branch: capacitor (CPE_SEI) ---
        d.push()
        d += elm.Line().up(1.1)
        d += elm.Line().right(0.5)
        d += elm.Capacitor().right(1)
        d += elm.Line().right(0.5)
        d += elm.Line().down(1.1)
        d.pop()

        # CPE_SEI label
        d += elm.Label().at((sei_left[0] + 1.0, sei_left[1] + 2.0)).label(
            f"CPE_SEI\n{params['CPE_SEI']['value']}",
            fontsize=10
        )

        # --- bottom branch: R_SEI ---
        d += elm.Resistor().right(2).label(
            f"R_SEI\n{params['R_SEI']['value']} Ω",
            loc="bottom",
            fontsize=9
        )

        d += elm.Line().right(1)

        # ===================== CT + DIFFUSION PARALLEL BLOCK =====================
        ct_left = d.here

        # --- top branch: capacitor (CPE_DL) ---
        d.push()
        d += elm.Line().up(1.1)
        d += elm.Line().right(0.5)
        d += elm.Capacitor().right(1)
        d += elm.Line().right(0.5)
        d += elm.Line().down(1.1)
        d.pop()

        # CPE_DL label
        d += elm.Label().at((ct_left[0] + 1.0, ct_left[1] + 2.0)).label(
            f"CPE_DL\n{params['CPE_DL']['value']}",
            fontsize=10
        )

        # --- bottom branch: R_CT + Warburg ---
        d += elm.Resistor().right(1.2).label(
            f"R_CT\n{params['R_CT']['value']} Ω",
            loc="bottom",
            fontsize=9
        )

        d += elm.Resistor().right(0.8).label(
            f"W\n{params['Warburg']['value']}",
            loc="bottom",
            fontsize=9
        )

        d += elm.Line().right(1)

    return out_path
