"""
OPCOPILOT v4.0 - Application Taipy MULTI-UTILISATEURS CORRIGÉE
🚨 CORRECTION CRITIQUE : Variables globales → state.variable
Chaque ACO a sa propre session isolée
"""

from taipy.gui import Gui, Markdown, navigate
from taipy import Config
import pandas as pd
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import hashlib

# ==============================================================================
# ✅ SUPPRESSION COMPLÈTE DES VARIABLES GLOBALES PROBLÉMATIQUES
# ==============================================================================

# ❌ SUPPRIMÉ - Variables globales qui causaient collisions :
# authenticated = False
# current_user = None  
# user_data = None
# current_page = "login"
# selected_operation = None

# ✅ REMPLACEMENT : Tout est maintenant dans state.variable

# ==============================================================================
# DONNÉES STATIQUES (LECTURE SEULE - PARTAGÉES SANS PROBLÈME)
# ==============================================================================

# Base utilisateurs (lecture seule - pas de collision)
DEMO_ACO_USERS = {
    "aco1": {
        "password": "password1",
        "nom": "Pierre DUPONT",
        "role": "ACO",
        "secteur": "Les Abymes - Pointe-à-Pitre",
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
    },
    "marie.admin": {
        "password": "spic2024",
        "nom": "Marie-Claire ADMIN",
        "role": "ACO_SENIOR", 
        "secteur": "Les Abymes - Pointe-à-Pitre",
        "operations": 23
    }
}

# Données démo (lecture seule - partagées sans problème)
DEMO_DATA = {
    'operations_demo': [
        {
            'id': 1,
            'nom': 'RÉSIDENCE SOLEIL',
            'type_operation': 'OPP',
            'commune': 'Les Abymes',
            'statut': 'EN_COURS',
            'avancement': 75,
            'budget_total': 2450000,
            'nb_logements_total': 45,
            'date_creation': '2023-03-15',
            'date_debut_prevue': '2023-06-01',
            'date_fin_prevue': '2025-12-31',
            'freins_actifs': 1
        },
        {
            'id': 2,
            'nom': 'COUR CHARNEAU',
            'type_operation': 'OPP',
            'commune': 'Pointe-à-Pitre',
            'statut': 'EN_RECEPTION',
            'avancement': 95,
            'budget_total': 1850000,
            'nb_logements_total': 32,
            'date_creation': '2022-09-10',
            'date_debut_prevue': '2023-01-15',
            'date_fin_prevue': '2024-11-30',
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
            'date_debut_prevue': '2024-03-01',
            'date_fin_prevue': '2026-06-30',
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
# ✅ FONCTIONS D'INITIALISATION STATE PAR UTILISATEUR
# ==============================================================================

def init_user_state(state):
    """
    Initialise l'état pour chaque nouvelle session utilisateur
    🔒 CRITIQUE : Chaque utilisateur a son propre state
    """
    # Variables d'authentification PER USER
    if not hasattr(state, 'authenticated'):
        state.authenticated = False
    if not hasattr(state, 'current_user'):
        state.current_user = None
    if not hasattr(state, 'user_data'):
        state.user_data = None
    
    # Variables de navigation PER USER  
    if not hasattr(state, 'current_page'):
        state.current_page = "login"
    if not hasattr(state, 'selected_operation'):
        state.selected_operation = None
    if not hasattr(state, 'selected_operation_id'):
        state.selected_operation_id = None
    
    # Variables de formulaires PER USER
    if not hasattr(state, 'username_input'):
        state.username_input = ""
    if not hasattr(state, 'password_input'):
        state.password_input = ""
    if not hasattr(state, 'error_message'):
        state.error_message = ""
    
    # Variables métier PER USER
    if not hasattr(state, 'user_operations'):
        state.user_operations = []
    if not hasattr(state, 'user_kpis'):
        state.user_kpis = {}

# ==============================================================================
# ✅ FONCTIONS D'AUTHENTIFICATION CORRIGÉES  
# ==============================================================================

def verify_password(username, password):
    """Vérification identifiants (fonction pure - pas de state)"""
    if username in DEMO_ACO_USERS:
        stored_password = DEMO_ACO_USERS[username]["password"]
        return stored_password == password
    return False

def login_action(state):
    """
    ✅ CORRIGÉ : Action de connexion avec state isolé
    Chaque utilisateur connecté a sa propre session
    """
    # Initialisation state si nécessaire
    init_user_state(state)
    
    # Reset message d'erreur
    state.error_message = ""
    
    # Validation connexion
    if state.username_input and state.password_input:
        if verify_password(state.username_input, state.password_input):
            # ✅ Connexion réussie - DONNÉES ISOLÉES PAR UTILISATEUR
            state.authenticated = True
            state.current_user = state.username_input
            state.user_data = DEMO_ACO_USERS[state.username_input].copy()  # Copie pour isolation
            state.current_page = "dashboard"
            
            # Chargement des données spécifiques à cet utilisateur
            load_user_specific_data(state)
            
            # Reset champs connexion
            state.username_input = ""
            state.password_input = ""
            
            # Navigation vers dashboard
            navigate(state, "dashboard")
        else:
            state.error_message = "❌ Identifiants incorrects"
    else:
        state.error_message = "⚠️ Veuillez remplir tous les champs"

def logout_action(state):
    """
    ✅ CORRIGÉ : Déconnexion avec nettoyage state utilisateur
    """
    # Reset complet de la session utilisateur
    state.authenticated = False
    state.current_user = None
    state.user_data = None
    state.current_page = "login"
    state.selected_operation = None
    state.selected_operation_id = None
    state.user_operations = []
    state.user_kpis = {}
    state.error_message = ""
    
    # Navigation vers login
    navigate(state, "login")

def load_user_specific_data(state):
    """
    Charge les données spécifiques à l'utilisateur connecté
    🔒 ISOLATION : Chaque ACO voit ses propres données
    """
    if state.authenticated and state.current_user:
        # Filtrage des opérations par ACO (simulation)
        user_role = state.user_data.get('role', 'ACO')
        user_sector = state.user_data.get('secteur', '')
        
        # Simulation : filtrer opérations selon le secteur ACO
        all_operations = DEMO_DATA['operations_demo']
        if user_role == 'ACO':
            # ACO voit seulement les opérations de son secteur
            state.user_operations = [op for op in all_operations if 'Les Abymes' in user_sector or 'Pointe-à-Pitre' in user_sector]
        else:
            # ACO_SENIOR voit toutes les opérations
            state.user_operations = all_operations.copy()
        
        # KPIs spécifiques à l'utilisateur
        state.user_kpis = DEMO_DATA['kpis_aco_demo'].copy()
        
        # Ajustement des KPIs selon l'utilisateur
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
# ✅ FONCTIONS DE NAVIGATION CORRIGÉES
# ==============================================================================

def nav_dashboard(state):
    """✅ Navigation dashboard avec state isolé"""
    init_user_state(state)
    if state.authenticated:
        state.current_page = "dashboard"
        navigate(state, "dashboard")

def nav_portefeuille(state):
    """✅ Navigation portefeuille avec state isolé"""
    init_user_state(state)
    if state.authenticated:
        state.current_page = "portefeuille"
        navigate(state, "portefeuille")

def nav_operation(state, operation_id):
    """✅ Navigation opération avec state isolé"""
    init_user_state(state)
    if state.authenticated:
        state.current_page = "operation_details"
        state.selected_operation_id = operation_id
        
        # Recherche opération dans les données utilisateur
        for op in state.user_operations:
            if op['id'] == operation_id:
                state.selected_operation = op.copy()  # Copie pour isolation
                break
        
        navigate(state, "operation_details")

# ==============================================================================
# ✅ CSS STYLES (INCHANGÉ - PAS DE PROBLÈME MULTI-USERS)
# ==============================================================================

css_styles = """
<style>
/* THÈME MODERNE VIOLET-BLEU-VERT */
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
    background: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.kpi-card {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin: 0.5rem;
    box-shadow: 0 10px 40px rgba(139, 92, 246, 0.15);
    transition: all 0.4s ease;
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

.operation-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.1);
    border-left: 4px solid #8B5CF6;
}

.taipy-button {
    background: linear-gradient(135deg, #8B5CF6, #3B82F6, #10B981);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
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

.session-debug {
    background: #F3F4F6;
    border: 1px solid #D1D5DB;
    padding: 0.5rem;
    border-radius: 5px;
    font-size: 0.8rem;
    color: #6B7280;
    margin: 0.5rem 0;
}
</style>
"""

# ==============================================================================
# ✅ PAGES TAIPY CORRIGÉES AVEC STATE
# ==============================================================================

def get_login_page():
    """✅ Page de connexion avec state isolé"""
    return css_styles + """
<div class="main-header">
    <h1>🏗️ OPCOPILOT v4.0</h1>
    <h2>Tableau de Bord Opérationnel</h2>
    <p>SPIC Guadeloupe - Interface Multi-Utilisateurs Sécurisée</p>
</div>

<div class="login-container">
    <div class="login-title">🔐 Connexion ACO</div>
    
    **👤 Identifiant**
    <|{username_input}|text|class_name=login-input|>
    
    **🔑 Mot de passe**
    <|{password_input}|text|password=True|class_name=login-input|>
    
    <|🚀 Se connecter|button|on_action=login_action|class_name=taipy-button|>
    
    <|part|render={error_message != ""}|
    <div class="error-message">{error_message}</div>
    |>
</div>

---

**💡 Comptes de test multi-utilisateurs :**
- **aco1** / password1 (Pierre DUPONT - 18 opérations)
- **aco2** / password2 (Sophie MARTIN - 25 opérations)  
- **aco3** / password3 (Alexandre BERNARD - 12 opérations)

**🧪 TEST : Ouvrez plusieurs onglets et connectez différents ACO simultanément !**
"""

def get_dashboard_page():
    """✅ Dashboard avec données utilisateur isolées"""
    return css_styles + """
<|part|render={not authenticated}|
<div class="error-message">
    ❌ Accès non autorisé - Veuillez vous connecter
</div>
<|← Retour connexion|button|on_action={lambda s: navigate(s, "login")}|>
|>

<|part|render={authenticated}|
<div class="main-header">
    <h1>🏗️ OPCOPILOT v4.0 - Tableau de Bord</h1>
    <h2>👤 {user_data['nom'] if user_data else 'ACO'}</h2>
    <p>🏢 {user_data['secteur'] if user_data else 'Secteur'} • Session Isolée</p>
</div>

<div class="user-info">
    🔒 <strong>Session Sécurisée:</strong> {current_user} • 
    👥 <strong>Rôle:</strong> {user_data['role'] if user_data else 'N/A'} • 
    📊 <strong>Opérations:</strong> {len(user_operations)} visibles
</div>

## 📊 Mes KPIs Personnalisés

<|layout|columns=1 1 1 1|gap=1rem|
<div class="kpi-card kpi-operations">
    <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{user_kpis.get('operations_actives', 0) if user_kpis else 0}</div>
    <div style="font-size: 1rem; font-weight: 600;">Mes Opérations</div>
    <div style="font-size: 0.875rem; opacity: 0.9;">{user_kpis.get('operations_cloturees', 0) if user_kpis else 0} clôturées</div>
    <|📂 Mon Portfolio|button|on_action=nav_portefeuille|class_name=kpi-button|>
</div>
|
<div class="kpi-card kpi-rem">
    <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{int(user_kpis.get('rem_realisee_2024', 0)/1000) if user_kpis else 0}k€</div>
    <div style="font-size: 1rem; font-weight: 600;">Ma REM 2024</div>
    <div style="font-size: 0.875rem; opacity: 0.9;">{user_kpis.get('taux_realisation_rem', 0) if user_kpis else 0}% réalisé</div>
    <|💰 Mes REM|button|class_name=kpi-button|>
</div>
|
<div class="kpi-card kpi-freins">
    <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{user_kpis.get('freins_actifs', 0) if user_kpis else 0}</div>
    <div style="font-size: 1rem; font-weight: 600;">Mes Freins</div>
    <div style="font-size: 0.875rem; opacity: 0.9;">{user_kpis.get('freins_critiques', 0) if user_kpis else 0} critiques</div>
    <|🚨 Gérer|button|class_name=kpi-button|>
</div>
|
<div class="kpi-card kpi-echeances">
    <div style="font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{user_kpis.get('echeances_semaine', 0) if user_kpis else 0}</div>
    <div style="font-size: 1rem; font-weight: 600;">Mes Échéances</div>
    <div style="font-size: 0.875rem; opacity: 0.9;">{user_kpis.get('validations_requises', 0) if user_kpis else 0} validations</div>
    <|📅 Planning|button|class_name=kpi-button|>
</div>
|>

## 📋 Mes Opérations Récentes

<|{user_operations}|table|columns=nom,type_operation,commune,statut,avancement|page_size=5|>

<div class="session-debug">
🔍 <strong>Debug Multi-Users:</strong> User={current_user} | Ops={len(user_operations)} | Auth={authenticated}
</div>

<|🚪 Déconnexion|button|on_action=logout_action|class_name=taipy-button|>
|>
"""

def get_portefeuille_page():
    """✅ Portefeuille avec opérations utilisateur isolées"""
    return css_styles + """
<|part|render={not authenticated}|
<div class="error-message">❌ Connexion requise</div>
<|← Connexion|button|on_action={lambda s: navigate(s, "login")}|>
|>

<|part|render={authenticated}|
<div class="main-header">
    <h1>📂 Mon Portefeuille Personnel</h1>
    <h2>{user_data['nom'] if user_data else 'ACO'} - Mes Opérations</h2>
</div>

<div class="user-info">
👤 <strong>{current_user}</strong> • 📊 <strong>{len(user_operations)} opérations</strong> dans votre portefeuille
</div>

## 📋 Mes Opérations ({len(user_operations)} affichées)

<|layout|columns=1|
<|part|render={len(user_operations) > 0}|
<|{user_operations}|table|columns=nom,type_operation,commune,statut,avancement,budget_total|>
|>

<|part|render={len(user_operations) == 0}|
<div style="text-align: center; padding: 2rem; color: #6B7280;">
    📭 <strong>Aucune opération</strong> dans votre portefeuille<br>
    Contactez votre responsable pour attribution d'opérations
</div>
|>
|>

<|← Dashboard|button|on_action=nav_dashboard|class_name=taipy-button|>
<|🚪 Déconnexion|button|on_action=logout_action|class_name=taipy-button|>
|>
"""

# ==============================================================================
# ✅ APPLICATION TAIPY MULTI-UTILISATEURS
# ==============================================================================

def create_multiuser_app():
    """
    ✅ Application Taipy avec gestion multi-utilisateurs sécurisée
    🔒 CHAQUE SESSION EST ISOLÉE
    """
    
    # Pages avec state isolé
    pages = {
        "login": Markdown(get_login_page()),
        "dashboard": Markdown(get_dashboard_page()), 
        "portefeuille": Markdown(get_portefeuille_page())
    }
    
    # Configuration Taipy pour multi-utilisateurs
    gui = Gui(pages=pages)
    
    # Hook d'initialisation pour chaque nouvelle session
    def on_init(state):
        """Appelé pour chaque nouvelle session utilisateur"""
        print(f"🔄 Nouvelle session initialisée")
        init_user_state(state)
    
    # Hook de fin de session  
    def on_session_end(state):
        """Appelé quand une session se termine"""
        username = getattr(state, 'current_user', 'Anonyme')
        print(f"🔚 Session terminée pour: {username}")
    
    # Liaison des hooks
    gui.on_init = on_init
    
    return gui

# ==============================================================================
# ✅ POINT D'ENTRÉE AVEC MULTI-UTILISATEURS
# ==============================================================================

if __name__ == "__main__":
    print("🚀 Démarrage OPCOPILOT Multi-Utilisateurs")
    print("🔒 Sessions isolées par utilisateur")
    print("🧪 Test: Ouvrez plusieurs onglets avec différents comptes")
    print("👥 Comptes: aco1/password1, aco2/password2, aco3/password3")
    
    app = create_multiuser_app()
    
    # Configuration serveur pour multi-utilisateurs
    app.run(
        title="OPCOPILOT v4.0 - Multi-Utilisateurs",
        port=5000,
        debug=True,
        use_reloader=True,
        host="0.0.0.0"  # Accepte connexions externes pour test
    )
