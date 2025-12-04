import streamlit as st
import json
import os
from pathlib import Path

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
        # Falls aus Versehen eine Liste gespeichert wurde -> in Dict wandeln
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
# Seite
# ---------------------------------------------------------
st.title("Patientendaten")

patients = load_patients()

# Übersicht vorhandener Patienten
st.subheader("Übersicht vorhandener Patienten")
if patients:
    table_data = [
        {
            "Patienten-ID": pid,
            "Name": pdata.get("name", ""),
            "Alter": pdata.get("age", ""),
            "Diagnose": pdata.get("diagnose", ""),
            "Anzahl Messungen": len(pdata.get("verlauf", [])),
        }
        for pid, pdata in patients.items()
    ]
    st.table(table_data)
else:
    st.info("Noch keine Patienten gespeichert.")

st.markdown("---")
st.subheader("Neuen Patienten anlegen oder vorhandenen bearbeiten")

col1, col2 = st.columns(2)
with col1:
    pat_id = st.text_input("Patienten-ID (z.B. ECMO-001)")
    name = st.text_input("Name")
with col2:
    diagnose = st.text_input("Diagnose / Kommentar", value="VA-ECMO")
    age = st.number_input("Alter", min_value=0, max_value=120, value=60)

if st.button("Patient speichern"):
    if not pat_id:
        st.error("Bitte eine Patienten-ID eingeben.")
    else:
        if not isinstance(patients, dict):
            patients = {}

        if pat_id not in patients:
            # Neuer Patient
            patients[pat_id] = {
                "name": name,
                "age": age,
                "diagnose": diagnose,
                "verlauf": []
            }
        else:
            # Patient aktualisieren (Verlauf behalten)
            patients[pat_id]["name"] = name
            patients[pat_id]["age"] = age
            patients[pat_id]["diagnose"] = diagnose

        save_patients(patients)
        st.success(f"Patient **{pat_id}** wurde gespeichert.")

st.markdown("### Patient löschen")

if patients:
    del_id = st.selectbox("Patient auswählen", list(patients.keys()))
    if st.button("Ausgewählten Patienten löschen"):
        patients.pop(del_id, None)
        save_patients(patients)
        st.warning(f"Patient **{del_id}** wurde gelöscht.")
else:
    st.info("Zum Löschen muss zuerst ein Patient angelegt werden.")