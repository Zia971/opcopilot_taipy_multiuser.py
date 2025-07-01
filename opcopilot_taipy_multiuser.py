"""
OPCOPILOT v4.0 - Application Taipy ARCHITECTURE STATE OFFICIELLE
CORRECTION CRITIQUE : Declaration variables state selon syntaxe Taipy
Compatible Railway avec state management proper
"""

from taipy.gui import Gui, Markdown, navigate
import pandas as pd
import os

# ==============================================================================
# DECLARATION VARIABLES STATE TAIPY OFFICIELLE
# Toutes les variables state doivent etre declarees au niveau global
# Taipy les reconnait automatiquement selon cette syntaxe
# ==============================================================================

# Variables d'authentification (declarees globalement pour Taipy)
authenticated = False
current_user = ""
username_input = ""
password_input = ""
error_message = ""

# Variables utilisateur (declarees globalement pour Taipy)
user_nom = ""
user_role = ""
user_secteur = ""

# Variables navigation (declarees globalement pour Taipy)
current_page = "login"

# Variables KPIs (declarees globalement pour Taipy)
operations_actives = 0
operations_cloturees = 0
rem_realisee = 0
rem_prevue = 0
taux_realisation = 0
freins_actifs = 0
freins_critiques = 0
echeances_semaine = 0
validations_requises = 0

# Variables operations (declarees globalement pour Taipy)
user_operations = []

# ==============================================================================
# DONNEES STATIQUES
# ==============================================================================

DEMO_ACO_USERS = {
    "aco1": {
        "password": "password1",
        "nom": "Pierre DUPONT",
        "role": "ACO",
        "secteur": "Les Abymes - Pointe-a-Pitre"
    },
    "aco2": {
        "password": "password2", 
        "nom": "Sophie MARTIN",
        "role": "ACO_SENIOR",
        "secteur": "Basse-Terre - Sainte-Anne"
    },
    "aco3": {
        "password": "password3",
        "nom": "Alexandre BERNARD", 
        "role": "ACO",
        "secteur": "Baie-Mahault - Lamentin"
    }
}

DEMO_OPERATIONS = [
    {
        'nom': 'RESIDENCE SOLEIL',
        'type_operation': 'OPP',
        'commune': 'Les Abymes',
        'statut': 'EN_COURS',
        'avancement': 75,
        'budget_total': 2450000
    },
    {
        'nom': 'COUR CHARNEAU',
        'type_operation': 'OPP',
        'commune': 'Pointe-a-Pitre',
        'statut': 'EN_RECEPTION',
        'avancement': 95,
        'budget_total': 1850000
    },
    {
        'nom': 'VEFA BELCOURT',
        'type_operation': 'VEFA',
        'commune': 'Basse-Terre',
        'statut': 'EN_COURS',
        'avancement': 45,
        'budget_total': 1650000
    }
]

# ==============================================================================
# FONCTIONS METIER
# ==============================================================================

def verify_password(username, password):
    """Verification identifiants"""
    return username in DEMO_ACO_USERS and DEMO_ACO_USERS[username]["password"] == password

def load_user_data(state, username):
    """Charge donnees specifiques utilisateur"""
    if username in DEMO_ACO_USERS:
        user_data = DEMO_ACO_USERS[username]
        
        # Mise a jour variables utilisateur
        state.user_nom = user_data["nom"]
        state.user_role = user_data["role"]
        state.user_secteur = user_data["secteur"]
        
        # Filtrage operations selon utilisateur
        if username == "aco1":
            state.user_operations = [DEMO_OPERATIONS[0], DEMO_OPERATIONS[1]]
            state.operations_actives = 18
            state.rem_realisee = 385000
        elif username == "aco2":
            state.user_operations = DEMO_OPERATIONS.copy()
            state.operations_actives = 25
            state.rem_realisee = 598000
        elif username == "aco3":
            state.user_operations = [DEMO_OPERATIONS[2]]
            state.operations_actives = 12
            state.rem_realisee = 245000
        
        # KPIs communs
        state.operations_cloturees = 5
        state.rem_prevue = 620000
        state.taux_realisation = int((state.rem_realisee / state.rem_prevue) * 100)
        state.freins_actifs = 3
        state.freins_critiques = 2
        state.echeances_semaine = 5
        state.validations_requises = 12

# ==============================================================================
# ACTIONS UTILISATEUR AVEC STATE TAIPY OFFICIEL
# ==============================================================================

def login_action(state):
    """Action connexion avec variables state declarees"""
    print(f"Tentative connexion: {state.username_input}")
    
    # Reset erreur
    state.error_message = ""
    
    if state.username_input and state.password_input:
        if verify_password(state.username_input, state.password_input):
            # Connexion reussie
            state.authenticated = True
            state.current_user = state.username_input
            
            # Chargement donnees utilisateur
            load_user_data(state, state.username_input)
            
            # Reset formulaire
            state.username_input = ""
            state.password_input = ""
            
            print(f"Connexion reussie: {state.current_user}")
            navigate(state, "dashboard")
        else:
            state.error_message = "Identifiants incorrects"
    else:
        state.error_message = "Champs obligatoires manquants"

def logout_action(state):
    """Deconnexion avec reset variables state"""
    print(f"Deconnexion: {state.current_user}")
    
    # Reset toutes les variables state
    state.authenticated = False
    state.current_user = ""
    state.user_nom = ""
    state.user_role = ""
    state.user_secteur = ""
    state.operations_actives = 0
    state.operations_cloturees = 0
    state.rem_realisee = 0
    state.taux_realisation = 0
    state.user_operations = []
    state.error_message = ""
    
    navigate(state, "login")

def nav_dashboard(state):
    """Navigation dashboard"""
    if state.authenticated:
        navigate(state, "dashboard")

def nav_portefeuille(state):
    """Navigation portefeuille"""
    if state.authenticated:
        navigate(state, "portefeuille")

def nav_login(state):
    """Navigation login"""
    navigate(state, "login")

# ==============================================================================
# INITIALISATION TAIPY OFFICIELLE
# ==============================================================================

def on_init(state):
    """Initialisation session Taipy - variables deja declarees"""
    print("Initialisation session Taipy")
    
    # Les variables sont deja declarees globalement
    # Taipy les reconnait automatiquement
    # Pas besoin de state.variable = valeur dans on_init
    
    print(f"Session initialisee - Auth: {state.authenticated}")

# ==============================================================================
# CSS STYLES
# ==============================================================================

css_styles = """
<style>
.main-header {
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #10B981 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
}

.login-container {
    background: white;
    border-radius: 16px;
    padding: 3rem;
    box-shadow: 0 20px 50px rgba(139, 92, 246, 0.15);
    max-width: 450px;
    margin: 2rem auto;
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

.kpi-operations { background: linear-gradient(145deg, #3B82F6, #2563EB); color: white; }
.kpi-rem { background: linear-gradient(145deg, #10B981, #059669); color: white; }
.kpi-freins { background: linear-gradient(145deg, #F59E0B, #D97706); color: white; }
.kpi-echeances { background: linear-gradient(145deg, #EF4444, #DC2626); color: white; }

.user-info {
    background: linear-gradient(135deg, #D1FAE5, #10B981);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    font-weight: 600;
}

.error-message {
    background: #FEF2F2;
    color: #DC2626;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 4px solid #EF4444;
}

.success-info {
    background: #F0FDF4;
    color: #166534;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 4px solid #10B981;
}
</style>
"""

# ==============================================================================
# PAGES TAIPY AVEC VARIABLES STATE DECLAREES
# ==============================================================================

login_page = css_styles + """
<div class="main-header">
    <h1>OPCOPILOT v4.0</h1>
    <h2>Architecture State Officielle</h2>
    <p>SPIC Guadeloupe - Variables State Declarees</p>
</div>

<div class="login-container">
    <h3>Connexion ACO</h3>
    
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

**Comptes test Railway :**
- **aco1** / password1 (Pierre DUPONT)
- **aco2** / password2 (Sophie MARTIN)  
- **aco3** / password3 (Alexandre BERNARD)

**ARCHITECTURE : Variables state declarees selon syntaxe Taipy officielle**
"""

dashboard_page = css_styles + """
<|part|render={not authenticated}|
<div class="error-message">Connexion requise</div>
<|Connexion|button|on_action=nav_login|>
|>

<|part|render={authenticated}|
<div class="main-header">
    <h1>OPCOPILOT Dashboard</h1>
    <h2>{user_nom}</h2>
    <p>{user_secteur}</p>
</div>

<div class="user-info">
    Session: {current_user} | Role: {user_role} | Operations: {len(user_operations)}
</div>

## KPIs State Management Corrige

<|layout|columns=1 1 1 1|
<div class="kpi-card kpi-operations">
    <div style="font-size: 2.5rem; font-weight: bold;">{operations_actives}</div>
    <div>Operations Actives</div>
    <|Portfolio|button|on_action=nav_portefeuille|>
</div>
|
<div class="kpi-card kpi-rem">
    <div style="font-size: 2.5rem; font-weight: bold;">{int(rem_realisee/1000)}k</div>
    <div>REM 2024 (EUR)</div>
    <div style="font-size: 0.8rem;">{taux_realisation}% realise</div>
</div>
|
<div class="kpi-card kpi-freins">
    <div style="font-size: 2.5rem; font-weight: bold;">{freins_actifs}</div>
    <div>Freins Actifs</div>
    <div style="font-size: 0.8rem;">{freins_critiques} critiques</div>
</div>
|
<div class="kpi-card kpi-echeances">
    <div style="font-size: 2.5rem; font-weight: bold;">{echeances_semaine}</div>
    <div>Echeances</div>
    <div style="font-size: 0.8rem;">{validations_requises} validations</div>
</div>
|>

## Mes Operations

<|{user_operations}|table|columns=nom,type_operation,commune,statut,avancement|page_size=3|>

<div class="success-info">
    STATE MANAGEMENT: Variables declarees selon architecture Taipy | User: {current_user}
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
    <h1>Portefeuille {user_nom}</h1>
    <h2>{user_role} - {user_secteur}</h2>
</div>

<div class="user-info">
    {current_user} - {len(user_operations)} operations dans votre portefeuille
</div>

## Operations Assignees

<|{user_operations}|table|columns=nom,type_operation,commune,statut,avancement,budget_total|>

<|Dashboard|button|on_action=nav_dashboard|>
<|Deconnexion|button|on_action=logout_action|>
|>
"""

# ==============================================================================
# APPLICATION TAIPY AVEC STATE ARCHITECTURE OFFICIELLE
# ==============================================================================

if __name__ == "__main__":
    print("=== OPCOPILOT v4.0 - STATE ARCHITECTURE OFFICIELLE ===")
    print("Variables state: DECLAREES selon syntaxe Taipy")
    print("Multi-utilisateurs: ARCHITECTURE CORRIGEE")
    print("Railway: COMPATIBLE")
    
    # Pages avec variables state declarees
    pages = {
        "login": Markdown(login_page),
        "dashboard": Markdown(dashboard_page),
        "portefeuille": Markdown(portefeuille_page)
    }
    
    # Creation GUI avec hook d'initialisation
    gui = Gui(pages=pages)
    gui.on_init = on_init
    
    # Configuration Railway
    port = int(os.environ.get("PORT", 5000))
    is_production = os.environ.get("ENV") == "production"
    
    print(f"Port: {port}")
    print(f"Production: {is_production}")
    
    # Lancement application
    gui.run(
        title="OPCOPILOT v4.0 - State Architecture",
        port=port,
        debug=not is_production,
        use_reloader=False,
        host="0.0.0.0"
    )
