import pandas as pd
import numpy as np

class AnalyseEcommerce:
    def __init__(self, df):
        self.df = df
        self.df_clean = df[df['prix'].notna()].copy()
    
    def analyse_prix_complete(self):
        stats_group = self.df_clean.groupby(['produit', 'site'])['prix'].agg([
            'min', 'max', 'mean', 'count'
        ]).round(2)
        
        meilleur_prix = self.df_clean.loc[
            self.df_clean.groupby('produit')['prix'].idxmin()
        ][['produit', 'site', 'prix', 'promotion']]
        
        volatilite = self.df_clean.groupby('produit')['prix'].std().sort_values(ascending=False)
        dispo_site = self.df_clean.groupby('site')['disponible'].mean() * 100
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
        pivot = self.df_clean.pivot_table(
            index='produit', 
            columns='site', 
            values='prix',
            aggfunc='first'
        )
        
        if len(pivot.columns) >= 2:
            pivot['ecart_Amazon_Fnac'] = np.abs(pivot['Amazon'] - pivot['Fnac'])
            pivot['site_le_moins_cher'] = pivot.idxmin(axis=1)
        
        return pivot
    
    def detection_anomalies(self, seuil=2):
        anomalies = {}
        for produit in self.df_clean['produit'].unique():
            df_produit = self.df_clean[self.df_clean['produit'] == produit]
            moyenne = df_produit['prix'].mean()
            std = df_produit['prix'].std()
            
            if std > 0:
                df_produit['ecart_normalise'] = abs(df_produit['prix'] - moyenne) / std
                anomalies_produit = df_produit[df_produit['ecart_normalise'] > seuil]
                
                if not anomalies_produit.empty:
                    anomalies[produit] = anomalies_produit[['site', 'prix', 'ecart_normalise']]
        
        return anomalies
