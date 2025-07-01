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
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
from streamlit_option_menu import option_menu


######################################### CONFIGURATION DE LA PAGE ###############################################
# --- Configuration de la page ---
st.set_page_config(page_title="WildFlix", layout="wide") # Pour définir le titre de l’onglet dans le navigateur (en haut de la fenêtre). Le layout permet d'étendre l'application sur toute la largeur.

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



################################### TRADUCTION #######################################################

# --- LANGUES ---
drapeau = {
        "Français": {"fr": "https://upload.wikimedia.org/wikipedia/en/c/c3/Flag_of_France.svg"},
        "Anglais": {"en": "https://upload.wikimedia.org/wikipedia/en/a/ae/Flag_of_the_United_Kingdom.svg"}
        }

TRANSLATIONS = {
    "Francais": {
        "login_title": "Connexion à la plateforme",
        "username": "Nom d'utilisateur",
        "password": "Mot de passe",
        "connect": "🔑 Se connecter",
        "create_account": "🆕 Créer un compte",
        "logout": "Se déconnecter",
        "search_title": "🔎 RECHERCHER UN FILM PAR TITRE",
        "recommendation_method": "Méthode de recommandation :",
        "recommended_for": "🎯 Films recommandés pour :",
        "synopsis": "SYNOPSIS :",
        "no_recommendation": "Aucune recommandation trouvée pour ce film.",
        "register_title": "Création de Compte",
        "email": "Adresse Mail",
        "register_button": "✅ Enregistrer",
        "back_to_login": "↩️ Retour Connexion",
        "username_taken": "Ce nom d'utilisateur est déjà pris.",
        "account_created": "Compte créé avec succès ! Vous pouvez maintenant vous connecter.",
        "login_success": "Connexion réussie !",
        "wrong_password": "Mot de passe incorrect.",
        "wrong_id": "Identifiant incorrect.",
        "titre_page_utilisateur": "WildFlix, l'univers du cinéma réuni grâce à la donnée !"
    },
    "Anglais": {
        "login_title": "Login to platform",
        "username": "Username",
        "password": "Password",
        "connect": "🔑 Login",
        "create_account": "🆕 Create an account",
        "logout": "Logout",
        "search_title": "🔎 SEARCH FOR A MOVIE BY TITLE",
        "recommendation_method": "Recommendation method:",
        "recommended_for": "🎯 Recommended movies for:",
        "synopsis": "SYNOPSIS:",
        "no_recommendation": "No recommendations found for this movie.",
        "register_title": "Create Account",
        "email": "Email address",
        "register_button": "✅ Register",
        "back_to_login": "↩️ Back to Login",
        "username_taken": "This username is already taken.",
        "account_created": "Account successfully created! You can now log in.",
        "login_success": "Login successful!",
        "wrong_password": "Incorrect password.",
        "wrong_id": "Incorrect username.",
        "titre_page_utilisateur": "WildFlix, where is bryan"
    }
}

# --- SESSION ---
if "lang" not in st.session_state:
    st.session_state.lang = "Francais"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "show_registration" not in st.session_state:
    st.session_state.show_registration = False

# --- TRADUCTION ---
def _(key):
    return TRANSLATIONS.get(st.session_state.lang, {}).get(key, key)

# --- LANG SELECT (user only) ---
if "role" in st.session_state and st.session_state.role != "admin":
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("Selectionner votre langue", )
        st.selectbox("Traduction", ["Francais", "Anglais"], index=["Francais", "Anglais"].index(st.session_state.lang), key="lang")

# --- USER FILE ---
USER_FILE = "users1.json"

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

if "USERS" not in st.session_state:
    st.session_state.USERS = load_users()

# --- INSCRIPTION ---
if st.session_state.show_registration:
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("<h1 style='font-size:100px;color:red;'>WildFlix</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size:30px;color:white;'>{_('register_title')}</h1>", unsafe_allow_html=True)

        new_username = st.text_input(_("username"), key="register_username")
        new_password = st.text_input(_("password"), type="password", key="register_password")
        new_mail = st.text_input(_("email"), key="register_email")

        if st.button(_("register_button")):
            if new_username in st.session_state.USERS:
                st.error(_("username_taken"))
            else:
                st.session_state.USERS[new_username] = {"password": new_password, "role": "user"}
                save_users(st.session_state.USERS)
                st.success(_("account_created"))

        if st.button(_("back_to_login")):
            st.session_state.show_registration = False
            st.rerun()

# --- CONNEXION ---
def login():
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("<h1 style='font-size:100px;color:red;'>WildFlix</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size:30px;color:white;'>{_('login_title')}</h1>", unsafe_allow_html=True)

        username = st.text_input(_("username"), key="login_username")
        password = st.text_input(_("password"), type="password", key="login_password")

        if st.button(_("connect")):
            if username in st.session_state.USERS:
                stored_password = st.session_state.USERS[username]["password"]
                if password == stored_password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = st.session_state.USERS[username]["role"]
                    st.success(_("login_success"))
                    st.rerun()
                else:
                    st.error(_("wrong_password"))
            else:
                st.error(_("wrong_id"))

        if st.button(_("create_account")):
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
    st.markdown(f"<h1 style='color:red;'>📊 TABLEAU DE BORD - WILDFLIX</h1>", unsafe_allow_html=True)

    df = pd.read_csv("dataframe_final.csv")

    # Menu latéral avec les 9 noms
    with st.sidebar:
        st.markdown("### 📊 Graphique interactif")
        variable_x = st.selectbox("Axe X", df.columns, index=None, placeholder="Choisissez une variable X")
        variable_y = st.selectbox("Axe Y", df.columns, index=None, placeholder="Choisissez une variable Y")
        couleur = st.selectbox("Catégoriser par (optionnel)", ["Aucune"] + list(df.columns), index=None, placeholder="Choisissez une catégorie")
        type_graphique = st.selectbox("Type de graphique :", ["Nuage de points", "Barres", "Ligne"], index=None, placeholder="Choisissez un graphique")

    # Affichage conditionnel
    if not variable_x or not variable_y or not type_graphique:
        st.markdown("#### ⚠️ Renseigner des valeurs pour afficher votre graphique")
        st.markdown("")
        st.markdown("")
    else:
        if type_graphique == "Nuage de points":
            fig = px.scatter(df, x=variable_x, y=variable_y, color=None if couleur == "Aucune" else couleur)
        elif type_graphique == "Barres":
            fig = px.bar(df, x=variable_x, y=variable_y, color=None if couleur == "Aucune" else couleur)
        elif type_graphique == "Ligne":
            fig = px.line(df, x=variable_x, y=variable_y, color=None if couleur == "Aucune" else couleur)

        # Mise en forme
        fig.update_layout(
            title=f"{variable_y} en fonction de {variable_x}",
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=14)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    
    with st.sidebar:
        st.markdown("### 📊 Graphique Classique")
        choix = st.selectbox("", [
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
    st.markdown("### 📊 Graphique interactif")


    afficher_graphique(choix)

    with st.sidebar:
        df_user_show=pd.read_json("users1.json").transpose()
        st.markdown("")
        st.markdown("### 🔒 Base de donnée utilisateurs")
        st.markdown("")
        df_user_show = df_user_show.reset_index().rename(columns={"index": "nom_user"})
        df_user_show = df_user_show[["nom_user", "role"]]
        st.dataframe(df_user_show)

    if st.button("Se déconnecter"):
        st.session_state.authenticated = False
        st.rerun()

######

#######
def main_app():
    st.markdown(f"<h1 style='font-size:34px;'>WildFlix, l'univers du cinéma réuni grâce à la donnée !</h1>", unsafe_allow_html=True)
    st.markdown("")

    img_path = os.path.join(os.path.dirname(__file__), "intro1.png")
    if os.path.exists(img_path):
        with open(img_path, "rb") as file:
            data_url = base64.b64encode(file.read()).decode()

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
    film_choisi = st.selectbox("", titres_films, key="search_title")

    results = data[data["titre"]==film_choisi] 

    if st.button("traduction du synopsis"):
        modelTraductionFrancaisAnglais = pipeline("translation", model="Helsinki-NLP/opus-mt-en-fr")
        traduction_clique = True
    else:
        traduction_clique = False

    for _, row in results.iterrows(): 
        if traduction_clique:
            synopsis = modelTraductionFrancaisAnglais(row["synopsis"])[0]["translation_text"]
        else:
            synopsis = row['synopsis']
        st.markdown(f"<p style='color:white; text-align:left;font-weight:bold;font-size:30px ;'>🎬 TITRE :  {row['titre']} </p>", unsafe_allow_html=True)
        st.markdown("<p style='color:white; font-size:30px;text-align:left ;font-weight:bold;'>📖 SYNOPSIS :</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:white; text-align:justify;'>{synopsis}</p>", unsafe_allow_html=True)
        a,b,c = st.columns([1,1,1])
        with b:
            st.image(row['affiche'],use_container_width="always")
        with c:
            st.markdown(f"<p style='color:white; text-align:justify;'> Nom du réalisateur : {row["nom_du_realisateur_1"]}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:white; text-align:justify;'> Genre(s) : {row["genre_1"], row["genre_2"], row["genre_3"]}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:white; text-align:justify;'> Acteur(s) : {row["acteur1"], row["acteur2"], row["acteur3"]}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:white; text-align:justify;'> Date de sortie : {row["année_de_sortie"]}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:white; text-align:justify;'> Classification : {row["classification"]}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:white; text-align:justify;'> Note WildFlix : {int(row['note_wildflix'])}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:white; text-align:justify;'> Durée : {int(row['durée'])} min</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:white; text-align:justify;'> Type : {row["Type"]}</p>", unsafe_allow_html=True)



        # RECOMMANDATION DU FILM VIA NearestNeighbors/
        # Préparation des données (en dehors de la fonction si possible pour optimiser)

        # Chargement des données encodées
        df_encoded = pd.read_csv("version_globale_encodee.csv")
        X = df_encoded.drop("titre", axis=1).values
        titles = df_encoded["titre"].tolist()

        # Chargement des données originales pour l'affichage
        data = pd.read_csv("dataframe_final.csv")

        # Calcul de la similarité cosinus
        similarite_cosine = cosine_similarity(X)

        # Création du modèle KNN
        modele_knn = NearestNeighbors(n_neighbors=6)
        modele_knn.fit(X)

        # Interface utilisateur
        st.markdown("<p style='color:white; font-size:20px;text-align:left ;font-weight:bold;'>📖 Choix des recommandations :</p>", unsafe_allow_html=True)
        choix_algo = option_menu(
        menu_title=None,                # pas de titre
        options=["Les films les plus proches", "Les films qui ressemblent le plus"],
        icons=["film", "star"],         # icônes FontAwesome
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={                        # tout en blanc sur fond sombre
            "container": {"background-color": "#111"},
            "nav-link": {"font-size": "16px", "color": "white"},
            "nav-link-selected": {"background-color": "#005f73", "color": "white"}
        }
        )

        st.write("Tu as choisi :", choix_algo)

        # Fonction de recommandation
        def recommander_films(titre, methode="Les films les plus proches"):
            if titre not in titles:
                return []

            idx = titles.index(titre)

            if methode == "Les films les plus proches":
                _, indices = modele_knn.kneighbors([X[idx]])
                voisins = indices[0][1:]  # On exclut le film lui-même
                return voisins.tolist()
            else:
                scores = list(enumerate(similarite_cosine[idx]))
                scores = sorted(scores, key=lambda x: x[1], reverse=True)
                voisins = [i for i, _ in scores[1:6]]  # On exclut le film lui-même
                return voisins

        # Obtenir les recommandations
        recommandations = recommander_films(film_choisi, methode=choix_algo)

        # Affichage des recommandations
        if len(recommandations) > 0:
            st.markdown(f"<h2 style='color:white;'>🎯 Films recommandés pour : <em>{film_choisi}</em></h2>", unsafe_allow_html=True)
            cols = st.columns(5)

            for i, idx in enumerate(recommandations):
                if idx < len(data):  # Vérifie que l'index existe dans le DataFrame
                    with cols[i % 5]:  # Organiser les films sur une ligne
                        film = data.iloc[idx]
                        st.markdown(f"### 🎬 {film['titre']}")
                        st.image(film['affiche'], use_container_width=True)
                        st.markdown("<p style='color:white;'>SYNOPSIS :</p>", unsafe_allow_html=True)
                        if traduction_clique:
                            synopsis = modelTraductionFrancaisAnglais(film["synopsis"])[0]["translation_text"]
                            st.text("")
                            st.text("")
                        else:
                            synopsis = row['synopsis']
                        st.markdown(f"<p style='color:white; text-align:justify;'>{synopsis}</p>", unsafe_allow_html=True)
                        st.text("")
                        st.text("")
        else:
            st.warning("Aucune recommandation trouvée pour ce film.")


        col1, col2, col3, col4,col5 = st.columns(5)
        with col1:
            if st.button("Se déconnecter"):
                st.text("")
                st.text("")
                st.session_state.authenticated = False
                st.rerun()


if st.session_state.authenticated:
    if st.session_state.role == "admin":
        admin_dashboard()
    else:
        main_app()
else:
    login()

# --- ROUTAGE PRINCIPAL ---
st.text(" ")
st.text(" ")

