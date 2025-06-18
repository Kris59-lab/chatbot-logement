import streamlit as st
import json
import os
import requests
from dotenv import load_dotenv

# Charger la clé API depuis .env
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL_NAME = "mistral-large-latest"
API_URL = "https://api.mistral.ai/v1/chat/completions"


@st.cache_data
def lire_json(path_fichier):
    """Charge les données JSON des logements."""
    with open(path_fichier, 'r', encoding='utf-8') as fichier:
        data = json.load(fichier)
        return data["logements"]


def generate_response(messages):
    """Appelle l’API Mistral pour obtenir une réponse."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"Erreur API : {response.status_code} - {response.text}")

    data = response.json()
    return data['choices'][0]['message']['content']


# --- INTERFACE STREAMLIT ---

st.set_page_config(page_title="Assistante Logement", page_icon="🏠")
st.title("🏠 Assistante IA - Infos Logement")

# Charger les logements
try:
    logements = lire_json("logements.json")
except Exception as e:
    st.error(f"Erreur lors du chargement des logements : {e}")
    st.stop()

# Choix du logement
logement_noms = [f"{l['id']} - {l['nom']}" for l in logements]
choix = st.selectbox("Choisissez un logement :", logement_noms)
logement = next(l for l in logements if f"{l['id']} - {l['nom']}" == choix)

# Initialisation de l'historique
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "Tu es une assistante IA professionnelle et chaleureuse. "
                "Tu aides les voyageurs concernant leur logement, leur donnant des renseignements clairs et réconfortants. "
                "Si tu ne sais pas répondre, redirige-les vers le propriétaire. "
                "Réponds uniquement en français. Voici les infos du logement :\n"
                f"{json.dumps(logement, indent=2, ensure_ascii=False)}"
            )
        }
    ]
    st.session_state.chat_log = []


# Affichage des échanges
for msg in st.session_state.chat_log:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrée utilisateur
if user_input := st.chat_input("Posez votre question..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.chat_log.append({"role": "user", "content": user_input})

    try:
        response = generate_response(st.session_state.messages)
    except Exception as e:
        response = f"Erreur : {e}"

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.chat_log.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)
