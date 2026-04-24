#!/usr/bin/env python3
import pandas as pd
import logging
import json
from datetime import datetime
from pathlib import Path

from collecteur import CollecteurAmazon, CollecteurFnac, CollecteurDarty
from analyse.stats import AnalyseEcommerce
from analyse.alertes import SystemeAlertes
from visualisation.graphiques import VisualisateurEcommerce
from config import PRODUITS

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ecommerce_tp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def creer_dossiers():
    """Crée l'arborescence des dossiers"""
    dossiers = ['data/raw', 'data/processed', 'outputs/graphiques', 'outputs/rapports']
    for dossier in dossiers:
        Path(dossier).mkdir(parents=True, exist_ok=True)

def sauvegarder_json(data, fichier):
    """Sauvegarde robuste en JSON"""
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, pd.Series):
                return obj.to_dict()
            if isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient='records')
            return super().default(obj)
    
    with open(fichier, 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=NumpyEncoder, indent=2, ensure_ascii=False)

def main():
    logger.info("="*60)
    logger.info("DÉMARRAGE DE L'APPLICATION E-COMMERCE ANALYTICS")
    logger.info("="*60)
    
    # 1. Création des dossiers
    creer_dossiers()
    
    # 2. Collecte des données (robustesse)
    logger.info("\n[1/5] Lancement de la collecte multi-sites...")
    
    collecteurs = [
        CollecteurAmazon(),
        CollecteurFnac(),
        CollecteurDarty()
    ]
    
    toutes_donnees = []
    for collecteur in collecteurs:
        logger.info(f"\nCollecte sur {collecteur.nom_site}...")
        donnees = collecteur.collecter_tous_produits(PRODUITS)
        toutes_donnees.extend(donnees)
    
    # Conversion en DataFrame
    df = pd.DataFrame(toutes_donnees)
    df.to_csv('data/raw/collecte_brute.csv', index=False)
    logger.info(f"✓ Données brutes sauvegardées : {len(df)} enregistrements")
    
    # 3. Analyse descriptive (efficacité)
    logger.info("\n[2/5] Analyse statistique...")
    analyse = AnalyseEcommerce(df)
    rapport = analyse.analyse_prix_complete()
    
    # Sauvegarde rapport
    sauvegarder_json(rapport, 'outputs/rapports/rapport_statistiques.json')
    logger.info("✓ Rapport statistique généré")
    
    # 4. Analyse concurrentielle
    logger.info("\n[3/5] Analyse concurrentielle...")
    matrice_compet = analyse.comparaison_concurrentielle()
    matrice_compet.to_csv('data/processed/matrice_concurrentielle.csv')
    logger.info(f"✓ Matrice concurrentielle sauvegardée")
    
    # 5. Détection des anomalies
    logger.info("\n[4/5] Détection des anomalies...")
    anomalies = analyse.detection_anomalies(seuil=1.5)
    if anomalies:
        logger.warning(f"⚠️ {len(anomalies)} produits avec prix anormal détectés")
        sauvegarder_json(anomalies, 'outputs/rapports/anomalies.json')
    
    # 6. Alertes bonnes affaires
    logger.info("\n[5/5] Génération des alertes...")
    alertes = SystemeAlertes.check_bonnes_affaires(df, seuil_economie=50)
    if alertes:
        logger.info(f"💰 {len(alertes)} bonnes affaires identifiées !")
        sauvegarder_json(alertes, 'outputs/rapports/alertes_bonnes_affaires.json')
        
        # Affichage console
        print("\n" + "="*60)
        print("🔥 BONNES AFFAIRES DÉTECTÉES 🔥")
        print("="*60)
        for alerte in alertes:
            print(f"• {alerte['produit']} sur {alerte['site']}")
            print(f"  Prix : {alerte['prix_actuel']}€ (au lieu de {alerte['prix_original']}€)")
            print(f"  Économie : {alerte['economie']}€ - {alerte['promotion']}")
            print()
    
    ruptures = SystemeAlertes.check_rupture(df)
    if ruptures is not None and not ruptures.empty:
        logger.warning(f"⚠️ Produits en rupture : {len(ruptures)} cas")
    
    # 7. Visualisations
    logger.info("\n[6/6] Génération des graphiques...")
    viz = VisualisateurEcommerce()
    viz.barplot_comparatif(df)
    viz.boxplot_distribution(df)
    viz.heatmap_disponibilite(df)
    viz.pie_promotions(df)
    viz.courbe_evolution(df)
    logger.info("✓ Graphiques générés dans outputs/graphiques/")
    
    # 8. Rapport final textuel
    with open('outputs/rapports/rapport_final.txt', 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("RAPPORT E-COMMERCE ANALYTICS\n")
        f.write(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        f.write(f"📊 {len(df)} offres analysées\n")
        f.write(f"🏷️ {df['produit'].nunique()} produits uniques\n")
        f.write(f"🛒 {df['site'].nunique()} sites comparés\n\n")
        
        f.write("💰 STATISTIQUES PRIX :\n")
        f.write(f"  • Prix moyen global : {rapport['prix_moyen_global']:.2f}€\n")
        f.write(f"  • Prix minimum : {rapport['prix_min_global']:.2f}€\n")
        f.write(f"  • Prix maximum : {rapport['prix_max_global']:.2f}€\n\n")
        
        f.write("🏆 MEILLEURS PRIX PAR PRODUIT :\n")
        for _, row in rapport['meilleur_prix_par_produit'].iterrows():
            f.write(f"  • {row['produit']} : {row['prix']:.2f}€ chez {row['site']}\n")
        
        if alertes:
            f.write(f"\n🔥 {len(alertes)} BONNES AFFAIRES IDENTIFIÉES\n")
            for alerte in alertes:
                f.write(f"  • {alerte['produit']} : économie {alerte['economie']}€\n")
    
    logger.info("\n✅ APPLICATION TERMINÉE AVEC SUCCÈS")
    logger.info(f"📁 Résultats disponibles dans outputs/")
    
    return 0

if __name__ == "__main__":
    exit(main())