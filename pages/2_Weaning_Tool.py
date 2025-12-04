import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# Sidebar Logo (perfekt zentriert)
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)

    LOGO_PATH = Path(__file__).parent.parent / "logo" / "logo_main.png"
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)

    st.markdown("<br>", unsafe_allow_html=True)
PATIENT_FILE = Path("data") / "patients.json"

# ---------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------
def load_patients():
    if not PATIENT_FILE.exists():
        return {}
    try:
        with open(PATIENT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        else:
            return {}
    except json.JSONDecodeError:
        return {}

def save_patients(data: dict):
    PATIENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PATIENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------
# Demo-Berechnungsmodell
# (vereinfachte Gewichtung, ECMO-Flow & vitale Parameter stärker gewichtet)
# ---------------------------------------------------------
def calc_weaning_score(
    map_mmHg,
    hr,
    vasopressor,
    ecmo_flow,
    sweep,
    ecmo_fio2,
    vent_fio2,
    peep,
    dp,
    lactate,
    ph,
    pao2,
    organ,
    echo,
):
    # alles auf 0..1 Risiko normieren (0 = gut, 1 = schlecht)
    def clamp01(x): 
        return max(0.0, min(1.0, x))

    # Hämodynamik
    if map_mmHg < 55:
        map_risk = 1.0
    elif map_mmHg < 65:
        map_risk = 0.7
    elif map_mmHg <= 85:
        map_risk = 0.2
    else:
        map_risk = 0.5

    if hr < 50 or hr > 130:
        hr_risk = 1.0
    elif 50 <= hr <= 110:
        hr_risk = 0.3
    else:
        hr_risk = 0.6

    vaso_risk = clamp01(vasopressor / 10.0)

    # Oxygenierung / Ventilation
    if pao2 < 60:
        pao2_risk = 0.9
    elif pao2 < 80:
        pao2_risk = 0.5
    else:
        pao2_risk = 0.2

    if lactate > 4:
        lactate_risk = 1.0
    elif lactate > 2:
        lactate_risk = 0.6
    else:
        lactate_risk = 0.2

    if ph < 7.2 or ph > 7.5:
        ph_risk = 0.9
    elif 7.3 <= ph <= 7.45:
        ph_risk = 0.2
    else:
        ph_risk = 0.5

    # ECMO-Parameter – Flow besonders wichtig
    if ecmo_flow < 2.0:
        flow_risk = 1.0
    elif ecmo_flow < 3.0:
        flow_risk = 0.6
    else:
        flow_risk = 0.2

    sweep_risk = clamp01((sweep - 1.0) / 4.0)  # höherer Sweep = eher schlechter
    ecmo_fio2_risk = clamp01((ecmo_fio2 - 0.5) / 0.5)
    vent_fio2_risk = clamp01((vent_fio2 - 0.4) / 0.6)
    peep_risk = clamp01(abs(peep - 10) / 10.0)
    dp_risk = clamp01((dp - 12) / 10.0)

    # Organfunktion / Echo (0 = schlecht, 10 = gut)
    organ_risk = clamp01((10 - organ) / 10.0)
    echo_risk = clamp01((10 - echo) / 10.0)

    # Gewichtung der Bereiche
    vitals = (map_risk + hr_risk + vaso_risk + pao2_risk + lactate_risk + ph_risk) / 6
    ecmo = (flow_risk * 2 + sweep_risk + ecmo_fio2_risk + vent_fio2_risk + peep_risk + dp_risk) / 7
    organs = (organ_risk + echo_risk) / 2

    # Flow stärker gewichtet -> ECMO-Teil insgesamt stärker
    total_risk = 0.4 * ecmo + 0.35 * vitals + 0.25 * organs
    total_risk = clamp01(total_risk)

    success_prob = round((1 - total_risk) * 100, 1)
    failure_prob = round(100 - success_prob, 1)

    # Ampel-Einteilung
    if success_prob >= 75:
        level = "green"
        text = "🟢 Günstiges Weaning-Szenario (Demo)"
    elif success_prob >= 50:
        level = "yellow"
        text = "🟡 Grenzbereich – engmaschig beobachten (Demo)"
    else:
        level = "red"
        text = "🔴 Ungünstiges Weaning-Szenario (Demo)"

    return success_prob, failure_prob, level, text

# ---------------------------------------------------------
# Seite
# ---------------------------------------------------------
st.title("🫁 Weaning-Tool (Demo)")

patients = load_patients()
if not patients:
    st.warning("Bitte zuerst einen Patienten unter **Patientendaten** anlegen.")
    st.stop()

st.markdown(
    """
Dieses Tool ist ein **Studienprototyp**. Alle Berechnungen sind vereinfachte, nicht validierte Demo-Modelle –
**nicht** zur klinischen Entscheidungsfindung geeignet.
"""
)

st.markdown("### Interpretation der Skalen (0–10)")
st.markdown(
    """
- **0–3** → kritisch / stark eingeschränkt  
- **4–6** → mittel / engmaschig beobachten  
- **7–10** → gut / stabil  
"""
)

# Patient auswählen
st.markdown("---")
pat_id = st.selectbox("Patient auswählen", list(patients.keys()))
patient = patients[pat_id]
st.info(f"Aktueller Patient: **{pat_id} – {patient.get('name', '')} ({patient.get('age', '')} Jahre)**")

st.markdown("### Eingabe der aktuellen Parameter")

c1, c2, c3 = st.columns(3)
with c1:
    map_mmHg = st.number_input("MAP (mmHg)", value=70.0, step=1.0)
    hr = st.number_input("Herzfrequenz (/min)", value=85.0, step=1.0)
    vasopressor = st.number_input("Vasopressorenbedarf (0–10)", value=3.0, min_value=0.0, max_value=10.0, step=0.1)
    lactate = st.number_input("Laktat (mmol/l)", value=2.0, step=0.1)
with c2:
    ecmo_flow = st.number_input("ECMO-Flow (L/min)", value=3.2, step=0.1)
    sweep = st.number_input("Sweep-Gas (L/min)", value=2.0, step=0.1)
    ecmo_fio2 = st.number_input("ECMO FiO₂ (0–1)", value=0.6, min_value=0.21, max_value=1.0, step=0.01, format="%.2f")
    vent_fio2 = st.number_input("Beatmungs-FiO₂ (0–1)", value=0.5, min_value=0.21, max_value=1.0, step=0.01, format="%.2f")
with c3:
    peep = st.number_input("PEEP (cmH₂O)", value=10.0, step=1.0)
    dp = st.number_input("Driving Pressure (cmH₂O)", value=12.0, step=1.0)
    ph = st.number_input("pH", value=7.38, step=0.01, format="%.2f")
    pao2 = st.number_input("PaO₂ (mmHg)", value=80.0, step=1.0)

st.markdown("### Organfunktion & Echo (0–10)")
col_o, col_e = st.columns(2)
with col_o:
    organ = st.slider("Organfunktion (0=schlecht, 10=gut)", 0.0, 10.0, 7.0, 0.1)
with col_e:
    echo = st.slider("Echo-Score LV/RV (0=schlecht, 10=gut)", 0.0, 10.0, 6.0, 0.1)

if st.button("Weaning-Risiko berechnen & speichern"):
    success, failure, level, text = calc_weaning_score(
        map_mmHg, hr, vasopressor, ecmo_flow, sweep, ecmo_fio2,
        vent_fio2, peep, dp, lactate, ph, pao2, organ, echo
    )

    st.markdown("## Ergebnis (Demo)")
    st.write(f"**Erfolgswahrscheinlichkeit:** {success:.1f} %")
    st.write(f"**Risiko für Weaning-Versagen:** {failure:.1f} %")
    st.write(f"**Ampel:** {text}")

    # Messung im Verlauf speichern
    verlauf = patient.get("verlauf", [])
    verlauf.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "MAP": map_mmHg,
        "HR": hr,
        "Vasopressor": vasopressor,
        "ECMO_Flow": ecmo_flow,
        "Sweep": sweep,
        "ECMO_FiO2": ecmo_fio2,
        "Vent_FiO2": vent_fio2,
        "PEEP": peep,
        "DP": dp,
        "Laktat": lactate,
        "pH": ph,
        "PaO2": pao2,
        "Organ": organ,
        "Echo": echo,
        "score": success,
    })
    patient["verlauf"] = verlauf
    patients[pat_id] = patient
    save_patients(patients)

    st.success("Messung wurde im Verlauf gespeichert.")