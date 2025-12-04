import streamlit as st
import json
from pathlib import Path
import pandas as pd

# Sidebar Logo (perfekt zentriert)
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)

    LOGO_PATH = Path(__file__).parent.parent / "logo" / "logo_main.png"
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)

    st.markdown("<br>", unsafe_allow_html=True)

PATIENT_FILE = Path("data") / "patients.json"

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

st.title("📈 Weaning-Verläufe")

patients = load_patients()
if not patients:
    st.info("Es sind noch keine Patienten/messungen vorhanden.")
    st.stop()

pat_id = st.selectbox("Patient auswählen", list(patients.keys()))
patient = patients[pat_id]
st.write(f"Verlauf für: **{patient.get('name','')} ({patient.get('age','')} Jahre)**")

verlauf = patient.get("verlauf", [])
if not verlauf:
    st.info("Für diesen Patienten wurden noch keine Messungen gespeichert.")
    st.stop()

df = pd.DataFrame(verlauf)

st.subheader("Tabelle der Messungen")
st.dataframe(df)

if "timestamp" in df.columns and "score" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    df = df.set_index("timestamp")

    st.subheader("Score-Verlauf (Demo)")
    st.line_chart(df["score"])
else:
    st.info("Keine Score-Daten zum Plotten gefunden.")