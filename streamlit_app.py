import streamlit as st
import json
import os
from pathlib import Path

# -------------------------------------------------------------
# Grundkonfiguration der App
# -------------------------------------------------------------
st.set_page_config(
    page_title="Bischoff ECMO Weaning Prediction",
    page_icon="🫀",
    layout="centered"
)

USER_FILE = "data/user.json"

# -------------------------------------------------------------
# Hilfsfunktionen für Nutzer
# -------------------------------------------------------------
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# -------------------------------------------------------------
# Sidebar: Logo + Navigation
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)

    # Logo-Pfad robust bestimmen (egal, von wo die App gestartet wird)
    LOGO_PATH = Path(__file__).parent / "logo" / "logo_main.png"
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=160)
    else:
        st.write("⚠️ Logo nicht gefunden")

    st.markdown("<br>", unsafe_allow_html=True)

    # keine eigene Navigation mehr – Streamlit-Menü reicht aus

# -------------------------------------------------------------
# Startseite – Titel & Untertitel
# -------------------------------------------------------------
st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:0px;'>
        Bischoff ECMO Weaning Prediction
    </h1>
    <h4 style='text-align:center; color:#555; margin-top:5px;'>
        Frühwarn- & Entscheidungsunterstützung für VA-ECMO-Weaning (Studienversion)
    </h4>
    <br>
    """,
    unsafe_allow_html=True
)

# Medizinischer Hinweis / Disclaimer
st.info(
    "Dieses Tool dient als **klinisches Assistenzsystem** zur Abschätzung der "
    "**Weaning-Wahrscheinlichkeit** unter VA-ECMO.\n\n"
    "Es ersetzt **keine ärztliche Beurteilung** und darf nur im Rahmen von "
    "Forschung/Lehre bzw. kontrollierten Simulationen verwendet werden."
)

st.write("---")

users = load_users()
have_users = len(users) > 0

# -------------------------------------------------------------
# Optionales Login
# -------------------------------------------------------------
st.markdown("### 🔐 Login (optional)")

username = st.text_input("Benutzername", key="login_user")
password = st.text_input("Passwort", type="password", key="login_pass")

if not have_users:
    st.info(
        "Es sind noch **keine Benutzer registriert**.\n\n"
        "Wenn du möchtest, kannst du dich unten registrieren – "
        "die App ist aber auch **ohne Login** voll nutzbar."
    )

if st.button("Login"):
    if not have_users:
        st.warning(
            "Noch keine Benutzer vorhanden. "
            "Bitte zuerst unten registrieren (optional)."
        )
    else:
        if username in users and users[username] == password:
            st.success("Login erfolgreich (Demo – aktuell ohne Einschränkungen).")
        else:
            st.warning(
                "Benutzer nicht gefunden oder Passwort falsch.\n\n"
                "Falls du noch kein Konto hast, registriere dich unten (optional)."
            )
else:
    if have_users:
        st.info(
            "Login ist optional – die App kann auch ohne Anmeldung genutzt werden."
        )

# -------------------------------------------------------------
# Registrierung (optional)
# -------------------------------------------------------------
st.markdown("---")
st.markdown("### 🧾 Registrierung (optional)")

new_user = st.text_input("Neuer Benutzername", key="reg_user")
new_pass = st.text_input("Passwort wählen", type="password", key="reg_pass")

if st.button("Jetzt registrieren"):
    if new_user.strip() == "" or new_pass.strip() == "":
        st.error("Bitte Benutzername und Passwort eingeben.")
    elif new_user in users:
        st.error("Benutzername existiert bereits.")
    else:
        users[new_user] = new_pass
        save_users(users)
        st.success(
            f"Benutzer **{new_user}** wurde registriert! "
            "Du kannst dich jetzt im Login-Bereich anmelden (optional)."
        )

# Hinweis unten
st.markdown(
    """
    <br>
    <p style="text-align:center; color:#777;">
        Login & Registrierung sind freiwillig.<br>
        Nutze das Menü links, um Patientendaten, Weaning-Tool und Verläufe zu öffnen.
    </p>
    """,
    unsafe_allow_html=True
)
