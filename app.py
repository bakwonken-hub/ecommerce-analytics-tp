# app.py - Interface web pour Streamlit Cloud
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys

# Configuration de la page
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide"
)

# Titre
st.title("🛍️ E-Commerce Analytics Dashboard")
st.markdown("*Application de collecte et analyse de données e-commerce*")
st.markdown("---")

# Importer les modules existants (adaptés pour fonctionner en ligne)
from collecteur.amazon import CollecteurAmazon
from collecteur.fnac import CollecteurFnac
from collecteur.darty import CollecteurDarty
from analyse.stats import AnalyseEcommerce
from analyse.alertes import SystemeAlertes
from config import PRODUITS

# Sidebar pour les contrôles
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    if st.button("🔄 Lancer la collecte des données", type="primary"):
        st.session_state['run_analysis'] = True
        st.rerun()
    
    st.markdown("---")
    st.header("📊 Filtres")
    
    # Filtres à appliquer après analyse
    if 'df' in st.session_state:
        sites_dispo = st.session_state['df']['site'].unique()
        sites_selection = st.multiselect("Sites", sites_dispo, default=sites_dispo)
        
        produits_dispo = st.session_state['df']['produit'].unique()
        produits_selection = st.multiselect("Produits", produits_dispo, default=produits_dispo)
    
    st.markdown("---")
    st.caption(f"Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")

# Fonction principale de collecte et analyse
def collecter_et_analyser():
    with st.spinner("🔄 Collecte des données en cours..."):
        # 1. Collecte
        collecteurs = [
            CollecteurAmazon(),
            CollecteurFnac(),
            CollecteurDarty()
        ]
        
        toutes_donnees = []
        progress_bar = st.progress(0)
        for i, collecteur in enumerate(collecteurs):
            st.info(f"Collecte sur {collecteur.nom_site}...")
            donnees = collecteur.collecter_tous_produits(PRODUITS)
            toutes_donnees.extend(donnees)
            progress_bar.progress((i + 1) / len(collecteurs))
        
        # 2. Conversion en DataFrame
        df = pd.DataFrame(toutes_donnees)
        
        # 3. Analyse
        analyse = AnalyseEcommerce(df)
        rapport = analyse.analyse_prix_complete()
        anomalies = analyse.detection_anomalies()
        alertes = SystemeAlertes.check_bonnes_affaires(df)
        
        # Stocker dans session state
        st.session_state['df'] = df
        st.session_state['rapport'] = rapport
        st.session_state['anomalies'] = anomalies
        st.session_state['alertes'] = alertes
        st.session_state['last_update'] = datetime.now()
        
        return df, rapport, anomalies, alertes

# Interface principale
col1, col2, col3 = st.columns(3)

if 'df' not in st.session_state:
    st.info("👈 Cliquez sur 'Lancer la collecte' dans la barre latérale pour commencer")
    
    with col1:
        st.metric("🚀 Prêt à collecter", "Cliquez sur le bouton")
    with col2:
        st.metric("🛒 Sites surveillés", "3")
    with col3:
        st.metric("📦 Produits", len(PRODUITS))
    
else:
    # Appliquer les filtres
    df_filtered = st.session_state['df']
    if 'sites_selection' in locals() and sites_selection:
        df_filtered = df_filtered[df_filtered['site'].isin(sites_selection)]
    if 'produits_selection' in locals() and produits_selection:
        df_filtered = df_filtered[df_filtered['produit'].isin(produits_selection)]
    
    # Affichage des métriques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        prix_moyen = df_filtered['prix'].mean()
        st.metric("💰 Prix moyen", f"{prix_moyen:.0f}€", 
                  delta=f"{prix_moyen - st.session_state.get('prev_prix', prix_moyen):.0f}€")
    
    with col2:
        nb_promos = df_filtered['promotion'].notna().sum()
        st.metric("🏷️ Promos actives", nb_promos)
    
    with col3:
        dispo_rate = df_filtered['disponible'].mean() * 100
        st.metric("✅ Disponibilité", f"{dispo_rate:.0f}%")
    
    with col4:
        if 'alertes' in st.session_state and st.session_state['alertes']:
            st.metric("🔥 Bonnes affaires", len(st.session_state['alertes']), delta="🔥")
        else:
            st.metric("🔥 Bonnes affaires", 0)
    
    st.markdown("---")
    
    # Onglets pour différentes vues
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Prix par produit", "🏪 Comparaison sites", "🔥 Alertes", "📈 Analyses"])
    
    with tab1:
        st.subheader("Comparaison des prix par produit")
        
        # Créer un graphique Plotly
        fig = px.bar(
            df_filtered, 
            x='produit', 
            y='prix', 
            color='site', 
            barmode='group',
            title="Prix par produit et par site",
            labels={'prix': 'Prix (€)', 'produit': 'Produit'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des prix
        st.dataframe(
            df_filtered.pivot_table(index='produit', columns='site', values='prix', aggfunc='first'),
            use_container_width=True
        )
    
    with tab2:
        st.subheader("Distribution des prix par site")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.box(df_filtered, x='site', y='prix', color='site', 
                        title="Distribution des prix")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Disponibilité
            dispo_data = df_filtered.groupby('site')['disponible'].mean().reset_index()
            fig = px.bar(dispo_data, x='site', y='disponible', color='site',
                        title="Taux de disponibilité", text_auto='.0%')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("🔥 Alertes bonnes affaires")
        
        if st.session_state['alertes']:
            for alerte in st.session_state['alertes']:
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{alerte['produit']}**")
                        st.caption(f"chez {alerte['site']}")
                    with col2:
                        st.markdown(f"~~{alerte['prix_original']}€~~")
                        st.markdown(f"**{alerte['prix_actuel']}€**")
                    with col3:
                        st.markdown(f"💰 Économie : **{alerte['economie']}€**")
                        st.success(alerte['promotion'])
                    st.markdown("---")
        else:
            st.info("Aucune alerte pour le moment")
    
    with tab4:
        st.subheader("Statistiques détaillées")
        
        if 'rapport' in st.session_state:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Meilleurs prix par produit**")
                meilleurs_prix = st.session_state['rapport']['meilleur_prix_par_produit']
                st.dataframe(meilleurs_prix, use_container_width=True)
            
            with col2:
                st.markdown("**📈 Volatilité des prix**")
                volatilite = st.session_state['rapport']['volatilite_prix'].reset_index()
                volatilite.columns = ['Produit', 'Écart-type']
                st.dataframe(volatilite, use_container_width=True)
            
            st.markdown("**⚠️ Anomalies détectées**")
            if st.session_state['anomalies']:
                for produit, anomalies_data in st.session_state['anomalies'].items():
                    with st.expander(f"Anomalies pour {produit}"):
                        st.dataframe(anomalies_data)
            else:
                st.success("Aucune anomalie détectée")

# Footer
st.markdown("---")
st.caption(f"© TP INF232 EC2 - Application développée avec Streamlit | Dernière collecte : {st.session_state.get('last_update', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if 'last_update' in st.session_state else 'Non encore lancée'}")