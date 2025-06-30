import streamlit as st
import pandas as pd
import requests as r
import json
import base64
import os
from sklearn.neighbors import NearestNeighbors

# --- Configuration de la page ---
st.set_page_config(page_title="WildFlix", layout="centered")

# --- STYLE CSS personnalisé ---
st.markdown("""
    <style>
        .stApp {
            background-color: black;
            color: white;
            text-align: center;
        }
        img {
            width: 100%;
            border-radius: 10px;
        }
        div.stButton > button {
            background-color: white;
            color: black;
            font-size: 18px;
            border-radius: 8px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Fichier JSON où stocker les utilisateurs
USER_FILE = "users1.json"

# Fonction de sauvegarde des utilisateurs
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Fonction de chargement des utilisateurs
def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

#  Initialisation
if "USERS" not in st.session_state:
    st.session_state.USERS = load_users()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "show_registration" not in st.session_state:
    st.session_state.show_registration = False

#  Inscription
if st.session_state.get("show_registration", False):
    st.markdown("<h1 style='font-size:100px;color:red;'>WildFlix</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:30px;color:white;'>Création de Compte</h1>", unsafe_allow_html=True)

    new_username = st.text_input("Nom d'utilisateur", key="register_username")
    new_password = st.text_input("Mot de passe", type="password", key="register_password")
    new_mail = st.text_input("Adresse Mail", key="register_email")

    if st.button("✅ Enregistrer"):
        if new_username in st.session_state.USERS:
            st.error("Ce nom d'utilisateur est déjà pris.")
        else:
            st.session_state.USERS[new_username] = {"password": new_password, "role": "user"}
            save_users(st.session_state.USERS)
            st.success("Compte créé avec succès ! Vous pouvez maintenant vous connecter.")

    if st.button("↩️ Retour Connexion"):
        st.session_state.show_registration = False
        st.rerun()

#  Connexion
def login():
    # Titre principal
    st.markdown("<h1 style='font-size:100px;color:red;'>WildFlix</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:30px;color:white;'>Connexion requise pour accéder à la plateforme </h1>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Label pour le nom d'utilisateur
    st.markdown("""<div style='text-align: left; font-size:15px; margin-bottom: -1px;'><label for='user'>Nom d'Utilisateur</label></div>""", unsafe_allow_html=True)
    username = st.text_input("")

    # Label pour le mot de passe
    st.markdown("""<div style='text-align: left; font-size:15px; margin-bottom: -1px;'><label for='motdepasse'>Mot de passe</label></div>""", unsafe_allow_html=True)
    password = st.text_input("", type="password")
    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("🔑 Se connecter"):
        if username in st.session_state.USERS:
            stored_password = st.session_state.USERS[username]["password"]
            if password == stored_password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = st.session_state.USERS[username]["role"]
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Mot de passe incorrect.")
        else:
            st.error("Identifiant incorrect.")

    if st.button("🆕 Créer un compte"):
        st.session_state.show_registration = True
        st.rerun()

# --- Chargement du CSV ---
@st.cache_data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), "dataframe_final.csv")
    try:
        return pd.read_csv(csv_path)
    except:
        st.error("Fichier 'dataframe_final.csv' introuvable.")
        return pd.DataFrame()

# --- Fonction ADMIN ---
def admin_dashboard():
    st.markdown("<h1 style='color:red;'>🎛️ Tableau de bord Administrateur</h1>", unsafe_allow_html=True)

    df = load_data()
    st.markdown("<h3 style='color:white;'>📋 Aperçu des films</h3>", unsafe_allow_html=True)
    st.dataframe(df)

    st.markdown("<h3 style='color:white;'>📊 Statistiques</h3>", unsafe_allow_html=True)
    st.write("Nombre total de films :", df.shape[0])

    if "genre" in df.columns:
        st.write("Genres disponibles :", df["genre"].nunique())
        st.bar_chart(df["genre"].value_counts())

    if "note" in df.columns:
        st.write("Distribution des notes :")
        st.bar_chart(df["note"].value_counts().sort_index())

    if st.button("Se déconnecter"):
        st.session_state.authenticated = False
        st.rerun()

# --- Fonction UTILISATEUR ---
def main_app():
    st.markdown("<h1 style='font-size:34px;'>WildFlix, l'univers du cinéma réuni grâce à la Data !</h1>", unsafe_allow_html=True)

    img_path = os.path.join(os.path.dirname(__file__), "intro1test.png")
    if os.path.exists(img_path):
        with open(img_path, "rb") as file:
            data_url = base64.b64encode(file.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{data_url}">', unsafe_allow_html=True)
    else:
        st.error("Le fichier 'intro1test.png' est introuvable.")

    audio_path = os.path.join(os.path.dirname(__file__), "intro.mp3")
    if os.path.exists(audio_path):
        audio_url = f"data:audio/mp3;base64,{base64.b64encode(open(audio_path, 'rb').read()).decode()}"
        st.markdown(f"<audio autoplay><source src='{audio_url}' type='audio/mp3'></audio>", unsafe_allow_html=True)
    else:
        st.error("Le fichier 'intro.mp3' est introuvable.")

    data = load_data()

    st.markdown("<p style='font-size:30px; color:white; font-weight:bold;'>🔎 RECHERCHER UN FILM PAR TITRE</p>", unsafe_allow_html=True)
    titres_films = data['titre'].dropna().sort_values().unique().tolist()
    search = st.selectbox("", titres_films, key="search_title")

    if search:
        results = data[data["titre"].str.contains(search, case=False, na=False)]
    else:
        results = pd.DataFrame()

    if not results.empty:
        for _, row in results.iterrows():
            st.markdown(f"### 🎬 {row['titre']}")
            if pd.notna(row.get('affiche')) and str(row['affiche']).startswith("http"):
                st.image(row['affiche'], use_container_width=True)
            if 'synopsis' in row and pd.notna(row['synopsis']):
                st.markdown("### Synopsis :")
                st.markdown(f"<p style='color:white; font-size:22px; text-align:justify;'>{row['synopsis']}</p>", unsafe_allow_html=True)
            else:
                st.markdown("### Synopsis :")
                st.markdown("<p style='color:gray; font-style:italic;text-align: center;'>Aucun synopsis disponible.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    # TRADUCTEUR
    # Définition des langues avec leurs noms et URL d'images de drapeaux
    langues = {
        "Français": {"code": "fr", "flag": "https://upload.wikimedia.org/wikipedia/en/c/c3/Flag_of_France.svg"},
        "Anglais": {"code": "en", "flag": "https://upload.wikimedia.org/wikipedia/en/a/ae/Flag_of_the_United_Kingdom.svg"},
        "Espagnol": {"code": "es", "flag": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Flag_of_Spain.svg"},
        "Allemand": {"code": "de", "flag": "https://upload.wikimedia.org/wikipedia/en/b/ba/Flag_of_Germany.svg"},
        "Italien": {"code": "it", "flag": "https://upload.wikimedia.org/wikipedia/en/0/03/Flag_of_Italy.svg"}
        }
    # Ajout des boutons de traduction
    st.markdown("###### 🌍Quelle est votre langue préférée pour lire le Synopsis?🌍") # Titre
    col_vide1, col_centrale, col_vide2 = st.columns([0.3, 0.4, 0.3])  # Mise en page centrale
    with col_centrale:
        for langue, data in langues.items():
            col1, col2 = st.columns([0.2, 0.8])  # Rapprochement drapeau-bouton
            with col1:
                st.image(data["flag"], width=50)  # Drapeau à gauche
            with col2:
                if st.button(langue, key=langue):  # Bouton juste à côté
                    synopsis_traduit = traduire_texte(synopsis_original, data["code"])
                    st.markdown(f"### 📖 Synopsis traduit en {langue}:")
                    st.markdown(f"<p style='color:white; font-size:22px; text-align:justify;'>{synopsis_traduit}</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    try:
        df_encoded = pd.read_csv("version_globale_encodee.csv")
        model = NearestNeighbors(n_neighbors=6).fit(df_encoded.drop("titre", axis=1).values)

        def recommander_films(titre):#On vérifie si titre du film existe dans la colonne titre,
            if titre not in df_encoded['titre'].values: # si non on retourne une liste vide
                return []
            idx = df_encoded.index[df_encoded['titre'] == titre][0] #🔹 On récupère l’index de la ligne correspondant au film recherché.
            _, indices = model.kneighbors(df_encoded.drop("titre", axis=1).iloc[idx].values.reshape(1, -1)) #  on retire la colonne titre, on prend la ligne du film recherché avec .iloc, passage du modèle en format 2D


            return df_encoded.loc[indices[0][1:], 'titre'].tolist() # on retourne les titres des autres films similaires

        recommandations = recommander_films(search)  # On appelle la fonction avec le film choisi (search) pour obtenir la liste des recommandations.
        if recommandations:
            st.markdown("<h2 style='color:white;'>🎯 Films recommandés :</h2>", unsafe_allow_html=True)
            cols = st.columns(5) # On crée 5 colonnes côte à côte dans Streamlit pour un affichage visuel.
            for i, titre in enumerate(recommandations[:5]): # 🔹 Pour les 5 premières recommandations, on affiche leur titre dans une des colonnes créées.
                with cols[i]:
                    st.markdown(f"**{titre}**")
                    try:
                        poster = r.get(f"http://www.omdbapi.com/?t={titre}&apikey=548c959e").json().get("Poster") #🔹 On fait une requête à l’API OMDB pour récupérer l’affiche du film (basée sur son titre).
                        if poster and poster.startswith("http"):
                            st.image(poster)
                        else:
                            st.markdown("*Pas d'affiche*")
                    except:
                        st.markdown("*Erreur*")
    except:                                              #🔹 Un try/except global autour de tout ça permet d’éviter que l’appli plante si une erreur survient.
        st.warning("Erreur lors des recommandations.")

    if st.button("Se déconnecter"):
        st.session_state.authenticated = False
        st.rerun()

# --- ROUTAGE PRINCIPAL ---
if st.session_state.authenticated:
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        main_app()
else:
    login()




### Mettre la vidéo en ligne
# Allez sur le site Streamlit Sharing et cliquez sur "Sign in with GitHub" pour vous inscrire.
# Déployez votre application : Une fois connecté, cliquez sur "New app", 
# Sélectionnez votre dépôt GitHub, la branche et le chemin du fichier, puis cliquez sur "Deploy".