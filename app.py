# app.py - Application Streamlit pour E-Commerce Analytics
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide"
)

# Titre
st.title("🛍️ E-Commerce Analytics Dashboard")
st.markdown("*Application de collecte et analyse de données e-commerce - TP INF232 EC2*")
st.markdown("---")

# Importer les modules
from collecteur.amazon import CollecteurAmazon
from collecteur.fnac import CollecteurFnac
from collecteur.darty import CollecteurDarty
from analyse.stats import AnalyseEcommerce
from analyse.alertes import SystemeAlertes
from config import PRODUITS

# Sidebar
with st.sidebar:
    st.header("⚙️ Contrôles")
    
    if st.button("🔄 Lancer la collecte", type="primary", use_container_width=True):
        st.session_state['run_analysis'] = True
        st.rerun()
    
    st.markdown("---")
    st.header("📊 Filtres")
    
    if 'df' in st.session_state:
        sites_dispo = st.session_state['df']['site'].unique()
        sites_selection = st.multiselect("Sites", sites_dispo, default=list(sites_dispo))
        
        produits_dispo = st.session_state['df']['produit'].unique()
        produits_selection = st.multiselect("Produits", produits_dispo, default=list(produits_dispo))
    
    st.markdown("---")
    st.caption(f"⏰ {datetime.now().strftime('%H:%M:%S')}")

# Fonction de collecte
def collecter_et_analyser():
    with st.spinner("🔄 Collecte des données en cours..."):
        collecteurs = [
            CollecteurAmazon(),
            CollecteurFnac(),
            CollecteurDarty()
        ]
        
        toutes_donnees = []
        progress_bar = st.progress(0)
        
        for i, collecteur in enumerate(collecteurs):
            st.info(f"📦 Collecte sur {collecteur.nom_site}...")
            donnees = collecteur.collecter_tous_produits(PRODUITS)
            toutes_donnees.extend(donnees)
            progress_bar.progress((i + 1) / len(collecteurs))
        
        df = pd.DataFrame(toutes_donnees)
        analyse = AnalyseEcommerce(df)
        rapport = analyse.analyse_prix_complete()
        anomalies = analyse.detection_anomalies()
        alertes = SystemeAlertes.check_bonnes_affaires(df)
        
        st.session_state['df'] = df
        st.session_state['rapport'] = rapport
        st.session_state['anomalies'] = anomalies
        st.session_state['alertes'] = alertes
        st.session_state['last_update'] = datetime.now()
        
        return df, rapport, anomalies, alertes

# Interface principale
col1, col2, col3, col4 = st.columns(4)

if 'df' not in st.session_state:
    st.info("👈 Cliquez sur **'Lancer la collecte'** dans la barre latérale pour commencer")
    
    with col1:
        st.metric("🚀 Statut", "Prêt")
    with col2:
        st.metric("🛒 Sites", "3")
    with col3:
        st.metric("📦 Produits", len(PRODUITS))
    with col4:
        st.metric("📊 Version", "1.0")
else:
    # Appliquer les filtres
    df_filtered = st.session_state['df']
    
    if 'sites_selection' in locals() and sites_selection:
        df_filtered = df_filtered[df_filtered['site'].isin(sites_selection)]
    if 'produits_selection' in locals() and produits_selection:
        df_filtered = df_filtered[df_filtered['produit'].isin(produits_selection)]
    
    # Métriques
    prix_moyen = df_filtered['prix'].mean()
    nb_promos = df_filtered['promotion'].notna().sum()
    dispo_rate = df_filtered['disponible'].mean() * 100
    nb_alertes = len(st.session_state.get('alertes', []))
    
    with col1:
        st.metric("💰 Prix moyen", f"{prix_moyen:.0f}€")
    with col2:
        st.metric("🏷️ Promotions", nb_promos)
    with col3:
        st.metric("✅ Disponibilité", f"{dispo_rate:.0f}%")
    with col4:
        st.metric("🔥 Alertes", nb_alertes, delta="🔥" if nb_alertes > 0 else None)
    
    st.markdown("---")
    
    # Onglets
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Prix par produit", "🏪 Comparaison sites", "🔥 Alertes", "📈 Analyses"])
    
    with tab1:
        st.subheader("Comparaison des prix par produit")
        
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
        
        st.subheader("Tableau des prix")
        tableau_prix = df_filtered.pivot_table(
            index='produit', 
            columns='site', 
            values='prix', 
            aggfunc='first'
        )
        st.dataframe(tableau_prix, use_container_width=True)
    
    with tab2:
        st.subheader("Distribution des prix par site")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.box(df_filtered, x='site', y='prix', color='site',
                        title="Distribution des prix")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            dispo_data = df_filtered.groupby('site')['disponible'].mean().reset_index()
            fig = px.bar(dispo_data, x='site', y='disponible', color='site',
                        title="Taux de disponibilité", text_auto='.0%')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Matrice concurrentielle")
        matrice = st.session_state['rapport']['statistiques_globales']
        st.dataframe(matrice, use_container_width=True)
    
    with tab3:
        st.subheader("🔥 Bonnes affaires détectées")
        
        alertes = st.session_state.get('alertes', [])
        if alertes:
            for alerte in alertes:
                with st.container():
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        st.markdown(f"**{alerte['produit']}**")
                        st.caption(f"🏪 {alerte['site']}")
                    with c2:
                        st.markdown(f"~~{alerte['prix_original']}€~~")
                        st.markdown(f"**{alerte['prix_actuel']}€**")
                    with c3:
                        st.markdown(f"💰 Économie : **{alerte['economie']}€**")
                        st.success(alerte['promotion'])
                    st.markdown("---")
        else:
            st.info("Aucune bonne affaire détectée pour le moment")
        
        st.subheader("⚠️ Ruptures de stock")
        ruptures = SystemeAlertes.check_rupture(df_filtered)
        if ruptures is not None and not ruptures.empty:
            st.warning(f"{len(ruptures)} produits en rupture")
            st.dataframe(ruptures)
        else:
            st.success("Tous les produits sont disponibles")
    
    with tab4:
        st.subheader("Statistiques détaillées")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🏆 Meilleurs prix par produit**")
            meilleurs_prix = st.session_state['rapport']['meilleur_prix_par_produit']
            st.dataframe(meilleurs_prix, use_container_width=True)
        
        with col2:
            st.markdown("**📈 Volatilité des prix**")
            volatilite = st.session_state['rapport']['volatilite_prix'].reset_index()
            if not volatilite.empty:
                volatilite.columns = ['Produit', 'Écart-type']
                st.dataframe(volatilite, use_container_width=True)
        
        st.markdown("**⚠️ Anomalies détectées**")
        anomalies = st.session_state.get('anomalies', {})
        if anomalies:
            for produit, anomalies_data in anomalies.items():
                with st.expander(f"🔍 {produit}"):
                    st.dataframe(anomalies_data)
        else:
            st.success("✅ Aucune anomalie détectée")

# Footer
st.markdown("---")
st.caption(f"© TP INF232 EC2 - Application E-Commerce Analytics | Dernière mise à jour : {st.session_state.get('last_update', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if 'last_update' in st.session_state else 'Non lancée'}")
