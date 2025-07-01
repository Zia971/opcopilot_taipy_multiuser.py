"""
OPCOPILOT v4.0 - Application Taipy MULTI-UTILISATEURS
STATE MANAGEMENT CORRIGE - Compatible Railway
Variables state correctement initialisees
"""

from taipy.gui import Gui, Markdown, navigate
from taipy import Config
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import hashlib
import os

# ==============================================================================
# VARIABLES STATE GLOBALES - DECLARATION EXPLICITE POUR TAIPY
# ==============================================================================

# Variables d'authentification (initialisees globalement)
authenticated = False
current_user = None
user_data = None

# Variables de navigation
current_page = "login"
selected_operation = None
selected_operation_id = None

# Variables de formulaires
username_input = ""
password_input = ""
error_message = ""

# Variables metier
user_operations = []
user_kpis = {}

# ==============================================================================
# DONNEES STATIQUES
# ==============================================================================

DEMO_ACO_USERS = {
    "aco1": {
        "password": "password1",
        "nom": "Pierre DUPONT",
        "role": "ACO",
        "secteur": "Les Abymes - Pointe-a-Pitre",
        "operations": 18
    },
    "aco2": {
        "password": "password2", 
        "nom": "Sophie MARTIN",
        "role": "ACO_SENIOR",
        "secteur": "Basse-Terre - Sainte-Anne",
        "operations": 25
    },
    "aco3": {
        "password": "password3",
        "nom": "Alexandre BERNARD", 
        "role": "ACO",
        "secteur": "Baie-Mahault - Lamentin",
        "operations": 12
    }
}

DEMO_DATA = {
    'operations_demo': [
        {
            'id': 1,
            'nom': 'RESIDENCE SOLEIL',
            'type_operation': 'OPP',
            'commune': 'Les Abymes',
            'statut': 'EN_COURS',
            'avancement': 75,
            'budget_total': 2450000,
            'nb_logements_total': 45,
            'date_creation': '2023-03-15',
            'freins_actifs': 1
        },
        {
            'id': 2,
            'nom': 'COUR CHARNEAU',
            'type_operation': 'OPP',
            'commune': 'Pointe-a-Pitre',
            'statut': 'EN_RECEPTION',
            'avancement': 95,
            'budget_total': 1850000,
            'nb_logements_total': 32,
            'date_creation': '2022-09-10',
            'freins_actifs': 0
        },
        {
            'id': 3,
            'nom': 'VEFA BELCOURT',
            'type_operation': 'VEFA',
            'commune': 'Basse-Terre',
            'statut': 'EN_COURS',
            'avancement': 45,
            'budget_total': 1650000,
            'nb_logements_total': 28,
            'date_creation': '2024-01-20',
            'freins_actifs': 2
        }
    ],
    'kpis_aco_demo': {
        'operations_actives': 23,
        'operations_cloturees': 5,
        'rem_realisee_2024': 485000,
        'rem_prevue_2024': 620000,
        'taux_realisation_rem': 78,
        'freins_actifs': 3,
        'freins_critiques': 2,
        'echeances_semaine': 5,
        'validations_requises': 12
    }
}

# ==============================================================================
# FONCTIONS D'INITIALISATION CORRIGEES
# ==============================================================================

def on_init(state):
    """
    FONCTION CRITIQUE : Initialisation automatique Taipy
    Appelee pour chaque nouvelle session
    """
    print("Initialisation nouvelle session utilisateur")
    
    # Initialisation variables d'authentification
    state.authenticated = False
    state.current_user = None
    state.user_data = None
    
    # Initialisation variables de navigation
    state.current_page = "login"
    state.selected_operation = None
    state.selected_operation_id = None
    
    # Initialisation variables de formulaires
    state.username_input = ""
    state.password_input = ""
    state.error_message = ""
    
    # Initialisation variables metier
    state.user_operations = []
    state.user_kpis = {}
    
    print(f"Session initialisee - Auth: {state.authenticated}")

def verify_password(username, password):
    """Verification identifiants"""
    if username in DEMO_ACO_USERS:
        stored_password = DEMO_ACO_USERS[username]["password"]
        return stored_password == password
    return False

def load_user_specific_data(state):
    """Charge les donnees specifiques a l'utilisateur"""
    if state.authenticated and state.current_user:
        user_role = state.user_data.get('role', 'ACO')
        user_sector = state.user_data.get('secteur', '')
        
        # Filtrage operations par ACO
        all_operations = DEMO_DATA['operations_demo']
        if user_role == 'ACO':
            state.user_operations = [op for op in all_operations if 'Les Abymes' in user_sector or 'Pointe-a-Pitre' in user_sector]
        else:
            state.user_operations = all_operations.copy()
        
        # KPIs specifiques utilisateur
        state.user_kpis = DEMO_DATA['kpis_aco_demo'].copy()
        
        # Ajustement KPIs selon utilisateur
        if state.current_user == 'aco1':
            state.user_kpis['operations_actives'] = 18
            state.user_kpis['rem_realisee_2024'] = 385000
        elif state.current_user == 'aco2':
            state.user_kpis['operations_actives'] = 25
            state.user_kpis['rem_realisee_2024'] = 598000
        elif state.current_user == 'aco3':
            state.user_kpis['operations_actives'] = 12
            state.user_kpis['rem_realisee_2024'] = 245000

# ==============================================================================
# ACTIONS UTILISATEUR CORRIGEES
# ==============================================================================

def login_action(state):
    """Action de connexion corrigee"""
    print(f"Tentative connexion: {state.username_input}")
    
    # Reset message erreur
    state.error_message = ""
    
    if state.username_input and state.password_input:
        if verify_password(state.username_input, state.password_input):
            # Connexion reussie
            state.authenticated = True
            state.current_user = state.username_input
            state.user_data = DEMO_ACO_USERS[state.username_input].copy()
            state.current_page = "dashboard"
            
            # Chargement donnees utilisateur
            load_user_specific_data(state)
            
            # Reset formulaire
            state.username_input = ""
            state.password_input = ""
            
            print(f"Connexion reussie pour: {state.current_user}")
            navigate(state, "dashboard")
        else:
            state.error_message = "Identifiants incorrects"
            print("Echec connexion - identifiants incorrects")
    else:
        state.error_message = "Veuillez remplir tous les champs"
        print("Echec connexion - champs manquants")

def logout_action(state):
    """Action de deconnexion"""
    print(f"Deconnexion utilisateur: {state.current_user}")
    
    # Reset session
    state.authenticated = False
    state.current_user = None
    state.user_data = None
    state.current_page = "login"
    state.selected_operation = None
    state.selected_operation_id = None
    state.user_operations = []
    state.user_kpis = {}
    state.error_message = ""
    
    navigate(state, "login")

def nav_dashboard(state):
    """Navigation dashboard"""
    if state.authenticated:
        state.current_page = "dashboard"
        navigate(state, "dashboard")

def nav_portefeuille(state):
    """Navigation portefeuille"""
    if state.authenticated:
        state.current_page = "portefeuille"
        navigate(state, "portefeuille")

def nav_login(state):
    """Navigation login"""
    state.current_page = "login"
    navigate(state, "login")

# ==============================================================================
# CSS STYLES
# ==============================================================================

css_styles = """
<style>
.taipy-page {
    background-color: #F9FAFB !important;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #10B981 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px rgba(139, 92, 246, 0.2);
    text-align: center;
}

.login-container {
    background: white;
    border-radius: 16px;
    padding: 3rem;
    box-shadow: 0 20px 50px rgba(139, 92, 246, 0.15);
    border: 1px solid #E5E7EB;
    max-width: 450px;
    margin: 2rem auto;
}

.login-title {
    text-align: center;
    color: #1F2937;
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.kpi-card {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin: 0.5rem;
    box-shadow: 0 10px 40px rgba(139, 92, 246, 0.15);
    min-height: 180px;
}

.kpi-operations {
    background: linear-gradient(145deg, #3B82F6, #2563EB);
    color: white;
}

.kpi-rem {
    background: linear-gradient(145deg, #10B981, #059669);
    color: white;
}

.kpi-freins {
    background: linear-gradient(145deg, #F59E0B, #D97706);
    color: white;
}

.kpi-echeances {
    background: linear-gradient(145deg, #EF4444, #DC2626);
    color: white;
}

.taipy-button {
    background: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
}

.error-message {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    color: #DC2626;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 4px solid #EF4444;
}

.user-info {
    background: linear-gradient(135deg, #D1FAE5, #10B981);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    font-weight: 600;
}

.success-info {
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    color: #166534;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 4px solid #10B981;
}
</style>
"""

# ==============================================================================
# PAGES TAIPY
# ==============================================================================

login_page = css_styles + """
<div class="main-header">
    <h1>OPCOPILOT v4.0</h1>
    <h2>Tableau de Bord Operationnel</h2>
    <p>SPIC Guadeloupe - Sessions Securisees</p>
</div>

<div class="login-container">
    <div class="login-title">Connexion ACO</div>
    
    **Identifiant**
    <|{username_input}|text|>
    
    **Mot de passe**
    <|{password_input}|text|password=True|>
    
    <|Se connecter|button|on_action=login_action|>
    
    <|part|render={error_message != ""}|
    <div class="error-message">{error_message}</div>
    |>
</div>

---

**Comptes de test :**
- **aco1** / password1 (Pierre DUPONT)
- **aco2** / password2 (Sophie MARTIN)  
- **aco3** / password3 (Alexandre BERNARD)

**RAILWAY TEST : Multi-utilisateurs fonctionnel**
"""

dashboard_page = css_styles + """
<|part|render={not authenticated}|
<div class="error-message">
    Acces non autorise - Connexion requise
</div>
<|Connexion|button|on_action=nav_login|>
|>

<|part|render={authenticated}|
<div class="main-header">
    <h1>OPCOPILOT v4.0 - Dashboard</h1>
    <h2>{user_data.get('nom', 'ACO') if user_data else 'ACO'}</h2>
    <p>{user_data.get('secteur', '') if user_data else ''}</p>
</div>

<div class="user-info">
    Session: {current_user} | Role: {user_data.get('role', '') if user_data else ''} | Operations: {len(user_operations)}
</div>

## KPIs Personnalises

<|layout|columns=1 1 1 1|
<div class="kpi-card kpi-operations">
    <div style="font-size: 2.5rem; font-weight: bold;">{user_kpis.get('operations_actives', 0) if user_kpis else 0}</div>
    <div>Mes Operations</div>
    <|Portfolio|button|on_action=nav_portefeuille|>
</div>
|
<div class="kpi-card kpi-rem">
    <div style="font-size: 2.5rem; font-weight: bold;">{int(user_kpis.get('rem_realisee_2024', 0)/1000) if user_kpis else 0}k</div>
    <div>REM 2024 (EUR)</div>
    <|Analyse|button|>
</div>
|
<div class="kpi-card kpi-freins">
    <div style="font-size: 2.5rem; font-weight: bold;">{user_kpis.get('freins_actifs', 0) if user_kpis else 0}</div>
    <div>Freins Actifs</div>
    <|Gestion|button|>
</div>
|
<div class="kpi-card kpi-echeances">
    <div style="font-size: 2.5rem; font-weight: bold;">{user_kpis.get('echeances_semaine', 0) if user_kpis else 0}</div>
    <div>Echeances</div>
    <|Planning|button|>
</div>
|>

## Operations Recentes

<|{user_operations}|table|columns=nom,type_operation,commune,statut,avancement|page_size=3|>

<div class="success-info">
    RAILWAY: State management fonctionne | User: {current_user} | Auth: {authenticated}
</div>

<|Deconnexion|button|on_action=logout_action|>
|>
"""

portefeuille_page = css_styles + """
<|part|render={not authenticated}|
<div class="error-message">Connexion requise</div>
<|Connexion|button|on_action=nav_login|>
|>

<|part|render={authenticated}|
<div class="main-header">
    <h1>Mon Portefeuille</h1>
    <h2>{user_data.get('nom', '') if user_data else ''}</h2>
</div>

<div class="user-info">
    {current_user} - {len(user_operations)} operations dans votre portefeuille
</div>

## Mes Operations

<|{user_operations}|table|columns=nom,type_operation,commune,statut,avancement,budget_total|>

<|Dashboard|button|on_action=nav_dashboard|>
<|Deconnexion|button|on_action=logout_action|>
|>
"""

# ==============================================================================
# APPLICATION PRINCIPALE
# ==============================================================================

def create_app():
    """Creation application Taipy avec state management corrige"""
    
    pages = {
        "login": Markdown(login_page),
        "dashboard": Markdown(dashboard_page),
        "portefeuille": Markdown(portefeuille_page)
    }
    
    gui = Gui(pages=pages)
    
    # Configuration hook d'initialisation
    gui.on_init = on_init
    
    return gui

# ==============================================================================
# POINT D'ENTREE RAILWAY
# ==============================================================================

if __name__ == "__main__":
    print("=== OPCOPILOT v4.0 - RAILWAY DEPLOYMENT ===")
    print("State management: CORRIGE")
    print("Multi-utilisateurs: ACTIF")
    print("Comptes test: aco1/password1, aco2/password2, aco3/password3")
    
    app = create_app()
    
    # Configuration Railway
    port = int(os.environ.get("PORT", 5000))
    is_production = os.environ.get("ENV") == "production"
    
    print(f"Port: {port}")
    print(f"Mode production: {is_production}")
    
    app.run(
        title="OPCOPILOT v4.0 - Multi-Users",
        port=port,
        debug=not is_production,
        use_reloader=False,
        host="0.0.0.0"
    )
