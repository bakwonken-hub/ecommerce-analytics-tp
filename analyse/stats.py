import pandas as pd
import numpy as np
from datetime import datetime

class AnalyseEcommerce:
    def __init__(self, df):
        """
        df : DataFrame avec colonnes site, produit, prix, disponible, promotion, etc.
        """
        self.df = df
        self.df_clean = df[df['prix'].notna()].copy()
    
    def analyse_prix_complete(self):
        """Rapport statistique complet des prix"""
        stats_group = self.df_clean.groupby(['produit', 'site'])['prix'].agg([
            'min', 'max', 'mean', 'std', 'count'
        ]).round(2)
        
        # Meilleur prix par produit
        meilleur_prix = self.df_clean.loc[
            self.df_clean.groupby('produit')['prix'].idxmin()
        ][['produit', 'site', 'prix', 'promotion']]
        
        # Écart type global (volatilité des prix)
        volatilite = self.df_clean.groupby('produit')['prix'].std().sort_values(ascending=False)
        
        # Taux de disponibilité par site
        dispo_site = self.df_clean.groupby('site')['disponible'].mean() * 100
        
        # Top promos
        promos = self.df_clean[self.df_clean['promotion'].notna()][['produit', 'site', 'prix', 'promotion']]
        
        rapport = {
            "statistiques_globales": stats_group,
            "meilleur_prix_par_produit": meilleur_prix,
            "volatilite_prix": volatilite,
            "disponibilite_par_site": dispo_site,
            "promotions_actives": promos,
            "prix_moyen_global": self.df_clean['prix'].mean(),
            "prix_min_global": self.df_clean['prix'].min(),
            "prix_max_global": self.df_clean['prix'].max()
        }
        
        return rapport
    
    def comparaison_concurrentielle(self):
        """Matrice de comparaison des prix entre sites"""
        pivot = self.df_clean.pivot_table(
            index='produit', 
            columns='site', 
            values='prix',
            aggfunc='first'
        )
        
        # Calcul des écarts
        if len(pivot.columns) >= 2:
            pivot['ecart_Amazon_Fnac'] = np.abs(pivot['Amazon'] - pivot['Fnac'])
            pivot['site_le_moins_cher'] = pivot.idxmin(axis=1)
        
        return pivot
    
    def detection_anomalies(self, seuil=2):
        """Détection des prix anormaux (écart-type > seuil)"""
        anomalies = {}
        for produit in self.df_clean['produit'].unique():
            df_produit = self.df_clean[self.df_clean['produit'] == produit]
            moyenne = df_produit['prix'].mean()
            std = df_produit['prix'].std()
            
            df_produit['ecart_normalise'] = abs(df_produit['prix'] - moyenne) / std
            anomalies_produit = df_produit[df_produit['ecart_normalise'] > seuil]
            
            if not anomalies_produit.empty:
                anomalies[produit] = anomalies_produit[['site', 'prix', 'ecart_normalise']]
        
        return anomalies