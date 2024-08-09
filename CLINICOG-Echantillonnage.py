import streamlit as st
import pandas as pd
import base64
from datetime import datetime, timedelta, date
import pymongo
import hmac
from streamlit_date_picker import date_range_picker, date_picker, PickerType
import time
import requests
#from bson import ObjectId

st.set_page_config(page_title="CLINICOG Echantillonnage", page_icon="🧠")

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



#st.markdown(
#        """<style>
#        .main {
#            background-color: #bbdcee;
#        }
#        div[class*="stSlider"] > label > div[data-testid="stMarkdownContainer"] > p {
#        font-size: 20px;
#        color: #000000;
#                }
#        /* Override Streamlit's default styles for both modes */
#        /* Override Streamlit's default styles for both modes */
#    [data-testid="stAppViewContainer"], 
#    .css-1v5fq88, 
#    .css-10trblm, 
#    .css-1cpxqw2, 
#    .css-qbe2hs {
#        background-color: #bbdcee; /* Same background color for both modes */
#        color: #000000; /* Your desired font color */
#    }
#    /* Additional general text styling */
#    body, .css-1cpxqw2 *, .css-qbe2hs * {
#        color: #000000; /* Ensure general text color is black */
#    }
#        </style>
#                """, unsafe_allow_html=True)


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

def get_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        return ip
    except Exception as e:
        st.error(f"Error getting IP address: {e}")
        return None

###
# Consentement

st.markdown("### Merci de remplir les questions suivantes, et de cliquer sur 'Enregistrer' à la fin du questionnaire. Seules les questions marquées d'un (*) sont obligatoires.")

st.subheader("Je suis :*")
sex = st.radio(
        "Sexe",
        ('Un homme', 'Une femme'),
        index=None,
        label_visibility="hidden"
    )

st.subheader("Mon âge :*")
age = st.number_input(
    "Age",
    label_visibility="hidden",
    min_value=0,  # Placeholder value
    max_value=99,
    value=0,  # Start with -1 as a "None" equivalent
    step=1
)

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

ip_collection = st.radio(
        "Je consens à la collecte de mon adresse IP *",
        ('Oui', 'Non'),
        index=None
    )

###

st.header("Vie quotidienne et autonomie")

# Niveau d'autonomie
st.subheader("Niveau d'autonomie dans les activités quotidiennes (manger, s'habiller, se laver, etc.) : *")
autonomie = st.radio(
    "autonomie",
    ('Totalement autonome', 'Partiellement autonome (besoin d\'aide pour certaines activités)', 
     'Dépendant (besoin d\'aide pour la plupart des activités)', 'Totalement dépendant'),
    index=None,
    label_visibility="hidden"
)

# Assistance pour déplacements
st.subheader("Avez-vous besoin d'une assistance pour vos déplacements ?*")
assistance_deplacement = st.radio(
    "assistance",
    ('Oui', 'Non'),
    index=None,
    key = "assitance",
    label_visibility="hidden"
)

# Si oui, quel type d'assistance ?
if assistance_deplacement == 'Oui':
    st.subheader("Si oui, quel type d'assistance ?")
    assistance_humaine = st.checkbox("Assistance humaine (aidant familial, assistant personnel)")
    aide_technique = st.checkbox("Aide technique (fauteuil roulant, déambulateur)")
    autre_assistance = st.checkbox("Autre (préciser) :")
    autre_assistance_text = st.text_input("Préciser si autre :")

# Travail
st.subheader("Travaillez-vous actuellement ?*")
travail = st.radio(
    "travail",
    ('Oui, à temps plein', 'Oui, à temps partiel', 'Non, mais je cherche du travail', 'Non, je ne cherche pas de travail'),
    index=None,
    key="travail",
    label_visibility="hidden"
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
st.header("Aménagement du Lieu de Vie")

st.subheader("Cuisine :")

st.subheader("Votre cuisine est-elle aménagée pour être accessible en fauteuil roulant ?*")
cuisine_roulant = st.radio(
    "cuisine",
    ('Oui', 'Non'),
    index=None,
    key="roulant",
    label_visibility="hidden"
)


st.subheader("Quels aménagements spécifiques avez-vous dans votre cuisine pour faciliter l'accès et l'utilisation ?")
cuisine_plans = st.checkbox("Plans de travail abaissés")
cusine_placards = st.checkbox("Placards accessibles")
cuisine_adapte = st.checkbox("Évier adapté")
autre_cuisine = st.checkbox("Autre (préciser) :",key="autre_cuisine")
autre_cuisine_text = st.text_input("Préciser si autre :", key="autre_cuisine_text")

st.subheader("Salle de Bain :")

st.subheader("Disposez-vous d'une douche accessible, telle qu'une douche à l'italienne ?*")
bain_italienne = st.radio(
    "bain",
    ('Oui', 'Non'),
    index=None,
    key="italienne",
    label_visibility="hidden"
)


st.subheader("Avez-vous des équipements spéciaux installés dans votre salle de bain pour faciliter votre autonomie ?")
bain_banc = st.checkbox("Banc de douche")
bain_barres = st.checkbox("Barres d'appui")
bain_douche = st.checkbox("Douche à l'italienne")
autre_bain = st.checkbox("Autre (préciser) :",key="autre_bain")
autre_bain_text = st.text_input("Préciser si autre :", key="autre_bain_text")

st.subheader("Y a-t-il des obstacles spécifiques dans votre lieu de vie qui rendent l'utilisation de la planche de transfert difficile ?*")
obstacles = st.radio(
    "obstacles",
    ('Oui', 'Non'),
    index=None,
    key="obstacles",
    label_visibility="hidden"
)
obstacles_text = None
if obstacles == 'Oui':
    obstacles_text = st.text_input("Veuillez préciser", key="obstacles_text")

st.subheader("Avez-vous des suggestions pour des améliorations de produits qui pourraient aider à surmonter ces obstacles ?")
ameliorations = st.text_input("suggest", key="améliorations",label_visibility="hidden")



amenagement_data = {
    "cuisine roulant": cuisine_roulant,
    "amenagement cuisine":{
        "plans": cuisine_plans,
        "placards": cusine_placards,
        "adapte": cuisine_adapte,
        "autre": autre_cuisine,
        "autre_text": autre_cuisine_text
    },
    "bain italienne": bain_italienne,
    "amenagement bain": {
        "bain banc": bain_banc,
        "bain barres": bain_barres,
        "bain douche": bain_douche,
        "autre bain": autre_bain,
        "autre bain text": autre_bain_text
    },
    "obstacles": obstacles,
    "obstacles text": obstacles_text,
    "ameliorations": ameliorations
}

### 



###
slider_values_vie = [1,2,3,4,5]
#slider_strings = ["Très insuffisant", "Insuffisant", "Satisfaisant", "Très satisfaisant"]
#slider_strings = ["Non", "Un peu", "Oui"]
slider_strings = ["Pas du tout d'accord", "Plutôt pas d'accord", "Plutôt d'accord", "Assez d'accord", "Très d'accord", "Complètement d'accord"]



st.header("Qualité de Vie")

def format_func(value):
    options = ["Très Mauvaise", "Mauvaise", "Moyenne", "Bonne", "Très bonne"]
    return options[value - 1]  

vie_general = st.select_slider(
    "Comment évaluez-vous votre qualité de vie générale*",
    options=[1, 2, 3, 4, 5],
    value=1,
    format_func=format_func
)


def format_func2(value):
    options = ["Aucun impact", "Impact mineur", "Impact modéré", "Impact important", "Impact très important"]
    return options[value - 1]  

vie_sociale = st.select_slider(
    "Quel impact votre trouble moteur a-t-il sur votre vie sociale ?*",
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








st.write("""
# Questionnaire Planche de Transfert
""")


#st.sidebar.header('Informations')

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
        #surname = st.sidebar.text_input("Nom")
        #name = st.sidebar.text_input("Prénom")
        #date = st.sidebar.date_input("Date de naissance", datetime.date(2010, 1, 1))
        #default_value = datetime.now()
        #with st.sidebar.container():
        #    st.write("Date de Naissance")
        #    birthDate = date_picker(picker_type=PickerType.date, value=default_value, key='date_picker')
        #age = current_date.year - date.year - ((current_date.month, current_date.day) < (date.month, date.day))
        #sex = st.sidebar.selectbox('Genre',('Homme','Femme'))
        #study = st.sidebar.selectbox("Niveau d'etude",('CAP/BEP','Baccalauréat professionnel','Baccalauréat général', 'Bac +2 (DUT/BTS)', 'Bac +3 (Licence)',
        #                                               'Bac +5 (Master)', 'Bac +7 (Doctorat, écoles supérieurs)'))
        #questionnaire = st.sidebar.selectbox('Questionnaire',('TRAQ','FAST','TRAQ+FAST'))
        ip = get_ip()
        st.write("""## A propos de votre perception de la planche de transfert...*""")
        for i, question in enumerate(Comp, start=1):
            slider_output = st.select_slider(
            f"{question}",
            options=slider_values,
            value=1,
            format_func=stringify
            )
            answers[f"THERM{i}"] = slider_output


        user_data = {"ip": ip,
                     "sex": sex,
                     "age": age,
                     "date": datetime.now()}
        answers_data = answers

        document = {
        #"_id": ObjectId(),  # Generate a new ObjectId
        "questionaire": "Planche de Transfer",
        "user": user_data,
        "vie": {},
        "amenagement": {},
        "qualite": {},
        "situation": {},
        "answers": answers_data
        #"__v": 0
        }
                
        return document



document = user_input_features()

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

st.subheader("Depuis combien de temps avez-vous ce trouble moteur ? (en années)*")
temps_trouble = st.number_input(
    "temps",
    min_value=0,
    max_value=None,
    value=0,
    step=1,
    label_visibility="hidden"
)

# Nature du trouble moteur
st.subheader("Le trouble moteur est-il :*")
nature_trouble = st.radio(
    "moteur",
    ('Congénital (depuis la naissance)', 'Acquis (après un accident, une maladie, etc.)'),
    index=None,
    label_visibility="hidden"
)

# Douleurs associées au trouble moteur
st.subheader("Avez-vous des douleurs associées à votre trouble moteur ?*")
douleurs = st.radio(
    "moteur2",
    ('Oui, constamment', 'Oui, fréquemment', 'Oui, de temps en temps', 'Non'),
    index=None,
    label_visibility="hidden"
)

# Aides techniques
st.subheader("Utilisez-vous des aides techniques autres que la planche de transfert ? (ex. : fauteuil roulant, canne, déambulateur)*")
aides_techniques = st.radio(
    "aide",
    ('Oui', 'Non'),
    index=None,
    label_visibility="hidden"
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

document["situation"] = situation_data
document["amenagement"] = amenagement_data
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

if "disabled" not in st.session_state:
    st.session_state.disabled = False

left_co, cent_co,last_co = st.columns(3)

with cent_co:
    button = st.button('Enregistrer', disabled=st.session_state.disabled)

     
left_co, cent_co,last_co = st.columns(3)
with left_co:
    st.image("logo.png", width=200)

with last_co:
    st.image("Logo_GrHandiOse.png", width=150)


with cent_co:
    st.image("clinicogImg.png", width=200)


    
if button:
    if all([participation == 'Oui', retrait == 'Oui', confidentialite == 'Oui', utilisation_donnees == 'Oui', ip_collection == 'Oui', sex,
            age!=0, autonomie, assistance_deplacement, travail, cuisine_roulant, bain_italienne, obstacles, nature_trouble, douleurs, aides_techniques]):
        write_data(document)
        st.write("### Merci d'avoir participé(e) à ce questionnaire. Ce questionnaire a été réalisé en collaboration avec Innov'Autonomie et GRHANDIOSE.")
        st.session_state.disabled = True
        time.sleep(5)
        st.rerun()
        
    else:
        st.write("### Pour enregistrer vos résultats, vous devez remplir toutes les questions marquées avec *.")
     


     

