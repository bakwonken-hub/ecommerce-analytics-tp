import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

class VisualisateurEcommerce:
    def __init__(self, output_dir="outputs/graphiques"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def barplot_comparatif(self, df):
        """Comparaison des prix par produit et site"""
        pivot = df.pivot_table(index='produit', columns='site', values='prix', aggfunc='first')
        
        pivot.plot(kind='bar', figsize=(12, 6))
        plt.title("Comparaison des prix par produit et par site", fontsize=14, fontweight='bold')
        plt.xlabel("Produit", fontsize=12)
        plt.ylabel("Prix (€)", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title="Site")
        plt.tight_layout()
        plt.savefig(self.output_dir / "comparaison_prix.png", dpi=150)
        plt.close()
    
    def boxplot_distribution(self, df):
        """Distribution des prix par site"""
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x='site', y='prix')
        plt.title("Distribution des prix par site", fontsize=14, fontweight='bold')
        plt.xlabel("Site e-commerce", fontsize=12)
        plt.ylabel("Prix (€)", fontsize=12)
        plt.tight_layout()
        plt.savefig(self.output_dir / "distribution_prix_site.png", dpi=150)
        plt.close()
    
    def heatmap_disponibilite(self, df):
        """Heatmap de disponibilité"""
        dispo_matrix = df.groupby(['produit', 'site'])['disponible'].mean().unstack()
        
        plt.figure(figsize=(10, 6))
        sns.heatmap(dispo_matrix, annot=True, cmap='YlOrRd', fmt='.0%', cbar_kws={'label': 'Taux disponibilité'})
        plt.title("Taux de disponibilité par produit et site", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / "heatmap_disponibilite.png", dpi=150)
        plt.close()
    
    def pie_promotions(self, df):
        """Part des produits en promotion par site"""
        promos_site = df[df['promotion'].notna()].groupby('site').size()
        total_par_site = df.groupby('site').size()
        taux_promo = (promos_site / total_par_site * 100).fillna(0)
        
        plt.figure(figsize=(8, 8))
        plt.pie(taux_promo, labels=taux_promo.index, autopct='%1.1f%%', startangle=90)
        plt.title("Taux de produits en promotion par site", fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / "taux_promotions.png", dpi=150)
        plt.close()
    
    def courbe_evolution(self, df):
        """Évolution des prix dans le temps (si plusieurs collectes)"""
        if 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp'], unit='s')
            evolution = df.groupby(['date', 'site'])['prix'].mean().unstack()
            
            plt.figure(figsize=(12, 6))
            evolution.plot(marker='o')
            plt.title("Évolution des prix moyens dans le temps", fontsize=14, fontweight='bold')
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Prix moyen (€)", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(self.output_dir / "evolution_temporelle.png", dpi=150)
            plt.close()