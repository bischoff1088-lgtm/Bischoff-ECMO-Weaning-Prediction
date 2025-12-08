import streamlit as st
from pathlib import Path
import json
from datetime import date
import pandas as pd


# ---------------------------------------
# Speicherort für die Studiendaten
# ---------------------------------------
STUDY_FILE = Path("data") / "study_30cerw_cases.json"


def load_cases() -> dict:
    """Bestehende Fälle aus JSON laden."""
    if not STUDY_FILE.exists():
        return {}
    try:
        with open(STUDY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            return {}
    except Exception:
        return {}


def save_cases(cases: dict):
    """Fälle in JSON-Datei speichern."""
    STUDY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STUDY_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)


# ---------------------------------------
# Sidebar: Logo wie in den anderen Seiten
# ---------------------------------------
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    LOGO_PATH = Path(__file__).parent.parent / "logo" / "logo_main.png"
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)
    st.markdown("<br>", unsafe_allow_html=True)


# ---------------------------------------
# Seite: Datenerhebungsbogen 30CERW
# ---------------------------------------
st.title("📝 Datenerhebungsbogen – 30CERW-Score (VA-ECMO)")

st.info(
    "Diese Seite dient zur **pseudonymisierten Erfassung** der Studiendaten für den "
    "30CERW-Score (VA-ECMO).\n\n"
    "Bitte **keine Klarnamen** und keine direkt identifizierenden Daten eingeben."
)

cases = load_cases()

st.markdown("## Allgemeine Studienangaben")

col1, col2, col3 = st.columns(3)
with col1:
    study_id = st.text_input("Studien-ID (pseudonymisiert)")
with col2:
    center = st.text_input("Zentrum")
with col3:
    va_date = st.date_input("Datum der VA-Implantation", value=date.today())

col4, col5, col6 = st.columns(3)
with col4:
    sex = st.selectbox("Geschlecht", ["-", "w", "m", "divers"])
with col5:
    age = st.number_input("Alter [Jahre]", min_value=0, max_value=120, value=60)
with col6:
    height_cm = st.number_input("Körpergröße [cm]", min_value=100, max_value=230, value=175)

col7, col8 = st.columns(2)
with col7:
    weight_kg = st.number_input("Körpergewicht [kg]", min_value=30.0, max_value=250.0, value=80.0, step=0.5)
with col8:
    bmi = st.number_input("BMI", min_value=10.0, max_value=80.0, value=26.0, step=0.1)


st.markdown("## Reanimation")

col9, col10, col11 = st.columns(3)
with col9:
    cpr = st.selectbox("Reanimation vor ECMO", ["-", "ja", "nein"])
with col10:
    cpr_duration = st.selectbox("Falls ja: Dauer", ["-", "< 30 min", "> 30 min"])
with col11:
    ecpr = st.selectbox("ECPR", ["-", "ja", "nein"])


st.markdown("## Beatmung / Intensivaufenthalt (präimplantativ)")

col12, col13, col14 = st.columns(3)
with col12:
    mech_vent_pre = st.selectbox("Mechanische Beatmung prä-ECMO", ["-", "ja", "nein"])
with col13:
    vent_duration_cat = st.selectbox("Beatmungsdauer", ["-", "< 7 Tage", "> 7 Tage"])
with col14:
    icu_days_pre = st.number_input("ICU-Aufenthalt prä-ECMO [Tage]", min_value=0, max_value=365, value=0)


st.markdown("## Diagnostische Kategorie")

col15, col16 = st.columns(2)
with col15:
    main_diag = st.selectbox(
        "Hauptdiagnose",
        [
            "-",
            "Kardiogener Schock",
            "Postkardiotomie Schock",
            "Gemischter Schock",
        ],
    )
with col16:
    cause = st.selectbox(
        "Ursache",
        [
            "-",
            "AMI (STEMI / NSTEMI)",
            "Dilatative Kardiomyopathie",
            "Akute Herzinsuffizienz",
            "Myokarditis",
            "Post-OP",
            "Sonstiges",
        ],
    )

other_cause = st.text_input("Falls 'Sonstiges': kurze Beschreibung", value="")


st.markdown("## Vorerkrankungen")

def yes_no(label: str):
    return st.selectbox(label, ["-", "ja", "nein"])

col17, col18, col19 = st.columns(3)
with col17:
    copd = yes_no("COPD")
with col18:
    cki = yes_no("Chronische Niereninsuffizienz")
with col19:
    khk = yes_no("KHK")

col20, col21, col22 = st.columns(3)
with col20:
    cardiomyopathy = yes_no("Kardiomyopathie")
with col21:
    liver_disease = yes_no("Lebererkrankungen")
with col22:
    diabetes = yes_no("Diabetes mellitus")

cerebro_vasc = yes_no("Zerebrovaskuläre Vorerkrankungen")
other_comorbid = st.text_area("Weitere relevante Vorerkrankungen", height=80)


st.markdown("## Laborparameter (präimplantativ)")

col23, col24, col25 = st.columns(3)
with col23:
    ph = st.number_input("pH", min_value=6.5, max_value=7.8, value=7.35, step=0.01)
with col24:
    lactate = st.number_input("Laktat [mmol/L]", min_value=0.0, max_value=30.0, value=2.0, step=0.1)
with col25:
    be = st.number_input("Base Excess (BE) [mmol/L]", min_value=-30.0, max_value=30.0, value=0.0, step=0.5)

col26, col27, col28 = st.columns(3)
with col26:
    creatinine = st.number_input("Kreatinin [mg/dl]", min_value=0.1, max_value=20.0, value=1.0, step=0.1)
with col27:
    bilirubin = st.number_input("Bilirubin [mg/dl]", min_value=0.1, max_value=30.0, value=1.0, step=0.1)
with col28:
    pao2 = st.number_input("PaO₂ [mmHg]", min_value=20.0, max_value=600.0, value=80.0, step=1.0)


st.markdown("## Vitalparameter / Kreislauf")

col29, col30, col31 = st.columns(3)
with col29:
    map_mean = st.number_input("MAP [mmHg]", min_value=30, max_value=130, value=65)
with col30:
    vasopressor = yes_no("Vasopressor erforderlich")
with col31:
    norad_eq = st.number_input(
        "Noradrenalin-Äquivalent [g/kgKG/min]",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.01,
    )

mech_vent_status = yes_no("Mechanische Beatmung (aktuell)")


st.markdown("## Primäre Endpunkte")

col32, col33, col34 = st.columns(3)
with col32:
    surv_30d = yes_no("30-Tage-Überleben")
with col33:
    weaning_success = yes_no("Erfolgreiches ECMO-Weaning")
with col34:
    explant_date = st.date_input("Datum ECMO-Explantation", value=date.today())

weaning_def = st.text_input(
    "Definition Weaning (intern)",
    value="Explantation ohne erneute ECMO innerhalb von ___ Stunden",
)


st.markdown("---")

if st.button("📥 Fall speichern"):
    if not study_id.strip():
        st.error("Bitte eine **Studien-ID** angeben – sie ist der Schlüssel für diesen Fall.")
    else:
        case_data = {
            "Studien_ID": study_id.strip(),
            "Zentrum": center.strip(),
            "Datum_VA_Implantation": va_date.isoformat(),
            "Geschlecht": sex,
            "Alter": age,
            "Koerpergroesse_cm": height_cm,
            "Koerpergewicht_kg": weight_kg,
            "BMI": bmi,
            # Reanimation
            "Reanimation_vor_ECMO": cpr,
            "Reanimationsdauer": cpr_duration,
            "ECPR": ecpr,
            # Beatmung / ICU
            "Mechanische_Beatmung_prae": mech_vent_pre,
            "Beatmungsdauer_Kat": vent_duration_cat,
            "ICU_Aufenthalt_prae_Tage": icu_days_pre,
            # Diagnose
            "Hauptdiagnose": main_diag,
            "Ursache": cause,
            "Ursache_sonstiges": other_cause,
            # Vorerkrankungen
            "COPD": copd,
            "Chronische_Niereninsuffizienz": cki,
            "KHK": khk,
            "Kardiomyopathie": cardiomyopathy,
            "Lebererkrankungen": liver_disease,
            "Diabetes_mellitus": diabetes,
            "Zerebrovaskulaere_Vorerkrankungen": cerebro_vasc,
            "Weitere_Vorerkrankungen": other_comorbid,
            # Labor
            "pH": ph,
            "Laktat": lactate,
            "BE": be,
            "Kreatinin": creatinine,
            "Bilirubin": bilirubin,
            "PaO2_mmHg": pao2,
            # Kreislauf
            "MAP_mmHg": map_mean,
            "Vasopressor_erforderlich": vasopressor,
            "Noradrenalin_Aequivalent_g_pro_kgKG_min": norad_eq,
            "Mechanische_Beatmung_aktuell": mech_vent_status,
            # Endpunkte
            "Ueberleben_30Tage": surv_30d,
            "ECMO_Weaning_erfolgreich": weaning_success,
            "Datum_ECMO_Explantation": explant_date.isoformat(),
            "Weaning_Definition_intern": weaning_def,
        }

        # existierende Fälle laden, aktuellen Fall (nach Studien-ID) setzen
        cases[study_id.strip()] = case_data
        save_cases(cases)
        st.success(f"Fall **{study_id}** wurde gespeichert / aktualisiert.")


# ---------------------------------------
# Übersicht aller erfassten Fälle
# ---------------------------------------
st.markdown("## Bisher erfasste Fälle")

if cases:
    df = pd.DataFrame.from_dict(cases, orient="index")
    st.dataframe(df)
else:
    st.info("Bisher wurden noch **keine Fälle** erfasst.")