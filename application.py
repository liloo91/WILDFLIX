import streamlit as st
import pandas as pd
import requests as r
import json
import base64
import os
from sklearn.neighbors import NearestNeighbors
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration de la page ---
st.set_page_config(page_title="WildFlix", layout="wide")

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
    st.markdown("<h1 style='font-size:100px;color:red;'>WildFlix</h1>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:30px;color:white;'>Connexion requise pour accéder à la plateforme</h1>", unsafe_allow_html=True)

    username = st.text_input("Nom d'utilisateur", key="login_username")
    password = st.text_input("Mot de passe", type="password", key="login_password")

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

    df = pd.read_csv("dataframe_final.csv")

    # Menu latéral avec les 9 noms
    with st.sidebar:
        choix = st.radio("Choisissez un graphique :", [
            "Répartition des films par genre",
            "Répartition des films par réalisateur",
            "Répartition des films par acteur",
            "Evolution du catalogue",
            "Répartition des films par catégorie de Budget",
            "Répartition des films par catégorie de Durée",
            "Répartition des films par catégorie de Like",
            "Nombre d'utilisateur inscrit",
            "Nombre de films"
        ])
        # Fonction d'affichage (panneau latéral)
        def afficher_graphique(nom):
            x = np.linspace(0, 10, 100)
            fig, ax = plt.subplots()

            if nom == "Répartition des films par genre":
                # --- GRAPHIQUE KPI 3 : Nombre de films par genre ---
                st.markdown("### 🎨 Répartition des films par genre")

                # Partie 1 : concaténation des genres
                concatGenre = pd.concat([df["genre_1"], df["genre_2"], df["genre_3"]], axis=0)

                # Partie 2 : comptage des genres
                genre_counts = concatGenre.value_counts()

                # Partie 3 : création du graphique
                fig = go.Figure(go.Bar(
                x=genre_counts.values,
                y=genre_counts.index,
                orientation='h',
                text=genre_counts.values,
                textposition='outside',
                textfont=dict(size=16) # Taille des chiffres
                ))

                fig.update_layout(
                height=600,
                margin=dict(l=40, r=40, t=40, b=40),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                )

                st.plotly_chart(fig)

            elif nom == "Répartition des films par acteur":
        # --- GRAPHIQUE KPI 4 : Nombre de films par acteur ---
                st.markdown("### 🎨 Classement des 10 acteurs les plus présents")

                # Partie 1 : concaténation des colonnes acteurs
                concatActeur = pd.concat([df["acteur1"], df["acteur2"], df["acteur3"], df["acteur4"]], axis=0)

                # Partie 2 : comptage des acteurs
                concatActeur.value_counts()

                # Partie 3 : création du graphique
                # Nombre de résultats à afficher
                x_limit_acteur = 10

                # Comptage des acteurs et sélection des x premiers
                valeurs_Acteurs = concatActeur.value_counts().head(x_limit_acteur)

                fig = go.Figure(go.Bar(
                x=valeurs_Acteurs.values,
                y=valeurs_Acteurs.index,
                orientation='h',
                text=valeurs_Acteurs.values,
                textposition='outside',
                textfont=dict(size=16) # Taille des chiffres
                ))

                fig.update_layout(
                height=600,
                margin=dict(l=40, r=40, t=40, b=40),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                )

                st.plotly_chart(fig)

            #################################
            elif nom == "Répartition des films par réalisateur":
                # --- GRAPHIQUE KPI 3 : Nombre de films par réalisateur ---
                st.markdown("### 🎨 Répartition des films par réalisateur")

                # concaténation des réalisateurs
                concatRealisateur = pd.concat([df["nom_du_realisateur_1"],df["nom_du_realisateur_2"],df["nom_du_realisateur_3"]], axis=0)

                # comptage des genres
                concatRealisateur.value_counts()

                # Nombre de résultats à afficher
                x_limit_realisateur = 10

                # Comptage des realisateurs et sélection des x premiers
                valeurs_realisateur = concatRealisateur.value_counts().head(x_limit_realisateur)

                # création du graphique
                fig = go.Figure(go.Bar(
                x=valeurs_realisateur.values,
                y=valeurs_realisateur.index,
                orientation='h',
                text=valeurs_realisateur.values,
                textposition='outside',
                textfont=dict(size=16) # Taille des chiffres
                ))

                fig.update_layout(
                height=600,
                margin=dict(l=40, r=40, t=40, b=40),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                )

                st.plotly_chart(fig)


            ################################
            # --- GRAPHIQUE KPI 6 : Evolution du catalogue
            elif nom == "Evolution du catalogue":
                st.markdown("### 🎨 Evolution du catalogue")

                # Comptage des realisateurs et sélection des x premiers
                valeurs_date_publication = df["date_publication_film"].value_counts().sort_index()

                # création du graphique
                fig = go.Figure(go.Bar(
                x=valeurs_date_publication.index,
                y=valeurs_date_publication.values,
                orientation='v',
                text=valeurs_date_publication.values,
                textposition='outside',
                textfont=dict(size=16) # Taille des chiffres
                ))

                fig.update_layout(
                height=600,
                margin=dict(l=40, r=40, t=40, b=40),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                )

                st.plotly_chart(fig)


            #################################
            # --- GRAPHIQUE KPI 7 : Part des films par catégorie de Like
            elif nom == "Répartition des films par catégorie de Like":
                st.markdown("### 🎨 Répartition des films par catégorie de Like")

                if "categorie_like" in df.columns:
                    valeurs_like = df["categorie_like"].value_counts()
                    labels = valeurs_like.index
                    sizes = valeurs_like.values
                    colors = plt.get_cmap("Set3").colors  # Palette douce et lisible

                    # Création du graphique
                    fig, ax = plt.subplots(figsize=(7, 7),facecolor='black')
                    wedges, texts, autotexts = ax.pie(
                        sizes,
                        labels=None,  # on met les labels dans la légende pour plus de clarté
                        colors=colors,
                        autopct=lambda pct: f'{pct:.1f}%' if pct > 2 else '',
                        startangle=140,
                        textprops={'color': 'black', 'fontsize': 12}
                    )
                    ax.axis('equal')

                    # Ajout d'un titre au centre du camembert
                    ax.set_title("Catégories de Like des films", color='black', fontsize=16)

                    # Légende sur le côté droit
                    ax.legend(wedges, labels, title="Likes", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

                    # Affichage dans Streamlit
                    st.pyplot(fig)
                else:
                    st.warning("La colonne 'categorie_like' est absente du fichier.")


            ################################
            # --- GRAPHIQUE KPI 8 : Part des films par catégorie de Budget
            elif nom=="Répartition des films par catégorie de Budget":
                st.markdown("### 🎨 Répartition des films par catégorie de Budget")

                if "categorie_budget" in df.columns:
                    valeurs_budget = df["categorie_budget"].value_counts()
                    labels = valeurs_budget.index
                    sizes = valeurs_budget.values
                    colors = plt.get_cmap("Set3").colors  # Palette douce et lisible

                    # Création du graphique
                    fig, ax = plt.subplots(figsize=(7, 7),facecolor='black')
                    wedges, texts, autotexts = ax.pie(
                        sizes,
                        labels=None,  # on met les labels dans la légende pour plus de clarté
                        colors=colors,
                        autopct=lambda pct: f'{pct:.1f}%' if pct > 2 else '',
                        startangle=140,
                        textprops={'color': 'black', 'fontsize': 12}
                    )
                    ax.axis('equal')

                    # Ajout d'un titre au centre du camembert
                    ax.set_title("Catégories de Budget des films", color='black', fontsize=16)

                    # Légende sur le côté droit
                    ax.legend(wedges, labels, title="Budget", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

                    # Affichage dans Streamlit
                    st.pyplot(fig)
                else:
                    st.warning("La colonne 'categorie_budget' est absente du fichier.")


                ##################################

                    # --- GRAPHIQUE KPI 9 : Part des films par catégorie de durée de film
            elif nom == "Répartition des films par catégorie de Durée":
                st.markdown("### 🎨 Répartition des films par catégorie de Durée")

                if "categorie_durée" in df.columns:
                    valeurs_duree = df["categorie_durée"].value_counts()
                    labels = valeurs_duree.index
                    sizes = valeurs_duree.values
                    colors = plt.get_cmap("Set3").colors  # Palette douce et lisible

                    # Création du graphique
                    fig, ax = plt.subplots(figsize=(7, 7),facecolor='black')
                    wedges, texts, autotexts = ax.pie(
                        sizes,
                        labels=None,  # on met les labels dans la légende pour plus de clarté
                        colors=colors,
                        autopct=lambda pct: f'{pct:.1f}%' if pct > 2 else '',
                        startangle=140,
                        textprops={'color': 'black', 'fontsize': 12}
                    )
                    ax.axis('equal')

                    # Ajout d'un titre au centre du camembert
                    ax.set_title("Catégories de Durée des Films", color='black', fontsize=16)

                    # Légende sur le côté droit
                    ax.legend(wedges, labels, title="Durée", loc="center left", bbox_to_anchor=(1, 0.5), fontsize=12)

                    # Affichage dans Streamlit
                    st.pyplot(fig)
                else:
                    st.warning("La colonne 'categorie_durée' est absente du fichier.")


                # Graphique KPI 1 : Nombre d’utilisateurs inscrits
            elif nom == "Nombre d'utilisateur inscrit":
                st.markdown("### 🎨 Nombre d'utilisateur inscrit")
                df_user = pd.read_json("users1.json")
                df_user = df_user.transpose()
                nombre_lignes = len(df_user)
                nombre_utilisateur_site = nombre_lignes - 1
                st.markdown(f"""
                <div style='background-color: #222;
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    font-size: 50px;
                    color: white;
                    font-weight: bold;
                    box-shadow: 0px 0px 10px rgba(255,255,255,0.2);
                '>
                👤 {nombre_utilisateur_site} utilisateurs
                </div>
                """, unsafe_allow_html=True)

                # Graphique KPI 2 : Nombre de films
            elif nom == "Nombre de films":
                st.markdown(f"""
                <div style='background-color: #222;
                    padding: 30px;
                    border-radius: 15px;
                    text-align: center;
                    font-size: 50px;
                    color: white;
                    font-weight: bold;
                    box-shadow: 0px 0px 10px rgba(255,255,255,0.2);
                '>
                👤 {df.shape[0]} films
                </div>
                """, unsafe_allow_html=True)

    afficher_graphique(choix)

    if st.button("Se déconnecter"):
        st.session_state.authenticated = False
        st.rerun()

# --- Fonction UTILISATEUR ---
def main_app():
    st.markdown("<h1 style='font-size:34px;'>WildFlix, l'univers du cinéma réuni grâce à la Data !</h1>", unsafe_allow_html=True)

    img_path = os.path.join(os.path.dirname(__file__), "intro1.png")
    if os.path.exists(img_path):
        with open(img_path, "rb") as file:
            data_url = base64.b64encode(file.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{data_url}">', unsafe_allow_html=True)
    else:
        st.error("Le fichier 'intro1.png' est introuvable.")

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
            if 'synopsis' in row and pd.notna(row['synopsis']):
                st.markdown("<p style='color:white;'>SYNOPSIS : </p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:white; text-align:justify;'>{row['synopsis']}</p>", unsafe_allow_html=True)
            if pd.notna(row.get('affiche')) and str(row['affiche']).startswith("http"):
                st.image(row['affiche'], use_container_width=True)

    try:
        df_encoded = pd.read_csv("version_globale_encodee.csv")
        model = NearestNeighbors(n_neighbors=6).fit(df_encoded.drop("titre", axis=1).values)

        def recommander_films(titre):
            if titre not in df_encoded['titre'].values:
                return []
            idx = df_encoded.index[df_encoded['titre'] == titre][0]
            _, indices = model.kneighbors(df_encoded.drop("titre", axis=1).iloc[idx].values.reshape(1, -1))
            return df_encoded.loc[indices[0][1:], 'titre'].tolist()

        recommandations = recommander_films(search)
        if recommandations:
            st.markdown("<h2 style='color:white;'>🎯 Films recommandés :</h2>", unsafe_allow_html=True)
            cols = st.columns(5)
            for i, titre in enumerate(recommandations[:5]):
                with cols[i]:
                    st.markdown(f"**{titre}**")
                    try:
                        poster = r.get(f"http://www.omdbapi.com/?t={titre}&apikey=548c959e").json().get("Poster")
                        if poster and poster.startswith("http"):
                            st.image(poster)
                        else:
                            st.markdown("*Pas d'affiche*")
                    except:
                        st.markdown("*Erreur*")
    except:
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