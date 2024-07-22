import streamlit as st
import pandas as pd
import base64
from datetime import datetime, timedelta, date
import pymongo
import hmac
from streamlit_date_picker import date_range_picker, date_picker, PickerType
#from bson import ObjectId

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()

sex_mapping = {'male': 0, 'female': 1}
answers = {}

st.markdown(
        """<style>
        div[class*="stSlider"] > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 20px;
                }
        /* Style for radio buttons */
    div[class*="stRadio"] > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 20px;
    }
        </style>
                """, unsafe_allow_html=True)


st.markdown(
    """
    <style>
    .centered_button {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

###
# Consentement

st.subheader("Je reconnais que :")

participation = st.radio(
        "Je participe volontairement à cette recherche *",
        ('Oui', 'Non'),
        index=None
    )

retrait = st.radio(
        "Je peux cesser ma participation à tout moment sans avoir à donner d'explications *",
        ('Oui', 'Non'),
        index=None
    )

confidentialite = st.radio(
        "Toutes les informations que je fournirai seront confidentielles et mon identité ne sera jamais divulguée *",
        ('Oui', 'Non'),
        index=None
    )

utilisation_donnees = st.radio(
        "J'autorise la conversation et l'utilisation de ces données confidentielles dans le cadre de la recherche scientifique en psychologie *",
        ('Oui', 'Non'),
        index=None
    )


###
# situation de Handicap:
st.header("Situation de handicap")

# Nature du trouble moteur
st.subheader("Nature du trouble moteur :")
paralysie = st.checkbox("Paralysie")
sclerose = st.checkbox("Sclérose en plaques")
dystrophie = st.checkbox("Dystrophie musculaire")
amputation = st.checkbox("Amputation")
atrophie = st.checkbox("Atrophie musculaire spinale")
autre = st.checkbox("Autre (préciser) :", key="autre_assitance")
autre_text = st.text_input("Préciser si autre :", key="autre_assistance_text")

membre_superieur_gauche = st.checkbox("Membre supérieur Gauche")
membre_superieur_droit = st.checkbox("Membre supérieur Droit")
membre_inferieur_gauche = st.checkbox("Membre inférieur Gauche")
membre_inferieur_droit = st.checkbox("Membre inférieur Droit")

# Temps avec le trouble moteur
#st.subheader("Depuis combien de temps avez-vous ce trouble moteur ?")
#temps_trouble = st.radio(
#    "",
#    ('Moins de 1 an', '1 à 3 ans', '3 à 5 ans', 'Plus de 5 ans'),
#    index=None
#)

st.subheader("Depuis combien de temps avez-vous ce trouble moteur ? (en années)")
temps_trouble = st.number_input(
    "",
    min_value=0,
    max_value=None,
    value=0,
    step=1
)

# Nature du trouble moteur
st.subheader("Le trouble moteur est-il :")
nature_trouble = st.radio(
    "",
    ('Congénital (depuis la naissance)', 'Acquis (après un accident, une maladie, etc.)'),
    index=None
)

# Douleurs associées au trouble moteur
st.subheader("Avez-vous des douleurs associées à votre trouble moteur ?")
douleurs = st.radio(
    "",
    ('Oui, constamment', 'Oui, fréquemment', 'Oui, de temps en temps', 'Non'),
    index=None
)

# Aides techniques
st.subheader("Utilisez-vous des aides techniques autres que la planche de transfert ? (ex. : fauteuil roulant, canne, déambulateur)")
aides_techniques = st.radio(
    "",
    ('Oui', 'Non'),
    index=None
)

if aides_techniques == 'Oui':
    st.subheader("Si oui, lesquelles ?")
    fauteuil_manuel = st.checkbox("Fauteuil roulant manuel")
    fauteuil_electrique = st.checkbox("Fauteuil roulant électrique")
    canne = st.checkbox("Canne")
    deambulateur = st.checkbox("Déambulateur")
    orthese = st.checkbox("Orthèse")
    autre_aide = st.checkbox("Autre (préciser) :",key="autre_aide")
    autre_aide_text = st.text_input("Préciser si autre :", key="autre_aide_text")

###
# Collect:
situation_data = {
    "nature_trouble": {
        "paralysie": paralysie,
        "sclerose": sclerose,
        "dystrophie": dystrophie,
        "amputation": amputation,
        "atrophie": atrophie,
        "autre": autre,
        "autre_text": autre_text
    },
    "Membre": {"Membre supérieur Gauche": membre_superieur_gauche,
               "Membre supérieur Gauche": membre_superieur_droit,
               "Membre supérieur Gauche": membre_inferieur_gauche,
               "Membre supérieur Gauche": membre_inferieur_gauche
    },
    "temps_trouble": temps_trouble,
    "nature_trouble_type": nature_trouble,
    "douleurs": douleurs,
    "aides_techniques": {
        "utilise_aides": aides_techniques,
        "fauteuil_manuel": fauteuil_manuel if aides_techniques == 'Oui' else None,
        "fauteuil_electrique": fauteuil_electrique if aides_techniques == 'Oui' else None,
        "canne": canne if aides_techniques == 'Oui' else None,
        "deambulateur": deambulateur if aides_techniques == 'Oui' else None,
        "orthese": orthese if aides_techniques == 'Oui' else None,
        "autre_aide": autre_aide if aides_techniques == 'Oui' else None,
        "autre_aide_text": autre_aide_text if aides_techniques == 'Oui' else None
    }
}

# 

st.header("Vie quotidienne et autonomie")

# Niveau d'autonomie
st.subheader("Niveau d'autonomie dans les activités quotidiennes (manger, s'habiller, se laver, etc.) :")
autonomie = st.radio(
    "",
    ('Totalement autonome', 'Partiellement autonome (besoin d\'aide pour certaines activités)', 
     'Dépendant (besoin d\'aide pour la plupart des activités)', 'Totalement dépendant'),
    index=None
)

# Assistance pour déplacements
st.subheader("Avez-vous besoin d'une assistance pour vos déplacements ?")
assistance_deplacement = st.radio(
    "",
    ('Oui', 'Non'),
    index=None,
    key = "assitance"
)

# Si oui, quel type d'assistance ?
if assistance_deplacement == 'Oui':
    st.subheader("Si oui, quel type d'assistance ?")
    assistance_humaine = st.checkbox("Assistance humaine (aidant familial, assistant personnel)")
    aide_technique = st.checkbox("Aide technique (fauteuil roulant, déambulateur)")
    autre_assistance = st.checkbox("Autre (préciser) :")
    autre_assistance_text = st.text_input("Préciser si autre :")

# Travail
st.subheader("Travaillez-vous actuellement ?")
travail = st.radio(
    "",
    ('Oui, à temps plein', 'Oui, à temps partiel', 'Non, mais je cherche du travail', 'Non, je ne cherche pas de travail'),
    index=None,
    key="travail"
)

# Collect:

vie_data = {
    "autonomie": autonomie,
    "assistance_deplacement": assistance_deplacement,
    "assistance_details": {
        "assistance_humaine": assistance_humaine if assistance_deplacement == 'Oui' else None,
        "aide_technique": aide_technique if assistance_deplacement == 'Oui' else None,
        "autre_assistance": autre_assistance if assistance_deplacement == 'Oui' else None,
        "autre_assistance_text": autre_assistance_text if assistance_deplacement == 'Oui' else None
    },
    "travail": travail
}

###
slider_values_vie = [1,2,3,4,5]
#slider_strings = ["Très insuffisant", "Insuffisant", "Satisfaisant", "Très satisfaisant"]
#slider_strings = ["Non", "Un peu", "Oui"]
slider_strings = ["Pas du tout d'accord", "Plutôt pas d'accord", "Plutôt d'accord", "Assez d'accord", "Très d'accord", "Complètement d'accord"]



st.header("Qualité de Vie")

def format_func(value):
    options = ["Très bonne", "Bonne", "Moyenne", "Mauvaise", "Très Mauvaise"]
    return options[value - 1]  

vie_general = st.select_slider(
    "Comment évaluez-vous votre qualité de vie générale",
    options=[5, 4, 3, 2, 1],
    value=5,
    format_func=format_func
)


def format_func2(value):
    options = ["Aucun impact", "Impact mineur", "Impact modéré", "Impact important", "Impact très important"]
    return options[value - 1]  

vie_sociale = st.select_slider(
    "Quel impact votre trouble moteur a-t-il sur votre vie sociale ?",
    options=[1, 2, 3, 4, 5],
    value=1,
    format_func=format_func2
)

commentaires = st.text_input("Autre commentaires :")

# Collect:
qualite_data = {
    "qualite_vie": vie_general,
    "impact_vie_sociale": vie_sociale,
    "commentaires": commentaires
}



# Submission
#if st.button("Soumettre"):
#    if temps_trouble is None or nature_trouble is None or douleurs is None or aides_techniques is None:
#        st.error("Veuillez répondre à toutes les questions.")
#    else:
#        st.success("Merci pour vos réponses.")
#        # Process the responses
#        responses = {
#            "paralysie": paralysie,
#            "sclerose": sclerose,
#            "dystrophie": dystrophie,
#            "amputation": amputation,
#            "atrophie": atrophie,
#            "autre": autre,
#            "autre_text": autre_text,
#            "temps_trouble": temps_trouble,
#            "nature_trouble": nature_trouble,
#            "douleurs": douleurs,
#            "aides_techniques": aides_techniques
#        }
#        st.write(responses)
#        # Here you can add code to save the responses



###

#Comp = [
#    "Organisation du matériel (ex. matériel rangé sur la table)",
#    "Concentration sur tâches exigeantes (ex. reste sur une activité sans se distraire)",
#    "Application des instructions (ex. suit une directive sans rappel)",
#    "Réactivité modérée aux distractions externes (ex. ignore les bruits alentours lors d'une tâche)",
#    "Fluidité dans les transitions (ex. change d'activité sans délai)",
#    "Capacité à rester calme (ex. reste assis pendant une histoire)",
#    "Gestion des mouvements et manipulations (ex. ne met pas d'objets à la bouche)",
#    "Régulation des prises de parole (ex. parle à des moments appropriés)",
#    "Adaptation sociale et émotionnelle (ex. joue sans exclure les autres)",
#    "Engagement dans les jeux collectifs (ex. suit les règles du jeu)"
#    ]

Comp = [
     "L'utilisation de la planche permet d'améliorer ma mobilité.",
    "L'utilisation de la planche améliore mon indépendance dans les activités quotidiennes.",
    "Je trouve que la planche s'adapte facilement à différents environnements et situations.",
    "Je pense que l'utilisation de la planche réduit mon risque de blessures lors des transferts.",
    "Je trouve globalement la planche encombrante et difficile à transporter.",
    "J'ai peur de basculer ou de tomber quand j'utilise la planche.",
    "L'utilisation de la planche est inconfortable.",
    "J'utilise la planche uniquement parce que je n'ai pas d'autres options.",
    "Je préfère utiliser d'autres méthodes que la planche pour les transferts (aide d'un aidant, support mural, etc.).",
    "Le bois semble adapté en terme de poids.",
    "Le bois semble adapté en terme de durabilité.",
    "Le polycarbonate semble adapté en terme de poids.",
    "Le polycarbonate semble adapté en terme de durabilité.",
    "Les matériaux en résine semblent adaptés en terme de poids.",
    "Les matériaux en résine semblent adaptés en terme de durabilité.",
    "Les matériaux en composite semblent adaptés en terme de poids.",
    "Les matériaux en composite semblent adaptés en terme de durabilité.",
    "La planche offre actuellement un équilibre optimal pour prévenir le glissement non désiré.",
    "Un antidérapant semble nécessaire pour améliorer la sécurité de la glisse.",
    "Ma glisse est identique peu importe les vêtements que je porte.",
    "Je peux réaliser la glisse en sécurité même en étant totalement dénudé.",
    "Une forme courbe me semblerait adaptée en terme de fonctionnalité.",
    "Une forme courbe me semblerait adaptée en terme de stabilité et de sécurité.",
    "Une encoche sur la planche me semblerait adaptée en terme de fonctionnalité.",
    "Une encoche sur la planche me semblerait adaptée en terme de stabilité et de sécurité.",
    "Une accroche permettant de fixer la planche au fauteuil semble indispensable à une planche innovante.",
    "Un système permettant à la planche de se plier semble indispensable à une planche innovante.",
    "Un système permettant à la planche de se monter sur plusieurs supports semble indispensable à une planche innovante.",
    "Une technologie intégrée à la planche pour prévenir les escarres serait une innovation notable pour les utilisateurs.",
    "Une technologie intégrée à la planche pour réaliser sa pesée lors des transferts serait une innovation notable pour les utilisateurs.",
    "Des capteurs intégrés à la planche pour surveiller la glisse lors des transferts représenteraient une innovation notable pour les utilisateurs."]





st.markdown(
        """<style>
        div[class*="stSlider"] > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 20px;
                }
        </style>
                """, unsafe_allow_html=True)


st.markdown(
    """
    <style>
    .centered_button {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.write("""
# Questionnaire Planche de Transfert
""")


st.sidebar.header('Informations')

#slider_values = [1,2,3,4]
#slider_values = [1,2,3]
slider_values = [1,2,3,4,5,6]
#slider_strings = ["Très insuffisant", "Insuffisant", "Satisfaisant", "Très satisfaisant"]
#slider_strings = ["Non", "Un peu", "Oui"]
slider_strings = ["Pas du tout d'accord", "Plutôt pas d'accord", "Plutôt d'accord", "Assez d'accord", "Très d'accord", "Complètement d'accord"]

def stringify(i:int = 0) -> str:
    return slider_strings[i-1]

#T1 = st.select_slider(
#    "Je quitte souvent ma place sans nécessité lors d'une réunion.",
#    options=slider_values,
#    value=1,
#    format_func=stringify)

#def save_and_download_csv(df):
#    csv_string = df.to_csv(index=False,sep=';')
#    b64 = base64.b64encode(csv_string.encode()).decode()
#    href = f'<a href="data:file/csv;base64,{b64}" download="features.csv">Download CSV File</a>'
#    st.markdown(href, unsafe_allow_html=True)

# def custom_date_input(label, min_date=None, max_date=None):
#     if min_date is None:
#         min_date = datetime.datetime(year=1900, month=1, day=1)
#     if max_date is None:
#         max_date = datetime.datetime(year=2100, month=12, day=31)
#     year = st.number_input("Year", min_value=min_date.year, max_value=max_date.year, step=1, value=min_date.year)
#     month = st.number_input("Month", min_value=1, max_value=12, step=1, value=min_date.month)
#     day = st.number_input("Day", min_value=1, max_value=31, step=1, value=min_date.day)
#     try:
#         date_input = datetime.datetime(year=year, month=month, day=day)
#         if min_date <= date_input <= max_date:
#             return date_input
#         else:
#             st.error("Please enter a date within the specified range.")
#             return None
#     except ValueError:
#         st.error("Please enter a valid date.")
#         return None

def write_data(new_data):
    db = client.Questionnaire
    db.Transfer.insert_one(new_data)
    


def user_input_features():
        #current_date = datetime.date.today()
        surname = st.sidebar.text_input("Nom")
        name = st.sidebar.text_input("Prénom")
        #date = st.sidebar.date_input("Date de naissance", datetime.date(2010, 1, 1))
        default_value = datetime.now()
        with st.sidebar.container():
            st.write("Date de Naissance")
            birthDate = date_picker(picker_type=PickerType.date, value=default_value, key='date_picker')
        #age = current_date.year - date.year - ((current_date.month, current_date.day) < (date.month, date.day))
        sex = st.sidebar.selectbox('Genre',('Homme','Femme'))
        #study = st.sidebar.selectbox("Niveau d'etude",('CAP/BEP','Baccalauréat professionnel','Baccalauréat général', 'Bac +2 (DUT/BTS)', 'Bac +3 (Licence)',
        #                                               'Bac +5 (Master)', 'Bac +7 (Doctorat, écoles supérieurs)'))
        #questionnaire = st.sidebar.selectbox('Questionnaire',('TRAQ','FAST','TRAQ+FAST'))
        st.write("""## A propos de votre perception de la planche de transfert...""")
        for i, question in enumerate(Comp, start=1):
            slider_output = st.select_slider(
            f"{question}",
            options=slider_values,
            value=1,
            format_func=stringify
            )
            answers[f"THERM{i}"] = slider_output


        user_data = {"lastName": surname,
                     'firstName': name,
                     #'birthDate': birthDate.isoformat(),
                     'birthDate': birthDate,
                     'sex': sex}
        answers_data = answers

        document = {
        #"_id": ObjectId(),  # Generate a new ObjectId
        "questionaire": "Planche de Transfer",
        "situation": {},
        "vie": {},
        "qualite": {},
        "user": user_data,
        "answers": answers_data
        #"__v": 0
        }
                
        return document



document = user_input_features()
document["situation"] = situation_data
document["vie"] = vie_data
document["qualite"] = qualite_data

#if st.button('Enregisterez'):
#    write_data(document)
#save_and_download_csv(df)
#st.write(document)
# for centering the page
#input_date = custom_date_input("Select a date")
#if input_date:
#    st.write("Selected date:", input_date)
     
     
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    button = st.button('Enregistrer')
    st.image("clinicogImg.png", width=200)
    
if button:
    if all([participation == 'Oui', retrait == 'Oui', confidentialite == 'Oui', utilisation_donnees == 'Oui']):
        write_data(document)
        st.write("Merci d'avoir participé(e) à ce questionnaire")
    else:
        st.write("Pour enregistrer vos résultats, vous devez consentir à cette étude.")
     


     

