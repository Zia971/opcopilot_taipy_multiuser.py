"""
OPCOPILOT v4.0 - Conversion Taipy complète
Application de gestion d'opérations immobilières SPIC Guadeloupe
Convertie de Streamlit vers Taipy GUI
Configurée pour déploiement Railway
"""

from taipy.gui import Gui, Markdown, navigate
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os

# ==============================================================================
# VARIABLES D'ÉTAT GLOBALES
# ==============================================================================

# Variables d'authentification
username = ""
password = ""
message = ""
authenticated = False
user_data = None
current_page = "login"

# Variables de navigation
selected_operation_id = None
selected_operation = None
active_tab = "timeline"

# Variables de filtres
filtre_type = "Tous"
filtre_statut = "Tous"
filtre_commune = "Toutes"

# Variables de formulaires
nom_operation = ""
type_operation_nouveau = "OPP"
commune_nouvelle = "Les Abymes"

# ==============================================================================
# DONNÉES DE DÉMONSTRATION
# ==============================================================================

# Utilisateurs ACO (repris du code Streamlit)
DEMO_ACO_USERS = {
    "aco1": {"password": "password1", "nom": "Pierre DUPONT", "role": "ACO", "secteur": "Les Abymes - Pointe-à-Pitre", "operations": 18},
    "aco2": {"password": "password2", "nom": "Sophie MARTIN", "role": "ACO_SENIOR", "secteur": "Basse-Terre - Sainte-Anne", "operations": 25},
    "aco3": {"password": "password3", "nom": "Alexandre BERNARD", "role": "ACO", "secteur": "Baie-Mahault - Lamentin", "operations": 12},
    "marie.admin": {"password": "spic2024", "nom": "Marie-Claire ADMIN", "role": "ACO_SENIOR", "secteur": "Les Abymes - Pointe-à-Pitre", "operations": 23},
    "jean.martin": {"password": "aco123", "nom": "Jean MARTIN", "role": "ACO", "secteur": "Basse-Terre - Sainte-Anne", "operations": 15},
    "admin": {"password": "admin2024", "nom": "Administrateur SPIC", "role": "ADMIN", "secteur": "Tous secteurs", "operations": 0}
}

# Données de démonstration des opérations
DEMO_OPERATIONS = [
    {
        "id": 1,
        "nom": "COUR CHARNEAU",
        "type_operation": "OPP",
        "commune": "Les Abymes",
        "nb_logements_total": 40,
        "budget_total": 2400000,
        "avancement": 75,
        "statut": "EN_COURS",
        "date_creation": "2023-01-15",
        "date_fin_prevue": "2024-12-31",
        "freins_actifs": 2,
        "aco_responsable": "Pierre DUPONT"
    },
    {
        "id": 2,
        "nom": "VEFA BELCOURT",
        "type_operation": "VEFA",
        "commune": "Pointe-à-Pitre",
        "nb_logements_total": 25,
        "budget_total": 1800000,
        "avancement": 60,
        "statut": "EN_COURS",
        "date_creation": "2023-06-01",
        "date_fin_prevue": "2024-10-30",
        "freins_actifs": 1,
        "aco_responsable": "Sophie MARTIN"
    },
    {
        "id": 3,
        "nom": "RÉSIDENCE SOLEIL",
        "type_operation": "OPP",
        "commune": "Basse-Terre",
        "nb_logements_total": 60,
        "budget_total": 3200000,
        "avancement": 90,
        "statut": "EN_RECEPTION",
        "date_creation": "2022-09-01",
        "date_fin_prevue": "2024-11-15",
        "freins_actifs": 0,
        "aco_responsable": "Alexandre BERNARD"
    }
]

# KPIs de démonstration
DEMO_KPIS = {
    "operations_actives": 23,
    "operations_cloturees": 5,
    "rem_realisee_2024": 485000,
    "rem_prevue_2024": 620000,
    "taux_realisation_rem": 78,
    "freins_actifs": 3,
    "freins_critiques": 2,
    "echeances_semaine": 5,
    "validations_requises": 12
}

# Alertes de démonstration
DEMO_ALERTES = [
    {"operation": "COUR CHARNEAU", "type": "CRITIQUE", "message": "Retard 5 jours sur réception provisoire", "action": "Relancer MOE immédiatement"},
    {"operation": "VEFA BELCOURT", "type": "WARNING", "message": "Validation promoteur en attente", "action": "RDV programmé cette semaine"},
    {"operation": "RÉSIDENCE SOLEIL", "type": "INFO", "message": "Phase Travaux en cours - bon avancement", "action": "Suivi hebdomadaire maintenu"}
]

# ==============================================================================
# FONCTIONS D'AUTHENTIFICATION
# ==============================================================================

def on_login(state):
    """Gestion de la connexion utilisateur"""
    if state.username and state.password:
        user = DEMO_ACO_USERS.get(state.username)
        if user and user["password"] == state.password:
            state.authenticated = True
            state.user_data = user
            state.current_page = "dashboard"
            state.message = f"✅ Connexion réussie ! Bienvenue {user['nom']}"
            # Navigation directe dans Taipy
            return "dashboard"
        else:
            state.message = "❌ Identifiants incorrects."
    else:
        state.message = "⚠️ Veuillez remplir tous les champs."
    return None

def on_logout(state):
    """Déconnexion utilisateur"""
    state.authenticated = False
    state.user_data = None
    state.current_page = "login"
    state.username = ""
    state.password = ""
    state.message = ""
    return "login"

# ==============================================================================
# FONCTIONS DE NAVIGATION
# ==============================================================================

def on_navigate_dashboard(state):
    state.current_page = "dashboard"
    return "dashboard"

def on_navigate_portefeuille(state):
    state.current_page = "portefeuille"
    return "portefeuille"

def on_navigate_operation(state):
    state.current_page = "operation_details"
    return "operation_details"

def on_navigate_creation(state):
    state.current_page = "creation_operation"
    return "creation_operation"

def on_select_operation(state, var_name, payload):
    """Sélection d'une opération depuis la liste"""
    if payload and "args" in payload and len(payload["args"]) > 0:
        operation_id = payload["args"][0]
        state.selected_operation_id = operation_id
        # Recherche de l'opération dans les données de démo
        for op in DEMO_OPERATIONS:
            if op["id"] == operation_id:
                state.selected_operation = op
                break
        state.current_page = "operation_details"
        return "operation_details"
    return None

# ==============================================================================
# GÉNÉRATION DE GRAPHIQUES
# ==============================================================================

def create_activite_chart():
    """Graphique d'activité mensuelle"""
    mois = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct']
    rem_mensuelle = [45000, 52000, 48000, 55000, 49000, 61000, 58000, 47000, 53000, 62000]
    operations_actives = [18, 19, 20, 22, 21, 23, 24, 23, 22, 23]
    
    fig = go.Figure()
    
    # REM mensuelle
    fig.add_trace(go.Scatter(
        x=mois,
        y=rem_mensuelle,
        mode='lines+markers',
        name='REM Mensuelle (€)',
        yaxis='y',
        line=dict(color='#8B5CF6', width=3),
        marker=dict(size=8, color='#8B5CF6')
    ))
    
    # Opérations actives
    fig.add_trace(go.Scatter(
        x=mois,
        y=operations_actives,
        mode='lines+markers',
        name='Opérations Actives',
        yaxis='y2',
        line=dict(color='#10B981', width=3),
        marker=dict(size=8, color='#10B981')
    ))
    
    fig.update_layout(
        title="Évolution Activité 2024",
        xaxis=dict(title="Mois"),
        yaxis=dict(title="REM (€)", side="left"),
        yaxis2=dict(title="Nb Opérations", side="right", overlaying="y"),
        height=450,
        hovermode='x unified',
        plot_bgcolor='rgba(139, 92, 246, 0.02)',
        paper_bgcolor='#f9fafb'
    )
    
    return fig

def create_timeline_chart(operation):
    """Timeline horizontale pour une opération"""
    if not operation:
        return go.Figure()
    
    # Phases de démonstration
    phases = [
        {"nom": "Faisabilité", "debut": "2023-01-15", "fin": "2023-04-15", "statut": "VALIDEE"},
        {"nom": "Esquisse", "debut": "2023-04-16", "fin": "2023-06-15", "statut": "VALIDEE"},
        {"nom": "Avant-Projet", "debut": "2023-06-16", "fin": "2023-10-15", "statut": "VALIDEE"},
        {"nom": "Permis Construire", "debut": "2023-10-16", "fin": "2024-04-15", "statut": "EN_COURS"},
        {"nom": "Consultation", "debut": "2024-04-16", "fin": "2024-07-15", "statut": "EN_ATTENTE"},
        {"nom": "Travaux", "debut": "2024-07-16", "fin": "2025-01-15", "statut": "NON_DEMARREE"},
        {"nom": "Réception", "debut": "2025-01-16", "fin": "2025-02-15", "statut": "NON_DEMARREE"},
        {"nom": "Livraison", "debut": "2025-02-16", "fin": "2025-03-15", "statut": "NON_DEMARREE"}
    ]
    
    fig = go.Figure()
    
    couleurs = {"VALIDEE": "#10B981", "EN_COURS": "#3B82F6", "EN_ATTENTE": "#F59E0B", "NON_DEMARREE": "#9E9E9E"}
    
    for i, phase in enumerate(phases):
        # Barre de progression pour chaque phase
        debut = pd.to_datetime(phase["debut"])
        fin = pd.to_datetime(phase["fin"])
        couleur = couleurs.get(phase["statut"], "#9E9E9E")
        
        fig.add_trace(go.Bar(
            x=[fin - debut],
            y=[phase["nom"]],
            base=[debut],
            orientation='h',
            name=phase["statut"],
            marker_color=couleur,
            text=f"{phase['nom']} ({phase['statut']})",
            textposition='middle center',
            showlegend=i == 0
        ))
    
    fig.update_layout(
        title=f"Timeline - {operation.get('nom', 'Opération')}",
        xaxis_title="Période",
        yaxis_title="Phases",
        height=600,
        showlegend=True,
        barmode='overlay'
    )
    
    return fig

# ==============================================================================
# DÉFINITION DES PAGES TAIPY
# ==============================================================================

# Page de connexion
login_page = """
<|layout|columns=1 1 1|gap=30px|
<|part|>
<|part|
# 🏗️ OPCOPILOT v4.0
## Tableau de Bord Opérationnel
SPIC Guadeloupe - Interface de Gestion d'Opérations Immobilières

---

### 🔐 Connexion ACO
Accédez à votre espace de travail sécurisé

<|{message}|text|>

<|layout|columns=1|gap=20px|
<|{username}|input|label=👤 Identifiant|placeholder=Saisissez votre identifiant ACO|>
<|{password}|input|label=🔑 Mot de passe|password=True|placeholder=Saisissez votre mot de passe|>
<|Se connecter|button|on_action=on_login|>
|>

**Comptes de test disponibles :**
- `aco1` / `password1` (Pierre DUPONT)
- `aco2` / `password2` (Sophie MARTIN) 
- `admin` / `admin2024` (Administrateur)
|>
<|part|>
|>
"""

# Page dashboard
dashboard_page = """
<|layout|columns=1|gap=20px|
<|part|
# 🏗️ OPCOPILOT v4.0 - Tableau de Bord Opérationnel
**Mon Tableau de Bord - {user_data['nom'] if user_data else 'ACO'}**  
Interface de Gestion d'Opérations • SPIC Guadeloupe

<|layout|columns=1 1 1 1|gap=15px|
<|part|class_name=kpi-card|
### 📁 Opérations Actives
**{DEMO_KPIS['operations_actives']}**  
{DEMO_KPIS['operations_cloturees']} clôturées
<|📂 Voir Portfolio|button|on_action=on_navigate_portefeuille|>
|>
<|part|class_name=kpi-card|
### 💰 REM Réalisée 2024
**{DEMO_KPIS['rem_realisee_2024']/1000:.0f}k€**  
{DEMO_KPIS['taux_realisation_rem']}% / {DEMO_KPIS['rem_prevue_2024']/1000:.0f}k€ prévue
<|💰 Analyse REM|button|>
|>
<|part|class_name=kpi-card|
### ⚠️ Freins Actifs
**{DEMO_KPIS['freins_actifs']}**  
{DEMO_KPIS['freins_critiques']} critiques
<|🚨 Gérer Freins|button|>
|>
<|part|class_name=kpi-card|
### 📅 Échéances Semaine
**{DEMO_KPIS['echeances_semaine']}**  
{DEMO_KPIS['validations_requises']} validations requises
<|📅 Planning|button|>
|>
|>

---

## 🚨 Alertes et Actions Prioritaires

<|layout|columns=1 1|gap=20px|
<|part|
### Alertes Critiques
**🏗️ COUR CHARNEAU** - CRITIQUE  
Retard 5 jours sur réception provisoire  
*Action: Relancer MOE immédiatement*

**🏠 VEFA BELCOURT** - WARNING  
Validation promoteur en attente  
*Action: RDV programmé cette semaine*

**🏗️ RÉSIDENCE SOLEIL** - INFO  
Phase Travaux en cours - bon avancement  
*Action: Suivi hebdomadaire maintenu*
|>
<|part|
### Actions Réalisées Aujourd'hui
✅ DGD validé - RÉSIDENCE SOLEIL  
✅ Phase ESQ terminée - COUR CHARNEAU  
✅ MED envoyé - MANDAT ÉCOLE  
✅ REM T3 saisi - 3 opérations  
✅ Timeline mise à jour - VEFA BELCOURT  
|>
|>

---

## 📈 Activité Mensuelle
<|{create_activite_chart()}|chart|>

<|Déconnexion|button|on_action=on_logout|>
|>
"""

# Page portefeuille
portefeuille_page = """
<|layout|columns=1|gap=20px|
<|part|
# 📂 Mon Portefeuille - {user_data['nom'] if user_data else 'ACO'}

<|layout|columns=1 1 1 1|gap=15px|
<|{filtre_type}|selector|lov=Tous;OPP;VEFA;MANDAT_ETUDES|label=Type Opération|>
<|{filtre_statut}|selector|lov=Tous;EN_MONTAGE;EN_COURS;EN_RECEPTION;CLOTUREE|label=Statut|>
<|{filtre_commune}|selector|lov=Toutes;Les Abymes;Pointe-à-Pitre;Basse-Terre;Sainte-Anne|label=Commune|>
<|➕ Nouvelle Opération|button|on_action=on_navigate_creation|>
|>

---

## 📋 Mes Opérations ({len(DEMO_OPERATIONS)} affichées)

<|{DEMO_OPERATIONS}|table|columns=nom|type_operation|commune|nb_logements_total|budget_total|avancement|statut|on_action=on_select_operation|>

<|← Retour Dashboard|button|on_action=on_navigate_dashboard|>
|>
"""

# Page détails opération
operation_details_page = """
<|layout|columns=1|gap=20px|
<|part|
# 🏗️ {selected_operation['nom'] if selected_operation else 'Opération'} - {selected_operation['type_operation'] if selected_operation else 'OPP'}

**📍 {selected_operation['commune'] if selected_operation else 'Commune'}** • {selected_operation['nb_logements_total'] if selected_operation else 0} logements • **Budget:** {selected_operation['budget_total'] if selected_operation else 0:,} € • **Avancement:** {selected_operation['avancement'] if selected_operation else 0}%

<|← Retour au Portefeuille|button|on_action=on_navigate_portefeuille|>

---

## 📅 Timeline Horizontale - Gestion des Phases

<|{create_timeline_chart(selected_operation)}|chart|>

### 🔧 Gestion des Phases

<|layout|columns=1 1 1 1|gap=15px|
<|➕ Ajouter Phase|button|>
<|✏️ Modifier Phase|button|>
<|⚠️ Signaler Frein|button|>
<|📊 Exporter Planning|button|>
|>

---

## 📋 Modules Intégrés

**💰 Module REM** - Suivi Trimestriel (En développement)  
**📝 Module Avenants** - Gestion des modifications (En développement)  
**⚖️ Module MED** - Mise en demeure automatisée (En développement)  
**🔌 Module Concessionnaires** - Suivi des réseaux (En développement)  
**📊 Module DGD** - Décompte Général Définitif (En développement)  
**🛡️ Module GPA** - Garantie Parfait Achèvement (En développement)  
**✅ Module Clôture** - Finalisation Opération (En développement)  

|>
"""

# Page création opération
creation_page = """
<|layout|columns=1|gap=20px|
<|part|
# ➕ Nouvelle Opération

## 📝 Informations Générales

<|layout|columns=1 1|gap=20px|
<|part|
<|{nom_operation}|input|label=Nom Opération *|placeholder=Ex: RÉSIDENCE LES JARDINS|>
<|{type_operation_nouveau}|selector|lov=OPP;VEFA;MANDAT_ETUDES;MANDAT_REALISATION|label=Type Opération *|>
<|{commune_nouvelle}|selector|lov=Les Abymes;Pointe-à-Pitre;Basse-Terre;Sainte-Anne;Le Gosier;Petit-Bourg|label=Commune *|>
|>
<|part|
**ACO Responsable:** {user_data['nom'] if user_data else 'ACO'}

**Description du type d'opération:**  
- **OPP:** Construction neuve de logements sociaux (8 phases)  
- **VEFA:** Acquisition de logements sur plan (6 phases)  
- **MANDAT_ETUDES:** Mission d'études préalables  
- **MANDAT_REALISATION:** Mission de réalisation complète  
|>
|>

<|layout|columns=1 1|gap=15px|
<|✅ Créer l'Opération|button|>
<|← Annuler|button|on_action=on_navigate_portefeuille|>
|>
|>
"""

# ==============================================================================
# GESTION DES PAGES ET NAVIGATION
# ==============================================================================

def on_change_current_page(state, var_name, var_value):
    """Gestionnaire de changement de page"""
    if var_value == "dashboard" and not state.authenticated:
        return "login"
    return var_value

# ==============================================================================
# PAGES ET CONFIGURATION
# ==============================================================================

pages = {
    "/": login_page,
    "login": login_page,
    "dashboard": dashboard_page,
    "portefeuille": portefeuille_page,
    "operation_details": operation_details_page,
    "creation_operation": creation_page
}

# CSS modernisé (adapté de Streamlit)
css_styles = """
.taipy-gui {
    font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    background-color: #F9FAFB !important;
}

.kpi-card {
    background: white !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    text-align: center !important;
    margin: 0.5rem !important;
    box-shadow: 0 10px 40px rgba(139, 92, 246, 0.15) !important;
    transition: all 0.4s ease !important;
    cursor: pointer !important;
}

.kpi-card:hover {
    box-shadow: 0 20px 60px rgba(139, 92, 246, 0.25) !important;
    transform: translateY(-5px) scale(1.02) !important;
}

.taipy-button {
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 50%, #10B981 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.25) !important;
}

.taipy-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 40px rgba(139, 92, 246, 0.35) !important;
}

/* Messages d'état */
.taipy-text {
    padding: 1rem !important;
    border-radius: 8px !important;
    margin: 1rem 0 !important;
}
"""

# ==============================================================================
# LANCEMENT DE L'APPLICATION
# ==============================================================================

if __name__ == "__main__":
    # Configuration pour Railway
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    
    # Configuration Taipy
    gui = Gui(pages=pages)
    
    # Application du CSS
    gui.add_css_file("custom.css", css_styles)
    
    print(f"🚀 Démarrage OPCOPILOT v4.0 sur {host}:{port}")
    print("📋 Comptes de test:")
    print("   - aco1 / password1 (Pierre DUPONT)")
    print("   - aco2 / password2 (Sophie MARTIN)")
    print("   - admin / admin2024 (Administrateur)")
    
    gui.run(
        host=host,
        port=port,
        debug=False,
        title="OPCOPILOT v4.0 - SPIC Guadeloupe",
        dark_mode=False,
        margin="1rem",
        run_server=True,
        allow_unsafe_werkzeug=True
    )
